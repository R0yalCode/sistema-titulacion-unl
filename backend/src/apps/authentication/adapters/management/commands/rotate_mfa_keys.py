"""Recifra los secretos TOTP con la clave primaria de MFA_ENCRYPTION_KEYS.

Procedimiento de rotación (docs/autenticacion/politica-2fa.md):
1. Anteponer la clave nueva: MFA_ENCRYPTION_KEYS=<nueva>,<anterior>.
2. Reiniciar el servicio y ejecutar `python manage.py rotate_mfa_keys`.
3. Retirar la clave anterior de la variable y reiniciar.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.authentication.services.mfa import rotar_cifrado_secretos


class Command(BaseCommand):
    help = "Recifra los secretos TOTP con la primera clave de MFA_ENCRYPTION_KEYS."

    def handle(self, *args, **options):
        with transaction.atomic():
            total = rotar_cifrado_secretos()
        self.stdout.write(self.style.SUCCESS(f"Secretos recifrados: {total}"))
