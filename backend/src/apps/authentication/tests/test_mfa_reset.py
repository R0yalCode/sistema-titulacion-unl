"""Restablecimiento del doble factor por enlace (MFA-RST)."""

import re

import pyotp
import pytest
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.core.cache import cache
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APIClient

from apps.authentication.adapters.models import (
    EventoAutenticacion,
    MfaDevice,
    MfaRecoveryCode,
    TrustedDevice,
    User,
)
from apps.authentication.services import mfa, password_reset

PASSWORD = "pwd_mfa_reset_2026"
EMAIL = "rst.estudiante@unl.edu.ec"
CEDULA = "7500000001"
RESPUESTA = (
    "Si los datos corresponden a una cuenta con doble factor activo, "
    "enviaremos un enlace de vigencia limitada al correo registrado."
)


@pytest.fixture(autouse=True)
def _limpiar_throttle():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture(name="usuario")
def fixture_usuario(db):
    return User.objects.create_user(
        username="rst_est", email=EMAIL, password=PASSWORD, cedula=CEDULA
    )


@pytest.fixture(name="con_2fa")
def fixture_con_2fa(usuario):
    cliente = APIClient(HTTP_USER_AGENT="Prueba/1.0")
    reto = cliente.post(
        reverse("auth-login"), {"email": EMAIL, "password": PASSWORD}, format="json"
    ).json()["challenge"]
    cliente.post(reverse("auth-mfa-setup"), {"challenge": reto}, format="json")
    device = MfaDevice.objects.get(user=usuario)
    codigo = pyotp.TOTP(mfa.descifrar_secreto(device.secret_encrypted)).now()
    cliente.post(
        reverse("auth-mfa-setup-confirm"),
        {"challenge": reto, "code": codigo, "trust_device": True},
        format="json",
    )
    assert MfaDevice.objects.get(user=usuario).is_confirmed
    return usuario


def _solicitar(email=EMAIL, cedula=CEDULA, password=PASSWORD):
    return APIClient().post(
        reverse("auth-mfa-reset"),
        {"email": email, "cedula": cedula, "password": password},
        format="json",
    )


def _enlace():
    assert len(mail.outbox) == 1
    uid, token = re.search(
        r"uid=([^&\s]+)&token=([^\s]+)", mail.outbox[0].body
    ).groups()
    return uid, token


def _confirmar(uid, token):
    return APIClient().post(
        reverse("auth-mfa-reset-confirm"), {"uid": uid, "token": token}, format="json"
    )


def test_solicitud_valida_envia_enlace_y_no_retira_el_2fa(con_2fa):
    respuesta = _solicitar()
    assert respuesta.status_code == 200
    assert respuesta.json()["detail"] == RESPUESTA
    assert mail.outbox[0].to == [EMAIL]
    assert "/restablecer-2fa/confirmar?uid=" in mail.outbox[0].body
    # Conocer correo, cédula y contraseña no basta: el 2FA sigue activo.
    assert MfaDevice.objects.get(user=con_2fa).is_confirmed


@pytest.mark.parametrize(
    "datos",
    [
        {"password": "incorrecta"},
        {"cedula": "7599999999"},
        {"email": "otra.persona@unl.edu.ec"},
    ],
)
def test_datos_incorrectos_responden_igual_sin_enviar(con_2fa, datos):
    respuesta = _solicitar(**datos)
    assert respuesta.status_code == 200
    assert respuesta.json()["detail"] == RESPUESTA
    assert mail.outbox == []
    assert EventoAutenticacion.objects.filter(
        tipo=EventoAutenticacion.Tipo.MFA_RESTABLECIMIENTO_RECHAZADO
    ).exists()


def test_cuenta_sin_2fa_responde_igual_sin_enviar(usuario):
    assert _solicitar().json()["detail"] == RESPUESTA
    assert mail.outbox == []


def test_dominio_no_institucional_rechazado(con_2fa):
    respuesta = _solicitar(email="rst.estudiante@gmail.com")
    assert respuesta.status_code == 400
    assert mail.outbox == []


def test_confirmar_enlace_restablece_el_2fa_y_obliga_a_registrar(con_2fa):
    _solicitar()
    uid, token = _enlace()
    respuesta = _confirmar(uid, token)
    assert respuesta.status_code == 200
    assert not MfaDevice.objects.filter(user=con_2fa).exists()
    assert not MfaRecoveryCode.objects.filter(user=con_2fa).exists()
    assert not TrustedDevice.objects.filter(
        user=con_2fa, revoked_at__isnull=True
    ).exists()
    login = APIClient().post(
        reverse("auth-login"), {"email": EMAIL, "password": PASSWORD}, format="json"
    )
    assert login.json()["status"] == "mfa_setup_required"


def test_enlace_de_un_solo_uso(con_2fa):
    _solicitar()
    uid, token = _enlace()
    assert _confirmar(uid, token).status_code == 200
    segunda = _confirmar(uid, token)
    assert segunda.status_code == 400
    assert segunda.json()["code"] == "enlace_mfa_invalido"


def test_enlace_alterado_o_de_contrasena_no_sirve(con_2fa):
    _solicitar()
    uid, token = _enlace()
    assert _confirmar(uid, token + "x").status_code == 400
    # Un token de restablecimiento de contraseña no es intercambiable.
    token_pwd = default_token_generator.make_token(con_2fa)
    assert _confirmar(uid, token_pwd).status_code == 400
    assert MfaDevice.objects.filter(user=con_2fa).exists()


def test_cambio_de_contrasena_invalida_el_enlace(con_2fa):
    _solicitar()
    uid, token = _enlace()
    con_2fa.set_password("Otra-Clave-Segura-2026")
    con_2fa.save()
    assert _confirmar(uid, token).status_code == 400


def test_espera_tras_restablecer_contrasena(con_2fa):
    nueva = "Nueva-Clave-Segura-2026"
    uid = urlsafe_base64_encode(force_bytes(con_2fa.pk))
    password_reset.confirmar_restablecimiento(
        uid, default_token_generator.make_token(con_2fa), nueva
    )
    respuesta = _solicitar(password=nueva)
    assert respuesta.json()["detail"] == RESPUESTA
    assert mail.outbox == []
    evento = EventoAutenticacion.objects.filter(
        tipo=EventoAutenticacion.Tipo.MFA_RESTABLECIMIENTO_RECHAZADO
    ).first()
    assert evento.detalle["motivo"] == "espera_tras_cambio_de_contrasena"


def test_auditoria_sin_datos_sensibles(con_2fa):
    _solicitar()
    uid, token = _enlace()
    _confirmar(uid, token)
    texto = str(list(EventoAutenticacion.objects.values_list("detalle", flat=True)))
    for sensible in (PASSWORD, CEDULA, EMAIL, token):
        assert sensible not in texto
    assert EventoAutenticacion.objects.filter(
        tipo=EventoAutenticacion.Tipo.MFA_RESTABLECIDO, user=con_2fa
    ).exists()


def test_solicitudes_repetidas_limitadas(con_2fa, settings):
    # Throttle "password_reset" por IP (10/h por defecto).
    codigos = [_solicitar(password="x").status_code for _ in range(11)]
    assert codigos[:10] == [200] * 10
    assert codigos[10] == 429
