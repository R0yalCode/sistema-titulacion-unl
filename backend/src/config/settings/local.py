from .base import *  # noqa: F401,F403,F405

DEBUG = True

# Desarrollo: simulación MockSGA habilitada salvo que se configure otra fuente.
ACADEMIC_PROFILE_PROVIDER = env(  # noqa: F405
    "ACADEMIC_PROFILE_PROVIDER", default="mock_sga"
)
ACADEMIC_PROFILE_MOCK_ALLOWED = env.bool(  # noqa: F405
    "ACADEMIC_PROFILE_MOCK_ALLOWED", default=True
)

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

# AUTH-A: base.py calcula la bandera Secure de la cookie de confianza con el
# DEBUG del entorno, antes de que este archivo fije DEBUG=True. Sin la
# variable DEBUG la cookie saldría Secure y no viajaría por http://localhost.
MFA_TRUSTED_DEVICE_COOKIE_SECURE = env.bool(  # noqa: F405
    "MFA_TRUSTED_DEVICE_COOKIE_SECURE", default=False
)
