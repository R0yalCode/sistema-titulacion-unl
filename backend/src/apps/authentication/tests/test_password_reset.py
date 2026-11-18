"""Pruebas de recuperación de contraseña por correo (AUTH-RC)."""

import re
from datetime import timedelta
from unittest import mock

import pytest
from django.core import mail
from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.authentication.adapters.models import User
from apps.authentication.services import password_reset

PASSWORD = "clave_inicial_rc_2026"
NUEVA = "Titulacion-Nueva-2026"
EMAIL = "rc.estudiante@unl.edu.ec"
RESPUESTA_GENERICA = (
    "Si existe una cuenta asociada a ese correo, se enviarán "
    "las instrucciones para restablecer la contraseña."
)


@pytest.fixture(autouse=True)
def _limpiar_cache_throttle():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture(name="usuario")
def fixture_usuario(db):
    return User.objects.create_user(
        username="rc_estudiante", email=EMAIL, password=PASSWORD, cedula="7300000001"
    )


@pytest.fixture(name="client")
def fixture_client():
    return APIClient()


def _solicitar(client, email):
    return client.post(reverse("auth-password-reset"), {"email": email}, format="json")


def _enlace_del_correo():
    assert len(mail.outbox) == 1
    coincidencia = re.search(r"\?uid=([^&\s]+)&token=(\S+)", mail.outbox[0].body)
    assert coincidencia
    return coincidencia.group(1), coincidencia.group(2)


def _confirmar(client, uid, token, nueva=NUEVA):
    return client.post(
        reverse("auth-password-reset-confirm"),
        {"uid": uid, "token": token, "new_password": nueva},
        format="json",
    )


def _validar(client, uid, token):
    return client.post(
        reverse("auth-password-reset-validate"),
        {"uid": uid, "token": token},
        format="json",
    )


def _login(client, password):
    return client.post(
        reverse("auth-token"),
        {"username": "rc_estudiante", "password": password},
        format="json",
    )


# --- Solicitud -------------------------------------------------------------


@override_settings(FRONTEND_BASE_URL="https://sgt.example.test/")
def test_solicitud_con_correo_registrado_envia_enlace(client, usuario):
    respuesta = _solicitar(client, EMAIL.upper())

    assert respuesta.status_code == 200
    assert respuesta.json() == {"detail": RESPUESTA_GENERICA}
    assert mail.outbox[0].to == [EMAIL]
    assert "https://sgt.example.test/restablecer-contrasena?uid=" in mail.outbox[0].body


def test_solicitud_con_correo_desconocido_responde_igual_y_no_envia(client, usuario):
    respuesta = _solicitar(client, "nadie@unl.edu.ec")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"detail": RESPUESTA_GENERICA}
    assert mail.outbox == []


def test_solicitud_de_usuario_inactivo_no_envia(client, usuario):
    usuario.is_active = False
    usuario.save(update_fields=["is_active"])

    assert _solicitar(client, EMAIL).status_code == 200
    assert mail.outbox == []


def test_solicitud_sin_contrasena_utilizable_no_envia(client, usuario):
    usuario.set_unusable_password()
    usuario.save(update_fields=["password"])

    assert _solicitar(client, EMAIL).status_code == 200
    assert mail.outbox == []


def test_solicitud_con_correo_mal_formado_es_400(client, db):
    respuesta = _solicitar(client, "no-es-un-correo")

    assert respuesta.status_code == 400
    assert "email" in respuesta.json()


def test_fallo_de_envio_no_altera_la_respuesta(client, usuario):
    with mock.patch.object(password_reset, "send_mail", side_effect=OSError("smtp")):
        respuesta = _solicitar(client, EMAIL)

    assert respuesta.status_code == 200
    assert respuesta.json() == {"detail": RESPUESTA_GENERICA}


@override_settings(
    REST_FRAMEWORK={
        "DEFAULT_THROTTLE_RATES": {"password_reset": "3/hour", "auth": "5/minute"}
    }
)
def test_solicitud_limitada_por_ip(client, usuario):
    from rest_framework.settings import api_settings
    from rest_framework.throttling import SimpleRateThrottle

    with mock.patch.object(
        SimpleRateThrottle,
        "THROTTLE_RATES",
        api_settings.DEFAULT_THROTTLE_RATES,
    ):
        for _ in range(3):
            assert _solicitar(client, "nadie@unl.edu.ec").status_code == 200
        assert _solicitar(client, "nadie@unl.edu.ec").status_code == 429


# --- Validación y confirmación ---------------------------------------------


def test_flujo_completo_cambia_la_contrasena(client, usuario):
    _solicitar(client, EMAIL)
    uid, token = _enlace_del_correo()

    assert _validar(client, uid, token).status_code == 200
    respuesta = _confirmar(client, uid, token)

    assert respuesta.status_code == 200
    assert _login(client, NUEVA).status_code == 200
    assert _login(client, PASSWORD).status_code == 401


def test_enlace_es_de_un_solo_uso(client, usuario):
    _solicitar(client, EMAIL)
    uid, token = _enlace_del_correo()
    assert _confirmar(client, uid, token).status_code == 200

    assert _validar(client, uid, token).status_code == 400
    respuesta = _confirmar(client, uid, token, "Otra-Clave-Distinta-77")
    assert respuesta.status_code == 400
    assert respuesta.json()["code"] == "enlace_restablecimiento_invalido"


@pytest.mark.parametrize(
    "uid, token",
    [
        ("no-base64-valido", "abc-123"),
        ("MTIz", "token-inventado"),
        ("", ""),
    ],
)
def test_enlace_invalido_es_400(client, usuario, uid, token):
    respuesta = _validar(client, uid, token)

    assert respuesta.status_code == 400
    assert respuesta.json()["code"] == "enlace_restablecimiento_invalido"
    assert _confirmar(client, uid, token).status_code == 400


def test_token_manipulado_no_cambia_la_contrasena(client, usuario):
    _solicitar(client, EMAIL)
    uid, token = _enlace_del_correo()

    assert _confirmar(client, uid, token[:-1] + "x").status_code == 400
    assert _login(client, PASSWORD).status_code == 200


def test_enlace_vencido_es_400(client, usuario):
    _solicitar(client, EMAIL)
    uid, token = _enlace_del_correo()

    futuro = timezone.now() + timedelta(seconds=3601)
    with mock.patch(
        "django.contrib.auth.tokens.PasswordResetTokenGenerator._now",
        return_value=futuro.replace(tzinfo=None),
    ):
        assert _validar(client, uid, token).status_code == 400
        respuesta = _confirmar(client, uid, token)

    assert respuesta.status_code == 400
    assert respuesta.json()["code"] == "enlace_restablecimiento_invalido"
    assert _login(client, PASSWORD).status_code == 200


def test_enlace_de_usuario_desactivado_es_400(client, usuario):
    _solicitar(client, EMAIL)
    uid, token = _enlace_del_correo()
    usuario.is_active = False
    usuario.save(update_fields=["is_active"])

    assert _confirmar(client, uid, token).status_code == 400


@pytest.mark.parametrize(
    "debil", ["corta1", "12345678901", "password", "rc_estudiante"]
)
def test_contrasena_debil_es_rechazada_por_la_politica(client, usuario, debil):
    _solicitar(client, EMAIL)
    uid, token = _enlace_del_correo()

    respuesta = _confirmar(client, uid, token, debil)

    assert respuesta.status_code == 400
    assert respuesta.json()["new_password"]
    # El enlace sigue siendo utilizable tras un rechazo de política.
    assert _confirmar(client, uid, token).status_code == 200


def test_respuestas_no_exponen_la_contrasena(client, usuario):
    _solicitar(client, EMAIL)
    uid, token = _enlace_del_correo()

    respuesta = _confirmar(client, uid, token)

    assert NUEVA not in respuesta.content.decode()
    assert "new_password" not in respuesta.json()


def test_endpoints_no_requieren_autenticacion_ni_aceptan_get(client, db):
    for nombre in (
        "auth-password-reset",
        "auth-password-reset-validate",
        "auth-password-reset-confirm",
    ):
        assert client.get(reverse(nombre)).status_code == 405
