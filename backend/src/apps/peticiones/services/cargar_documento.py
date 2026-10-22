"""Caso de uso para carga de documentos PDF (T023; HU-003, RF-005, DEC-02).

Recibe archivo multipart, valida con PDFValidationAdapter, guarda en almacenamiento
privado, registra subido_por y actualiza estado de peticion a CARGADO.
Versionado N+1: cada carga incrementa version y marca anterior como no vigente.
"""
from django.db import transaction
from django.utils import timezone

from apps.peticiones.adapters.models import (
    ESTADO_CARGADO,
    ESTADO_PENDIENTE,
    ESTADO_SOLICITADO,
    DocumentoEntregado,
    PeticionDocumental,
)
from core.adapters.local_storage import guardar_archivo_privado
from core.adapters.pdf_validation import (
    PDFValidationError,
    validar_pdf_completo,
)


class PeticionNoEncontradaError(Exception):
    """La peticion no existe."""


class EstadoPeticionInvalidoError(Exception):
    """La peticion no esta en estado que permita carga (PENDIENTE, SOLICITADO, OBSERVADO)."""


class UsuarioNoAutorizadoError(Exception):
    """El usuario no puede cargar documentos en esta peticion."""


class ValidacionPDFError(Exception):
    """Error en la validación del archivo PDF."""

    def __init__(self, message: str, code: str = "pdf_validation_error"):
        super().__init__(message)
        self.code = code


def _obtener_siguiente_version(peticion: PeticionDocumental) -> int:
    """Obtiene el siguiente número de versión para la petición."""
    ultima_version = peticion.documentos_entregados.aggregate(
        max_version=models.Max("version")
    )["max_version"]
    return (ultima_version or 0) + 1


# Importar models aquí para evitar import circular
from django.db import models


def execute(
    usuario,
    peticion_id,
    archivo,
    nombre_original: str,
) -> DocumentoEntregado:
    """Ejecuta la carga de un documento PDF para una petición.

    Args:
        usuario: Usuario autenticado que sube el archivo.
        peticion_id: UUID de la petición documental.
        archivo: Archivo binario (request.FILES['archivo']).
        nombre_original: Nombre original del archivo.

    Returns:
        DocumentoEntregado creado con metadata completa.

    Raises:
        PeticionNoEncontradaError: Si la petición no existe.
        EstadoPeticionInvalidoError: Si el estado no permite carga.
        UsuarioNoAutorizadoError: Si el usuario no tiene permisos.
        ValidacionPDFError: Si el archivo no pasa validaciones PDF.
    """
    with transaction.atomic():
        # Obtener petición con bloqueo para evitar condiciones de carrera
        try:
            peticion = PeticionDocumental.objects.select_related("expediente").select_for_update().get(
                pk=peticion_id
            )
        except PeticionDocumental.DoesNotExist:
            raise PeticionNoEncontradaError("La petición documental no existe.")

        expediente = peticion.expediente

        # Validar estado de la petición (permitir carga en PENDIENTE, SOLICITADO, OBSERVADO, CARGADO para versionado)
        estados_permitidos = (ESTADO_PENDIENTE, ESTADO_SOLICITADO, "OBSERVADO", ESTADO_CARGADO)
        if peticion.estado_peticion not in estados_permitidos:
            raise EstadoPeticionInvalidoError(
                f"No se puede cargar documento en estado {peticion.estado_peticion}. "
                f"Estados permitidos: {', '.join(estados_permitidos)}."
            )

        # Validar permisos: estudiante propietario o secretaria de carrera de la misma carrera
        es_estudiante_propietario = usuario == expediente.estudiante
        
        # Normalizar carrera_id a string para comparación (usuario.carrera_id puede ser str, expediente.carrera_id es UUID)
        usuario_carrera_id = str(usuario.carrera_id) if usuario.carrera_id else None
        expediente_carrera_id = str(expediente.carrera_id) if expediente.carrera_id else None
        carrera_match = (usuario_carrera_id == expediente_carrera_id)
        
        has_role = usuario.has_role("SECRETARIA_CARRERA")
        es_secretaria_carrera = has_role and carrera_match
        
        if not (es_estudiante_propietario or es_secretaria_carrera):
            raise UsuarioNoAutorizadoError(
                "Solo el estudiante propietario o la Secretaría de Carrera "
                "de la misma carrera pueden cargar documentos."
            )

        # Validar PDF (tamaño, magic bytes, hash SHA-256)
        try:
            metadata = validar_pdf_completo(archivo)
        except PDFValidationError as error:
            raise ValidacionPDFError(str(error), code=error.code)

        # Guardar archivo en almacenamiento privado
        archivo_path = guardar_archivo_privado(
            file=archivo,
            expediente_id=str(expediente.id),
            nombre_original=nombre_original,
        )

        # Obtener siguiente versión y marcar anterior como no vigente
        siguiente_version = _obtener_siguiente_version(peticion)

        # Marcar documento anterior como no vigente (si existe)
        DocumentoEntregado.objects.filter(peticion=peticion, es_vigente=True).update(
            es_vigente=False
        )

        # Crear nuevo DocumentoEntregado
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

        # Actualizar estado de la petición a CARGADO
        peticion.estado_peticion = ESTADO_CARGADO
        peticion.fecha_actualizacion = timezone.now()
        peticion.save(update_fields=["estado_peticion", "fecha_actualizacion"])

        return documento