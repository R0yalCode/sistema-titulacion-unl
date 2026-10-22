"""Semilla del catalogo base: los 5 requisitos obligatorios de la
Declaratoria de Aptitud Legal (Art. 235 RRA-UNL; RN-001 de
specify.md).

Los `rol_emisor_sugerido` son valores configurables del catalogo
(specify.md 7.1 los expone al ADMINISTRADOR via /api/v1/catalogos/)
y no condicionan la logica del backend.
"""

from django.db import migrations

REQUISITOS_BASE_ART235 = [
    (
        "ART235-01-RECORD-ACADEMICO",
        "Récord académico legalizado",
        "Récord académico legalizado otorgado por la Secretaría de Carrera.",
        "SECRETARIA_CARRERA",
    ),
    (
        "ART235-02-PRACTICAS-VINCULACION",
        "Certificado de prácticas o vinculación",
        "Certificado de prácticas preprofesionales o vinculación emitido por la unidad responsable.",
        "RESPONSABLE_DEPENDENCIA",
    ),
    (
        "ART235-03-IDIOMA-B1",
        "Certificado de idioma nivel B1",
        "Certificado de dominio de idioma extranjero nivel B1.",
        "RESPONSABLE_DEPENDENCIA",
    ),
    (
        "ART235-04-DIRECTOR-TRABAJO",
        "Certificado del Director de Trabajo",
        "Certificado de aprobación del tema y director de trabajo de titulación.",
        "DIRECTOR_CARRERA",
    ),
    (
        "ART235-05-TESORERIA",
        "Certificado de no adeudar (Tesorería)",
        "Certificado de Tesorería que acredita no adeudar a la Universidad.",
        "RESPONSABLE_DEPENDENCIA",
    ),
]


def seed_catalogo_base(apps, schema_editor):
    CatalogoDocumental = apps.get_model("peticiones", "CatalogoDocumental")
    for codigo, nombre, descripcion, rol in REQUISITOS_BASE_ART235:
        CatalogoDocumental.objects.get_or_create(
            codigo_requisito=codigo,
            defaults={
                "nombre": nombre,
                "descripcion": descripcion,
                "es_obligatorio_base": True,
                "fase": "FASE_1",
                "rol_emisor_sugerido": rol,
                "activo": True,
            },
        )


def despoblar_catalogo_base(apps, schema_editor):
    CatalogoDocumental = apps.get_model("peticiones", "CatalogoDocumental")
    CatalogoDocumental.objects.filter(
        codigo_requisito__in=[r[0] for r in REQUISITOS_BASE_ART235]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("peticiones", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_catalogo_base, despoblar_catalogo_base),
    ]
