"""Pruebas de autenticacion JWT (T012; RNF-001).

Cubre: obtencion de token, credenciales invalidas, expiracion, renovacion
y rechazo 401 de token valido con expiracion pasada.
"""

import datetime

import jwt
import pyotp
import pytest
from django.urls import reverse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from apps.authentication.adapters.models import MfaDevice, Role, User, UserRole
from apps.authentication.services.mfa import descifrar_secreto

PASSWORD = "pwd_seguro_t012"


@pytest.fixture(name="estudiante")
def fixture_estudiante(db):
    user = User.objects.create_user(
        username="t012_est",
        email="t012.est@unl.edu.ec",
        password=PASSWORD,
        cedula="7200000001",
    )
    role, _ = Role.objects.get_or_create(name="ESTUDIANTE")
    UserRole.objects.get_or_create(user=user, role=role)
    return user


class VistaProtegidaSandbox(APIView):
    """Vista sandbox para probar el flujo JWT sin tocar el arbol de src."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response({"acceso": True})


def _tokens_con_mfa(cliente: APIClient) -> dict:
    """Flujo completo: contraseña, registro TOTP y primer código (AUTH-B).

    Desde AUTH-B el JWT solo se emite tras el segundo factor; antes lo
    entregaba `POST /api/v1/auth/token/` solo con contraseña.
    """
    paso1 = cliente.post(
        reverse("auth-login"),
        data={"email": "t012.est@unl.edu.ec", "password": PASSWORD},
        format="json",
    ).json()
    assert paso1["status"] == "mfa_setup_required"
    cliente.post(
        reverse("auth-mfa-setup"), {"challenge": paso1["challenge"]}, format="json"
    )
    device = MfaDevice.objects.get(user__username="t012_est")
    codigo = pyotp.TOTP(descifrar_secreto(device.secret_encrypted)).now()
    respuesta = cliente.post(
        reverse("auth-mfa-setup-confirm"),
        {"challenge": paso1["challenge"], "code": codigo},
        format="json",
    )
    assert respuesta.status_code == 200
    return respuesta.json()


def test_obtener_token_credenciales_validas(client, estudiante):
    cuerpo = _tokens_con_mfa(APIClient())
    assert cuerpo["status"] == "authenticated"
    claims = jwt.decode(cuerpo["access"], options={"verify_signature": False})
    assert claims["cedula"] == "7200000001"
    assert claims["roles"] == ["ESTUDIANTE"]
    assert "user_id" in claims and "exp" in claims and "jti" in claims


def test_obtener_token_credenciales_invalidas(client, estudiante):
    respuesta = client.post(
        reverse("auth-login"),
        data={"email": "t012.est@unl.edu.ec", "password": "incorrecta"},
        content_type="application/json",
    )
    assert respuesta.status_code == 401


def test_refresh_tokens_no_renovacion_por_defecto(client, estudiante):
    par = _tokens_con_mfa(APIClient())
    serializador = TokenRefreshSerializer(data={"refresh": par["refresh"]})
    assert serializador.is_valid()
    nuevo = serializador.validated_data
    assert nuevo["access"] != par["access"]
    assert "refresh" not in nuevo
    assert "access" in nuevo


def test_access_token_expirado_rechazado_401(estudiante):
    def responder_con_token(expirado):
        from rest_framework_simplejwt.tokens import AccessToken

        token = AccessToken.for_user(estudiante)
        token["cedula"] = estudiante.cedula
        token["roles"] = estudiante.get_roles()
        if expirado:
            token.set_exp(
                from_time=datetime.datetime.now(datetime.timezone.utc)
                - datetime.timedelta(seconds=3),
                lifetime=datetime.timedelta(seconds=1),
            )
        else:
            token.set_exp(lifetime=datetime.timedelta(minutes=5))
        factory = APIRequestFactory()
        request = factory.get("/", HTTP_AUTHORIZATION=f"Bearer {token}")
        return VistaProtegidaSandbox.as_view()(request)

    assert responder_con_token(expirado=True).status_code == 401
    assert responder_con_token(expirado=False).status_code == 200


def test_peticion_sin_token_devuelve_401(db):
    factory = APIRequestFactory()
    request = factory.get("/")
    respuesta = VistaProtegidaSandbox.as_view()(request)
    assert respuesta.status_code == 401


def test_token_firma_invalida_rechazado(estudiante):
    factory = APIRequestFactory()
    request = factory.get("/", HTTP_AUTHORIZATION="Bearer no-es-una-firma-valida.xyz")
    vista = VistaProtegidaSandbox.as_view()(request)
    assert vista.status_code == 401


def test_authentication_failed_rechaza_token_expirado(estudiante):
    from rest_framework_simplejwt.tokens import AccessToken

    token = AccessToken.for_user(estudiante)
    token.set_exp(lifetime=datetime.timedelta(seconds=-5))
    factory = APIRequestFactory()
    request = factory.get("/", HTTP_AUTHORIZATION=f"Bearer {token}")
    with pytest.raises(AuthenticationFailed):
        JWTAuthentication().authenticate(request)
