"""Throttling de operaciones mutantes (VULN-001 / SEC-01, INC-01-T01).

Limita, por usuario autenticado, la frecuencia de las operaciones que
cambian el estado del trámite (enviar, observar, evaluar/subsanar
checklist, emitir informe, registrar declaratoria, solicitar emisión,
crear expediente). Todas comparten un único contador por usuario: el
objetivo es frenar automatizaciones abusivas o errores de cliente en
bucle, no limitar el trabajo normal de un funcionario.

Las lecturas (GET/HEAD/OPTIONS) nunca se limitan con esta clase.
La tasa se configura en `REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["mutante"]`
(variable de entorno `MUTANT_THROTTLE_RATE`).

Este módulo de `core` no importa de `apps` (aislamiento hexagonal).
"""

from rest_framework.permissions import SAFE_METHODS
from rest_framework.throttling import SimpleRateThrottle

MUTANT_THROTTLE_SCOPE = "mutante"


class MutantOperationThrottle(SimpleRateThrottle):
    """Tasa compartida de operaciones mutantes por usuario (HTTP 429 al exceder)."""

    scope = MUTANT_THROTTLE_SCOPE

    def allow_request(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return super().allow_request(request, view)

    def get_cache_key(self, request, view):
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated:
            ident = user.pk
        else:
            # Las vistas protegidas exigen autenticación; este camino solo
            # cubre peticiones anónimas que llegan antes del rechazo 401.
            ident = self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}
