"""I-3 (T5): fallo real al confirmar (*commit*) con PostgreSQL.

Con `transaction=True`, la transacción del servicio es la externa y su salida
llama de verdad a `connection.commit()`. Se hace fallar ese commit (una vez,
como un error del servidor de base de datos) y se comprueba que la BD queda
sin cambios y que no queda ningún archivo sin registro (H-I3-01, H-I3-02).
"""

import importlib
import io
import itertools
from pathlib import Path

import pytest
from django.conf import settings
from django.core.cache import cache
from django.db import OperationalError, connections
from rest_framework.test import APIClient

from apps.authentication.adapters.models import Role, User, UserRole
from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.expedientes.services import (
    crear_expediente,
    enviar_expediente,
    iniciar_verificacion,
)
from apps.peticiones.adapters.models import DocumentoEntregado, PeticionDocumental
from apps.verificacion.adapters.models import (
    ChecklistVerification,
    ObservacionAccionable,
)
from apps.verificacion.services import evaluar_checklist

pytestmark = [
    pytest.mark.postgres,
    pytest.mark.django_db(transaction=True, serialized_rollback=True),
]

E = ExpedienteTitulacion
CARRERA = "aaaaaaaa-1306-4111-8111-111111111111"
FACULTAD = "bbbbbbbb-1306-4111-8111-111111111111"
_CEDULAS = itertools.count(9060000001)
PDF = (
    b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    b"2 0 obj\n<< /Type /Pages /Kids [] /Count 0 >>\nendobj\n"
    b"trailer\n<< /Root 1 0 R >>\n%%EOF\n"
)
cargar_mod = importlib.import_module("apps.peticiones.services.cargar_documento")


def _usuario(username, rol):
    user = User.objects.create_user(
        username=username,
        password="x",
        cedula=f"{next(_CEDULAS):010d}",
        carrera_id=CARRERA,
        facultad_id=FACULTAD,
    )
    UserRole.objects.create(user=user, role=Role.objects.get_or_create(name=rol)[0])
    return user


def _cliente(user):
    client = APIClient()
    client.force_authenticate(user=user)
    client.raise_request_exception = False
    return client


def _archivos():
    raiz = Path(settings.PRIVATE_MEDIA_ROOT)
    return sorted(str(p.relative_to(raiz)) for p in raiz.rglob("*") if p.is_file())


@pytest.fixture(autouse=True)
def _cache_limpia():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def commit_fallido(monkeypatch):
    """Hace fallar el siguiente commit real de la conexión, una sola vez."""
    conexion = connections["default"]
    real = conexion.commit
    estado = {"fallos": 0}

    def commit():
        if estado["fallos"] == 0:
            estado["fallos"] += 1
            raise OperationalError("fallo de commit simulado en el servidor")
        return real()

    def activar():
        monkeypatch.setattr(conexion, "commit", commit)
        return estado

    return activar


@pytest.fixture
def actores():
    return {
        "estudiante": _usuario("i3pg_est", "ESTUDIANTE"),
        "jurista": _usuario("i3pg_jur", "SECRETARIO_ABOGADO"),
    }


def test_carga_con_commit_fallido_no_deja_huerfano(actores, commit_fallido):
    expediente = crear_expediente.execute(actores["estudiante"], CARRERA)
    peticion = PeticionDocumental.objects.filter(expediente=expediente).first()
    estado = commit_fallido()

    archivo = io.BytesIO(PDF)
    archivo.name = "doc.pdf"
    respuesta = _cliente(actores["estudiante"]).post(
        f"/api/v1/peticiones/{peticion.pk}/documento/",
        {"archivo": archivo},
        format="multipart",
    )

    assert estado["fallos"] == 1
    assert respuesta.status_code == 500
    peticion.refresh_from_db()
    assert peticion.estado_peticion == "PENDIENTE"
    assert not DocumentoEntregado.objects.filter(peticion=peticion).exists()
    assert _archivos() == []


def test_subsanar_con_commit_fallido_no_deja_huerfano(actores, commit_fallido):
    expediente = crear_expediente.execute(actores["estudiante"], CARRERA)
    for peticion in PeticionDocumental.objects.filter(expediente=expediente):
        cargar_mod.execute(
            usuario=actores["estudiante"],
            peticion_id=peticion.pk,
            archivo=io.BytesIO(PDF),
            nombre_original="v1.pdf",
        )
    enviar_expediente.execute(expediente, actor=actores["estudiante"])
    iniciar_verificacion.execute(expediente.pk, actor=actores["jurista"])
    item = ChecklistVerification.objects.filter(expediente=expediente).first()
    evaluar_checklist.execute(actores["jurista"], item.pk, "OBSERVADO", "Ilegible")
    antes = _archivos()
    estado = commit_fallido()

    archivo = io.BytesIO(PDF + b"% v2\n")
    archivo.name = "v2.pdf"
    respuesta = _cliente(actores["estudiante"]).post(
        f"/api/v1/checklist/{item.pk}/subsanar/",
        {"archivo": archivo},
        format="multipart",
    )

    assert estado["fallos"] == 1
    assert respuesta.status_code == 500
    expediente.refresh_from_db()
    assert expediente.estado == E.ESTADO_OBSERVADA
    assert (
        ObservacionAccionable.objects.filter(
            expediente=expediente, resuelta=False
        ).count()
        == 1
    )
    assert _archivos() == antes
