"""Puerto de proveedor de identidad (AUTH-A).

Separa *quién verifica la identidad* (contraseña local hoy; SAC/Apereo CAS
en el futuro) del resto del flujo: segundo factor, confianza del
dispositivo, emisión de la sesión (JWT) y autorización RBAC, que siguen en
SGT-SIAAF y no dependen del proveedor.

Ver docs/autenticacion/arquitectura-cas.md.
"""

from typing import Protocol

from django.contrib.auth.base_user import AbstractBaseUser


class IdentityProvider(Protocol):
    """Contrato mínimo de un proveedor de identidad."""

    #: Identificador estable ("local", y en el futuro "cas").
    name: str

    #: True si el proveedor ya exige un segundo factor institucional. En ese
    #: caso SGT-SIAAF no pide un TOTP adicional (evita doble MFA con CAS).
    provides_mfa: bool

    def authenticate(
        self, request, username: str, password: str
    ) -> AbstractBaseUser | None:
        """Devuelve el usuario local verificado o None.

        No revela el motivo del rechazo (usuario inexistente, contraseña
        incorrecta o cuenta inactiva) para no permitir enumeración.
        """
        ...
