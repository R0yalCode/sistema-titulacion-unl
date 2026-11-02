"""Pruebas unitarias del dominio puro de plazos (T014; RF-003, RN-002).

Fechas fijas de prueba; importacion directa del modulo (fixture db=False;
pausa/reanudacion operan sobre instancias no persistidas).
"""

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from django.utils import timezone as dj_timezone

from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.expedientes.domain.plazo_calculator import PlazoLaboralCalculator

UTC = ZoneInfo("UTC")

# El calendario institucional: feriado arbitrario apto para pruebas
FERIADO = date(2026, 1, 7)


@pytest.fixture(name="calculador")
def fixture_calculador():
    return PlazoLaboralCalculator(feriados=[FERIADO])


@pytest.fixture(name="calculador_simple")
def fixture_calculador_simple():
    return PlazoLaboralCalculator()


# --- calcular_fecha_limite ---


def test_8_dias_laborables_desde_lunes(calculador_simple):
    # lunes 2026-01-05: habiles 06,07,08,09,12,13,14,15 -> limite 15
    assert calculador_simple.calcular_fecha_limite(date(2026, 1, 5)) == date(
        2026, 1, 15
    )


def test_omite_feriado_configurado(calculador):
    # feriado Mie 07: habiles 06,08,09,12,13,14,15,16 -> limite 16
    assert calculador.calcular_fecha_limite(date(2026, 1, 5)) == date(2026, 1, 16)


def test_omite_sabado_y_domingo(calculador_simple):
    # inicio sabado 03: habiles Lun 05(1) Mar 06(2) Mie 07(3) Jue 08(4)
    # Vie 09(5) Lun 12(6) Mar 13(7) Mie 14(8)
    assert calculador_simple.calcular_fecha_limite(date(2026, 1, 3)) == date(
        2026, 1, 14
    )


def test_inicio_domingo(calculador_simple):
    # inicio domingo 04: el termino sigue contando desde el habil
    # siguiente (Lun 05), igual que el caso sabado -> limite Mie 14
    assert calculador_simple.calcular_fecha_limite(date(2026, 1, 4)) == date(
        2026, 1, 14
    )


def test_cantidad_de_dias_configurable(calculador_simple):
    assert calculador_simple.calcular_fecha_limite(date(2026, 1, 5), dias=3) == date(
        2026, 1, 8
    )


# --- pausar_reloj / reanudar_reloj (puros, sin save) ---


def _expediente_sin_persistir(**kwargs) -> ExpedienteTitulacion:
    return ExpedienteTitulacion(
        numero_expediente="EXP-TEST-T014",
        estudiante_id=None,
        **kwargs,
    )


def test_pausar_reloj_congela(tiempo_fijo, calculador_simple):
    expediente = _expediente_sin_persistir()
    calculador_simple.pausar_reloj(expediente)
    assert expediente.fecha_ultima_pausa == tiempo_fijo
    calculador_simple.pausar_reloj(expediente)
    assert expediente.fecha_ultima_pausa == tiempo_fijo


@pytest.fixture(name="tiempo_fijo")
def fixture_tiempo_fijo(monkeypatch):
    aguja = datetime(2026, 1, 6, 9, 0, tzinfo=UTC)
    monkeypatch.setattr(dj_timezone, "now", lambda: aguja)
    return aguja


def test_pausa_fin_de_semana_acumula_cero(calculador_simple, tiempo_fijo):
    # pausa Viernes 09 12:00, reanuda Lunes 12 08:00 -> 0 habiles entre
    expediente = _expediente_sin_persistir()
    pausa = datetime(2026, 1, 9, 12, 0, tzinfo=UTC)
    expediente.fecha_ultima_pausa = pausa
    reanudando = datetime(2026, 1, 12, 8, 0, tzinfo=UTC)
    agregados = calculador_simple.reanudar_reloj(expediente, ahora=reanudando)
    assert agregados == 0
    assert expediente.dias_laborables_acumulados == 0
    assert expediente.fecha_ultima_pausa is None


def test_pausa_habiles_acumulados_extienden_limite(calculador_simple):
    # recepcion Lun 05 -> limite base Jue 15. Pausa Mie 07, reanuda Mar 13
    # => habiles entre 07(excl) y 13(excl): 08,09,12 = 3 -> limite pasa a
    # 16(1) 19(2) 20(3) = Martes 20 enero
    expediente = _expediente_sin_persistir(
        fecha_recepcion=datetime(2026, 1, 5, 12, 0, tzinfo=UTC),
        fecha_limite_atencion=datetime(2026, 1, 15, 23, 59, tzinfo=UTC),
    )
    expediente.fecha_ultima_pausa = datetime(2026, 1, 7, 10, 0, tzinfo=UTC)
    agregados = calculador_simple.reanudar_reloj(
        expediente, ahora=datetime(2026, 1, 13, 8, 0, tzinfo=UTC)
    )
    assert agregados == 3
    assert expediente.dias_laborables_acumulados == 3
    assert dj_timezone.localtime(expediente.fecha_limite_atencion).date() == date(
        2026, 1, 20
    )


def test_reanudar_sin_pausa_previa_es_noop(calculador_simple, tiempo_fijo):
    expediente = _expediente_sin_persistir()
    assert (
        calculador_simple.reanudar_reloj(
            expediente, ahora=tiempo_fijo + timedelta(days=2)
        )
        == 0
    )
    assert expediente.dias_laborables_acumulados == 0


def test_pausas_sucesivas_acumulan(calculador_simple):
    expediente = _expediente_sin_persistir(
        fecha_recepcion=datetime(2026, 1, 5, 12, 0, tzinfo=UTC)
    )
    expediente.fecha_ultima_pausa = datetime(2026, 1, 7, 10, 0, tzinfo=UTC)
    calculador_simple.reanudar_reloj(
        expediente, ahora=datetime(2026, 1, 9, 8, 0, tzinfo=UTC)
    )
    assert expediente.dias_laborables_acumulados == 1
    expediente.fecha_ultima_pausa = datetime(2026, 1, 9, 12, 0, tzinfo=UTC)
    calculador_simple.reanudar_reloj(
        expediente, ahora=datetime(2026, 1, 14, 8, 0, tzinfo=UTC)
    )
    assert expediente.dias_laborables_acumulados == 3


def test_dias_laborables_entre(calculador_simple):
    assert (
        calculador_simple.dias_laborables_entre(date(2026, 1, 9), date(2026, 1, 12))
        == 0
    )
    assert (
        calculador_simple.dias_laborables_entre(date(2026, 1, 5), date(2026, 1, 16))
        == 8
    )
