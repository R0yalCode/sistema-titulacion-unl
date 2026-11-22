"""Prepara el entorno de demostración de la simulación MockSGA.

Carga, de forma idempotente y sin sobrescribir datos existentes:

1. Un catálogo académico de DEMOSTRACIÓN (`es_simulada=True`, códigos
   `MOCK-…`): la facultad y la carrera nombradas en la especificación del
   proyecto (spec 001 §1), más una carrera ficticia inactiva para demostrar
   el bloqueo. Los códigos e identificadores NO son los oficiales de la UNL.
2. Un perfil MockSGA por cada cuenta demo con rol ESTUDIANTE (por defecto
   `estudiante_1`), tomado de la cédula y el correo de la propia cuenta.
3. Con `--asignar-ambito-personal`: la carrera o facultad de demostración en
   las cuentas demo del personal que aún no tienen ninguna (nunca reemplaza
   un valor ya asignado), para que las bandejas por ámbito vean los
   expedientes creados en la demo.

No crea ni elimina cuentas, no cambia contraseñas, roles ni 2FA, y no
escribe cédulas, nombres ni correos en la salida. Se niega a ejecutarse si el
entorno no permite la fuente simulada (`ACADEMIC_PROFILE_MOCK_ALLOWED`).
Cada alta queda en `EventoCatalogoAcademico` con origen `seed_mock_sga`.
"""

import uuid

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.academico.adapters.models import (
    Carrera,
    EventoCatalogoAcademico,
    Facultad,
    PerfilSGASimulado,
)
from apps.academico.services.auditoria import (
    registrar_asignacion_ambito,
    registrar_cambio,
)
from apps.authentication.adapters.models import User

ORIGEN = "seed_mock_sga"

# Espacio de nombres fijo: los UUID del catálogo de demostración son los
# mismos en todos los entornos (reproducibles), derivados del código.
NAMESPACE_MOCK = uuid.UUID("6f1d3c52-8a4e-5b7f-9c2d-0e4a6b8c1d3f")


def uuid_mock(codigo: str) -> uuid.UUID:
    return uuid.uuid5(NAMESPACE_MOCK, codigo)


FACULTAD_DEMO = {
    "codigo": "MOCK-FEIRNNR",
    "nombre": (
        "Facultad de la Energía, las Industrias y los Recursos Naturales "
        "No Renovables"
    ),
}
CARRERAS_DEMO = (
    {"codigo": "MOCK-COMPUTACION", "nombre": "Computación", "activa": True},
    {
        "codigo": "MOCK-CARRERA-INACTIVA",
        "nombre": "Carrera ficticia inactiva (solo demostración)",
        "activa": False,
    },
)
CARRERA_ESTUDIANTES = "MOCK-COMPUTACION"

ESTUDIANTES_DEMO = ("estudiante_1",)

# Cuentas demo del personal y qué ámbito necesita cada rol (scope_filter).
AMBITO_POR_ROL = {
    "SECRETARIA_CARRERA": "carrera",
    "DIRECTOR_CARRERA": "carrera",
    "SECRETARIO_ABOGADO": "facultad",
    "ANALISTA_APOYO": "facultad",
    "DECANO": "facultad",
}
PERSONAL_DEMO = (
    "secretaria_carrera",
    "director_computacion",
    "secretario_abogado",
    "analista_apoyo",
    "decano_feirnnr",
)


class Command(BaseCommand):
    help = (
        "Carga el catálogo académico de demostración (MOCK) y los perfiles "
        "MockSGA de las cuentas demo. Simulación de prototipo."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--estudiantes",
            nargs="+",
            default=list(ESTUDIANTES_DEMO),
            help="Usuarios ESTUDIANTE a los que crear perfil MockSGA.",
        )
        parser.add_argument(
            "--asignar-ambito-personal",
            action="store_true",
            help=(
                "Asigna la carrera/facultad de demostración a las cuentas demo "
                "del personal que no tienen ninguna."
            ),
        )

    def handle(self, *args, **options):
        if not getattr(settings, "ACADEMIC_PROFILE_MOCK_ALLOWED", False):
            raise CommandError(
                "Este entorno no permite la fuente académica simulada "
                "(ACADEMIC_PROFILE_MOCK_ALLOWED es falso). No se cargó nada."
            )
        with transaction.atomic():
            facultad = self._facultad()
            carreras = {c["codigo"]: self._carrera(c, facultad) for c in CARRERAS_DEMO}
            perfiles = self._perfiles(options["estudiantes"], facultad)
            ambitos = 0
            if options["asignar_ambito_personal"]:
                ambitos = self._ambitos(carreras[CARRERA_ESTUDIANTES], facultad)
        self.stdout.write(
            self.style.SUCCESS(
                f"MockSGA listo: {len(carreras)} carreras de demostración, "
                f"{perfiles} perfiles simulados nuevos, {ambitos} cuentas de "
                "personal con ámbito asignado."
            )
        )

    def _registrar_alta(self, instancia):
        registrar_cambio(
            instancia, tipo=EventoCatalogoAcademico.Tipo.CREADO, origen=ORIGEN
        )

    def _facultad(self):
        facultad, creada = Facultad.objects.get_or_create(
            codigo=FACULTAD_DEMO["codigo"],
            defaults={
                "id": uuid_mock(FACULTAD_DEMO["codigo"]),
                "nombre": FACULTAD_DEMO["nombre"],
                "activa": True,
                "es_simulada": True,
            },
        )
        if creada:
            self._registrar_alta(facultad)
        return facultad

    def _carrera(self, datos, facultad):
        carrera, creada = Carrera.objects.get_or_create(
            codigo=datos["codigo"],
            defaults={
                "id": uuid_mock(datos["codigo"]),
                "nombre": datos["nombre"],
                "facultad": facultad,
                "activa": datos["activa"],
                "es_simulada": True,
            },
        )
        if creada:
            self._registrar_alta(carrera)
        return carrera

    def _perfiles(self, usernames, facultad) -> int:
        nuevos = 0
        for username in usernames:
            user = User.objects.filter(username=username).first()
            if user is None:
                self.stdout.write(
                    self.style.WARNING(f"{username}: no existe; se omite.")
                )
                continue
            if not user.has_role("ESTUDIANTE"):
                self.stdout.write(
                    self.style.WARNING(
                        f"{username}: no tiene rol ESTUDIANTE; se omite."
                    )
                )
                continue
            if not user.cedula:
                self.stdout.write(
                    self.style.WARNING(f"{username}: sin cédula registrada; se omite.")
                )
                continue
            perfil, creado = PerfilSGASimulado.objects.get_or_create(
                identificacion=user.cedula,
                defaults={
                    "nombres": user.first_name or "Estudiante",
                    "apellidos": user.last_name or "De Prueba (MOCK)",
                    "correo_institucional": user.email,
                    "codigo_carrera": CARRERA_ESTUDIANTES,
                    "codigo_facultad": facultad.codigo,
                },
            )
            if creado:
                self._registrar_alta(perfil)
                nuevos += 1
            else:
                self.stdout.write(
                    f"{username}: ya tenía perfil MockSGA; no se modifica."
                )
        return nuevos

    def _ambitos(self, carrera, facultad) -> int:
        asignadas = 0
        for username in PERSONAL_DEMO:
            user = User.objects.filter(username=username).first()
            if user is None:
                continue
            if user.carrera_id or user.facultad_id:
                self.stdout.write(
                    f"{username}: ya tiene ámbito asignado; no se modifica."
                )
                continue
            ambitos = {
                AMBITO_POR_ROL[r] for r in user.get_roles() if r in AMBITO_POR_ROL
            }
            if not ambitos:
                continue
            campos = {"facultad_id": facultad.id}
            if "carrera" in ambitos:
                campos["carrera_id"] = carrera.id
            for campo, valor in campos.items():
                setattr(user, campo, valor)
            user.save(update_fields=list(campos))
            registrar_asignacion_ambito(user, origen=ORIGEN, campos=campos)
            asignadas += 1
        return asignadas
