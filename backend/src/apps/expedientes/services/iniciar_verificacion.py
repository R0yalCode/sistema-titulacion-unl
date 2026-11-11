"""Caso de uso: iniciar la verificación de un expediente (PLB-E2-01; H-01, H-17).

`POST /api/v1/expedientes/{id}/iniciar-verificacion/`. El SECRETARIO_ABOGADO
de la facultad del expediente inicia de forma explícita la verificación de
un expediente `ENVIADA` (DP-01; celda RBAC autorizada por AUT-02). En una
única transacción, con el expediente bloqueado (`select_for_update`):

1. revalida el rol y la facultad del actor (defensa en profundidad; la vista
   ya filtra por ámbito y aplica la matriz RBAC);
2. exige el estado `ENVIADA`;
3. crea, de forma idempotente, una fila `ChecklistVerification` PENDIENTE por
   cada requisito base activo de FASE_1 (los cinco del Art. 235), reutilizando
   `_get_or_create_checklist_verification` (H-17);
4. registra `ENVIADA -> EN_VERIFICACION` con `registrar_transicion()` (DT-12):
   un `HistorialEstado` y un `ESTADO_CAMBIADO` con el actor autenticado;
5. notifica al estudiante (solo informativo).

Si cualquier paso falla, la transacción revierte todo: ni cambio de estado
ni filas de checklist huérfanas. Una segunda llamada concurrente espera el
bloqueo y encuentra el expediente fuera de `ENVIADA` (error de estado).

El plazo **no** cambia: sigue corriendo desde `fecha_recepcion` (RN-002).
El ANALISTA_APOYO queda excluido hasta que se decida DP-01b.
"""

from django.db import transaction

from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.expedientes.services.transiciones import registrar_transicion
from apps.notificaciones.adapters.models import NotificacionInterna
from apps.peticiones.adapters.models import FASE_1, CatalogoDocumental
from apps.verificacion.services.evaluar_checklist import (
    _get_or_create_checklist_verification,
)

ROL_AUTORIZADO = "SECRETARIO_ABOGADO"
REQUISITOS_BASE_ESPERADOS = 5
ORIGEN = "iniciar_verificacion"


class ExpedienteNoEncontradoError(Exception):
    """El expediente no existe."""


class UsuarioNoAutorizadoError(Exception):
    """El actor no es SECRETARIO_ABOGADO de la facultad del expediente."""


class EstadoInvalidoError(Exception):
    """El expediente no está en estado ENVIADA."""


class CatalogoIncompletoError(Exception):
    """El catálogo base vigente no tiene los cinco requisitos del Art. 235."""


def _misma_facultad(actor, expediente) -> bool:
    if not actor.facultad_id or not expediente.facultad_id:
        return False
    return str(actor.facultad_id) == str(expediente.facultad_id)


def execute(expediente_id, *, actor):
    """Inicia la verificación: ENVIADA -> EN_VERIFICACION + checklist.

    Args:
        expediente_id: identificador del expediente.
        actor: usuario autenticado que ejecuta la acción.

    Returns:
        El `ExpedienteTitulacion` actualizado.

    Raises:
        UsuarioNoAutorizadoError: el actor no es SECRETARIO_ABOGADO o no
            pertenece a la facultad del expediente.
        ExpedienteNoEncontradoError: el expediente no existe.
        EstadoInvalidoError: el expediente no está en ENVIADA.
        CatalogoIncompletoError: el catálogo base vigente está incompleto.
    """
    if not actor.has_role(ROL_AUTORIZADO):
        raise UsuarioNoAutorizadoError(
            "Solo el SECRETARIO_ABOGADO puede iniciar la verificación."
        )

    with transaction.atomic():
        try:
            expediente = ExpedienteTitulacion.objects.select_for_update().get(
                pk=expediente_id
            )
        except ExpedienteTitulacion.DoesNotExist as error:
            raise ExpedienteNoEncontradoError("El expediente no existe.") from error

        if not _misma_facultad(actor, expediente):
            raise UsuarioNoAutorizadoError(
                "El usuario no pertenece a la facultad del expediente."
            )

        if expediente.estado != ExpedienteTitulacion.ESTADO_ENVIADA:
            raise EstadoInvalidoError(
                "Solo un expediente en estado ENVIADA puede pasar a verificación. "
                f"Estado actual: {expediente.estado}."
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
                "El catálogo base del Art. 235 requiere "
                f"{REQUISITOS_BASE_ESPERADOS} requisitos vigentes; se "
                f"encontraron {len(catalogo)}."
            )

        for requisito in catalogo:
            _get_or_create_checklist_verification(expediente, requisito)

        registrar_transicion(
            expediente,
            ExpedienteTitulacion.ESTADO_EN_VERIFICACION,
            actor,
            origen=ORIGEN,
        )

        NotificacionInterna.objects.create(
            usuario_destino=expediente.estudiante,
            expediente=expediente,
            titulo="Verificación iniciada",
            mensaje=(
                "Se inició la verificación de los requisitos del expediente "
                f"{expediente.numero_expediente}."
            ),
        )
    return expediente


__all__ = [
    "CatalogoIncompletoError",
    "EstadoInvalidoError",
    "ExpedienteNoEncontradoError",
    "UsuarioNoAutorizadoError",
    "execute",
]
