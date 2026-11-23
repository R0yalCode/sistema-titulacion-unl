"""Pruebas de integracion del endpoint POST /api/v1/expedientes/ (T015; V-03).

Fuente de requisitos: HU-001, RF-001 (specify.md), criterio de
finalizacion de T015: 201 Created con el objeto expediente y las 5
peticiones documentales base del Art. 235 inicializadas en PENDIENTE;
caso negativo por expediente activo previo (400) y RBAC (401/403).

V-03 (MockSGA, 2026-11-22): el cuerpo es vacío; la carrera sale del perfil
académico validado y la facultad, de la carrera. El cliente no puede fijar
`carrera_id`, `facultad_id` ni `estudiante_id`.
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.academico.tests.factories import (
    crear_carrera,
    crear_facultad,
    crear_perfil_mock,
)
from apps.authentication.adapters.models import Role, User, UserRole
from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.notificaciones.adapters.models import EventoAuditoria
from apps.peticiones.adapters.models import (
    ESTADO_PENDIENTE,
    CatalogoDocumental,
    PeticionDocumental,
)

URL_EXPEDIENTES = "/api/v1/expedientes/"
PASSWORD = "pwd_seguro_t015"
CARRERA_1 = "aaaaaaaa-c111-4111-8111-111111111111"
CARRERA_2 = "aaaaaaaa-c222-4222-8222-222222222222"
FACULTAD_1 = "bbbbbbbb-f111-4111-8111-111111111111"

CODIGOS_BASE_ESPERADOS = [
    "ART235-01-RECORD-ACADEMICO",
    "ART235-02-PRACTICAS-VINCULACION",
    "ART235-03-IDIOMA-B1",
    "ART235-04-DIRECTOR-TRABAJO",
    "ART235-05-TESORERIA",
]


def _estudiante(username):
    user = User.objects.create_user(username=username, password=PASSWORD)
    role, _ = Role.objects.get_or_create(name="ESTUDIANTE")
    UserRole.objects.get_or_create(user=user, role=role)
    return user


@pytest.fixture(name="carrera")
def fixture_carrera(db):
    facultad = crear_facultad("T015-FAC", id=FACULTAD_1)
    return crear_carrera("T015-CARRERA", id=CARRERA_1, facultad=facultad)


@pytest.fixture(name="usuario_estudiante")
def fixture_usuario_estudiante(db, carrera):
    user = _estudiante("t015_estudiante_a")
    crear_perfil_mock(user, carrera)
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


def test_crear_expediente_201_con_5_peticiones_pendiente(usuario_estudiante):
    """HU-001 / RF-001: 201 + expediente BORRADOR + 5 peticiones PENDIENTE."""
    client = auth_client(usuario_estudiante)
    respuesta = client.post(URL_EXPEDIENTES, {}, format="json")

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


def test_facultad_se_deriva_de_la_carrera(usuario_estudiante):
    """La facultad del expediente es la de la carrera, no la de la cuenta."""
    respuesta = auth_client(usuario_estudiante).post(URL_EXPEDIENTES, {}, format="json")
    assert respuesta.status_code == status.HTTP_201_CREATED
    expediente = ExpedienteTitulacion.objects.get(estudiante=usuario_estudiante)
    assert str(expediente.carrera_id) == CARRERA_1
    assert str(expediente.facultad_id) == FACULTAD_1


def test_creacion_auditada_con_asociacion_y_fuente(usuario_estudiante):
    """Un único EXPEDIENTE_CREADO con carrera, facultad y fuente del perfil."""
    auth_client(usuario_estudiante).post(URL_EXPEDIENTES, {}, format="json")
    eventos = EventoAuditoria.objects.filter(
        accion=EventoAuditoria.Accion.EXPEDIENTE_CREADO
    )
    assert eventos.count() == 1
    detalles = eventos.get().detalles
    assert detalles["carrera_id"] == CARRERA_1
    assert detalles["facultad_id"] == FACULTAD_1
    assert detalles["carrera_codigo"] == "T015-CARRERA"
    assert detalles["fuente_perfil"] == "MOCK_SGA"
    assert detalles["fuente_simulada"] is True
    assert usuario_estudiante.cedula not in str(detalles)


def test_creacion_rechazada_con_expediente_activo_previo_400(usuario_estudiante):
    """HU-001: sin expedientes activos en curso; activo previo -> 400."""
    client = auth_client(usuario_estudiante)
    primera = client.post(URL_EXPEDIENTES, {}, format="json")
    assert primera.status_code == status.HTTP_201_CREATED

    segunda = client.post(URL_EXPEDIENTES, {}, format="json")
    assert segunda.status_code == status.HTTP_400_BAD_REQUEST
    assert segunda.json()["code"] == "expediente_activo_existente"
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
    respuesta = client.post(URL_EXPEDIENTES, {}, format="json")
    assert respuesta.status_code == status.HTTP_201_CREATED
    assert respuesta.json()["carrera_id"] == CARRERA_1


def test_rol_sin_concesion_403(usuario_secretario_abogado):
    """Matriz RBAC 6.2: POST expedientes concedido solo a ESTUDIANTE/ADMIN."""
    client = auth_client(usuario_secretario_abogado)
    respuesta = client.post(URL_EXPEDIENTES, {}, format="json")
    assert respuesta.status_code == status.HTTP_403_FORBIDDEN
    assert ExpedienteTitulacion.objects.count() == 0


def test_sin_autenticacion_401(db):
    client = APIClient()
    respuesta = client.post(URL_EXPEDIENTES, {}, format="json")
    assert respuesta.status_code == status.HTTP_401_UNAUTHORIZED
    assert ExpedienteTitulacion.objects.count() == 0


@pytest.mark.parametrize(
    "cuerpo",
    [
        {"carrera_id": CARRERA_2},
        {"carrera_id": CARRERA_1},
        {"carrera_id": "no-es-uuid"},
        {"facultad_id": FACULTAD_1},
        {"estudiante_id": "cccccccc-0000-4000-8000-000000000000"},
    ],
)
def test_cliente_no_puede_fijar_carrera_facultad_ni_estudiante_400(
    usuario_estudiante, cuerpo
):
    """Manipulación del UUID (IDOR de clasificación): siempre 400, sin efectos."""
    respuesta = auth_client(usuario_estudiante).post(
        URL_EXPEDIENTES, cuerpo, format="json"
    )
    assert respuesta.status_code == status.HTTP_400_BAD_REQUEST
    assert respuesta.json()["code"] == "campo_no_permitido"
    assert ExpedienteTitulacion.objects.count() == 0


def test_sin_perfil_asociado_422(carrera):
    user = _estudiante("t015_sin_perfil")
    user.cedula = "9100000999"
    user.save(update_fields=["cedula"])
    respuesta = auth_client(user).post(URL_EXPEDIENTES, {}, format="json")
    assert respuesta.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert respuesta.json()["code"] == "perfil_academico_no_asociado"
    assert ExpedienteTitulacion.objects.count() == 0


def test_sin_identificacion_422(db):
    user = _estudiante("t015_sin_cedula")
    respuesta = auth_client(user).post(URL_EXPEDIENTES, {}, format="json")
    assert respuesta.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert respuesta.json()["code"] == "perfil_academico_incompleto"


def test_perfil_incompleto_422(carrera):
    user = _estudiante("t015_incompleto")
    crear_perfil_mock(user, carrera, codigo_carrera="")
    respuesta = auth_client(user).post(URL_EXPEDIENTES, {}, format="json")
    assert respuesta.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert respuesta.json()["code"] == "perfil_academico_incompleto"
    assert ExpedienteTitulacion.objects.count() == 0


def test_perfil_inconsistente_422(carrera):
    user = _estudiante("t015_inconsistente")
    crear_perfil_mock(user, carrera, codigo_facultad="OTRA-FAC")
    respuesta = auth_client(user).post(URL_EXPEDIENTES, {}, format="json")
    assert respuesta.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert respuesta.json()["code"] == "perfil_academico_inconsistente"
    assert ExpedienteTitulacion.objects.count() == 0


def test_carrera_inactiva_422(db):
    inactiva = crear_carrera("T015-INACTIVA", activa=False)
    user = _estudiante("t015_inactiva")
    crear_perfil_mock(user, inactiva)
    respuesta = auth_client(user).post(URL_EXPEDIENTES, {}, format="json")
    assert respuesta.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert respuesta.json()["code"] == "carrera_inactiva"
    assert ExpedienteTitulacion.objects.count() == 0


def test_carrera_desactivada_entre_consulta_y_creacion_422(usuario_estudiante, carrera):
    """La vigencia se revalida dentro de la transacción (sin efectos)."""
    from apps.academico.services.perfil_academico import (
        get_academic_profile_service,
    )
    from apps.expedientes.services import crear_expediente

    servicio = get_academic_profile_service()
    perfil = servicio.obtener_perfil(usuario_estudiante)

    class ServicioCongelado:
        def obtener_perfil(self, usuario):
            return perfil

    carrera.activa = False
    carrera.save(update_fields=["activa"])
    with pytest.raises(crear_expediente.CarreraNoVigenteError):
        crear_expediente.execute(usuario_estudiante, ServicioCongelado())
    assert ExpedienteTitulacion.objects.count() == 0


def test_fuente_no_configurada_503(usuario_estudiante, settings):
    settings.ACADEMIC_PROFILE_PROVIDER = ""
    respuesta = auth_client(usuario_estudiante).post(URL_EXPEDIENTES, {}, format="json")
    assert respuesta.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert respuesta.json()["code"] == "servicio_academico_no_configurado"
    assert ExpedienteTitulacion.objects.count() == 0


def test_numero_expediente_correlativo(carrera):
    """RF-001: correlativo `EXP-{anio}-{n:04d}` secuencial por anio."""
    clientes = []
    for idx in range(2):
        user = _estudiante(f"t015_corr_{idx}")
        crear_perfil_mock(user, carrera)
        clientes.append(auth_client(user))

    primera = clientes[0].post(URL_EXPEDIENTES, {}, format="json")
    segunda = clientes[1].post(URL_EXPEDIENTES, {}, format="json")
    assert primera.json()["numero_expediente"].endswith("-0001")
    assert segunda.json()["numero_expediente"].endswith("-0002")


def test_casos_de_uso_atomicidad_rollback(db, usuario_estudiante):
    """Si la inicializacion falla, no queda expediente ni peticion parcial."""
    from apps.expedientes.services import crear_expediente

    CatalogoDocumental.objects.update(activo=False)

    with pytest.raises(crear_expediente.CatalogoIncompletoError):
        crear_expediente.execute(usuario_estudiante)
    assert ExpedienteTitulacion.objects.count() == 0
    assert PeticionDocumental.objects.count() == 0
