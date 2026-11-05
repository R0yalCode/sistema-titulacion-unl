"""Administración de verificaciones y observaciones (S1-T04; ADR-0009).

Los estados de verificación y la resolución de observaciones son
consecuencia de servicios de dominio (subsana/evaluar); la consola no
permite alterarlos manualmente (P-04/P-10).
"""

from django.contrib import admin

from apps.verificacion.adapters.models import (
    ChecklistVerification,
    ObservacionAccionable,
)


@admin.register(ChecklistVerification)
class ChecklistVerificationAdmin(admin.ModelAdmin):
    list_display = ("expediente", "requisito", "estado_verificacion", "evaluado_por", "fecha_evaluacion")
    search_fields = ("expediente__numero_expediente", "requisito__codigo_requisito")
    list_filter = ("estado_verificacion",)
    ordering = ("-fecha_creacion",)
    readonly_fields = (
        "expediente",
        "requisito",
        "estado_verificacion",
        "evaluado_por",
        "fecha_evaluacion",
        "fecha_creacion",
        "fecha_actualizacion",
    )
    actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ObservacionAccionable)
class ObservacionAccionableAdmin(admin.ModelAdmin):
    list_display = ("expediente", "peticion", "registrada_por", "resuelta", "fecha_registro")
    search_fields = ("expediente__numero_expediente", "motivo_observacion")
    list_filter = ("resuelta",)
    ordering = ("-fecha_registro",)
    date_hierarchy = "fecha_registro"
    readonly_fields = (
        "expediente",
        "peticion",
        "registrada_por",
        "motivo_observacion",
        "resuelta",
        "fecha_registro",
        "fecha_resolucion",
        "fecha_creacion",
        "fecha_actualizacion",
    )
    actions = None

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
