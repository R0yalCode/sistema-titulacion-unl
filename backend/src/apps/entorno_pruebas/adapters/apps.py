from django.apps import AppConfig


class EntornoPruebasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.entorno_pruebas.adapters"
    label = "entorno_pruebas"
    verbose_name = "Dataset del entorno local de pruebas"
