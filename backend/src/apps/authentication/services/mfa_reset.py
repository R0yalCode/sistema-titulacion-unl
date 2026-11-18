"""Restablecimiento del doble factor por enlace (MFA-RST).

Reproduce el procedimiento de referencia del SAC (correo institucional +
cédula + contraseña actual → enlace de vigencia limitada) con estas
salvaguardas:

1. Conocer correo, cédula y contraseña **no** basta: la solicitud solo envía
   un enlace de un solo uso al correo registrado de la cuenta. El 2FA se
   restablece únicamente al confirmar ese enlace (posesión del buzón).
2. Respuesta pública idéntica en todos los casos (antienumeración): no se
   revela si el correo existe, si la cédula coincide ni si se envió algo.
3. Espera tras restablecer la contraseña (`MFA_RESET_COOLDOWN_HOURS`): quien
   solo controle el buzón no puede cambiar la contraseña y, enseguida,
   anular el 2FA por el mismo canal.
4. El enlace queda ligado al autenticador vigente: deja de valer en cuanto
   se usa (el autenticador desaparece) o si cambia la contraseña.
5. Auditoría en `EventoAutenticacion` sin correo, cédula, contraseña ni token.

Pendiente de la UNL (docs/autenticacion/politica-2fa.md §6): el canal al que
debe ir el enlace (la referencia menciona el «correo personal»; SGT-SIAAF
solo almacena el correo institucional) y la aceptación formal del
procedimiento.
"""

import hmac
import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from apps.authentication.adapters.models import EventoAutenticacion, MfaDevice
from apps.authentication.services.identity_providers import get_identity_provider
from apps.authentication.services.mfa import registrar_evento, restablecer_mfa

logger = logging.getLogger(__name__)

RUTA_CONFIRMAR = "/restablecer-2fa/confirmar"


class EnlaceMfaInvalido(Exception):
    """Enlace inexistente, caducado, ya usado o de otra cuenta."""


class _GeneradorEnlaceMfa(PasswordResetTokenGenerator):
    """Token firmado con SECRET_KEY y una sal propia (no intercambiable con
    el de contraseña). Vigencia: PASSWORD_RESET_TIMEOUT."""

    key_salt = "apps.authentication.services.mfa_reset.EnlaceMfa"

    def _make_hash_value(self, user, timestamp):
        device = MfaDevice.objects.filter(user=user).first()
        estado = f"{device.pk}:{device.confirmed_at}" if device else "sin-2fa"
        return f"{user.pk}{user.password}{timestamp}{estado}"


generador_enlace_mfa = _GeneradorEnlaceMfa()


def _en_espera_tras_cambio_de_contrasena(user) -> bool:
    desde = timezone.now() - timedelta(hours=settings.MFA_RESET_COOLDOWN_HOURS)
    return EventoAutenticacion.objects.filter(
        user=user,
        tipo=EventoAutenticacion.Tipo.CONTRASENA_RESTABLECIDA,
        created_at__gte=desde,
    ).exists()


def _rechazar(request, user, motivo: str) -> None:
    registrar_evento(
        EventoAutenticacion.Tipo.MFA_RESTABLECIMIENTO_RECHAZADO,
        request,
        user,
        motivo=motivo,
    )


def construir_enlace(user) -> str:
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = generador_enlace_mfa.make_token(user)
    base = settings.FRONTEND_BASE_URL.rstrip("/")
    return f"{base}{RUTA_CONFIRMAR}?uid={uid}&token={token}"


def solicitar_restablecimiento(request, email: str, cedula: str, password: str):
    """Envía el enlace si correo, cédula y contraseña corresponden a una
    cuenta activa con 2FA. Nunca informa del resultado al llamador."""
    user = get_identity_provider().authenticate(request, email=email, password=password)
    if user is None:
        _rechazar(request, None, "credenciales")
        return
    if not hmac.compare_digest((user.cedula or "").strip(), cedula.strip()):
        _rechazar(request, user, "cedula")
        return
    if not MfaDevice.objects.filter(user=user).exists():
        _rechazar(request, user, "sin_2fa")
        return
    if _en_espera_tras_cambio_de_contrasena(user):
        _rechazar(request, user, "espera_tras_cambio_de_contrasena")
        return

    registrar_evento(
        EventoAutenticacion.Tipo.MFA_RESTABLECIMIENTO_SOLICITADO, request, user
    )
    minutos = settings.PASSWORD_RESET_TIMEOUT // 60
    mensaje = (
        "Hola,\n\n"
        "Recibimos una solicitud para restablecer el doble factor de "
        "autenticación (2FA) de su cuenta en el Sistema de Gestión de "
        "Titulación (SGT-SIAAF).\n\n"
        "Para retirar el autenticador actual y registrar uno nuevo, abra este "
        "enlace y confirme la operación:\n\n"
        f"{construir_enlace(user)}\n\n"
        f"El enlace caduca en {minutos} minutos y solo puede usarse una vez.\n\n"
        "Si usted no realizó esta solicitud, no abra el enlace y cambie su "
        "contraseña: alguien la conoce.\n\n"
        "Universidad Nacional de Loja"
    )
    try:
        send_mail(
            subject="SGT-SIAAF: restablecimiento del doble factor (2FA)",
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception:  # noqa: BLE001 - nunca debe alterar la respuesta
        logger.exception(
            "No se pudo enviar el correo de restablecimiento del 2FA",
            extra={"usuario_id": str(user.pk)},
        )


def _resolver(uid: str, token: str):
    modelo = get_user_model()
    try:
        pk = force_str(urlsafe_base64_decode(uid))
        user = modelo._default_manager.get(pk=pk, is_active=True)
    except (TypeError, ValueError, OverflowError, ValidationError, modelo.DoesNotExist):
        raise EnlaceMfaInvalido from None
    if not MfaDevice.objects.filter(user=user).exists():
        raise EnlaceMfaInvalido
    if not generador_enlace_mfa.check_token(user, token):
        raise EnlaceMfaInvalido
    return user


@transaction.atomic
def confirmar_restablecimiento(request, uid: str, token: str) -> None:
    """Retira autenticador, códigos y confianzas; el siguiente ingreso con
    contraseña obliga a registrar un autenticador nuevo."""
    user = _resolver(uid, token)
    restablecer_mfa(user, request, actor=user)
