"""Adaptador generador de PDFs institucionales (T033; RF-010, Plantillas #590 / #162).

Genera borradores profesionales de:
- Providencia N° 590 (Informe de Aptitud Legal) - Secretaría-Abogacía
- Memorando N° 162 (Declaratoria de Aptitud) - Decanato

Usa ReportLab para maquetado programático sin dependencias externas pesadas.
"""

import os
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class PDFGeneratorAdapter:
    """Generador de PDFs institucionales para resoluciones UNL-FEIRNNR."""

    # Colores institucionales UNL
    COLOR_UNL_AZUL = colors.HexColor("#003366")
    COLOR_UNL_DORADO = colors.HexColor("#C8A040")
    COLOR_GRIS_CLARO = colors.HexColor("#F0F0F0")
    COLOR_GRIS_MEDIO = colors.HexColor("#CCCCCC")
    COLOR_NEGRO = colors.black
    COLOR_BLANCO = colors.white

    # Rutas de plantillas (se crean si no existen)
    PLANTILLAS_DIR = os.path.join(os.path.dirname(__file__), "plantillas")

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir or "/media/private/resoluciones"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.PLANTILLAS_DIR, exist_ok=True)

    # ============================================================
    # ESTILOS BASE
    # ============================================================

    def _get_styles(self) -> Dict[str, ParagraphStyle]:
        """Retorna diccionario de estilos reutilizables."""
        styles = getSampleStyleSheet()

        return {
            "titulo_institucional": ParagraphStyle(
                "TituloInstitucional",
                parent=styles["Title"],
                fontName="Helvetica-Bold",
                fontSize=14,
                leading=18,
                alignment=TA_CENTER,
                textColor=self.COLOR_UNL_AZUL,
                spaceAfter=4,
            ),
            "subtitulo_institucional": ParagraphStyle(
                "SubtituloInstitucional",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=10,
                leading=13,
                alignment=TA_CENTER,
                textColor=self.COLOR_UNL_AZUL,
                spaceAfter=2,
            ),
            "numero_documento": ParagraphStyle(
                "NumeroDocumento",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=12,
                leading=16,
                alignment=TA_CENTER,
                textColor=self.COLOR_UNL_DORADO,
                spaceBefore=12,
                spaceAfter=12,
            ),
            "encabezado_seccion": ParagraphStyle(
                "EncabezadoSeccion",
                parent=styles["Heading2"],
                fontName="Helvetica-Bold",
                fontSize=11,
                leading=14,
                textColor=self.COLOR_UNL_AZUL,
                spaceBefore=12,
                spaceAfter=6,
                borderWidth=0,
                borderPadding=0,
            ),
            "texto_normal": ParagraphStyle(
                "TextoNormal",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=10,
                leading=14,
                alignment=TA_JUSTIFY,
                spaceAfter=6,
            ),
            "texto_centrado": ParagraphStyle(
                "TextoCentrado",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=10,
                leading=14,
                alignment=TA_CENTER,
                spaceAfter=6,
            ),
            "texto_negrita": ParagraphStyle(
                "TextoNegrita",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=10,
                leading=14,
                alignment=TA_JUSTIFY,
                spaceAfter=6,
            ),
            "campo_valor": ParagraphStyle(
                "CampoValor",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=10,
                leading=14,
                leftIndent=20,
                spaceAfter=4,
            ),
            "campo_etiqueta": ParagraphStyle(
                "CampoEtiqueta",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=10,
                leading=14,
                leftIndent=20,
                spaceAfter=4,
                textColor=self.COLOR_UNL_AZUL,
            ),
            "firma": ParagraphStyle(
                "Firma",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=10,
                leading=14,
                alignment=TA_CENTER,
                spaceBefore=30,
            ),
            "firma_nombre": ParagraphStyle(
                "FirmaNombre",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=10,
                leading=14,
                alignment=TA_CENTER,
            ),
            "firma_cargo": ParagraphStyle(
                "FirmaCargo",
                parent=styles["Normal"],
                fontName="Helvetica-Oblique",
                fontSize=9,
                leading=12,
                alignment=TA_CENTER,
                textColor=colors.grey,
            ),
            "pie_pagina": ParagraphStyle(
                "PiePagina",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=7,
                leading=9,
                alignment=TA_CENTER,
                textColor=colors.grey,
            ),
            "borrador_marca": ParagraphStyle(
                "BorradorMarca",
                parent=styles["Normal"],
                fontName="Helvetica-BoldOblique",
                fontSize=48,
                leading=58,
                alignment=TA_CENTER,
                textColor=colors.HexColor("#FF000080"),  # Rojo semi-transparente
            ),
        }

    # ============================================================
    # COMPONENTES REUTILIZABLES
    # ============================================================

    def _build_header(self, styles: Dict[str, ParagraphStyle]) -> List:
        """Construye el encabezado institucional UNL-FEIRNNR."""
        elements = []

        # Logo placeholder + textos institucionales
        header_data = [
            [
                "",  # Placeholder para logo
                [
                    Paragraph(
                        "UNIVERSIDAD NACIONAL DE LOJA",
                        styles["titulo_institucional"],
                    ),
                    Paragraph(
                        "FACULTAD DE LA ENERGÍA, LAS INDUSTRIAS Y LOS RECURSOS NATURALES NO RENOVABLES",
                        styles["subtitulo_institucional"],
                    ),
                    Paragraph(
                        "CARRERA DE COMPUTACIÓN",
                        styles["subtitulo_institucional"],
                    ),
                    Paragraph(
                        "SECRETARÍA GENERAL DE ABOGACÍA / DECANATO",
                        styles["subtitulo_institucional"],
                    ),
                ],
            ]
        ]

        header_table = Table(header_data, colWidths=[3.5 * cm, 14 * cm])
        header_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (0, 0), (0, 0), "CENTER"),
                    ("ALIGN", (1, 0), (1, 0), "CENTER"),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("LINEBELOW", (0, 0), (-1, -1), 1.5, self.COLOR_UNL_AZUL),
                ]
            )
        )
        elements.append(header_table)
        elements.append(Spacer(1, 8))

        return elements

    def _build_linea_horizontal(self, color=None, width=1) -> HRFlowable:
        """Línea horizontal decorativa."""
        return HRFlowable(
            width="100%",
            thickness=width,
            color=color or self.COLOR_UNL_DORADO,
            spaceAfter=8,
            spaceBefore=4,
        )

    def _build_campo(self, etiqueta: str, valor: str, styles: Dict) -> Table:
        """Construye una fila etiqueta-valor formateada."""
        data = [[Paragraph(etiqueta, styles["campo_etiqueta"]), Paragraph(valor, styles["campo_valor"])]]
        table = Table(data, colWidths=[4.5 * cm, 13 * cm])
        table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        return table

    def _build_tabla_checklist(
        self, checklist_data: List[Dict], styles: Dict[str, ParagraphStyle]
    ) -> Table:
        """Construye tabla del checklist de requisitos."""
        # Encabezados
        headers = ["N°", "Código", "Requisito", "Estado", "Observaciones"]
        data = [headers]

        for i, item in enumerate(checklist_data, 1):
            estado_color = (
                colors.green if item.get("estado") == "VERIFICADO" else colors.red
            )
            estado_style = ParagraphStyle(
                "EstadoStyle", parent=styles["texto_normal"], textColor=estado_color
            )

            data.append(
                [
                    Paragraph(str(i), styles["texto_normal"]),
                    Paragraph(item.get("codigo", ""), styles["texto_normal"]),
                    Paragraph(item.get("nombre", ""), styles["texto_normal"]),
                    Paragraph(item.get("estado", ""), estado_style),
                    Paragraph(item.get("observacion", "-"), styles["texto_normal"]),
                ]
            )

        col_widths = [0.8 * cm, 2 * cm, 7 * cm, 2.5 * cm, 4.7 * cm]
        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    # Encabezado
                    ("BACKGROUND", (0, 0), (-1, 0), self.COLOR_UNL_AZUL),
                    ("TEXTCOLOR", (0, 0), (-1, 0), self.COLOR_BLANCO),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                    # Cuerpo
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 1), (-1, -1), 8),
                    ("ALIGN", (0, 0), (0, -1), "CENTER"),
                    ("ALIGN", (1, 0), (1, -1), "CENTER"),
                    ("ALIGN", (3, 0), (3, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    # Bordes
                    ("GRID", (0, 0), (-1, -1), 0.5, self.COLOR_GRIS_MEDIO),
                    ("BOX", (0, 0), (-1, -1), 1, self.COLOR_UNL_AZUL),
                    # Padding
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    # Filas alternadas
                    *[
                        ("BACKGROUND", (0, i), (-1, i), self.COLOR_GRIS_CLARO)
                        for i in range(2, len(data), 2)
                    ],
                ]
            )
        )
        return table

    def _build_firma_block(
        self,
        nombre: str,
        cargo: str,
        ci: Optional[str] = None,
        styles: Optional[Dict] = None,
    ) -> List:
        """Construye bloque de firma con línea y datos."""
        s = styles or self._get_styles()
        elements = []

        # Línea de firma
        elements.append(Spacer(1, 40))
        elements.append(
            Paragraph("________________________________________", s["firma"])
        )
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(nombre, s["firma_nombre"]))
        elements.append(Paragraph(cargo, s["firma_cargo"]))
        if ci:
            elements.append(Paragraph(f"C.I.: {ci}", s["firma_cargo"]))

        return elements

    def _build_footer(
        self,
        numero_documento: str,
        fecha: datetime,
        styles: Dict[str, ParagraphStyle],
    ) -> List:
        """Construye pie de página con metadatos."""
        elements = []
        elements.append(Spacer(1, 20))
        elements.append(self._build_linea_horizontal(self.COLOR_GRIS_MEDIO, 0.5))
        elements.append(
            Paragraph(
                f"Documento: {numero_documento} | Generado: {fecha.strftime('%d/%m/%Y %H:%M')} | UNL-FEIRNNR - Sistema de Titulación",
                styles["pie_pagina"],
            )
        )
        return elements

    def _build_marca_borrador(self, canvas, doc):
        """Dibuja marca de agua 'BORRADOR' en cada página."""
        canvas.saveState()
        canvas.setFont("Helvetica-BoldOblique", 60)
        canvas.setFillColorRGB(1, 0, 0, alpha=0.1)
        canvas.translate(A4[0] / 2, A4[1] / 2)
        canvas.rotate(45)
        canvas.drawCentredString(0, 0, "BORRADOR")
        canvas.restoreState()

    # ============================================================
    # GENERADORES PRINCIPALES
    # ============================================================

    def generar_providencia_590(
        self,
        expediente: Dict[str, Any],
        secretario: Dict[str, Any],
        checklist: List[Dict[str, Any]],
        dictamen: str = "APTO",
        numero_providencia: Optional[str] = None,
        archivo_salida: Optional[str] = None,
        es_borrador: bool = True,
    ) -> str:
        """
        Genera Providencia N° 590 (Informe de Aptitud Legal).

        Args:
            expediente: Dict con datos del expediente (numero_expediente, estudiante, fechas, etc.)
            secretario: Dict con datos del Secretario/a-Abogado/a (nombres, ci, cargo)
            checklist: Lista de dicts con requisitos verificados
            dictamen: "APTO" o "NO APTO"
            numero_providencia: Número de providencia (se autogenera si None)
            archivo_salida: Ruta completa del archivo PDF (se autogenera si None)
            es_borrador: Si True, agrega marca de agua "BORRADOR"

        Returns:
            Ruta absoluta del archivo PDF generado
        """
        styles = self._get_styles()
        elements = []

        # Autogenerar número si no se provee
        if not numero_providencia:
            anio = datetime.now().year
            numero_providencia = f"PROV-590-{anio}-{expediente.get('numero_expediente', '0000').split('-')[-1].zfill(4)}"

        if not archivo_salida:
            nombre_base = f"providencia_590_{numero_providencia.replace('/', '-').replace(' ', '_')}"
            if es_borrador:
                nombre_base += "_BORRADOR"
            archivo_salida = os.path.join(self.output_dir, f"{nombre_base}.pdf")

        # Crear documento
        doc = SimpleDocTemplate(
            archivo_salida,
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=1.5 * cm,
            bottomMargin=2 * cm,
        )

        # ===== ENCABEZADO INSTITUCIONAL =====
        elements.extend(self._build_header(styles))

        # ===== TÍTULO DEL DOCUMENTO =====
        elements.append(self._build_linea_horizontal())
        elements.append(
            Paragraph("PROVIDENCIA N° 590", styles["numero_documento"])
        )
        elements.append(
            Paragraph("INFORME DE APTITUD LEGAL PARA TITULACIÓN", styles["numero_documento"])
        )
        elements.append(self._build_linea_horizontal())

        # ===== DATOS DEL EXPEDIENTE =====
        elements.append(Paragraph("I. DATOS DEL EXPEDIENTE", styles["encabezado_seccion"]))

        campos_expediente = [
            ("N° Expediente:", expediente.get("numero_expediente", "N/A")),
            ("Estudiante:", expediente.get("estudiante_nombre", "N/A")),
            ("Cédula:", expediente.get("estudiante_cedula", "N/A")),
            ("Carrera:", expediente.get("carrera_nombre", "N/A")),
            ("Facultad:", "FEIRNNR"),
            ("Fecha Recepción:", self._formato_fecha(expediente.get("fecha_recepcion"))),
            ("Fecha Límite:", self._formato_fecha(expediente.get("fecha_limite_atencion"))),
        ]
        for etiqueta, valor in campos_expediente:
            elements.append(self._build_campo(etiqueta, valor, styles))

        # ===== BASE LEGAL =====
        elements.append(Paragraph("II. BASE LEGAL", styles["encabezado_seccion"]))
        elements.append(
            Paragraph(
                "El presente informe se emite en cumplimiento de lo dispuesto en el "
                "<b>Art. 235 del Reglamento de Régimen Académico (RRA-UNL)</b> y el "
                "<b>Art. 160 del Código Orgánico Administrativo (COA)</b>, "
                "que establecen el plazo de 8 días hábiles para la calificación de los "
                "requisitos de titulación y la obligatoriedad de emitir informe legal "
                "previa a la declaratoria de aptitud.",
                styles["texto_normal"],
            )
        )

        # ===== CHECKLIST DE REQUISITOS =====
        elements.append(
            Paragraph("III. ESTADO DEL CHECKLIST DE REQUISITOS (ART. 235 RRA-UNL)", styles["encabezado_seccion"])
        )

        if checklist:
            elements.append(self._build_tabla_checklist(checklist, styles))
        else:
            elements.append(Paragraph("No hay datos de checklist disponibles.", styles["texto_normal"]))

        # Resumen
        total = len(checklist)
        verificados = sum(1 for c in checklist if c.get("estado") == "VERIFICADO")
        observados = sum(1 for c in checklist if c.get("estado") == "OBSERVADO")
        pendientes = sum(1 for c in checklist if c.get("estado") == "PENDIENTE")

        elements.append(Spacer(1, 8))
        elements.append(
            Paragraph(
                f"<b>Resumen:</b> Total: {total} | Verificados: {verificados} | Observados: {observados} | Pendientes: {pendientes}",
                styles["texto_negrita"],
            )
        )

        # ===== DICTAMEN LEGAL =====
        elements.append(Paragraph("IV. DICTAMEN LEGAL", styles["encabezado_seccion"]))

        dictamen_color = colors.green if dictamen == "APTO" else colors.red
        dictamen_style = ParagraphStyle(
            "DictamenStyle",
            parent=styles["texto_negrita"],
            textColor=dictamen_color,
            fontSize=12,
            alignment=TA_CENTER,
        )

        elements.append(
            Paragraph(
                f"En virtud de la revisión documental efectuada y el análisis jurídico correspondiente, "
                f"este Despacho emite el siguiente dictamen:",
                styles["texto_normal"],
            )
        )
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(f"D I C T A M E N:  {dictamen}", dictamen_style))
        elements.append(Spacer(1, 10))

        if dictamen == "APTO":
            elements.append(
                Paragraph(
                    "El expediente cumple con la totalidad de los requisitos establecidos en el "
                    "Art. 235 del RRA-UNL, habiendo sido todos los requisitos verificados por el "
                    "Secretario/a-Abogado/a competente. No existen observaciones pendientes de subsanación. "
                    "En consecuencia, el expediente se encuentra en condiciones legales para proceder "
                    "a la emisión de la Declaratoria de Aptitud por parte del Decano/a de la Facultad.",
                    styles["texto_normal"],
                )
            )
        else:
            elements.append(
                Paragraph(
                    "El expediente presenta observaciones pendientes de resolución que impiden "
                    "la emisión de dictamen favorable. Se detallan las deficiencias en el checklist "
                    "anterior. El interesado deberá proceder a la subsanación correspondiente dentro "
                    "del plazo legal establecido.",
                    styles["texto_normal"],
                )
            )

        # ===== FUNDAMENTACIÓN (opcional, si viene en dictamen completo) =====
        if expediente.get("fundamentacion"):
            elements.append(Paragraph("V. FUNDAMENTACIÓN JURÍDICA", styles["encabezado_seccion"]))
            elements.append(
                Paragraph(expediente["fundamentacion"], styles["texto_normal"])
            )

        # ===== FIRMA =====
        elements.extend(
            self._build_firma_block(
                nombre=secretario.get("nombre_completo", "__________________________"),
                cargo=secretario.get("cargo", "SECRETARIO/A-ABOGADO/A"),
                ci=secretario.get("ci"),
                styles=styles,
            )
        )

        elements.append(Spacer(1, 15))
        elements.append(
            Paragraph(
                f"Loja, {self._formato_fecha_larga(datetime.now())}",
                styles["texto_centrado"],
            )
        )

        # ===== PIE DE PÁGINA =====
        elements.extend(self._build_footer(numero_providencia, datetime.now(), styles))

        # Construir PDF
        if es_borrador:
            doc.build(elements, onFirstPage=self._build_marca_borrador, onLaterPages=self._build_marca_borrador)
        else:
            doc.build(elements)

        return archivo_salida

    def generar_memorando_162(
        self,
        expediente: Dict[str, Any],
        decano: Dict[str, Any],
        informe_providencia: str,
        numero_memorando: Optional[str] = None,
        archivo_salida: Optional[str] = None,
        es_borrador: bool = True,
    ) -> str:
        """
        Genera Memorando N° 162 (Declaratoria de Aptitud Legal).

        Args:
            expediente: Dict con datos del expediente
            decano: Dict con datos del Decano/a (nombres, ci, cargo)
            informe_providencia: Número de providencia del informe previo (ej. PROV-590-2026-0001)
            numero_memorando: Número de memorando (se autogenera si None)
            archivo_salida: Ruta completa del archivo PDF
            es_borrador: Si True, agrega marca de agua "BORRADOR"

        Returns:
            Ruta absoluta del archivo PDF generado
        """
        styles = self._get_styles()
        elements = []

        if not numero_memorando:
            anio = datetime.now().year
            numero_memorando = f"MEM-162-{anio}-{expediente.get('numero_expediente', '0000').split('-')[-1].zfill(4)}"

        if not archivo_salida:
            nombre_base = f"memorando_162_{numero_memorando.replace('/', '-').replace(' ', '_')}"
            if es_borrador:
                nombre_base += "_BORRADOR"
            archivo_salida = os.path.join(self.output_dir, f"{nombre_base}.pdf")

        doc = SimpleDocTemplate(
            archivo_salida,
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=1.5 * cm,
            bottomMargin=2 * cm,
        )

        # ===== ENCABEZADO INSTITUCIONAL =====
        elements.extend(self._build_header(styles))

        # ===== TÍTULO =====
        elements.append(self._build_linea_horizontal())
        elements.append(Paragraph("MEMORANDO N° 162", styles["numero_documento"]))
        elements.append(Paragraph("DECLARATORIA DE APTITUD LEGAL", styles["numero_documento"]))
        elements.append(self._build_linea_horizontal())

        # ===== REFERENCIA =====
        elements.append(Paragraph("REFERENCIA:", styles["encabezado_seccion"]))
        elements.append(
            Paragraph(
                f"Informe de Aptitud Legal <b>Providencia N° 590: {informe_providencia}</b>",
                styles["texto_normal"],
            )
        )
        elements.append(
            Paragraph(
                f"Expediente N°: <b>{expediente.get('numero_expediente', 'N/A')}</b>",
                styles["texto_normal"],
            )
        )

        # ===== CONSIDERANDOS =====
        elements.append(Paragraph("CONSIDERANDOS:", styles["encabezado_seccion"]))

        considerandos = [
            f"1. Que el/la estudiante <b>{expediente.get('estudiante_nombre', 'N/A')}</b>, "
            f"identificado/a con cédula N° <b>{expediente.get('estudiante_cedula', 'N/A')}</b>, "
            f"ha cumplido con los requisitos académicos y documentales para optar al título de "
            f"<b>{expediente.get('carrera_nombre', 'N/A')}</b>;",
            f"2. Que mediante <b>Providencia N° 590 ({informe_providencia})</b>, la Secretaría "
            f"General de Abogacía emitió informe legal declarando el expediente como <b>APTO</b>, "
            f"verificando el cumplimiento de los requisitos del Art. 235 del RRA-UNL;",
            f"3. Que no existen observaciones pendientes ni recursos administrativos en trámite "
            f"que impidan la declaratoria de aptitud;",
            f"4. Que el presente acto se enmarca en lo dispuesto por el Art. 236 y 237 del "
            f"Reglamento de Régimen Académico de la UNL y la normativa vigente del SENESCYT.",
        ]

        for considerando in considerandos:
            elements.append(Paragraph(considerando, styles["texto_normal"]))
            elements.append(Spacer(1, 4))

        # ===== RESUELVE =====
        elements.append(Paragraph("RESUELVE:", styles["encabezado_seccion"]))

        resuelve_items = [
            "PRIMERO.- Declarar la APTITUD LEGAL del/la estudiante para optar al título de "
            f"{expediente.get('carrera_nombre', 'N/A')}, conforme al expediente N° "
            f"{expediente.get('numero_expediente', 'N/A')};",
            "SEGUNDO.- Disponer la notificación de la presente declaratoria al/la interesado/a, "
            "a la Secretaría General de Abogacía y al archivo institucional;",
            "TERCERO.- La presente declaratoria surte efectos jurídicos inmediatos a partir "
            "de su suscripción, habilitando al/la estudiante para iniciar el trámite de "
            "registro del título ante el SENESCYT.",
        ]

        for item in resuelve_items:
            elements.append(Paragraph(item, styles["texto_normal"]))
            elements.append(Spacer(1, 6))

        # ===== FIRMA DECANO =====
        elements.extend(
            self._build_firma_block(
                nombre=decano.get("nombre_completo", "__________________________"),
                cargo=decano.get("cargo", "DECANO/A - FEIRNNR"),
                ci=decano.get("ci"),
                styles=styles,
            )
        )

        elements.append(Spacer(1, 15))
        elements.append(
            Paragraph(
                f"Loja, {self._formato_fecha_larga(datetime.now())}",
                styles["texto_centrado"],
            )
        )

        # ===== CC =====
        elements.append(Spacer(1, 20))
        elements.append(self._build_linea_horizontal(self.COLOR_GRIS_MEDIO, 0.5))
        elements.append(
            Paragraph(
                "C.C.:<br/>"
                "• Secretaría General de Abogacía (para archivo)<br/>"
                f"• Estudiante: {expediente.get('estudiante_nombre', 'N/A')}<br/>"
                "• Archivo Institucional<br/>"
                "• Dirección de Registro Académico (SENESCYT)",
                styles["texto_normal"],
            )
        )

        # ===== PIE DE PÁGINA =====
        elements.extend(self._build_footer(numero_memorando, datetime.now(), styles))

        # Construir PDF
        if es_borrador:
            doc.build(elements, onFirstPage=self._build_marca_borrador, onLaterPages=self._build_marca_borrador)
        else:
            doc.build(elements)

        return archivo_salida

    # ============================================================
    # UTILIDADES
    # ============================================================

    def _formato_fecha(self, fecha: Any) -> str:
        """Formatea fecha a dd/mm/yyyy."""
        if not fecha:
            return "N/A"
        if isinstance(fecha, str):
            return fecha
        if isinstance(fecha, datetime):
            return fecha.strftime("%d/%m/%Y")
        if hasattr(fecha, "strftime"):
            return fecha.strftime("%d/%m/%Y")
        return str(fecha)

    def _formato_fecha_larga(self, fecha: datetime) -> str:
        """Formato fecha larga: '15 de octubre de 2026'."""
        meses = [
            "enero",
            "febrero",
            "marzo",
            "abril",
            "mayo",
            "junio",
            "julio",
            "agosto",
            "septiembre",
            "octubre",
            "noviembre",
            "diciembre",
        ]
        return f"{fecha.day} de {meses[fecha.month - 1]} de {fecha.year}"


# Función de conveniencia para uso directo
def generar_providencia_590(
    expediente: Dict,
    secretario: Dict,
    checklist: List[Dict],
    output_dir: Optional[str] = None,
    **kwargs,
) -> str:
    """Función shortcut para generar Providencia 590."""
    generator = PDFGeneratorAdapter(output_dir=output_dir)
    return generator.generar_providencia_590(expediente, secretario, checklist, **kwargs)


def generar_memorando_162(
    expediente: Dict,
    decano: Dict,
    informe_providencia: str,
    output_dir: Optional[str] = None,
    **kwargs,
) -> str:
    """Función shortcut para generar Memorando 162."""
    generator = PDFGeneratorAdapter(output_dir=output_dir)
    return generator.generar_memorando_162(expediente, decano, informe_providencia, **kwargs)