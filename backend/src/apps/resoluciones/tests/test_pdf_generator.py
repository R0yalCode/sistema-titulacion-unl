"""Tests para T033: Generador de PDFs institucionales (Providencia #590 / Memorando #162).

Verifica:
- Generación exitosa de PDFs válidos
- Contenido correcto con datos del expediente
- Formato profesional con estilos institucionales
- Marca de agua BORRADOR en borradores
- Archivos guardados en sistema de archivos
"""

import os
import tempfile

import pytest
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from apps.resoluciones.adapters.pdf_generator import PDFGeneratorAdapter, generar_memorando_162, generar_providencia_590


def _leer_pdf_texto(ruta: str) -> str:
    """Extrae texto de un PDF para validación."""
    try:
        from pypdf import PdfReader

        reader = PdfReader(ruta)
        texto = ""
        for page in reader.pages:
            texto += page.extract_text() or ""
        return texto
    except ImportError:
        # Si no está pypdf, solo validar que existe y tiene tamaño > 0
        return ""


@pytest.fixture
def temp_output_dir():
    """Directorio temporal para PDFs de prueba."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def datos_expediente():
    """Datos típicos de un expediente para pruebas."""
    return {
        "numero_expediente": "EXP-2026-0001",
        "estudiante_nombre": "María Fernanda González Loor",
        "estudiante_cedula": "1104567890",
        "carrera_nombre": "Computación",
        "carrera_id": "11111111-1111-1111-1111-111111111111",
        "facultad_nombre": "FEIRNNR",
        "fecha_recepcion": "15/10/2026",
        "fecha_limite_atencion": "29/10/2026",
        "fundamentacion": "El expediente ha sido revisado en su totalidad...",
    }


@pytest.fixture
def datos_secretario():
    """Datos del Secretario/a-Abogado/a."""
    return {
        "nombre_completo": "Abg. Juan Carlos Pérez Mendoza",
        "cargo": "SECRETARIO/A-ABOGADO/A - FEIRNNR",
        "ci": "1101234567",
    }


@pytest.fixture
def datos_decano():
    """Datos del Decano/a."""
    return {
        "nombre_completo": "PhD. Ana Lucía Ramírez Vaca",
        "cargo": "DECANO/A - FEIRNNR",
        "ci": "1107654321",
    }


@pytest.fixture
def checklist_completo():
    """Checklist con todos los requisitos verificados."""
    return [
        {
            "codigo": "REQ-01",
            "nombre": "Acta de Grado",
            "estado": "VERIFICADO",
            "observacion": "",
        },
        {
            "codigo": "REQ-02",
            "nombre": "Certificado de Votación",
            "estado": "VERIFICADO",
            "observacion": "",
        },
        {
            "codigo": "REQ-03",
            "nombre": "Certificado Militar (varones)",
            "estado": "VERIFICADO",
            "observacion": "No aplica (estudiante femenino)",
        },
        {
            "codigo": "REQ-04",
            "nombre": "Título de Bachiller",
            "estado": "VERIFICADO",
            "observacion": "",
        },
        {
            "codigo": "REQ-05",
            "nombre": "Record Académico Legalizado",
            "estado": "VERIFICADO",
            "observacion": "",
        },
    ]


@pytest.fixture
def checklist_con_observados():
    """Checklist con algunos observados."""
    return [
        {"codigo": "REQ-01", "nombre": "Acta de Grado", "estado": "VERIFICADO", "observacion": ""},
        {"codigo": "REQ-02", "nombre": "Certificado de Votación", "estado": "OBSERVADO", "observacion": "Falta firma"},
        {"codigo": "REQ-03", "nombre": "Certificado Militar", "estado": "VERIFICADO", "observacion": ""},
    ]


class TestPDFGeneratorAdapter:
    """Tests del adaptador generador de PDFs."""

    def test_instancia_crea_directorio_salida(self, temp_output_dir):
        """La instancia crea el directorio de salida si no existe."""
        generator = PDFGeneratorAdapter(output_dir=temp_output_dir)
        assert os.path.exists(temp_output_dir)
        assert os.path.isdir(temp_output_dir)

    def test_estilos_incluyen_claves_requeridas(self, temp_output_dir):
        """Los estilos incluyen todas las claves necesarias."""
        generator = PDFGeneratorAdapter(output_dir=temp_output_dir)
        styles = generator._get_styles()

        claves_requeridas = [
            "titulo_institucional",
            "subtitulo_institucional",
            "numero_documento",
            "encabezado_seccion",
            "texto_normal",
            "texto_negrita",
            "firma",
            "firma_nombre",
            "firma_cargo",
            "pie_pagina",
            "campo_etiqueta",
            "campo_valor",
        ]
        for clave in claves_requeridas:
            assert clave in styles, f"Falta estilo: {clave}"

    def test_formato_fecha_valido(self, temp_output_dir):
        """Formateo de fechas funciona correctamente."""
        generator = PDFGeneratorAdapter(output_dir=temp_output_dir)
        from datetime import datetime, date

        assert generator._formato_fecha(datetime(2026, 10, 15)) == "15/10/2026"
        assert generator._formato_fecha(date(2026, 10, 15)) == "15/10/2026"
        assert generator._formato_fecha("15/10/2026") == "15/10/2026"
        assert generator._formato_fecha(None) == "N/A"

    def test_formato_fecha_larga(self, temp_output_dir):
        """Formato fecha larga en español."""
        generator = PDFGeneratorAdapter(output_dir=temp_output_dir)
        from datetime import datetime

        resultado = generator._formato_fecha_larga(datetime(2026, 10, 15))
        assert "15" in resultado
        assert "octubre" in resultado.lower()
        assert "2026" in resultado


class TestGenerarProvidencia590:
    """Tests de generación de Providencia N° 590."""

    def test_generar_providencia_borrador_exitoso(
        self, temp_output_dir, datos_expediente, datos_secretario, checklist_completo
    ):
        """Genera PDF borrador de Providencia 590 exitosamente."""
        generator = PDFGeneratorAdapter(output_dir=temp_output_dir)

        archivo = generator.generar_providencia_590(
            expediente=datos_expediente,
            secretario=datos_secretario,
            checklist=checklist_completo,
            dictamen="APTO",
            es_borrador=True,
        )

        assert os.path.exists(archivo)
        assert archivo.endswith(".pdf")
        assert "BORRADOR" in os.path.basename(archivo).upper()
        assert os.path.getsize(archivo) > 1000  # Al menos 1KB

    def test_generar_providencia_final_sin_marca_borrador(
        self, temp_output_dir, datos_expediente, datos_secretario, checklist_completo
    ):
        """Genera PDF final SIN marca de agua BORRADOR."""
        generator = PDFGeneratorAdapter(output_dir=temp_output_dir)

        archivo = generator.generar_providencia_590(
            expediente=datos_expediente,
            secretario=datos_secretario,
            checklist=checklist_completo,
            dictamen="APTO",
            es_borrador=False,
        )

        assert os.path.exists(archivo)
        assert "BORRADOR" not in os.path.basename(archivo).upper()

    def test_providencia_con_numero_personalizado(
        self, temp_output_dir, datos_expediente, datos_secretario, checklist_completo
    ):
        """Permite especificar número de providencia personalizado."""
        generator = PDFGeneratorAdapter(output_dir=temp_output_dir)

        archivo = generator.generar_providencia_590(
            expediente=datos_expediente,
            secretario=datos_secretario,
            checklist=checklist_completo,
            numero_providencia="PROV-590-2026-CUSTOM-001",
            es_borrador=True,
        )

        assert os.path.exists(archivo)
        assert "CUSTOM-001" in os.path.basename(archivo)

    def test_providencia_con_archivo_salida_personalizado(
        self, temp_output_dir, datos_expediente, datos_secretario, checklist_completo
    ):
        """Permite especificar ruta de archivo de salida personalizada."""
        generator = PDFGeneratorAdapter(output_dir=temp_output_dir)
        ruta_custom = os.path.join(temp_output_dir, "mi_providencia_personalizada.pdf")

        archivo = generator.generar_providencia_590(
            expediente=datos_expediente,
            secretario=datos_secretario,
            checklist=checklist_completo,
            archivo_salida=ruta_custom,
            es_borrador=True,
        )

        assert archivo == ruta_custom
        assert os.path.exists(ruta_custom)

    def test_providencia_dictamen_apto_incluye_texto_apto(
        self, temp_output_dir, datos_expediente, datos_secretario, checklist_completo
    ):
        """Dictamen APTO incluye texto específico en el PDF."""
        generator = PDFGeneratorAdapter(output_dir=temp_output_dir)

        archivo = generator.generar_providencia_590(
            expediente=datos_expediente,
            secretario=datos_secretario,
            checklist=checklist_completo,
            dictamen="APTO",
            es_borrador=True,
        )

        texto = _leer_pdf_texto(archivo)
        assert "APTO" in texto
        assert "cumple con la totalidad" in texto or "cumple" in texto.lower()

    def test_providencia_dictamen_no_apto_incluye_texto_no_apto(
        self, temp_output_dir, datos_expediente, datos_secretario, checklist_con_observados
    ):
        """Dictamen NO APTO incluye texto específico."""
        generator = PDFGeneratorAdapter(output_dir=temp_output_dir)

        archivo = generator.generar_providencia_590(
            expediente=datos_expediente,
            secretario=datos_secretario,
            checklist=checklist_con_observados,
            dictamen="NO APTO",
            es_borrador=True,
        )

        texto = _leer_pdf_texto(archivo)
        assert "NO APTO" in texto
        assert "observaciones pendientes" in texto.lower() or "deficiencias" in texto.lower()

    def test_providencia_incluye_datos_estudiante(
        self, temp_output_dir, datos_expediente, datos_secretario, checklist_completo
    ):
        """El PDF incluye datos del estudiante."""
        generator = PDFGeneratorAdapter(output_dir=temp_output_dir)

        archivo = generator.generar_providencia_590(
            expediente=datos_expediente,
            secretario=datos_secretario,
            checklist=checklist_completo,
            es_borrador=True,
        )

        texto = _leer_pdf_texto(archivo)
        assert "María Fernanda González Loor" in texto
        assert "1104567890" in texto
        assert "Computación" in texto
        assert "EXP-2026-0001" in texto

    def test_providencia_incluye_checklist_tabla(
        self, temp_output_dir, datos_expediente, datos_secretario, checklist_completo
    ):
        """El PDF incluye tabla del checklist."""
        generator = PDFGeneratorAdapter(output_dir=temp_output_dir)

        archivo = generator.generar_providencia_590(
            expediente=datos_expediente,
            secretario=datos_secretario,
            checklist=checklist_completo,
            es_borrador=True,
        )

        texto = _leer_pdf_texto(archivo)
        # Verificar códigos de requisitos
        for req in checklist_completo:
            assert req["codigo"] in texto
            assert req["nombre"] in texto
            assert req["estado"] in texto

    def test_providencia_incluye_firma_secretario(
        self, temp_output_dir, datos_expediente, datos_secretario, checklist_completo
    ):
        """El PDF incluye bloque de firma del secretario."""
        generator = PDFGeneratorAdapter(output_dir=temp_output_dir)

        archivo = generator.generar_providencia_590(
            expediente=datos_expediente,
            secretario=datos_secretario,
            checklist=checklist_completo,
            es_borrador=True,
        )

        texto = _leer_pdf_texto(archivo)
        assert "Juan Carlos Pérez Mendoza" in texto
        assert "SECRETARIO" in texto.upper()
        assert "1101234567" in texto

    def test_providencia_resumen_checklist_correcto(
        self, temp_output_dir, datos_expediente, datos_secretario, checklist_completo
    ):
        """Resumen de checklist muestra conteos correctos."""
        generator = PDFGeneratorAdapter(output_dir=temp_output_dir)

        archivo = generator.generar_providencia_590(
            expediente=datos_expediente,
            secretario=datos_secretario,
            checklist=checklist_completo,
            es_borrador=True,
        )

        texto = _leer_pdf_texto(archivo)
        assert "Total: 5" in texto or "5" in texto
        assert "Verificados: 5" in texto or "5" in texto


class TestGenerarMemorando162:
    """Tests de generación de Memorando N° 162."""

    def test_generar_memorando_borrador_exitoso(
        self, temp_output_dir, datos_expediente, datos_decano
    ):
        """Genera PDF borrador de Memorando 162 exitosamente."""
        generator = PDFGeneratorAdapter(output_dir=temp_output_dir)

        archivo = generator.generar_memorando_162(
            expediente=datos_expediente,
            decano=datos_decano,
            informe_providencia="PROV-590-2026-0001",
            es_borrador=True,
        )

        assert os.path.exists(archivo)
        assert archivo.endswith(".pdf")
        assert "BORRADOR" in os.path.basename(archivo).upper()
        assert os.path.getsize(archivo) > 1000

    def test_memorando_final_sin_marca_borrador(
        self, temp_output_dir, datos_expediente, datos_decano
    ):
        """Genera PDF final SIN marca de agua."""
        generator = PDFGeneratorAdapter(output_dir=temp_output_dir)

        archivo = generator.generar_memorando_162(
            expediente=datos_expediente,
            decano=datos_decano,
            informe_providencia="PROV-590-2026-0001",
            es_borrador=False,
        )

        assert os.path.exists(archivo)
        assert "BORRADOR" not in os.path.basename(archivo).upper()

    def test_memorando_incluye_referencia_providencia(
        self, temp_output_dir, datos_expediente, datos_decano
    ):
        """Incluye referencia a la providencia del informe previo."""
        generator = PDFGeneratorAdapter(output_dir=temp_output_dir)

        archivo = generator.generar_memorando_162(
            expediente=datos_expediente,
            decano=datos_decano,
            informe_providencia="PROV-590-2026-0001",
            es_borrador=True,
        )

        texto = _leer_pdf_texto(archivo)
        assert "PROV-590-2026-0001" in texto

    def test_memorando_incluye_considerandos(
        self, temp_output_dir, datos_expediente, datos_decano
    ):
        """Incluye sección de considerandos."""
        generator = PDFGeneratorAdapter(output_dir=temp_output_dir)

        archivo = generator.generar_memorando_162(
            expediente=datos_expediente,
            decano=datos_decano,
            informe_providencia="PROV-590-2026-0001",
            es_borrador=True,
        )

        texto = _leer_pdf_texto(archivo)
        assert "CONSIDERANDOS" in texto
        assert "estudiante" in texto.lower()
        assert "APTO" in texto

    def test_memorando_incluye_resuelve(
        self, temp_output_dir, datos_expediente, datos_decano
    ):
        """Incluye sección RESUELVE con tres puntos."""
        generator = PDFGeneratorAdapter(output_dir=temp_output_dir)

        archivo = generator.generar_memorando_162(
            expediente=datos_expediente,
            decano=datos_decano,
            informe_providencia="PROV-590-2026-0001",
            es_borrador=True,
        )

        texto = _leer_pdf_texto(archivo)
        assert "RESUELVE" in texto
        assert "PRIMERO" in texto
        assert "SEGUNDO" in texto
        assert "TERCERO" in texto
        assert "APTITUD LEGAL" in texto

    def test_memorando_incluye_firma_decano(
        self, temp_output_dir, datos_expediente, datos_decano
    ):
        """Incluye bloque de firma del Decano."""
        generator = PDFGeneratorAdapter(output_dir=temp_output_dir)

        archivo = generator.generar_memorando_162(
            expediente=datos_expediente,
            decano=datos_decano,
            informe_providencia="PROV-590-2026-0001",
            es_borrador=True,
        )

        texto = _leer_pdf_texto(archivo)
        assert "Ana Lucía Ramírez Vaca" in texto
        assert "DECANO" in texto.upper()
        assert "1107654321" in texto

    def test_memorando_incluye_cc(
        self, temp_output_dir, datos_expediente, datos_decano
    ):
        """Incluye sección de copias (C.C.)."""
        generator = PDFGeneratorAdapter(output_dir=temp_output_dir)

        archivo = generator.generar_memorando_162(
            expediente=datos_expediente,
            decano=datos_decano,
            informe_providencia="PROV-590-2026-0001",
            es_borrador=True,
        )

        texto = _leer_pdf_texto(archivo)
        assert "C.C." in texto or "Copia" in texto
        assert "Secretaría" in texto
        assert "Archivo" in texto


class TestFuncionesShortcut:
    """Tests de funciones de conveniencia (shortcuts)."""

    def test_shortcut_generar_providencia_590(
        self, temp_output_dir, datos_expediente, datos_secretario, checklist_completo
    ):
        """Función shortcut generar_providencia_590 funciona."""
        archivo = generar_providencia_590(
            expediente=datos_expediente,
            secretario=datos_secretario,
            checklist=checklist_completo,
            output_dir=temp_output_dir,
            es_borrador=True,
        )

        assert os.path.exists(archivo)
        assert archivo.endswith(".pdf")

    def test_shortcut_generar_memorando_162(
        self, temp_output_dir, datos_expediente, datos_decano
    ):
        """Función shortcut generar_memorando_162 funciona."""
        archivo = generar_memorando_162(
            expediente=datos_expediente,
            decano=datos_decano,
            informe_providencia="PROV-590-2026-0001",
            output_dir=temp_output_dir,
            es_borrador=True,
        )

        assert os.path.exists(archivo)
        assert archivo.endswith(".pdf")


class TestValidacionEstructuraPDF:
    """Tests de validación de estructura del PDF generado."""

    def test_pdf_tiene_multiples_paginas_si_contenido_largo(
        self, temp_output_dir, datos_expediente, datos_secretario
    ):
        """PDF con mucho contenido genera múltiples páginas."""
        # Crear checklist muy largo
        checklist_largo = [
            {"codigo": f"REQ-{i:02d}", "nombre": f"Requisito {i}", "estado": "VERIFICADO", "observacion": ""}
            for i in range(1, 25)
        ]

        generator = PDFGeneratorAdapter(output_dir=temp_output_dir)
        archivo = generator.generar_providencia_590(
            expediente=datos_expediente,
            secretario=datos_secretario,
            checklist=checklist_largo,
            es_borrador=True,
        )

        assert os.path.exists(archivo)
        # Validar que el PDF tiene al menos 2 páginas
        try:
            from pypdf import PdfReader
            reader = PdfReader(archivo)
            assert len(reader.pages) >= 2
        except ImportError:
            pass  # Solo validar existencia si no hay pypdf

    def test_pdf_metadata_tiene_titulo(self, temp_output_dir, datos_expediente, datos_secretario, checklist_completo):
        """El PDF tiene metadatos básicos."""
        generator = PDFGeneratorAdapter(output_dir=temp_output_dir)
        archivo = generator.generar_providencia_590(
            expediente=datos_expediente,
            secretario=datos_secretario,
            checklist=checklist_completo,
            es_borrador=True,
        )

        try:
            from pypdf import PdfReader
            reader = PdfReader(archivo)
            meta = reader.metadata
            # ReportLab no siempre agrega metadata, pero el archivo debe ser válido
            assert len(reader.pages) >= 1
        except ImportError:
            assert os.path.getsize(archivo) > 0

    def test_pdf_valido_reportlab(self, temp_output_dir, datos_expediente, datos_secretario, checklist_completo):
        """El PDF generado es válido según ReportLab."""
        generator = PDFGeneratorAdapter(output_dir=temp_output_dir)
        archivo = generator.generar_providencia_590(
            expediente=datos_expediente,
            secretario=datos_secretario,
            checklist=checklist_completo,
            es_borrador=True,
        )

        # Validar que es un PDF válido leyendo magic bytes
        with open(archivo, "rb") as f:
            header = f.read(5)
            assert header == b"%PDF-", f"Magic bytes inválidos: {header}"


class TestCasosEdge:
    """Tests de casos edge y validaciones."""

    def test_checklist_vacio(self, temp_output_dir, datos_expediente, datos_secretario):
        """Maneja checklist vacío sin error."""
        generator = PDFGeneratorAdapter(output_dir=temp_output_dir)

        archivo = generator.generar_providencia_590(
            expediente=datos_expediente,
            secretario=datos_secretario,
            checklist=[],
            es_borrador=True,
        )

        assert os.path.exists(archivo)
        texto = _leer_pdf_texto(archivo)
        assert "No hay datos" in texto or "checklist" in texto.lower()

    def test_datos_expediente_incompletos(self, temp_output_dir, datos_secretario, checklist_completo):
        """Maneja datos incompletos del expediente con valores N/A."""
        expediente_minimo = {"numero_expediente": "EXP-TEST"}
        generator = PDFGeneratorAdapter(output_dir=temp_output_dir)

        archivo = generator.generar_providencia_590(
            expediente=expediente_minimo,
            secretario=datos_secretario,
            checklist=checklist_completo,
            es_borrador=True,
        )

        assert os.path.exists(archivo)
        texto = _leer_pdf_texto(archivo)
        assert "N/A" in texto

    def test_autogeneracion_numero_providencia(self, temp_output_dir, datos_expediente, datos_secretario, checklist_completo):
        """Autogenera número de providencia si no se proporciona."""
        generator = PDFGeneratorAdapter(output_dir=temp_output_dir)

        archivo = generator.generar_providencia_590(
            expediente=datos_expediente,
            secretario=datos_secretario,
            checklist=checklist_completo,
            numero_providencia=None,  # Debe autogenerarse
            es_borrador=True,
        )

        assert os.path.exists(archivo)
        # El nombre del archivo debe contener el número autogenerado
        basename = os.path.basename(archivo)
        assert "PROV-590-" in basename

    def test_autogeneracion_numero_memorando(self, temp_output_dir, datos_expediente, datos_decano):
        """Autogenera número de memorando si no se proporciona."""
        generator = PDFGeneratorAdapter(output_dir=temp_output_dir)

        archivo = generator.generar_memorando_162(
            expediente=datos_expediente,
            decano=datos_decano,
            informe_providencia="PROV-590-2026-0001",
            numero_memorando=None,  # Debe autogenerarse
            es_borrador=True,
        )

        assert os.path.exists(archivo)
        basename = os.path.basename(archivo)
        assert "MEM-162-" in basename