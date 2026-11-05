"""Administración de notificaciones y auditoría (S1-T04; ADR-0009).

EventoAuditoria es una bitácora inmutable (P-08): solo consulta, sin
agregar, editar ni eliminar. Las notificaciones no se editan desde la
consola; la marca de lectura es operación de la API.
"""

from django.contrib import admin

from apps.notificaciones.adapters.models import EventoAuditoria, NotificacionInterna


@admin.register(NotificacionInterna)
class NotificacionInternaAdmin(admin.ModelAdmin):
    list_display = ("usuario_destino", "titulo", "expediente", "leida", "fecha_creacion")
    search_fields = ("titulo", "usuario_destino__username")
    list_filter = ("leida",)
    ordering = ("-fecha_creacion",)
    date_hierarchy = "fecha_creacion"
    readonly_fields = ("usuario_destino", "expediente", "peticion", "titulo", "mensaje", "leida", "fecha_creacion")
    actions = None

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(EventoAuditoria)
class EventoAuditoriaAdmin(admin.ModelAdmin):
    list_display = ("usuario", "rol_usuario", "accion", "expediente", "ip", "timestamp")
    search_fields = ("usuario__username", "accion")
    list_filter = ("rol_usuario", "accion")
    ordering = ("-timestamp",)
    date_hierarchy = "timestamp"
    actions = None

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
