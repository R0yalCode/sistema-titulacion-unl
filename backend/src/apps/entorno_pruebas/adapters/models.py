"""Marcador interno de los registros del dataset local de pruebas.

Las cuentas del dataset son ficticias. Este registro, que no se muestra en la
interfaz ni en la API, sirve para localizarlas y administrarlas sin afectar a
cuentas reales. No debe eliminarse.
"""

import uuid

from django.db import models


class RegistroDatasetSintetico(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lote = models.CharField(max_length=32, db_index=True)
    #: Tipo de objeto marcado: usuario, perfil_sga, carrera, facultad,
    #: expediente.
    objeto = models.CharField(max_length=32)
    objeto_id = models.CharField(max_length=64)
    #: Clave estable dentro del lote (p. ej. "usuario:ESTUDIANTE:01"): permite
    #: que el comando sea idempotente.
    clave = models.CharField(max_length=96)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "entorno_pruebas_registro_dataset"
        constraints = [
            models.UniqueConstraint(
                fields=["lote", "clave"], name="uniq_dataset_lote_clave"
            ),
            models.UniqueConstraint(
                fields=["objeto", "objeto_id"], name="uniq_dataset_objeto"
            ),
        ]
        verbose_name = "registro del dataset de pruebas"
        verbose_name_plural = "registros del dataset de pruebas"

    def __str__(self):
        return f"{self.lote} {self.clave}"
