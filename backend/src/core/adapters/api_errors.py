"""Respuesta HTTP común para errores de dominio (PLB-E1-04 + O-2).

Todas las clases devuelven el cuerpo JSON estructurado::

    {"detail": "Mensaje legible.", "code": "codigo_estable"}

sin necesidad de un manejador de excepciones global (D-5): DRF renderiza
tal cual un `detail` de tipo diccionario. El `code` es estable y lo
consume el cliente; el mensaje puede cambiar.

Criterio de uso (plan E1-04 §2):

- 400: precondición de estado no cumplida o cambio concurrente legítimo.
- 404: recurso inexistente o fuera de ámbito.
- 409: regla funcional pendiente de decisión (p. ej. O-1). No es BE-11: no
  hay ETag, If-Match ni concurrencia optimista.
- 422: requisitos del envío incompletos (contrato existente de T016).
- 500 explícito: inconsistencia de datos o de configuración institucional;
  se registra en el log técnico con su `code` y un contexto sin datos
  personales. Nunca se usa para reglas de negocio.

Este módulo de `core` no importa de `apps` (aislamiento hexagonal).
"""

import logging

from rest_framework import status
from rest_framework.exceptions import APIException

logger = logging.getLogger(
    __name__
)  # bajo "core": manejador JSON + filtro de datos sensibles


class ErrorDominioAPI(APIException):
    """Base: cuerpo `{"detail", "code"}` con el código de error visible."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "error_dominio"
    default_detail = "La operación no puede realizarse."

    def __init__(self, detail=None, code=None):
        codigo = code or self.default_code
        mensaje = str(detail) if detail is not None else str(self.default_detail)
        self.codigo = codigo
        self.mensaje = mensaje
        super().__init__({"detail": mensaje, "code": codigo}, codigo)


class SolicitudInvalidaAPI(ErrorDominioAPI):
    """400: la operación no es válida en el estado actual del recurso."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "solicitud_invalida"
    default_detail = "La operación no es válida en el estado actual."


class TransicionInvalidaAPI(ErrorDominioAPI):
    """400: la transición de estado no está permitida desde el estado vigente.

    Se produce sin efectos (rollback): el estado vigente se leyó con bloqueo.
    """

    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "transicion_invalida"
    default_detail = "Transición de estado no permitida."


class RecursoNoEncontradoAPI(ErrorDominioAPI):
    """404: el recurso no existe o está fuera del ámbito del usuario."""

    status_code = status.HTTP_404_NOT_FOUND
    default_code = "recurso_no_encontrado"
    default_detail = "El recurso solicitado no existe."


class ReglaPendienteAPI(ErrorDominioAPI):
    """409: la operación depende de una regla funcional aún no decidida."""

    status_code = status.HTTP_409_CONFLICT
    default_code = "regla_pendiente"
    default_detail = (
        "La operación depende de una regla funcional pendiente de decisión."
    )


class RequisitosIncompletosAPI(ErrorDominioAPI):
    """422: envío con requisitos sin documento en firme (contrato de T016)."""

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_code = "requisitos_incompletos"
    default_detail = "Envío incompleto: requisitos sin documento en firme."


class ErrorInternoExplicitoAPI(ErrorDominioAPI):
    """500 explícito y justificado: inconsistencia interna, nunca de negocio.

    Registra un evento técnico con el `code` y el contexto recibido. El
    contexto solo debe contener identificadores técnicos (ids, estados), no
    datos personales.
    """

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_code = "error_interno"
    default_detail = "Error interno del servidor."

    def __init__(self, detail=None, code=None, *, contexto=None):
        super().__init__(detail, code)
        logger.error(
            "Error interno explícito %s: %s",
            self.codigo,
            self.mensaje,
            extra={"codigo_error": self.codigo, "contexto": contexto or {}},
        )


class ConfiguracionInconsistenteAPI(ErrorInternoExplicitoAPI):
    """500: configuración institucional incompleta (catálogo, emisores)."""

    default_code = "configuracion_inconsistente"
    default_detail = "La configuración institucional está incompleta."


class InconsistenciaDatosAPI(ErrorInternoExplicitoAPI):
    """500: los datos persistidos contradicen una invariante del dominio."""

    default_code = "inconsistencia_datos"
    default_detail = "Los datos del trámite son inconsistentes."


__all__ = [
    "ConfiguracionInconsistenteAPI",
    "ErrorDominioAPI",
    "ErrorInternoExplicitoAPI",
    "InconsistenciaDatosAPI",
    "RecursoNoEncontradoAPI",
    "ReglaPendienteAPI",
    "RequisitosIncompletosAPI",
    "SolicitudInvalidaAPI",
    "TransicionInvalidaAPI",
]
