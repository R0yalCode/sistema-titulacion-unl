"""Pruebas de integracion de POST /api/v1/expedientes/{id}/enviar/ (T016).

Fuente de requisitos: HU-004, RF-002, RF-003, RN-002, RN-010, EX-006,
EX-003 y CA-001 (specify.md): envio con 5 requisitos con documento en
firme -> 200 con fecha_recepcion UTC inmutable, numero_providencia
correlativo y fecha_limite_atencion de 8 dias laborables; envio
incompleto -> 422; reenvio/transicion invalida -> 400; expediente ajeno
-> 404 (IDOR); rol sin concesion -> 403 (RBAC).
"""

import re

import pytest
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.test import APIClient

from apps.authentication.adapters.models import Role, User, UserRole
from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.expedientes.domain.plazo_calculator import PlazoLaboralCalculator
from apps.expedientes.services import crear_expediente
from apps.peticiones.adapters.models import PeticionDocumental

PASSWORD = "pwd_seguro_t016"
CARRERA_1 = "aaaaaaaa-c111-4111-8111-111111111111"
CARRERA_2 = "aaaaaaaa-c222-4222-8222-222222222222"
ESTADOS_CON_DOCUMENTO = ("CARGADO", "LEGALIZADO", "VERIFICADO")


def crear_estudiante(username):
    user = User.objects.create_user(
        username=username, password=PASSWORD, carrera_id=CARRERA_1
    )
    role, _ = Role.objects.get_or_create(name="ESTUDIANTE")
    UserRole.objects.get_or_create(user=user, role=role)
    return user


def cliente(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture(name="borrador")
def fixture_borrador(db):
    """Expediente en BORRADOR con sus 5 peticiones base."""
    user = crear_estudiante("t016_estudiante_a")
    return user, crear_expediente.execute(user, CARRERA_1)


def marcar_requisitos_cargados(expediente, estados=None):
    estados = estados or ("CARGADO",) * 5
    for peticion, estado in zip(
        PeticionDocumental.objects.filter(expediente=expediente).order_by(
            "requisito__codigo_requisito"
        ),
        estados,
    ):
        peticion.estado_peticion = estado
        peticion.save()


def enviar(client, expediente):
    return client.post(f"/api/v1/expedientes/{expediente.pk}/enviar/", format="json")


def test_envio_completo_200_con_timestamp_y_plazo(borrador):
    """CA-001 / RF-002 / RF-003: 200 + ENVIADA + UTC + providencia + plazo."""
    user, expediente = borrador
    marcar_requisitos_cargados(expediente)
    respuesta = enviar(cliente(user), expediente)

    assert respuesta.status_code == status.HTTP_200_OK
    cuerpo = respuesta.json()
    assert cuerpo["estado"] == ExpedienteTitulacion.ESTADO_ENVIADA
    assert cuerpo["numero_providencia"] == "PROV-%d-0001" % timezone.now().year
    assert re.match(r"^PROV-\d{4}-\d{4}$", cuerpo["numero_providencia"])
    fecha_recepcion = parse_datetime(cuerpo["fecha_recepcion"])
    assert fecha_recepcion is not None
    assert fecha_recepcion.utcoffset() == timezone.timedelta(0)
    limite = parse_datetime(cuerpo["fecha_limite_atencion"])
    esperado = PlazoLaboralCalculator().calcular_fecha_limite(fecha_recepcion.date(), 8)
    assert limite.date() == esperado
    assert limite.date() > fecha_recepcion.date()

    expediente.refresh_from_db()
    assert expediente.fecha_recepcion is not None
    assert timezone.is_aware(expediente.fecha_recepcion)
    assert expediente.fecha_limite_atencion is not None
    assert expediente.dias_laborables_acumulados == 0


def test_envio_incompleto_422_detalla_requisito(borrador):
    """T016 criterio: envio incompleto -> 422 y expediente sigue BORRADOR."""
    user, expediente = borrador
    marcar_requisitos_cargados(
        expediente,
        ("CARGADO", "CARGADO", "PENDIENTE", "LEGALIZADO", "SOLICITADO"),
    )
    respuesta = enviar(cliente(user), expediente)

    assert respuesta.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    detalle = str(respuesta.json()).lower()
    assert "art235-03" in detalle
    assert "art235-05" in detalle
    expediente.refresh_from_db()
    assert expediente.estado == ExpedienteTitulacion.ESTADO_BORRADOR
    assert expediente.fecha_recepcion is None
    assert expediente.numero_providencia is None


def test_reenvio_transicion_invalida_400(borrador):
    """EX-006: solo BORRADOR puede enviarse; reenvio -> 400 (RN-010)."""
    user, expediente = borrador
    marcar_requisitos_cargados(expediente)
    primera = enviar(cliente(user), expediente)
    assert primera.status_code == status.HTTP_200_OK
    marca_inmutable = primera.json()["fecha_recepcion"]

    segunda = enviar(cliente(user), expediente)
    assert segunda.status_code == status.HTTP_400_BAD_REQUEST

    expediente.refresh_from_db()
    assert expediente.estado == ExpedienteTitulacion.ESTADO_ENVIADA
    assert parse_datetime(marca_inmutable) == expediente.fecha_recepcion
    assert expediente.numero_providencia == primera.json()["numero_providencia"]


def test_expediente_ajeno_404_idor(db, borrador):
    """EX-003 / RNF-003: alcance own; expediente de otro estudiante -> 404."""
    otro = crear_estudiante("t016_estudiante_b")
    _, expediente = borrador
    respuesta = enviar(cliente(otro), expediente)
    assert respuesta.status_code == status.HTTP_404_NOT_FOUND
    expediente.refresh_from_db()
    assert expediente.estado == ExpedienteTitulacion.ESTADO_BORRADOR


def test_rol_sin_concesion_403(db, borrador):
    user, expediente = borrador
    abogado = User.objects.create_user(username="t016_secretario", password=PASSWORD)
    role, _ = Role.objects.get_or_create(name="SECRETARIO_ABOGADO")
    UserRole.objects.get_or_create(user=abogado, role=role)
    respuesta = enviar(cliente(abogado), expediente)
    assert respuesta.status_code == status.HTTP_403_FORBIDDEN


def test_sin_autenticacion_401(db):
    client = APIClient()
    respuesta = client.post(
        f"/api/v1/expedientes/{'aaaaaaaa-d001-4001-8001-000000000001'}/enviar/",
        format="json",
    )
    assert respuesta.status_code == status.HTTP_401_UNAUTHORIZED


def test_numeros_providencia_correlativos(db):
    """DEC-03 / AP-02: correlativo por anio entre expedientes distintos."""
    marcos = []
    for idx in ("a", "b"):
        user = crear_estudiante(f"t016_prov_{idx}")
        carrera = CARRERA_1 if idx == "a" else CARRERA_2
        expediente = crear_expediente.execute(user, carrera)
        marcar_requisitos_cargados(expediente)
        marcos.append((user, expediente))

    respuesta_a = enviar(cliente(marcos[0][0]), marcos[0][1])
    respuesta_b = enviar(cliente(marcos[1][0]), marcos[1][1])
    assert respuesta_a.status_code == respuesta_b.status_code == 200
    anio = timezone.now().year
    assert respuesta_a.json()["numero_providencia"] == f"PROV-{anio}-0001"
    assert respuesta_b.json()["numero_providencia"] == f"PROV-{anio}-0002"
