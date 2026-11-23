"""Validación de la configuración de correo y de enlaces en producción.

Los mensajes de error no incluyen los valores recibidos: la configuración de
correo puede contener credenciales.
"""

import ipaddress
from urllib.parse import urlsplit

from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.validators import validate_email
from django.http.request import validate_host

BACKEND_SMTP = "django.core.mail.backends.smtp.EmailBackend"


def _es_host_local(host: str) -> bool:
    nombre = host.strip().rstrip(".").lower()
    if nombre == "localhost" or nombre.endswith(".localhost"):
        return True
    try:
        direccion = ipaddress.ip_address(nombre.strip("[]"))
    except ValueError:
        return False
    return direccion.is_loopback or direccion.is_unspecified


def validar_backend_correo(backend: str) -> str:
    if backend != BACKEND_SMTP:
        raise ImproperlyConfigured(
            f"EMAIL_BACKEND debe ser {BACKEND_SMTP} en producción."
        )
    return backend


def validar_servidor_correo(
    host: str, usuario: str, contrasena: str, usa_tls: bool
) -> str:
    host = host.strip()
    if not host or _es_host_local(host):
        raise ImproperlyConfigured(
            "EMAIL_HOST debe ser un servidor SMTP real en producción."
        )
    if not usa_tls:
        raise ImproperlyConfigured("EMAIL_USE_TLS debe estar activo en producción.")
    if bool(usuario) != bool(contrasena):
        raise ImproperlyConfigured(
            "EMAIL_HOST_USER y EMAIL_HOST_PASSWORD deben definirse juntos."
        )
    return host


def validar_remitente(remitente: str) -> str:
    remitente = remitente.strip()
    try:
        validate_email(remitente)
    except ValidationError:
        raise ImproperlyConfigured(
            "DEFAULT_FROM_EMAIL debe ser una dirección de correo válida."
        ) from None
    return remitente


def validar_url_frontend(valor: str, hosts_permitidos: list[str]) -> str:
    """Exige un origen HTTPS público y admitido por `ALLOWED_HOSTS`."""
    error = ImproperlyConfigured(
        "FRONTEND_BASE_URL debe ser un origen HTTPS público, sin ruta ni barra "
        "final, cuyo host figure en ALLOWED_HOSTS."
    )
    if valor != valor.strip() or any(c in valor for c in "\\\r\n\t "):
        raise error
    try:
        partes = urlsplit(valor)
        host = partes.hostname
        _ = partes.port
    except ValueError:
        raise error from None
    if (
        partes.scheme != "https"
        or not host
        or partes.username is not None
        or partes.password is not None
        or partes.path
        or partes.query
        or partes.fragment
        or _es_host_local(host)
        or not validate_host(host.lower(), hosts_permitidos)
    ):
        raise error
    return valor
