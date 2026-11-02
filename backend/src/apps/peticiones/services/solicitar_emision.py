"""Caso de uso para peticion interna de certificados (T021; HU-002, RF-004).

Cambia el estado de la peticion de PENDIENTE a SOLICITADO y despacha
una NotificacionInterna a la dependencia emisora (DEC-01).
"""
from django.db import transaction
from django.utils import timezone

from apps.notificaciones.adapters.models import NotificacionInterna
from apps.peticiones.adapters.models import (
    ESTADO_PENDIENTE,
    ESTADO_SOLICITADO,
    PeticionDocumental,
)
from apps.expedientes.adapters.models import ExpedienteTitulacion


class PeticionNoEncontradaError(Exception):
    """La peticion no existe o no pertenece al expediente."""


class EstadoPeticionInvalidoError(Exception):
    """La peticion no esta en estado PENDIENTE."""


class ExpedienteEstadoInvalidoError(Exception):
    """El expediente no esta en BORRADOR u OBSERVADA."""


class UsuarioNoAutorizadoError(Exception):
    """El usuario no puede solicitar la emision de esta peticion."""


class UsuarioEmisorNoEncontradoError(Exception):
    """No se encontro usuario de la dependencia emisora para notificar."""


def execute(usuario, peticion_id):
    """Ejecuta la peticion interna de emision de certificado."""
    with transaction.atomic():
        try:
            peticion = PeticionDocumental.objects.select_related(
                "expediente", "requisito"
            ).get(pk=peticion_id)
        except PeticionDocumental.DoesNotExist:
            raise PeticionNoEncontradaError(
                "La peticion documental no existe."
            )

        expediente = peticion.expediente

        if expediente.estado not in (
            ExpedienteTitulacion.ESTADO_BORRADOR,
            ExpedienteTitulacion.ESTADO_OBSERVADA,
        ):
            raise ExpedienteEstadoInvalidoError(
                "Solo se pueden solicitar emisiones con el expediente en "
                f"BORRADOR u OBSERVADA (estado actual: {expediente.estado})."
            )

        if peticion.estado_peticion != ESTADO_PENDIENTE:
            raise EstadoPeticionInvalidoError(
                f"La peticion ya fue solicitada o procesada "
                f"(estado actual: {peticion.estado_peticion})."
            )

        if not (usuario == expediente.estudiante or usuario.has_role("SECRETARIA_CARRERA")):
            raise UsuarioNoAutorizadoError(
                "Solo el estudiante propietario o la Secretaria de Carrera "
                "pueden solicitar la emision de este certificado."
            )

        peticion.estado_peticion = ESTADO_SOLICITADO
        peticion.fecha_solicitud = timezone.now()
        peticion.save(update_fields=["estado_peticion", "fecha_solicitud", "fecha_actualizacion"])

        NotificacionInterna.objects.create(
            usuario_destino=obtener_usuario_emisor(peticion.dependencia_emisora, expediente),
            expediente=expediente,
            peticion=peticion,
            titulo=f"Solicitud de emision: {peticion.requisito.nombre}",
            mensaje=(
                f"Se ha solicitado la emision del certificado "
                f"'{peticion.requisito.nombre}' para el expediente "
                f"{expediente.numero_expediente} del estudiante "
                f"{expediente.estudiante.get_full_name() or expediente.estudiante.username}."
            ),
        )

        return peticion


def obtener_usuario_emisor(dependencia_emisora, expediente):
    """Obtiene un usuario representativo de la dependencia emisora.

    En el MVP, se busca un usuario con el rol correspondiente en la misma
    carrera/facultad. Si no existe, se retorna el primer usuario con ese rol.
    Lanza excepcion si no hay usuarios con ese rol en el sistema.
    """
    from apps.authentication.adapters.models import User

    usuarios = User.objects.filter(
        role_assignments__role__name=dependencia_emisora
    ).distinct()

    if dependencia_emisora in ("SECRETARIA_CARRERA", "DIRECTOR_CARRERA"):
        usuarios = usuarios.filter(carrera_id=expediente.carrera_id)
    elif dependencia_emisora in ("SECRETARIO_ABOGADO", "ANALISTA_APOYO", "DECANO"):
        usuarios = usuarios.filter(facultad_id=expediente.facultad_id)

    usuario = usuarios.first()
    if not usuario:
        usuario = User.objects.filter(
            role_assignments__role__name=dependencia_emisora
        ).first()

    if not usuario:
        raise UsuarioEmisorNoEncontradoError(
            f"No existe usuario con rol {dependencia_emisora} para notificar."
        )

    return usuario