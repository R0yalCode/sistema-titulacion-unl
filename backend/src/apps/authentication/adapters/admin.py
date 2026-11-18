"""Administración de usuarios y roles (S1-T04; ADR-0009).

Consola interna de soporte: los actores del trámite operan por la API.
La contraseña y los roles se gestionan con controles de solo lectura
según el perfil administrativo.
"""

from django.contrib import admin, messages

from apps.authentication.adapters.models import (
    EventoAutenticacion,
    Role,
    TrustedDevice,
    User,
    UserRole,
)


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
    actions = ("restablecer_doble_factor",)

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

    @admin.action(description="Restablecer doble factor (2FA) de los seleccionados")
    def restablecer_doble_factor(self, request, queryset):
        """Soporte ante pérdida del teléfono sin códigos de recuperación.

        Antes de usarla, el personal verifica la identidad del titular por
        un canal institucional (docs/autenticacion/politica-2fa.md). Retira
        el autenticador, los códigos y la confianza de todos sus
        dispositivos; queda auditado con el actor.
        """
        from apps.authentication.services.mfa import restablecer_mfa

        for usuario in queryset:
            restablecer_mfa(usuario, request, actor=request.user)
        self.message_user(
            request,
            f"Doble factor restablecido para {queryset.count()} usuario(s). "
            "Deberán registrar un autenticador nuevo en su próximo ingreso.",
            messages.SUCCESS,
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


class _SoloLecturaAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(EventoAutenticacion)
class EventoAutenticacionAdmin(_SoloLecturaAdmin):
    list_display = ("created_at", "tipo", "user", "ip")
    list_filter = ("tipo",)
    search_fields = ("user__username",)
    ordering = ("-created_at",)


@admin.register(TrustedDevice)
class TrustedDeviceAdmin(_SoloLecturaAdmin):
    """Consulta de dispositivos de confianza (sin el hash del token)."""

    list_display = ("user", "created_at", "expires_at", "last_used_at", "revoked_at")
    fields = (
        "user",
        "user_agent",
        "ip",
        "created_at",
        "expires_at",
        "last_used_at",
        "revoked_at",
    )
    search_fields = ("user__username",)
    ordering = ("-created_at",)
