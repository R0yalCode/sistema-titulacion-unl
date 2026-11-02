"""Modelos de verificación y observaciones (T026; specify.md 7.5).

Tablas: `ChecklistVerification` (evaluación de requisitos por jurista),
`ObservacionAccionable` (deficiencias documentales con trazabilidad).
Principio C-007: integridad transaccional y trazabilidad.
"""

import uuid

from django.db import models

from apps.authentication.adapters.models import ROLE_CHOICES
from apps.peticiones.adapters.models import ESTADO_VERIFICADO, ESTADO_OBSERVADO


ESTADO_VERIFICACION_PENDIENTE = "PENDIENTE"
ESTADO_VERIFICACION_VERIFICADO = ESTADO_VERIFICADO
ESTADO_VERIFICACION_OBSERVADO = ESTADO_OBSERVADO

ESTADOS_VERIFICACION_CHOICES = [
    (ESTADO_VERIFICACION_PENDIENTE, ESTADO_VERIFICACION_PENDIENTE),
    (ESTADO_VERIFICACION_VERIFICADO, ESTADO_VERIFICACION_VERIFICADO),
    (ESTADO_VERIFICACION_OBSERVADO, ESTADO_VERIFICACION_OBSERVADO),
]


class ChecklistVerification(models.Model):
    """Evaluación de un requisito del checklist por parte del jurista (specify.md 7.5).

    Cada requisito del expediente es evaluado una vez por el Secretario/a-Abogado/a
    o Analista de Apoyo. El estado puede ser VERIFICADO u OBSERVADO.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expediente = models.ForeignKey(
        "expedientes.ExpedienteTitulacion",
        on_delete=models.CASCADE,
        related_name="checklist_verificaciones",
    )
    requisito = models.ForeignKey(
        "peticiones.CatalogoDocumental",
        on_delete=models.PROTECT,
        related_name="verificaciones",
    )
    estado_verificacion = models.CharField(
        max_length=16,
        choices=ESTADOS_VERIFICACION_CHOICES,
        default=ESTADO_VERIFICACION_PENDIENTE,
        db_index=True,
    )
    evaluado_por = models.ForeignKey(
        "authentication.User",
        on_delete=models.PROTECT,
        related_name="verificaciones_realizadas",
        null=True,
        blank=True,
    )
    fecha_evaluacion = models.DateTimeField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "verificacion_checklistverification"
        constraints = [
            models.UniqueConstraint(
                fields=["expediente", "requisito"],
                name="unique_verificacion_por_requisito",
            )
        ]
        indexes = [
            models.Index(
                fields=["expediente", "estado_verificacion"],
                name="idx_verif_expediente_estado",
            ),
            models.Index(
                fields=["evaluado_por"], name="idx_verif_evaluado_por"
            ),
        ]

    def __str__(self):
        return f"{self.expediente_id}/{self.requisito_id} ({self.estado_verificacion})"


class ObservacionAccionable(models.Model):
    """Registro de deficiencias documentales accionables (specify.md 7.5).

    Cuando un requisito es OBSERVADO, se crea una observación con el motivo.
    La observación debe ser resuelta (subsanada) por el estudiante para
    continuar el trámite.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expediente = models.ForeignKey(
        "expedientes.ExpedienteTitulacion",
        on_delete=models.CASCADE,
        related_name="observaciones",
    )
    peticion = models.ForeignKey(
        "peticiones.PeticionDocumental",
        on_delete=models.CASCADE,
        related_name="observaciones",
    )
    registrada_por = models.ForeignKey(
        "authentication.User",
        on_delete=models.PROTECT,
        related_name="observaciones_registradas",
    )
    motivo_observacion = models.TextField()
    fecha_registro = models.DateTimeField(auto_now_add=True, db_index=True)
    resuelta = models.BooleanField(default=False, db_index=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "verificacion_observacionaccionable"
        indexes = [
            models.Index(
                fields=["expediente", "resuelta"], name="idx_obs_expediente_resuelta"
            ),
            models.Index(
                fields=["peticion", "resuelta"], name="idx_obs_peticion_resuelta"
            ),
            models.Index(
                fields=["registrada_por"], name="idx_obs_registrada_por"
            ),
            models.Index(
                fields=["fecha_registro"], name="idx_obs_fecha_registro"
            ),
        ]

    def __str__(self):
        return f"Obs {self.id} -> {self.peticion_id} ({'Resuelta' if self.resuelta else 'Pendiente'})"