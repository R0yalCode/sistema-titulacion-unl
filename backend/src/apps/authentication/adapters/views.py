from rest_framework_simplejwt.views import (
    TokenObtainPairView as BaseTokenObtainPairView,
)

from .serializers import TokenObtainPairSerializer
from .throttling import TrustedProxyScopedRateThrottle


class TokenPairView(BaseTokenObtainPairView):
    """Login (T012). Throttling por IP (SEC-T002, DEC-002: 5/min).

    `TrustedProxyScopedRateThrottle` (no `AnonRateThrottle` ni
    `ScopedRateThrottle` genérica): `AnonRateThrottle` tiene un `scope`
    fijo ('anon') que ignora `throttle_scope` de la vista, y el
    `get_ident()` por defecto de DRF confía ciegamente en
    `X-Forwarded-For` sin validar contra `TRUSTED_PROXIES` (SEC-T005).
    """

    serializer_class = TokenObtainPairSerializer
    throttle_classes = [TrustedProxyScopedRateThrottle]
    throttle_scope = "auth"
