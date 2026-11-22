"""`GET /api/v1/perfil-academico/`: contrato, RBAC, IDOR y disponibilidad."""

import pytest
from rest_framework.test import APIClient

from apps.academico.tests.factories import (
    crear_carrera,
    crear_facultad,
    crear_perfil_mock,
)
from apps.authentication.adapters.models import Role, User, UserRole
from apps.expedientes.services import crear_expediente

pytestmark = pytest.mark.django_db

URL = "/api/v1/perfil-academico/"


def _usuario(username, rol, **extra):
    user = User.objects.create_user(username=username, password="x", **extra)
    role, _ = Role.objects.get_or_create(name=rol)
    UserRole.objects.get_or_create(user=user, role=role)
    return user


def _cliente(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def carrera():
    return crear_carrera("EP-CAR", facultad=crear_facultad("EP-FAC"))


@pytest.fixture
def estudiante(carrera):
    user = _usuario("ep_est", "ESTUDIANTE")
    crear_perfil_mock(user, carrera, nombres="Ana", apellidos="Ficticia")
    return user


def test_perfil_validado_contrato_completo(estudiante, carrera):
    respuesta = _cliente(estudiante).get(URL)
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert set(cuerpo) == {
        "estudiante",
        "carrera",
        "facultad",
        "fuente",
        "consultado_en",
        "estado_perfil",
        "perfil_validado",
        "puede_iniciar_tramite",
        "motivos_bloqueo",
    }
    assert cuerpo["estudiante"] == {
        "identificacion": estudiante.cedula,
        "nombres": "Ana",
        "apellidos": "Ficticia",
        "correo_institucional": estudiante.email,
    }
    assert cuerpo["carrera"] == {
        "id": str(carrera.id),
        "codigo": "EP-CAR",
        "nombre": carrera.nombre,
        "activa": True,
    }
    assert cuerpo["facultad"]["id"] == str(carrera.facultad_id)
    assert cuerpo["fuente"]["codigo"] == "MOCK_SGA"
    assert cuerpo["fuente"]["es_simulada"] is True
    assert cuerpo["estado_perfil"] == "VALIDADO"
    assert cuerpo["perfil_validado"] is True
    assert cuerpo["puede_iniciar_tramite"] is True
    assert cuerpo["motivos_bloqueo"] == []
    assert cuerpo["consultado_en"]


def test_expediente_activo_bloquea_inicio_sin_invalidar_perfil(estudiante):
    crear_expediente.execute(estudiante)
    cuerpo = _cliente(estudiante).get(URL).json()
    assert cuerpo["perfil_validado"] is True
    assert cuerpo["puede_iniciar_tramite"] is False
    assert [m["codigo"] for m in cuerpo["motivos_bloqueo"]] == [
        "expediente_activo_existente"
    ]


def test_sin_perfil_asociado_200_con_motivo():
    user = _usuario("ep_sin", "ESTUDIANTE", cedula="9300000001")
    cuerpo = _cliente(user).get(URL).json()
    assert cuerpo["estado_perfil"] == "NO_ASOCIADO"
    assert cuerpo["estudiante"] is None
    assert cuerpo["carrera"] is None
    assert cuerpo["facultad"] is None
    assert cuerpo["perfil_validado"] is False
    assert cuerpo["puede_iniciar_tramite"] is False
    assert cuerpo["motivos_bloqueo"][0]["codigo"] == "perfil_academico_no_asociado"
    assert cuerpo["motivos_bloqueo"][0]["mensaje"]


def test_carrera_inactiva_200_con_motivo():
    user = _usuario("ep_inact", "ESTUDIANTE")
    crear_perfil_mock(user, crear_carrera("EP-INACT", activa=False))
    cuerpo = _cliente(user).get(URL).json()
    assert cuerpo["estado_perfil"] == "CARRERA_INACTIVA"
    assert cuerpo["carrera"]["activa"] is False
    assert cuerpo["puede_iniciar_tramite"] is False


def test_sin_autenticacion_401(db):
    assert APIClient().get(URL).status_code == 401


@pytest.mark.parametrize(
    "rol",
    [
        "SECRETARIA_CARRERA",
        "SECRETARIO_ABOGADO",
        "ANALISTA_APOYO",
        "DECANO",
        "DIRECTOR_CARRERA",
        "RESPONSABLE_DEPENDENCIA",
        "ADMINISTRADOR",
    ],
)
def test_solo_estudiante_403_para_otros_roles(rol):
    user = _usuario(f"ep_{rol.lower()}", rol)
    assert _cliente(user).get(URL).status_code == 403


def test_usuario_sin_rol_403():
    user = User.objects.create_user(username="ep_sin_rol", password="x")
    assert _cliente(user).get(URL).status_code == 403


def test_idor_parametros_ignorados_siempre_perfil_propio(estudiante, carrera):
    """Ni la cédula ni ids en la consulta cambian el perfil devuelto."""
    otro = _usuario("ep_otro", "ESTUDIANTE")
    crear_perfil_mock(otro, crear_carrera("EP-OTRA"), nombres="Otra")
    for consulta in (
        {"cedula": otro.cedula},
        {"identificacion": otro.cedula},
        {"usuario": str(otro.pk)},
        {"carrera_id": str(otro.pk)},
    ):
        cuerpo = _cliente(estudiante).get(URL, consulta).json()
        assert cuerpo["estudiante"]["identificacion"] == estudiante.cedula
        assert cuerpo["carrera"]["codigo"] == "EP-CAR"
        assert otro.cedula not in str(cuerpo)


@pytest.mark.parametrize("metodo", ["post", "put", "patch", "delete"])
def test_solo_lectura(estudiante, metodo):
    respuesta = getattr(_cliente(estudiante), metodo)(URL, {}, format="json")
    assert respuesta.status_code in (403, 405)


def test_fuente_no_configurada_503(estudiante, settings):
    settings.ACADEMIC_PROFILE_PROVIDER = ""
    respuesta = _cliente(estudiante).get(URL)
    assert respuesta.status_code == 503
    assert respuesta.json()["code"] == "servicio_academico_no_configurado"


def test_mock_en_produccion_no_disponible_503(estudiante, settings):
    """El MockSGA no responde en un entorno que no lo permite expresamente."""
    settings.ACADEMIC_PROFILE_PROVIDER = "mock_sga"
    settings.ACADEMIC_PROFILE_MOCK_ALLOWED = False
    respuesta = _cliente(estudiante).get(URL)
    assert respuesta.status_code == 503
    assert respuesta.json()["code"] == "servicio_academico_no_configurado"
    assert estudiante.cedula not in respuesta.content.decode()


def test_fuente_caida_503(estudiante, monkeypatch):
    from apps.academico.adapters import mock_sga

    def falla(self, identificacion):
        raise ConnectionError("sin red")

    monkeypatch.setattr(mock_sga.MockSGAAdapter, "consultar_por_identificacion", falla)
    respuesta = _cliente(estudiante).get(URL)
    assert respuesta.status_code == 503
    assert respuesta.json()["code"] == "servicio_academico_no_disponible"
