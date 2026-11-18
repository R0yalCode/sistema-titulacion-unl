"""Segundo factor TOTP, confianza del dispositivo y flujo de inicio de sesión.

Responsabilidades separadas (docs/autenticacion/flujo-autenticacion.md):

1. Identidad: `identity_providers.get_identity_provider()` (hoy, local).
2. Segundo factor: TOTP RFC 6238 (Google Authenticator) validado aquí con
   `pyotp`; el secreto se cifra en reposo con MultiFernet.
3. Confianza del dispositivo: cookie HttpOnly con token aleatorio; el
   servidor guarda su hash, su expiración (5 días) y su revocación.
4. Sesión: JWT emitido solo después de completar los pasos anteriores.
5. Autorización: roles del usuario (claim `roles`) y RBAC en cada endpoint.

Nunca se registran en logs secretos, URI otpauth, códigos ni tokens.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import secrets
import time
from dataclasses import dataclass, field
from datetime import timedelta

import pyotp
import segno
from cryptography.fernet import Fernet, InvalidToken, MultiFernet
from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from apps.authentication.adapters.models import (
    EventoAutenticacion,
    MfaChallenge,
    MfaDevice,
    MfaRecoveryCode,
    TrustedDevice,
    User,
)
from apps.authentication.services.identity_providers import get_identity_provider
from core.adapters.client_ip import resolver_ip_cliente

logger = logging.getLogger(__name__)

TOTP_DIGITS = 6
TOTP_INTERVAL = 30
_RECOVERY_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # sin 0/O ni 1/I


# --- Errores de dominio --------------------------------------------------


class ErrorMfa(Exception):
    """Base de los errores del flujo de autenticación."""


class CredencialesInvalidas(ErrorMfa):
    """Usuario o contraseña incorrectos (sin distinguir cuál)."""


class RetoInvalido(ErrorMfa):
    """Reto inexistente, caducado, consumido o agotado."""


class CodigoInvalido(ErrorMfa):
    """Código TOTP o de recuperación incorrecto."""


class MfaBloqueado(ErrorMfa):
    """Demasiados fallos de segundo factor recientes para la cuenta."""


class EstadoMfaInvalido(ErrorMfa):
    """La operación no corresponde al estado del autenticador."""


# --- Utilidades ----------------------------------------------------------


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _user_agent(request) -> str:
    if request is None:
        return ""
    return (request.META.get("HTTP_USER_AGENT") or "")[:255]


def registrar_evento(tipo: str, request=None, user=None, **detalle) -> None:
    """Auditoría de autenticación. `detalle` nunca debe contener secretos."""
    EventoAutenticacion.objects.create(
        tipo=tipo,
        user=user,
        ip=resolver_ip_cliente(request),
        user_agent=_user_agent(request),
        detalle=detalle,
    )


# --- Cifrado del secreto -------------------------------------------------


def _fernet() -> MultiFernet:
    claves = [c for c in getattr(settings, "MFA_ENCRYPTION_KEYS", []) if c]
    if not claves:
        raise ImproperlyConfigured(
            "MFA_ENCRYPTION_KEYS no está configurada: no se pueden proteger "
            "los secretos TOTP."
        )
    try:
        return MultiFernet([Fernet(c.encode()) for c in claves])
    except (ValueError, TypeError) as error:
        raise ImproperlyConfigured(
            "MFA_ENCRYPTION_KEYS contiene una clave Fernet inválida."
        ) from error


def cifrar_secreto(secreto: str) -> str:
    return _fernet().encrypt(secreto.encode()).decode()


def descifrar_secreto(cifrado: str) -> str:
    try:
        return _fernet().decrypt(cifrado.encode()).decode()
    except InvalidToken as error:
        # Clave retirada o dato corrupto: no se degrada a texto plano.
        raise ImproperlyConfigured(
            "No se pudo descifrar un secreto TOTP con MFA_ENCRYPTION_KEYS."
        ) from error


def rotar_cifrado_secretos() -> int:
    """Recifra todos los secretos con la clave primaria (la primera)."""
    fernet = _fernet()
    total = 0
    for device in MfaDevice.objects.select_for_update().iterator():
        device.secret_encrypted = fernet.rotate(
            device.secret_encrypted.encode()
        ).decode()
        device.save(update_fields=["secret_encrypted"])
        total += 1
    return total


# --- TOTP ----------------------------------------------------------------


def _totp(secreto: str) -> pyotp.TOTP:
    return pyotp.TOTP(secreto, digits=TOTP_DIGITS, interval=TOTP_INTERVAL)


def _normalizar_codigo(codigo: str) -> str:
    return "".join(ch for ch in (codigo or "") if not ch.isspace())


def verificar_totp(device: MfaDevice, codigo: str, ahora: float | None = None) -> bool:
    """Valida el código con tolerancia ±MFA_TOTP_VALID_WINDOW periodos.

    Rechaza códigos de periodos ya usados (anti-reutilización) y fuera de
    la ventana. Si acepta, persiste el periodo usado.
    """
    codigo = _normalizar_codigo(codigo)
    if len(codigo) != TOTP_DIGITS or not codigo.isdigit():
        return False
    secreto = descifrar_secreto(device.secret_encrypted)
    totp = _totp(secreto)
    instante = time.time() if ahora is None else ahora
    paso_actual = int(instante // TOTP_INTERVAL)
    ventana = max(0, int(getattr(settings, "MFA_TOTP_VALID_WINDOW", 1)))

    aceptado = None
    for desfase in range(-ventana, ventana + 1):
        paso = paso_actual + desfase
        if hmac.compare_digest(totp.generate_otp(paso), codigo):
            aceptado = paso
            break
    if aceptado is None:
        return False
    if device.last_used_step is not None and aceptado <= device.last_used_step:
        return False

    # Actualización condicional: dos peticiones concurrentes con el mismo
    # código no pueden aceptarse ambas.
    filtro = MfaDevice.objects.filter(pk=device.pk)
    if device.last_used_step is None:
        filtro = filtro.filter(last_used_step__isnull=True)
    else:
        filtro = filtro.filter(last_used_step=device.last_used_step)
    if filtro.update(last_used_step=aceptado) != 1:
        return False
    device.last_used_step = aceptado
    return True


def uri_aprovisionamiento(user: User, secreto: str) -> str:
    return _totp(secreto).provisioning_uri(
        name=user.get_username(), issuer_name=settings.MFA_ISSUER_NAME
    )


def qr_svg_data_uri(uri: str) -> str:
    """QR del URI otpauth como `data:image/svg+xml` (no se persiste)."""
    return segno.make(uri, error="m").svg_data_uri(scale=6, border=2)


def _formatear_clave_manual(secreto: str) -> str:
    return " ".join(secreto[i : i + 4] for i in range(0, len(secreto), 4))


# --- Retos ---------------------------------------------------------------


def crear_reto(user: User, proposito: str) -> tuple[str, MfaChallenge]:
    """Invalida retos previos del usuario y emite uno nuevo."""
    ahora = timezone.now()
    MfaChallenge.objects.filter(user=user, consumed_at__isnull=True).update(
        consumed_at=ahora
    )
    token = secrets.token_urlsafe(32)
    reto = MfaChallenge.objects.create(
        user=user,
        token_hash=_hash_token(token),
        purpose=proposito,
        expires_at=ahora + timedelta(seconds=settings.MFA_CHALLENGE_TTL_SECONDS),
    )
    return token, reto


def obtener_reto(token: str, proposito: str) -> MfaChallenge:
    if not token:
        raise RetoInvalido()
    reto = (
        MfaChallenge.objects.select_related("user")
        .filter(token_hash=_hash_token(token), purpose=proposito)
        .first()
    )
    if (
        reto is None
        or reto.consumed_at is not None
        or reto.expires_at <= timezone.now()
        or reto.attempts >= settings.MFA_CHALLENGE_MAX_ATTEMPTS
        or not reto.user.is_active
    ):
        raise RetoInvalido()
    return reto


def _consumir_reto(reto: MfaChallenge) -> None:
    actualizado = MfaChallenge.objects.filter(
        pk=reto.pk, consumed_at__isnull=True
    ).update(consumed_at=timezone.now())
    if actualizado != 1:
        raise RetoInvalido()


def _registrar_fallo(reto: MfaChallenge, request, motivo: str) -> None:
    MfaChallenge.objects.filter(pk=reto.pk).update(attempts=F("attempts") + 1)
    reto.refresh_from_db(fields=["attempts"])
    registrar_evento(
        EventoAutenticacion.Tipo.MFA_VERIFICACION_FALLIDA,
        request,
        reto.user,
        motivo=motivo,
        intento=reto.attempts,
    )
    if reto.attempts >= settings.MFA_CHALLENGE_MAX_ATTEMPTS:
        _consumir_reto_silencioso(reto)


def _consumir_reto_silencioso(reto: MfaChallenge) -> None:
    MfaChallenge.objects.filter(pk=reto.pk, consumed_at__isnull=True).update(
        consumed_at=timezone.now()
    )


def _comprobar_bloqueo(user: User, request) -> None:
    desde = timezone.now() - timedelta(minutes=settings.MFA_USER_LOCKOUT_MINUTES)
    fallos = EventoAutenticacion.objects.filter(
        user=user,
        tipo=EventoAutenticacion.Tipo.MFA_VERIFICACION_FALLIDA,
        created_at__gte=desde,
    ).count()
    if fallos >= settings.MFA_USER_MAX_FAILURES:
        registrar_evento(EventoAutenticacion.Tipo.MFA_BLOQUEO, request, user)
        raise MfaBloqueado()


# --- Confianza del dispositivo ------------------------------------------


def crear_confianza(user: User, request) -> tuple[str, TrustedDevice]:
    token = secrets.token_urlsafe(32)
    dispositivo = TrustedDevice.objects.create(
        user=user,
        token_hash=_hash_token(token),
        user_agent=_user_agent(request),
        ip=resolver_ip_cliente(request),
        expires_at=timezone.now() + timedelta(days=settings.MFA_TRUSTED_DEVICE_DAYS),
    )
    registrar_evento(
        EventoAutenticacion.Tipo.DISPOSITIVO_CONFIABLE_CREADO,
        request,
        user,
        dias=settings.MFA_TRUSTED_DEVICE_DAYS,
    )
    return token, dispositivo


def confianza_vigente(user: User, token: str | None, request) -> bool:
    """True si el token de la cookie corresponde a una confianza vigente.

    Un cambio de agente de usuario se trata como evento de riesgo: se
    revoca esa confianza y se exige de nuevo el segundo factor.
    """
    if not token:
        return False
    ahora = timezone.now()
    dispositivo = TrustedDevice.objects.filter(
        token_hash=_hash_token(token), user=user, revoked_at__isnull=True
    ).first()
    if dispositivo is None or dispositivo.expires_at <= ahora:
        return False
    if dispositivo.user_agent and dispositivo.user_agent != _user_agent(request):
        _revocar(dispositivo, request, motivo="riesgo_agente_usuario")
        return False
    dispositivo.last_used_at = ahora
    dispositivo.save(update_fields=["last_used_at"])
    return True


def _revocar(dispositivo: TrustedDevice, request, motivo: str) -> None:
    TrustedDevice.objects.filter(pk=dispositivo.pk, revoked_at__isnull=True).update(
        revoked_at=timezone.now()
    )
    registrar_evento(
        EventoAutenticacion.Tipo.DISPOSITIVO_CONFIABLE_REVOCADO,
        request,
        dispositivo.user,
        motivo=motivo,
    )


def revocar_confianza_por_token(token: str | None, request) -> bool:
    if not token:
        return False
    dispositivo = (
        TrustedDevice.objects.select_related("user")
        .filter(token_hash=_hash_token(token), revoked_at__isnull=True)
        .first()
    )
    if dispositivo is None:
        return False
    _revocar(dispositivo, request, motivo="logout")
    return True


def revocar_todas_las_confianzas(user: User, request=None, motivo: str = "") -> int:
    total = TrustedDevice.objects.filter(user=user, revoked_at__isnull=True).update(
        revoked_at=timezone.now()
    )
    if total:
        registrar_evento(
            EventoAutenticacion.Tipo.DISPOSITIVO_CONFIABLE_REVOCADO,
            request,
            user,
            motivo=motivo,
            total=total,
        )
    return total


# --- Códigos de recuperación --------------------------------------------


def _generar_codigo_recuperacion() -> str:
    crudo = "".join(secrets.choice(_RECOVERY_ALPHABET) for _ in range(10))
    return f"{crudo[:5]}-{crudo[5:]}"


def _normalizar_recuperacion(codigo: str) -> str:
    return "".join(ch for ch in (codigo or "").upper() if ch.isalnum())


def generar_codigos_recuperacion(user: User) -> list[str]:
    """Sustituye los códigos del usuario. Solo se muestran una vez."""
    MfaRecoveryCode.objects.filter(user=user).delete()
    codigos = [
        _generar_codigo_recuperacion() for _ in range(settings.MFA_RECOVERY_CODES_COUNT)
    ]
    MfaRecoveryCode.objects.bulk_create(
        MfaRecoveryCode(user=user, code_hash=make_password(_normalizar_recuperacion(c)))
        for c in codigos
    )
    return codigos


def _consumir_codigo_recuperacion(user: User, codigo: str) -> bool:
    normalizado = _normalizar_recuperacion(codigo)
    if len(normalizado) != 10:
        return False
    for registro in MfaRecoveryCode.objects.filter(user=user, used_at__isnull=True):
        if check_password(normalizado, registro.code_hash):
            usados = MfaRecoveryCode.objects.filter(
                pk=registro.pk, used_at__isnull=True
            ).update(used_at=timezone.now())
            return usados == 1
    return False


def restablecer_mfa(user: User, request=None, actor: User | None = None) -> None:
    """Retira autenticador, códigos y confianzas (soporte o recuperación)."""
    with transaction.atomic():
        MfaDevice.objects.filter(user=user).delete()
        MfaRecoveryCode.objects.filter(user=user).delete()
        MfaChallenge.objects.filter(user=user, consumed_at__isnull=True).update(
            consumed_at=timezone.now()
        )
        revocar_todas_las_confianzas(user, request, motivo="restablecimiento_mfa")
        registrar_evento(
            EventoAutenticacion.Tipo.MFA_RESTABLECIDO,
            request,
            user,
            actor=str(actor.pk) if actor is not None else None,
        )


# --- Sesión --------------------------------------------------------------


def emitir_tokens(user: User, metodos: list[str]) -> dict[str, str]:
    from apps.authentication.adapters.serializers import TokenObtainPairSerializer

    refresh = TokenObtainPairSerializer.get_token(user)
    # RFC 8176: métodos de autenticación usados (trazabilidad, no autoriza).
    refresh["amr"] = metodos
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


# --- Flujo ---------------------------------------------------------------


@dataclass
class ResultadoAutenticacion:
    status: str  # "authenticated" | "mfa_required" | "mfa_setup_required"
    user: User
    tokens: dict[str, str] = field(default_factory=dict)
    challenge: str | None = None
    #: Token de confianza nuevo para escribir en la cookie (si aplica).
    trusted_device_token: str | None = None
    recovery_codes: list[str] | None = None

    def cuerpo(self) -> dict:
        cuerpo: dict = {"status": self.status}
        if self.status == "authenticated":
            cuerpo.update(self.tokens)
        else:
            cuerpo["challenge"] = self.challenge
            cuerpo["expires_in"] = settings.MFA_CHALLENGE_TTL_SECONDS
        if self.recovery_codes is not None:
            cuerpo["recovery_codes"] = self.recovery_codes
        return cuerpo


def iniciar_sesion(
    request, username: str, password: str, token_confianza: str | None
) -> ResultadoAutenticacion:
    """Paso 1: credenciales. Nunca emite JWT sin segundo factor."""
    proveedor = get_identity_provider()
    user = proveedor.authenticate(request, username=username, password=password)
    if user is None:
        registrar_evento(
            EventoAutenticacion.Tipo.LOGIN_FALLIDO,
            request,
            None,
            proveedor=proveedor.name,
        )
        raise CredencialesInvalidas()

    if proveedor.provides_mfa:
        # Futuro CAS con MFA institucional: no se pide un TOTP adicional.
        registrar_evento(EventoAutenticacion.Tipo.LOGIN_EXITOSO, request, user)
        return ResultadoAutenticacion(
            "authenticated", user, tokens=emitir_tokens(user, [proveedor.name, "mfa"])
        )

    device = MfaDevice.objects.filter(user=user, confirmed_at__isnull=False).first()
    if device is not None and confianza_vigente(user, token_confianza, request):
        registrar_evento(
            EventoAutenticacion.Tipo.DISPOSITIVO_CONFIABLE_USADO, request, user
        )
        registrar_evento(EventoAutenticacion.Tipo.LOGIN_EXITOSO, request, user)
        return ResultadoAutenticacion(
            "authenticated", user, tokens=emitir_tokens(user, ["pwd", "otp"])
        )

    proposito = (
        MfaChallenge.Proposito.VERIFY
        if device is not None
        else MfaChallenge.Proposito.SETUP
    )
    token, _ = crear_reto(user, proposito)
    estado = "mfa_required" if device is not None else "mfa_setup_required"
    return ResultadoAutenticacion(estado, user, challenge=token)


def iniciar_registro(request, token_reto: str) -> dict[str, str]:
    """Genera (o regenera) el secreto pendiente y devuelve el QR."""
    reto = obtener_reto(token_reto, MfaChallenge.Proposito.SETUP)
    user = reto.user
    if MfaDevice.objects.filter(user=user, confirmed_at__isnull=False).exists():
        raise EstadoMfaInvalido()
    secreto = pyotp.random_base32()  # 160 bits
    MfaDevice.objects.update_or_create(
        user=user,
        defaults={
            "secret_encrypted": cifrar_secreto(secreto),
            "confirmed_at": None,
            "last_used_step": None,
        },
    )
    registrar_evento(EventoAutenticacion.Tipo.MFA_REGISTRO_INICIADO, request, user)
    return {
        "qr_svg": qr_svg_data_uri(uri_aprovisionamiento(user, secreto)),
        "manual_key": _formatear_clave_manual(secreto),
        "issuer": settings.MFA_ISSUER_NAME,
        "account": user.get_username(),
    }


def _completar(
    request, user: User, confiar: bool, recovery_codes: list[str] | None = None
) -> ResultadoAutenticacion:
    token_confianza = None
    if confiar:
        token_confianza, _ = crear_confianza(user, request)
    registrar_evento(EventoAutenticacion.Tipo.LOGIN_EXITOSO, request, user)
    return ResultadoAutenticacion(
        "authenticated",
        user,
        tokens=emitir_tokens(user, ["pwd", "otp"]),
        trusted_device_token=token_confianza,
        recovery_codes=recovery_codes,
    )


def confirmar_registro(
    request, token_reto: str, codigo: str, confiar: bool
) -> ResultadoAutenticacion:
    reto = obtener_reto(token_reto, MfaChallenge.Proposito.SETUP)
    user = reto.user
    _comprobar_bloqueo(user, request)
    device = MfaDevice.objects.filter(user=user, confirmed_at__isnull=True).first()
    if device is None:
        raise EstadoMfaInvalido()
    if not verificar_totp(device, codigo):
        _registrar_fallo(reto, request, motivo="registro")
        raise CodigoInvalido()
    with transaction.atomic():
        _consumir_reto(reto)
        device.confirmed_at = timezone.now()
        device.save(update_fields=["confirmed_at"])
        codigos = generar_codigos_recuperacion(user)
    registrar_evento(EventoAutenticacion.Tipo.MFA_REGISTRO_COMPLETADO, request, user)
    return _completar(request, user, confiar, recovery_codes=codigos)


def verificar_segundo_factor(
    request, token_reto: str, codigo: str, confiar: bool
) -> ResultadoAutenticacion:
    reto = obtener_reto(token_reto, MfaChallenge.Proposito.VERIFY)
    user = reto.user
    _comprobar_bloqueo(user, request)
    device = MfaDevice.objects.filter(user=user, confirmed_at__isnull=False).first()
    if device is None:
        raise EstadoMfaInvalido()
    if not verificar_totp(device, codigo):
        _registrar_fallo(reto, request, motivo="totp")
        raise CodigoInvalido()
    _consumir_reto(reto)
    return _completar(request, user, confiar)


def recuperar_con_codigo(
    request, token_reto: str, codigo: str
) -> ResultadoAutenticacion:
    """Pérdida del teléfono: el código de recuperación (un solo uso) retira el
    autenticador anterior y obliga a registrar uno nuevo en el mismo paso."""
    reto = obtener_reto(token_reto, MfaChallenge.Proposito.VERIFY)
    user = reto.user
    _comprobar_bloqueo(user, request)
    if not _consumir_codigo_recuperacion(user, codigo):
        _registrar_fallo(reto, request, motivo="recuperacion")
        raise CodigoInvalido()
    _consumir_reto(reto)
    registrar_evento(EventoAutenticacion.Tipo.MFA_RECUPERACION_USADA, request, user)
    restablecer_mfa(user, request)
    token, _ = crear_reto(user, MfaChallenge.Proposito.SETUP)
    return ResultadoAutenticacion("mfa_setup_required", user, challenge=token)


def cerrar_sesion(request, token_confianza: str | None, user: User | None) -> None:
    """Política aprobada (2026-11-18): todo cierre de sesión revoca la
    confianza del dispositivo desde el que se cierra."""
    revocado = revocar_confianza_por_token(token_confianza, request)
    registrar_evento(
        EventoAutenticacion.Tipo.LOGOUT,
        request,
        user,
        confianza_revocada=revocado,
    )
