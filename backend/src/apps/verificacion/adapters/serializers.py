"""Serializadores DRF del módulo verificación (T027/T028/T030)."""

from rest_framework import serializers

from apps.verificacion.adapters.models import (
    ChecklistVerification,
    ObservacionAccionable,
)
from apps.peticiones.adapters.models import DocumentoEntregado


class ChecklistVerificationSerializer(serializers.ModelSerializer):
    """Serializador de verificación de checklist."""

    requisito_codigo = serializers.CharField(source="requisito.codigo_requisito", read_only=True)
    requisito_nombre = serializers.CharField(source="requisito.nombre", read_only=True)
    evaluado_por_username = serializers.CharField(source="evaluado_por.username", read_only=True, allow_null=True)
    evaluado_por = serializers.SerializerMethodField()

    class Meta:
        model = ChecklistVerification
        fields = [
            "id",
            "expediente",
            "requisito",
            "requisito_codigo",
            "requisito_nombre",
            "estado_verificacion",
            "evaluado_por",
            "evaluado_por_username",
            "fecha_evaluacion",
            "fecha_creacion",
            "fecha_actualizacion",
        ]
        read_only_fields = fields

    def get_evaluado_por(self, obj):
        if obj.evaluado_por:
            return str(obj.evaluado_por.pk)
        return None


class ChecklistEvaluationSerializer(serializers.Serializer):
    """Entrada para PUT /api/v1/checklist/{id}/ (T027)."""

    estado_verificacion = serializers.ChoiceField(
        choices=["VERIFICADO", "OBSERVADO"],
        help_text="Estado de la verificación: VERIFICADO u OBSERVADO"
    )
    motivo_observacion = serializers.CharField(
        required=False,
        allow_blank=False,
        help_text="Obligatorio si estado_verificacion es OBSERVADO"
    )

    def validate(self, data):
        estado = data.get("estado_verificacion")
        motivo = data.get("motivo_observacion")
        
        if estado == "OBSERVADO" and not motivo:
            raise serializers.ValidationError(
                "El motivo_observacion es obligatorio cuando el estado es OBSERVADO."
            )
        
        return data


class ChecklistListSerializer(serializers.ModelSerializer):
    """Serializador para listado de checklist de un expediente."""

    requisito_codigo = serializers.CharField(source="requisito.codigo_requisito", read_only=True)
    requisito_nombre = serializers.CharField(source="requisito.nombre", read_only=True)
    requisito_descripcion = serializers.CharField(source="requisito.descripcion", read_only=True)

    class Meta:
        model = ChecklistVerification
        fields = [
            "id",
            "requisito",
            "requisito_codigo",
            "requisito_nombre",
            "requisito_descripcion",
            "estado_verificacion",
            "evaluado_por",
            "fecha_evaluacion",
        ]
        read_only_fields = fields


class ObservacionRegistroSerializer(serializers.Serializer):
    """Entrada para POST /api/v1/expedientes/{id}/observar/ (T028)."""

    motivo_observacion = serializers.CharField(
        help_text="Motivo de la observación (obligatorio)",
        allow_blank=False,
    )


class ObservacionResponseSerializer(serializers.ModelSerializer):
    """Salida para observación registrada."""

    requisito_codigo = serializers.CharField(source="requisito.codigo_requisito", read_only=True)
    requisito_nombre = serializers.CharField(source="requisito.nombre", read_only=True)
    peticion_id = serializers.UUIDField(source="peticion.id", read_only=True)
    observacion_id = serializers.UUIDField(source="observacion.id", read_only=True)

    class Meta:
        model = ChecklistVerification
        fields = [
            "id",
            "expediente",
            "requisito",
            "requisito_codigo",
            "requisito_nombre",
            "estado_verificacion",
            "evaluado_por",
            "fecha_evaluacion",
            "peticion_id",
            "observacion_id",
        ]
        read_only_fields = fields


class ObservacionAccionableSerializer(serializers.ModelSerializer):
    """Serializador de observación accionable."""

    registrada_por_username = serializers.CharField(source="registrada_por.username", read_only=True)
    peticion_requisito_nombre = serializers.CharField(source="peticion.requisito.nombre", read_only=True)

    class Meta:
        model = ObservacionAccionable
        fields = [
            "id",
            "expediente",
            "peticion",
            "peticion_requisito_nombre",
            "registrada_por",
            "registrada_por_username",
            "motivo_observacion",
            "fecha_registro",
            "resuelta",
            "fecha_resolucion",
            "fecha_creacion",
            "fecha_actualizacion",
        ]
        read_only_fields = fields


class SubsanacionSerializer(serializers.Serializer):
    """Entrada para POST /api/v1/checklist/{id}/subsanar/ (T030)."""

    archivo = serializers.FileField()

    def validate_archivo(self, value):
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError(
                "El archivo excede el límite máximo de 10 MB (RNF-004)."
            )
        return value


class SubsanacionResponseSerializer(serializers.ModelSerializer):
    """Salida 201 de subsanación."""

    subido_por_username = serializers.CharField(source="subido_por.username", read_only=True)

    class Meta:
        model = DocumentoEntregado
        fields = [
            "id",
            "peticion",
            "version",
            "archivo_path",
            "nombre_original",
            "tamanio_bytes",
            "hash_sha256",
            "tipo_mime",
            "subido_por",
            "subido_por_username",
            "fecha_carga",
            "es_vigente",
        ]
        read_only_fields = fields