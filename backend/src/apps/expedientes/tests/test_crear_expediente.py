"""Pruebas de integracion del endpoint POST /api/v1/expedientes/ (T015).

Fuente de requisitos: HU-001, RF-001 (specify.md), criterio de
finalizacion de T015: 201 Created con el objeto expediente y las 5
peticiones documentales base del Art. 235 inicializadas en PENDIENTE;
caso negativo por expediente activo previo (400) y RBAC (401/403).
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.authentication.adapters.models import Role, User, UserRole
from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.peticiones.adapters.models import (
    ESTADO_PENDIENTE,
    CatalogoDocumental,
    PeticionDocumental,
)

URL_EXPEDIENTES = "/api/v1/expedientes/"
PASSWORD = "pwd_seguro_t015"
CARRERA_1 = "aaaaaaaa-c111-4111-8111-111111111111"
CARRERA_2 = "aaaaaaaa-c222-4222-8222-222222222222"

CODIGOS_BASE_ESPERADOS = [
    "ART235-01-RECORD-ACADEMICO",
    "ART235-02-PRACTICAS-VINCULACION",
    "ART235-03-IDIOMA-B1",
    "ART235-04-DIRECTOR-TRABAJO",
    "ART235-05-TESORERIA",
]


@pytest.fixture(name="usuario_estudiante")
def fixture_usuario_estudiante(db):
    user = User.objects.create_user(
        username="t015_estudiante_a",
        password=PASSWORD,
        carrera_id=CARRERA_1,
    )
    role, _ = Role.objects.get_or_create(name="ESTUDIANTE")
    UserRole.objects.get_or_create(user=user, role=role)
    return user


@pytest.fixture(name="usuario_secretario_abogado")
def fixture_usuario_secretario(db):
    user = User.objects.create_user(
        username="t015_secretario_abogado", password=PASSWORD
    )
    role, _ = Role.objects.get_or_create(name="SECRETARIO_ABOGADO")
    UserRole.objects.get_or_create(user=user, role=role)
    return user


def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def _cuerpo_creacion(carrera_id=CARRERA_1):
    return {"carrera_id": str(carrera_id)}


def test_crear_expediente_201_con_5_peticiones_pendiente(usuario_estudiante):
    """HU-001 / RF-001: 201 + expediente BORRADOR + 5 peticiones PENDIENTE."""
    client = auth_client(usuario_estudiante)
    respuesta = client.post(URL_EXPEDIENTES, _cuerpo_creacion(), format="json")

    assert respuesta.status_code == status.HTTP_201_CREATED
    cuerpo = respuesta.json()
    assert cuerpo["estado"] == ExpedienteTitulacion.ESTADO_BORRADOR
    assert cuerpo["activa"] is True
    assert cuerpo["carrera_id"] == CARRERA_1
    assert cuerpo["numero_expediente"].startswith("EXP-")
    assert len(cuerpo["peticiones"]) == 5
    assert all(
        peticion["estado_peticion"] == ESTADO_PENDIENTE
        for peticion in cuerpo["peticiones"]
    )
    assert (
        sorted(peticion["requisito_codigo"] for peticion in cuerpo["peticiones"])
        == CODIGOS_BASE_ESPERADOS
    )

    expediente = ExpedienteTitulacion.objects.get(estudiante=usuario_estudiante)
    assert ExpedienteTitulacion.objects.count() == 1
    assert expediente.estado == ExpedienteTitulacion.ESTADO_BORRADOR
    assert PeticionDocumental.objects.filter(expediente=expediente).count() == 5
    assert expediente.fecha_recepcion is None
    assert expediente.fecha_limite_atencion is None


def test_creacion_rechazada_con_expediente_activo_previo_400(usuario_estudiante):
    """HU-001: sin expedientes activos en curso; activo previo -> 400."""
    client = auth_client(usuario_estudiante)
    primera = client.post(URL_EXPEDIENTES, _cuerpo_creacion(), format="json")
    assert primera.status_code == status.HTTP_201_CREATED

    segunda = client.post(URL_EXPEDIENTES, _cuerpo_creacion(), format="json")
    assert segunda.status_code == status.HTTP_400_BAD_REQUEST
    assert "activo" in str(segunda.json()).lower()
    assert ExpedienteTitulacion.objects.count() == 1


def test_permite_nuevo_expediente_si_previo_inactivo(usuario_estudiante):
    """RN-001: solo los expedientes activos bloquean una nueva solicitud."""
    ExpedienteTitulacion.objects.create(
        numero_expediente="EXP-2026-9999",
        estudiante=usuario_estudiante,
        carrera_id=CARRERA_2,
        activa=False,
    )
    client = auth_client(usuario_estudiante)
    respuesta = client.post(URL_EXPEDIENTES, _cuerpo_creacion(), format="json")
    assert respuesta.status_code == status.HTTP_201_CREATED
    assert respuesta.json()["carrera_id"] == CARRERA_1


def test_rol_sin_concesion_403(usuario_secretario_abogado):
    """Matriz RBAC 6.2: POST expedientes concedido solo a ESTUDIANTE/ADMIN."""
    client = auth_client(usuario_secretario_abogado)
    respuesta = client.post(URL_EXPEDIENTES, _cuerpo_creacion(), format="json")
    assert respuesta.status_code == status.HTTP_403_FORBIDDEN
    assert ExpedienteTitulacion.objects.count() == 0


def test_sin_autenticacion_401(db):
    client = APIClient()
    respuesta = client.post(URL_EXPEDIENTES, _cuerpo_creacion(), format="json")
    assert respuesta.status_code == status.HTTP_401_UNAUTHORIZED
    assert ExpedienteTitulacion.objects.count() == 0


@pytest.mark.parametrize(
    "cuerpo",
    [
        {},
        {"carrera_id": "no-es-uuid"},
        {"carrera_id": "!@#$%"},
    ],
)
def test_carrera_id_invalida_400(usuario_estudiante, cuerpo):
    client = auth_client(usuario_estudiante)
    respuesta = client.post(URL_EXPEDIENTES, cuerpo, format="json")
    assert respuesta.status_code == status.HTTP_400_BAD_REQUEST
    assert ExpedienteTitulacion.objects.count() == 0


def test_numero_expediente_correlativo(db):
    """RF-001: correlativo `EXP-{anio}-{n:04d}` secuencial por anio."""
    users = []
    for idx in range(2):
        user = User.objects.create_user(username=f"t015_corr_{idx}", password=PASSWORD)
        role, _ = Role.objects.get_or_create(name="ESTUDIANTE")
        UserRole.objects.get_or_create(user=user, role=role)
        users.append(user)

    clientes = [auth_client(u) for u in users]
    primera = clientes[0].post(URL_EXPEDIENTES, _cuerpo_creacion(), format="json")
    segunda = clientes[1].post(
        URL_EXPEDIENTES,
        {"carrera_id": str(CARRERA_2)},
        format="json",
    )
    assert primera.json()["numero_expediente"].endswith("-0001")
    assert segunda.json()["numero_expediente"].endswith("-0002")


def test_casos_de_uso_atomicidad_rollback(db, usuario_estudiante):
    """Si la inicializacion falla, no queda expediente ni peticion parcial."""
    from apps.expedientes.services import crear_expediente

    CatalogoDocumental.objects.update(activo=False)

    with pytest.raises(crear_expediente.CatalogoIncompletoError):
        crear_expediente.execute(usuario_estudiante, CARRERA_1)
    assert ExpedienteTitulacion.objects.count() == 0
    assert PeticionDocumental.objects.count() == 0
