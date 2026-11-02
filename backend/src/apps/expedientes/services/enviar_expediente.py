"""Caso de uso de envio formal del expediente (T016; RF-002, RF-003).

Transicion `BORRADOR` -> `ENVIADA` (HU-004): valida que las 5 peticiones
documentales base del Art. 235 se encuentren en un estado con documento
en firme (`CARGADO`, `LEGALIZADO`, `VERIFICADO`), registra inmutablemente
la `fecha_recepcion` en UTC (RN-010), autogenera el numero correlativo de
providencia (`DEC-03` / AP-02) y calcula la `fecha_limite_atencion`
sumando 8 dias laborables (`PlazoLaboralCalculator`, T014).

Nota de alcance: la verificacion por metadatos de archivos PDF vigentes
(`DocumentoEntregado`, specify.md 7.4) se intensificara cuando se
implementen las tareas T020/T022/T023; la regla de completitud se apoya
por ahora en el estado de la peticion.
"""

import re
from datetime import datetime, time
from datetime import timezone as dt_timezone

from django.db import transaction
from django.utils import timezone

from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.expedientes.domain.plazo_calculator import PlazoLaboralCalculator
from apps.peticiones.adapters.models import PeticionDocumental

DIAS_PLAZO_RRA = 8

ESTADOS_SIN_DOCUMENTO_VIGENTE = {
    "PENDIENTE",
    "SOLICITADO",
    "OBSERVADO",
    "CANCELADA",
}


class EstadoInvalidoError(Exception):
    """Transicion de estado invalida para enviar (EX-006)."""


class RequisitosIncompletosError(Exception):
    """Algun requisito base no posee documento en firme (criterio T016)."""


def generar_numero_providencia():
    """Numero correlativo anual, p. ej. `PROV-2026-0001` (DEC-03 / AP-02)."""
    anio = timezone.localtime(timezone.now()).year
    ultimo = (
        ExpedienteTitulacion.objects.filter(
            numero_providencia__startswith=f"PROV-{anio}-",
        )
        .order_by("-numero_providencia")
        .values_list("numero_providencia", flat=True)
        .first()
    )
    if ultimo:
        coincidencia = re.match(r"^PROV-\d{4}-(\d{4})$", ultimo)
        correlativo = int(coincidencia.group(1)) + 1 if coincidencia else 1
    else:
        correlativo = 1
    return f"PROV-{anio}-{correlativo:04d}"


def _requisitos_sin_documento_vigente(expediente):
    """Codigos base cuya peticion no posee documento en firme (Art. 235)."""
    peticiones = list(
        PeticionDocumental.objects.filter(
            expediente=expediente,
            requisito__es_obligatorio_base=True,
            requisito__fase="FASE_1",
            requisito__activo=True,
        )
        .select_related("requisito")
        .order_by("requisito__codigo_requisito")
    )
    return [
        peticion.requisito.codigo_requisito
        for peticion in peticiones
        if peticion.estado_peticion in ESTADOS_SIN_DOCUMENTO_VIGENTE
    ]


def execute(expediente, ahora=None):
    """Envia el expediente: BORRADOR -> ENVIADA dentro de transaccion atomica."""
    with transaction.atomic():
        cadena = (
            ExpedienteTitulacion.objects.select_for_update()
            .filter(pk=expediente.pk)
            .first()
        )
        if cadena is None or cadena.estado != ExpedienteTitulacion.ESTADO_BORRADOR:
            raise EstadoInvalidoError(
                "Solo un expediente en estado BORRADOR puede enviarse "
                "(EX-006: transicion de estado invalida)."
            )
        faltantes = _requisitos_sin_documento_vigente(cadena)
        if faltantes:
            raise RequisitosIncompletosError(
                "Envio incompleto: los siguientes requisitos del Art. 235 "
                "no poseen documento en firme: " + ", ".join(faltantes)
            )
        recepcion = ahora if ahora is not None else timezone.now()
        cadena.estado = ExpedienteTitulacion.ESTADO_ENVIADA
        cadena.fecha_recepcion = recepcion
        cadena.numero_providencia = generar_numero_providencia()
        fecha_limite = PlazoLaboralCalculator().calcular_fecha_limite(
            timezone.localtime(recepcion).date(), DIAS_PLAZO_RRA
        )
        cadena.fecha_limite_atencion = timezone.make_aware(
            datetime.combine(fecha_limite, time.min),
            dt_timezone.utc,
        )
        cadena.save()
    return cadena


__all__ = [
    "EstadoInvalidoError",
    "RequisitosIncompletosError",
    "DIAS_PLAZO_RRA",
    "execute",
]
