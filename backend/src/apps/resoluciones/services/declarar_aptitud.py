"""Caso de uso para registro de declaratoria de aptitud (T035; HU-010, RF-011, RN-004, CA-006, DEC-04).

Registra la declaratoria de aptitud legal (Memorando N° 162) firmado externamente (FirmaEC).
Valida el PDF, asocia al expediente, cambia estado a DECLARADA_APTA y notifica con copia a autoridades y estudiante (DEC-04).
"""

from django.db import transaction
from django.utils import timezone

from apps.resoluciones.adapters.models import DeclaratoriaAptitud, InformeAptitud
from apps.expedientes.adapters.models import ExpedienteTitulacion, HistorialEstado
from apps.notificaciones.adapters.models import NotificacionInterna
from core.adapters.pdf_validation import validar_pdf_completo, PDFValidationError


class DeclaratoriaYaExisteError(Exception):
    """El expediente ya tiene una declaratoria registrada."""


class ExpedienteNoValidoParaDeclaratoriaError(Exception):
    """El expediente no cumple los requisitos para la declaratoria."""


class UsuarioNoAutorizadoError(Exception):
    """El usuario no tiene permisos para registrar la declaratoria."""


class PDFInvalidoError(Exception):
    """El archivo PDF no pasa las validaciones de seguridad."""

    def __init__(self, message: str, code: str = "invalid_pdf"):
        super().__init__(message)
        self.code = code


def _generar_numero_memorando(expediente: 'ExpedienteTitulacion') -> str:
    """Genera número de memorando único: MEM-162-YYYY-NNNN."""
    from django.db.models import Max
    anio = timezone.now().year
    # Buscar el último número de memorando de este año
    ultimo = DeclaratoriaAptitud.objects.filter(
        numero_memorando__startswith=f"MEM-162-{anio}-"
    ).aggregate(Max("numero_memorando"))
    if ultimo["numero_memorando__max"]:
        try:
            ultimo_num = int(ultimo["numero_memorando__max"].split("-")[-1])
            nuevo_num = ultimo_num + 1
        except (ValueError, IndexError):
            nuevo_num = 1
    else:
        nuevo_num = 1
    return f"MEM-162-{anio}-{nuevo_num:04d}"


def _obtener_autoridades_facultad(facultad_id: str):
    """Obtiene los usuarios con rol DECANO y DIRECTOR_CARRERA de la facultad dada."""
    from apps.authentication.adapters.models import User, Role, UserRole

    try:
        roles_autoridades = Role.objects.filter(
            name__in=["DECANO", "DIRECTOR_CARRERA", "RESPONSABLE_DEPENDENCIA"]
        )
        return User.objects.filter(
            role_assignments__role__in=roles_autoridades,
            facultad_id=facultad_id,
        ).distinct()
    except Role.DoesNotExist:
        return User.objects.none()


def _crear_notificaciones_copia(expediente: 'ExpedienteTitulacion', numero_memorando: str, decano_emisor):
    """Crea notificaciones internas con copia a autoridades y estudiante (DEC-04)."""
    # Notificar al estudiante
    NotificacionInterna.objects.create(
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
    autoridades = _obtener_autoridades_facultad(str(expediente.facultad_id))
    for autoridad in autoridades:
        if autoridad.id != decano_emisor.id:  # No notificar al emisor
            NotificacionInterna.objects.create(
                usuario_destino=autoridad,
                expediente=expediente,
                titulo=f"Copia: Declaratoria de Aptitud - {expediente.numero_expediente}",
                mensaje=(
                    f"Se ha emitido la Declaratoria de Aptitud Legal (Memorando N° {numero_memorando}) "
                    f"para el expediente {expediente.numero_expediente} del estudiante "
                    f"{expediente.estudiante.get_full_name() or expediente.estudiante.username}. "
                    f"El expediente ha cambiado al estado DECLARADA_APTA."
                ),
            )


def execute(usuario, expediente_id, archivo_memorando, numero_memorando=None):
    """
    Registra la declaratoria de aptitud legal (Memorando N° 162).

    Args:
        usuario: Usuario autenticado (DECANO o Analista autorizado)
        expediente_id: UUID del expediente
        archivo_memorando: Archivo binario del Memorando N° 162 firmado (FirmaEC)
        numero_memorando: Número de memorando opcional (se autogenera si None)

    Returns:
        DeclaratoriaAptitud creada

    Raises:
        ExpedienteNoValidoParaDeclaratoriaError: Si el expediente no cumple requisitos
        DeclaratoriaYaExisteError: Si ya existe declaratoria para este expediente
        UsuarioNoAutorizadoError: Si el usuario no tiene permisos
        PDFInvalidoError: Si el archivo no pasa validaciones PDF
    """
    # Validar rol del usuario (DECANO o ANALISTA_APOYO autorizado)
    roles_permitidos = ["DECANO", "ANALISTA_APOYO"]
    if not any(usuario.has_role(rol) for rol in ["DECANO", "ANALISTA_APOYO"]):
        raise UsuarioNoAutorizadoError(
            "Solo DECANO y ANALISTA_APOYO pueden registrar declaratorias de aptitud."
        )

    if not archivo_memorando:
        raise PDFInvalidoError("No se proporcionó archivo del memorando.", code="no_file")

    with transaction.atomic():
        # Obtener expediente con bloqueo
        try:
            expediente = ExpedienteTitulacion.objects.select_for_update().get(pk=expediente_id)
        except ExpedienteTitulacion.DoesNotExist:
            raise ValueError("El expediente no existe.")

        # Verificar que el expediente esté en INFORME_EMITIDO
        if expediente.estado != ExpedienteTitulacion.ESTADO_INFORME_EMITIDO:
            raise ExpedienteNoValidoParaDeclaratoriaError(
                f"El expediente debe estar en INFORME_EMITIDO. Estado actual: {expediente.estado}"
            )

        # Verificar que existe InformeAptitud (Providencia N° 590 emitida)
        if not hasattr(expediente, "informe_aptitud"):
            raise ExpedienteNoValidoParaDeclaratoriaError(
                "El expediente no tiene un Informe de Aptitud emitido (Providencia N° 590)."
            )

        # Verificar que no exista declaratoria previa
        if hasattr(expediente, "declaratoria_aptitud"):
            raise DeclaratoriaYaExisteError(
                f"El expediente {expediente.numero_expediente} ya tiene una declaratoria registrada."
            )

        # Verificar pertenencia a facultad
        user_facultad = str(usuario.facultad_id) if usuario.facultad_id else None
        expediente_facultad = str(expediente.facultad_id) if expediente.facultad_id else None
        if user_facultad != expediente_facultad:
            raise UsuarioNoAutorizadoError(
                "El usuario no pertenece a la facultad del expediente."
            )

        # Validar PDF del memorando firmado (FirmaEC)
        try:
            metadata = validar_pdf_completo(archivo_memorando)
        except PDFValidationError as error:
            raise PDFInvalidoError(str(error), code=error.code)

        # Generar número de memorando si no se proporciona
        if not numero_memorando:
            numero_memorando = _generar_numero_memorando(expediente)

        # Crear registro DeclaratoriaAptitud
        declaratoria = DeclaratoriaAptitud.objects.create(
            expediente=expediente,
            numero_memorando=numero_memorando,
            decano=usuario,
            archivo_memorando_firmado_path=f"expedientes/{timezone.now().year}/{expediente.id}/memorando_162_{numero_memorando.replace('/', '-').replace(' ', '_')}.pdf",
        )

        # Actualizar expediente a DECLARADA_APTA
        expediente.estado = ExpedienteTitulacion.ESTADO_DECLARADA_APTA
        expediente.fecha_actualizacion = timezone.now()
        expediente.save(update_fields=["estado", "fecha_actualizacion"])

        # Registrar en historial de estados
        HistorialEstado.objects.create(
            expediente=expediente,
            estado_anterior=ExpedienteTitulacion.ESTADO_INFORME_EMITIDO,
            estado_nuevo=ExpedienteTitulacion.ESTADO_DECLARADA_APTA,
            registrado_por=usuario,
        )

        # Notificar con copia a autoridades y estudiante (DEC-04)
        _crear_notificaciones_copia(expediente, numero_memorando, usuario)

        return declaratoria