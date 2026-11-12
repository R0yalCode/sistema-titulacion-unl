"""PLB-E1-04 (T1b): errores de dominio de `expedientes` sin 500 genéricos.

Cada prueba comprueba la respuesta externa: status HTTP + JSON
`{"detail", "code"}`, y la ausencia de efectos cuando la operación falla.
Endpoints: crear, enviar, iniciar-verificacion y observar.
"""

import itertools
import uuid
from unittest import mock

import pytest
from django.core.cache import cache
from rest_framework.test import APIClient

from apps.authentication.adapters.models import Role, User, UserRole
from apps.expedientes.adapters.models import ExpedienteTitulacion, HistorialEstado
from apps.expedientes.services import (
    crear_expediente,
    enviar_expediente,
    iniciar_verificacion,
    transiciones,
)
from apps.expedientes.services.transiciones import (
    TransicionNoPermitidaError,
    registrar_transicion,
    transicion_permitida,
)
from apps.peticiones.adapters.models import CatalogoDocumental, PeticionDocumental
from apps.verificacion.adapters.models import ObservacionAccionable
from apps.verificacion.services import registrar_observacion
from core.adapters import api_errors

pytestmark = pytest.mark.django_db

E = ExpedienteTitulacion
CARRERA = "aaaaaaaa-e104-4111-8111-111111111111"
FACULTAD = "bbbbbbbb-e104-4111-8111-111111111111"
_CEDULAS = itertools.count(4010000001)


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


@pytest.fixture(autouse=True)
def _limpiar_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def estudiante():
    return _usuario("e104_est", "ESTUDIANTE")


@pytest.fixture
def jurista():
    return _usuario("e104_jur", "SECRETARIO_ABOGADO")


@pytest.fixture
def borrador(estudiante):
    return crear_expediente.execute(estudiante, CARRERA)


def _cargar(expediente):
    PeticionDocumental.objects.filter(expediente=expediente).update(
        estado_peticion="CARGADO"
    )


@pytest.fixture
def enviado(borrador, estudiante):
    _cargar(borrador)
    return enviar_expediente.execute(borrador, actor=estudiante)


@pytest.fixture
def en_verificacion(enviado, jurista):
    return iniciar_verificacion.execute(enviado.pk, actor=jurista)


def _desactivar_un_requisito_base():
    requisito = CatalogoDocumental.objects.filter(
        es_obligatorio_base=True, fase="FASE_1", activo=True
    ).first()
    requisito.activo = False
    requisito.save(update_fields=["activo"])


# --- T1a: transiciones ------------------------------------------------------


def test_transicion_permitida_solo_lee_la_tabla():
    copia = dict(transiciones.TRANSICIONES_PERMITIDAS)
    assert transicion_permitida(E.ESTADO_ENVIADA, E.ESTADO_EN_VERIFICACION)
    assert not transicion_permitida(E.ESTADO_OBSERVADA, E.ESTADO_INFORME_EMITIDO)
    assert transiciones.TRANSICIONES_PERMITIDAS == copia


def test_error_de_transicion_expone_estados(borrador, estudiante):
    with pytest.raises(TransicionNoPermitidaError) as info:
        registrar_transicion(
            borrador, E.ESTADO_DECLARADA_APTA, estudiante, origen="prueba"
        )
    assert info.value.estado_anterior == E.ESTADO_BORRADOR
    assert info.value.estado_nuevo == E.ESTADO_DECLARADA_APTA


# --- POST /expedientes/ -----------------------------------------------------


def test_crear_con_expediente_activo_400_con_code(borrador, estudiante):
    respuesta = _cliente(estudiante).post(
        "/api/v1/expedientes/", {"carrera_id": CARRERA}, format="json"
    )
    assert respuesta.status_code == 400
    cuerpo = respuesta.json()
    assert cuerpo["code"] == "expediente_activo_existente"
    assert "activo" in cuerpo["detail"].lower()


def test_crear_con_catalogo_incompleto_500_explicito(estudiante):
    _desactivar_un_requisito_base()
    with mock.patch.object(api_errors.logger, "error") as log_error:
        respuesta = _cliente(estudiante).post(
            "/api/v1/expedientes/", {"carrera_id": CARRERA}, format="json"
        )
    assert respuesta.status_code == 500
    assert respuesta.json()["code"] == "configuracion_catalogo_incompleta"
    log_error.assert_called_once()
    assert not E.objects.filter(estudiante=estudiante).exists()


# --- POST /expedientes/{id}/enviar/ -----------------------------------------


def _enviar(client, expediente):
    return client.post(f"/api/v1/expedientes/{expediente.pk}/enviar/")


def test_enviar_estado_invalido_400_con_code(enviado, estudiante):
    respuesta = _enviar(_cliente(estudiante), enviado)
    assert respuesta.status_code == 400
    assert respuesta.json()["code"] == "estado_invalido"


def test_enviar_requisitos_incompletos_422_con_code(borrador, estudiante):
    respuesta = _enviar(_cliente(estudiante), borrador)
    assert respuesta.status_code == 422
    assert respuesta.json()["code"] == "requisitos_incompletos"


def test_enviar_transicion_invalida_400_sin_efectos(borrador, estudiante):
    _cargar(borrador)
    with mock.patch.object(
        enviar_expediente,
        "registrar_transicion",
        side_effect=TransicionNoPermitidaError(
            "simulada", estado_anterior="X", estado_nuevo="Y"
        ),
    ):
        respuesta = _enviar(_cliente(estudiante), borrador)
    assert respuesta.status_code == 400
    assert respuesta.json()["code"] == "transicion_invalida"
    borrador.refresh_from_db()
    assert borrador.estado == E.ESTADO_BORRADOR
    assert borrador.numero_providencia in (None, "")


# --- POST /expedientes/{id}/iniciar-verificacion/ ---------------------------


def _iniciar(client, expediente):
    return client.post(f"/api/v1/expedientes/{expediente.pk}/iniciar-verificacion/")


def test_iniciar_dos_veces_400_con_code_en_json(enviado, jurista):
    client = _cliente(jurista)
    assert _iniciar(client, enviado).status_code == 200
    respuesta = _iniciar(client, enviado)
    assert respuesta.status_code == 400
    assert respuesta.json()["code"] == "transicion_invalida"
    assert "EN_VERIFICACION" in respuesta.json()["detail"]


def test_iniciar_con_catalogo_incompleto_500_explicito(enviado, jurista):
    _desactivar_un_requisito_base()
    with mock.patch.object(api_errors.logger, "error") as log_error:
        respuesta = _iniciar(_cliente(jurista), enviado)
    assert respuesta.status_code == 500
    assert respuesta.json()["code"] == "configuracion_catalogo_incompleta"
    log_error.assert_called_once()
    enviado.refresh_from_db()
    assert enviado.estado == E.ESTADO_ENVIADA


# --- POST /expedientes/{id}/observar/ ---------------------------------------


def _observar(client, expediente, peticion_id, motivo="Falta firma"):
    return client.post(
        f"/api/v1/expedientes/{expediente.pk}/observar/",
        {"peticion_id": str(peticion_id), "motivo_observacion": motivo},
        format="json",
    )


def _peticion(expediente):
    return PeticionDocumental.objects.filter(expediente=expediente).first()


def test_observar_fuera_de_verificacion_400_antes_500(enviado, jurista):
    respuesta = _observar(_cliente(jurista), enviado, _peticion(enviado).pk)
    assert respuesta.status_code == 400
    assert respuesta.json()["code"] == "expediente_no_en_verificacion"


@pytest.mark.parametrize("peticion_id", [uuid.uuid4(), "no-es-un-uuid"])
def test_observar_peticion_inexistente_404_antes_500(
    en_verificacion, jurista, peticion_id
):
    respuesta = _observar(_cliente(jurista), en_verificacion, peticion_id)
    assert respuesta.status_code == 404
    assert respuesta.json()["code"] == "peticion_no_encontrada"


def test_observar_peticion_ya_observada_400_antes_500(en_verificacion, jurista):
    peticion = _peticion(en_verificacion)
    PeticionDocumental.objects.filter(pk=peticion.pk).update(
        estado_peticion="OBSERVADO"
    )
    respuesta = _observar(_cliente(jurista), en_verificacion, peticion.pk)
    assert respuesta.status_code == 400
    assert respuesta.json()["code"] == "peticion_ya_observada"
    assert not ObservacionAccionable.objects.filter(peticion=peticion).exists()


def test_observar_con_observacion_pendiente_400_con_code(en_verificacion, jurista):
    peticion = _peticion(en_verificacion)
    ObservacionAccionable.objects.create(
        expediente=en_verificacion,
        peticion=peticion,
        registrada_por=jurista,
        motivo_observacion="previa",
        resuelta=False,
    )
    respuesta = _observar(_cliente(jurista), en_verificacion, peticion.pk)
    assert respuesta.status_code == 400
    assert respuesta.json()["code"] == "observacion_ya_existe"


def test_observar_transicion_invalida_400_con_rollback(en_verificacion, jurista):
    peticion = _peticion(en_verificacion)
    historial_antes = HistorialEstado.objects.filter(expediente=en_verificacion).count()
    with mock.patch.object(
        registrar_observacion,
        "registrar_transicion",
        side_effect=TransicionNoPermitidaError(
            "simulada",
            estado_anterior=E.ESTADO_OBSERVADA,
            estado_nuevo=E.ESTADO_OBSERVADA,
        ),
    ):
        respuesta = _observar(_cliente(jurista), en_verificacion, peticion.pk)
    assert respuesta.status_code == 400
    assert respuesta.json()["code"] == "transicion_invalida"
    peticion.refresh_from_db()
    en_verificacion.refresh_from_db()
    assert peticion.estado_peticion == "CARGADO"
    assert en_verificacion.estado == E.ESTADO_EN_VERIFICACION
    assert en_verificacion.fecha_ultima_pausa is None
    assert not ObservacionAccionable.objects.filter(peticion=peticion).exists()
    assert (
        HistorialEstado.objects.filter(expediente=en_verificacion).count()
        == historial_antes
    )


def test_observar_correcto_sigue_funcionando(en_verificacion, jurista):
    respuesta = _observar(
        _cliente(jurista), en_verificacion, _peticion(en_verificacion).pk
    )
    assert respuesta.status_code == 201
    en_verificacion.refresh_from_db()
    assert en_verificacion.estado == E.ESTADO_OBSERVADA
