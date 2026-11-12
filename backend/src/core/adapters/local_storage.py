"""Adaptador de almacenamiento local privado (T023/T024; ADR-005).

Almacena archivos PDF en volumen privado fuera de la carpeta pública web.
Estructura: /media/private/expedientes/{year}/{expediente_id}/

I-3 (archivos huérfanos):

- Escritura atómica (H-I3-03): el contenido se escribe en un temporal del
  mismo directorio (`PREFIJO_TEMPORAL`) y se publica con un enlace que falla
  si el destino existe; si algo falla, el temporal se borra. Nunca queda un
  archivo final parcial y nunca se sobrescribe un archivo existente.
- Nombre físico acotado en bytes (H-I3-04): `nombre_original` no cambia; solo
  el nombre en disco se limita a `MAX_BYTES_NOMBRE_FISICO` conservando la
  extensión.
- Compensación (H-I3-01/02): `compensacion_de_archivos()` borra, si la
  operación falla, únicamente los archivos que ella misma creó.
"""

import contextlib
import errno
import hashlib
import logging
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import BinaryIO

from django.conf import settings
from django.core.files.storage import FileSystemStorage

logger = logging.getLogger(__name__)

# Prefijo de los temporales de escritura: `reconciliar_archivos` los reconoce.
PREFIJO_TEMPORAL = ".tmp-"
# Límite del nombre físico (no de la ruta). Deja margen bajo el límite de
# 255 bytes del sistema de archivos para el sufijo de `get_available_name()`.
MAX_BYTES_NOMBRE_FISICO = 180
_MAX_BYTES_EXTENSION = 16
_TAMANIO_BLOQUE = 64 * 1024
# Sistemas de archivos sin enlaces duros: se usa reserva exclusiva + rename.
_ERRNOS_SIN_ENLACE = {errno.EPERM, errno.EOPNOTSUPP, errno.ENOTSUP, errno.EMLINK}


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


def _acotar_bytes(texto: str, max_bytes: int) -> str:
    """Recorta `texto` a `max_bytes` en UTF-8 sin partir caracteres."""
    return texto.encode("utf-8")[:max_bytes].decode("utf-8", errors="ignore")


def generar_ruta_archivo(expediente_id: str, nombre_original: str) -> str:
    """Genera la ruta de almacenamiento privado para un archivo.

    Estructura: expedientes/{year}/{expediente_id}/{timestamp}_{nombre_original}

    El nombre físico se acota a `MAX_BYTES_NOMBRE_FISICO` bytes conservando la
    extensión (H-I3-04); `nombre_original` se guarda aparte, sin cambios.
    """
    now = datetime.now()
    year = now.year
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    # Sanitizar nombre de archivo
    nombre_seguro = "".join(c for c in nombre_original if c.isalnum() or c in "._-")
    base, extension = os.path.splitext(nombre_seguro)
    extension = _acotar_bytes(extension, _MAX_BYTES_EXTENSION)
    disponible = (
        MAX_BYTES_NOMBRE_FISICO
        - len(f"{timestamp}_".encode())
        - len(extension.encode("utf-8"))
    )
    nombre_fisico = f"{timestamp}_{_acotar_bytes(base, disponible)}{extension}"
    return f"expedientes/{year}/{expediente_id}/{nombre_fisico}"


def _bloques(contenido):
    if hasattr(contenido, "chunks"):
        yield from contenido.chunks()
        return
    while True:
        bloque = contenido.read(_TAMANIO_BLOQUE)
        if not bloque:
            return
        yield bloque


def _publicar_sin_sobrescribir(temporal: str, destino: str) -> None:
    """Publica `temporal` en `destino`; FileExistsError si `destino` existe."""
    try:
        os.link(temporal, destino)
    except OSError as error:
        if isinstance(error, FileExistsError) or error.errno not in _ERRNOS_SIN_ENLACE:
            raise
        # Sin enlaces duros: reserva exclusiva del destino y rename atómico.
        descriptor = os.open(destino, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        os.close(descriptor)
        try:
            os.replace(temporal, destino)
        except BaseException:
            os.unlink(destino)
            raise


def _crear_directorio(storage: FileSystemStorage, directorio: str) -> None:
    """Crea el directorio respetando `directory_permissions_mode` (D-08).

    Mismo criterio que `FileSystemStorage._save()` de Django: si el modo está
    configurado (`FILE_UPLOAD_DIRECTORY_PERMISSIONS`), se aplica con un umask
    temporal; si no, se usan los permisos por defecto del proceso.
    """
    modo = storage.directory_permissions_mode
    if modo is None:
        os.makedirs(directorio, exist_ok=True)
        return
    umask_anterior = os.umask(0o777 & ~modo)
    try:
        os.makedirs(directorio, modo, exist_ok=True)
    finally:
        os.umask(umask_anterior)


def _escribir_atomico(storage: FileSystemStorage, nombre: str, contenido) -> str:
    """Escribe `contenido` en `nombre` sin parciales ni sobrescritura (H-I3-03).

    Si un paso posterior a la publicación falla (p. ej. `chmod`), el archivo
    publicado se borra antes de propagar el error (D-05): la operación nunca
    deja un archivo final cuya ruta no haya devuelto. Un fallo al borrar el
    temporal tras una publicación correcta no convierte el éxito en error: se
    registra y `reconciliar_archivos` lo listará como temporal.
    """
    destino = storage.path(nombre)
    directorio = os.path.dirname(destino)
    _crear_directorio(storage, directorio)
    descriptor, temporal = tempfile.mkstemp(prefix=PREFIJO_TEMPORAL, dir=directorio)
    publicado = None
    try:
        with os.fdopen(descriptor, "wb") as salida:
            for bloque in _bloques(contenido):
                salida.write(bloque)
            salida.flush()
            os.fsync(salida.fileno())
        while True:
            try:
                _publicar_sin_sobrescribir(temporal, destino)
            except FileExistsError:
                nombre = storage.get_available_name(nombre)
                destino = storage.path(nombre)
                continue
            publicado = destino
            break
        if storage.file_permissions_mode is not None:
            os.chmod(destino, storage.file_permissions_mode)
        return nombre.replace("\\", "/")
    except BaseException:
        if publicado is not None:
            try:
                os.unlink(publicado)
            except OSError:
                logger.warning(
                    "No se pudo retirar el archivo publicado tras un fallo: %s",
                    publicado,
                    exc_info=True,
                )
        raise
    finally:
        try:
            os.unlink(temporal)
        except FileNotFoundError:
            pass
        except OSError:
            logger.warning(
                "No se pudo eliminar el temporal de escritura %s",
                temporal,
                exc_info=True,
            )


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
    try:
        # Escritura atómica: sin fragmentos ni sobrescritura (I-3, H-I3-03)
        return _escribir_atomico(storage, ruta_relativa, file)
    finally:
        # Restaurar posición
        file.seek(pos_actual)


def obtener_ruta_absoluta(ruta_relativa: str) -> Path:
    """Obtiene la ruta absoluta en disco para un archivo guardado."""
    storage = PrivateMediaStorage()
    return Path(storage.path(ruta_relativa))


def archivo_existe(ruta_relativa: str) -> bool:
    """Verifica si un archivo existe en el almacenamiento privado."""
    storage = PrivateMediaStorage()
    return storage.exists(ruta_relativa)


def calcular_sha256(ruta_relativa: str, tamanio_bloque: int = 64 * 1024) -> str:
    """SHA-256 (hex) del archivo almacenado, leído por bloques (VULN-003).

    Lectura en streaming: no carga el archivo completo en memoria.
    """
    digest = hashlib.sha256()
    with open(obtener_ruta_absoluta(ruta_relativa), "rb") as fh:
        for bloque in iter(lambda: fh.read(tamanio_bloque), b""):
            digest.update(bloque)
    return digest.hexdigest()


def eliminar_archivo(ruta_relativa: str) -> bool:
    """Elimina un archivo del almacenamiento privado."""
    storage = PrivateMediaStorage()
    if storage.exists(ruta_relativa):
        storage.delete(ruta_relativa)
        return True
    return False


class ArchivosDeLaOperacion:
    """Registro de los archivos creados por una operación (I-3)."""

    def __init__(self):
        self._rutas: list[str] = []

    def guardar(self, file: BinaryIO, expediente_id: str, nombre_original: str) -> str:
        """Guarda con `guardar_archivo_privado()` y registra la ruta creada."""
        ruta = guardar_archivo_privado(
            file=file, expediente_id=expediente_id, nombre_original=nombre_original
        )
        self._rutas.append(ruta)
        return ruta

    def descartar(self) -> None:
        """Borra solo las rutas registradas; nunca otras."""
        storage = PrivateMediaStorage()
        for ruta in self._rutas:
            try:
                storage.delete(ruta)
            except OSError:
                logger.warning(
                    "No se pudo eliminar el archivo de una operación fallida: %s",
                    ruta,
                    exc_info=True,
                )
        self._rutas.clear()


@contextlib.contextmanager
def compensacion_de_archivos():
    """Compensa los archivos creados si la operación falla (H-I3-01/02).

    Debe envolver el bloque `transaction.atomic()` del servicio, de modo que
    también cubra un fallo al confirmar (*commit*)::

        with compensacion_de_archivos() as archivos, transaction.atomic():
            ruta = archivos.guardar(file, expediente_id, nombre_original)

    Invariante: sin `ATOMIC_REQUESTS`, esa transacción es la más externa en
    HTTP. Si el servicio se llamara dentro de otra transacción que revierte
    después, el archivo quedaría sin registro: lo detecta `reconciliar_archivos`.
    """
    archivos = ArchivosDeLaOperacion()
    try:
        yield archivos
    except BaseException:
        archivos.descartar()
        raise
