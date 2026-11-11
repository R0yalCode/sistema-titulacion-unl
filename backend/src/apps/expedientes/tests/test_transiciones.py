"""Pruebas de PLB-E2-06 / DT-12: `registrar_transicion()` como fuente única.

Cubren: actor autenticado explícito, estado anterior real (leído antes del
cambio), validación de transiciones, un único `HistorialEstado` y un único
`ESTADO_CAMBIADO` por transición, atomicidad (rollback completo) y una
prueba de arquitectura que impide cambiar el estado fuera de la función.
"""

import re
from pathlib import Path
from unittest import mock

import pytest
from django.contrib.auth.models import AnonymousUser

from apps.authentication.adapters.models import Role, User, UserRole
from apps.expedientes.adapters.models import ExpedienteTitulacion, HistorialEstado
from apps.expedientes.services import transiciones
from apps.expedientes.services.transiciones import (
    ActorRequeridoError,
    TransicionNoPermitidaError,
    registrar_transicion,
)
from apps.notificaciones.adapters.models import EventoAuditoria

pytestmark = pytest.mark.django_db

CARRERA = "11111111-1111-1111-1111-111111111111"
FACULTAD = "22222222-2222-2222-2222-222222222222"
E = ExpedienteTitulacion


def _usuario(username, *roles):
    user = User.objects.create_user(
        username=username,
        password="x",
        cedula=f"{abs(hash(username)) % 10**10:010d}",
        carrera_id=CARRERA,
        facultad_id=FACULTAD,
    )
    for rol in roles:
        role, _ = Role.objects.get_or_create(name=rol)
        UserRole.objects.create(user=user, role=role)
    return user


@pytest.fixture
def estudiante():
    return _usuario("est_tr", "ESTUDIANTE")


@pytest.fixture
def jurista():
    return _usuario("jur_tr", "SECRETARIO_ABOGADO")


def _expediente(estudiante, estado):
    return ExpedienteTitulacion.objects.create(
        numero_expediente=f"EXP-TR-{estado}",
        estudiante=estudiante,
        carrera_id=CARRERA,
        facultad_id=FACULTAD,
        estado=estado,
        activa=True,
    )


def _transiciones(expediente):
    return EventoAuditoria.objects.filter(
        expediente=expediente, accion=EventoAuditoria.Accion.ESTADO_CAMBIADO
    )


def test_actor_y_estado_anterior_correctos_un_solo_registro(estudiante, jurista):
    exp = _expediente(estudiante, E.ESTADO_EN_VERIFICACION)

    historial = registrar_transicion(exp, E.ESTADO_OBSERVADA, jurista, origen="prueba")

    exp.refresh_from_db()
    assert exp.estado == E.ESTADO_OBSERVADA
    assert HistorialEstado.objects.filter(expediente=exp).count() == 1
    assert historial.estado_anterior == E.ESTADO_EN_VERIFICACION
    assert historial.estado_nuevo == E.ESTADO_OBSERVADA
    assert historial.registrado_por == jurista
    evento = _transiciones(exp).get()
    assert evento.usuario == jurista
    assert evento.rol_usuario == "SECRETARIO_ABOGADO"
    assert evento.detalles == {
        "estado_anterior": E.ESTADO_EN_VERIFICACION,
        "estado_nuevo": E.ESTADO_OBSERVADA,
        "origen": "prueba",
        "historial_id": str(historial.id),
    }


def test_estado_anterior_se_lee_de_la_bd_no_de_la_instancia(estudiante, jurista):
    exp = _expediente(estudiante, E.ESTADO_EN_VERIFICACION)
    exp.estado = E.ESTADO_INFORME_EMITIDO  # instancia alterada sin guardar

    historial = registrar_transicion(exp, E.ESTADO_OBSERVADA, jurista, origen="prueba")
    assert historial.estado_anterior == E.ESTADO_EN_VERIFICACION


def test_transicion_no_permitida_sin_efectos(estudiante, jurista):
    exp = _expediente(estudiante, E.ESTADO_BORRADOR)

    with pytest.raises(TransicionNoPermitidaError):
        registrar_transicion(exp, E.ESTADO_DECLARADA_APTA, jurista, origen="prueba")

    exp.refresh_from_db()
    assert exp.estado == E.ESTADO_BORRADOR
    assert not HistorialEstado.objects.filter(expediente=exp).exists()
    assert not _transiciones(exp).exists()


@pytest.mark.parametrize("actor", [None, AnonymousUser()])
def test_actor_obligatorio(estudiante, actor):
    exp = _expediente(estudiante, E.ESTADO_BORRADOR)
    with pytest.raises(ActorRequeridoError):
        registrar_transicion(exp, E.ESTADO_ENVIADA, actor, origen="prueba")
    exp.refresh_from_db()
    assert exp.estado == E.ESTADO_BORRADOR


def test_atomicidad_rollback_si_falla_la_auditoria(estudiante, jurista):
    exp = _expediente(estudiante, E.ESTADO_EN_VERIFICACION)

    with mock.patch.object(
        transiciones.EventoAuditoria.objects,
        "create",
        side_effect=RuntimeError("fallo simulado"),
    ):
        with pytest.raises(RuntimeError):
            registrar_transicion(exp, E.ESTADO_OBSERVADA, jurista, origen="prueba")

    exp.refresh_from_db()
    assert exp.estado == E.ESTADO_EN_VERIFICACION
    assert not HistorialEstado.objects.filter(expediente=exp).exists()
    assert not _transiciones(exp).exists()


def test_campos_adicionales_se_persisten_en_la_misma_escritura(estudiante):
    exp = _expediente(estudiante, E.ESTADO_BORRADOR)
    exp.numero_providencia = "PROV-2026-9999"

    registrar_transicion(
        exp,
        E.ESTADO_ENVIADA,
        estudiante,
        origen="prueba",
        campos_adicionales=("numero_providencia",),
    )
    exp.refresh_from_db()
    assert exp.estado == E.ESTADO_ENVIADA
    assert exp.numero_providencia == "PROV-2026-9999"
    assert _transiciones(exp).get().rol_usuario == "ESTUDIANTE"


def test_rol_atribuido_es_el_de_la_transicion_en_usuario_multirrol(estudiante):
    multirrol = _usuario("multi_tr", "ESTUDIANTE", "SECRETARIO_ABOGADO")
    exp = _expediente(estudiante, E.ESTADO_EN_VERIFICACION)
    registrar_transicion(exp, E.ESTADO_OBSERVADA, multirrol, origen="prueba")
    assert _transiciones(exp).get().rol_usuario == "SECRETARIO_ABOGADO"


def test_eventos_historicos_no_se_modifican(estudiante, jurista):
    exp = _expediente(estudiante, E.ESTADO_EN_VERIFICACION)
    previo = EventoAuditoria.objects.create(
        accion=EventoAuditoria.Accion.ESTADO_CAMBIADO,
        usuario=estudiante,
        rol_usuario="ESTUDIANTE",
        expediente=exp,
        detalles={"estado_anterior": "ENVIADA", "estado_nuevo": "EN_VERIFICACION"},
    )
    registrar_transicion(exp, E.ESTADO_OBSERVADA, jurista, origen="prueba")
    previo.refresh_from_db()
    assert previo.usuario == estudiante
    assert previo.detalles["estado_nuevo"] == "EN_VERIFICACION"
    assert _transiciones(exp).count() == 2


# --- Prueba de arquitectura -------------------------------------------------

APPS_DIR = Path(__file__).resolve().parents[2]
PERMITIDO = APPS_DIR / "expedientes" / "services" / "transiciones.py"
ASIGNACION_ESTADO = re.compile(r"\b(expediente|cadena|exp|instance)\.estado\s*=(?!=)")
CREACION_HISTORIAL = re.compile(r"HistorialEstado\.objects\.(create|bulk_create)")


def _fuentes_productivas():
    for ruta in APPS_DIR.rglob("*.py"):
        partes = ruta.parts
        if "tests" in partes or "migrations" in partes or ruta == PERMITIDO:
            continue
        yield ruta


def test_arquitectura_ningun_servicio_cambia_estado_fuera_de_la_funcion():
    infractores = []
    for ruta in _fuentes_productivas():
        texto = ruta.read_text(encoding="utf-8")
        for patron in (ASIGNACION_ESTADO, CREACION_HISTORIAL):
            for m in patron.finditer(texto):
                linea = texto.count("\n", 0, m.start()) + 1
                infractores.append(f"{ruta.relative_to(APPS_DIR)}:{linea}")
    assert (
        infractores == []
    ), "Cambios de estado o historial fuera de registrar_transicion(): " + ", ".join(
        infractores
    )
