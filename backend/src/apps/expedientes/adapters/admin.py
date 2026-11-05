"""Administración de expedientes (S1-T04; ADR-0009).

Las transiciones de estado y el cálculo de plazos son controladas por
los servicios de dominio; el formulario administrativo no permite
editarlos. El historial es solo lectura (P-08).
"""

from django.contrib import admin

from apps.expedientes.adapters.models import ExpedienteTitulacion, HistorialEstado


class HistorialEstadoInline(admin.TabularInline):
    model = HistorialEstado
    extra = 0
    fields = ("estado_anterior", "estado_nuevo", "registrado_por", "fecha_cambio")
    readonly_fields = fields
    can_delete = False
    max_num = 0


@admin.register(ExpedienteTitulacion)
class ExpedienteTitulacionAdmin(admin.ModelAdmin):
    list_display = (
        "numero_expediente",
        "estado",
        "estudiante",
        "carrera_id",
        "fecha_recepcion",
        "fecha_limite_atencion",
        "activa",
    )
    search_fields = ("numero_expediente", "estudiante__username", "estudiante__cedula")
    list_filter = ("estado", "activa")
    ordering = ("-fecha_creacion",)
    date_hierarchy = "fecha_creacion"
    readonly_fields = (
        "estado",
        "numero_expediente",
        "numero_providencia",
        "fecha_creacion",
        "fecha_recepcion",
        "fecha_limite_atencion",
        "dias_laborables_acumulados",
        "fecha_ultima_pausa",
        "fecha_actualizacion",
    )
    inlines = (HistorialEstadoInline,)
    actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(HistorialEstado)
class HistorialEstadoAdmin(admin.ModelAdmin):
    list_display = ("expediente", "estado_anterior", "estado_nuevo", "registrado_por", "fecha_cambio")
    search_fields = ("expediente__numero_expediente", "registrado_por__username")
    list_filter = ("estado_nuevo",)
    date_hierarchy = "fecha_cambio"
    readonly_fields = (
        "expediente",
        "estado_anterior",
        "estado_nuevo",
        "registrado_por",
        "fecha_cambio",
    )
    actions = None

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
