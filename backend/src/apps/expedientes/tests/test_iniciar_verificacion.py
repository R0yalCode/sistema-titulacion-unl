"""Pruebas de PLB-E2-01: iniciar verificación (ENVIADA -> EN_VERIFICACION).

Servicio (`iniciar_verificacion.execute`): transición, checklist de los cinco
requisitos base, idempotencia de filas, rollback completo si algo falla,
plazo sin cambios, facultad y rol revalidados, registro único mediante
`registrar_transicion()` (DT-12).

Endpoint (`POST /api/v1/expedientes/{id}/iniciar-verificacion/`): 200 para el
SECRETARIO_ABOGADO de la facultad (AUT-02), 404 fuera de ámbito, 403 para el
resto de roles, 400 si no está en ENVIADA, 401 anónimo, 429 heredado y
`GET /checklist/` con los ítems creados.
"""

import itertools
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
)
from apps.expedientes.services.iniciar_verificacion import (
    CatalogoIncompletoError,
    EstadoInvalidoError,
    UsuarioNoAutorizadoError,
)
from apps.notificaciones.adapters.models import EventoAuditoria, NotificacionInterna
from apps.peticiones.adapters.models import CatalogoDocumental, PeticionDocumental
from apps.verificacion.adapters.models import ChecklistVerification
from core.adapters.throttling import MutantOperationThrottle

pytestmark = pytest.mark.django_db

E = ExpedienteTitulacion
CARRERA_1 = "aaaaaaaa-e201-4111-8111-111111111111"
FACULTAD_1 = "bbbbbbbb-e201-4111-8111-111111111111"
CARRERA_2 = "aaaaaaaa-e201-4222-8222-222222222222"
FACULTAD_2 = "bbbbbbbb-e201-4222-8222-222222222222"
_CEDULAS = itertools.count(2010000001)


def _usuario(username, rol, *, carrera_id=CARRERA_1, facultad_id=FACULTAD_1):
    user = User.objects.create_user(
        username=username,
        password="x",
        cedula=f"{next(_CEDULAS):010d}",
        carrera_id=carrera_id,
        facultad_id=facultad_id,
    )
    role, _ = Role.objects.get_or_create(name=rol)
    UserRole.objects.create(user=user, role=role)
    return user


def _cliente(user=None):
    client = APIClient()
    if user is not None:
        client.force_authenticate(user=user)
    return client


def _url(expediente):
    return f"/api/v1/expedientes/{expediente.pk}/iniciar-verificacion/"


@pytest.fixture(autouse=True)
def _limpiar_cache_throttle():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def estudiante():
    return _usuario("e201_estudiante", "ESTUDIANTE")


@pytest.fixture
def jurista():
    return _usuario("e201_jurista", "SECRETARIO_ABOGADO")


@pytest.fixture
def jurista_otra_facultad():
    return _usuario(
        "e201_jurista_f2",
        "SECRETARIO_ABOGADO",
        carrera_id=CARRERA_2,
        facultad_id=FACULTAD_2,
    )


@pytest.fixture
def enviado(estudiante):
    """Expediente ENVIADA por el flujo real: crear, cargar y enviar."""
    expediente = crear_expediente.execute(estudiante, CARRERA_1)
    PeticionDocumental.objects.filter(expediente=expediente).update(
        estado_peticion="CARGADO"
    )
    return enviar_expediente.execute(expediente, actor=estudiante)


def _transiciones(expediente):
    """Eventos ESTADO_CAMBIADO de inicio de verificación (excluye el envío)."""
    return EventoAuditoria.objects.filter(
        expediente=expediente,
        accion=EventoAuditoria.Accion.ESTADO_CAMBIADO,
        detalles__origen="iniciar_verificacion",
    )


def _historial_inicio(expediente):
    return HistorialEstado.objects.filter(
        expediente=expediente, estado_anterior=E.ESTADO_ENVIADA
    )


# --- Servicio ---------------------------------------------------------------


def test_servicio_transiciona_y_crea_cinco_filas_pendientes(enviado, jurista):
    resultado = iniciar_verificacion.execute(enviado.pk, actor=jurista)

    assert resultado.estado == E.ESTADO_EN_VERIFICACION
    filas = ChecklistVerification.objects.filter(expediente=enviado)
    base = CatalogoDocumental.objects.filter(
        es_obligatorio_base=True, fase="FASE_1", activo=True
    )
    assert filas.count() == 5
    assert set(filas.values_list("requisito_id", flat=True)) == set(
        base.values_list("id", flat=True)
    )
    assert set(filas.values_list("estado_verificacion", flat=True)) == {"PENDIENTE"}


def test_servicio_registra_una_sola_transicion_con_el_actor(enviado, jurista):
    iniciar_verificacion.execute(enviado.pk, actor=jurista)

    historial = HistorialEstado.objects.get(
        expediente=enviado, estado_nuevo=E.ESTADO_EN_VERIFICACION
    )
    assert historial.estado_anterior == E.ESTADO_ENVIADA
    assert historial.estado_nuevo == E.ESTADO_EN_VERIFICACION
    assert historial.registrado_por == jurista
    evento = _transiciones(enviado).get(detalles__estado_nuevo=E.ESTADO_EN_VERIFICACION)
    assert evento.usuario == jurista
    assert evento.rol_usuario == "SECRETARIO_ABOGADO"
    assert evento.detalles["origen"] == "iniciar_verificacion"


def test_servicio_notifica_al_estudiante(enviado, jurista, estudiante):
    iniciar_verificacion.execute(enviado.pk, actor=jurista)

    notificacion = NotificacionInterna.objects.get(
        usuario_destino=estudiante, expediente=enviado, titulo="Verificación iniciada"
    )
    assert notificacion.titulo == "Verificación iniciada"
    assert enviado.numero_expediente in notificacion.mensaje


def test_servicio_no_modifica_el_plazo(enviado, jurista):
    antes = ExpedienteTitulacion.objects.values(
        "fecha_recepcion",
        "fecha_limite_atencion",
        "numero_providencia",
        "dias_laborables_acumulados",
        "fecha_ultima_pausa",
    ).get(pk=enviado.pk)

    iniciar_verificacion.execute(enviado.pk, actor=jurista)

    despues = ExpedienteTitulacion.objects.values(*antes.keys()).get(pk=enviado.pk)
    assert despues == antes


@pytest.mark.parametrize(
    "estado",
    [
        E.ESTADO_BORRADOR,
        E.ESTADO_EN_VERIFICACION,
        E.ESTADO_OBSERVADA,
        E.ESTADO_INFORME_EMITIDO,
        E.ESTADO_DECLARADA_APTA,
    ],
)
def test_servicio_rechaza_estado_distinto_de_enviada(enviado, jurista, estado):
    ExpedienteTitulacion.objects.filter(pk=enviado.pk).update(estado=estado)

    with pytest.raises(EstadoInvalidoError):
        iniciar_verificacion.execute(enviado.pk, actor=jurista)

    assert not ChecklistVerification.objects.filter(expediente=enviado).exists()
    assert not _historial_inicio(enviado).exists()


def test_servicio_filas_idempotentes_no_duplica(enviado, jurista):
    """Filas preexistentes (p. ej. cargadas a mano) no se duplican."""
    requisito = CatalogoDocumental.objects.filter(
        es_obligatorio_base=True, fase="FASE_1", activo=True
    ).first()
    previa = ChecklistVerification.objects.create(
        expediente=enviado, requisito=requisito, estado_verificacion="PENDIENTE"
    )

    iniciar_verificacion.execute(enviado.pk, actor=jurista)

    assert ChecklistVerification.objects.filter(expediente=enviado).count() == 5
    assert (
        ChecklistVerification.objects.filter(
            expediente=enviado, requisito=requisito
        ).get()
        == previa
    )


def test_servicio_segunda_llamada_falla_sin_duplicar(enviado, jurista):
    iniciar_verificacion.execute(enviado.pk, actor=jurista)

    with pytest.raises(EstadoInvalidoError):
        iniciar_verificacion.execute(enviado.pk, actor=jurista)

    assert ChecklistVerification.objects.filter(expediente=enviado).count() == 5
    assert _historial_inicio(enviado).count() == 1
    assert _transiciones(enviado).count() == 1


def test_servicio_rollback_si_falla_la_creacion_de_filas(enviado, jurista):
    original = iniciar_verificacion._get_or_create_checklist_verification
    llamadas = []

    def falla_en_la_tercera(expediente, requisito):
        llamadas.append(requisito)
        if len(llamadas) == 3:
            raise RuntimeError("fallo simulado al crear la fila")
        return original(expediente, requisito)

    with mock.patch.object(
        iniciar_verificacion,
        "_get_or_create_checklist_verification",
        side_effect=falla_en_la_tercera,
    ):
        with pytest.raises(RuntimeError):
            iniciar_verificacion.execute(enviado.pk, actor=jurista)

    enviado.refresh_from_db()
    assert enviado.estado == E.ESTADO_ENVIADA
    assert not ChecklistVerification.objects.filter(expediente=enviado).exists()
    assert not _historial_inicio(enviado).exists()
    assert not _transiciones(enviado).exists()
    assert not NotificacionInterna.objects.filter(
        expediente=enviado, titulo="Verificación iniciada"
    ).exists()


def test_servicio_rollback_si_falla_la_notificacion(enviado, jurista):
    with mock.patch.object(
        NotificacionInterna.objects,
        "create",
        side_effect=RuntimeError("fallo simulado al notificar"),
    ):
        with pytest.raises(RuntimeError):
            iniciar_verificacion.execute(enviado.pk, actor=jurista)

    enviado.refresh_from_db()
    assert enviado.estado == E.ESTADO_ENVIADA
    assert not ChecklistVerification.objects.filter(expediente=enviado).exists()
    assert not _historial_inicio(enviado).exists()


def test_servicio_catalogo_incompleto_sin_efectos(enviado, jurista):
    requisito = CatalogoDocumental.objects.filter(
        es_obligatorio_base=True, fase="FASE_1", activo=True
    ).first()
    requisito.activo = False
    requisito.save(update_fields=["activo"])

    with pytest.raises(CatalogoIncompletoError):
        iniciar_verificacion.execute(enviado.pk, actor=jurista)

    enviado.refresh_from_db()
    assert enviado.estado == E.ESTADO_ENVIADA
    assert not ChecklistVerification.objects.filter(expediente=enviado).exists()


def test_servicio_rechaza_otra_facultad(enviado, jurista_otra_facultad):
    with pytest.raises(UsuarioNoAutorizadoError):
        iniciar_verificacion.execute(enviado.pk, actor=jurista_otra_facultad)

    enviado.refresh_from_db()
    assert enviado.estado == E.ESTADO_ENVIADA


@pytest.mark.parametrize(
    "rol", ["ANALISTA_APOYO", "DECANO", "ESTUDIANTE", "SECRETARIA_CARRERA"]
)
def test_servicio_rechaza_otros_roles(enviado, rol):
    actor = _usuario(f"e201_srv_{rol.lower()}", rol)

    with pytest.raises(UsuarioNoAutorizadoError):
        iniciar_verificacion.execute(enviado.pk, actor=actor)

    enviado.refresh_from_db()
    assert enviado.estado == E.ESTADO_ENVIADA


# --- Endpoint ---------------------------------------------------------------


def test_endpoint_200_jurista_de_la_facultad(enviado, jurista):
    response = _cliente(jurista).post(_url(enviado))

    assert response.status_code == 200
    assert response.data["id"] == str(enviado.pk)
    assert response.data["estado"] == E.ESTADO_EN_VERIFICACION
    assert ChecklistVerification.objects.filter(expediente=enviado).count() == 5


def test_endpoint_404_jurista_de_otra_facultad(enviado, jurista_otra_facultad):
    response = _cliente(jurista_otra_facultad).post(_url(enviado))

    assert response.status_code == 404
    enviado.refresh_from_db()
    assert enviado.estado == E.ESTADO_ENVIADA


@pytest.mark.parametrize(
    "rol",
    [
        "ESTUDIANTE",
        "ANALISTA_APOYO",
        "DECANO",
        "SECRETARIA_CARRERA",
        "DIRECTOR_CARRERA",
        "RESPONSABLE_DEPENDENCIA",
        "ADMINISTRADOR",
    ],
)
def test_endpoint_403_roles_sin_celda(enviado, rol):
    actor = _usuario(f"e201_api_{rol.lower()}", rol)

    response = _cliente(actor).post(_url(enviado))

    assert response.status_code == 403
    enviado.refresh_from_db()
    assert enviado.estado == E.ESTADO_ENVIADA


def test_endpoint_403_estudiante_duenio(enviado, estudiante):
    response = _cliente(estudiante).post(_url(enviado))

    assert response.status_code == 403


def test_endpoint_400_si_ya_esta_en_verificacion(enviado, jurista):
    client = _cliente(jurista)
    assert client.post(_url(enviado)).status_code == 200

    response = client.post(_url(enviado))

    assert response.status_code == 400
    assert response.data["detail"].code == "transicion_invalida"
    assert "EN_VERIFICACION" in str(response.data["detail"])
    assert ChecklistVerification.objects.filter(expediente=enviado).count() == 5
    assert _transiciones(enviado).count() == 1


def test_endpoint_400_si_esta_en_borrador(estudiante, jurista):
    borrador = crear_expediente.execute(estudiante, CARRERA_1)

    response = _cliente(jurista).post(_url(borrador))

    assert response.status_code == 400
    assert not ChecklistVerification.objects.filter(expediente=borrador).exists()


def test_endpoint_401_anonimo(enviado):
    response = _cliente().post(_url(enviado))

    assert response.status_code == 401


def test_endpoint_429_heredado(enviado, jurista, monkeypatch):
    monkeypatch.setattr(
        MutantOperationThrottle, "THROTTLE_RATES", {"mutante": "1/minute"}
    )
    client = _cliente(jurista)
    assert client.post(_url(enviado)).status_code == 200

    assert client.post(_url(enviado)).status_code == 429


def test_endpoint_checklist_visible_tras_iniciar(enviado, jurista):
    client = _cliente(jurista)
    client.post(_url(enviado))

    response = client.get(f"/api/v1/expedientes/{enviado.pk}/checklist/")

    assert response.status_code == 200
    items = response.data
    assert len(items) == 5
    assert {item["estado_verificacion"] for item in items} == {"PENDIENTE"}
