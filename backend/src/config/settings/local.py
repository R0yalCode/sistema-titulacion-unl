from .base import *  # noqa: F401,F403,F405

DEBUG = True

# SEC-T011: en desarrollo, nivel DEBUG en consola (ya es el handler base).
LOGGING["loggers"]["apps"]["level"] = "DEBUG"
LOGGING["loggers"]["core"]["level"] = "DEBUG"
