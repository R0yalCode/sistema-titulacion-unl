from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentication.services import mfa, mfa_reset, password_reset
from core.adapters.api_errors import ErrorDominioAPI

from .serializers import (
    AuthResultSerializer,
    LoginSerializer,
    MensajeSerializer,
    MfaChallengeSerializer,
    MfaCodeSerializer,
    MfaRecoverySerializer,
    MfaResetConfirmSerializer,
    MfaResetRequestSerializer,
    MfaSetupSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetLinkSerializer,
    PasswordResetRequestSerializer,
)
from .throttling import TrustedProxyScopedRateThrottle

# --- Inicio de sesión en dos pasos (AUTH-B) ------------------------------
# Sustituye a `POST /api/v1/auth/token/` (T012), que emitía el JWT solo con
# contraseña y habría permitido saltarse el segundo factor.


class CredencialesInvalidasAPI(ErrorDominioAPI):
    """401 sin distinguir usuario inexistente, contraseña errónea o cuenta
    inactiva (antienumeración). No hereda de `AuthenticationFailed`: DRF lo
    convertiría en 403 en vistas sin autenticadores."""

    status_code = status.HTTP_401_UNAUTHORIZED
    default_code = "credenciales_invalidas"
    default_detail = "Usuario o contraseña incorrectos."


class RetoMfaInvalidoAPI(ErrorDominioAPI):
    default_code = "reto_mfa_invalido"
    default_detail = (
        "La verificación caducó o ya no es válida. Inicie sesión nuevamente."
    )


class CodigoMfaInvalidoAPI(ErrorDominioAPI):
    default_code = "codigo_mfa_invalido"
    default_detail = "El código no es válido. Verifique e intente nuevamente."


class EstadoMfaInvalidoAPI(ErrorDominioAPI):
    default_code = "estado_mfa_invalido"
    default_detail = (
        "La operación no corresponde al estado del autenticador. "
        "Inicie sesión nuevamente."
    )


class MfaBloqueadoAPI(ErrorDominioAPI):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_code = "mfa_bloqueado"
    default_detail = (
        "Demasiados intentos fallidos de verificación. Espere unos minutos "
        "antes de volver a intentarlo."
    )


_ERRORES = {
    mfa.CredencialesInvalidas: CredencialesInvalidasAPI,
    mfa.RetoInvalido: RetoMfaInvalidoAPI,
    mfa.CodigoInvalido: CodigoMfaInvalidoAPI,
    mfa.EstadoMfaInvalido: EstadoMfaInvalidoAPI,
    mfa.MfaBloqueado: MfaBloqueadoAPI,
}


def _cookie_confianza(request) -> str | None:
    return request.COOKIES.get(settings.MFA_TRUSTED_DEVICE_COOKIE_NAME)


def _respuesta(resultado: "mfa.ResultadoAutenticacion") -> Response:
    respuesta = Response(resultado.cuerpo())
    respuesta["Cache-Control"] = "no-store"
    if resultado.trusted_device_token:
        respuesta.set_cookie(
            settings.MFA_TRUSTED_DEVICE_COOKIE_NAME,
            resultado.trusted_device_token,
            max_age=settings.MFA_TRUSTED_DEVICE_DAYS * 24 * 3600,
            httponly=True,
            secure=settings.MFA_TRUSTED_DEVICE_COOKIE_SECURE,
            samesite="Strict",
            path="/api/v1/auth/",
        )
    return respuesta


class _VistaPublicaAuth(APIView):
    """Endpoints previos a la sesión: sin autenticadores y con throttle por
    IP consciente de `TRUSTED_PROXIES` (SEC-T002/SEC-T005)."""

    authentication_classes: list = []
    permission_classes = [AllowAny]
    throttle_classes = [TrustedProxyScopedRateThrottle]
    throttle_scope = "mfa"

    def handle_exception(self, exc):
        for origen, destino in _ERRORES.items():
            if isinstance(exc, origen):
                exc = destino()
                break
        return super().handle_exception(exc)


class LoginView(_VistaPublicaAuth):
    """Paso 1: usuario y contraseña (throttle `auth`, 5/min por IP).

    Nunca devuelve JWT sin segundo factor, salvo que la cookie de confianza
    del dispositivo sea válida y vigente (política de 5 días).
    """

    throttle_scope = "auth"

    @extend_schema(
        request=LoginSerializer, responses={200: AuthResultSerializer}, auth=[]
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        resultado = mfa.iniciar_sesion(
            request,
            serializer.validated_data["email"],
            serializer.validated_data["password"],
            _cookie_confianza(request),
        )
        return _respuesta(resultado)


class MfaSetupView(_VistaPublicaAuth):
    """Registro: genera el secreto pendiente y devuelve el QR (SVG).

    Llamarlo de nuevo con el mismo reto reinicia el registro con un secreto
    nuevo (reanudación segura de un registro incompleto).
    """

    @extend_schema(
        request=MfaChallengeSerializer, responses={200: MfaSetupSerializer}, auth=[]
    )
    def post(self, request):
        serializer = MfaChallengeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        datos = mfa.iniciar_registro(request, serializer.validated_data["challenge"])
        respuesta = Response(datos)
        respuesta["Cache-Control"] = "no-store"
        return respuesta


class MfaSetupConfirmView(_VistaPublicaAuth):
    """Registro: activa el MFA tras el primer código válido y entrega los
    códigos de recuperación una única vez."""

    @extend_schema(
        request=MfaCodeSerializer, responses={200: AuthResultSerializer}, auth=[]
    )
    def post(self, request):
        serializer = MfaCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        datos = serializer.validated_data
        resultado = mfa.confirmar_registro(
            request, datos["challenge"], datos["code"], datos["trust_device"]
        )
        return _respuesta(resultado)


class MfaVerifyView(_VistaPublicaAuth):
    """Paso 2: código TOTP actual de Google Authenticator."""

    @extend_schema(
        request=MfaCodeSerializer, responses={200: AuthResultSerializer}, auth=[]
    )
    def post(self, request):
        serializer = MfaCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        datos = serializer.validated_data
        resultado = mfa.verificar_segundo_factor(
            request, datos["challenge"], datos["code"], datos["trust_device"]
        )
        return _respuesta(resultado)


class MfaRecoveryView(_VistaPublicaAuth):
    """Pérdida del autenticador: un código de recuperación retira el
    autenticador anterior y exige registrar uno nuevo
    (`status=mfa_setup_required`)."""

    @extend_schema(
        request=MfaRecoverySerializer, responses={200: AuthResultSerializer}, auth=[]
    )
    def post(self, request):
        serializer = MfaRecoverySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        datos = serializer.validated_data
        resultado = mfa.recuperar_con_codigo(
            request, datos["challenge"], datos["recovery_code"]
        )
        return _respuesta(resultado)


class EnlaceMfaInvalidoAPI(ErrorDominioAPI):
    default_code = "enlace_mfa_invalido"
    default_detail = (
        "El enlace para restablecer el doble factor no es válido o ha "
        "caducado. Solicite uno nuevo."
    )


class MfaResetRequestView(_VistaPublicaAuth):
    """Restablecimiento del 2FA, paso 1 (MFA-RST): correo institucional,
    cédula y contraseña actual. Responde siempre igual; si los datos
    corresponden a una cuenta con 2FA, envía un enlace de un solo uso al
    correo registrado. No retira el 2FA por sí misma."""

    throttle_scope = "password_reset"

    @extend_schema(
        request=MfaResetRequestSerializer, responses={200: MensajeSerializer}, auth=[]
    )
    def post(self, request):
        serializer = MfaResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        datos = serializer.validated_data
        mfa_reset.solicitar_restablecimiento(
            request, datos["email"], datos["cedula"], datos["password"]
        )
        return Response(
            {
                "detail": (
                    "Si los datos corresponden a una cuenta con doble factor "
                    "activo, enviaremos un enlace de vigencia limitada al "
                    "correo registrado."
                )
            }
        )


class MfaResetConfirmView(_VistaPublicaAuth):
    """Restablecimiento del 2FA, paso 2: confirma el enlace recibido por
    correo y retira el autenticador; el siguiente ingreso exige registrar
    uno nuevo."""

    throttle_scope = "password_reset"

    @extend_schema(
        request=MfaResetConfirmSerializer, responses={200: MensajeSerializer}, auth=[]
    )
    def post(self, request):
        serializer = MfaResetConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            raise EnlaceMfaInvalidoAPI()
        try:
            mfa_reset.confirmar_restablecimiento(request, **serializer.validated_data)
        except mfa_reset.EnlaceMfaInvalido:
            raise EnlaceMfaInvalidoAPI() from None
        return Response(
            {
                "detail": (
                    "El doble factor se restableció. Inicie sesión para "
                    "registrar su nuevo autenticador."
                )
            }
        )


class LogoutView(_VistaPublicaAuth):
    """Cierre de sesión: revoca en el servidor la confianza del dispositivo
    y borra su cookie (política aprobada el 2026-11-18).

    Público a propósito: debe funcionar aunque el JWT ya haya caducado. Solo
    actúa sobre la cookie del propio navegador (SameSite=Strict). El JWT
    vigente no se invalida en el servidor (sin lista de revocación); caduca
    según `SIMPLE_JWT`.
    """

    @extend_schema(request=None, responses={200: MensajeSerializer}, auth=[])
    def post(self, request):
        mfa.cerrar_sesion(request, _cookie_confianza(request), None)
        respuesta = Response({"detail": "Sesión cerrada."})
        respuesta.delete_cookie(
            settings.MFA_TRUSTED_DEVICE_COOKIE_NAME,
            path="/api/v1/auth/",
            samesite="Strict",
        )
        return respuesta


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
