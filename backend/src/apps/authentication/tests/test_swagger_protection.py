"""Pruebas de SEC-T013: protección de Swagger/ReDoc/Schema en producción.

Nota de diseño: `drf-spectacular` cachea internamente su objeto de
configuración (`drf_spectacular.settings.spectacular_settings`) la primera
vez que se accede a él, y no reacciona de forma fiable a
`django.test.override_settings` dentro del mismo proceso de pytest — se
comprobó empíricamente que el resultado dependía del orden de ejecución de
los tests, no del valor "overrideado" (comportamiento no determinista, por
lo que una prueba basada en eso sería una prueba inválida, no una prueba
real). Por eso aquí se verifica:
1. El contenido real de `production.py`/`local.py` como módulos (estático,
   determinista).
2. El comportamiento real de la clase de permiso que `production.py`
   configura (`IsAdminUser`), de forma aislada y determinista.
La verificación de extremo a extremo (arrancar Django bajo
`DJANGO_SETTINGS_MODULE=config.settings.production` real y golpear
`/api/v1/docs/`) se hizo manualmente en esta sesión (ver informe de
cierre de SEC-T013), no como test automatizado de este archivo.
"""

import importlib

import pytest
from rest_framework.permissions import IsAdminUser
from rest_framework.test import APIRequestFactory

from apps.authentication.adapters.models import User

pytestmark = pytest.mark.django_db


def test_production_settings_module_restricts_to_admin(monkeypatch):
    """`production.py` exige variables sin default (ALLOWED_HOSTS,
    CSRF_TRUSTED_ORIGINS, CORS_ALLOWED_ORIGINS); se fijan solo para poder
    importar el módulo y leer su contenido, no para ejecutar la app bajo
    esos settings."""
    monkeypatch.setenv("ALLOWED_HOSTS", "test.invalid")
    monkeypatch.setenv("CSRF_TRUSTED_ORIGINS", "https://test.invalid")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://test.invalid")

    produccion = importlib.import_module("config.settings.production")
    assert produccion.SPECTACULAR_SETTINGS["SERVE_PERMISSIONS"] == [
        "rest_framework.permissions.IsAdminUser"
    ]
    # La copia de production.py no debe haber contaminado la de base.py
    base = importlib.import_module("config.settings.base")
    assert base.SPECTACULAR_SETTINGS["SERVE_PERMISSIONS"] == [
        "rest_framework.permissions.AllowAny"
    ]


def test_local_settings_module_keeps_allowany():
    local = importlib.import_module("config.settings.local")
    assert local.SPECTACULAR_SETTINGS["SERVE_PERMISSIONS"] == [
        "rest_framework.permissions.AllowAny"
    ]


def test_swagger_anonymous_denied_in_production_settings():
    """Comportamiento real de la clase de permiso que production.py
    configura, con una petición anónima."""
    request = APIRequestFactory().get("/api/v1/docs/")
    request.user = None
    assert IsAdminUser().has_permission(request, view=None) is False


def test_swagger_admin_allowed_in_production_settings():
    admin = User.objects.create_user(
        username="sec_t013_admin", password="pass1234", is_staff=True
    )
    request = APIRequestFactory().get("/api/v1/docs/")
    request.user = admin
    assert IsAdminUser().has_permission(request, view=None) is True


def test_schema_anonymous_denied_in_production_settings():
    request = APIRequestFactory().get("/api/v1/schema/")
    request.user = None
    assert IsAdminUser().has_permission(request, view=None) is False


def test_swagger_allowany_in_local_settings():
    """En local.py (AllowAny, verificado en test_local_settings_module_keeps_allowany
    arriba) cualquier request pasa — AllowAny no deniega nunca."""
    from rest_framework.permissions import AllowAny

    request = APIRequestFactory().get("/api/v1/docs/")
    request.user = None
    assert AllowAny().has_permission(request, view=None) is True
