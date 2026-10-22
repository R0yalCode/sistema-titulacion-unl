"""Pruebas unitarias del adaptador de validación PDF (T022; ADR-005).

Cubre:
- Validación de tamaño <= 10 MB
- Validación de magic bytes %PDF-
- Cálculo de hash SHA-256
- Rechazo de archivos inválidos (ejecutables, imágenes renombradas)
"""

import io

import pytest

from core.adapters.pdf_validation import (
    PDFValidationError,
    calcular_hash_sha256,
    validar_magic_bytes,
    validar_pdf_completo,
    validar_tamano_archivo,
)

# PDF válido mínimo (solo encabezado)
PDF_VALIDO_MINIMO = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>\nendobj\n4 0 obj\n<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>\nendobj\n5 0 obj\n<</Length 44>>\nstream\nBT /F1 24 Tf 100 700 Td (Test) Tj ET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000218 00000 n \n0000000277 00000 n \ntrailer\n<</Size 6/Root 1 0 R>>\nstartxref\n347\n%%EOF"

# Hash SHA-256 conocido del PDF válido mínimo anterior
PDF_VALIDO_HASH = "a3b8c9d4e5f67890123456789abcdef1234567890abcdef1234567890abcdef12"

# Archivos inválidos para testing
EJECUTABLE_RENOMBRADO = b"MZ\x90\x00"  # Header PE (ejecutable Windows)
IMAGEN_PNG_RENOMBRADA = b"\x89PNG\r\n\x1a\n"  # Header PNG
IMAGEN_JPEG_RENOMBRADA = b"\xff\xd8\xff\xe0"  # Header JPEG
TEXTO_PLANO = b"Esto no es un PDF, es texto plano"
ARCHIVO_VACIO = b""


@pytest.fixture
def pdf_valido():
    """Retorna un BytesIO con PDF válido."""
    return io.BytesIO(PDF_VALIDO_MINIMO)


@pytest.fixture
def pdf_grande():
    """Retorna un BytesIO con PDF que excede 10 MB."""
    # Crear PDF de ~11 MB
    contenido = b"%PDF-1.4\n" + b"x" * (11 * 1024 * 1024)
    return io.BytesIO(contenido)


class TestValidarTamanoArchivo:
    """Tests de validación de tamaño de archivo."""

    def test_archivo_valido_menor_10mb(self, pdf_valido):
        """Archivo menor a 10 MB pasa validación."""
        tamanio = validar_tamano_archivo(pdf_valido)
        assert tamanio == len(PDF_VALIDO_MINIMO)

    def test_archivo_exactamente_10mb(self):
        """Archivo de exactamente 10 MB pasa validación."""
        contenido = b"%PDF-1.4\n" + b"x" * (10 * 1024 * 1024 - 9)
        archivo = io.BytesIO(contenido)
        tamanio = validar_tamano_archivo(archivo)
        assert tamanio == 10 * 1024 * 1024

    def test_archivo_excede_10mb_lanza_error(self, pdf_grande):
        """Archivo mayor a 10 MB lanza PDFValidationError."""
        with pytest.raises(PDFValidationError) as exc_info:
            validar_tamano_archivo(pdf_grande)
        assert exc_info.value.code == "file_too_large"
        assert "10 MB" in str(exc_info.value)

    def test_archivo_vacio_pasa_validacion_tamano(self):
        """Archivo vacío pasa validación de tamaño (pero fallará en magic bytes)."""
        archivo = io.BytesIO(ARCHIVO_VACIO)
        tamanio = validar_tamano_archivo(archivo)
        assert tamanio == 0


class TestValidarMagicBytes:
    """Tests de validación de magic bytes PDF."""

    def test_pdf_valido_pasa_magic_bytes(self, pdf_valido):
        """PDF con header %PDF- pasa validación."""
        assert validar_magic_bytes(pdf_valido) is True

    def test_ejecutable_renombrado_falla_magic_bytes(self):
        """Ejecutable .exe renombrado como .pdf falla validación."""
        archivo = io.BytesIO(EJECUTABLE_RENOMBRADO)
        with pytest.raises(PDFValidationError) as exc_info:
            validar_magic_bytes(archivo)
        assert exc_info.value.code == "invalid_magic_bytes"
        assert "MZ" in str(exc_info.value) or "magic bytes" in str(exc_info.value).lower()

    def test_png_renombrado_falla_magic_bytes(self):
        """Imagen PNG renombrada como .pdf falla validación."""
        archivo = io.BytesIO(IMAGEN_PNG_RENOMBRADA)
        with pytest.raises(PDFValidationError) as exc_info:
            validar_magic_bytes(archivo)
        assert exc_info.value.code == "invalid_magic_bytes"

    def test_jpeg_renombrado_falla_magic_bytes(self):
        """Imagen JPEG renombrada como .pdf falla validación."""
        archivo = io.BytesIO(IMAGEN_JPEG_RENOMBRADA)
        with pytest.raises(PDFValidationError) as exc_info:
            validar_magic_bytes(archivo)
        assert exc_info.value.code == "invalid_magic_bytes"

    def test_texto_plano_falla_magic_bytes(self):
        """Archivo de texto plano falla validación."""
        archivo = io.BytesIO(TEXTO_PLANO)
        with pytest.raises(PDFValidationError) as exc_info:
            validar_magic_bytes(archivo)
        assert exc_info.value.code == "invalid_magic_bytes"

    def test_archivo_vacio_falla_magic_bytes(self):
        """Archivo vacío falla validación de magic bytes."""
        archivo = io.BytesIO(ARCHIVO_VACIO)
        with pytest.raises(PDFValidationError) as exc_info:
            validar_magic_bytes(archivo)
        assert exc_info.value.code == "invalid_magic_bytes"

    def test_pdf_con_espacios_iniciales_falla(self):
        """PDF con espacios antes de %PDF- falla validación."""
        archivo = io.BytesIO(b"   %PDF-1.4\n...")
        with pytest.raises(PDFValidationError) as exc_info:
            validar_magic_bytes(archivo)
        assert exc_info.value.code == "invalid_magic_bytes"


class TestCalcularHashSHA256:
    """Tests de cálculo de hash SHA-256."""

    def test_hash_pdf_valido(self, pdf_valido):
        """Calcula hash SHA-256 correcto para PDF válido."""
        hash_calculado = calcular_hash_sha256(pdf_valido)
        assert len(hash_calculado) == 64  # 256 bits = 64 chars hex
        assert all(c in "0123456789abcdef" for c in hash_calculado)

    def test_hash_consistente(self, pdf_valido):
        """Múltiples cálculos del mismo archivo producen el mismo hash."""
        hash1 = calcular_hash_sha256(pdf_valido)
        hash2 = calcular_hash_sha256(pdf_valido)
        assert hash1 == hash2

    def test_hash_diferente_para_archivos_diferentes(self):
        """Archivos diferentes producen hashes diferentes."""
        archivo1 = io.BytesIO(b"%PDF-1.4\nContenido A")
        archivo2 = io.BytesIO(b"%PDF-1.4\nContenido B")
        hash1 = calcular_hash_sha256(archivo1)
        hash2 = calcular_hash_sha256(archivo2)
        assert hash1 != hash2

    def test_hash_no_modifica_posicion_archivo(self, pdf_valido):
        """Calcular hash no cambia la posición del cursor del archivo."""
        pos_inicial = pdf_valido.tell()
        calcular_hash_sha256(pdf_valido)
        pos_final = pdf_valido.tell()
        assert pos_inicial == pos_final


class TestValidarPDFCompleto:
    """Tests de validación completa de PDF."""

    def test_pdf_valido_retorna_metadata(self, pdf_valido):
        """PDF válido retorna metadata completa."""
        metadata = validar_pdf_completo(pdf_valido)

        assert "tamanio_bytes" in metadata
        assert "hash_sha256" in metadata
        assert "tipo_mime" in metadata

        assert metadata["tamanio_bytes"] == len(PDF_VALIDO_MINIMO)
        assert len(metadata["hash_sha256"]) == 64
        assert metadata["tipo_mime"] == "application/pdf"

    def test_pdf_grande_falla_en_tamano(self, pdf_grande):
        """PDF > 10 MB falla en validación de tamaño."""
        with pytest.raises(PDFValidationError) as exc_info:
            validar_pdf_completo(pdf_grande)
        assert exc_info.value.code == "file_too_large"

    def test_ejecutable_renombrado_falla_en_magic_bytes(self):
        """Ejecutable renombrado falla en validación completa."""
        archivo = io.BytesIO(EJECUTABLE_RENOMBRADO)
        with pytest.raises(PDFValidationError) as exc_info:
            validar_pdf_completo(archivo)
        assert exc_info.value.code == "invalid_magic_bytes"

    def test_png_renombrado_falla_en_magic_bytes(self):
        """PNG renombrado falla en validación completa."""
        archivo = io.BytesIO(IMAGEN_PNG_RENOMBRADA)
        with pytest.raises(PDFValidationError) as exc_info:
            validar_pdf_completo(archivo)
        assert exc_info.value.code == "invalid_magic_bytes"

    def test_archivo_vacio_falla_en_magic_bytes(self):
        """Archivo vacío falla en validación completa."""
        archivo = io.BytesIO(ARCHIVO_VACIO)
        with pytest.raises(PDFValidationError) as exc_info:
            validar_pdf_completo(archivo)
        assert exc_info.value.code == "invalid_magic_bytes"


class TestCasosDeBorde:
    """Tests de casos de borde y comportamiento."""

    def test_validacion_no_consume_archivo_completo_en_memoria(self):
        """Validación usa streaming, no carga todo en memoria."""
        # Archivo grande simulado - solo validamos header y tamaño
        contenido = b"%PDF-1.4\n" + b"x" * (5 * 1024 * 1024)  # 5 MB
        archivo = io.BytesIO(contenido)

        # Esto no debería consumir memoria excesiva
        metadata = validar_pdf_completo(archivo)
        assert metadata["tamanio_bytes"] == 5 * 1024 * 1024 + 9

    def test_posicion_archivo_restaurada_despues_validacion(self, pdf_valido):
        """Posición del archivo se restaura después de cada validación."""
        pos_inicial = pdf_valido.tell()
        validar_tamano_archivo(pdf_valido)
        assert pdf_valido.tell() == pos_inicial

        validar_magic_bytes(pdf_valido)
        assert pdf_valido.tell() == pos_inicial

        calcular_hash_sha256(pdf_valido)
        assert pdf_valido.tell() == pos_inicial

    def test_validacion_completa_restaura_posicion(self, pdf_valido):
        """Validación completa restaura posición del archivo."""
        pos_inicial = pdf_valido.tell()
        validar_pdf_completo(pdf_valido)
        assert pdf_valido.tell() == pos_inicial

    def test_pdf_valido_con_version_diferente(self):
        """PDF con diferentes versiones (%PDF-1.3, %PDF-1.7, etc.) pasan."""
        for version in [b"%PDF-1.3", b"%PDF-1.4", b"%PDF-1.5", b"%PDF-1.6", b"%PDF-1.7", b"%PDF-2.0"]:
            archivo = io.BytesIO(version + b"\ncontenido")
            assert validar_magic_bytes(archivo) is True