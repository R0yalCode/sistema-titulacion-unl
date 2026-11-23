from django.contrib import admin
from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from apps.authentication.adapters.views import (
    LoginView,
    LogoutView,
    MfaRecoveryView,
    MfaResetConfirmView,
    MfaResetRequestView,
    MfaSetupConfirmView,
    MfaSetupView,
    MfaVerifyView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    PasswordResetValidateView,
)
from apps.academico.adapters.views import PerfilAcademicoView
from apps.expedientes.adapters.views import (
    BandejaExpedienteViewSet,
    ExpedienteViewSet,
    MiTramiteView,
)
from apps.peticiones.adapters.views import PeticionViewSet
from apps.verificacion.adapters.views import (
    ChecklistListViewSet,
    ChecklistViewSet,
    ObservacionViewSet,
)
from apps.resoluciones.adapters.views import (
    InformeViewSet,
    DeclaratoriaViewSet,
)
from apps.notificaciones.adapters.views import NotificacionViewSet
from core.adapters.health import health

urlpatterns = [
    # Healthcheck del contenedor (SEC-T001): sin autenticación, sin datos.
    path("health/", health, name="health"),
    # Consola interna de administración (ADR-0009): solo staff/superuser,
    # sin exposición operativa del trámite.
    path("admin/", admin.site.urls),
    # Inicio de sesión en dos pasos (AUTH-B). Sustituye a /auth/token/, que
    # emitía el JWT sin segundo factor.
    path("api/v1/auth/login/", LoginView.as_view(), name="auth-login"),
    path("api/v1/auth/mfa/setup/", MfaSetupView.as_view(), name="auth-mfa-setup"),
    path(
        "api/v1/auth/mfa/setup/confirm/",
        MfaSetupConfirmView.as_view(),
        name="auth-mfa-setup-confirm",
    ),
    path("api/v1/auth/mfa/verify/", MfaVerifyView.as_view(), name="auth-mfa-verify"),
    path(
        "api/v1/auth/mfa/recovery/",
        MfaRecoveryView.as_view(),
        name="auth-mfa-recovery",
    ),
    # Restablecimiento del 2FA por enlace (MFA-RST).
    path(
        "api/v1/auth/mfa/reset/",
        MfaResetRequestView.as_view(),
        name="auth-mfa-reset",
    ),
    path(
        "api/v1/auth/mfa/reset/confirm/",
        MfaResetConfirmView.as_view(),
        name="auth-mfa-reset-confirm",
    ),
    path("api/v1/auth/logout/", LogoutView.as_view(), name="auth-logout"),
    # Recuperación de contraseña (AUTH-RC): públicos, throttle por IP.
    path(
        "api/v1/auth/password-reset/",
        PasswordResetRequestView.as_view(),
        name="auth-password-reset",
    ),
    path(
        "api/v1/auth/password-reset/validate/",
        PasswordResetValidateView.as_view(),
        name="auth-password-reset-validate",
    ),
    path(
        "api/v1/auth/password-reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="auth-password-reset-confirm",
    ),
    path(
        "api/v1/expedientes/",
        ExpedienteViewSet.as_view({"post": "create"}),
        name="expedientes-list",
    ),
    path(
        "api/v1/expedientes/bandeja/",
        BandejaExpedienteViewSet.as_view({"get": "list"}),
        name="expedientes-bandeja",
    ),
    path(
        "api/v1/perfil-academico/",
        PerfilAcademicoView.as_view(),
        name="perfil-academico",
    ),
    path(
        "api/v1/expedientes/mi-tramite/",
        MiTramiteView.as_view(),
        name="expedientes-mi-tramite",
    ),
    path(
        "api/v1/expedientes/<uuid:pk>/",
        ExpedienteViewSet.as_view({"get": "retrieve"}),
        name="expedientes-detail",
    ),
    path(
        "api/v1/expedientes/<uuid:pk>/enviar/",
        ExpedienteViewSet.as_view({"post": "enviar"}),
        name="expedientes-enviar",
    ),
    path(
        "api/v1/expedientes/<uuid:pk>/iniciar-verificacion/",
        ExpedienteViewSet.as_view({"post": "iniciar_verificacion"}),
        name="expedientes-iniciar-verificacion",
    ),
    path(
        "api/v1/expedientes/<uuid:expediente_id>/checklist/",
        ChecklistListViewSet.as_view({"get": "list"}),
        name="expedientes-checklist",
    ),
    path(
        "api/v1/checklist/<uuid:pk>/",
        ChecklistViewSet.as_view({"put": "update"}),
        name="checklist-evaluar",
    ),
    path(
        "api/v1/checklist/<uuid:pk>/subsanar/",
        ChecklistViewSet.as_view({"post": "subsanar"}),
        name="checklist-subsanar",
    ),
    path(
        "api/v1/expedientes/<uuid:pk>/observar/",
        ExpedienteViewSet.as_view({"post": "observar"}),
        name="expedientes-observar",
    ),
    path(
        "api/v1/informes/",
        InformeViewSet.as_view({"post": "create"}),
        name="informes-create",
    ),
    path(
        "api/v1/declaratorias/",
        DeclaratoriaViewSet.as_view({"post": "create"}),
        name="declaratorias-create",
    ),
    path(
        "api/v1/notificaciones/",
        NotificacionViewSet.as_view({"get": "list"}),
        name="notificaciones-list",
    ),
    path(
        "api/v1/notificaciones/<uuid:pk>/marcar-leida/",
        NotificacionViewSet.as_view({"patch": "marcar_leida"}),
        name="notificaciones-marcar-leida",
    ),
    path(
        "api/v1/peticiones/<uuid:pk>/solicitar-emision/",
        PeticionViewSet.as_view({"post": "solicitar_emision"}),
        name="peticiones-solicitar-emision",
    ),
    path(
        "api/v1/peticiones/<uuid:pk>/documento/",
        PeticionViewSet.as_view(
            {"get": "descargar_documento", "post": "cargar_documento"}
        ),
        name="peticiones-documento",
    ),
    path(
        "api/v1/peticiones/<uuid:pk>/documento/<int:version>/",
        PeticionViewSet.as_view({"get": "descargar_documento"}),
        name="peticiones-descargar-documento",
    ),
    # OpenAPI Schema endpoints
    path(
        "api/v1/schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),
    path(
        "api/v1/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/v1/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
