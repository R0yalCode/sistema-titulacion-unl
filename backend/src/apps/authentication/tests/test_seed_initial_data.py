"""Pruebas del comando seed_initial_data (cuentas demo, DK-014).

La contrasena demo se lee de la variable de entorno SEED_DEMO_PASSWORD, que
es obligatoria y no tiene valor por defecto. Las pruebas generan valores
aleatorios para no versionar ningun literal con forma de contrasena.
"""

import secrets
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.authentication.adapters.management.commands.seed_initial_data import (
    CUENTAS_DEMO,
    VARIABLE_CLAVE_DEMO,
)
from apps.authentication.adapters.models import User, UserRole

pytestmark = pytest.mark.django_db


def _ejecutar() -> str:
    salida = StringIO()
    call_command("seed_initial_data", stdout=salida, stderr=StringIO())
    return salida.getvalue()


@pytest.mark.parametrize("valor", [None, "", "   "])
def test_sin_variable_o_vacia_detiene_sin_crear_cuentas(monkeypatch, valor):
    if valor is None:
        monkeypatch.delenv(VARIABLE_CLAVE_DEMO, raising=False)
    else:
        monkeypatch.setenv(VARIABLE_CLAVE_DEMO, valor)

    with pytest.raises(CommandError, match=VARIABLE_CLAVE_DEMO):
        _ejecutar()

    usernames = [username for username, _, _ in CUENTAS_DEMO]
    assert not User.objects.filter(username__in=usernames).exists()


def test_crea_las_cuentas_demo_con_la_clave_de_la_variable(monkeypatch):
    clave = secrets.token_urlsafe(16)
    monkeypatch.setenv(VARIABLE_CLAVE_DEMO, clave)

    salida = _ejecutar()

    assert len(CUENTAS_DEMO) == 8
    for username, cedula, rol in CUENTAS_DEMO:
        user = User.objects.get(username=username)
        assert user.cedula == cedula
        assert user.check_password(clave)
        assert UserRole.objects.filter(user=user, role__name=rol).exists()
    assert "8 nuevas" in salida
    assert clave not in salida


def test_es_idempotente_y_no_cambia_claves_existentes(monkeypatch):
    clave_inicial = secrets.token_urlsafe(16)
    monkeypatch.setenv(VARIABLE_CLAVE_DEMO, clave_inicial)
    _ejecutar()

    clave_nueva = secrets.token_urlsafe(16)
    monkeypatch.setenv(VARIABLE_CLAVE_DEMO, clave_nueva)
    salida = _ejecutar()

    usernames = [username for username, _, _ in CUENTAS_DEMO]
    total = len(CUENTAS_DEMO)
    assert User.objects.filter(username__in=usernames).count() == total
    assert UserRole.objects.filter(user__username__in=usernames).count() == total
    assert "0 nuevas" in salida
    for username in usernames:
        user = User.objects.get(username=username)
        assert user.check_password(clave_inicial)
        assert not user.check_password(clave_nueva)
    assert clave_nueva not in salida
