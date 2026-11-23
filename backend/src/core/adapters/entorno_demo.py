"""Protección de los comandos que cargan datos de demostración.

La decisión no se lee de ninguna variable propia ni de `DEBUG`. Solo se permite
la carga si se cumplen las dos condiciones:

1. el módulo de settings activo pertenece a la lista cerrada de desarrollo y
   pruebas, de modo que un módulo desconocido queda rechazado;
2. no existe la marca que la imagen de producción crea como root, de modo que
   cambiar `DJANGO_SETTINGS_MODULE` o usar `--settings` dentro de esa imagen
   tampoco habilita la carga.
"""

import os
from pathlib import Path

from django.conf import settings
from django.core.management.base import CommandError

MODULOS_PERMITIDOS = frozenset(
    {
        "config.settings.local",
        "config.settings.test",
        "config.settings.test_postgres",
    }
)
NOMBRE_MARCA_PRODUCCION = ".entorno-produccion"


def _existe_marca_produccion() -> bool:
    return (Path(settings.BASE_DIR).parent / NOMBRE_MARCA_PRODUCCION).exists()


def exigir_entorno_de_demostracion(comando: str) -> None:
    """Detiene el comando, antes de acceder a la base, fuera de desarrollo y pruebas."""
    modulo = os.environ.get("DJANGO_SETTINGS_MODULE", "")
    if _existe_marca_produccion() or modulo not in MODULOS_PERMITIDOS:
        raise CommandError(
            f"{comando} solo puede ejecutarse en desarrollo o pruebas: carga "
            "datos de demostración y este entorno no lo permite. No se "
            "escribió ningún dato."
        )
