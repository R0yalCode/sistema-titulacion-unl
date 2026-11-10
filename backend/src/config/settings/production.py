"""Settings de producción (SEC-T001).

Hereda de `base.py` y endurece la configuración para un despliegue real:
HTTPS obligatorio, cookies seguras, CSRF, CORS, cabeceras de seguridad y
CSP (DEC-010). No incluye el handler global de excepciones (SEC-T010,
bloqueada por DEC-009), la protección de Swagger (SEC-T013, siguiente
tarea tras esta) ni el logging estructurado completo (SEC-T011, siguiente
tarea tras SEC-T012) para evitar duplicar configuración entre fichas que
añaden a este mismo archivo por separado (ver
`MATRIZ_DEPENDENCIAS_Y_PRIORIZACION.md`, sección "Archivos settings/
modificados por múltiples tareas").

Todas las variables de entorno nuevas son obligatorias (sin valor por
defecto salvo donde se indica explícitamente) y deben ser provistas por
quien despliegue — este archivo no contiene ningún dominio, secreto ni
certificado real.
"""

import copy

from .base import *  # noqa: F401,F403,F405

# `from .base import *` liga estos nombres al MISMO objeto dict/list que
# usa base.py. Mutarlos in-place (LOGGING["handlers"][...] = ...) ensuciaría
# también base.py (y por lo tanto local.py/test.py) dentro del mismo
# proceso — p. ej. en una suite de tests que importe production.py una vez.
# Se copian antes de modificarlos; INSTALLED_APPS/MIDDLEWARE no necesitan
# esto porque se reasignan con `+` (crea una lista nueva, no muta la vieja).
LOGGING = copy.deepcopy(LOGGING)
SPECTACULAR_SETTINGS = copy.deepcopy(SPECTACULAR_SETTINGS)

DEBUG = False

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# --- HTTPS / HSTS -----------------------------------------------------
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# El healthcheck del contenedor golpea al backend directamente (sin pasar
# por Nginx/TLS), por lo que no lleva X-Forwarded-Proto: https. Sin esta
# excepción, SECURE_SSL_REDIRECT lo redirigiría (301) y Docker lo marcaría
# como unhealthy pese a que el proceso está perfectamente sano.
SECURE_REDIRECT_EXEMPT = [r"^health/?$"]

# --- Cookies / CSRF -----------------------------------------------------
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS")

# --- CORS (django-cors-headers) ----------------------------------------
INSTALLED_APPS = INSTALLED_APPS + ["corsheaders"]
MIDDLEWARE = (
    ["corsheaders.middleware.CorsMiddleware"]
    + MIDDLEWARE
    + ["core.adapters.security_headers.ContentSecurityPolicyMiddleware"]
)
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS")
CORS_ALLOW_CREDENTIALS = True

# --- IP real tras proxy (consumida por el middleware de SEC-T005; aquí
# solo se declara la configuración, SEC-T001 no implementa el middleware) --
TRUSTED_PROXIES = env.list(
    "TRUSTED_PROXIES",
    default=["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"],
)

# --- Otras cabeceras de seguridad ---------------------------------------
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"

# --- Content-Security-Policy (DEC-010, aprobada 2026-11-05: opción D) --
# Bloqueante: solo frame-ancestors/base-uri (bajo riesgo, protege
# clickjacking e inyección de <base>). El resto de directivas va en modo
# Report-Only: NO BLOQUEAN NADA, solo se reportarían si existiera un
# endpoint de recepción (no incluido en el alcance de SEC-T001).
CSP_BLOCKING_POLICY = "frame-ancestors 'none'; base-uri 'self'"

_csp_connect_extra = env.list("CSP_CONNECT_SRC_EXTRA", default=[])
_csp_connect_src = "'self'" + (
    " " + " ".join(_csp_connect_extra) if _csp_connect_extra else ""
)
CSP_REPORT_ONLY_POLICY = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self'; "
    "img-src 'self' data:; "
    "font-src 'self'; "
    f"connect-src {_csp_connect_src}; "
    "frame-ancestors 'none'; "
    "base-uri 'self'"
)

# --- Validación de claves distintas (SEC-T004, ya implementada en base.py) --
# El warning si JWT_SIGNING_KEY == SECRET_KEY ya se evalúa en base.py y
# aplica igual aquí por herencia; no se repite la lógica.

# --- Logging estructurado con archivos rotativos (SEC-T011) ------------
# Requiere que /var/log/sgt-siaaf/ exista y sea escribible por appuser;
# lo crea el target `production` del Dockerfile. Si el directorio no
# existe, Django fallará al arrancar con un error claro (preferible a
# silenciarlo o escribir en un lugar inesperado).
_LOG_DIR = env("LOG_DIR", default="/var/log/sgt-siaaf")
_ROTATING_FILE_BASE = {
    "class": "logging.handlers.RotatingFileHandler",
    "maxBytes": 10 * 1024 * 1024,
    "backupCount": 5,
    "formatter": "json",
    "filters": ["sensitive_data", "request_id"],
}
LOGGING["handlers"]["apps_file"] = {**_ROTATING_FILE_BASE, "filename": f"{_LOG_DIR}/apps.log"}
LOGGING["handlers"]["django_file"] = {**_ROTATING_FILE_BASE, "filename": f"{_LOG_DIR}/django.log"}
LOGGING["handlers"]["security_file"] = {
    **_ROTATING_FILE_BASE,
    "filename": f"{_LOG_DIR}/security.log",
}
LOGGING["loggers"]["apps"] = {"handlers": ["apps_file"], "level": "INFO", "propagate": False}
LOGGING["loggers"]["core"] = {"handlers": ["apps_file"], "level": "INFO", "propagate": False}
LOGGING["loggers"]["django"] = {"handlers": ["django_file"], "level": "WARNING", "propagate": False}
LOGGING["loggers"]["django.request"] = {
    "handlers": ["django_file"],
    "level": "WARNING",
    "propagate": False,
}
LOGGING["loggers"]["django.security"] = {
    "handlers": ["security_file"],
    "level": "INFO",
    "propagate": False,
}

# --- Protección de Swagger/ReDoc/Schema (SEC-T013) ----------------------
# En base.py (dev/test) es AllowAny; solo en producción se restringe a
# administradores, para no exponer la superficie de la API públicamente.
SPECTACULAR_SETTINGS["SERVE_PERMISSIONS"] = ["rest_framework.permissions.IsAdminUser"]
