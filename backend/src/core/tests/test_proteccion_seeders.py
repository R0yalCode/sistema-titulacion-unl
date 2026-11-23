"""Los comandos de datos de demostración no escriben fuera de desarrollo y pruebas."""

import base64
import os
import secrets
import subprocess
import sys
from io import StringIO
from pathlib import Path

import pytest
from django.core.management import CommandError, call_command
from django.db import connection
from django.test.utils import CaptureQueriesContext

from apps.academico.adapters.models import (
    Carrera,
    EventoCatalogoAcademico,
    Facultad,
    PerfilSGASimulado,
)
from apps.authentication.adapters.management.commands.seed_initial_data import (
    CUENTAS_DEMO,
    VARIABLE_CLAVE_DEMO,
)
from apps.authentication.adapters.models import Role, User, UserRole
from core.adapters.entorno_demo import NOMBRE_MARCA_PRODUCCION

BACKEND = Path(__file__).resolve().parents[3]
RAIZ = BACKEND.parent
PRODUCCION = "config.settings.production"

COMANDOS = [
    ("seed_initial_data",),
    ("seed_mock_sga",),
    ("seed_mock_sga", "--asignar-ambito-personal"),
    ("seed_mock_sga", "--estudiantes", "estudiante_1"),
]
MODULOS_RECHAZADOS = [
    PRODUCCION,
    "config.settings.base",
    "config.settings.staging",
    "config.settings.local.extra",
    "CONFIG.SETTINGS.LOCAL",
    "",
]
MODULOS_PERMITIDOS = [
    "config.settings.local",
    "config.settings.test",
    "config.settings.test_postgres",
]


def _ejecutar(*comando):
    salida = StringIO()
    call_command(*comando, stdout=salida, stderr=StringIO())
    return salida.getvalue()


def _sin_datos_demo():
    assert not User.objects.exists()
    assert not Role.objects.exists()
    assert not UserRole.objects.exists()
    assert not Facultad.objects.exists()
    assert not Carrera.objects.exists()
    assert not PerfilSGASimulado.objects.exists()
    assert not EventoCatalogoAcademico.objects.exists()


@pytest.fixture
def clave_demo(monkeypatch):
    monkeypatch.setenv(VARIABLE_CLAVE_DEMO, secrets.token_urlsafe(18))


@pytest.mark.django_db
@pytest.mark.parametrize("modulo", MODULOS_RECHAZADOS)
@pytest.mark.parametrize("comando", COMANDOS)
def test_rechaza_sin_consultas_ni_escrituras(monkeypatch, clave_demo, modulo, comando):
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", modulo)

    with CaptureQueriesContext(connection) as consultas:
        with pytest.raises(CommandError, match="solo puede ejecutarse"):
            _ejecutar(*comando)

    assert len(consultas) == 0
    _sin_datos_demo()


@pytest.mark.django_db
@pytest.mark.parametrize("comando", COMANDOS)
def test_rechaza_sin_variable_de_modulo(monkeypatch, clave_demo, comando):
    monkeypatch.delenv("DJANGO_SETTINGS_MODULE")

    with pytest.raises(CommandError, match="solo puede ejecutarse"):
        _ejecutar(*comando)

    _sin_datos_demo()


@pytest.mark.django_db
@pytest.mark.parametrize("modulo", MODULOS_PERMITIDOS)
@pytest.mark.parametrize("comando", COMANDOS)
def test_la_marca_de_produccion_prevalece_sobre_un_modulo_permitido(
    monkeypatch, settings, tmp_path, clave_demo, modulo, comando
):
    raiz = tmp_path / "backend"
    (raiz / "src").mkdir(parents=True)
    (raiz / NOMBRE_MARCA_PRODUCCION).touch()
    settings.BASE_DIR = raiz / "src"
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", modulo)

    with CaptureQueriesContext(connection) as consultas:
        with pytest.raises(CommandError, match="solo puede ejecutarse"):
            _ejecutar(*comando)

    assert len(consultas) == 0
    _sin_datos_demo()


@pytest.mark.django_db
def test_seed_mock_conserva_el_rechazo_si_el_mock_no_esta_permitido(settings):
    settings.ACADEMIC_PROFILE_MOCK_ALLOWED = False

    with pytest.raises(CommandError, match="fuente académica simulada"):
        _ejecutar("seed_mock_sga")

    _sin_datos_demo()


@pytest.mark.django_db
@pytest.mark.parametrize("modulo", MODULOS_PERMITIDOS)
def test_carga_e_idempotencia_en_desarrollo_y_pruebas(monkeypatch, clave_demo, modulo):
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", modulo)

    for _ in range(2):
        _ejecutar("seed_initial_data")
        _ejecutar("seed_mock_sga", "--asignar-ambito-personal")

    assert User.objects.count() == len(CUENTAS_DEMO)
    assert UserRole.objects.count() == len(CUENTAS_DEMO)
    assert Role.objects.count() == len(CUENTAS_DEMO)
    assert Facultad.objects.count() == 1
    assert Carrera.objects.count() == 2
    assert PerfilSGASimulado.objects.count() == 1


def _entorno_produccion(tmp_path, **extra):
    entorno = {
        "PATH": os.environ.get("PATH", ""),
        "HOME": str(tmp_path),
        "PYTHONDONTWRITEBYTECODE": "1",
        "DJANGO_SETTINGS_MODULE": PRODUCCION,
        "SECRET_KEY": secrets.token_urlsafe(50),
        "JWT_SIGNING_KEY": secrets.token_urlsafe(50),
        "MFA_ENCRYPTION_KEYS": base64.urlsafe_b64encode(os.urandom(32)).decode(),
        "ALLOWED_HOSTS": "test.invalid",
        "CSRF_TRUSTED_ORIGINS": "https://test.invalid",
        "CORS_ALLOWED_ORIGINS": "https://test.invalid",
        "FRONTEND_BASE_URL": "https://test.invalid",
        "EMAIL_HOST": "smtp.test.invalid",
        "DEFAULT_FROM_EMAIL": "no-reply@test.invalid",
        "LOG_DIR": str(tmp_path),
        # Puerto cerrado: cualquier intento de acceso a la base fallaría con
        # un error de conexión, distinto del mensaje de la protección.
        "DB_ENGINE": "django.db.backends.postgresql",
        "DB_NAME": "inexistente",
        "DB_USER": "inexistente",
        "DB_PASSWORD": "inexistente",
        "DB_HOST": "127.0.0.1",
        "DB_PORT": "1",
        VARIABLE_CLAVE_DEMO: secrets.token_urlsafe(18),
    }
    entorno.update(extra)
    return entorno


@pytest.mark.parametrize(
    "extra",
    [
        {},
        {"DEBUG": "True"},
        {"DEBUG": "1", "ACADEMIC_PROFILE_MOCK_ALLOWED": "true"},
        {"DEMO_SEED_ALLOWED": "true", "SEED_ALLOW_PRODUCTION": "1"},
    ],
)
@pytest.mark.parametrize("comando", COMANDOS)
def test_arranque_real_en_produccion_rechaza_antes_de_conectar(
    tmp_path, comando, extra
):
    entorno = _entorno_produccion(tmp_path, **extra)
    proceso = subprocess.run(
        [sys.executable, "manage.py", *comando],
        cwd=BACKEND,
        env=entorno,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )

    assert proceso.returncode != 0
    assert "solo puede ejecutarse en desarrollo o pruebas" in proceso.stderr
    assert "OperationalError" not in proceso.stderr
    assert entorno[VARIABLE_CLAVE_DEMO] not in proceso.stdout + proceso.stderr


def test_la_imagen_de_produccion_crea_la_marca():
    dockerfile = (RAIZ / "Dockerfile").read_text(encoding="utf-8")
    produccion = dockerfile.split("FROM base AS production", 1)[1]
    desarrollo = dockerfile.split("FROM base AS development", 1)[1].split(
        "FROM base AS production", 1
    )[0]

    assert f"touch {NOMBRE_MARCA_PRODUCCION}" in produccion
    assert f"chmod 444 {NOMBRE_MARCA_PRODUCCION}" in produccion
    assert NOMBRE_MARCA_PRODUCCION not in desarrollo
