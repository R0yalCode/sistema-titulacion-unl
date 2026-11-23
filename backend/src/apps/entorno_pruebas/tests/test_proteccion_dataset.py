"""El dataset usa la misma protección de destino que los demás seeders."""

import secrets
from io import StringIO

import pytest
from django.core.management import CommandError, call_command
from django.db import connection
from django.test.utils import CaptureQueriesContext

from apps.authentication.adapters.models import IdentidadEntornoBD, User

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def clave(monkeypatch):
    monkeypatch.setenv("SEED_DATASET_PASSWORD", secrets.token_urlsafe(24) + "aA1!")


def _ejecutar():
    call_command("seed_sgt_siaaf", "--sin-escenarios", stdout=StringIO())


def _escrituras(consultas):
    return [
        q["sql"]
        for q in consultas.captured_queries
        if q["sql"].lstrip().upper().startswith(("INSERT", "UPDATE", "DELETE"))
    ]


def test_rechaza_una_base_de_produccion_sin_escribir(monkeypatch):
    IdentidadEntornoBD.objects.create(entorno="produccion", base_registrada="x")
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "config.settings.local")

    with CaptureQueriesContext(connection) as consultas:
        with pytest.raises(CommandError, match="registrada como producción"):
            _ejecutar()

    assert _escrituras(consultas) == []
    assert not User.objects.exists()


def test_rechaza_una_base_sin_identidad_de_desarrollo(monkeypatch):
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "config.settings.local")

    with pytest.raises(CommandError, match="no tiene identidad de desarrollo"):
        _ejecutar()

    assert not User.objects.exists()


def test_carga_en_una_base_de_desarrollo(monkeypatch, roles):
    IdentidadEntornoBD.objects.create(entorno="desarrollo", base_registrada="x")
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "config.settings.local")

    _ejecutar()
    total = User.objects.count()
    _ejecutar()

    assert total == 80
    assert User.objects.count() == total


def test_correo_institucional_es_opcional_y_local(monkeypatch, roles, settings):
    IdentidadEntornoBD.objects.create(entorno="desarrollo", base_registrada="x")
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "config.settings.local")
    settings.INSTITUTIONAL_EMAIL_DOMAIN = "unl.edu.ec"

    call_command(
        "seed_sgt_siaaf",
        "--sin-escenarios",
        "--correo-institucional",
        stdout=StringIO(),
    )

    correos = list(User.objects.values_list("email", flat=True))
    assert len(correos) == 80
    assert all(
        c.startswith("sgtdemo.ds.") and c.endswith("@unl.edu.ec") for c in correos
    )
