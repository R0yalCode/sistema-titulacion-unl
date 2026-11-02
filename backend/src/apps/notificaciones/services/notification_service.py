"""Servicio de despacho de notificaciones internas in-app (T037; DEC-01).

Despachador sincrónico in-process sin dependencias de infraestructura SMTP.
Inserta el registro en la base de datos de forma sincrónica sin bloquear
la transacción principal.
"""

from typing import Optional

from django.db import transaction
from django.utils import timezone

from apps.notificaciones.adapters.models import NotificacionInterna
from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.peticiones.adapters.models import PeticionDocumental
from apps.authentication.adapters.models import User


class NotificacionNoCreadaError(Exception):
    """Error al crear la notificación."""


def crear_notificacion(
    *,
    usuario_destino: User,
    expediente: ExpedienteTitulacion,
    titulo: str,
    mensaje: str,
    peticion: Optional[PeticionDocumental] = None,
) -> NotificacionInterna:
    """
    Crea una notificación interna in-app de forma sincrónica.

    Args:
        usuario_destino: Usuario que recibirá la notificación.
        expediente: Expediente relacionado con la notificación.
        titulo: Título de la notificación.
        mensaje: Cuerpo del mensaje.
        peticion: Petición documental opcional relacionada.

    Returns:
        NotificacionInterna creada.

    Raises:
        NotificacionNoCreadaError: Si ocurre un error al crear la notificación.
    """
    try:
        with transaction.atomic():
            notificacion = NotificacionInterna.objects.create(
                usuario_destino=usuario_destino,
                expediente=expediente,
                peticion=peticion,
                titulo=titulo,
                mensaje=mensaje,
                leida=False,
                fecha_creacion=timezone.now(),
            )
            return notificacion
    except Exception as e:
        raise NotificacionNoCreadaError(f"Error al crear notificación: {str(e)}")


def crear_notificacion_expediente(
    *,
    usuario_destino: User,
    expediente_id: str,
    titulo: str,
    mensaje: str,
    peticion_id: Optional[str] = None,
) -> NotificacionInterna:
    """
    Crea una notificación asociada a un expediente (versión simplificada).

    Args:
        usuario_destino: Usuario que recibirá la notificación.
        expediente_id: UUID del expediente.
        titulo: Título de la notificación.
        mensaje: Cuerpo del mensaje.
        peticion_id: UUID opcional de la petición documental.

    Returns:
        NotificacionInterna creada.

    Raises:
        NotificacionNoCreadaError: Si no se encuentra el expediente o hay error.
    """
    try:
        with transaction.atomic():
            expediente = ExpedienteTitulacion.objects.select_for_update().get(pk=expediente_id)

            peticion = None
            if peticion_id:
                peticion = PeticionDocumental.objects.get(pk=peticion_id, expediente=expediente)

            notificacion = NotificacionInterna.objects.create(
                usuario_destino=usuario_destino,
                expediente=expediente,
                peticion=peticion,
                titulo=titulo,
                mensaje=mensaje,
                leida=False,
                fecha_creacion=timezone.now(),
            )
            return notificacion
    except ExpedienteTitulacion.DoesNotExist:
        raise NotificacionNoCreadaError(f"Expediente {expediente_id} no encontrado.")
    except PeticionDocumental.DoesNotExist:
        raise NotificacionNoCreadaError(f"Petición {peticion_id} no encontrada.")
    except Exception as e:
        raise NotificacionNoCreadaError(f"Error al crear notificación: {str(e)}")


def notificar_estudiante_subsanacion(
    *,
    expediente: ExpedienteTitulacion,
    numero_providencia: Optional[str] = None,
) -> NotificacionInterna:
    """
    Notifica al estudiante que su subsanación fue recibida.

    Args:
        expediente: Expediente con la subsanación.
        numero_providencia: Número de providencia opcional.

    Returns:
        NotificacionInterna creada.
    """
    titulo = f"Subsanación recibida - {expediente.numero_expediente}"
    if numero_providencia:
        titulo += f" (Prov. {numero_providencia})"

    mensaje = (
        f"Se ha recibido su documento subsanado para el expediente "
        f"{expediente.numero_expediente}. "
        f"El expediente ha vuelto a estado EN_VERIFICACION y será "
        f"revisado por el jurista asignado."
    )

    return crear_notificacion(
        usuario_destino=expediente.estudiante,
        expediente=expediente,
        titulo=titulo,
        mensaje=mensaje,
    )


def notificar_jurista_subsanacion(
    *,
    expediente: ExpedienteTitulacion,
    numero_providencia: Optional[str] = None,
    jurista: Optional[object] = None,
) -> Optional[NotificacionInterna]:
    """
    Notifica al jurista/analista que hay una subsanación para revisar.

    Args:
        expediente: Expediente con la subsanación.
        numero_providencia: Número de providencia opcional.
        jurista: Usuario jurista/analista a notificar (opcional).

    Returns:
        NotificacionInterna creada o None si no hay jurista.
    """
    if jurista is None:
        # Intentar obtener jurista de la facultad del expediente
        from apps.authentication.adapters.models import User, Role, UserRole
        try:
            rol_jurista = Role.objects.get(name="SECRETARIO_ABOGADO")
            jurista = User.objects.filter(
                role_assignments__role=rol_jurista,
                facultad_id=expediente.facultad_id,
            ).first()
        except Role.DoesNotExist:
            return None

    if jurista is None:
        return None

    titulo = f"Subsanación recibida para revisar - {expediente.numero_expediente}"
    mensaje = (
        f"El estudiante ha subsanado la observación del expediente "
        f"{expediente.numero_expediente}. "
        f"Por favor, proceda a la revisión del documento subsanado."
    )

    return crear_notificacion(
        usuario_destino=jurista,
        expediente=expediente,
        titulo=titulo,
        mensaje=mensaje,
    )


def notificar_estudiante_observacion(
    *,
    expediente: ExpedienteTitulacion,
    peticion: "PeticionDocumental",
    motivo: str,
) -> NotificacionInterna:
    """
    Notifica al estudiante que se registró una observación.

    Args:
        expediente: Expediente observado.
        peticion: Petición con la observación.
        motivo: Motivo de la observación.

    Returns:
        NotificacionInterna creada.
    """
    titulo = f"Observación en requisito: {peticion.requisito.nombre}"
    mensaje = (
        f"Se ha registrado una observación en el requisito "
        f"'{peticion.requisito.nombre}' del expediente "
        f"{expediente.numero_expediente}.\n\n"
        f"Motivo: {motivo}\n\n"
        f"Por favor, revise y subsane el documento."
    )

    return crear_notificacion(
        usuario_destino=expediente.estudiante,
        expediente=expediente,
        peticion=peticion,
        titulo=titulo,
        mensaje=mensaje,
    )


def notificar_informe_emitido(
    *,
    expediente: ExpedienteTitulacion,
    numero_providencia: str,
) -> NotificacionInterna:
    """
    Notifica al Decano/a que se emitió el informe legal.

    Args:
        expediente: Expediente con informe emitido.
        numero_providencia: Número de providencia.

    Returns:
        NotificacionInterna creada.
    """
    # Buscar decano de la facultad
    from apps.authentication.adapters.models import User, Role, UserRole
    try:
        rol_decano = Role.objects.get(name="DECANO")
        decano = User.objects.filter(
            role_assignments__role=rol_decano,
            facultad_id=expediente.facultad_id,
        ).first()

        if not decano:
            return None
    except Role.DoesNotExist:
        return None

    titulo = f"Informe Legal Emitido - {expediente.numero_expediente}"
    mensaje = (
        f"Se ha emitido el Informe Legal de Aptitud (Providencia N° {numero_providencia}) "
        f"para el expediente {expediente.numero_expediente}. "
        f"El expediente ha cambiado al estado INFORME_EMITIDO y está listo para la "
        f"Declaratoria de Aptitud por parte del Decanato."
    )

    return crear_notificacion(
        usuario_destino=decano,
        expediente=expediente,
        titulo=titulo,
        mensaje=mensaje,
    )


def notificar_declaratoria_emitida(
    *,
    expediente: ExpedienteTitulacion,
    numero_memorando: str,
    decano_emisor: object,
) -> tuple[Optional["NotificacionInterna"], list["NotificacionInterna"]]:
    """
    Notifica al estudiante y con copia a autoridades la declaratoria emitida.

    Args:
        expediente: Expediente con declaratoria emitida.
        numero_memorando: Número de memorando.
        decano_emisor: Usuario decano que firmó.

    Returns:
        Tupla (notificacion_estudiante, lista_notificaciones_autoridades).
    """
    # Notificar al estudiante
    notif_est = crear_notificacion(
        usuario_destino=expediente.estudiante,
        expediente=expediente,
        titulo=f"Declaratoria de Aptitud Emitida - {expediente.numero_expediente}",
        mensaje=(
            f"Se ha emitido la Declaratoria de Aptitud Legal (Memorando N° {numero_memorando}) "
            f"para su expediente {expediente.numero_expediente}. "
            f"El expediente ha cambiado al estado DECLARADA_APTA. "
            f"Ya puede proceder con el trámite de registro del título ante el SENESCYT."
        ),
    )

    # Notificar a autoridades de la facultad (copia)
    from apps.authentication.adapters.models import User, Role, UserRole
    try:
        roles_autoridades = Role.objects.filter(
            name__in=["DECANO", "DIRECTOR_CARRERA", "RESPONSABLE_DEPENDENCIA"]
        )
        autoridades = User.objects.filter(
            role_assignments__role__in=roles_autoridades,
            facultad_id=expediente.facultad_id,
        ).distinct()

        notificaciones_autoridades = []
        for autoridad in autoridades:
            if autoridad.id == decano_emisor.id:
                continue  # No notificar al emisor

            notif = NotificacionInterna.objects.create(
                usuario_destino=autoridad,
                expediente=expediente,
                titulo=f"Copia: Declaratoria de Aptitud - {expediente.numero_expediente}",
                mensaje=(
                    f"Se ha emitido la Declaratoria de Aptitud Legal (Memorando N° {expediente.numero_expediente}) "
                    f"para el expediente {expediente.numero_expediente} del estudiante "
                    f"{expediente.estudiante.get_full_name() or expediente.estudiante.username}. "
                    f"El expediente ha cambiado al estado DECLARADA_APTA."
                ),
            )
            notificaciones_autoridades.append(notif)

        return notif_est, notificaciones_autoridades
    except Role.DoesNotExist:
        return None, []


def marcar_como_leida(notificacion_id: str, usuario: User) -> bool:
    """
    Marca una notificación como leída.

    Args:
        notificacion_id: UUID de la notificación.
        usuario: Usuario que la marca como leída (debe ser el destinatario).

    Returns:
        True si se marcó correctamente, False si no existe o no pertenece al usuario.
    """
    try:
        notificacion = NotificacionInterna.objects.get(
            pk=notificacion_id, usuario_destino=usuario
        )
        notificacion.leida = True
        notificacion.save(update_fields=["leida"])
        return True
    except NotificacionInterna.DoesNotExist:
        return False