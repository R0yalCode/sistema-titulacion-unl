"""Caso de uso para evaluar checklist digital con bloqueo pesimista (T027; HU-006, RF-006, ADR-007).

Evalúa cada requisito (VERIFICADO / OBSERVADO) encapsulado en
@transaction.atomic utilizando select_for_update() para evitar
condiciones de carrera entre juristas y analistas de apoyo (AP-06).
"""

import logging

from django.db import transaction
from django.utils import timezone

from apps.verificacion.adapters.models import (
    ChecklistVerification,
    ESTADO_VERIFICACION_PENDIENTE,
    ESTADO_VERIFICACION_VERIFICADO,
    ESTADO_VERIFICACION_OBSERVADO,
    ObservacionAccionable,
)
from apps.peticiones.adapters.models import (
    PeticionDocumental,
    ESTADO_VERIFICADO as PETICION_ESTADO_VERIFICADO,
    ESTADO_OBSERVADO as PETICION_ESTADO_OBSERVADO,
)
from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.expedientes.services.transiciones import registrar_transicion
from apps.notificaciones.adapters.models import NotificacionInterna

logger = logging.getLogger(__name__)


class ChecklistVerificationNotFoundError(Exception):
    """La verificación de checklist no existe."""


class InvalidVerificationStateError(Exception):
    """Estado de verificación inválido (debe ser VERIFICADO u OBSERVADO)."""


class VerificationAlreadyCompletedError(Exception):
    """El requisito ya fue evaluado y no puede modificarse."""


class ExpedienteNotInVerificationError(Exception):
    """El expediente no está en estado EN_VERIFICACION."""


class UserNotAuthorizedError(Exception):
    """Usuario no autorizado para evaluar checklist."""


def _get_or_create_checklist_verification(expediente, requisito):
    """Obtiene o crea la verificación de checklist para un requisito."""
    verif, created = ChecklistVerification.objects.get_or_create(
        expediente=expediente,
        requisito=requisito,
        defaults={"estado_verificacion": "PENDIENTE"},
    )
    return verif


def _update_peticion_state(peticion, nuevo_estado):
    """Actualiza el estado de la petición y la fecha de actualización."""
    peticion.estado_peticion = nuevo_estado
    peticion.fecha_actualizacion = timezone.now()
    peticion.save(update_fields=["estado_peticion", "fecha_actualizacion"])


def _check_expediente_all_verified(expediente):
    """Verifica si todas las peticiones del expediente están VERIFICADO."""
    from apps.peticiones.adapters.models import PeticionDocumental, ESTADO_VERIFICADO
    
    peticiones_pendientes = PeticionDocumental.objects.filter(
        expediente=expediente
    ).exclude(estado_peticion=ESTADO_VERIFICADO).exists()
    
    return not peticiones_pendientes


def _create_observacion_and_notify(expediente, peticion, registrada_por, motivo):
    """Crea una observación accionable y notifica al estudiante."""
    observacion = ObservacionAccionable.objects.create(
        expediente=expediente,
        peticion=peticion,
        registrada_por=registrada_por,
        motivo_observacion=motivo,
        resuelta=False,
    )
    
    # Notificar al estudiante
    NotificacionInterna.objects.create(
        usuario_destino=expediente.estudiante,
        expediente=expediente,
        peticion=peticion,
        titulo=f"Observación en requisito: {peticion.requisito.nombre}",
        mensaje=(
            f"Se ha registrado una observación en el requisito "
            f"'{peticion.requisito.nombre}' del expediente "
            f"{expediente.numero_expediente}.\n\n"
            f"Motivo: {motivo}\n\n"
            f"Por favor, revise y subsane el documento."
        ),
    )
    
    return observacion


def execute(usuario, checklist_verification_id, nuevo_estado, motivo_observacion=None):
    """
    Ejecuta la evaluación de un requisito del checklist.
    
    Args:
        usuario: Usuario autenticado (SECRETARIO_ABOGADO o ANALISTA_APOYO)
        checklist_verification_id: UUID de la verificación de checklist
        nuevo_estado: "VERIFICADO" u "OBSERVADO"
        motivo_observacion: Obligatorio si nuevo_estado es "OBSERVADO"
        
    Returns:
        ChecklistVerification actualizada
        
    Raises:
        ChecklistVerificationNotFoundError: Si no existe la verificación
        InvalidVerificationStateError: Si el estado no es válido
        VerificationAlreadyCompletedError: Si ya fue evaluado
        ExpedienteNotInVerificationError: Si el expediente no está en verificación
        UserNotAuthorizedError: Si el usuario no tiene permisos
    """
    # Validar estado
    estados_validos = [ESTADO_VERIFICACION_VERIFICADO, ESTADO_VERIFICACION_OBSERVADO]
    if nuevo_estado not in estados_validos:
        raise InvalidVerificationStateError(
            f"Estado inválido: {nuevo_estado}. Debe ser 'VERIFICADO' u 'OBSERVADO'."
        )
    
    # Validar motivo si es OBSERVADO
    if nuevo_estado == ESTADO_VERIFICACION_OBSERVADO and not motivo_observacion:
        raise InvalidVerificationStateError(
            "El motivo de observación es obligatorio cuando el estado es OBSERVADO."
        )
    
    # Validar rol del usuario
    roles_permitidos = ["SECRETARIO_ABOGADO", "ANALISTA_APOYO"]
    if not any(usuario.has_role(rol) for rol in roles_permitidos):
        raise UserNotAuthorizedError(
            "Solo SECRETARIO_ABOGADO y ANALISTA_APOYO pueden evaluar el checklist."
        )
    
    with transaction.atomic():
        # Orden de bloqueo canónico (PLB-E1-04 + O-2, plan §4.2; H-29):
        # expediente -> petición -> checklist. Antes se bloqueaba primero el
        # checklist y el expediente al final (en registrar_transicion), en
        # orden inverso a `registrar_observacion`: interbloqueo 40P01
        # reproducido en PostgreSQL. Además el estado del expediente se
        # validaba sobre una lectura sin bloqueo (obsoleta).
        ids = (
            ChecklistVerification.objects.filter(pk=checklist_verification_id)
            .values_list("expediente_id", "requisito_id")
            .first()
        )
        if ids is None:
            raise ChecklistVerificationNotFoundError(
                "La verificación de checklist no existe."
            )
        expediente_id, requisito_id = ids
        expediente = ExpedienteTitulacion.objects.select_for_update().get(
            pk=expediente_id
        )
        peticion = (
            PeticionDocumental.objects.select_for_update(of=("self",))
            .filter(expediente_id=expediente_id, requisito_id=requisito_id)
            .first()
        )
        try:
            checklist_verif = (
                ChecklistVerification.objects.select_for_update(of=("self",))
                .select_related("requisito")
                .get(pk=checklist_verification_id, expediente_id=expediente_id)
            )
        except ChecklistVerification.DoesNotExist:
            raise ChecklistVerificationNotFoundError(
                "La verificación de checklist no existe."
            )
        # Las validaciones usan las filas recién bloqueadas, no copias previas.
        checklist_verif.expediente = expediente
        requisito = checklist_verif.requisito

        # Verificar que el expediente esté en estado EN_VERIFICACION
        if expediente.estado != ExpedienteTitulacion.ESTADO_EN_VERIFICACION:
            raise ExpedienteNotInVerificationError(
                f"El expediente debe estar en estado EN_VERIFICACION. Estado actual: {expediente.estado}"
            )
        
        # Verificar que el usuario pertenezca a la facultad/carrera del expediente
        logger.debug(
            "evaluar_checklist: user=%s roles=%s has_secretario=%s has_analista=%s",
            usuario.username,
            list(usuario.get_roles()),
            usuario.has_role("SECRETARIO_ABOGADO"),
            usuario.has_role("ANALISTA_APOYO"),
        )
        if usuario.has_role("SECRETARIO_ABOGADO") or usuario.has_role("ANALISTA_APOYO"):
            # Comparar como strings para evitar problemas de tipo UUID vs string
            user_facultad = str(usuario.facultad_id) if usuario.facultad_id else None
            expediente_facultad = str(expediente.facultad_id) if expediente.facultad_id else None
            logger.debug(
                "evaluar_checklist faculty check: user_facultad=%s expediente_facultad=%s match=%s",
                user_facultad,
                expediente_facultad,
                user_facultad == expediente_facultad,
            )
            if user_facultad != expediente_facultad:
                raise UserNotAuthorizedError(
                    "El usuario no pertenece a la facultad del expediente."
                )
        
        # Verificar que no esté ya evaluado (no PENDIENTE)
        if checklist_verif.estado_verificacion != ESTADO_VERIFICACION_PENDIENTE:
            raise VerificationAlreadyCompletedError(
                f"El requisito ya fue evaluado con estado: {checklist_verif.estado_verificacion}"
            )
        
        # Petición asociada (ya bloqueada arriba, en orden canónico)
        if peticion is None:
            # Crear la petición si no existe (para casos de test con nuevos requisitos)
            peticion = PeticionDocumental.objects.create(
                expediente=expediente,
                requisito=requisito,
                estado_peticion="PENDIENTE",
                dependencia_emisora=requisito.rol_emisor_sugerido,
            )
        
        # Actualizar la verificación
        checklist_verif.estado_verificacion = nuevo_estado
        checklist_verif.evaluado_por = usuario
        checklist_verif.fecha_evaluacion = timezone.now()
        checklist_verif.save(update_fields=[
            "estado_verificacion", "evaluado_por", "fecha_evaluacion", "fecha_actualizacion"
        ])
        
        # Actualizar estado de la petición
        if nuevo_estado == ESTADO_VERIFICACION_VERIFICADO:
            _update_peticion_state(peticion, PETICION_ESTADO_VERIFICADO)
        else:  # OBSERVADO
            _update_peticion_state(peticion, PETICION_ESTADO_OBSERVADO)
            
            # Cambiar estado del expediente a OBSERVADA
            registrar_transicion(
                expediente,
                ExpedienteTitulacion.ESTADO_OBSERVADA,
                usuario,
                origen="evaluar_checklist",
            )
            
            # Crear observación accionable
            _create_observacion_and_notify(
                expediente=expediente,
                peticion=peticion,
                registrada_por=usuario,
                motivo=motivo_observacion,
            )
        
        return checklist_verif


def is_checklist_fully_verified(expediente_id):
    """
    Verifica si el 100% de los requisitos del expediente están VERIFICADO.
    Usado para validar emisión de informe legal (RN-003).
    """
    from apps.peticiones.adapters.models import PeticionDocumental, ESTADO_VERIFICADO
    
    try:
        expediente = ExpedienteTitulacion.objects.get(pk=expediente_id)
    except ExpedienteTitulacion.DoesNotExist:
        return False
    
    return _check_expediente_all_verified(expediente)