"""Protección de los comandos que cargan datos de demostración.

La carga solo continúa si se cumplen todas las condiciones:

1. El módulo de settings pertenece a la lista cerrada de desarrollo y pruebas.
2. No existe la marca que la imagen de producción crea como root.
3. El **destino** lo admite: la base está registrada como `desarrollo` o es una
   base temporal creada por el ejecutor de pruebas.

Una base de producción, sin identidad, con identidad inconsistente o que no se
pueda consultar se rechaza. La comprobación solo lee y ocurre antes de cualquier
escritura. Ninguna variable propia ni `DEBUG` la desactiva.
"""

import os
from pathlib import Path

from django.conf import settings
from django.core.management.base import CommandError
from django.db import DatabaseError, connection, transaction
from django.test.utils import _TestState

MODULO_PRODUCCION = "config.settings.production"
MODULO_DESARROLLO = "config.settings.local"
MODULOS_PRUEBAS = frozenset({"config.settings.test", "config.settings.test_postgres"})
MODULOS_PERMITIDOS = MODULOS_PRUEBAS | {MODULO_DESARROLLO}
NOMBRE_MARCA_PRODUCCION = ".entorno-produccion"
TABLA_IDENTIDAD = "sgt_identidad_entorno"
ENTORNO_DESARROLLO = "desarrollo"
ENTORNO_PRODUCCION = "produccion"


class IdentidadNoVerificable(Exception):
    """La identidad de la base no se pudo leer o no es coherente."""


def modulo_activo() -> str:
    return os.environ.get("DJANGO_SETTINGS_MODULE", "")


def existe_marca_produccion() -> bool:
    return (Path(settings.BASE_DIR).parent / NOMBRE_MARCA_PRODUCCION).exists()


def leer_identidad_base() -> str | None:
    """Devuelve el entorno registrado, o `None` si la base no tiene identidad."""
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                if TABLA_IDENTIDAD not in connection.introspection.table_names(cursor):
                    return None
                cursor.execute(f"SELECT entorno FROM {TABLA_IDENTIDAD}")  # nosec B608
                filas = cursor.fetchall()
    except DatabaseError as error:
        raise IdentidadNoVerificable from error
    if not filas:
        return None
    if len(filas) != 1 or filas[0][0] not in (ENTORNO_DESARROLLO, ENTORNO_PRODUCCION):
        raise IdentidadNoVerificable
    return filas[0][0]


def _es_base_temporal_de_pruebas() -> bool:
    """Solo dentro del ejecutor de pruebas y sobre la base que este creó."""
    if modulo_activo() not in MODULOS_PRUEBAS or not hasattr(_TestState, "saved_data"):
        return False
    if connection.vendor == "sqlite":
        return connection.is_in_memory_db()
    nombre = str(connection.settings_dict.get("NAME") or "")
    return connection.vendor == "postgresql" and nombre.startswith("test_")


def _rechazar(comando: str, motivo: str) -> None:
    raise CommandError(
        f"{comando} solo puede ejecutarse en desarrollo o pruebas: {motivo} "
        "No se escribió ningún dato."
    )


def exigir_entorno_de_demostracion(comando: str) -> None:
    """Detiene el comando, antes de escribir, si el entorno o el destino no lo admiten."""
    if existe_marca_produccion() or modulo_activo() not in MODULOS_PERMITIDOS:
        _rechazar(comando, "este entorno no permite datos de demostración.")
    try:
        identidad = leer_identidad_base()
    except IdentidadNoVerificable:
        _rechazar(comando, "no se pudo verificar la identidad de la base.")
    if identidad == ENTORNO_PRODUCCION:
        _rechazar(comando, "la base está registrada como producción.")
    if identidad == ENTORNO_DESARROLLO or _es_base_temporal_de_pruebas():
        return
    _rechazar(
        comando,
        "la base no tiene identidad de desarrollo. Si es una base local de "
        "desarrollo, regístrela con: python manage.py registrar_entorno_bd "
        "desarrollo --confirmar-base <nombre de la base>.",
    )
