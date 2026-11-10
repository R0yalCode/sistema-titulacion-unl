"""Throttle de login consciente de TRUSTED_PROXIES (SEC-T002).

`rest_framework.throttling.BaseThrottle.get_ident()` (usado por defecto
por `ScopedRateThrottle`/`AnonRateThrottle`) confía ciegamente en
`X-Forwarded-For` si está presente y `NUM_PROXIES` no está configurado —
es decir, por defecto el throttling de DRF es trivialmente evadible
falsificando esa cabecera, independientemente de la validación de
TRUSTED_PROXIES que SEC-T005 ya implementó para la auditoría. Esta clase
reutiliza esa misma validación para que el throttling de login no tenga
una puerta trasera distinta a la de la auditoría.
"""

from rest_framework.throttling import ScopedRateThrottle

from core.adapters.client_ip import resolver_ip_cliente


class TrustedProxyScopedRateThrottle(ScopedRateThrottle):
    def get_ident(self, request):
        ip = resolver_ip_cliente(request)
        return ip or super().get_ident(request)
