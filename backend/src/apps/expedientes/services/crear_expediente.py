"""Caso de uso de creacion e inicializacion de expediente (T015; RF-001).

Valida la ausencia de expedientes activos del estudiante (HU-001,
RN-001), crea el `ExpedienteTitulacion` en estado `BORRADOR` e
inicializa automaticamente las 5 peticiones documentales base del
Art. 235 del RRA-UNL en estado `PENDIENTE`, todo dentro de una
transaccion atomica.
"""

from django.db import transaction
from django.utils import timezone

from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.peticiones.adapters.models import (
    ESTADO_PENDIENTE,
    FASE_1,
    CatalogoDocumental,
    PeticionDocumental,
)

REQUISITOS_BASE_ESPERADOS = 5


class ExpedienteActivoExistenteError(Exception):
    """El estudiante ya posee un expediente activo (HU-001 precondicion)."""


class CatalogoIncompletoError(Exception):
    """El catalogo base del Art. 235 no contiene los 5 requisitos vigentes."""


def generar_numero_expediente():
    """Numero correlativo anual, p. ej. `EXP-2026-0001` (plan.md 12)."""
    anio = timezone.localtime(timezone.now()).year
    prefijo = f"EXP-{anio}-"
    ultimo = (
        ExpedienteTitulacion.objects.filter(
            numero_expediente__startswith=prefijo,
        )
        .order_by("-numero_expediente")
        .values_list("numero_expediente", flat=True)
        .first()
    )
    correlativo = int(ultimo[len(prefijo) :]) + 1 if ultimo else 1
    return f"{prefijo}{correlativo:04d}"


def execute(estudiante, carrera_id):
    """Crea el expediente BORRADOR + 5 peticiones PENDIENTE; lo retorna."""
    with transaction.atomic():
        existe_activo = (
            ExpedienteTitulacion.objects.select_for_update()
            .filter(estudiante=estudiante, activa=True)
            .exists()
        )
        if existe_activo:
            raise ExpedienteActivoExistenteError(
                "El estudiante ya posee un expediente de titulacion activo; "
                "no se permite iniciar otro tramite en curso (HU-001)."
            )
        catalogo = list(
            CatalogoDocumental.objects.filter(
                es_obligatorio_base=True,
                fase=FASE_1,
                activo=True,
            ).order_by("codigo_requisito")
        )
        if len(catalogo) != REQUISITOS_BASE_ESPERADOS:
            raise CatalogoIncompletoError(
                f"El catalogo base del Art. 235 requiere "
                f"{REQUISITOS_BASE_ESPERADOS} requisitos vigentes; se "
                f"encontraron {len(catalogo)}."
            )
        expediente = ExpedienteTitulacion(
            numero_expediente=generar_numero_expediente(),
            estudiante=estudiante,
            carrera_id=carrera_id,
            facultad_id=estudiante.facultad_id,
            estado=ExpedienteTitulacion.ESTADO_BORRADOR,
            activa=True,
        )
        expediente.save()

        PeticionDocumental.objects.bulk_create(
            PeticionDocumental(
                expediente=expediente,
                requisito=requisito,
                estado_peticion=ESTADO_PENDIENTE,
                dependencia_emisora=requisito.rol_emisor_sugerido,
            )
            for requisito in catalogo
        )
        expediente.refresh_from_db()
        return expediente
