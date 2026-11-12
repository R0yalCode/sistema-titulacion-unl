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
from apps.expedientes.adapters.models import ExpedienteTitulacion
from core.adapters.local_storage import compensacion_de_archivos
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
    # I-3 (H-I3-01): la compensación envuelve la transacción; si cualquier
    # paso posterior a la escritura (o el commit) falla, se borra el archivo
    # creado por esta operación y la BD revierte. Nada más se borra.
    with compensacion_de_archivos() as archivos, transaction.atomic():
        # Orden de bloqueo canónico (PLB-E1-04 + O-2, plan §4.2): primero el
        # expediente (bloqueo del agregado) y después la petición, cada uno
        # en su propia sentencia. Antes, `select_related(...).select_for_update()`
        # bloqueaba petición y expediente en un orden no controlado.
        expediente_id = (
            PeticionDocumental.objects.filter(pk=peticion_id)
            .values_list("expediente_id", flat=True)
            .first()
        )
        if expediente_id is None:
            raise PeticionNoEncontradaError("La petición documental no existe.")
        expediente = ExpedienteTitulacion.objects.select_for_update().get(
            pk=expediente_id
        )
        try:
            peticion = PeticionDocumental.objects.select_for_update(
                of=("self",)
            ).get(pk=peticion_id, expediente_id=expediente_id)
        except PeticionDocumental.DoesNotExist:
            raise PeticionNoEncontradaError("La petición documental no existe.")
        peticion.expediente = expediente

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
        # VULN-002 (INC-01-T02): SCOPE_ASIGNADO — la Secretaría solo carga en
        # peticiones cuya dependencia emisora es la propia Secretaría.
        asignada_a_secretaria = peticion.dependencia_emisora == "SECRETARIA_CARRERA"
        es_secretaria_carrera = has_role and carrera_match and asignada_a_secretaria

        if not (es_estudiante_propietario or es_secretaria_carrera):
            raise UsuarioNoAutorizadoError(
                "Solo el estudiante propietario o la Secretaría de Carrera "
                "de la misma carrera, en peticiones asignadas a la "
                "Secretaría, pueden cargar documentos."
            )

        # Validar PDF (tamaño, magic bytes, hash SHA-256)
        try:
            metadata = validar_pdf_completo(archivo)
        except PDFValidationError as error:
            raise ValidacionPDFError(str(error), code=error.code)

        # Guardar archivo en almacenamiento privado
        archivo_path = archivos.guardar(
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