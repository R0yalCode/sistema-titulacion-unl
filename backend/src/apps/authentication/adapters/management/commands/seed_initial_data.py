"""Comando de carga de datos iniciales ficticios (T011, C-002, P-01).

Crea las 8 cuentas demo del MVP (specify.md 2.2) con su rol institucional
asignado. Es idempotente: re-ejecutar no duplica usuarios ni roles ni
reemplaza datos existentes.

La contrasena de las cuentas demo NO esta en el codigo: se lee de la
variable de entorno SEED_DEMO_PASSWORD, que es obligatoria y no tiene valor
por defecto. Si falta o esta vacia, el comando se detiene sin crear nada.
Su valor nunca se escribe en la salida. NINGUNA cuenta demo debe existir en
produccion (C-012). Las cedulas son ficticias y validas para el validador de
digitos.
"""

import os

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.authentication.adapters.models import Role, User, UserRole

CUENTAS_DEMO = [
    (
        "estudiante_1",
        "1100000002",
        "ESTUDIANTE",
    ),
    (
        "secretaria_carrera",
        "1100000003",
        "SECRETARIA_CARRERA",
    ),
    (
        "secretario_abogado",
        "1100000004",
        "SECRETARIO_ABOGADO",
    ),
    (
        "analista_apoyo",
        "1100000005",
        "ANALISTA_APOYO",
    ),
    (
        "decano_feirnnr",
        "1100000006",
        "DECANO",
    ),
    (
        "director_computacion",
        "1100000007",
        "DIRECTOR_CARRERA",
    ),
    (
        "responsable_practicas",
        "1100000008",
        "RESPONSABLE_DEPENDENCIA",
    ),
    (
        "admin_sys",
        "1100000009",
        "ADMINISTRADOR",
    ),
]

# Nombre de la variable de entorno con la contrasena de las cuentas demo.
VARIABLE_CLAVE_DEMO = "SEED_DEMO_PASSWORD"


def _clave_demo() -> str:
    """Devuelve la contrasena demo de la variable de entorno o detiene el comando."""
    clave = os.environ.get(VARIABLE_CLAVE_DEMO, "")
    if not clave.strip():
        raise CommandError(
            f"La variable de entorno {VARIABLE_CLAVE_DEMO} es obligatoria y no "
            f"puede estar vacia: define la contrasena de las cuentas demo antes "
            f"de ejecutar seed_initial_data. No se creo ninguna cuenta."
        )
    return clave


class Command(BaseCommand):
    help = "Crea las 8 cuentas demo para la demostracion academica del MVP."

    @transaction.atomic
    def handle(self, *args, **options):
        clave_demo = _clave_demo()
        creadas = []
        for username, cedula, rol in CUENTAS_DEMO:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"cedula": cedula},
            )
            if created:
                user.set_password(clave_demo)
                user.save()
                creadas.append(username)
            role, _ = Role.objects.get_or_create(name=rol)
            UserRole.objects.get_or_create(user=user, role=role)
        self.stdout.write(
            self.style.SUCCESS(
                f"seed_initial_data completo: {len(creadas)} nuevas, "
                f"{len(CUENTAS_DEMO)} cuentas demo garantizadas "
                f"(idempotente). Contrasena demo de {VARIABLE_CLAVE_DEMO} "
                f"aplicada solo a cuentas nuevas."
            )
        )
