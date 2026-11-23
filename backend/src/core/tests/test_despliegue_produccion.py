"""Arranque, rutas de persistencia y contexto Docker del despliegue de producción."""

import base64
import importlib.util
import json
import os
import secrets
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest
import yaml  # type: ignore[import-untyped]

BACKEND = Path(__file__).resolve().parents[3]
RAIZ = BACKEND.parent
COMPOSE = RAIZ / "docker-compose.prod.yml"

pytestmark = pytest.mark.skipif(
    not COMPOSE.exists(), reason="Requiere la raíz del repositorio."
)


def _entorno(tmp_path, **extra):
    entorno = {
        "PATH": os.environ.get("PATH", ""),
        "HOME": str(tmp_path),
        "PYTHONDONTWRITEBYTECODE": "1",
        "DJANGO_SETTINGS_MODULE": "config.settings.production",
        "SECRET_KEY": secrets.token_urlsafe(50),
        "JWT_SIGNING_KEY": secrets.token_urlsafe(50),
        "MFA_ENCRYPTION_KEYS": base64.urlsafe_b64encode(os.urandom(32)).decode(),
        "DB_PASSWORD": "pruebas",
        "ALLOWED_HOSTS": "test.invalid",
        "CSRF_TRUSTED_ORIGINS": "https://test.invalid",
        "CORS_ALLOWED_ORIGINS": "https://test.invalid",
        "FRONTEND_BASE_URL": "https://test.invalid",
        "EMAIL_HOST": "smtp.test.invalid",
        "DEFAULT_FROM_EMAIL": "no-reply@test.invalid",
        "LOG_DIR": str(tmp_path),
    }
    entorno.update(extra)
    return entorno


def _servicios():
    return yaml.safe_load(COMPOSE.read_text(encoding="utf-8"))["services"]


def _puerto_libre():
    with socket.socket() as conexion:
        conexion.bind(("127.0.0.1", 0))
        return conexion.getsockname()[1]


def test_gunicorn_arranca_sin_pythonpath_desde_otro_directorio(tmp_path):
    """Arranque real: `--check-config` no aplica el ajuste `pythonpath`."""
    entorno = _entorno(tmp_path)
    assert "PYTHONPATH" not in entorno
    puerto = _puerto_libre()
    salida = tmp_path / "gunicorn.log"

    with salida.open("w", encoding="utf-8") as registro:
        proceso = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "gunicorn",
                "--config",
                str(BACKEND / "gunicorn.conf.py"),
                "--bind",
                f"127.0.0.1:{puerto}",
                "--workers",
                "1",
                "config.wsgi:application",
            ],
            cwd=tmp_path,
            env=entorno,
            stdout=registro,
            stderr=subprocess.STDOUT,
        )
        try:
            estado = None
            limite = time.monotonic() + 30
            while estado is None and time.monotonic() < limite:
                assert proceso.poll() is None, salida.read_text(encoding="utf-8")
                peticion = urllib.request.Request(
                    f"http://127.0.0.1:{puerto}/health/",
                    headers={"Host": "test.invalid"},
                )
                try:
                    with urllib.request.urlopen(peticion, timeout=2) as respuesta:
                        estado = respuesta.status
                except OSError:
                    time.sleep(0.2)
        finally:
            proceso.terminate()
            proceso.wait(timeout=15)

    assert estado == 200, salida.read_text(encoding="utf-8")
    assert "No module named" not in salida.read_text(encoding="utf-8")


def test_gunicorn_sin_la_configuracion_reproduce_el_fallo(tmp_path):
    proceso = subprocess.run(
        [sys.executable, "-m", "gunicorn", "--check-config", "config.wsgi:application"],
        cwd=tmp_path,
        env=_entorno(tmp_path),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )

    assert proceso.returncode != 0
    assert "No module named 'config'" in proceso.stderr


def test_entrypoint_usa_la_configuracion_de_gunicorn():
    contenido = (BACKEND / "entrypoint.sh").read_text(encoding="utf-8")
    assert "gunicorn --config ./gunicorn.conf.py config.wsgi:application" in contenido
    assert "collectstatic --noinput" in contenido
    assert "--clear" not in contenido


@pytest.mark.parametrize(
    "archivo", ["Dockerfile", "docker-compose.prod.yml", "backend/entrypoint.sh"]
)
def test_el_despliegue_no_depende_de_pythonpath(archivo):
    assert "PYTHONPATH" not in (RAIZ / archivo).read_text(encoding="utf-8")


def test_rutas_de_produccion_coinciden_con_los_volumenes(tmp_path):
    codigo = (
        "import json, environ\n"
        "environ.Env.read_env = lambda *a, **k: None\n"
        "from config.settings import production as p\n"
        "print(json.dumps({'media': str(p.MEDIA_ROOT), 'static': str(p.STATIC_ROOT),"
        " 'archivo': p.FILE_UPLOAD_PERMISSIONS,"
        " 'directorio': p.FILE_UPLOAD_DIRECTORY_PERMISSIONS,"
        " 'static_op': p.STORAGES['staticfiles']['OPTIONS']}))"
    )
    proceso = subprocess.run(
        [sys.executable, "-c", codigo],
        cwd=BACKEND,
        env=_entorno(tmp_path, PYTHONPATH=str(BACKEND / "src")),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert proceso.returncode == 0, proceso.stderr
    datos = json.loads(proceso.stdout)

    assert Path(datos["media"]) == BACKEND / "media"
    assert Path(datos["static"]) == BACKEND / "staticfiles"
    assert datos["archivo"] == 0o640
    assert datos["directorio"] == 0o750
    assert datos["static_op"] == {
        "file_permissions_mode": 0o644,
        "directory_permissions_mode": 0o755,
    }

    volumenes = _servicios()["backend"]["volumes"]
    assert "media_private_prod:/app/backend/media" in volumenes
    assert "static_data_prod:/app/backend/staticfiles" in volumenes


def test_nginx_no_monta_documentos_y_lee_estaticos_en_solo_lectura():
    nginx = _servicios()["nginx"]
    assert not any("media" in volumen for volumen in nginx["volumes"])
    assert "static_data_prod:/var/www/static:ro" in nginx["volumes"]
    assert nginx["build"]["context"] == "./frontend"
    assert nginx["build"]["target"] == "web"


def test_compose_no_fija_nombres_de_contenedor():
    assert all("container_name" not in s for s in _servicios().values())


def test_nginx_no_publica_media():
    contenido = (RAIZ / "nginx/prod.conf").read_text(encoding="utf-8")
    bloque = contenido.split("location ^~ /media/ {", 1)[1].split("}", 1)[0]
    assert "return 404;" in bloque
    assert "alias /var/www/static/;" in contenido
    assert "autoindex" not in contenido


@pytest.mark.parametrize(
    "patron",
    [
        "backend/media/",
        "backend/src/media/",
        "backend/src/staticfiles/",
        "**/media/private/",
        "**/*.pdf",
        "**/.env",
        "**/*.pem",
        "**/*.key",
        "nginx/certs/",
    ],
)
def test_dockerignore_excluye_documentos_y_secretos(patron):
    lineas = (RAIZ / ".dockerignore").read_text(encoding="utf-8").splitlines()
    assert patron in lineas


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        ("sgt.unl.edu.ec", "sgt.unl.edu.ec"),
        (" sgt.unl.edu.ec , otro.unl.edu.ec", "sgt.unl.edu.ec"),
        (".unl.edu.ec", "unl.edu.ec"),
        ("*", "localhost"),
        ("", "localhost"),
    ],
)
def test_healthcheck_usa_un_host_permitido(valor, esperado):
    especificacion = importlib.util.spec_from_file_location(
        "healthcheck_produccion", BACKEND / "healthcheck.py"
    )
    assert especificacion is not None and especificacion.loader is not None
    modulo = importlib.util.module_from_spec(especificacion)
    especificacion.loader.exec_module(modulo)

    assert modulo.host_permitido(valor) == esperado
