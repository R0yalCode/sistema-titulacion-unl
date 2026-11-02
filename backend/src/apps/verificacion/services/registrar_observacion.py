"""Caso de uso para registrar observación accionable (T028; HU-007, RF-007, AP-01).

Registra la observación, cambia estados, pausa el plazo de 8 días hábiles
y notifica al estudiante (DEC-01).
"""

from django.db import transaction
from django.utils import timezone

from apps.verificacion.adapters.models import (
    ChecklistVerification,
    ESTADO_VERIFICACION_PENDIENTE,
    ESTADO_VERIFICACION_OBSERVADO,
    ObservacionAccionable,
)
from apps.peticiones.adapters.models import (
    PeticionDocumental,
    ESTADO_OBSERVADO as PETICION_ESTADO_OBSERVADO,
)
from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.expedientes.domain.plazo_calculator import PlazoLaboralCalculator
from apps.notificaciones.adapters.models import NotificacionInterna


class ObservacionYaExisteError(Exception):
    """El requisito ya tiene una observación pendiente de resolución."""


class ExpedienteNoEnVerificacionError(Exception):
    """El expediente no está en estado EN_VERIFICACION."""


class PeticionNoEncontradaError(Exception):
    """No existe petición asociada al requisito en el expediente."""


class UsuarioNoAutorizadoError(Exception):
    """El usuario no tiene permisos para registrar observaciones."""


def _create_observacion_and_notify(expediente, peticion, registrada_por, motivo):
    """Crea observación accionable y notifica al estudiante."""
    observacion = ObservacionAccionable.objects.create(
        expediente=expediente,
        peticion=peticion,
        registrada_por=registrada_por,
        motivo_observacion=motivo,
        resuelta=False,
    )

    # Notificar al estudiante (DEC-01)
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


def execute(usuario, expediente_id, peticion_id, motivo_observacion):
    """
    Registra una observación accionable sobre un requisito del expediente.

    Args:
        usuario: Usuario autenticado (SECRETARIO_ABOGADO o ANALISTA_APOYO)
        expediente_id: UUID del expediente
        peticion_id: UUID de la petición documental
        motivo_observacion: Motivo escrito de la observación

    Returns:
        ObservacionAccionable creada

    Raises:
        ExpedienteNoEnVerificacionError: Si el expediente no está en EN_VERIFICACION
        PeticionNoEncontradaError: Si la petición no existe o no pertenece al expediente
        ObservacionYaExisteError: Si ya hay una observación pendiente para esta petición
        UsuarioNoAutorizadoError: Si el usuario no tiene permisos
    """
    # Validar rol del usuario
    roles_permitidos = ["SECRETARIO_ABOGADO", "ANALISTA_APOYO"]
    if not any(usuario.has_role(rol) for rol in ["SECRETARIO_ABOGADO", "ANALISTA_APOYO"]):
        raise UsuarioNoAutorizadoError(
            "Solo SECRETARIO_ABOGADO y ANALISTA_APOYO pueden registrar observaciones."
        )

    if not motivo_observacion or not motivo_observacion.strip():
        raise ValueError("El motivo de observación es obligatorio.")

    with transaction.atomic():
        # Obtener expediente con bloqueo
        try:
            expediente = ExpedienteTitulacion.objects.select_for_update().get(pk=expediente_id)
        except ExpedienteTitulacion.DoesNotExist:
            raise ValueError("El expediente no existe.")

        # Verificar estado del expediente
        if expediente.estado != ExpedienteTitulacion.ESTADO_EN_VERIFICACION:
            raise ExpedienteNoEnVerificacionError(
                f"El expediente debe estar en EN_VERIFICACION. Estado actual: {expediente.estado}"
            )

        # Verificar pertenencia a facultad/carrera
        if usuario.has_role("SECRETARIO_ABOGADO") or usuario.has_role("ANALISTA_APOYO"):
            user_facultad = str(usuario.facultad_id) if usuario.facultad_id else None
            expediente_facultad = str(expediente.facultad_id) if expediente.facultad_id else None
            if user_facultad != expediente_facultad:
                raise UsuarioNoAutorizadoError(
                    "El usuario no pertenece a la facultad del expediente."
                )

        # Obtener petición con bloqueo
        try:
            peticion = PeticionDocumental.objects.select_for_update().get(
                pk=peticion_id, expediente=expediente
            )
        except PeticionDocumental.DoesNotExist:
            raise PeticionNoEncontradaError("La petición no existe o no pertenece al expediente.")

        # Verificar que no haya observación pendiente
        if ObservacionAccionable.objects.filter(
            peticion=peticion, resuelta=False
        ).exists():
            raise ObservacionYaExisteError(
                "Ya existe una observación pendiente de resolución para esta petición."
            )

        # Verificar que la petición no esté ya en OBSERVADO
        if peticion.estado_peticion == "OBSERVADO":
            raise ValueError("La petición ya está en estado OBSERVADO.")

        # PAUSA EL RELOJ DE 8 DÍAS HÁBILES (AP-01)
        PlazoLaboralCalculator().pausar_reloj(expediente)

        # Cambiar estado de la petición a OBSERVADO
        peticion.estado_peticion = "OBSERVADO"
        peticion.fecha_actualizacion = timezone.now()
        peticion.save(update_fields=["estado_peticion", "fecha_actualizacion"])

        # Cambiar estado del expediente a OBSERVADA
        expediente.estado = "OBSERVADA"
        expediente.save(update_fields=["estado", "fecha_actualizacion", "fecha_ultima_pausa"])

        # Actualizar ChecklistVerification a OBSERVADO
        ChecklistVerification.objects.filter(
            expediente=expediente, requisito=peticion.requisito
        ).update(
            estado_verificacion=ESTADO_VERIFICACION_OBSERVADO,
            evaluado_por=usuario,
            fecha_evaluacion=timezone.now(),
        )

        # Crear observación accionable
        observacion = ObservacionAccionable.objects.create(
            expediente=expediente,
            peticion=peticion,
            registrada_por=usuario,
            motivo_observacion=motivo_observacion.strip(),
            resuelta=False,
        )

        # Notificar al estudiante (DEC-01)
        NotificacionInterna.objects.create(
            usuario_destino=expediente.estudiante,
            expediente=expediente,
            peticion=peticion,
            titulo=f"Observación en requisito: {peticion.requisito.nombre}",
            mensaje=(
                f"Se ha registrado una observación en el requisito "
                f"'{peticion.requisito.nombre}' del expediente "
                f"{expediente.numero_expediente}.\n\n"
                f"Motivo: {motivo_observacion.strip()}\n\n"
                f"Por favor, revise y subsane el documento."
            ),
        )

        return observacion