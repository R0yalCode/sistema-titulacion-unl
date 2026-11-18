"""Pruebas de seguridad del segundo factor TOTP (AUTH-D).

Cubre el registro con Google Authenticator (QR), la verificación en cada
inicio de sesión, la ventana temporal, la reutilización de códigos, el
límite de intentos, el bloqueo por cuenta, el cifrado del secreto, los
códigos de recuperación y el restablecimiento por soporte.
"""

import logging
from datetime import timedelta

import jwt
import pyotp
import pytest
from cryptography.fernet import Fernet
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.authentication.adapters.models import (
    EventoAutenticacion,
    MfaChallenge,
    MfaDevice,
    MfaRecoveryCode,
    Role,
    TrustedDevice,
    User,
    UserRole,
)
from apps.authentication.services import identity_providers, mfa

PASSWORD = "pwd_mfa_authd_2026"
USERNAME = "authd_est"
EMAIL = "authd.est@unl.edu.ec"


@pytest.fixture(autouse=True)
def _limpiar_throttle():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture(name="usuario")
def fixture_usuario(db):
    user = User.objects.create_user(
        username=USERNAME, email=EMAIL, password=PASSWORD, cedula="7300000001"
    )
    role, _ = Role.objects.get_or_create(name="ESTUDIANTE")
    UserRole.objects.get_or_create(user=user, role=role)
    return user


def _login(cliente, password=PASSWORD):
    return cliente.post(
        reverse("auth-login"),
        {"email": EMAIL, "password": password},
        format="json",
    )


def _secreto(user) -> str:
    device = MfaDevice.objects.get(user=user)
    return mfa.descifrar_secreto(device.secret_encrypted)


def _codigo(user, desfase_pasos: int = 0) -> str:
    totp = pyotp.TOTP(_secreto(user))
    return totp.at(timezone.now().timestamp() + desfase_pasos * 30)


def _registrar(cliente, user, trust_device=False):
    reto = _login(cliente).json()["challenge"]
    cliente.post(reverse("auth-mfa-setup"), {"challenge": reto}, format="json")
    return cliente.post(
        reverse("auth-mfa-setup-confirm"),
        {"challenge": reto, "code": _codigo(user), "trust_device": trust_device},
        format="json",
    )


def _avanzar_paso(user):
    """Simula que el periodo usado quedó atrás (anti-reutilización)."""
    MfaDevice.objects.filter(user=user).update(last_used_step=None)


# --- Paso 1: credenciales -----------------------------------------------


def test_login_sin_mfa_exige_registro_y_no_entrega_jwt(usuario):
    respuesta = _login(APIClient())
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["status"] == "mfa_setup_required"
    assert "access" not in cuerpo and "refresh" not in cuerpo
    assert cuerpo["challenge"] and cuerpo["expires_in"] == 300
    # El reto se guarda solo como hash.
    assert not MfaChallenge.objects.filter(token_hash=cuerpo["challenge"]).exists()


def test_credenciales_invalidas_401_generico_y_auditado(usuario):
    respuesta = _login(APIClient(), password="incorrecta")
    assert respuesta.status_code == 401
    assert respuesta.json() == {
        "detail": "Usuario o contraseña incorrectos.",
        "code": "credenciales_invalidas",
    }
    assert EventoAutenticacion.objects.filter(
        tipo=EventoAutenticacion.Tipo.LOGIN_FALLIDO
    ).exists()


def test_usuario_inactivo_recibe_el_mismo_401(usuario):
    usuario.is_active = False
    usuario.save()
    respuesta = _login(APIClient())
    assert respuesta.status_code == 401
    assert respuesta.json()["code"] == "credenciales_invalidas"


def test_endpoint_token_sin_segundo_factor_ya_no_existe(usuario):
    respuesta = APIClient().post(
        "/api/v1/auth/token/",
        {"email": EMAIL, "password": PASSWORD},
        format="json",
    )
    assert respuesta.status_code == 404


# --- Registro TOTP ------------------------------------------------------


def test_registro_devuelve_qr_y_cifra_el_secreto(usuario):
    cliente = APIClient()
    reto = _login(cliente).json()["challenge"]
    respuesta = cliente.post(
        reverse("auth-mfa-setup"), {"challenge": reto}, format="json"
    )
    assert respuesta.status_code == 200
    assert respuesta["Cache-Control"] == "no-store"
    cuerpo = respuesta.json()
    assert cuerpo["qr_svg"].startswith("data:image/svg+xml")
    assert cuerpo["account"] == USERNAME
    device = MfaDevice.objects.get(user=usuario)
    secreto = mfa.descifrar_secreto(device.secret_encrypted)
    assert len(secreto) == 32  # 160 bits en base32
    assert secreto not in device.secret_encrypted
    assert cuerpo["manual_key"].replace(" ", "") == secreto
    assert device.confirmed_at is None  # aún no activo


def test_reiniciar_registro_genera_un_secreto_nuevo(usuario):
    cliente = APIClient()
    reto = _login(cliente).json()["challenge"]
    cliente.post(reverse("auth-mfa-setup"), {"challenge": reto}, format="json")
    primero = _secreto(usuario)
    cliente.post(reverse("auth-mfa-setup"), {"challenge": reto}, format="json")
    assert _secreto(usuario) != primero


def test_confirmacion_con_codigo_incorrecto_no_activa(usuario):
    cliente = APIClient()
    reto = _login(cliente).json()["challenge"]
    cliente.post(reverse("auth-mfa-setup"), {"challenge": reto}, format="json")
    respuesta = cliente.post(
        reverse("auth-mfa-setup-confirm"),
        {"challenge": reto, "code": "000000"},
        format="json",
    )
    assert respuesta.status_code == 400
    assert respuesta.json()["code"] == "codigo_mfa_invalido"
    assert MfaDevice.objects.get(user=usuario).confirmed_at is None


def test_confirmacion_correcta_activa_mfa_y_emite_jwt(usuario):
    respuesta = _registrar(APIClient(), usuario)
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["status"] == "authenticated"
    assert len(cuerpo["recovery_codes"]) == 10
    claims = jwt.decode(cuerpo["access"], options={"verify_signature": False})
    assert claims["roles"] == ["ESTUDIANTE"]
    assert claims["amr"] == ["pwd", "otp"]
    assert MfaDevice.objects.get(user=usuario).is_confirmed
    # Los códigos de recuperación se guardan con hash, nunca en claro.
    hashes = MfaRecoveryCode.objects.filter(user=usuario).values_list(
        "code_hash", flat=True
    )
    assert all(
        c.replace("-", "") not in h for c in cuerpo["recovery_codes"] for h in hashes
    )


def test_no_se_puede_reemplazar_un_autenticador_activo_con_reto_de_registro(usuario):
    cliente = APIClient()
    _registrar(cliente, usuario)
    MfaChallenge.objects.create(
        user=usuario,
        token_hash=mfa._hash_token("forzado"),
        purpose=MfaChallenge.Proposito.SETUP,
        expires_at=timezone.now() + timedelta(minutes=5),
    )
    respuesta = cliente.post(
        reverse("auth-mfa-setup"), {"challenge": "forzado"}, format="json"
    )
    assert respuesta.status_code == 400
    assert respuesta.json()["code"] == "estado_mfa_invalido"


# --- Verificación en inicios posteriores -------------------------------


def test_login_posterior_pide_totp_y_lo_valida(usuario):
    cliente = APIClient()
    _registrar(cliente, usuario)
    _avanzar_paso(usuario)
    paso1 = _login(cliente).json()
    assert paso1["status"] == "mfa_required"
    assert "access" not in paso1
    respuesta = cliente.post(
        reverse("auth-mfa-verify"),
        {"challenge": paso1["challenge"], "code": _codigo(usuario)},
        format="json",
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["status"] == "authenticated"


def test_codigo_reutilizado_es_rechazado(usuario):
    cliente = APIClient()
    _registrar(cliente, usuario)
    _avanzar_paso(usuario)
    codigo = _codigo(usuario)
    reto = _login(cliente).json()["challenge"]
    assert (
        cliente.post(
            reverse("auth-mfa-verify"),
            {"challenge": reto, "code": codigo},
            format="json",
        ).status_code
        == 200
    )
    reto2 = _login(cliente).json()["challenge"]
    respuesta = cliente.post(
        reverse("auth-mfa-verify"), {"challenge": reto2, "code": codigo}, format="json"
    )
    assert respuesta.status_code == 400
    assert respuesta.json()["code"] == "codigo_mfa_invalido"


@pytest.mark.parametrize("desfase,aceptado", [(-1, True), (1, True), (-3, False)])
def test_ventana_temporal_limitada(usuario, desfase, aceptado):
    _registrar(APIClient(), usuario)
    _avanzar_paso(usuario)
    device = MfaDevice.objects.get(user=usuario)
    assert mfa.verificar_totp(device, _codigo(usuario, desfase)) is aceptado


@pytest.mark.parametrize("codigo", ["", "12345", "1234567", "abcdef", "12 34 5x"])
def test_formatos_invalidos_rechazados(usuario, codigo):
    _registrar(APIClient(), usuario)
    device = MfaDevice.objects.get(user=usuario)
    assert mfa.verificar_totp(device, codigo) is False


def test_reto_se_invalida_tras_maximo_de_intentos(usuario):
    cliente = APIClient()
    _registrar(cliente, usuario)
    _avanzar_paso(usuario)
    reto = _login(cliente).json()["challenge"]
    for _ in range(5):
        cliente.post(
            reverse("auth-mfa-verify"),
            {"challenge": reto, "code": "000000"},
            format="json",
        )
    respuesta = cliente.post(
        reverse("auth-mfa-verify"),
        {"challenge": reto, "code": _codigo(usuario)},
        format="json",
    )
    assert respuesta.status_code == 400
    assert respuesta.json()["code"] == "reto_mfa_invalido"


def test_reto_caducado_es_rechazado(usuario):
    cliente = APIClient()
    _registrar(cliente, usuario)
    _avanzar_paso(usuario)
    reto = _login(cliente).json()["challenge"]
    MfaChallenge.objects.filter(user=usuario).update(expires_at=timezone.now())
    respuesta = cliente.post(
        reverse("auth-mfa-verify"),
        {"challenge": reto, "code": _codigo(usuario)},
        format="json",
    )
    assert respuesta.json()["code"] == "reto_mfa_invalido"


def test_reto_de_registro_no_sirve_para_verificar(usuario):
    cliente = APIClient()
    reto = _login(cliente).json()["challenge"]
    respuesta = cliente.post(
        reverse("auth-mfa-verify"), {"challenge": reto, "code": "123456"}, format="json"
    )
    assert respuesta.json()["code"] == "reto_mfa_invalido"


@override_settings(MFA_USER_MAX_FAILURES=3)
def test_bloqueo_por_cuenta_tras_fallos_acumulados(usuario):
    cliente = APIClient()
    _registrar(cliente, usuario)
    _avanzar_paso(usuario)
    reto = _login(cliente).json()["challenge"]
    for _ in range(3):
        cliente.post(
            reverse("auth-mfa-verify"),
            {"challenge": reto, "code": "000000"},
            format="json",
        )
    respuesta = cliente.post(
        reverse("auth-mfa-verify"),
        {"challenge": reto, "code": _codigo(usuario)},
        format="json",
    )
    assert respuesta.status_code == 429
    assert respuesta.json()["code"] == "mfa_bloqueado"


def test_secretos_y_codigos_no_aparecen_en_logs(usuario, caplog):
    caplog.set_level(logging.DEBUG)
    cliente = APIClient()
    reto = _login(cliente).json()["challenge"]
    cliente.post(reverse("auth-mfa-setup"), {"challenge": reto}, format="json")
    secreto = _secreto(usuario)
    codigo = _codigo(usuario)
    cliente.post(
        reverse("auth-mfa-setup-confirm"),
        {"challenge": reto, "code": codigo},
        format="json",
    )
    texto = caplog.text
    assert secreto not in texto and reto not in texto and PASSWORD not in texto
    eventos = EventoAutenticacion.objects.values_list("detalle", flat=True)
    assert all(secreto not in str(d) and codigo not in str(d) for d in eventos)


# --- Recuperación -------------------------------------------------------


def test_codigo_de_recuperacion_obliga_a_registrar_nuevo_autenticador(usuario):
    cliente = APIClient()
    codigos = _registrar(cliente, usuario, trust_device=True).json()["recovery_codes"]
    secreto_anterior = _secreto(usuario)
    cliente.cookies.clear()
    reto = _login(cliente).json()["challenge"]
    respuesta = cliente.post(
        reverse("auth-mfa-recovery"),
        {"challenge": reto, "recovery_code": codigos[0].lower()},
        format="json",
    )
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["status"] == "mfa_setup_required"
    assert "access" not in cuerpo
    assert not MfaDevice.objects.filter(user=usuario).exists()
    assert not TrustedDevice.objects.filter(
        user=usuario, revoked_at__isnull=True
    ).exists()
    cliente.post(
        reverse("auth-mfa-setup"), {"challenge": cuerpo["challenge"]}, format="json"
    )
    assert _secreto(usuario) != secreto_anterior


def test_codigo_de_recuperacion_es_de_un_solo_uso(usuario):
    cliente = APIClient()
    codigos = _registrar(cliente, usuario).json()["recovery_codes"]
    reto = _login(cliente).json()["challenge"]
    cliente.post(
        reverse("auth-mfa-recovery"),
        {"challenge": reto, "recovery_code": codigos[0]},
        format="json",
    )
    # Tras el restablecimiento, los códigos anteriores dejaron de existir.
    assert not mfa._consumir_codigo_recuperacion(usuario, codigos[1])
    assert not mfa._consumir_codigo_recuperacion(usuario, codigos[0])


def test_codigo_de_recuperacion_incorrecto_cuenta_como_fallo(usuario):
    cliente = APIClient()
    _registrar(cliente, usuario)
    reto = _login(cliente).json()["challenge"]
    respuesta = cliente.post(
        reverse("auth-mfa-recovery"),
        {"challenge": reto, "recovery_code": "AAAAA-BBBBB"},
        format="json",
    )
    assert respuesta.status_code == 400
    assert MfaDevice.objects.filter(user=usuario).exists()
    assert (
        MfaChallenge.objects.get(user=usuario, consumed_at__isnull=True).attempts == 1
    )


def test_restablecimiento_por_soporte_queda_auditado(usuario, admin_user):
    _registrar(APIClient(), usuario, trust_device=True)
    mfa.restablecer_mfa(usuario, actor=admin_user)
    assert not MfaDevice.objects.filter(user=usuario).exists()
    assert not MfaRecoveryCode.objects.filter(user=usuario).exists()
    evento = EventoAutenticacion.objects.get(
        tipo=EventoAutenticacion.Tipo.MFA_RESTABLECIDO
    )
    assert evento.detalle["actor"] == str(admin_user.pk)
    assert _login(APIClient()).json()["status"] == "mfa_setup_required"


# --- Cifrado y proveedor de identidad ----------------------------------


def test_rotacion_de_claves_recifra_los_secretos(usuario, settings):
    _registrar(APIClient(), usuario)
    secreto = _secreto(usuario)
    nueva = Fernet.generate_key().decode()
    settings.MFA_ENCRYPTION_KEYS = [nueva, *settings.MFA_ENCRYPTION_KEYS]
    call_command("rotate_mfa_keys")
    settings.MFA_ENCRYPTION_KEYS = [nueva]
    assert _secreto(usuario) == secreto


def test_sin_clave_de_cifrado_no_se_degrada_a_texto_plano(settings):
    settings.MFA_ENCRYPTION_KEYS = []
    with pytest.raises(ImproperlyConfigured):
        mfa.cifrar_secreto("JBSWY3DPEHPK3PXP")


def test_proveedor_desconocido_no_degrada_a_local(settings):
    settings.AUTH_IDENTITY_PROVIDER = "cas"
    with pytest.raises(ImproperlyConfigured):
        identity_providers.get_identity_provider()


def test_proveedor_con_mfa_propio_no_pide_totp_adicional(usuario, monkeypatch):
    class ProveedorConMfa:
        name = "prueba"
        provides_mfa = True

        def authenticate(self, request, email, password):
            return usuario

    monkeypatch.setattr(mfa, "get_identity_provider", lambda: ProveedorConMfa())
    cuerpo = _login(APIClient()).json()
    assert cuerpo["status"] == "authenticated"
    claims = jwt.decode(cuerpo["access"], options={"verify_signature": False})
    assert claims["amr"] == ["prueba", "mfa"]
