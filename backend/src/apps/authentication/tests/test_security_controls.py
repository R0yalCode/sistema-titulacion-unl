"""Pruebas de SEC-T004 (separacion JWT_SIGNING_KEY/SECRET_KEY), SEC-T006
(access token de 30 minutos) y SEC-T002 (throttling de login)."""

import datetime

import jwt
import pytest
from django.core.cache import cache
from django.conf import settings
from django.core.signing import Signer
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework_simplejwt.tokens import AccessToken

from apps.authentication.adapters.models import Role, User, UserRole
from apps.authentication.tests.test_jwt import VistaProtegidaSandbox

PASSWORD = "pwd_seguro_sec_t004"


@pytest.fixture(name="estudiante")
def fixture_estudiante(db):
    user = User.objects.create_user(
        username="sec_t004_est", password=PASSWORD, cedula="7200000099"
    )
    role, _ = Role.objects.get_or_create(name="ESTUDIANTE")
    UserRole.objects.get_or_create(user=user, role=role)
    return user


def test_jwt_signing_key_separate_from_secret_key():
    assert settings.SIMPLE_JWT["SIGNING_KEY"] == settings.JWT_SIGNING_KEY
    assert settings.SIMPLE_JWT["SIGNING_KEY"] != settings.SECRET_KEY


def test_jwt_token_verification_uses_jwt_signing_key(estudiante):
    token_valido = AccessToken.for_user(estudiante)
    factory = APIRequestFactory()

    request_valido = factory.get("/", HTTP_AUTHORIZATION=f"Bearer {token_valido}")
    assert VistaProtegidaSandbox.as_view()(request_valido).status_code == 200

    payload = jwt.decode(str(token_valido), options={"verify_signature": False})
    token_firmado_con_secret_key = jwt.encode(
        payload, settings.SECRET_KEY, algorithm=settings.SIMPLE_JWT["ALGORITHM"]
    )
    request_invalido = factory.get(
        "/", HTTP_AUTHORIZATION=f"Bearer {token_firmado_con_secret_key}"
    )
    assert VistaProtegidaSandbox.as_view()(request_invalido).status_code == 401


def test_django_sessions_use_secret_key():
    firmante = Signer()
    valor_firmado = firmante.sign("sec-t004-sesion-ok")

    assert firmante.key == settings.SECRET_KEY
    assert firmante.key != settings.JWT_SIGNING_KEY
    assert firmante.unsign(valor_firmado) == "sec-t004-sesion-ok"


def test_access_token_lifetime_30_minutes(estudiante):
    token = AccessToken.for_user(estudiante)
    vigencia = token["exp"] - token["iat"]
    assert vigencia == 1800
    assert settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"] == datetime.timedelta(minutes=30)


def test_access_token_expired_after_31_minutes_rejected(estudiante):
    token = AccessToken.for_user(estudiante)
    token.set_exp(
        from_time=datetime.datetime.now(datetime.timezone.utc)
        - datetime.timedelta(minutes=31),
        lifetime=datetime.timedelta(minutes=30),
    )
    request = APIRequestFactory().get("/", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert VistaProtegidaSandbox.as_view()(request).status_code == 401


# --- SEC-T002: throttling de login (DEC-002: 5/min/IP) ---------------------


@pytest.fixture(autouse=True, name="_limpiar_cache_throttle_login")
def fixture_limpiar_cache_throttle_login():
    cache.clear()
    yield
    cache.clear()


def _login(client, **extra):
    return client.post(
        reverse("auth-token"),
        {"username": "sec_t004_est", "password": PASSWORD},
        format="json",
        **extra,
    )


def test_login_throttle_allows_5_requests_per_minute(estudiante):
    client = APIClient()
    for _ in range(5):
        assert _login(client).status_code == 200


def test_login_throttle_6th_request_returns_429(estudiante):
    client = APIClient()
    for _ in range(5):
        assert _login(client).status_code == 200
    assert _login(client).status_code == 429


def test_login_throttle_resets_after_window(estudiante):
    client = APIClient()
    for _ in range(5):
        assert _login(client).status_code == 200
    assert _login(client).status_code == 429

    cache.clear()  # equivalente a que la ventana de 1 minuto haya expirado

    assert _login(client).status_code == 200


def test_login_throttle_per_ip_isolation(estudiante):
    client_a = APIClient()
    client_b = APIClient()
    for _ in range(5):
        assert _login(client_a, REMOTE_ADDR="203.0.113.10").status_code == 200
    assert _login(client_a, REMOTE_ADDR="203.0.113.10").status_code == 429

    # IP B, sin relación, conserva su propio límite completo
    assert _login(client_b, REMOTE_ADDR="203.0.113.20").status_code == 200


@override_settings(TRUSTED_PROXIES=["127.0.0.0/8"])
def test_login_throttle_respects_trusted_proxies(estudiante):
    """Con REMOTE_ADDR (del test client) en TRUSTED_PROXIES, dos IPs
    distintas detrás de X-Forwarded-For deben tener límites independientes;
    sin eso (ver test_login_throttle_per_ip_isolation con REMOTE_ADDR
    directo) el throttle ya aísla por REMOTE_ADDR igual."""
    client = APIClient()
    for _ in range(5):
        assert (
            _login(client, HTTP_X_FORWARDED_FOR="203.0.113.30").status_code == 200
        )
    agotada = _login(client, HTTP_X_FORWARDED_FOR="203.0.113.30")
    assert agotada.status_code == 429

    # IP distinta tras el mismo proxy confiable: límite propio, no agotado
    otra = _login(client, HTTP_X_FORWARDED_FOR="203.0.113.31")
    assert otra.status_code == 200
