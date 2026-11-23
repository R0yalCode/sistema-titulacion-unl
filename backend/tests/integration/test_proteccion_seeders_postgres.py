"""Identidad de entorno de la base sobre PostgreSQL real y desechable."""

import secrets
from io import StringIO

import pytest
from django.core.management import CommandError, call_command
from django.db import DatabaseError, connection, transaction

from apps.academico.adapters.models import Facultad
from apps.authentication.adapters.models import IdentidadEntornoBD, User
from core.adapters import entorno_demo

pytestmark = [pytest.mark.postgres, pytest.mark.django_db]


def _ejecutar(*comando):
    call_command(*comando, stdout=StringIO(), stderr=StringIO())


@pytest.fixture
def clave_demo(monkeypatch):
    monkeypatch.setenv("SEED_DEMO_PASSWORD", secrets.token_urlsafe(18))


@pytest.mark.parametrize(
    "sentencia",
    [
        "UPDATE sgt_identidad_entorno SET entorno = 'desarrollo'",
        "DELETE FROM sgt_identidad_entorno",
        "TRUNCATE sgt_identidad_entorno",
    ],
)
def test_la_identidad_no_se_puede_modificar(sentencia):
    IdentidadEntornoBD.objects.create(entorno="produccion", base_registrada="x")

    with pytest.raises(DatabaseError, match="inmutable"):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(sentencia)

    assert IdentidadEntornoBD.objects.get().entorno == "produccion"


def test_la_base_solo_admite_una_identidad_valida():
    IdentidadEntornoBD.objects.create(entorno="produccion", base_registrada="x")
    for sentencia in [
        "INSERT INTO sgt_identidad_entorno VALUES (2, 'desarrollo', 'x', now())",
        "INSERT INTO sgt_identidad_entorno VALUES (1, 'desarrollo', 'x', now())",
    ]:
        with pytest.raises(DatabaseError):
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute(sentencia)
    assert IdentidadEntornoBD.objects.count() == 1


@pytest.mark.parametrize(
    "modulo",
    ["config.settings.local", "config.settings.test", "config.settings.test_postgres"],
)
@pytest.mark.parametrize("comando", ["seed_initial_data", "seed_mock_sga"])
def test_base_de_produccion_rechaza_seeders(monkeypatch, clave_demo, modulo, comando):
    IdentidadEntornoBD.objects.create(entorno="produccion", base_registrada="x")
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", modulo)

    with pytest.raises(CommandError, match="registrada como producción"):
        _ejecutar(comando)

    assert not User.objects.exists()
    assert not Facultad.objects.exists()


def test_base_temporal_de_pytest_admite_la_carga(clave_demo):
    assert connection.settings_dict["NAME"].startswith("test_")

    _ejecutar("seed_initial_data")
    _ejecutar("seed_initial_data")

    assert User.objects.count() == 8


def test_nombre_sin_prefijo_de_pruebas_se_rechaza(monkeypatch, clave_demo):
    monkeypatch.setitem(connection.settings_dict, "NAME", "sgt_siaaf")

    with pytest.raises(CommandError, match="no tiene identidad de desarrollo"):
        _ejecutar("seed_initial_data")

    assert not User.objects.exists()
