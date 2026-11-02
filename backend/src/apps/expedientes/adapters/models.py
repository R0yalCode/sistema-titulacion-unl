import uuid

from django.db import models


class ExpedienteTitulacion(models.Model):
    """Expediente de titulacion (specify.md 7.1; tasks.md T013).

    Estados definidos por la fuente: BORRADOR, ENVIADA, EN_VERIFICACION,
    OBSERVADA, INFORME_EMITIDO, DECLARADA_APTA, CANCELADA.
    motor de estados y plazos: T014/T015.
    """

    ESTADO_BORRADOR = "BORRADOR"
    ESTADO_ENVIADA = "ENVIADA"
    ESTADO_EN_VERIFICACION = "EN_VERIFICACION"
    ESTADO_OBSERVADA = "OBSERVADA"
    ESTADO_INFORME_EMITIDO = "INFORME_EMITIDO"
    ESTADO_DECLARADA_APTA = "DECLARADA_APTA"
    ESTADO_CANCELADA = "CANCELADA"

    ESTADOS_CHOICES = [
        (ESTADO_BORRADOR, ESTADO_BORRADOR),
        (ESTADO_ENVIADA, ESTADO_ENVIADA),
        (ESTADO_EN_VERIFICACION, ESTADO_EN_VERIFICACION),
        (ESTADO_OBSERVADA, ESTADO_OBSERVADA),
        (ESTADO_INFORME_EMITIDO, ESTADO_INFORME_EMITIDO),
        (ESTADO_DECLARADA_APTA, ESTADO_DECLARADA_APTA),
        (ESTADO_CANCELADA, ESTADO_CANCELADA),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero_expediente = models.CharField(max_length=64, unique=True)
    numero_providencia = models.CharField(
        max_length=64,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
    )
    estudiante = models.ForeignKey(
        "authentication.User",
        on_delete=models.PROTECT,
        related_name="expedientes",
    )
    carrera_id = models.UUIDField(null=True, blank=True)
    facultad_id = models.UUIDField(null=True, blank=True, db_index=True)
    estado = models.CharField(
        max_length=32,
        choices=ESTADOS_CHOICES,
        default=ESTADO_BORRADOR,
        db_index=True,
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_recepcion = models.DateTimeField(null=True, blank=True)
    fecha_limite_atencion = models.DateTimeField(null=True, blank=True)
    dias_laborables_acumulados = models.IntegerField(default=0)
    fecha_ultima_pausa = models.DateTimeField(null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    activa = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["carrera_id"], name="idx_exped_carrera"),
        ]

    def __str__(self):
        return f"{self.numero_expediente} ({self.estado})"


class HistorialEstado(models.Model):
    """Bitacora de cambios de estado del expediente (plan.md 12)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expediente = models.ForeignKey(
        ExpedienteTitulacion,
        on_delete=models.CASCADE,
        related_name="historial_estado",
    )
    estado_anterior = models.CharField(
        max_length=32, choices=ExpedienteTitulacion.ESTADOS_CHOICES
    )
    estado_nuevo = models.CharField(
        max_length=32, choices=ExpedienteTitulacion.ESTADOS_CHOICES
    )
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    registrado_por = models.ForeignKey(
        "authentication.User",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=["expediente"], name="idx_hist_expediente"),
        ]

    def __str__(self):
        return f"{self.expediente_id}: {self.estado_anterior} -> {self.estado_nuevo}"
