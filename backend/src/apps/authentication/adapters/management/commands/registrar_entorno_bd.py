"""Registra la identidad de entorno de la base de datos conectada.

- `produccion`: lo ejecuta el arranque de la imagen de producción tras migrar.
  Detiene el arranque si la base ya está registrada como desarrollo.
- `desarrollo`: lo ejecuta una persona, una vez, sobre una base local. Exige
  escribir el nombre de la base y nunca cambia una identidad existente.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, connection, transaction

from apps.authentication.adapters.models import IdentidadEntornoBD
from core.adapters.entorno_demo import (
    ENTORNO_DESARROLLO,
    ENTORNO_PRODUCCION,
    MODULO_DESARROLLO,
    MODULO_PRODUCCION,
    IdentidadNoVerificable,
    existe_marca_produccion,
    leer_identidad_base,
    modulo_activo,
)


class Command(BaseCommand):
    help = "Registra si la base conectada es de desarrollo o de producción."

    def add_arguments(self, parser):
        parser.add_argument("entorno", choices=[ENTORNO_DESARROLLO, ENTORNO_PRODUCCION])
        parser.add_argument(
            "--confirmar-base",
            default="",
            help="Nombre exacto de la base. Obligatorio para registrar desarrollo.",
        )

    def handle(self, *args, **options):
        entorno = options["entorno"]
        nombre = str(connection.settings_dict.get("NAME") or "")
        if entorno == ENTORNO_PRODUCCION:
            self._exigir_produccion()
        else:
            self._exigir_desarrollo(nombre, options["confirmar_base"])
        try:
            with transaction.atomic():
                actual = leer_identidad_base()
                if actual is None:
                    IdentidadEntornoBD.objects.create(
                        entorno=entorno, base_registrada=nombre
                    )
        except (IdentidadNoVerificable, IntegrityError) as error:
            raise CommandError(
                "No se pudo verificar la identidad de la base. No se registró nada."
            ) from error
        if actual not in (None, entorno):
            raise CommandError(
                f"La base ya está registrada como {actual}: su identidad no se "
                f"puede cambiar a {entorno}."
            )
        estado = "ya estaba registrada" if actual else "registrada"
        self.stdout.write(self.style.SUCCESS(f"Base {estado} como {entorno}."))

    @staticmethod
    def _exigir_produccion():
        if not existe_marca_produccion() or modulo_activo() != MODULO_PRODUCCION:
            raise CommandError(
                "La identidad de producción solo la registra la imagen de "
                "producción con config.settings.production."
            )

    @staticmethod
    def _exigir_desarrollo(nombre, confirmacion):
        if existe_marca_produccion() or modulo_activo() != MODULO_DESARROLLO:
            raise CommandError(
                "La identidad de desarrollo solo se registra con "
                "config.settings.local fuera de la imagen de producción."
            )
        if not nombre or confirmacion != nombre:
            raise CommandError(
                "Indique el nombre exacto de la base con --confirmar-base. "
                "No se registró nada."
            )
