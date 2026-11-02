"""Serializadores DRF del módulo notificaciones (T038)."""

from rest_framework import serializers

from apps.notificaciones.adapters.models import NotificacionInterna


class NotificacionInternaSerializer(serializers.ModelSerializer):
    """Serializador de notificación interna."""

    expediente_numero = serializers.CharField(source="expediente.numero_expediente", read_only=True)
    peticion_requisito_nombre = serializers.CharField(source="peticion.requisito.nombre", read_only=True, allow_null=True)

    class Meta:
        model = NotificacionInterna
        fields = [
            "id",
            "expediente",
            "expediente_numero",
            "peticion",
            "peticion_requisito_nombre",
            "titulo",
            "mensaje",
            "leida",
            "fecha_creacion",
        ]
        read_only_fields = fields


class NotificacionMarcarLeidaSerializer(serializers.Serializer):
    """Serializador para marcar notificación como leída."""

    pass  # No se requiere body, solo el ID en la URL