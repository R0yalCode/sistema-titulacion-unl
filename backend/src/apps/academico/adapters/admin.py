"""Administración del catálogo académico y de la simulación MockSGA.

Consola interna (ADR-0009): solo personal con acceso al admin de Django.
Todo alta, cambio o baja queda en `EventoCatalogoAcademico` con el usuario
que lo hizo. Las facultades y carreras no se eliminan (se desactivan): los
expedientes conservan su referencia.
"""

from django.contrib import admin

from apps.academico.adapters.models import (
    Carrera,
    EventoCatalogoAcademico,
    Facultad,
    PerfilSGASimulado,
)
from apps.academico.services.auditoria import instantanea, registrar_cambio

ORIGEN_ADMIN = "admin"


class CambiosAuditadosAdmin(admin.ModelAdmin):
    """Registra en la bitácora cada alta, cambio o baja hecha desde el admin."""

    def save_model(self, request, obj, form, change):
        antes = {}
        if change:
            previo = type(obj).objects.filter(pk=obj.pk).first()
            antes = instantanea(previo) if previo is not None else {}
        super().save_model(request, obj, form, change)
        registrar_cambio(
            obj,
            tipo=(
                EventoCatalogoAcademico.Tipo.MODIFICADO
                if change
                else EventoCatalogoAcademico.Tipo.CREADO
            ),
            actor=request.user,
            origen=ORIGEN_ADMIN,
            antes=antes,
            campos_modificados=list(form.changed_data),
        )

    def delete_model(self, request, obj):
        registrar_cambio(
            obj,
            tipo=EventoCatalogoAcademico.Tipo.ELIMINADO,
            actor=request.user,
            origen=ORIGEN_ADMIN,
            antes=instantanea(obj),
        )
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            registrar_cambio(
                obj,
                tipo=EventoCatalogoAcademico.Tipo.ELIMINADO,
                actor=request.user,
                origen=ORIGEN_ADMIN,
                antes=instantanea(obj),
            )
        super().delete_queryset(request, queryset)


class SinEliminarAdmin(CambiosAuditadosAdmin):
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Facultad)
class FacultadAdmin(SinEliminarAdmin):
    list_display = ("codigo", "nombre", "activa", "es_simulada")
    list_filter = ("activa", "es_simulada")
    search_fields = ("codigo", "nombre")
    readonly_fields = ("id", "fecha_creacion", "fecha_actualizacion")


@admin.register(Carrera)
class CarreraAdmin(SinEliminarAdmin):
    list_display = ("codigo", "nombre", "facultad", "activa", "es_simulada")
    list_filter = ("activa", "es_simulada", "facultad")
    search_fields = ("codigo", "nombre")
    readonly_fields = ("id", "fecha_creacion", "fecha_actualizacion")


@admin.register(PerfilSGASimulado)
class PerfilSGASimuladoAdmin(CambiosAuditadosAdmin):
    list_display = ("identificacion", "codigo_carrera", "codigo_facultad", "activo")
    list_filter = ("activo", "codigo_carrera")
    search_fields = ("identificacion", "codigo_carrera")
    readonly_fields = ("id", "fecha_creacion", "fecha_actualizacion")


@admin.register(EventoCatalogoAcademico)
class EventoCatalogoAcademicoAdmin(admin.ModelAdmin):
    """Bitácora de solo lectura."""

    list_display = ("timestamp", "tipo", "objeto", "objeto_id", "actor", "origen")
    list_filter = ("tipo", "objeto", "origen")
    readonly_fields = (
        "id",
        "tipo",
        "objeto",
        "objeto_id",
        "actor",
        "origen",
        "timestamp",
        "detalles",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
