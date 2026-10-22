"""Caso de uso para subsanación de requisitos observados (T030; HU-008, RF-008, RN-011, CA-004).

Permite la carga de un nuevo PDF para un requisito OBSERVADO,
incrementa la versión del archivo a N+1, marca ObservacionAccionable.resuelta = True,
reanuda el reloj de plazo laborable y retorna el expediente al estado EN_VERIFICACION.
"""

from django.db import transaction, models
from django.utils import timezone

from apps.verificacion.adapters.models import (
    ChecklistVerification,
    ObservacionAccionable,
    ESTADO_VERIFICACION_OBSERVADO,
    ESTADO_VERIFICACION_PENDIENTE,
    ESTADO_VERIFICACION_VERIFICADO,
)
from apps.peticiones.adapters.models import (
    PeticionDocumental,
    DocumentoEntregado,
    ESTADO_CARGADO,
)
from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.expedientes.domain.plazo_calculator import PlazoLaboralCalculator
from apps.notificaciones.adapters.models import NotificacionInterna
from core.adapters.pdf_validation import validar_pdf_completo, PDFValidationError
from core.adapters.local_storage import guardar_archivo_privado


class SubsanacionNoPermitidaError(Exception):
    """El requisito no está en estado OBSERVADO o no tiene observación pendiente."""


class PeticionNoEncontradaError(Exception):
    """La petición no existe o no pertenece al expediente."""


class ObservacionNoEncontradaError(Exception):
    """No existe observación pendiente para esta petición."""


class UsuarioNoAutorizadoError(Exception):
    """El usuario no tiene permisos para subsanar este requisito."""


class ValidacionPDFError(Exception):
    """Error en la validación del archivo PDF."""

    def __init__(self, message, code="pdf_validation_error"):
        super().__init__(message)
        self.code = code


def _get_siguiente_version(peticion):
    """Obtiene el siguiente número de versión para la petición."""
    ultima_version = peticion.documentos_entregados.aggregate(
        max_version=models.Max("version")
    )["max_version"]
    return (ultima_version or 0) + 1


def _marcar_anterior_no_vigente(peticion):
    """Marca el documento anterior como no vigente."""
    DocumentoEntregado.objects.filter(peticion=peticion, es_vigente=True).update(
        es_vigente=False
    )


def _reanudar_plazo_y_cambiar_estados(expediente, peticion):
    """Reanuda el reloj y cambia estados a EN_VERIFICACION/CARGADO."""
    # Reanudar el reloj de plazo laborable (AP-01)
    PlazoLaboralCalculator().reanudar_reloj(expediente)

    # Cambiar estado de la petición a CARGADO
    peticion.estado_peticion = "CARGADO"
    peticion.fecha_actualizacion = timezone.now()
    peticion.save(update_fields=["estado_peticion", "fecha_actualizacion"])

    # Cambiar estado del expediente a EN_VERIFICACION
    expediente.estado = ExpedienteTitulacion.ESTADO_EN_VERIFICACION
    expediente.save(update_fields=["estado", "fecha_actualizacion", "fecha_ultima_pausa", "fecha_limite_atencion", "dias_laborables_acumulados"])


def execute(usuario, checklist_verification_id, archivo, nombre_original):
    """
    Ejecuta la subsanación de un requisito observado.

    Args:
        usuario: Usuario autenticado (ESTUDIANTE o SECRETARIA_CARRERA - DEC-02)
        checklist_verification_id: UUID de la verificación de checklist
        archivo: Archivo binario (request.FILES['archivo'])
        nombre_original: Nombre original del archivo

    Returns:
        DocumentoEntregado creado con la nueva versión

    Raises:
        SubsanacionNoPermitidaError: Si el requisito no está en OBSERVADO
        PeticionNoEncontradaError: Si la petición no existe
        ObservacionNoEncontradaError: Si no hay observación pendiente
        UsuarioNoAutorizadoError: Si el usuario no tiene permisos
        ValidacionPDFError: Si el archivo no pasa validaciones PDF
    """
    # Validar rol del usuario (DEC-02: ESTUDIANTE o SECRETARIA_CARRERA)
    roles_permitidos = ["ESTUDIANTE", "SECRETARIA_CARRERA"]
    if not any(usuario.has_role(rol) for rol in ["ESTUDIANTE", "SECRETARIA_CARRERA"]):
        raise UsuarioNoAutorizadoError(
            "Solo ESTUDIANTE y SECRETARIA_CARRERA pueden subsanar requisitos."
        )

    if not archivo:
        raise ValidacionPDFError("No se proporcionó archivo.", code="no_file")

    with transaction.atomic():
        # Bloquear la verificación de checklist
        try:
            checklist_verif = ChecklistVerification.objects.select_for_update().get(
                pk=checklist_verification_id
            )
        except ChecklistVerification.DoesNotExist:
            raise SubsanacionNoPermitidaError("La verificación de checklist no existe.")

        expediente = checklist_verif.expediente
        requisito = checklist_verif.requisito

        # Verificar estado del expediente (debe estar OBSERVADA)
        if expediente.estado != ExpedienteTitulacion.ESTADO_OBSERVADA:
            raise SubsanacionNoPermitidaError(
                f"El expediente debe estar en OBSERVADA. Estado actual: {expediente.estado}"
            )

        # Verificar que la verificación esté en OBSERVADO
        if checklist_verif.estado_verificacion != ESTADO_VERIFICACION_OBSERVADO:
            raise SubsanacionNoPermitidaError(
                f"El requisito debe estar en OBSERVADO. Estado actual: {checklist_verif.estado_verificacion}"
            )

        # Verificar permisos (ESTUDIANTE propietario o SECRETARIA_CARRERA de la carrera)
        es_estudiante_propietario = usuario == expediente.estudiante
        es_secretaria_carrera = (
            usuario.has_role("SECRETARIA_CARRERA")
            and str(usuario.carrera_id) == str(expediente.carrera_id)
        )

        if not (es_estudiante_propietario or es_secretaria_carrera):
            raise UsuarioNoAutorizadoError(
                "Solo el estudiante propietario o la Secretaría de Carrera "
                "de la misma carrera pueden subsanar."
            )

        # Obtener la petición asociada
        try:
            peticion = PeticionDocumental.objects.select_for_update().get(
                expediente=expediente, requisito=checklist_verif.requisito
            )
        except PeticionDocumental.DoesNotExist:
            raise PeticionNoEncontradaError("La petición no existe o no pertenece al expediente.")

        # Verificar que la petición esté en OBSERVADO
        if peticion.estado_peticion != "OBSERVADO":
            raise SubsanacionNoPermitidaError(
                f"La petición debe estar en OBSERVADO. Estado actual: {peticion.estado_peticion}"
            )

        # Verificar que existe observación pendiente
        observacion = ObservacionAccionable.objects.filter(
            peticion=peticion, resuelta=False
        ).first()
        if not observacion:
            raise ObservacionNoEncontradaError(
                "No existe observación pendiente de resolución para esta petición."
            )

        # Validar PDF
        try:
            metadata = validar_pdf_completo(archivo)
        except PDFValidationError as error:
            raise ValidacionPDFError(str(error), code=error.code)

        # Marcar observación como resuelta
        observacion.resuelta = True
        observacion.fecha_resolucion = timezone.now()
        observacion.save(update_fields=["resuelta", "fecha_resolucion"])

        # Obtener siguiente versión y marcar anterior como no vigente
        siguiente_version = _get_siguiente_version(peticion)
        _marcar_anterior_no_vigente(peticion)

        # Guardar archivo en almacenamiento privado
        archivo_path = guardar_archivo_privado(
            file=archivo,
            expediente_id=str(expediente.id),
            nombre_original=nombre_original,
        )

        # Crear nuevo DocumentoEntregado versión N+1
        documento = DocumentoEntregado.objects.create(
            peticion=peticion,
            version=siguiente_version,
            archivo_path=archivo_path,
            nombre_original=nombre_original,
            tamanio_bytes=metadata["tamanio_bytes"],
            hash_sha256=metadata["hash_sha256"],
            tipo_mime=metadata["tipo_mime"],
            subido_por=usuario,
            es_vigente=True,
        )

        # Actualizar estados
        peticion.estado_peticion = "CARGADO"
        peticion.fecha_actualizacion = timezone.now()
        peticion.save(update_fields=["estado_peticion", "fecha_actualizacion"])

        checklist_verif.estado_verificacion = ESTADO_VERIFICACION_PENDIENTE
        checklist_verif.fecha_actualizacion = timezone.now()
        checklist_verif.save(update_fields=["estado_verificacion", "fecha_actualizacion"])

        # Reanudar plazo y cambiar estados a EN_VERIFICACION / CARGADO
        _reanudar_plazo_y_cambiar_estados(expediente, peticion)

        # Notificar al jurista/analista que hay una subsanación
        NotificacionInterna.objects.create(
            usuario_destino=expediente.estudiante,
            expediente=expediente,
            peticion=peticion,
            titulo=f"Subsanación recibida: {peticion.requisito.nombre}",
            mensaje=(
                f"El estudiante ha subsanado la observación en el requisito "
                f"'{peticion.requisito.nombre}' del expediente "
                f"{expediente.numero_expediente}.\n\n"
                f"El requisito ha pasado a estado CARGADO y el expediente a EN_VERIFICACION.\n\n"
                f"Por favor, proceda a la verificación."
            ),
        )

        return documento