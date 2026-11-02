"""Serializadores DRF del modulo peticiones (T021/T023; HU-002, HU-003)."""

from rest_framework import serializers

from apps.peticiones.adapters.models import (
    CatalogoDocumental,
    DocumentoEntregado,
    PeticionDocumental,
)


class CatalogoDocumentalSerializer(serializers.ModelSerializer):
    """Serializador basico del catalogo de requisitos."""

    class Meta:
        model = CatalogoDocumental
        fields = [
            "id",
            "codigo_requisito",
            "nombre",
            "descripcion",
            "es_obligatorio_base",
            "fase",
            "rol_emisor_sugerido",
            "activo",
        ]
        read_only_fields = fields


class PeticionDocumentalSerializer(serializers.ModelSerializer):
    """Serializador de peticion documental con datos del requisito."""

    requisito_codigo = serializers.CharField(source="requisito.codigo_requisito", read_only=True)
    requisito_nombre = serializers.CharField(source="requisito.nombre", read_only=True)
    requisito_descripcion = serializers.CharField(source="requisito.descripcion", read_only=True)
    dependencia_emisora_display = serializers.CharField(source="get_dependencia_emisora_display", read_only=True)

    class Meta:
        model = PeticionDocumental
        fields = [
            "id",
            "expediente",
            "requisito",
            "requisito_codigo",
            "requisito_nombre",
            "requisito_descripcion",
            "estado_peticion",
            "dependencia_emisora",
            "dependencia_emisora_display",
            "fecha_solicitud",
            "fecha_actualizacion",
        ]
        read_only_fields = fields


class SolicitarEmisionSerializer(serializers.Serializer):
    """Entrada para POST /api/v1/peticiones/{id}/solicitar-emision/ (T021)."""

    pass


class SolicitarEmisionResponseSerializer(serializers.ModelSerializer):
    """Salida 200 de solicitar emision: peticion actualizada + notificacion creada."""

    requisito_codigo = serializers.CharField(source="requisito.codigo_requisito", read_only=True)
    requisito_nombre = serializers.CharField(source="requisito.nombre", read_only=True)

    class Meta:
        model = PeticionDocumental
        fields = [
            "id",
            "requisito_codigo",
            "requisito_nombre",
            "estado_peticion",
            "dependencia_emisora",
            "fecha_solicitud",
        ]
        read_only_fields = fields


class DocumentoEntregadoSerializer(serializers.ModelSerializer):
    """Serializador de documento entregado (T023)."""

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


class CargarDocumentoSerializer(serializers.Serializer):
    """Entrada multipart para POST /api/v1/peticiones/{id}/documento/ (T023)."""

    archivo = serializers.FileField()

    def validate_archivo(self, value):
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError(
                "El archivo excede el limite maximo de 10 MB (RNF-004)."
            )
        return value


class CargarDocumentoResponseSerializer(serializers.ModelSerializer):
    """Salida 201 de carga de documento."""

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