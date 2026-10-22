"""Servicio de validación de checklist completo (T029; RN-003).

Valida que el 100% de los requisitos del Art. 235 estén en estado VERIFICADO
antes de permitir la emisión del informe legal.
"""

from django.db import transaction

from apps.verificacion.adapters.models import ChecklistVerification
from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.verificacion.services.evaluar_checklist import is_checklist_fully_verified


class ChecklistIncompletoError(Exception):
    """El checklist no está completo (existen requisitos PENDIENTE u OBSERVADO)."""

    def __init__(self, requisitos_pendientes):
        self.requisitos_pendientes = requisitos_pendientes
        mensaje = (
            f"No se puede emitir el informe legal: el checklist no está completo. "
            f"Requisitos pendientes: {', '.join(requisitos_pendientes)}"
        )
        super().__init__(mensaje)
        self.requisitos_pendientes = requisitos_pendientes


def obtener_requisitos_pendientes(expediente_id):
    """
    Obtiene la lista de códigos de requisitos que no están VERIFICADO.

    Args:
        expediente_id: UUID del expediente

    Returns:
        Lista de códigos de requisitos que no están en estado VERIFICADO
    """
    from apps.peticiones.adapters.models import PeticionDocumental, ESTADO_VERIFICADO

    peticiones_pendientes = PeticionDocumental.objects.filter(
        expediente_id=expediente_id
    ).exclude(estado_peticion="VERIFICADO").select_related("requisito")

    return [p.requisito.codigo_requisito for p in peticiones_pendientes]


def execute(expediente_id):
    """
    Valida que el checklist esté completo (100% VERIFICADO) para emitir el informe legal.

    Args:
        expediente_id: UUID del expediente a validar

    Returns:
        True si el checklist está completo

    Raises:
        ChecklistIncompletoError: Si hay requisitos PENDIENTE u OBSERVADO
    """
    with transaction.atomic():
        # Verificar que el expediente existe
        try:
            expediente = ExpedienteTitulacion.objects.select_for_update().get(pk=expediente_id)
        except ExpedienteTitulacion.DoesNotExist:
            raise ValueError("El expediente no existe.")

        # Verificar que el expediente esté en estado que permita emitir informe
        estados_permitidos = ("EN_VERIFICACION", "OBSERVADA")
        if expediente.estado not in estados_permitidos:
            raise ValueError(
                f"El expediente debe estar en EN_VERIFICACION u OBSERVADA para emitir informe. "
                f"Estado actual: {expediente.estado}"
            )

        # Verificar checklist completo
        if not is_checklist_fully_verified(expediente_id):
            requisitos_pendientes = obtener_requisitos_pendientes(expediente_id)
            raise ChecklistIncompletoError(requisitos_pendientes)

        return True


def obtener_estado_checklist(expediente_id):
    """
    Obtiene el estado detallado del checklist para un expediente.

    Args:
        expediente_id: UUID del expediente

    Returns:
        Dict con estado del checklist y lista de requisitos pendientes
    """
    from apps.peticiones.adapters.models import PeticionDocumental, ESTADO_VERIFICADO

    peticiones = PeticionDocumental.objects.filter(
        expediente_id=expediente_id
    ).select_related("requisito")

    total = peticiones.count()
    verificados = peticiones.filter(estado_peticion="VERIFICADO").count()
    pendientes = peticiones.exclude(estado_peticion="VERIFICADO").select_related("requisito")

    return {
        "total_requisitos": total,
        "verificados": verificados,
        "pendientes": [
            {
                "peticion_id": str(p.id),
                "requisito_codigo": p.requisito.codigo_requisito,
                "requisito_nombre": p.requisito.nombre,
                "estado": p.estado_peticion,
            }
            for p in pendientes
        ],
        "completo": total == verificados,
    }