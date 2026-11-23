"""Ayudantes de prueba: catálogo y perfiles MockSGA (datos ficticios)."""

import uuid

from apps.academico.adapters.models import Carrera, Facultad, PerfilSGASimulado

FACULTAD_PRUEBA = "TEST-FAC"
CARRERA_PRUEBA = "TEST-CARRERA"


def crear_facultad(codigo=FACULTAD_PRUEBA, *, id=None, activa=True):
    facultad, _ = Facultad.objects.get_or_create(
        codigo=codigo,
        defaults={
            "id": id or uuid.uuid4(),
            "nombre": f"Facultad de prueba {codigo}",
            "activa": activa,
            "es_simulada": True,
        },
    )
    return facultad


def crear_carrera(codigo=CARRERA_PRUEBA, *, id=None, facultad=None, activa=True):
    carrera, _ = Carrera.objects.get_or_create(
        codigo=codigo,
        defaults={
            "id": id or uuid.uuid4(),
            "nombre": f"Carrera de prueba {codigo}",
            "facultad": facultad or crear_facultad(),
            "activa": activa,
            "es_simulada": True,
        },
    )
    return carrera


_cedulas = iter(range(9100000000, 9199999999))


def crear_perfil_mock(user, carrera=None, **campos):
    """Perfil MockSGA coherente con la cuenta (cédula y correo).

    Si la cuenta no tiene cédula o correo, se le asignan valores ficticios
    (solo cuentas creadas por la prueba).
    """
    carrera = carrera or crear_carrera()
    cambios = []
    if not user.cedula:
        user.cedula = str(next(_cedulas))
        cambios.append("cedula")
    if not user.email:
        user.email = f"{user.username}@prueba.unl.edu.ec"
        cambios.append("email")
    if cambios:
        user.save(update_fields=cambios)
    datos = {
        "identificacion": user.cedula,
        "nombres": "Nombre",
        "apellidos": "Ficticio",
        "correo_institucional": user.email,
        "codigo_carrera": carrera.codigo,
        "codigo_facultad": carrera.facultad.codigo,
    }
    datos.update(campos)
    return PerfilSGASimulado.objects.create(**datos)
