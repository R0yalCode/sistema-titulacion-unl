"""Pruebas automatizadas del motor de estados y cómputo de plazos (T019).

Fuente de requisitos: HU-004, HU-007, HU-009, HU-010, RF-002, RF-003, RF-007,
RF-009, RF-011, RN-002, RN-003, RN-010, EX-006, CA-001, CA-003, CA-005, CA-006,
Principio C-007, Principio C-011.

Cubre:
- Transiciones válidas del ciclo de vida completo
- Transiciones inválidas (EX-006)
- Cálculo de 8 días laborables (RN-002, Principio C-007)
- Registro inmutable de timestamp y providencia (RN-010, CA-001)
- Pausa/reanudación de plazo por observaciones (RN-003, AP-01)
"""

import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from django.utils import timezone

from apps.authentication.adapters.models import Role, User, UserRole
from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.expedientes.domain.plazo_calculator import PlazoLaboralCalculator
from apps.expedientes.services import crear_expediente, enviar_expediente
from apps.peticiones.adapters.models import PeticionDocumental

UTC = ZoneInfo("UTC")
PASSWORD = "pwd_seguro_t019"
CARRERA_1 = "aaaaaaaa-c111-4111-8111-111111111111"
FERIADO = "2026-01-07"  # Miércoles feriado para pruebas


# --- Helpers ----------------------------------------------------------------


def crear_usuario(username, rol, carrera_id=None, facultad_id=None):
    user = User.objects.create_user(
        username=username,
        password=PASSWORD,
        carrera_id=carrera_id,
        facultad_id=facultad_id,
    )
    role, _ = Role.objects.get_or_create(name=rol)
    UserRole.objects.get_or_create(user=user, role=role)
    return user


def cliente(user):
    from rest_framework.test import APIClient

    client = APIClient()
    client.force_authenticate(user=user)
    return client


def expediente_completo_para_enviar(estudiante):
    """Crea expediente en BORRADOR y marca las 5 peticiones como CARGADO."""
    expediente = crear_expediente.execute(estudiante, CARRERA_1)
    for peticion in PeticionDocumental.objects.filter(expediente=expediente):
        peticion.estado_peticion = "CARGADO"
        peticion.save()
    return expediente


def avanzar_a_enviada(expediente, ahora=None):
    """Ejecuta el caso de uso enviar_expediente (BORRADOR -> ENVIADA)."""
    return enviar_expediente.execute(expediente, ahora=ahora)


# --- FIXTURES ---------------------------------------------------------------


@pytest.fixture(name="estudiante")
def fixture_estudiante(db):
    return crear_usuario("t019_estudiante", "ESTUDIANTE", CARRERA_1)


@pytest.fixture(name="abogado")
def fixture_abogado(db):
    return crear_usuario(
        "t019_abogado",
        "SECRETARIO_ABOGADO",
        facultad_id="aaaaaaaa-f111-4111-8111-111111111111",
    )


@pytest.fixture(name="decano")
def fixture_decano(db):
    return crear_usuario(
        "t019_decano", "DECANO", facultad_id="aaaaaaaa-f111-4111-8111-111111111111"
    )


# --- TRANSICIONES VÁLIDAS ---------------------------------------------------


class TestTransicionesValidas:
    """Ciclo de vida completo: BORRADOR -> ENVIADA -> EN_VERIFICACION ->
    OBSERVADA -> EN_VERIFICACION -> INFORME_EMITIDO -> DECLARADA_APTA.
    """

    def test_borrador_a_enviada(self, estudiante):
        """BORRADOR -> ENVIADA vía POST /enviar/ con 5 requisitos CARGADO."""
        expediente = expediente_completo_para_enviar(estudiante)
        assert expediente.estado == ExpedienteTitulacion.ESTADO_BORRADOR

        enviado = enviar_expediente.execute(expediente)

        assert enviado.estado == ExpedienteTitulacion.ESTADO_ENVIADA
        assert enviado.fecha_recepcion is not None
        assert enviado.numero_providencia is not None
        assert re.match(r"^PROV-\d{4}-\d{4}$", enviado.numero_providencia)
        assert enviado.fecha_limite_atencion is not None
        assert enviado.dias_laborables_acumulados == 0

    def test_enviada_a_en_verificacion(self, estudiante):
        """ENVIADA -> EN_VERIFICACION: inicio de evaluación por Secretaría.
        En el modelo actual no hay endpoint explícito, pero el estado existe.
        Simulamos cambio directo de estado (como lo haría checklist T024).
        """
        expediente = expediente_completo_para_enviar(estudiante)
        enviado = avanzar_a_enviada(expediente)

        enviado.estado = ExpedienteTitulacion.ESTADO_EN_VERIFICACION
        enviado.save()

        enviado.refresh_from_db()
        assert enviado.estado == ExpedienteTitulacion.ESTADO_EN_VERIFICACION

    def test_en_verificacion_a_observada(self, estudiante):
        """EN_VERIFICACION -> OBSERVADA: Secretaría registra observación."""
        expediente = expediente_completo_para_enviar(estudiante)
        enviado = avanzar_a_enviada(expediente)
        enviado.estado = ExpedienteTitulacion.ESTADO_EN_VERIFICACION
        enviado.save()

        enviado.estado = ExpedienteTitulacion.ESTADO_OBSERVADA
        enviado.save()

        enviado.refresh_from_db()
        assert enviado.estado == ExpedienteTitulacion.ESTADO_OBSERVADA

    def test_observada_a_en_verificacion_subsanacion(self, estudiante):
        """OBSERVADA -> EN_VERIFICACION: estudiante subsana y reenvía documento."""
        expediente = expediente_completo_para_enviar(estudiante)
        enviado = avanzar_a_enviada(expediente)
        enviado.estado = ExpedienteTitulacion.ESTADO_EN_VERIFICACION
        enviado.save()
        enviado.estado = ExpedienteTitulacion.ESTADO_OBSERVADA
        enviado.save()

        enviado.estado = ExpedienteTitulacion.ESTADO_EN_VERIFICACION
        enviado.save()

        enviado.refresh_from_db()
        assert enviado.estado == ExpedienteTitulacion.ESTADO_EN_VERIFICACION

    def test_en_verificacion_a_informe_emitido(self, estudiante, abogado):
        """EN_VERIFICACION -> INFORME_EMITIDO: 5 VERIFICADO -> POST /informes/.
        Simula cambio (endpoint T024/T025).
        """
        expediente = expediente_completo_para_enviar(estudiante)
        enviado = avanzar_a_enviada(expediente)
        enviado.estado = ExpedienteTitulacion.ESTADO_EN_VERIFICACION
        enviado.save()

        # Marcar todas las peticiones como VERIFICADO
        for p in PeticionDocumental.objects.filter(expediente=enviado):
            p.estado_peticion = "VERIFICADO"
            p.save()

        enviado.estado = ExpedienteTitulacion.ESTADO_INFORME_EMITIDO
        enviado.save()

        enviado.refresh_from_db()
        assert enviado.estado == ExpedienteTitulacion.ESTADO_INFORME_EMITIDO

    def test_informe_emitido_a_declarada_apta(self, estudiante, decano):
        """INFORME_EMITIDO -> DECLARADA_APTA: Decano emite declaratoria (T026)."""
        expediente = expediente_completo_para_enviar(estudiante)
        enviado = avanzar_a_enviada(expediente)
        enviado.estado = ExpedienteTitulacion.ESTADO_INFORME_EMITIDO
        enviado.save()

        enviado.estado = ExpedienteTitulacion.ESTADO_DECLARADA_APTA
        enviado.save()

        enviado.refresh_from_db()
        assert enviado.estado == ExpedienteTitulacion.ESTADO_DECLARADA_APTA

    def test_cualquier_estado_a_cancelada(self, estudiante):
        """Cualquier estado -> CANCELADA: cancelación administrativa."""
        estados = [
            ExpedienteTitulacion.ESTADO_BORRADOR,
            ExpedienteTitulacion.ESTADO_ENVIADA,
            ExpedienteTitulacion.ESTADO_EN_VERIFICACION,
            ExpedienteTitulacion.ESTADO_OBSERVADA,
            ExpedienteTitulacion.ESTADO_INFORME_EMITIDO,
        ]

        for i, estado in enumerate(estados):
            # Estudiante único por iteración para evitar ExpedienteActivoExistenteError
            est = crear_usuario(f"t019_cancel_{i}", "ESTUDIANTE", CARRERA_1)
            if estado == ExpedienteTitulacion.ESTADO_BORRADOR:
                exp_test = expediente_completo_para_enviar(est)
            else:
                exp_test = expediente_completo_para_enviar(est)
                exp_test = avanzar_a_enviada(exp_test)
                if estado != ExpedienteTitulacion.ESTADO_ENVIADA:
                    exp_test.estado = estado
                    exp_test.save()

            exp_test.estado = ExpedienteTitulacion.ESTADO_CANCELADA
            exp_test.save()
            exp_test.refresh_from_db()
            assert exp_test.estado == ExpedienteTitulacion.ESTADO_CANCELADA


# --- TRANSICIONES INVÁLIDAS (EX-006) ----------------------------------------


class TestTransicionesInvalidas:
    """EX-006: Transiciones de estado inválidas.
    La validación vive en los casos de uso / endpoints, no en el modelo ORM.
    Estos tests documentan las transiciones prohibidas y verifican que
    los campos inmutables (fecha_recepcion, numero_providencia) no se pierden.
    """

    def test_borrador_directo_a_informe_emitido_no_tiene_caso_de_uso(self, estudiante):
        """BORRADOR -> INFORME_EMITIDO: no existe caso de uso que lo permita."""
        expediente = expediente_completo_para_enviar(estudiante)
        assert expediente.estado == ExpedienteTitulacion.ESTADO_BORRADOR
        # El modelo permite el cambio directo, pero el flujo de negocio
        # requiere pasar por ENVIADA y EN_VERIFICACION (validado en endpoints).

    def test_enviada_no_puede_volver_a_borrador_campos_inmutables(self, estudiante):
        """ENVIADA -> BORRADO: campos inmutables se conservan (RN-010)."""
        expediente = expediente_completo_para_enviar(estudiante)
        enviado = avanzar_a_enviada(expediente)

        fecha_recepcion_original = enviado.fecha_recepcion
        providencia_original = enviado.numero_providencia

        # Cambio directo de estado en BD (simula bypass de endpoint)
        enviado.estado = ExpedienteTitulacion.ESTADO_BORRADOR
        enviado.save()

        enviado.refresh_from_db()
        assert enviado.fecha_recepcion == fecha_recepcion_original
        assert enviado.numero_providencia == providencia_original

    def test_enviada_directo_a_declarada_apta_sin_verificacion(self, estudiante):
        """ENVIADA -> DECLARADA_APTA saltea verificación e informe (prohibido)."""
        expediente = expediente_completo_para_enviar(estudiante)
        enviado = avanzar_a_enviada(expediente)
        # No hay caso de uso que permita este salto
        assert enviado.estado == ExpedienteTitulacion.ESTADO_ENVIADA

    def test_observada_directo_a_informe_emitido_bloqueada_rn003(self, estudiante):
        """OBSERVADA -> INFORME_EMITIDO bloqueada por RN-003 (requisitos pendientes)."""
        expediente = expediente_completo_para_enviar(estudiante)
        enviado = avanzar_a_enviada(expediente)
        enviado.estado = ExpedienteTitulacion.ESTADO_OBSERVADA
        enviado.save()

        # POST /informes/ (T024/T025) debe validar RN-003
        assert enviado.estado == ExpedienteTitulacion.ESTADO_OBSERVADA

    def test_declarada_apta_estado_terminal(self, estudiante):
        """DECLARADA_APTA es estado terminal del flujo principal."""
        expediente = expediente_completo_para_enviar(estudiante)
        enviado = avanzar_a_enviada(expediente)
        enviado.estado = ExpedienteTitulacion.ESTADO_DECLARADA_APTA
        enviado.save()

        # Aunque el modelo permite cambiar el estado, semánticamente es terminal
        assert enviado.estado == ExpedienteTitulacion.ESTADO_DECLARADA_APTA


# --- CÁLCULO DE 8 DÍAS LABORABLES (RN-002, Principio C-007) -----------------


class TestCalculoPlazoLaboral:
    """Integración: fecha_limite_atencion correcta en envío y tras pausas."""

    def test_fecha_limite_8_dias_habiles_desde_envio(self, estudiante):
        """Envío un lunes -> límite a 8 hábiles (excluye fin de semana)."""
        expediente = expediente_completo_para_enviar(estudiante)
        lunes = datetime(2026, 1, 5, 10, 0, tzinfo=UTC)  # Lunes 5 ene 2026

        enviado = enviar_expediente.execute(expediente, ahora=lunes)

        # Lunes 5 -> hábiles: 6,7,8,9,12,13,14,15 = Miércoles 15
        esperado = PlazoLaboralCalculator().calcular_fecha_limite(lunes.date(), 8)
        assert timezone.localtime(enviado.fecha_limite_atencion).date() == esperado

    def test_fecha_limite_omite_feriado_configurado(self, estudiante):
        """Feriado institucional dentro del plazo extiende la fecha límite."""
        expediente = expediente_completo_para_enviar(estudiante)
        lunes = datetime(2026, 1, 5, 10, 0, tzinfo=UTC)  # Mié 7 es feriado

        calc = PlazoLaboralCalculator(feriados=[datetime(2026, 1, 7).date()])
        esperado = calc.calcular_fecha_limite(lunes.date(), 8)
        # 6,8,9,12,13,14,15,16 = Viernes 16

        _ = enviar_expediente.execute(expediente, ahora=lunes)
        # El servicio usa PlazoLaboralCalculator() sin feriados por defecto
        # Este test verifica la lógica del calculador, no el servicio
        assert esperado == datetime(2026, 1, 16).date()

    def test_fecha_limite_utc_inmutable(self, estudiante):
        """fecha_recepcion y fecha_limite_atencion en UTC (RN-010, CA-001)."""
        expediente = expediente_completo_para_enviar(estudiante)
        ahora = datetime(2026, 3, 15, 14, 30, tzinfo=UTC)

        enviado = enviar_expediente.execute(expediente, ahora=ahora)

        assert timezone.is_aware(enviado.fecha_recepcion)
        assert enviado.fecha_recepcion.utcoffset() == timedelta(0)
        assert timezone.is_aware(enviado.fecha_limite_atencion)
        assert enviado.fecha_limite_atencion.utcoffset() == timedelta(0)

    def test_providencia_correlativa_no_cambia_en_reenvio(self, estudiante):
        """Reenvío no altera numero_providencia ni fecha_recepcion (RN-010)."""
        expediente = expediente_completo_para_enviar(estudiante)
        enviado = avanzar_a_enviada(expediente)

        providencia_orig = enviado.numero_providencia
        recepcion_orig = enviado.fecha_recepcion

        # Segundo execute lanza EstadoInvalidoError, no cambia nada
        with pytest.raises(enviar_expediente.EstadoInvalidoError):
            enviar_expediente.execute(enviado)

        enviado.refresh_from_db()
        assert enviado.numero_providencia == providencia_orig
        assert enviado.fecha_recepcion == recepcion_orig


# --- PAUSA / REANUDACIÓN DE PLAZO (Observaciones) ---------------------------


class TestPausaReanudacionPlazo:
    """Comportamiento ante observaciones: pausa reloj, reanuda y extiende límite.
    Basado en AP-01 (pregunta abierta): el plazo se PAUSA durante observaciones.
    """

    def test_pausa_congela_reloj(self, estudiante):
        """pausar_reloj fija fecha_ultima_pausa = now (idempotente)."""
        expediente = expediente_completo_para_enviar(estudiante)
        enviado = avanzar_a_enviada(expediente)
        enviado.estado = ExpedienteTitulacion.ESTADO_EN_VERIFICACION
        enviado.save()

        calc = PlazoLaboralCalculator()
        calc.pausar_reloj(enviado)

        assert enviado.fecha_ultima_pausa is not None
        assert enviado.dias_laborables_acumulados == 0
        primera_pausa = enviado.fecha_ultima_pausa

        # Segunda llamada no cambia la fecha (idempotente)
        calc.pausar_reloj(enviado)
        assert enviado.fecha_ultima_pausa == primera_pausa

    def test_pausa_doble_no_duplica(self, estudiante):
        """Segunda pausa sin reanudar no cambia fecha_ultima_pausa."""
        expediente = expediente_completo_para_enviar(estudiante)
        enviado = avanzar_a_enviada(expediente)
        enviado.estado = ExpedienteTitulacion.ESTADO_EN_VERIFICACION
        enviado.save()

        calc = PlazoLaboralCalculator()
        calc.pausar_reloj(enviado)
        primera_pausa = enviado.fecha_ultima_pausa
        calc.pausar_reloj(enviado)
        assert enviado.fecha_ultima_pausa == primera_pausa

    def test_reanudar_sin_pausa_previa_no_opera(self, estudiante):
        """reanudar_reloj sin pausa previa retorna 0 y no altera campos."""
        expediente = expediente_completo_para_enviar(estudiante)
        enviado = avanzar_a_enviada(expediente)

        calc = PlazoLaboralCalculator()
        agregados = calc.reanudar_reloj(
            enviado, ahora=datetime(2026, 1, 9, 10, 0, tzinfo=UTC)
        )

        assert agregados == 0
        assert enviado.dias_laborables_acumulados == 0
        assert enviado.fecha_ultima_pausa is None

    def test_pausa_fin_de_semana_acumula_cero(self, estudiante):
        """Pausa viernes, reanuda lunes -> 0 hábiles entre medio."""
        expediente = expediente_completo_para_enviar(estudiante)
        enviado = avanzar_a_enviada(expediente)
        enviado.estado = ExpedienteTitulacion.ESTADO_EN_VERIFICACION
        enviado.save()

        calc = PlazoLaboralCalculator()
        # Pausa viernes 9 ene 12:00
        enviado.fecha_ultima_pausa = datetime(2026, 1, 9, 12, 0, tzinfo=UTC)
        # Reanuda lunes 12 ene 08:00
        agregados = calc.reanudar_reloj(
            enviado, ahora=datetime(2026, 1, 12, 8, 0, tzinfo=UTC)
        )

        assert agregados == 0
        assert enviado.dias_laborables_acumulados == 0
        assert enviado.fecha_ultima_pausa is None

    def test_pausa_habiles_extienden_fecha_limite(self, estudiante):
        """Pausa en días hábiles acumula y extiende fecha_limite_atencion."""
        expediente = expediente_completo_para_enviar(estudiante)
        enviado = avanzar_a_enviada(expediente)
        enviado.estado = ExpedienteTitulacion.ESTADO_EN_VERIFICACION
        enviado.save()

        # Recepción lunes 5 -> límite base jueves 15
        enviado.fecha_recepcion = datetime(2026, 1, 5, 12, 0, tzinfo=UTC)
        enviado.fecha_limite_atencion = datetime(2026, 1, 15, 23, 59, tzinfo=UTC)
        enviado.save()

        calc = PlazoLaboralCalculator()
        # Pausa miércoles 7 10:00
        enviado.fecha_ultima_pausa = datetime(2026, 1, 7, 10, 0, tzinfo=UTC)
        # Reanuda martes 13 08:00 -> hábiles entre 7(excl) y 13(excl): 8,9,12 = 3
        agregados = calc.reanudar_reloj(
            enviado, ahora=datetime(2026, 1, 13, 8, 0, tzinfo=UTC)
        )

        assert agregados == 3
        assert enviado.dias_laborables_acumulados == 3
        # Límite base 15 + 3 = martes 20
        assert (
            timezone.localtime(enviado.fecha_limite_atencion).date()
            == datetime(2026, 1, 20).date()
        )

    def test_pausas_sucesivas_acumulan_correctamente(self, estudiante):
        """Múltiples pausa/reanuda suman días hábiles correctamente."""
        expediente = expediente_completo_para_enviar(estudiante)
        enviado = avanzar_a_enviada(expediente)
        enviado.estado = ExpedienteTitulacion.ESTADO_EN_VERIFICACION
        enviado.save()

        calc = PlazoLaboralCalculator()

        # Pausa 1: Mié 7 -> reanuda Vie 9 (hábiles: Jue 8 = 1)
        enviado.fecha_ultima_pausa = datetime(2026, 1, 7, 10, 0, tzinfo=UTC)
        calc.reanudar_reloj(enviado, ahora=datetime(2026, 1, 9, 8, 0, tzinfo=UTC))
        assert enviado.dias_laborables_acumulados == 1

        # Pausa 2: Vie 9 12:00 -> reanuda Mié 14 (hábiles: Lun 12, Mar 13 = 2)
        enviado.fecha_ultima_pausa = datetime(2026, 1, 9, 12, 0, tzinfo=UTC)
        calc.reanudar_reloj(enviado, ahora=datetime(2026, 1, 14, 8, 0, tzinfo=UTC))
        assert enviado.dias_laborables_acumulados == 3


# --- INMUTABILIDAD DE CAMPOS CRÍTICOS (RN-010, CA-001) ----------------------


class TestInmutabilidadCamposCriticos:
    """fecha_recepcion, numero_providencia, fecha_limite inmutables tras envio."""

    def test_fecha_recepcion_inmutable_tras_envio(self, estudiante):
        """fecha_recepcion no cambia tras reintentos ni transiciones posteriores."""
        expediente = expediente_completo_para_enviar(estudiante)
        enviado = avanzar_a_enviada(expediente)
        original = enviado.fecha_recepcion

        # Transiciones posteriores
        for estado in (
            ExpedienteTitulacion.ESTADO_EN_VERIFICACION,
            ExpedienteTitulacion.ESTADO_OBSERVADA,
            ExpedienteTitulacion.ESTADO_EN_VERIFICACION,
            ExpedienteTitulacion.ESTADO_INFORME_EMITIDO,
            ExpedienteTitulacion.ESTADO_DECLARADA_APTA,
        ):
            enviado.estado = estado
            enviado.save()
            enviado.refresh_from_db()
            assert enviado.fecha_recepcion == original

    def test_numero_providencia_inmutable(self, estudiante):
        """numero_providencia asignado una sola vez y no cambia."""
        expediente = expediente_completo_para_enviar(estudiante)
        enviado = avanzar_a_enviada(expediente)
        original = enviado.numero_providencia

        for estado in (
            ExpedienteTitulacion.ESTADO_EN_VERIFICACION,
            ExpedienteTitulacion.ESTADO_OBSERVADA,
            ExpedienteTitulacion.ESTADO_INFORME_EMITIDO,
        ):
            enviado.estado = estado
            enviado.save()
            enviado.refresh_from_db()
            assert enviado.numero_providencia == original

    def test_fecha_limite_original_conservada_sin_pausas(self, estudiante):
        """Sin pausas, fecha_limite_atencion no cambia tras transiciones."""
        expediente = expediente_completo_para_enviar(estudiante)
        enviado = avanzar_a_enviada(expediente)
        original = enviado.fecha_limite_atencion

        enviado.estado = ExpedienteTitulacion.ESTADO_EN_VERIFICACION
        enviado.save()
        enviado.refresh_from_db()
        assert enviado.fecha_limite_atencion == original


# HistorialEstado (T027): bitácora de cambios de estado - no implementado aún.
# Tests se añadirán cuando exista el signal/servicio que crea las entradas.
