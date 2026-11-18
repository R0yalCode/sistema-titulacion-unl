from .base import *  # noqa: F401,F403,F405

DEBUG = True

# SEC-T011: en desarrollo, nivel DEBUG en consola (ya es el handler base).
LOGGING["loggers"]["apps"]["level"] = "DEBUG"
LOGGING["loggers"]["core"]["level"] = "DEBUG"

# AUTH-A: sin MFA_ENCRYPTION_KEYS explícita, se deriva una clave Fernet
# determinista de SECRET_KEY para que el entorno de desarrollo arranque.
# Solo desarrollo: production.py exige la variable y no hereda esto.
if not MFA_ENCRYPTION_KEYS:  # noqa: F405
    import base64
    import hashlib

    MFA_ENCRYPTION_KEYS = [
        base64.urlsafe_b64encode(
            hashlib.sha256(
                ("sgt-siaaf-mfa-dev:" + SECRET_KEY).encode()  # noqa: F405
            ).digest()
        ).decode()
    ]
