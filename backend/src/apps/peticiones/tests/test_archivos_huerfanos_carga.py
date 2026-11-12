"""I-3 (T2): la carga de documentos no deja archivos huérfanos.

- H-I3-01: si falla un paso de BD posterior a la escritura, la BD revierte y
  el archivo creado por la operación se elimina; los documentos previos
  quedan intactos (SHA-256).
- H-I3-04: un nombre multibyte largo se carga (sin 500) y conserva
  `nombre_original`; la descarga verifica el SHA-256.
- H-I3-05 (fuera de alcance, comportamiento protegido): repetir la misma
  carga sigue creando una nueva versión.

El fallo en el *commit* real se prueba con PostgreSQL en
`tests/integration/test_archivos_huerfanos_postgres.py`.
"""

import hashlib
import io
import itertools
from pathlib import Path
from unittest import mock

import pytest
from django.conf import settings
from django.core.cache import cache
from rest_framework.test import APIClient

from apps.authentication.adapters.models import Role, User, UserRole
from apps.expedientes.services import crear_expediente
from apps.peticiones.adapters.models import DocumentoEntregado, PeticionDocumental

pytestmark = pytest.mark.django_db

CARRERA = "aaaaaaaa-1302-4111-8111-111111111111"
FACULTAD = "bbbbbbbb-1302-4111-8111-111111111111"
_CEDULAS = itertools.count(8020000001)
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


def _huerfanos():
    referenciados = set(
        DocumentoEntregado.objects.values_list("archivo_path", flat=True)
    )
    return sorted(set(_archivos()) - referenciados)


def _sha(ruta):
    return hashlib.sha256((_raiz() / ruta).read_bytes()).hexdigest()


@pytest.fixture(autouse=True)
def _limpiar_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def estudiante():
    return _usuario("i3t2_est", "ESTUDIANTE")


@pytest.fixture
def peticion(estudiante):
    expediente = crear_expediente.execute(estudiante, CARRERA)
    return PeticionDocumental.objects.filter(expediente=expediente).first()


def _cargar(estudiante, peticion, contenido=PDF, nombre="doc.pdf"):
    archivo = io.BytesIO(contenido)
    archivo.name = nombre
    return _cliente(estudiante).post(
        f"/api/v1/peticiones/{peticion.pk}/documento/",
        {"archivo": archivo},
        format="multipart",
    )


def _falla_create():
    return mock.patch.object(
        DocumentoEntregado.objects,
        "create",
        side_effect=RuntimeError("fallo BD simulado"),
    )


def _falla_save_peticion():
    real = PeticionDocumental.save

    def save(self, *args, **kwargs):
        if kwargs.get("update_fields") == ["estado_peticion", "fecha_actualizacion"]:
            raise RuntimeError("fallo BD simulado")
        return real(self, *args, **kwargs)

    return mock.patch.object(PeticionDocumental, "save", save)


@pytest.mark.parametrize("fallo", [_falla_create, _falla_save_peticion])
def test_fallo_tras_escribir_no_deja_huerfano(estudiante, peticion, fallo):
    with fallo():
        respuesta = _cargar(estudiante, peticion)

    assert respuesta.status_code == 500
    peticion.refresh_from_db()
    assert peticion.estado_peticion == "PENDIENTE"
    assert not DocumentoEntregado.objects.filter(peticion=peticion).exists()
    assert _archivos() == []


def test_fallo_no_toca_la_version_previa(estudiante, peticion):
    assert _cargar(estudiante, peticion).status_code == 201
    previa = DocumentoEntregado.objects.get(peticion=peticion)
    hash_previa = _sha(previa.archivo_path)

    cache.clear()
    with _falla_create():
        assert _cargar(estudiante, peticion, contenido=PDF + b"\n").status_code == 500

    assert _archivos() == [previa.archivo_path]
    assert _sha(previa.archivo_path) == hash_previa
    previa.refresh_from_db()
    assert previa.es_vigente is True
    assert _huerfanos() == []


def test_nombre_multibyte_largo_se_carga_y_descarga(estudiante, peticion):
    nombre = "é" * 200 + ".pdf"
    respuesta = _cargar(estudiante, peticion, nombre=nombre)

    assert respuesta.status_code == 201
    documento = DocumentoEntregado.objects.get(peticion=peticion)
    assert documento.nombre_original == nombre
    fisico = documento.archivo_path.rsplit("/", 1)[-1]
    assert len(fisico.encode("utf-8")) <= 255 and fisico.endswith(".pdf")
    descarga = _cliente(estudiante).get(f"/api/v1/peticiones/{peticion.pk}/documento/")
    assert descarga.status_code == 200
    assert b"".join(descarga.streaming_content) == PDF


def test_h_i3_05_carga_repetida_sigue_creando_version(estudiante, peticion):
    """Comportamiento protegido: H-I3-05 queda fuera de alcance."""
    assert _cargar(estudiante, peticion).status_code == 201
    cache.clear()
    assert _cargar(estudiante, peticion).status_code == 201

    versiones = list(
        DocumentoEntregado.objects.filter(peticion=peticion)
        .order_by("version")
        .values_list("version", "es_vigente", "hash_sha256")
    )
    assert [(v, vig) for v, vig, _ in versiones] == [(1, False), (2, True)]
    assert versiones[0][2] == versiones[1][2]
    assert len(_archivos()) == 2 and _huerfanos() == []
