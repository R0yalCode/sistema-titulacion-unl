"""Calculador de plazos laborables del dominio (T014; RF-003, RN-002, AP-01).

Dominio puro (sin dependencias de ORM ni de infraestructura): las funciones
de pausa/reanudacion mutan la instancia recibida y NO la persisten; la capa
de servicio es responsable del save() dentro de una transaccion.

Reglas aprobadas (clarify.md FICHA AP-01, Alternativa 1 - COA Art. 160):
- El termino de 8 dias laborables se cuenta a partir del dia habil
  siguiente al de inicio.
- El reloj se PAUSA mientras el expediente permanece en OBSERVADA y se
  reanuda al subsanar (EN_VERIFICACION, FL-04); los dias laborables
  transcurridos durante la pausa se acumulan y extienden la fecha limite
  en la misma cantidad (sin penalizar al estudiante).
- Sábados, domingos y feriados institucionales configurados no computan.
"""

from datetime import date, datetime, timedelta
from typing import Iterable

from django.utils import timezone


class PlazoLaboralCalculator:
    def __init__(self, feriados: Iterable[date] | None = None):
        if feriados is None:
            self._feriados: frozenset[date] = frozenset()
        else:
            self._feriados = frozenset(feriados)

    def es_dia_laborable(self, fecha: date) -> bool:
        return fecha.weekday() < 5 and fecha not in self._feriados

    def siguiente_dia_laborable(self, fecha: date) -> date:
        siguiente = fecha + timedelta(days=1)
        while not self.es_dia_laborable(siguiente):
            siguiente += timedelta(days=1)
        return siguiente

    def agregar_dias_laborables(self, desde: date, dias: int) -> date:
        resultado = desde
        for _ in range(dias):
            resultado = self.siguiente_dia_laborable(resultado)
        return resultado

    def calcular_fecha_limite(self, fecha_inicio: date, dias: int = 8) -> date:
        return self.agregar_dias_laborables(fecha_inicio, dias)

    def _hoy(self) -> date:
        return timezone.localtime(timezone.now()).date()

    def dias_laborables_entre(self, inicio: date, fin: date) -> int:
        if fin <= inicio:
            return 0
        actual = self.siguiente_dia_laborable(inicio)
        dias = 0
        while actual < fin:
            dias += 1
            actual = self.siguiente_dia_laborable(actual)
        return dias

    def pausar_reloj(self, expediente) -> None:
        """Congela el reloj (idempotente). No persiste."""
        if expediente.fecha_ultima_pausa is not None:
            return
        expediente.fecha_ultima_pausa = timezone.now()

    def reanudar_reloj(self, expediente, ahora: datetime | None = None) -> int:
        """Reanuda el reloj tras la subsanacion. No persiste.

        Acumula los dias laborables transcurridos durante la pausa
        (estrictamente entre el dia de pausa y el de reanudacion) y extiende
        la fecha_limite_atencion en la misma cantidad. Devuelve los dias
        agregados. Idempotente si no hay pausa activa.
        """
        if expediente.fecha_ultima_pausa is None:
            return 0
        inicio_pausa = expediente.fecha_ultima_pausa
        if timezone.is_naive(inicio_pausa):
            inicio_pausa = timezone.make_aware(inicio_pausa)
        referencia = ahora if ahora is not None else timezone.now()
        if timezone.is_naive(referencia):
            referencia = timezone.make_aware(referencia)
        fecha_reanudacion = timezone.localtime(referencia).date()
        dias_pausa = self.dias_laborables_entre(
            timezone.localtime(inicio_pausa).date(), fecha_reanudacion
        )
        expediente.dias_laborables_acumulados += dias_pausa
        expediente.fecha_ultima_pausa = None
        if dias_pausa > 0:
            if expediente.fecha_limite_atencion is None:
                base = (
                    timezone.localtime(expediente.fecha_recepcion).date()
                    if expediente.fecha_recepcion is not None
                    else None
                )
                if base is not None:
                    expediente.fecha_limite_atencion = timezone.make_aware(
                        datetime.combine(
                            self.calcular_fecha_limite(
                                base, 8 + expediente.dias_laborables_acumulados
                            ),
                            datetime.min.time(),
                        )
                    )
            else:
                base = timezone.localtime(expediente.fecha_limite_atencion).date()
                expediente.fecha_limite_atencion = timezone.make_aware(
                    datetime.combine(
                        self.agregar_dias_laborables(base, dias_pausa),
                        datetime.min.time(),
                    )
                )
        return dias_pausa
