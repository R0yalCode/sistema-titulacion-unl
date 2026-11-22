"""Catálogo académico interno y datos de la simulación MockSGA.

- `Facultad` y `Carrera`: catálogo interno de SGT-SIAAF. La carrera determina
  la facultad (una sola relación, sin duplicarla en el estudiante). Mientras
  la UNL no entregue el catálogo oficial validado, los registros cargados son
  de demostración y llevan `es_simulada=True` y códigos `MOCK-…`.
- `PerfilSGASimulado`: registros de la fuente simulada MockSGA. Representan
  lo que devolvería el SGA para una cédula; NO son datos institucionales.
- `EventoCatalogoAcademico`: bitácora inmutable de los cambios del catálogo,
  de los perfiles simulados y de las asignaciones de ámbito.
"""

import uuid

from django.conf import settings
from django.db import models

from apps.authentication.adapters.models import cedula_validator


class Facultad(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=32, unique=True)
    nombre = models.CharField(max_length=255)
    activa = models.BooleanField(default=True)
    es_simulada = models.BooleanField(
        default=False,
        help_text="Registro de demostración (MOCK): no es dato oficial de la UNL.",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "academico_facultad"
        ordering = ("nombre",)
        verbose_name = "facultad"
        verbose_name_plural = "facultades"

    def __str__(self):
        sufijo = " [MOCK]" if self.es_simulada else ""
        return f"{self.nombre} ({self.codigo}){sufijo}"


class Carrera(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=32, unique=True)
    nombre = models.CharField(max_length=255)
    facultad = models.ForeignKey(
        Facultad, on_delete=models.PROTECT, related_name="carreras"
    )
    activa = models.BooleanField(default=True)
    es_simulada = models.BooleanField(
        default=False,
        help_text="Registro de demostración (MOCK): no es dato oficial de la UNL.",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "academico_carrera"
        ordering = ("nombre",)

    def __str__(self):
        sufijo = " [MOCK]" if self.es_simulada else ""
        return f"{self.nombre} ({self.codigo}){sufijo}"


class PerfilSGASimulado(models.Model):
    """Registro de la fuente simulada MockSGA (prototipo, sin conexión real).

    Se localiza por `identificacion` (cédula), igual que lo haría una
    consulta al SGA. Los códigos de carrera y facultad se guardan como texto,
    como los entregaría la fuente, y el servicio los resuelve contra el
    catálogo interno: así se pueden demostrar perfiles incompletos o
    inconsistentes sin alterar el catálogo.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    identificacion = models.CharField(
        max_length=20, unique=True, validators=[cedula_validator]
    )
    nombres = models.CharField(max_length=150, blank=True)
    apellidos = models.CharField(max_length=150, blank=True)
    correo_institucional = models.EmailField(blank=True)
    codigo_carrera = models.CharField(max_length=32, blank=True)
    codigo_facultad = models.CharField(
        max_length=32,
        blank=True,
        help_text=(
            "Código de facultad que informa la fuente. Si se indica, debe "
            "coincidir con la facultad de la carrera en el catálogo."
        ),
    )
    activo = models.BooleanField(
        default=True,
        help_text="Si es falso, la fuente simulada responde como si no existiera.",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "academico_perfil_sga_simulado"
        verbose_name = "perfil SGA simulado (MockSGA)"
        verbose_name_plural = "perfiles SGA simulados (MockSGA)"

    def __str__(self):
        return (
            f"MockSGA {self.identificacion} → {self.codigo_carrera or '(sin carrera)'}"
        )


class EventoCatalogoAcademico(models.Model):
    """Bitácora inmutable del catálogo académico y de las asociaciones.

    `detalles` solo guarda códigos, identificadores técnicos y nombres de
    campos modificados; nunca cédulas, nombres ni correos.
    """

    class Tipo(models.TextChoices):
        CREADO = "CREADO", "Registro creado"
        MODIFICADO = "MODIFICADO", "Registro modificado"
        ELIMINADO = "ELIMINADO", "Registro eliminado"
        AMBITO_ASIGNADO = "AMBITO_ASIGNADO", "Ámbito institucional asignado"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo = models.CharField(max_length=32, choices=Tipo.choices, db_index=True)
    objeto = models.CharField(max_length=32, db_index=True)
    objeto_id = models.CharField(max_length=64)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="eventos_catalogo_academico",
        help_text="Usuario que hizo el cambio; vacío si fue un comando de gestión.",
    )
    origen = models.CharField(max_length=32)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    detalles = models.JSONField(default=dict)

    class Meta:
        db_table = "academico_evento_catalogo"
        ordering = ("-timestamp",)
        verbose_name = "evento del catálogo académico"
        verbose_name_plural = "eventos del catálogo académico"

    def __str__(self):
        return f"{self.timestamp:%Y-%m-%d %H:%M} {self.tipo} {self.objeto}"
