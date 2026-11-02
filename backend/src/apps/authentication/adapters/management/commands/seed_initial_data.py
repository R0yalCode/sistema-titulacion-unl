"""Comando de carga de datos iniciales ficticios (T011, C-002, P-01).

Crea las 8 cuentas demo del MVP (specify.md 2.2) con su rol institucional
asignado. Es idempotente: re-ejecutar no duplica usuarios ni roles ni
reemplaza datos existentes.

ADVERTENCIA: las contrasenas son de demostracion y estan en claro aca a
proposito; NINGUNA cuenta con esta contrasena debe existir en produccion
(C-012). Las cedulas son ficticias y validas para el validador de digitos.
"""

from django.core.management.base import BaseCommand, CommandError  # noqa: F401
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

PASSWORD_DEMO = "SgtDemo2026!"


class Command(BaseCommand):
    help = "Crea las 8 cuentas demo para la demostracion academica del MVP."

    @transaction.atomic
    def handle(self, *args, **options):
        creadas = []
        for username, cedula, rol in CUENTAS_DEMO:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"cedula": cedula},
            )
            if created:
                user.set_password(PASSWORD_DEMO)
                user.save()
                creadas.append(username)
            role, _ = Role.objects.get_or_create(name=rol)
            UserRole.objects.get_or_create(user=user, role=role)
        self.stdout.write(
            self.style.SUCCESS(
                f"seed_initial_data completo: {len(creadas)} nuevas, "
                f"{len(CUENTAS_DEMO)} cuentas demo garantizadas "
                f"(idempotente). Contrasena demo estandar aplicada solo a "
                f"cuentas nuevas."
            )
        )
