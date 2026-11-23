from django.db import migrations, models

INSTALAR_POSTGRES = """
CREATE FUNCTION sgt_identidad_entorno_inmutable() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    IF TG_OP = 'TRUNCATE' AND NOT EXISTS (SELECT 1 FROM sgt_identidad_entorno) THEN
        RETURN NULL;
    END IF;
    RAISE EXCEPTION 'La identidad de entorno de la base es inmutable.';
END;
$$;
CREATE TRIGGER sgt_identidad_entorno_sin_cambios
    BEFORE UPDATE OR DELETE ON sgt_identidad_entorno
    FOR EACH ROW EXECUTE FUNCTION sgt_identidad_entorno_inmutable();
CREATE TRIGGER sgt_identidad_entorno_sin_truncate
    BEFORE TRUNCATE ON sgt_identidad_entorno
    FOR EACH STATEMENT EXECUTE FUNCTION sgt_identidad_entorno_inmutable();
"""

RETIRAR_POSTGRES = """
DROP TRIGGER sgt_identidad_entorno_sin_truncate ON sgt_identidad_entorno;
DROP TRIGGER sgt_identidad_entorno_sin_cambios ON sgt_identidad_entorno;
DROP FUNCTION sgt_identidad_entorno_inmutable();
"""


def instalar_triggers(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(INSTALAR_POSTGRES)


def retirar_triggers(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(RETIRAR_POSTGRES)


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0003_acceso_correo_institucional"),
    ]

    operations = [
        migrations.CreateModel(
            name="IdentidadEntornoBD",
            fields=[
                (
                    "id",
                    models.PositiveSmallIntegerField(
                        default=1, editable=False, primary_key=True, serialize=False
                    ),
                ),
                (
                    "entorno",
                    models.CharField(
                        choices=[
                            ("desarrollo", "Desarrollo"),
                            ("produccion", "Producción"),
                        ],
                        max_length=16,
                    ),
                ),
                ("base_registrada", models.CharField(max_length=128)),
                ("registrada_en", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "sgt_identidad_entorno",
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(("id", 1)),
                        name="identidad_entorno_fila_unica",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(("entorno__in", ["desarrollo", "produccion"])),
                        name="identidad_entorno_valor_valido",
                    ),
                ],
            },
        ),
        migrations.RunPython(instalar_triggers, retirar_triggers),
    ]
