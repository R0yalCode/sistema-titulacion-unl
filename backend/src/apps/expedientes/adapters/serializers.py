"""Serializadores DRF del modulo expedientes (T015/T016; HU-001, HU-004)."""

from rest_framework import serializers

from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.peticiones.adapters.models import PeticionDocumental


class PeticionInicializadaSerializer(serializers.ModelSerializer):
    requisito_codigo = serializers.CharField(source="requisito.codigo_requisito")
    requisito_nombre = serializers.CharField(source="requisito.nombre")

    class Meta:
        model = PeticionDocumental
        fields = [
            "id",
            "requisito_codigo",
            "requisito_nombre",
            "estado_peticion",
            "dependencia_emisora",
        ]


class CrearExpedienteSerializer(serializers.Serializer):
    """Entrada del caso de uso (HU-001/RF-001): cuerpo vacío `{}`.

    El estudiante es el usuario autenticado; la carrera y la facultad se
    obtienen de su perfil académico validado en el servidor. Enviar
    `carrera_id`, `facultad_id` o `estudiante_id` responde 400
    `campo_no_permitido`.
    """


class ExpedienteBorradorSerializer(serializers.ModelSerializer):
    """Salida 201: objeto expediente con sus 5 peticiones inicializadas."""

    estudiante_id = serializers.UUIDField(format="hex_verbose")
    carrera_id = serializers.UUIDField(format="hex_verbose")
    peticiones = PeticionInicializadaSerializer(
        many=True,
        read_only=True,
        source="peticiones_documentales",
    )

    class Meta:
        model = ExpedienteTitulacion
        fields = [
            "id",
            "numero_expediente",
            "estudiante_id",
            "carrera_id",
            "estado",
            "activa",
            "fecha_creacion",
            "peticiones",
        ]
        read_only_fields = fields


class ExpedienteEnviadoSerializer(serializers.ModelSerializer):
    """Salida 200 de `POST /api/v1/expedientes/{id}/enviar/` (CA-001)."""

    estudiante_id = serializers.UUIDField(format="hex_verbose")
    carrera_id = serializers.UUIDField(format="hex_verbose")
    peticiones = PeticionInicializadaSerializer(
        many=True,
        read_only=True,
        source="peticiones_documentales",
    )

    class Meta:
        model = ExpedienteTitulacion
        fields = [
            "id",
            "numero_expediente",
            "estudiante_id",
            "carrera_id",
            "estado",
            "activa",
            "fecha_creacion",
            "fecha_recepcion",
            "numero_providencia",
            "fecha_limite_atencion",
            "dias_laborables_acumulados",
            "peticiones",
        ]
        read_only_fields = fields


class ExpedienteDetalleSerializer(serializers.ModelSerializer):
    """Detalle completo del expediente para GET /api/v1/expedientes/{id}/ (T018; EX-003, CA-008)."""

    estudiante_id = serializers.UUIDField(format="hex_verbose")
    carrera_id = serializers.UUIDField(format="hex_verbose")
    facultad_id = serializers.UUIDField(format="hex_verbose")
    peticiones = PeticionInicializadaSerializer(
        many=True,
        read_only=True,
        source="peticiones_documentales",
    )

    class Meta:
        model = ExpedienteTitulacion
        fields = [
            "id",
            "numero_expediente",
            "estudiante_id",
            "carrera_id",
            "facultad_id",
            "estado",
            "activa",
            "fecha_creacion",
            "fecha_recepcion",
            "numero_providencia",
            "fecha_limite_atencion",
            "dias_laborables_acumulados",
            "peticiones",
        ]
        read_only_fields = fields


class BandejaExpedienteSerializer(serializers.ModelSerializer):
    """Item de la bandeja operativa (T017; HU-005, RF-012)."""

    estudiante_id = serializers.UUIDField(format="hex_verbose")

    class Meta:
        model = ExpedienteTitulacion
        fields = [
            "id",
            "numero_expediente",
            "estudiante_id",
            "carrera_id",
            "facultad_id",
            "estado",
            "fecha_creacion",
            "fecha_recepcion",
            "numero_providencia",
            "fecha_limite_atencion",
        ]
        read_only_fields = fields
