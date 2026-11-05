"""Administración de usuarios y roles (S1-T04; ADR-0009).

Consola interna de soporte: los actores del trámite operan por la API.
La contraseña y los roles se gestionan con controles de solo lectura
según el perfil administrativo.
"""

from django.contrib import admin

from apps.authentication.adapters.models import Role, User, UserRole


class UserRoleInline(admin.TabularInline):
    model = UserRole
    extra = 0
    autocomplete_fields = ["role"]


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "get_full_name_display", "cedula", "is_active", "is_staff")
    search_fields = ("username", "cedula", "first_name", "last_name", "email")
    list_filter = ("is_active", "is_staff", "is_superuser")
    ordering = ("username",)
    readonly_fields = ("last_login", "date_joined")
    inlines = (UserRoleInline,)

    fieldsets = (
        (
            "Identidad",
            {"fields": ("username", "first_name", "last_name", "email", "cedula", "carrera_id", "facultad_id")},
        ),
        (
            "Cuenta",
            {"fields": ("password", "is_active", "is_staff", "is_superuser", "last_login", "date_joined")},
        ),
    )

    @admin.display(description="Nombre completo")
    def get_full_name_display(self, obj):
        return obj.get_full_name() or obj.username

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return self.readonly_fields
        return self.readonly_fields + ("username",)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)
    ordering = ("name",)

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "fecha_asignacion")
    autocomplete_fields = ("user", "role")
    readonly_fields = ("fecha_asignacion",)
    ordering = ("user__username",)

    def has_delete_permission(self, request, obj=None):
        return False
