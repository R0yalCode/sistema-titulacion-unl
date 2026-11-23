"""Configuración efectiva de correo y enlaces en producción."""

import base64
import json
import os
import secrets
import subprocess
import sys
from pathlib import Path

import pytest
import yaml  # type: ignore[import-untyped]
from django.core.exceptions import ImproperlyConfigured

from config.settings.correo_produccion import (
    BACKEND_SMTP,
    validar_backend_correo,
    validar_remitente,
    validar_servidor_correo,
    validar_url_frontend,
)

BACKEND = Path(__file__).resolve().parents[3]
COMPOSE = BACKEND.parent / "docker-compose.prod.yml"
HOSTS = ["sgt.test.invalid"]

EVALUADOR = """
import json
import environ
environ.Env.read_env = lambda *a, **k: None
from config.settings import production as p
print(json.dumps({
    "backend": p.EMAIL_BACKEND, "host": p.EMAIL_HOST, "puerto": p.EMAIL_PORT,
    "usuario": p.EMAIL_HOST_USER, "clave": bool(p.EMAIL_HOST_PASSWORD),
    "tls": p.EMAIL_USE_TLS, "timeout": p.EMAIL_TIMEOUT,
    "remitente": p.DEFAULT_FROM_EMAIL, "url": p.FRONTEND_BASE_URL,
}))
"""


def _entorno(tmp_path, **variables):
    entorno = {
        "PATH": os.environ.get("PATH", ""),
        "HOME": str(tmp_path),
        "PYTHONPATH": str(BACKEND / "src"),
        "PYTHONDONTWRITEBYTECODE": "1",
        "DJANGO_SETTINGS_MODULE": "config.settings.production",
        "SECRET_KEY": secrets.token_urlsafe(50),
        "JWT_SIGNING_KEY": secrets.token_urlsafe(50),
        "MFA_ENCRYPTION_KEYS": base64.urlsafe_b64encode(os.urandom(32)).decode(),
        "DB_PASSWORD": "pruebas",
        "ALLOWED_HOSTS": "sgt.test.invalid",
        "CSRF_TRUSTED_ORIGINS": "https://sgt.test.invalid",
        "CORS_ALLOWED_ORIGINS": "https://sgt.test.invalid",
        "FRONTEND_BASE_URL": "https://sgt.test.invalid",
        "EMAIL_HOST": "smtp.test.invalid",
        "DEFAULT_FROM_EMAIL": "no-reply@test.invalid",
        "LOG_DIR": str(tmp_path),
    }
    for nombre, valor in variables.items():
        if valor is None:
            entorno.pop(nombre, None)
        else:
            entorno[nombre] = valor
    return entorno


def _evaluar(entorno):
    return subprocess.run(
        [sys.executable, "-c", EVALUADOR],
        cwd=BACKEND,
        env=entorno,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


def test_configuracion_efectiva_con_valores_seguros_por_defecto(tmp_path):
    proceso = _evaluar(_entorno(tmp_path))

    assert proceso.returncode == 0, proceso.stderr
    assert json.loads(proceso.stdout) == {
        "backend": BACKEND_SMTP,
        "host": "smtp.test.invalid",
        "puerto": 587,
        "usuario": "",
        "clave": False,
        "tls": True,
        "timeout": 10,
        "remitente": "no-reply@test.invalid",
        "url": "https://sgt.test.invalid",
    }


@pytest.mark.parametrize(
    "variables",
    [
        {"EMAIL_HOST": None},
        {"EMAIL_HOST": ""},
        {"EMAIL_HOST": "localhost"},
        {"EMAIL_HOST": "127.0.0.1"},
        {"DEFAULT_FROM_EMAIL": None},
        {"DEFAULT_FROM_EMAIL": "no-es-correo"},
        {"FRONTEND_BASE_URL": None},
        {"FRONTEND_BASE_URL": "http://sgt.test.invalid"},
        {"FRONTEND_BASE_URL": "https://localhost"},
        {"FRONTEND_BASE_URL": "https://otro.test.invalid"},
        {"EMAIL_USE_TLS": "0"},
        {"EMAIL_BACKEND": "django.core.mail.backends.console.EmailBackend"},
        {"EMAIL_BACKEND": "django.core.mail.backends.locmem.EmailBackend"},
        {"EMAIL_BACKEND": "django.core.mail.backends.filebased.EmailBackend"},
        {"EMAIL_BACKEND": "django.core.mail.backends.dummy.EmailBackend"},
        {"EMAIL_HOST_USER": "cuenta"},
    ],
)
def test_produccion_no_arranca_con_correo_inseguro(tmp_path, variables):
    proceso = _evaluar(_entorno(tmp_path, **variables))

    assert proceso.returncode != 0
    assert "ImproperlyConfigured" in proceso.stderr


def test_el_error_no_expone_la_contrasena_smtp(tmp_path):
    clave = secrets.token_urlsafe(24)
    proceso = _evaluar(
        _entorno(
            tmp_path,
            EMAIL_HOST_PASSWORD=clave,
            EMAIL_HOST_USER=None,
        )
    )

    assert proceso.returncode != 0
    assert clave not in proceso.stdout + proceso.stderr


@pytest.mark.parametrize(
    "url",
    [
        "https://sgt.test.invalid",
        "https://sgt.test.invalid:8443",
        "https://SGT.test.invalid",
    ],
)
def test_url_frontend_valida(url):
    assert validar_url_frontend(url, HOSTS) == url


@pytest.mark.parametrize(
    "url",
    [
        "",
        "sgt.test.invalid",
        "//sgt.test.invalid",
        "http://sgt.test.invalid",
        "ftp://sgt.test.invalid",
        "https://sgt.test.invalid/",
        "https://sgt.test.invalid/app",
        "https://sgt.test.invalid?x=1",
        "https://sgt.test.invalid#x",
        "https://usuario@sgt.test.invalid",
        "https://usuario:clave@sgt.test.invalid",
        "https://sgt.test.invalid:puerto",
        "https://sgt.test.invalid:99999",
        " https://sgt.test.invalid",
        "https://sgt.test.invalid\n",
        "https://sgt.test.invalid\\@malicioso.invalid",
        "https://malicioso.invalid",
        "https://sgt.test.invalid.malicioso.invalid",
        "https://localhost",
        "https://app.localhost",
        "https://127.0.0.1",
        "https://0.0.0.0",
        "https://[::1]",
    ],
)
def test_url_frontend_invalida(url):
    hosts = [*HOSTS, "localhost", "app.localhost", "127.0.0.1", "0.0.0.0", "[::1]"]
    with pytest.raises(ImproperlyConfigured):
        validar_url_frontend(url, hosts)


def test_validadores_de_correo():
    assert validar_backend_correo(BACKEND_SMTP) == BACKEND_SMTP
    assert validar_servidor_correo(" smtp.unl.invalid ", "", "", True) == (
        "smtp.unl.invalid"
    )
    assert validar_remitente("no-reply@test.invalid") == "no-reply@test.invalid"


@pytest.mark.parametrize("ruta", ["/restablecer-contrasena", "/restablecer-2fa/confirmar"])
def test_nginx_no_registra_los_enlaces_de_recuperacion(ruta):
    contenido = (BACKEND.parent / "nginx/prod.conf").read_text(encoding="utf-8")
    bloque = contenido.split(f"location = {ruta} {{", 1)[1].split("}", 1)[0]

    assert "access_log off;" in bloque
    assert "try_files /index.html =404;" in bloque
    assert 'add_header Cache-Control "no-store";' in bloque
    assert "security-headers.conf" in bloque


def test_compose_entrega_la_configuracion_sin_valores_reales():
    backend = yaml.safe_load(COMPOSE.read_text(encoding="utf-8"))["services"][
        "backend"
    ]["environment"]

    assert backend["FRONTEND_BASE_URL"].startswith("${PUBLIC_BASE_URL:?")
    assert backend["EMAIL_HOST"].startswith("${EMAIL_HOST:?")
    assert backend["DEFAULT_FROM_EMAIL"].startswith("${DEFAULT_FROM_EMAIL:?")
    assert backend["EMAIL_BACKEND"] == f"${{EMAIL_BACKEND:-{BACKEND_SMTP}}}"
    assert backend["EMAIL_HOST_USER"] == "${EMAIL_HOST_USER:-}"
    assert backend["EMAIL_HOST_PASSWORD"] == "${EMAIL_HOST_PASSWORD:-}"
    assert backend["EMAIL_USE_TLS"] == "${EMAIL_USE_TLS:-1}"
    assert backend["EMAIL_PORT"] == "${EMAIL_PORT:-587}"
    assert backend["EMAIL_TIMEOUT"] == "${EMAIL_TIMEOUT:-10}"
