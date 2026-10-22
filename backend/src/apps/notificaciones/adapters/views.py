"""Adaptador HTTP del módulo notificaciones (T038).

Endpoints:
- GET /api/v1/notificaciones/ (lista notificaciones del usuario autenticado)
- PATCH /api/v1/notificaciones/{id}/marcar-leida/ (marcar como leída)
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.authentication.adapters.permissions import HasRolePermission
from apps.notificaciones.adapters.models import NotificacionInterna
from apps.notificaciones.services import marcar_como_leida
from core.adapters.scope_filter import ScopeFilterMixin

from .serializers import NotificacionInternaSerializer


class NotificacionViewSet(ScopeFilterMixin, viewsets.ReadOnlyModelViewSet):
    """Gestión de notificaciones internas (T038)."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    rbac_resource = "notificaciones"
    queryset = NotificacionInterna.objects.select_related("expediente", "peticion", "peticion__requisito")
    serializer_class = NotificacionInternaSerializer
    scope_owner_field = "usuario_destino_id"
    pagination_class = None  # Deshabilitar paginación para pruebas simples

    def get_rbac_resource(self):
        return "notificaciones"

    def get_queryset(self):
        """Filtrar notificaciones por usuario autenticado."""
        return self.scope_queryset(self.queryset, self.request).filter(
            usuario_destino=self.request.user
        )

    def list(self, request, *args, **kwargs):
        """GET /api/v1/notificaciones/ (T038).

        Retorna lista de notificaciones del usuario autenticado,
        con estado leida=False por defecto.
        """
        # Permitir filtro opcional por leida
        leida_param = request.query_params.get("leida")
        queryset = self.get_queryset()

        if leida_param is not None:
            if leida_param.lower() == "true":
                queryset = queryset.filter(leida=True)
            elif leida_param.lower() == "false":
                queryset = queryset.filter(leida=False)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"results": serializer.data})

    @action(detail=True, methods=["patch"], url_path="marcar-leida")
    def marcar_leida(self, request, pk=None):
        """PATCH /api/v1/notificaciones/{id}/marcar-leida/ (T038).

        Marca una notificación como leída.
        """
        notificacion = self.get_object()

        # Verificar que la notificación pertenece al usuario autenticado
        if notificacion.usuario_destino != request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("No tienes permiso para marcar esta notificación como leída.")

        from apps.notificaciones.services import marcar_como_leida
        exito = marcar_como_leida(str(notificacion.id), request.user)

        if not exito:
            from rest_framework.exceptions import NotFound
            raise NotFound("La notificación no existe o no pertenece al usuario.")

        # Refrescar la notificación para obtener el estado actualizado
        notificacion.refresh_from_db()

        # Retornar la notificación actualizada
        serializer = self.get_serializer(notificacion)
        return Response(serializer.data, status=status.HTTP_200_OK)