"""Administración de resoluciones (S1-T04; ADR-0009).

InformeAptitud y DeclaratoriaAptitud son inmutables por diseño (RN-004);
la consola es estrictamente de consulta. Los archivos privados nunca se
expuestan mediante enlaces (P-09).
"""

from django.contrib import admin

from apps.resoluciones.adapters.models import DeclaratoriaAptitud, InformeAptitud


class InformeAptitudReadOnlyAdmin(admin.ModelAdmin):
    """Base para modelos de resolución inmutables (consulta exclusiva)."""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(InformeAptitud)
class InformeAptitudAdmin(InformeAptitudReadOnlyAdmin):
    list_display = ("numero_providencia", "expediente", "emisor", "dictamen", "fecha_emision")
    search_fields = ("numero_providencia", "expediente__numero_expediente")
    list_filter = ("dictamen",)
    ordering = ("-fecha_emision",)
    date_hierarchy = "fecha_emision"
    actions = None


@admin.register(DeclaratoriaAptitud)
class DeclaratoriaAptitudAdmin(InformeAptitudReadOnlyAdmin):
    list_display = ("numero_memorando", "expediente", "decano", "fecha_declaratoria")
    search_fields = ("numero_memorando", "expediente__numero_expediente")
    ordering = ("-fecha_declaratoria",)
    date_hierarchy = "fecha_declaratoria"
    actions = None
