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
