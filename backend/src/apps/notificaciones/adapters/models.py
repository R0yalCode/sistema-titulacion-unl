"""Modelo de notificaciones internas in-app y bitácora de auditoría (DEC-01; T021/T037/T039).

Notificaciones 100% internas al sistema, sin uso de correo electronico.
Bitácora inmutable de auditoría en JSONB (T039).
"""
import uuid

from django.conf import settings
from django.db import models


class NotificacionInterna(models.Model):
    """Notificacion interna para bandeja de avisos del usuario."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario_destino = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notificaciones_recibidas",
    )
    expediente = models.ForeignKey(
        "expedientes.ExpedienteTitulacion",
        on_delete=models.CASCADE,
        related_name="notificaciones",
    )
    peticion = models.ForeignKey(
        "peticiones.PeticionDocumental",
        on_delete=models.CASCADE,
        related_name="notificaciones",
        null=True,
        blank=True,
    )
    titulo = models.CharField(max_length=255)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False, db_index=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "notificaciones_notificacioninterna"
        indexes = [
            models.Index(
                fields=["usuario_destino", "leida"], name="idx_notif_usuario_leida"
            ),
            models.Index(
                fields=["usuario_destino", "fecha_creacion"],
                name="idx_notif_usuario_fecha",
            ),
            models.Index(fields=["expediente"], name="idx_notif_expediente"),
            models.Index(fields=["peticion"], name="idx_notif_peticion"),
        ]
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"Notificacion {self.id} -> {self.usuario_destino} ({self.titulo})"


class EventoAuditoria(models.Model):
    """Bitácora inmutable de auditoría en JSONB (T039; Principio C-008).

    Registra automáticamente eventos de negocio y técnicos:
    - Cambios de estado de expediente
    - Evaluaciones de checklist
    - Cargas documentales
    - Emisiones de resoluciones (informe/declaratoria)

    Almacena el delta del cambio en formato JSONB para auditoría inmutable.
    """

    class Accion(models.TextChoices):
        EXPEDIENTE_CREADO = "EXPEDIENTE_CREADO", "Expediente creado"
        EXPEDIENTE_ENVIADO = "EXPEDIENTE_ENVIADO", "Expediente enviado"
        ESTADO_CAMBIADO = "ESTADO_CAMBIADO", "Estado de expediente cambiado"
        CHECKLIST_EVALUADO = "CHECKLIST_EVALUADO", "Checklist evaluado"
        OBSERVACION_REGISTRADA = "OBSERVACION_REGISTRADA", "Observación registrada"
        SUBSANACION_REALIZADA = "SUBSANACION_REALIZADA", "Subsanación realizada"
        DOCUMENTO_CARGADO = "DOCUMENTO_CARGADO", "Documento cargado"
        INFORME_EMITIDO = "INFORME_EMITIDO", "Informe legal emitido"
        DECLARATORIA_REGISTRADA = "DECLARATORIA_REGISTRADA", "Declaratoria registrada"
        EXPEDIENTE_CANCELADO = "EXPEDIENTE_CANCELADO", "Expediente cancelado"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    accion = models.CharField(
        max_length=32,
        choices=Accion.choices,
        db_index=True,
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="eventos_auditoria",
        help_text="Usuario que realizó la acción",
    )
    rol_usuario = models.CharField(
        max_length=32,
        help_text="Rol del usuario al momento de la acción",
    )
    expediente = models.ForeignKey(
        "expedientes.ExpedienteTitulacion",
        on_delete=models.PROTECT,
        related_name="eventos_auditoria",
        help_text="Expediente relacionado con el evento",
    )
    ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="Dirección IP del usuario",
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    detalles = models.JSONField(
        help_text="Detalles del evento en formato JSONB (delta del cambio, metadatos, etc.)"
    )

    class Meta:
        db_table = "notificaciones_eventoauditoria"
        indexes = [
            models.Index(
                fields=["expediente", "timestamp"], name="idx_audit_expediente_fecha"
            ),
            models.Index(fields=["usuario", "timestamp"], name="idx_audit_usuario_fecha"),
            models.Index(fields=["accion", "timestamp"], name="idx_audit_accion_fecha"),
            models.Index(fields=["timestamp"], name="idx_audit_fecha"),
        ]
        ordering = ["-timestamp"]

    def __str__(self):
        return f"Auditoria {self.id} -> {self.accion} by {self.usuario} on {self.expediente_id}"