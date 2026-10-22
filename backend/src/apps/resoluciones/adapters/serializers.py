"""Serializadores DRF del módulo resoluciones (T034/T035)."""

from rest_framework import serializers

from apps.resoluciones.adapters.models import InformeAptitud, DeclaratoriaAptitud


class InformeAptitudSerializer(serializers.ModelSerializer):
    """Serializador de InformeAptitud (Providencia N° 590)."""

    emisor_nombre = serializers.CharField(source="emisor.get_full_name", read_only=True)
    emisor_username = serializers.CharField(source="emisor.username", read_only=True)
    expediente_numero = serializers.CharField(source="expediente.numero_expediente", read_only=True)

    class Meta:
        model = InformeAptitud
        fields = [
            "id",
            "expediente",
            "expediente_numero",
            "numero_providencia",
            "emisor",
            "emisor_nombre",
            "emisor_username",
            "dictamen",
            "archivo_informe_path",
            "fecha_emision",
            "fecha_actualizacion",
        ]
        read_only_fields = fields


class DeclaratoriaAptitudSerializer(serializers.ModelSerializer):
    """Serializador de DeclaratoriaAptitud (Memorando N° 162)."""

    decano_nombre = serializers.CharField(source="decano.get_full_name", read_only=True)
    decano_username = serializers.CharField(source="decano.username", read_only=True)
    expediente_numero = serializers.CharField(source="expediente.numero_expediente", read_only=True)

    class Meta:
        model = DeclaratoriaAptitud
        fields = [
            "id",
            "expediente",
            "expediente_numero",
            "numero_memorando",
            "decano",
            "decano_nombre",
            "decano_username",
            "archivo_memorando_firmado_path",
            "fecha_declaratoria",
            "fecha_actualizacion",
        ]
        read_only_fields = fields