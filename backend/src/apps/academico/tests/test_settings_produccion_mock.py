"""MockSGA no puede activarse en producción con ninguna variable de entorno.

Los settings se evalúan en procesos aparte: `base.py` lee `DEBUG` al importarse
y recargar solo `production.py` dentro de la suite no reproduciría el arranque.
"""

import base64
import itertools
import json
import os
import secrets
import subprocess
import sys
from pathlib import Path

import pytest

from apps.academico.ports.fuente_academica import FuenteAcademicaNoConfiguradaError
from apps.academico.services import fuentes

BACKEND = Path(__file__).resolve().parents[4]
PRODUCCION = "config.settings.production"
AUSENTE = None

VALORES_DEBUG = [AUSENTE, "False", "True", "1"]
VALORES_PROVEEDOR = [
    AUSENTE,
    "",
    "mock_sga",
    "MOCK_SGA",
    "Mock_Sga",
    " mock_sga ",
    "sga",
    "desconocido",
]
VALORES_PERMISO = [AUSENTE, "false", "true", "1", "yes"]

# Evalúa cada combinación desde cero, sin leer un `.env` local.
EVALUADOR = """
import importlib, json, os, sys
import environ
from django.core.exceptions import ImproperlyConfigured

environ.Env.read_env = lambda *args, **kwargs: None
entorno = dict(os.environ)
resultados = []
for caso in json.load(sys.stdin):
    os.environ.clear()
    os.environ.update(entorno)
    os.environ.update(caso)
    for modulo in [m for m in sys.modules if m.startswith("config.settings.")]:
        del sys.modules[modulo]
    try:
        p = importlib.import_module("config.settings.production")
    except ImproperlyConfigured as exc:
        resultados.append({"arranca": False, "error": str(exc)})
    else:
        resultados.append({
            "arranca": True,
            "debug": p.DEBUG,
            "proveedor": p.ACADEMIC_PROFILE_PROVIDER,
            "permitido": p.ACADEMIC_PROFILE_MOCK_ALLOWED,
        })
print(json.dumps(resultados))
"""

CONSULTA_FUENTE = """
import django
django.setup()
from apps.academico.ports.fuente_academica import FuenteAcademicaNoConfiguradaError
from apps.academico.services.fuentes import get_fuente_academica
try:
    get_fuente_academica()
except FuenteAcademicaNoConfiguradaError:
    print("sin-fuente")
else:
    print("fuente-activa")
"""


class _FuenteInstitucional:
    """Adaptador no simulado, equivalente al contrato de un proveedor real."""

    es_simulada = False


def _entorno(tmp_path, modulo=PRODUCCION, **variables):
    entorno = {
        "PATH": os.environ.get("PATH", ""),
        "HOME": str(tmp_path),
        "PYTHONPATH": str(BACKEND / "src"),
        "PYTHONDONTWRITEBYTECODE": "1",
        "DJANGO_SETTINGS_MODULE": modulo,
        "SECRET_KEY": secrets.token_urlsafe(50),
        "JWT_SIGNING_KEY": secrets.token_urlsafe(50),
        "MFA_ENCRYPTION_KEYS": base64.urlsafe_b64encode(os.urandom(32)).decode(),
        "DB_PASSWORD": "pruebas",
        "ALLOWED_HOSTS": "test.invalid",
        "CSRF_TRUSTED_ORIGINS": "https://test.invalid",
        "CORS_ALLOWED_ORIGINS": "https://test.invalid",
        "LOG_DIR": str(tmp_path),
    }
    entorno.update(variables)
    return entorno


def _ejecutar(argumentos, entorno, entrada=None):
    return subprocess.run(
        [sys.executable, *argumentos],
        cwd=BACKEND,
        env=entorno,
        input=entrada,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


def _combinaciones():
    casos = []
    for debug, proveedor, permiso in itertools.product(
        VALORES_DEBUG, VALORES_PROVEEDOR, VALORES_PERMISO
    ):
        caso = {}
        if debug is not AUSENTE:
            caso["DEBUG"] = debug
        if proveedor is not AUSENTE:
            caso["ACADEMIC_PROFILE_PROVIDER"] = proveedor
        if permiso is not AUSENTE:
            caso["ACADEMIC_PROFILE_MOCK_ALLOWED"] = permiso
        casos.append(caso)
    return casos


def test_ninguna_combinacion_de_variables_habilita_el_mock(tmp_path):
    casos = _combinaciones()
    assert len(casos) == 160

    proceso = _ejecutar(
        ["-c", EVALUADOR], _entorno(tmp_path), entrada=json.dumps(casos)
    )
    assert proceso.returncode == 0, proceso.stderr
    resultados = json.loads(proceso.stdout)
    assert len(resultados) == len(casos)

    for caso, resultado in zip(casos, resultados):
        proveedor = caso.get("ACADEMIC_PROFILE_PROVIDER", "").strip()
        if proveedor.casefold() == "mock_sga":
            assert resultado["arranca"] is False, caso
            assert "MockSGA" in resultado["error"], caso
        else:
            assert resultado == {
                "arranca": True,
                "debug": False,
                "proveedor": proveedor,
                "permitido": False,
            }, caso


@pytest.mark.parametrize("debug", ["False", "True"])
@pytest.mark.parametrize("permiso", ["false", "true"])
@pytest.mark.parametrize(
    "orden",
    [
        ["manage.py", "check"],
        ["-c", "from config.wsgi import application"],
    ],
    ids=["manage-check", "wsgi"],
)
def test_arranque_de_produccion_con_mock_falla_con_error_claro(
    tmp_path, debug, permiso, orden
):
    entorno = _entorno(
        tmp_path,
        DEBUG=debug,
        ACADEMIC_PROFILE_PROVIDER="mock_sga",
        ACADEMIC_PROFILE_MOCK_ALLOWED=permiso,
    )
    proceso = _ejecutar(orden, entorno)

    assert proceso.returncode != 0
    assert "ImproperlyConfigured" in proceso.stderr
    assert "no está permitido en producción" in proceso.stderr
    assert entorno["SECRET_KEY"] not in proceso.stderr
    assert entorno["MFA_ENCRYPTION_KEYS"] not in proceso.stderr


@pytest.mark.parametrize("debug", ["False", "True"])
@pytest.mark.parametrize("proveedor", ["", "sga"])
def test_arranque_de_produccion_sin_mock_y_sin_fuente_activa(
    tmp_path, debug, proveedor
):
    entorno = _entorno(
        tmp_path,
        DEBUG=debug,
        ACADEMIC_PROFILE_PROVIDER=proveedor,
        ACADEMIC_PROFILE_MOCK_ALLOWED="true",
    )

    verificacion = _ejecutar(["manage.py", "check"], entorno)
    assert verificacion.returncode == 0, verificacion.stderr

    wsgi = _ejecutar(["-c", "from config.wsgi import application"], entorno)
    assert wsgi.returncode == 0, wsgi.stderr

    consulta = _ejecutar(["-c", CONSULTA_FUENTE], entorno)
    assert consulta.returncode == 0, consulta.stderr
    assert consulta.stdout.strip() == "sin-fuente"


def test_arranque_de_produccion_sin_variables_opcionales(tmp_path):
    proceso = _ejecutar(["manage.py", "check"], _entorno(tmp_path))
    assert proceso.returncode == 0, proceso.stderr


@pytest.mark.parametrize("modulo", ["config.settings.local", "config.settings.test"])
def test_desarrollo_y_pruebas_mantienen_el_mock(tmp_path, modulo):
    entorno = _entorno(tmp_path, modulo=modulo)

    verificacion = _ejecutar(["manage.py", "check"], entorno)
    assert verificacion.returncode == 0, verificacion.stderr

    consulta = _ejecutar(["-c", CONSULTA_FUENTE], entorno)
    assert consulta.returncode == 0, consulta.stderr
    assert consulta.stdout.strip() == "fuente-activa"


def test_proveedor_real_sigue_siendo_seleccionable(settings, monkeypatch):
    """Con los valores de producción, una fuente no simulada se resuelve."""
    ruta = f"{__name__}._FuenteInstitucional"
    monkeypatch.setitem(fuentes._FUENTES, "institucional", ruta)
    settings.ACADEMIC_PROFILE_PROVIDER = "institucional"
    settings.ACADEMIC_PROFILE_MOCK_ALLOWED = False

    assert isinstance(fuentes.get_fuente_academica(), _FuenteInstitucional)


def test_mock_registrado_sigue_rechazado_con_valores_de_produccion(settings):
    settings.ACADEMIC_PROFILE_PROVIDER = "mock_sga"
    settings.ACADEMIC_PROFILE_MOCK_ALLOWED = False

    with pytest.raises(FuenteAcademicaNoConfiguradaError):
        fuentes.get_fuente_academica()
