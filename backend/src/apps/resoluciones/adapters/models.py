"""Modelos de resoluciones oficiales (T032; specify.md 7.6).

Tablas: `InformeAptitud` (Providencia N° 590 emitida por Secretaría-Abogacía)
y `DeclaratoriaAptitud` (Memorando N° 162 firmado por Decano/a).
Principio C-002: trazabilidad completa. Principio C-007: integridad transaccional.
"""

import uuid

from django.db import models


class InformeAptitud(models.Model):
    """Informe legal de aptitud - Providencia N° 590 (specify.md 7.6, RF-009, HU-009).

    Emitido por Secretaría-Abogacía cuando el 100% del checklist está VERIFICADO.
    Inmutable una vez emitido (RN-004).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expediente = models.OneToOneField(
        "expedientes.ExpedienteTitulacion",
        on_delete=models.PROTECT,
        related_name="informe_aptitud",
    )
    numero_providencia = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text="Número de providencia (ej. PROV-590-2026-0001)",
    )
    emisor = models.ForeignKey(
        "authentication.User",
        on_delete=models.PROTECT,
        related_name="informes_emitidos",
        help_text="Secretario/a-Abogado/a que emite el informe",
    )
    dictamen = models.TextField(
        help_text="Dictamen legal: APTO / NO APTO con fundamentación"
    )
    archivo_informe_path = models.CharField(
        max_length=512,
        help_text="Ruta al PDF generado de la Providencia N° 590"
    )
    fecha_emision = models.DateTimeField(auto_now_add=True, db_index=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "resoluciones_informeaptitud"
        indexes = [
            models.Index(
                fields=["expediente"], name="idx_informe_expediente"
            ),
            models.Index(
                fields=["emisor"], name="idx_informe_emisor"
            ),
            models.Index(
                fields=["fecha_emision"], name="idx_informe_fecha"
            ),
        ]

    def __str__(self):
        return f"Informe {self.numero_providencia} -> {self.expediente_id}"


class DeclaratoriaAptitud(models.Model):
    """Declaratoria de aptitud legal - Memorando N° 162 (specify.md 7.6, RF-011, HU-010, DEC-04).

    Registrada por Decano/a con memorando firmado externamente (FirmaEC).
    Culmina el flujo de la Fase 1 (MVP) cambiando el expediente a DECLARADA_APTA.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expediente = models.OneToOneField(
        "expedientes.ExpedienteTitulacion",
        on_delete=models.PROTECT,
        related_name="declaratoria_aptitud",
    )
    numero_memorando = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text="Número de memorando (ej. MEM-162-2026-0001)",
    )
    decano = models.ForeignKey(
        "authentication.User",
        on_delete=models.PROTECT,
        related_name="declaratorias_firmadas",
        help_text="Decano/a que firma la declaratoria",
    )
    archivo_memorando_firmado_path = models.CharField(
        max_length=512,
        help_text="Ruta al PDF del Memorando N° 162 firmado (FirmaEC)"
    )
    fecha_declaratoria = models.DateTimeField(auto_now_add=True, db_index=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "resoluciones_declaratoriaaptitud"
        indexes = [
            models.Index(
                fields=["expediente"], name="idx_declaratoria_expediente"
            ),
            models.Index(
                fields=["decano"], name="idx_declaratoria_decano"
            ),
            models.Index(
                fields=["fecha_declaratoria"], name="idx_declaratoria_fecha"
            ),
        ]

    def __str__(self):
        return f"Declaratoria {self.numero_memorando} -> {self.expediente_id}"