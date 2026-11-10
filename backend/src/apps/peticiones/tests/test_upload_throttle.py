"""Pruebas de SEC-T008: throttling de carga de documentos (DEC-003: 10/hora/usuario).

Cada petición usada aquí es desechable (un CatalogoDocumental + PeticionDocumental
por carga), porque cargar_documento.execute() solo admite un documento por
petición mientras esta siga en PENDIENTE/SOLICITADO/OBSERVADO; esto aísla la
prueba de throttling de la máquina de estados de negocio (no son la misma cosa).
"""

import io
import uuid

import pytest
from django.core.cache import cache
from rest_framework.test import APIClient

from apps.authentication.adapters.models import ROLE_ESTUDIANTE, Role, User, UserRole
from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.peticiones.adapters.models import (
    ESTADO_PENDIENTE,
    CatalogoDocumental,
    PeticionDocumental,
)

pytestmark = pytest.mark.django_db

CARRERA_1 = "11111111-1111-1111-1111-111111111111"
FACULTAD_1 = "22222222-2222-2222-2222-222222222222"
PASSWORD = "pass1234"

PDF_VALIDO = (
    b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n"
    b"2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n"
    b"3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources"
    b"<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>\nendobj\n"
    b"4 0 obj\n<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>\nendobj\n"
    b"5 0 obj\n<</Length 44>>\nstream\nBT /F1 24 Tf 100 700 Td (Test) Tj ET\n"
    b"endstream\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n"
    b"0000000058 00000 n \n0000000115 00000 n \n0000000218 00000 n \n"
    b"0000000277 00000 n \ntrailer\n<</Size 6/Root 1 0 R>>\nstartxref\n347\n%%EOF"
)


@pytest.fixture(autouse=True)
def limpiar_cache_throttle():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def rol_estudiante():
    role, _ = Role.objects.get_or_create(name=ROLE_ESTUDIANTE)
    return role


def _crear_estudiante(username, rol_estudiante):
    return User.objects.create_user(
        username=username,
        email=f"{username}@test.com",
        password=PASSWORD,
        cedula=f"{abs(hash(username)) % 10**10:010d}",
        carrera_id=CARRERA_1,
        facultad_id=FACULTAD_1,
    )


def _crear_peticiones_pendientes(estudiante, cantidad):
    expediente = ExpedienteTitulacion.objects.create(
        numero_expediente=f"EXP-THR-{estudiante.username}-{uuid.uuid4().hex[:8]}",
        estudiante=estudiante,
        carrera_id=CARRERA_1,
        facultad_id=FACULTAD_1,
        estado=ExpedienteTitulacion.ESTADO_BORRADOR,
        activa=True,
    )
    peticiones = []
    for i in range(cantidad):
        requisito = CatalogoDocumental.objects.create(
            codigo_requisito=f"THR-{estudiante.username}-{uuid.uuid4().hex[:8]}-{i}",
            nombre=f"Requisito throttle {i}",
            rol_emisor_sugerido="SECRETARIA_CARRERA",
            activo=True,
        )
        peticiones.append(
            PeticionDocumental.objects.create(
                expediente=expediente,
                requisito=requisito,
                estado_peticion=ESTADO_PENDIENTE,
                dependencia_emisora="SECRETARIA_CARRERA",
            )
        )
    return peticiones


def _subir(client, peticion_id, nombre):
    archivo = io.BytesIO(PDF_VALIDO)
    archivo.name = nombre
    url = f"/api/v1/peticiones/{peticion_id}/documento/"
    return client.post(url, {"archivo": archivo}, format="multipart")


def test_document_upload_throttle_allows_10_per_hour(rol_estudiante):
    estudiante = _crear_estudiante("throttle_10ok", rol_estudiante)
    UserRole.objects.create(user=estudiante, role=rol_estudiante)
    peticiones = _crear_peticiones_pendientes(estudiante, 10)
    client = APIClient()
    client.force_authenticate(user=estudiante)

    for i, peticion in enumerate(peticiones):
        respuesta = _subir(client, peticion.id, f"doc{i}.pdf")
        assert respuesta.status_code == 201, respuesta.data


def test_document_upload_throttle_11th_returns_429(rol_estudiante):
    estudiante = _crear_estudiante("throttle_11", rol_estudiante)
    UserRole.objects.create(user=estudiante, role=rol_estudiante)
    peticiones = _crear_peticiones_pendientes(estudiante, 11)
    client = APIClient()
    client.force_authenticate(user=estudiante)

    for i, peticion in enumerate(peticiones[:10]):
        assert _subir(client, peticion.id, f"doc{i}.pdf").status_code == 201

    respuesta_11 = _subir(client, peticiones[10].id, "doc10.pdf")
    assert respuesta_11.status_code == 429


def test_document_upload_throttle_per_user_isolation(rol_estudiante):
    estudiante_a = _crear_estudiante("throttle_a", rol_estudiante)
    UserRole.objects.create(user=estudiante_a, role=rol_estudiante)
    estudiante_b = _crear_estudiante("throttle_b", rol_estudiante)
    UserRole.objects.create(user=estudiante_b, role=rol_estudiante)

    peticiones_a = _crear_peticiones_pendientes(estudiante_a, 11)
    peticiones_b = _crear_peticiones_pendientes(estudiante_b, 1)

    client_a = APIClient()
    client_a.force_authenticate(user=estudiante_a)
    for i, peticion in enumerate(peticiones_a[:10]):
        assert _subir(client_a, peticion.id, f"a{i}.pdf").status_code == 201
    assert _subir(client_a, peticiones_a[10].id, "a_extra.pdf").status_code == 429

    client_b = APIClient()
    client_b.force_authenticate(user=estudiante_b)
    assert _subir(client_b, peticiones_b[0].id, "b0.pdf").status_code == 201


def test_document_upload_throttle_resets_after_window(rol_estudiante):
    """Simula el fin de la ventana de 1 hora limpiando la cache de throttle
    (equivalente funcional a esperar 61 minutos; no se espera tiempo real)."""
    estudiante = _crear_estudiante("throttle_reset", rol_estudiante)
    UserRole.objects.create(user=estudiante, role=rol_estudiante)
    peticiones = _crear_peticiones_pendientes(estudiante, 11)
    client = APIClient()
    client.force_authenticate(user=estudiante)

    for i, peticion in enumerate(peticiones[:10]):
        assert _subir(client, peticion.id, f"r{i}.pdf").status_code == 201
    assert _subir(client, peticiones[10].id, "r10.pdf").status_code == 429

    cache.clear()

    extra = _crear_peticiones_pendientes(estudiante, 1)[0]
    assert _subir(client, extra.id, "r_reset.pdf").status_code == 201
