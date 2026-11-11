"""Esquema OpenAPI del proyecto (drf-spectacular) con respuestas transversales.

Declara en el contrato respuestas que el esquema automático no puede
inferir de los serializers:

- `429` en operaciones mutantes protegidas por `MutantOperationThrottle`
  (VULN-001, INC-01-T01).
- Respuestas extra por acción que una vista declare en
  `openapi_respuestas_extra = {"<accion>": {"<codigo>": "<descripcion>"}}`
  (p. ej. el 500 de integridad SHA-256 de la descarga, VULN-003).

Este módulo de `core` no importa de `apps` (aislamiento hexagonal).
"""

from drf_spectacular.openapi import AutoSchema
from rest_framework.permissions import SAFE_METHODS

from core.adapters.throttling import MutantOperationThrottle

DESCRIPCION_429 = (
    "Demasiadas operaciones mutantes en poco tiempo para este usuario "
    "(MutantOperationThrottle). Reintente cuando indique la cabecera "
    "Retry-After."
)

_ESQUEMA_ERROR = {
    "type": "object",
    "properties": {"detail": {"type": "string"}},
    "required": ["detail"],
}


def _respuesta(descripcion: str) -> dict:
    return {
        "description": descripcion,
        "content": {"application/json": {"schema": _ESQUEMA_ERROR}},
    }


class SGTAutoSchema(AutoSchema):
    """AutoSchema que añade respuestas de seguridad transversales."""

    def get_operation(self, *args, **kwargs):
        operation = super().get_operation(*args, **kwargs)
        if not operation:
            return operation
        responses = operation.setdefault("responses", {})

        throttles = getattr(self.view, "throttle_classes", None) or ()
        if self.method not in SAFE_METHODS and any(
            isinstance(t, type) and issubclass(t, MutantOperationThrottle)
            for t in throttles
        ):
            responses.setdefault("429", _respuesta(DESCRIPCION_429))

        extra = getattr(self.view, "openapi_respuestas_extra", {}) or {}
        accion = getattr(self.view, "action", None)
        for codigo, descripcion in extra.get(accion, {}).items():
            responses.setdefault(str(codigo), _respuesta(descripcion))
        return operation
