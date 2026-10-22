"""Adaptador de validación criptográfica de archivos PDF (T022; ADR-005).

Validación estricta en servidor:
- Tamaño máximo: 10 MB
- Magic bytes: %PDF-
- Hash SHA-256 para integridad

Principio C-006: almacenamiento privado, validación estricta en servidor.
"""

import hashlib
from typing import BinaryIO

from django.core.exceptions import ValidationError

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
PDF_MAGIC_BYTES = b"%PDF-"


class PDFValidationError(ValidationError):
    """Excepción específica para errores de validación PDF."""

    def __init__(self, message: str, code: str = "invalid_pdf"):
        super().__init__(message, code=code)


def validar_tamano_archivo(file: BinaryIO) -> int:
    """Valida que el archivo no exceda 10 MB y retorna su tamaño en bytes.

    Args:
        file: Archivo binario abierto (seekable).

    Returns:
        Tamaño del archivo en bytes.

    Raises:
        PDFValidationError: Si el archivo excede 10 MB.
    """
    # Guardar posición actual
    pos_actual = file.tell()

    # Mover al final para obtener tamaño
    file.seek(0, 2)
    tamanio = file.tell()

    # Restaurar posición
    file.seek(pos_actual)

    if tamanio > MAX_FILE_SIZE:
        raise PDFValidationError(
            f"El archivo excede el tamaño máximo permitido de 10 MB "
            f"(tamaño actual: {tamanio / (1024 * 1024):.2f} MB).",
            code="file_too_large",
        )

    return tamanio


def validar_magic_bytes(file: BinaryIO) -> bool:
    """Valida que el archivo tenga los magic bytes de PDF (%PDF-).

    Args:
        file: Archivo binario abierto (seekable).

    Returns:
        True si los magic bytes son válidos.

    Raises:
        PDFValidationError: Si los magic bytes no corresponden a PDF.
    """
    pos_actual = file.tell()

    # Leer los primeros 5 bytes
    file.seek(0)
    header = file.read(5)

    # Restaurar posición
    file.seek(pos_actual)

    if header != PDF_MAGIC_BYTES:
        raise PDFValidationError(
            "El archivo no es un PDF válido: magic bytes inválidos. "
            f"Se esperaba '%PDF-', se recibió '{header.decode('latin-1', errors='replace')}'.",
            code="invalid_magic_bytes",
        )

    return True


def calcular_hash_sha256(file: BinaryIO) -> str:
    """Calcula el hash SHA-256 del archivo completo.

    Args:
        file: Archivo binario abierto (seekable).

    Returns:
        Hash SHA-256 en formato hexadecimal (64 caracteres).
    """
    pos_actual = file.tell()
    file.seek(0)

    hasher = hashlib.sha256()
    # Leer en chunks para archivos grandes
    for chunk in iter(lambda: file.read(8192), b""):
        hasher.update(chunk)

    file.seek(pos_actual)
    return hasher.hexdigest()


def validar_pdf_completo(file: BinaryIO) -> dict:
    """Ejecuta todas las validaciones PDF y retorna metadata.

    Args:
        file: Archivo binario abierto (seekable).

    Returns:
        Diccionario con metadata: tamanio_bytes, hash_sha256, tipo_mime.

    Raises:
        PDFValidationError: Si alguna validación falla.
    """
    tamanio = validar_tamano_archivo(file)
    validar_magic_bytes(file)
    hash_sha256 = calcular_hash_sha256(file)

    return {
        "tamanio_bytes": tamanio,
        "hash_sha256": hash_sha256,
        "tipo_mime": "application/pdf",
    }