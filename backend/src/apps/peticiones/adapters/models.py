"""Modelos de peticiones documentales (T020; specify.md 7.2-7.4).

Tablas: `CatalogoDocumental` (catalogo de requisitos), `PeticionDocumental`
(solicitud atomica de requisito dentro del expediente), `DocumentoEntregado`
(versionado N+1 con hash SHA-256, validacion magic bytes %PDF-, max 10MB).
Principio C-006: almacenamiento privado, validacion estricta en servidor.
"""

import uuid

from django.db import models

from apps.authentication.adapters.models import ROLE_CHOICES

FASE_1 = "FASE_1"
FASE_2 = "FASE_2"
FASE_3 = "FASE_3"

FASES_CHOICES = [
    (FASE_1, FASE_1),
    (FASE_2, FASE_2),
    (FASE_3, FASE_3),
]

ESTADO_PENDIENTE = "PENDIENTE"
ESTADO_SOLICITADO = "SOLICITADO"
ESTADO_CARGADO = "CARGADO"
ESTADO_LEGALIZADO = "LEGALIZADO"
ESTADO_VERIFICADO = "VERIFICADO"
ESTADO_OBSERVADO = "OBSERVADO"

ESTADOS_PETICION_CHOICES = [
    (ESTADO_PENDIENTE, ESTADO_PENDIENTE),
    (ESTADO_SOLICITADO, ESTADO_SOLICITADO),
    (ESTADO_CARGADO, ESTADO_CARGADO),
    (ESTADO_LEGALIZADO, ESTADO_LEGALIZADO),
    (ESTADO_VERIFICADO, ESTADO_VERIFICADO),
    (ESTADO_OBSERVADO, ESTADO_OBSERVADO),
]


class CatalogoDocumental(models.Model):
    """Catalogo configurable de requisitos de titulacion (specify.md 7.2)."""

    codigo_requisito = models.CharField(max_length=64, unique=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    es_obligatorio_base = models.BooleanField(default=True)
    fase = models.CharField(max_length=8, choices=FASES_CHOICES, default=FASE_1)
    rol_emisor_sugerido = models.CharField(max_length=64, choices=ROLE_CHOICES)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "peticiones_catalogodocumental"
        indexes = [
            models.Index(fields=["fase"], name="idx_catalogo_fase"),
            models.Index(fields=["activo"], name="idx_catalogo_activo"),
        ]

    def __str__(self):
        return f"{self.codigo_requisito} - {self.nombre}"


class PeticionDocumental(models.Model):
    """Peticion atomica de un requisito dentro del expediente (7.3)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expediente = models.ForeignKey(
        "expedientes.ExpedienteTitulacion",
        on_delete=models.CASCADE,
        related_name="peticiones_documentales",
    )
    requisito = models.ForeignKey(
        CatalogoDocumental,
        on_delete=models.PROTECT,
        related_name="peticiones",
    )
    estado_peticion = models.CharField(
        max_length=16,
        choices=ESTADOS_PETICION_CHOICES,
        default=ESTADO_PENDIENTE,
        db_index=True,
    )
    dependencia_emisora = models.CharField(max_length=64, choices=ROLE_CHOICES)
    fecha_solicitud = models.DateTimeField(null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "peticiones_peticiondocumental"
        constraints = [
            models.UniqueConstraint(
                fields=["expediente", "requisito"],
                name="unique_peticion_por_requisito",
            )
        ]
        indexes = [
            models.Index(fields=["expediente"], name="idx_peticion_expediente"),
            models.Index(fields=["estado_peticion"], name="idx_peticion_estado"),
            models.Index(fields=["requisito"], name="idx_peticion_requisito"),
        ]

    def __str__(self):
        return f"{self.expediente_id}/{self.requisito_id} ({self.estado_peticion})"


class DocumentoEntregado(models.Model):
    """Metadata de archivos PDF adjuntos a una peticion (specify.md 7.4).

    Versionado N+1: cada carga incrementa version y marca anterior como
    no vigente. Validacion: magic bytes %PDF-, max 10MB, hash SHA-256.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    peticion = models.ForeignKey(
        PeticionDocumental,
        on_delete=models.CASCADE,
        related_name="documentos_entregados",
    )
    version = models.PositiveIntegerField()
    archivo_path = models.CharField(max_length=512)
    nombre_original = models.CharField(max_length=255)
    tamanio_bytes = models.BigIntegerField()
    hash_sha256 = models.CharField(max_length=64)
    tipo_mime = models.CharField(max_length=100)
    subido_por = models.ForeignKey(
        "authentication.User",
        on_delete=models.PROTECT,
        related_name="documentos_subidos",
    )
    fecha_carga = models.DateTimeField(auto_now_add=True)
    es_vigente = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "peticiones_documentoentregado"
        constraints = [
            models.UniqueConstraint(
                fields=["peticion", "version"],
                name="unique_version_por_peticion",
            )
        ]
        indexes = [
            models.Index(
                fields=["peticion", "es_vigente"], name="idx_doc_peticion_vigente"
            ),
            models.Index(
                fields=["peticion", "version"], name="idx_doc_peticion_version"
            ),
            models.Index(fields=["subido_por"], name="idx_doc_subido_por"),
            models.Index(fields=["hash_sha256"], name="idx_doc_hash"),
        ]

    def __str__(self):
        return f"{self.peticion_id} v{self.version} ({self.hash_sha256[:12]})"
