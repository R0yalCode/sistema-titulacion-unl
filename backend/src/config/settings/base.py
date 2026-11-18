from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
JWT_SIGNING_KEY = env("JWT_SIGNING_KEY")

if JWT_SIGNING_KEY == SECRET_KEY:
    import logging

    logging.getLogger(__name__).warning(
        "JWT_SIGNING_KEY coincide con SECRET_KEY: configure una clave "
        "distinta (openssl rand -base64 32) antes de producción."
    )

DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "rest_framework",
    "drf_spectacular",
    "apps.authentication.adapters",
    "apps.expedientes.adapters",
    "apps.peticiones.adapters",
    "apps.verificacion.adapters",
    "apps.resoluciones.adapters",
    "apps.notificaciones.adapters",
]

MIDDLEWARE = [
    "core.adapters.middleware.ThreadLocalRequestMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": env("DB_ENGINE", default="django.db.backends.postgresql"),
        "NAME": env("DB_NAME", default="sgt_siaaf"),
        "USER": env("DB_USER", default="sgt_user"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST", default="localhost"),
        "PORT": env("DB_PORT", default="5432"),
        "CONN_HEALTH_CHECKS": True,
        "CONN_MAX_AGE": env.int("DB_CONN_MAX_AGE", default=0),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "authentication.User"

# --- Recuperación de contraseña por correo (AUTH-RC) -------------------
# Vigencia del enlace (segundos). Tras cambiar la contraseña, el enlace deja
# de ser válido aunque no haya caducado.
PASSWORD_RESET_TIMEOUT = env.int("PASSWORD_RESET_TIMEOUT", default=3600)
# Origen público del frontend con el que se construye el enlace del correo.
FRONTEND_BASE_URL = env("FRONTEND_BASE_URL", default="http://localhost:8000")
# Por defecto el correo se escribe en la consola del proceso (desarrollo).
# Un entorno real debe configurar SMTP mediante estas variables.
EMAIL_BACKEND = env(
    "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = env("EMAIL_HOST", default="localhost")
EMAIL_PORT = env.int("EMAIL_PORT", default=25)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=False)
EMAIL_TIMEOUT = env.int("EMAIL_TIMEOUT", default=10)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="no-reply@unl.edu.ec")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    # Añade 429 (VULN-001) y respuestas extra por acción al contrato OpenAPI.
    "DEFAULT_SCHEMA_CLASS": "core.adapters.openapi.SGTAutoSchema",
    "DEFAULT_THROTTLE_RATES": {
        "document_upload": env("DOCUMENT_UPLOAD_THROTTLE", default="10/hour"),
        "auth": env("AUTH_THROTTLE_RATE", default="5/minute"),
        # AUTH-RC: solicitud, validación y confirmación de restablecimiento
        # de contraseña, por IP.
        "password_reset": env("PASSWORD_RESET_THROTTLE_RATE", default="10/hour"),
        # AUTH-B: endpoints del segundo factor (registro, verificación,
        # recuperación), por IP. Se suma al límite de intentos por reto.
        "mfa": env("MFA_THROTTLE_RATE", default="10/minute"),
        # VULN-001 / INC-01-T01: tasa compartida de operaciones mutantes por
        # usuario. Valor técnico provisional (DT-03, pendiente de aprobación).
        "mutante": env("MUTANT_THROTTLE_RATE", default="30/minute"),
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(hours=24),
    "ROTATE_REFRESH_TOKENS": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": JWT_SIGNING_KEY,
}

# --- Autenticación en dos factores (AUTH-A/AUTH-B) --------------------
# Ver docs/autenticacion/politica-2fa.md. Separación de conceptos:
# - Sesión: vida del JWT (SIMPLE_JWT arriba).
# - Confianza del dispositivo: MFA_TRUSTED_DEVICE_DAYS (cookie HttpOnly con
#   token aleatorio; el servidor guarda solo su hash y la fecha de expiración).
# - Reto MFA: ventana para completar el segundo factor tras la contraseña.
#
# Proveedor de identidad activo. Solo existe "local"; "cas" queda documentado
# en docs/autenticacion/arquitectura-cas.md y no está implementado.
AUTH_IDENTITY_PROVIDER = env("AUTH_IDENTITY_PROVIDER", default="local")
# Claves Fernet (URL-safe base64, 32 bytes) separadas por comas. La primera
# cifra; todas descifran (rotación con `manage.py rotate_mfa_keys`).
# Obligatoria en producción; local.py deriva una clave de desarrollo.
MFA_ENCRYPTION_KEYS = env.list("MFA_ENCRYPTION_KEYS", default=[])
MFA_ISSUER_NAME = env("MFA_ISSUER_NAME", default="SGT-SIAAF UNL")
# Tolerancia de deriva de reloj, en periodos de 30 s a cada lado.
MFA_TOTP_VALID_WINDOW = env.int("MFA_TOTP_VALID_WINDOW", default=1)
MFA_CHALLENGE_TTL_SECONDS = env.int("MFA_CHALLENGE_TTL_SECONDS", default=300)
MFA_CHALLENGE_MAX_ATTEMPTS = env.int("MFA_CHALLENGE_MAX_ATTEMPTS", default=5)
# Bloqueo temporal por usuario tras fallos de segundo factor acumulados.
MFA_USER_MAX_FAILURES = env.int("MFA_USER_MAX_FAILURES", default=10)
MFA_USER_LOCKOUT_MINUTES = env.int("MFA_USER_LOCKOUT_MINUTES", default=15)
MFA_RECOVERY_CODES_COUNT = env.int("MFA_RECOVERY_CODES_COUNT", default=10)
MFA_TRUSTED_DEVICE_DAYS = env.int("MFA_TRUSTED_DEVICE_DAYS", default=5)
MFA_TRUSTED_DEVICE_COOKIE_NAME = "sgt_trusted_device"
# Secure en producción (HTTPS); en desarrollo http://localhost no lo admite.
MFA_TRUSTED_DEVICE_COOKIE_SECURE = env.bool(
    "MFA_TRUSTED_DEVICE_COOKIE_SECURE", default=not DEBUG
)

# --- Logging estructurado (SEC-T011) ---------------------------------
# Base segura para TODOS los entornos: solo consola, JSON, con filtros de
# datos sensibles. `production.py` añade handlers de archivo con rotación
# (requieren un directorio que solo existe en el contenedor de producción,
# por lo que no pueden vivir aquí sin romper desarrollo/tests).
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "fmt": "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s %(user_id)s",
        },
    },
    "filters": {
        "sensitive_data": {"()": "core.adapters.logging_filters.SensitiveDataFilter"},
        "request_id": {"()": "core.adapters.logging_filters.RequestIdFilter"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "filters": ["sensitive_data", "request_id"],
        },
    },
    "loggers": {
        "apps": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "core": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "django.request": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "django.security": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
    "root": {"handlers": ["console"], "level": "WARNING"},
}

SPECTACULAR_SETTINGS = {
    "TITLE": "SGT-SIAAF API",
    "DESCRIPTION": "Sistema de Gestión del Trámite de Titulación integrado al SIAAF",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": "/api/v1",
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
    "SERVE_AUTHENTICATION": [],
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "displayOperationId": True,
    },
    "REDOC_SETTINGS": {
        "hideDownloadButton": False,
        "expandResponses": "200,201",
    },
    "CONTACT": {
        "name": "UNL - FEIRNNR",
        "email": "soporte@unl.edu.ec",
    },
    "LICENSE": {
        "name": "Proprietary",
    },
    "SECURITY": [{"BearerAuth": []}],
    "COMPONENTS": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
    },
}
