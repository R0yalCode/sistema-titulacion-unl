import secrets
from io import StringIO

import pytest
from django.core.management import call_command

from apps.authentication.adapters.models import Role, User
from apps.entorno_pruebas import dataset
from apps.entorno_pruebas.adapters.models import RegistroDatasetSintetico


@pytest.fixture(autouse=True)
def dominio_del_dataset(settings):
    """Permite el flujo de ingreso con los correos del dominio reservado."""
    settings.INSTITUTIONAL_EMAIL_DOMAIN = dataset.DOMINIO_CORREO


@pytest.fixture
def clave_dataset(monkeypatch):
    """Contraseña aleatoria por ejecución: nunca se fija en el código."""
    clave = "Dev-" + secrets.token_urlsafe(18)
    monkeypatch.setenv("SEED_DATASET_PASSWORD", clave)
    return clave


@pytest.fixture
def roles(db):
    return {rol: Role.objects.get_or_create(name=rol)[0] for rol in dataset.ROLES}


def ejecutar_seed(*args):
    salida = StringIO()
    call_command("seed_sgt_siaaf", *args, stdout=salida)
    return salida.getvalue()


def usuarios_del_dataset(rol=None):
    personas = dataset.personas()
    claves = {p.clave: p for p in personas if rol is None or p.rol == rol}
    marcas = RegistroDatasetSintetico.objects.filter(
        lote=dataset.LOTE, clave__in=claves
    )
    usuarios = {
        str(u.pk): u for u in User.objects.filter(pk__in=[m.objeto_id for m in marcas])
    }
    return [(claves[m.clave], usuarios[m.objeto_id]) for m in marcas.order_by("clave")]


@pytest.fixture
def dataset_creado(roles, clave_dataset):
    salida = ejecutar_seed()
    return salida
