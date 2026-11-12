"""Esquema OpenAPI del proyecto (drf-spectacular) con respuestas transversales.

Declara en el contrato respuestas que el esquema automático no puede
inferir de los serializers:

- `429` en operaciones mutantes protegidas por `MutantOperationThrottle`
  (VULN-001, INC-01-T01).
- Respuestas extra por acción que una vista declare en
  `openapi_respuestas_extra = {"<accion>": {"<codigo>": <declaración>}}`.

Errores de dominio (PLB-E1-04): los cuerpos se describen con componentes
reutilizables:

- `ErrorDominio`: `{"detail", "code"}` (ambos obligatorios), producido por
  `core.adapters.api_errors`.
- `ErrorSimple`: `{"detail"}`, para respuestas que DRF o Django generan sin
  `code` (p. ej. 404 de `get_object_or_404`, 429 de throttling, 500 de
  integridad SHA-256 de INC-01, que no cambia).
- `ErrorValidacion`: errores de validación de campos de los serializers de
  entrada (`{"campo": ["mensaje", ...]}`).

Esquema por código cuando la declaración es un texto (`anyOf`): 400 ->
ErrorDominio o ErrorValidacion; 404 -> ErrorDominio o ErrorSimple; 409, 422
y 500 -> ErrorDominio. Una declaración `{"descripcion": "...", "esquema": "simple"}`
fuerza `ErrorSimple` (se usa para el 500 de integridad).

Este módulo de `core` no importa de `apps` (aislamiento hexagonal).
"""

from drf_spectacular.openapi import AutoSchema
from drf_spectacular.plumbing import ResolvedComponent
from rest_framework.permissions import SAFE_METHODS

from core.adapters.throttling import MutantOperationThrottle

DESCRIPCION_429 = (
    "Demasiadas operaciones mutantes en poco tiempo para este usuario "
    "(MutantOperationThrottle). Reintente cuando indique la cabecera "
    "Retry-After."
)

ESQUEMA_ERROR_SIMPLE = {
    "type": "object",
    "properties": {"detail": {"type": "string"}},
    "required": ["detail"],
}

ESQUEMA_ERROR_DOMINIO = {
    "type": "object",
    "description": (
        "Error de dominio (PLB-E1-04). `code` es estable y lo consume el "
        "cliente; `detail` es un mensaje legible que puede cambiar."
    ),
    "properties": {
        "detail": {"type": "string"},
        "code": {"type": "string"},
    },
    "required": ["detail", "code"],
}

ESQUEMA_ERROR_VALIDACION = {
    "type": "object",
    "description": "Errores de validación de campos de entrada.",
    "additionalProperties": {"type": "array", "items": {"type": "string"}},
}

_COMPONENTES = {
    "ErrorDominio": ESQUEMA_ERROR_DOMINIO,
    "ErrorSimple": ESQUEMA_ERROR_SIMPLE,
    "ErrorValidacion": ESQUEMA_ERROR_VALIDACION,
}

_ESQUEMAS_POR_CODIGO = {
    "400": ("ErrorDominio", "ErrorValidacion"),
    "404": ("ErrorDominio", "ErrorSimple"),
}


def _respuesta_simple(descripcion: str) -> dict:
    return {
        "description": descripcion,
        "content": {"application/json": {"schema": ESQUEMA_ERROR_SIMPLE}},
    }


class SGTAutoSchema(AutoSchema):
    """AutoSchema que añade respuestas de seguridad y de errores de dominio."""

    def _ref(self, nombre: str) -> dict:
        componente = ResolvedComponent(
            name=nombre,
            type=ResolvedComponent.SCHEMA,
            object=nombre,
            schema=_COMPONENTES[nombre],
        )
        self.registry.register_on_missing(componente)
        return componente.ref

    def _respuesta_error(self, codigo: str, declaracion) -> dict:
        if isinstance(declaracion, dict):
            descripcion = declaracion["descripcion"]
            if declaracion.get("esquema") == "simple":
                return _respuesta_simple(descripcion)
        else:
            descripcion = declaracion
        nombres = _ESQUEMAS_POR_CODIGO.get(codigo, ("ErrorDominio",))
        if len(nombres) == 1:
            esquema = self._ref(nombres[0])
        else:
            # anyOf (no oneOf): un ErrorDominio también cumple ErrorSimple.
            esquema = {"anyOf": [self._ref(nombre) for nombre in nombres]}
        return {
            "description": descripcion,
            "content": {"application/json": {"schema": esquema}},
        }

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
            responses.setdefault("429", _respuesta_simple(DESCRIPCION_429))

        extra = getattr(self.view, "openapi_respuestas_extra", {}) or {}
        accion = getattr(self.view, "action", None)
        for codigo, declaracion in extra.get(accion, {}).items():
            responses.setdefault(
                str(codigo), self._respuesta_error(str(codigo), declaracion)
            )
        return operation
