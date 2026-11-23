"""Consulta de solo lectura del marcador del dataset (ADR-0009)."""

from django.contrib import admin

from apps.entorno_pruebas.adapters.models import RegistroDatasetSintetico


@admin.register(RegistroDatasetSintetico)
class RegistroDatasetSinteticoAdmin(admin.ModelAdmin):
    list_display = ("lote", "clave", "objeto", "objeto_id", "creado_en")
    list_filter = ("lote", "objeto")
    search_fields = ("clave", "objeto_id")
    readonly_fields = ("id", "lote", "objeto", "objeto_id", "clave", "creado_en")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
