"""Adaptador de almacenamiento local privado (T023/T024; ADR-005).

Almacena archivos PDF en volumen privado fuera de la carpeta pública web.
Estructura: /media/private/expedientes/{year}/{expediente_id}/
"""

import os
from datetime import datetime
from pathlib import Path
from typing import BinaryIO

from django.conf import settings
from django.core.files.storage import FileSystemStorage


class PrivateMediaStorage(FileSystemStorage):
    """Almacenamiento para archivos privados (no accesibles vía web directo)."""

    def __init__(self, *args, **kwargs):
        # Usar MEDIA_ROOT/private como base
        private_root = getattr(settings, "PRIVATE_MEDIA_ROOT", None)
        if private_root is None:
            private_root = settings.MEDIA_ROOT / "private"
        kwargs.setdefault("location", private_root)
        kwargs.setdefault("base_url", None)  # Sin URL pública
        super().__init__(*args, **kwargs)
        # Asegurar que base_url sea None (FileSystemStorage puede sobrescribirlo)
        self.base_url = None

    def url(self, name):
        """Los archivos privados no tienen URL pública directa."""
        raise NotImplementedError(
            "Los archivos en almacenamiento privado no tienen URL pública. "
            "Use el endpoint de descarga autorizada."
        )


def generar_ruta_archivo(expediente_id: str, nombre_original: str) -> str:
    """Genera la ruta de almacenamiento privado para un archivo.

    Estructura: expedientes/{year}/{expediente_id}/{timestamp}_{nombre_original}
    """
    now = datetime.now()
    year = now.year
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    # Sanitizar nombre de archivo
    nombre_seguro = "".join(c for c in nombre_original if c.isalnum() or c in "._-")
    return f"expedientes/{year}/{expediente_id}/{timestamp}_{nombre_seguro}"


def guardar_archivo_privado(
    file: BinaryIO,
    expediente_id: str,
    nombre_original: str,
) -> str:
    """Guarda un archivo en el almacenamiento privado y retorna la ruta relativa.

    Args:
        file: Archivo binario abierto (seekable).
        expediente_id: UUID del expediente.
        nombre_original: Nombre original del archivo subido.

    Returns:
        Ruta relativa del archivo guardado (desde MEDIA_ROOT/private).
    """
    storage = PrivateMediaStorage()
    ruta_relativa = generar_ruta_archivo(expediente_id, nombre_original)

    # Guardar posición actual
    pos_actual = file.tell()
    file.seek(0)

    # Guardar archivo
    ruta_guardada = storage.save(ruta_relativa, file)

    # Restaurar posición
    file.seek(pos_actual)

    return ruta_guardada


def obtener_ruta_absoluta(ruta_relativa: str) -> Path:
    """Obtiene la ruta absoluta en disco para un archivo guardado."""
    storage = PrivateMediaStorage()
    return Path(storage.path(ruta_relativa))


def archivo_existe(ruta_relativa: str) -> bool:
    """Verifica si un archivo existe en el almacenamiento privado."""
    storage = PrivateMediaStorage()
    return storage.exists(ruta_relativa)


def eliminar_archivo(ruta_relativa: str) -> bool:
    """Elimina un archivo del almacenamiento privado."""
    storage = PrivateMediaStorage()
    if storage.exists(ruta_relativa):
        storage.delete(ruta_relativa)
        return True
    return False