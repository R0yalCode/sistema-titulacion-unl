"""Configuración común de pytest para el backend (PLB-E1-04 + O-2, T3).

- Aísla `MEDIA_ROOT` y `PRIVATE_MEDIA_ROOT` en un directorio temporal por
  prueba: ninguna prueba escribe en `src/media/` (hallazgo F-04 de la
  auditoría de E2-01) ni puede sobrescribir o borrar archivos reales.
- Omite las pruebas marcadas `postgres` cuando la base de datos no es
  PostgreSQL (la suite por defecto usa SQLite en memoria).
"""

import pytest


def pytest_collection_modifyitems(config, items):
    from django.conf import settings

    motor = settings.DATABASES["default"]["ENGINE"]
    if "postgresql" in motor:
        return
    omitir = pytest.mark.skip(
        reason="Requiere PostgreSQL real: DJANGO_SETTINGS_MODULE="
        "config.settings.test_postgres (ver tests/integration/README.md)."
    )
    for item in items:
        if "postgres" in item.keywords:
            item.add_marker(omitir)


@pytest.fixture(autouse=True)
def _media_root_temporal(settings, tmp_path):
    raiz = tmp_path / "media"
    privada = raiz / "private"
    privada.mkdir(parents=True)
    settings.MEDIA_ROOT = raiz
    settings.PRIVATE_MEDIA_ROOT = privada
    return raiz
