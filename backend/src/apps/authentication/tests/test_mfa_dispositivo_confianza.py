"""Pruebas de la política de confianza del dispositivo de 5 días (AUTH-D).

La confianza es una cookie HttpOnly con un token aleatorio; el servidor
guarda su hash, la expiración y la revocación. React no puede alterarla.
"""

from datetime import timedelta

import pyotp
import pytest
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APIClient

from apps.authentication.adapters.models import (
    EventoAutenticacion,
    MfaDevice,
    Role,
    TrustedDevice,
    User,
    UserRole,
)
from apps.authentication.services import mfa, password_reset

PASSWORD = "pwd_confianza_authd_2026"
USERNAME = "authd_conf"
COOKIE = "sgt_trusted_device"
UA = "Mozilla/5.0 (X11; Linux x86_64) Prueba/1.0"


@pytest.fixture(autouse=True)
def _limpiar_throttle():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture(name="usuario")
def fixture_usuario(db):
    user = User.objects.create_user(
        username=USERNAME,
        password=PASSWORD,
        cedula="7300000002",
        email="authd_conf@unl.edu.ec",
    )
    role, _ = Role.objects.get_or_create(name="ESTUDIANTE")
    UserRole.objects.get_or_create(user=user, role=role)
    return user


def _cliente(ua=UA):
    return APIClient(HTTP_USER_AGENT=ua)


def _login(cliente):
    return cliente.post(
        reverse("auth-login"),
        {"email": "authd_conf@unl.edu.ec", "password": PASSWORD},
        format="json",
    )


def _codigo(user):
    device = MfaDevice.objects.get(user=user)
    return pyotp.TOTP(mfa.descifrar_secreto(device.secret_encrypted)).now()


def _registrar_confiando(cliente, user):
    reto = _login(cliente).json()["challenge"]
    cliente.post(reverse("auth-mfa-setup"), {"challenge": reto}, format="json")
    return cliente.post(
        reverse("auth-mfa-setup-confirm"),
        {"challenge": reto, "code": _codigo(user), "trust_device": True},
        format="json",
    )


def test_cookie_de_confianza_httponly_strict_5_dias(usuario):
    respuesta = _registrar_confiando(_cliente(), usuario)
    cookie = respuesta.cookies[COOKIE]
    assert cookie["httponly"] is True
    assert cookie["samesite"] == "Strict"
    assert cookie["path"] == "/api/v1/auth/"
    assert int(cookie["max-age"]) == 5 * 24 * 3600
    dispositivo = TrustedDevice.objects.get(user=usuario)
    # Solo el hash vive en el servidor; la expiración la fija el servidor.
    assert dispositivo.token_hash != cookie.value
    assert dispositivo.token_hash == mfa._hash_token(cookie.value)
    dias = (dispositivo.expires_at - dispositivo.created_at).total_seconds() / 86400
    assert round(dias) == 5


def test_sin_marcar_confianza_no_se_crea_cookie(usuario):
    cliente = _cliente()
    reto = _login(cliente).json()["challenge"]
    cliente.post(reverse("auth-mfa-setup"), {"challenge": reto}, format="json")
    respuesta = cliente.post(
        reverse("auth-mfa-setup-confirm"),
        {"challenge": reto, "code": _codigo(usuario)},
        format="json",
    )
    assert COOKIE not in respuesta.cookies
    assert not TrustedDevice.objects.exists()


def test_dispositivo_de_confianza_vigente_omite_el_totp(usuario):
    cliente = _cliente()
    _registrar_confiando(cliente, usuario)
    cuerpo = _login(cliente).json()
    assert cuerpo["status"] == "authenticated"
    assert cuerpo["access"]
    assert EventoAutenticacion.objects.filter(
        tipo=EventoAutenticacion.Tipo.DISPOSITIVO_CONFIABLE_USADO
    ).exists()


def test_al_cumplirse_5_dias_se_pide_de_nuevo_el_totp(usuario):
    cliente = _cliente()
    _registrar_confiando(cliente, usuario)
    TrustedDevice.objects.filter(user=usuario).update(expires_at=timezone.now())
    assert _login(cliente).json()["status"] == "mfa_required"


def test_un_dia_antes_de_caducar_sigue_vigente(usuario):
    cliente = _cliente()
    _registrar_confiando(cliente, usuario)
    TrustedDevice.objects.filter(user=usuario).update(
        expires_at=timezone.now() + timedelta(days=1)
    )
    assert _login(cliente).json()["status"] == "authenticated"


def test_cookie_manipulada_no_concede_confianza(usuario):
    cliente = _cliente()
    _registrar_confiando(cliente, usuario)
    cliente.cookies[COOKIE] = "valor-inventado-por-el-navegador"
    assert _login(cliente).json()["status"] == "mfa_required"


def test_cookie_de_otro_usuario_no_sirve(usuario):
    cliente = _cliente()
    _registrar_confiando(cliente, usuario)
    otro = User.objects.create_user(
        username="authd_otro", email="authd.otro@unl.edu.ec", password=PASSWORD
    )
    MfaDevice.objects.create(
        user=otro,
        secret_encrypted=mfa.cifrar_secreto(pyotp.random_base32()),
        confirmed_at=timezone.now(),
    )
    respuesta = cliente.post(
        reverse("auth-login"),
        {"email": "authd.otro@unl.edu.ec", "password": PASSWORD},
        format="json",
    )
    assert respuesta.json()["status"] == "mfa_required"


def test_logout_revoca_la_confianza_y_borra_la_cookie(usuario):
    cliente = _cliente()
    _registrar_confiando(cliente, usuario)
    token = cliente.cookies[COOKIE].value
    respuesta = cliente.post(reverse("auth-logout"))
    assert respuesta.status_code == 200
    assert respuesta.cookies[COOKIE].value == ""
    assert TrustedDevice.objects.get(user=usuario).revoked_at is not None
    # Aunque el navegador reenviara el valor anterior, ya no vale.
    cliente.cookies[COOKIE] = token
    assert _login(cliente).json()["status"] == "mfa_required"


def test_logout_sin_cookie_es_inocuo(db):
    respuesta = APIClient().post(reverse("auth-logout"))
    assert respuesta.status_code == 200
    assert EventoAutenticacion.objects.filter(
        tipo=EventoAutenticacion.Tipo.LOGOUT
    ).exists()


def test_cambio_de_agente_de_usuario_es_evento_de_riesgo(usuario):
    cliente = _cliente()
    _registrar_confiando(cliente, usuario)
    cookie = cliente.cookies[COOKIE].value
    otro_navegador = _cliente(ua="curl/8.0")
    otro_navegador.cookies[COOKIE] = cookie
    assert _login(otro_navegador).json()["status"] == "mfa_required"
    assert TrustedDevice.objects.get(user=usuario).revoked_at is not None


def test_cambio_de_contrasena_revoca_todas_las_confianzas(usuario):
    cliente = _cliente()
    _registrar_confiando(cliente, usuario)
    uid = urlsafe_base64_encode(force_bytes(usuario.pk))
    token = default_token_generator.make_token(usuario)
    password_reset.confirmar_restablecimiento(uid, token, "NuevaClave-Segura-2026")
    assert TrustedDevice.objects.get(user=usuario).revoked_at is not None


def test_restablecer_mfa_revoca_la_confianza(usuario):
    cliente = _cliente()
    _registrar_confiando(cliente, usuario)
    mfa.restablecer_mfa(usuario)
    assert _login(cliente).json()["status"] == "mfa_setup_required"
