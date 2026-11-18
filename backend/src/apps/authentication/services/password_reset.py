"""Recuperación de contraseña por correo (AUTH-RC).

Flujo sin estado propio: reutiliza `PasswordResetTokenGenerator` de Django.
El token queda ligado a la contraseña vigente, al último acceso y al correo
del usuario, por lo que:

- caduca a los `PASSWORD_RESET_TIMEOUT` segundos;
- deja de ser válido en cuanto la contraseña cambia (un solo uso);
- no requiere modelos ni migraciones nuevas.

Antienumeración: `solicitar_restablecimiento()` no devuelve nada ni lanza
excepciones que distingan si el correo existe; la vista responde siempre
igual. En los logs solo se registra el identificador interno del usuario,
nunca el correo, el token ni el enlace.
"""

import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

logger = logging.getLogger(__name__)

RUTA_RESTABLECER = "/restablecer-contrasena"


class EnlaceInvalido(Exception):
    """El par uid/token no es válido, caducó o ya se utilizó."""


class ContrasenaInvalida(Exception):
    """La nueva contraseña incumple la política (AUTH_PASSWORD_VALIDATORS)."""

    def __init__(self, mensajes):
        super().__init__("; ".join(mensajes))
        self.mensajes = list(mensajes)


def _usuarios_recuperables(email):
    """Usuarios activos, con contraseña utilizable, cuyo correo coincide."""
    modelo = get_user_model()
    candidatos = modelo._default_manager.filter(email__iexact=email, is_active=True)
    return [
        usuario
        for usuario in candidatos
        if usuario.has_usable_password() and usuario.email
    ]


def construir_enlace(usuario):
    uid = urlsafe_base64_encode(force_bytes(usuario.pk))
    token = default_token_generator.make_token(usuario)
    base = settings.FRONTEND_BASE_URL.rstrip("/")
    return f"{base}{RUTA_RESTABLECER}?uid={uid}&token={token}"


def solicitar_restablecimiento(email):
    """Envía las instrucciones si el correo pertenece a una cuenta activa.

    No informa del resultado al llamador: un fallo de envío se registra en
    el log técnico y no altera la respuesta pública.
    """
    minutos = settings.PASSWORD_RESET_TIMEOUT // 60
    for usuario in _usuarios_recuperables(email):
        mensaje = (
            "Hola,\n\n"
            "Recibimos una solicitud para restablecer la contraseña de su "
            "cuenta en el Sistema de Gestión de Titulación (SGT-SIAAF).\n\n"
            "Para definir una nueva contraseña, abra este enlace:\n\n"
            f"{construir_enlace(usuario)}\n\n"
            f"El enlace caduca en {minutos} minutos y solo puede usarse una "
            "vez.\n\n"
            "Si usted no realizó esta solicitud, ignore este mensaje: su "
            "contraseña no cambiará.\n\n"
            "Universidad Nacional de Loja"
        )
        try:
            send_mail(
                subject="SGT-SIAAF: restablecimiento de contraseña",
                message=mensaje,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[usuario.email],
                fail_silently=False,
            )
        except Exception:  # noqa: BLE001 - nunca debe alterar la respuesta
            logger.exception(
                "No se pudo enviar el correo de restablecimiento",
                extra={"usuario_id": str(usuario.pk)},
            )
        else:
            logger.info(
                "Correo de restablecimiento enviado",
                extra={"usuario_id": str(usuario.pk)},
            )


def _resolver_usuario(uid, token):
    modelo = get_user_model()
    try:
        pk = force_str(urlsafe_base64_decode(uid))
        usuario = modelo._default_manager.get(pk=pk, is_active=True)
    except (TypeError, ValueError, OverflowError, ValidationError, modelo.DoesNotExist):
        raise EnlaceInvalido from None
    if not default_token_generator.check_token(usuario, token):
        raise EnlaceInvalido
    return usuario


def validar_enlace(uid, token):
    """Lanza `EnlaceInvalido` si el enlace no puede usarse."""
    _resolver_usuario(uid, token)


@transaction.atomic
def confirmar_restablecimiento(uid, token, nueva_contrasena):
    usuario = _resolver_usuario(uid, token)
    try:
        validate_password(nueva_contrasena, user=usuario)
    except ValidationError as error:
        raise ContrasenaInvalida(error.messages) from None
    usuario.set_password(nueva_contrasena)
    usuario.save(update_fields=["password"])
    # AUTH-B: un cambio de contraseña retira la confianza de todos los
    # dispositivos; el siguiente ingreso vuelve a pedir el segundo factor.
    from apps.authentication.adapters.models import EventoAutenticacion
    from apps.authentication.services.mfa import (
        registrar_evento,
        revocar_todas_las_confianzas,
    )

    revocar_todas_las_confianzas(usuario, motivo="cambio_contrasena")
    # Inicia la espera de MFA_RESET_COOLDOWN_HOURS para el restablecimiento
    # del 2FA por enlace (services/mfa_reset.py).
    registrar_evento(EventoAutenticacion.Tipo.CONTRASENA_RESTABLECIDA, None, usuario)
    logger.info("Contraseña restablecida", extra={"usuario_id": str(usuario.pk)})
