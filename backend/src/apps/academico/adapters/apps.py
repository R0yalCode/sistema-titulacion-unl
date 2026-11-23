from django.apps import AppConfig


class AcademicoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.academico.adapters"
    label = "academico"
    verbose_name = "Catálogo y perfil académico"
