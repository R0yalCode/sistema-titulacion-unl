"""Proveedores de identidad disponibles (AUTH-A).

Solo existe el proveedor local (usuario y contraseña de Django). La
integración con el SAC de la UNL (Apereo CAS) no está implementada ni
simulada: requiere el registro de SGT-SIAAF como servicio y la información
listada en docs/autenticacion/arquitectura-cas.md.
"""

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.exceptions import ImproperlyConfigured

from apps.authentication.ports.identity_provider import IdentityProvider


class LocalIdentityProvider:
    """Correo institucional + contraseña verificados contra la BD local.

    El acceso es por correo, pero `USERNAME_FIELD` sigue siendo `username`
    (no se migra el modelo): se localiza la cuenta por `email` sin distinguir
    mayúsculas (restricción única `unique_user_email_ci`) y se delega en
    `django.contrib.auth.authenticate`, que usa el hasher configurado y
    rechaza cuentas inactivas. Los roles salen de `UserRole` (RBAC local), no
    del SAC.
    """

    name = "local"
    provides_mfa = False

    def authenticate(
        self, request, email: str, password: str
    ) -> AbstractBaseUser | None:
        modelo = get_user_model()
        cuenta = modelo._default_manager.filter(email__iexact=email).first()
        if cuenta is None:
            # Igualar el coste temporal con el de una cuenta existente para no
            # revelar qué correos están registrados (como hace ModelBackend).
            modelo().set_password(password)
            return None
        user = authenticate(request, username=cuenta.get_username(), password=password)
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
