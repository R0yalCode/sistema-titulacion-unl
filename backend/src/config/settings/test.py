from .base import *  # noqa: F401,F403

DEBUG = False

# Pruebas: fuente simulada habilitada explícitamente (las pruebas de
# configuración la deshabilitan con `settings`).
ACADEMIC_PROFILE_PROVIDER = "mock_sga"
ACADEMIC_PROFILE_MOCK_ALLOWED = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
# AUTH-A: clave Fernet efímera por proceso de pruebas (nunca persistida).
if not MFA_ENCRYPTION_KEYS:  # noqa: F405
    from cryptography.fernet import Fernet

    MFA_ENCRYPTION_KEYS = [Fernet.generate_key().decode()]
