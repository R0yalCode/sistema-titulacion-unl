"""Contrato de `GET /api/v1/perfil-academico/` (salida, solo lectura)."""

from rest_framework import serializers

from apps.academico.domain.perfil import EstadoPerfil


class EstudiantePerfilSerializer(serializers.Serializer):
    identificacion = serializers.CharField()
    nombres = serializers.CharField(allow_blank=True)
    apellidos = serializers.CharField(allow_blank=True)
    correo_institucional = serializers.CharField(allow_blank=True)


class CarreraPerfilSerializer(serializers.Serializer):
    id = serializers.UUIDField(format="hex_verbose")
    codigo = serializers.CharField()
    nombre = serializers.CharField()
    activa = serializers.BooleanField()


class FacultadPerfilSerializer(serializers.Serializer):
    id = serializers.UUIDField(format="hex_verbose")
    codigo = serializers.CharField()
    nombre = serializers.CharField()
    activa = serializers.BooleanField()


class FuentePerfilSerializer(serializers.Serializer):
    codigo = serializers.CharField(
        help_text="Código estable de la fuente, p. ej. MOCK_SGA."
    )
    nombre = serializers.CharField()
    es_simulada = serializers.BooleanField(
        help_text="True si los datos NO provienen de un sistema institucional real."
    )


class MotivoBloqueoSerializer(serializers.Serializer):
    codigo = serializers.CharField()
    mensaje = serializers.CharField()


class PerfilAcademicoSerializer(serializers.Serializer):
    """Perfil académico del estudiante autenticado.

    `estudiante`, `carrera` y `facultad` son nulos cuando la fuente no tiene
    la información. `puede_iniciar_tramite` combina el perfil validado con
    la regla RN-001 (sin expediente activo).
    """

    estudiante = EstudiantePerfilSerializer(allow_null=True)
    carrera = CarreraPerfilSerializer(allow_null=True)
    facultad = FacultadPerfilSerializer(allow_null=True)
    fuente = FuentePerfilSerializer()
    consultado_en = serializers.DateTimeField()
    estado_perfil = serializers.ChoiceField(choices=[e.value for e in EstadoPerfil])
    perfil_validado = serializers.BooleanField()
    puede_iniciar_tramite = serializers.BooleanField()
    motivos_bloqueo = MotivoBloqueoSerializer(many=True)
