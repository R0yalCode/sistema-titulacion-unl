"""Proveedores de identidad disponibles (AUTH-A).

Solo existe el proveedor local (usuario y contraseña de Django). La
integración con el SAC de la UNL (Apereo CAS) no está implementada ni
simulada: requiere el registro de SGT-SIAAF como servicio y la información
listada en docs/autenticacion/arquitectura-cas.md.
"""

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.exceptions import ImproperlyConfigured

from apps.authentication.ports.identity_provider import IdentityProvider


class LocalIdentityProvider:
    """Credenciales locales verificadas por los backends de Django.

    `django.contrib.auth.authenticate` usa el hasher configurado
    (PBKDF2 por defecto) y `ModelBackend` rechaza cuentas inactivas.
    """

    name = "local"
    provides_mfa = False

    def authenticate(
        self, request, username: str, password: str
    ) -> AbstractBaseUser | None:
        user = authenticate(request, username=username, password=password)
        if user is None or not user.is_active:
            return None
        return user


_PROVEEDORES: dict[str, type] = {
    LocalIdentityProvider.name: LocalIdentityProvider,
}


def get_identity_provider() -> IdentityProvider:
    """Proveedor configurado en `AUTH_IDENTITY_PROVIDER`.

    Un valor desconocido (incluido "cas" mientras no exista integración
    autorizada) detiene la operación en lugar de degradar a otro proveedor.
    """
    nombre = getattr(settings, "AUTH_IDENTITY_PROVIDER", "local")
    clase = _PROVEEDORES.get(nombre)
    if clase is None:
        raise ImproperlyConfigured(
            f"AUTH_IDENTITY_PROVIDER='{nombre}' no está disponible. "
            "Solo 'local' está implementado."
        )
    return clase()
