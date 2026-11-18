from django.conf import settings
from rest_framework import serializers

from apps.authentication.domain.correo_institucional import (
    MENSAJE_CORREO_INVALIDO,
    es_correo_institucional,
    normalizar_correo,
)
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer as BaseTokenObtainPairSerializer,
)


class TokenObtainPairSerializer(BaseTokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["cedula"] = user.cedula
        token["roles"] = user.get_roles()
        return token


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)


class PasswordResetLinkSerializer(serializers.Serializer):
    uid = serializers.CharField(max_length=128)
    token = serializers.CharField(max_length=128)


class PasswordResetConfirmSerializer(PasswordResetLinkSerializer):
    new_password = serializers.CharField(
        max_length=128, write_only=True, trim_whitespace=False
    )


class MensajeSerializer(serializers.Serializer):
    detail = serializers.CharField(read_only=True)


# --- Inicio de sesión en dos pasos (AUTH-B) ------------------------------


class CorreoInstitucionalField(serializers.CharField):
    """Correo `@<INSTITUTIONAL_EMAIL_DOMAIN>` normalizado (espacios y
    mayúsculas). Segunda barrera tras la validación del frontend."""

    default_error_messages = {
        "required": "El nombre de usuario es un campo requerido.",
        "blank": "El nombre de usuario es un campo requerido.",
        "invalid": MENSAJE_CORREO_INVALIDO,
    }

    def __init__(self, **kwargs):
        kwargs.setdefault("max_length", 254)
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        valor = normalizar_correo(super().to_internal_value(data))
        if not es_correo_institucional(valor, settings.INSTITUTIONAL_EMAIL_DOMAIN):
            self.fail("invalid")
        return valor


class LoginSerializer(serializers.Serializer):
    email = CorreoInstitucionalField()
    password = serializers.CharField(
        max_length=128,
        write_only=True,
        trim_whitespace=False,
        error_messages={
            "required": "La contraseña es un campo requerido.",
            "blank": "La contraseña es un campo requerido.",
        },
    )


class MfaResetRequestSerializer(LoginSerializer):
    """Solicitud de restablecimiento del 2FA (MFA-RST)."""

    cedula = serializers.CharField(
        max_length=20,
        error_messages={
            "required": "El número de cédula es un campo requerido.",
            "blank": "El número de cédula es un campo requerido.",
        },
    )


class MfaResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField(max_length=128)
    token = serializers.CharField(max_length=128)


class MfaChallengeSerializer(serializers.Serializer):
    challenge = serializers.CharField(max_length=128, write_only=True)


class MfaCodeSerializer(MfaChallengeSerializer):
    code = serializers.CharField(max_length=16, write_only=True)
    trust_device = serializers.BooleanField(default=False)


class MfaRecoverySerializer(MfaChallengeSerializer):
    recovery_code = serializers.CharField(max_length=32, write_only=True)


class AuthResultSerializer(serializers.Serializer):
    """Respuesta común del flujo. `access`/`refresh` solo con
    `status=authenticated`; `challenge` con `mfa_required` o
    `mfa_setup_required`; `recovery_codes` solo al completar el registro."""

    status = serializers.ChoiceField(
        choices=["authenticated", "mfa_required", "mfa_setup_required"],
        read_only=True,
    )
    access = serializers.CharField(read_only=True, required=False)
    refresh = serializers.CharField(read_only=True, required=False)
    challenge = serializers.CharField(read_only=True, required=False)
    expires_in = serializers.IntegerField(read_only=True, required=False)
    recovery_codes = serializers.ListField(
        child=serializers.CharField(), read_only=True, required=False
    )


class MfaSetupSerializer(serializers.Serializer):
    qr_svg = serializers.CharField(read_only=True)
    manual_key = serializers.CharField(read_only=True)
    issuer = serializers.CharField(read_only=True)
    account = serializers.CharField(read_only=True)
