from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView as BaseTokenObtainPairView,
)

from apps.authentication.services import password_reset
from core.adapters.api_errors import ErrorDominioAPI

from .serializers import (
    MensajeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetLinkSerializer,
    PasswordResetRequestSerializer,
    TokenObtainPairSerializer,
)
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


class EnlaceRestablecimientoInvalidoAPI(ErrorDominioAPI):
    """400: enlace inválido, caducado o ya utilizado (no se distingue cuál)."""

    default_code = "enlace_restablecimiento_invalido"
    default_detail = (
        "El enlace de restablecimiento no es válido o ha caducado. "
        "Solicite uno nuevo."
    )


class _VistaPublicaRestablecimiento(APIView):
    """Base de los endpoints públicos de recuperación (AUTH-RC).

    Sin autenticación (el usuario no puede iniciar sesión) y con el mismo
    throttle por IP consciente de `TRUSTED_PROXIES` que el login.
    """

    authentication_classes: list = []
    permission_classes = [AllowAny]
    throttle_classes = [TrustedProxyScopedRateThrottle]
    throttle_scope = "password_reset"


class PasswordResetRequestView(_VistaPublicaRestablecimiento):
    """Solicita el restablecimiento de contraseña por correo.

    Responde siempre 200 con el mismo cuerpo, exista o no una cuenta con ese
    correo (antienumeración de usuarios).
    """

    @extend_schema(
        request=PasswordResetRequestSerializer,
        responses={200: MensajeSerializer},
        auth=[],
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password_reset.solicitar_restablecimiento(serializer.validated_data["email"])
        return Response(
            {
                "detail": (
                    "Si existe una cuenta asociada a ese correo, se enviarán "
                    "las instrucciones para restablecer la contraseña."
                )
            }
        )


class PasswordResetValidateView(_VistaPublicaRestablecimiento):
    """Comprueba si un enlace de restablecimiento sigue siendo utilizable."""

    @extend_schema(
        request=PasswordResetLinkSerializer,
        responses={200: MensajeSerializer},
        auth=[],
    )
    def post(self, request):
        serializer = PasswordResetLinkSerializer(data=request.data)
        if not serializer.is_valid():
            raise EnlaceRestablecimientoInvalidoAPI()
        try:
            password_reset.validar_enlace(**serializer.validated_data)
        except password_reset.EnlaceInvalido:
            raise EnlaceRestablecimientoInvalidoAPI() from None
        return Response({"detail": "Enlace válido."})


class PasswordResetConfirmView(_VistaPublicaRestablecimiento):
    """Define la nueva contraseña con un enlace de restablecimiento válido.

    Aplica `AUTH_PASSWORD_VALIDATORS`. Tras el cambio el enlace deja de ser
    válido (un solo uso).
    """

    @extend_schema(
        request=PasswordResetConfirmSerializer,
        responses={200: MensajeSerializer},
        auth=[],
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        datos = serializer.validated_data
        try:
            password_reset.confirmar_restablecimiento(
                datos["uid"], datos["token"], datos["new_password"]
            )
        except password_reset.EnlaceInvalido:
            raise EnlaceRestablecimientoInvalidoAPI() from None
        except password_reset.ContrasenaInvalida as error:
            raise ValidationError({"new_password": error.mensajes}) from None
        return Response({"detail": "La contraseña se restableció correctamente."})
