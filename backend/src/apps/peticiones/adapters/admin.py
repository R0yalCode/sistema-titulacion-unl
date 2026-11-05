"""Administración de catálogo, peticiones y documentos (S1-T04; ADR-0009).

El catálogo documental es un parámetro configurable de responsabilidad del
ADMINISTRADOR. Los documentos entregados y su integridad (hash_sha256) son
solo lectura; no se registran archivos desde la consola.
"""

from django.contrib import admin

from apps.peticiones.adapters.models import (
    CatalogoDocumental,
    DocumentoEntregado,
    PeticionDocumental,
)


@admin.register(CatalogoDocumental)
class CatalogoDocumentalAdmin(admin.ModelAdmin):
    list_display = ("codigo_requisito", "nombre", "es_obligatorio_base", "rol_emisor_sugerido", "activo")
    search_fields = ("codigo_requisito", "nombre")
    list_filter = ("es_obligatorio_base", "fase", "activo")
    ordering = ("codigo_requisito",)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PeticionDocumental)
class PeticionDocumentalAdmin(admin.ModelAdmin):
    list_display = ("id", "expediente", "requisito", "estado_peticion", "dependencia_emisora", "fecha_solicitud")
    search_fields = ("expediente__numero_expediente", "requisito__codigo_requisito")
    list_filter = ("estado_peticion", "dependencia_emisora")
    ordering = ("-fecha_actualizacion",)
    readonly_fields = ("estado_peticion", "expediente", "requisito", "dependencia_emisora", "fecha_solicitud", "fecha_actualizacion")
    actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(DocumentoEntregado)
class DocumentoEntregadoAdmin(admin.ModelAdmin):
    list_display = ("peticion", "version", "nombre_original", "tamanio_bytes", "subido_por", "es_vigente", "fecha_carga")
    search_fields = ("peticion__expediente__numero_expediente", "nombre_original", "hash_sha256")
    list_filter = ("es_vigente", "tipo_mime")
    ordering = ("-fecha_carga",)
    readonly_fields = (
        "peticion",
        "version",
        "archivo_path",
        "nombre_original",
        "tamanio_bytes",
        "hash_sha256",
        "tipo_mime",
        "subido_por",
        "fecha_carga",
        "es_vigente",
    )
    actions = None

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
