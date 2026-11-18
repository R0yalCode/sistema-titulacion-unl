from rest_framework import serializers
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


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(
        max_length=128, write_only=True, trim_whitespace=False
    )


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
