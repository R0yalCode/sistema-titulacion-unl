"""I-3 (T3): la subsanación no deja archivos huérfanos (H-I3-02).

Si falla un paso posterior a la escritura (documento, transición,
notificación), la BD revierte (estado, observación pendiente, versión) y el
archivo creado por la operación se elimina; la versión anterior queda
intacta (SHA-256). El código HTTP de cada caso no cambia.

El fallo en el *commit* real se prueba con PostgreSQL en
`tests/integration/test_archivos_huerfanos_postgres.py`.
"""

import hashlib
import importlib
import io
import itertools
from pathlib import Path
from unittest import mock

import pytest
from django.conf import settings
from django.core.cache import cache
from rest_framework.test import APIClient

from apps.authentication.adapters.models import Role, User, UserRole
from apps.expedientes.adapters.models import ExpedienteTitulacion, HistorialEstado
from apps.expedientes.services import (
    crear_expediente,
    enviar_expediente,
    iniciar_verificacion,
)
from apps.expedientes.services.transiciones import TransicionNoPermitidaError
from apps.notificaciones.adapters.models import NotificacionInterna
from apps.peticiones.adapters.models import DocumentoEntregado, PeticionDocumental
from apps.peticiones.services import cargar_documento
from apps.verificacion.adapters.models import (
    ChecklistVerification,
    ObservacionAccionable,
)
from apps.verificacion.services import evaluar_checklist

subsanar_mod = importlib.import_module("apps.verificacion.services.subsanar_requisito")

pytestmark = pytest.mark.django_db

E = ExpedienteTitulacion
CARRERA = "aaaaaaaa-1303-4111-8111-111111111111"
FACULTAD = "bbbbbbbb-1303-4111-8111-111111111111"
_CEDULAS = itertools.count(8030000001)
PDF = (
    b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    b"2 0 obj\n<< /Type /Pages /Kids [] /Count 0 >>\nendobj\n"
    b"trailer\n<< /Root 1 0 R >>\n%%EOF\n"
)


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


def _raiz():
    return Path(settings.PRIVATE_MEDIA_ROOT)


def _archivos():
    return sorted(
        str(p.relative_to(_raiz())) for p in _raiz().rglob("*") if p.is_file()
    )


def _sha(ruta):
    return hashlib.sha256((_raiz() / ruta).read_bytes()).hexdigest()


@pytest.fixture(autouse=True)
def _limpiar_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def actores():
    return {
        "estudiante": _usuario("i3t3_est", "ESTUDIANTE"),
        "jurista": _usuario("i3t3_jur", "SECRETARIO_ABOGADO"),
    }


@pytest.fixture
def observado(actores):
    """Expediente OBSERVADA con una versión 1 real del requisito observado."""
    expediente = crear_expediente.execute(actores["estudiante"], CARRERA)
    for peticion in PeticionDocumental.objects.filter(expediente=expediente):
        archivo = io.BytesIO(PDF)
        cargar_documento.execute(
            usuario=actores["estudiante"],
            peticion_id=peticion.pk,
            archivo=archivo,
            nombre_original="v1.pdf",
        )
    enviar_expediente.execute(expediente, actor=actores["estudiante"])
    iniciar_verificacion.execute(expediente.pk, actor=actores["jurista"])
    item = ChecklistVerification.objects.filter(expediente=expediente).first()
    evaluar_checklist.execute(actores["jurista"], item.pk, "OBSERVADO", "Ilegible")
    expediente.refresh_from_db()
    peticion = PeticionDocumental.objects.get(
        expediente=expediente, requisito=item.requisito
    )
    return expediente, item, peticion


def _subsanar(actores, item):
    archivo = io.BytesIO(PDF + b"% v2\n")
    archivo.name = "v2.pdf"
    return _cliente(actores["estudiante"]).post(
        f"/api/v1/checklist/{item.pk}/subsanar/",
        {"archivo": archivo},
        format="multipart",
    )


def _falla_transicion():
    return mock.patch.object(
        subsanar_mod,
        "registrar_transicion",
        side_effect=TransicionNoPermitidaError(
            "simulada", estado_anterior=E.ESTADO_OBSERVADA, estado_nuevo="X"
        ),
    )


def _falla_notificacion():
    return mock.patch.object(
        NotificacionInterna.objects,
        "create",
        side_effect=RuntimeError("fallo BD simulado"),
    )


def _falla_documento():
    return mock.patch.object(
        DocumentoEntregado.objects,
        "create",
        side_effect=RuntimeError("fallo BD simulado"),
    )


@pytest.mark.parametrize(
    "fallo, status, code",
    [
        (_falla_transicion, 400, "transicion_invalida"),
        (_falla_notificacion, 500, None),
        (_falla_documento, 500, None),
    ],
)
def test_fallo_tras_escribir_no_deja_huerfano(observado, actores, fallo, status, code):
    expediente, item, peticion = observado
    antes = _archivos()
    v1 = DocumentoEntregado.objects.get(peticion=peticion, version=1)
    hash_v1 = _sha(v1.archivo_path)
    historial_antes = HistorialEstado.objects.filter(expediente=expediente).count()

    with fallo():
        respuesta = _subsanar(actores, item)

    assert respuesta.status_code == status
    if code:
        assert respuesta.json()["code"] == code
    assert _archivos() == antes
    assert _sha(v1.archivo_path) == hash_v1
    expediente.refresh_from_db()
    item.refresh_from_db()
    v1.refresh_from_db()
    assert expediente.estado == E.ESTADO_OBSERVADA
    assert item.estado_verificacion == "OBSERVADO"
    assert v1.es_vigente is True
    assert DocumentoEntregado.objects.filter(peticion=peticion).count() == 1
    assert (
        ObservacionAccionable.objects.filter(
            expediente=expediente, resuelta=False
        ).count()
        == 1
    )
    assert (
        HistorialEstado.objects.filter(expediente=expediente).count() == historial_antes
    )


def test_subsanacion_correcta_conserva_ambas_versiones(observado, actores):
    expediente, item, peticion = observado
    respuesta = _subsanar(actores, item)

    assert respuesta.status_code == 201
    documentos = DocumentoEntregado.objects.filter(peticion=peticion).order_by(
        "version"
    )
    assert [d.version for d in documentos] == [1, 2]
    referenciados = set(
        DocumentoEntregado.objects.values_list("archivo_path", flat=True)
    )
    assert set(_archivos()) == referenciados
    expediente.refresh_from_db()
    assert expediente.estado == E.ESTADO_EN_VERIFICACION
