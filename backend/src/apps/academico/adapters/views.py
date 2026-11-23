"""`GET /api/v1/perfil-academico/`: perfil académico del estudiante autenticado.

Sin parámetros ni identificadores: el perfil se construye siempre sobre
`request.user` (su cédula), por lo que no puede consultarse el de otra
persona (sin superficie IDOR). Solo ESTUDIANTE (celda RBAC
`perfil_academico`).
"""

from dataclasses import asdict

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.academico.adapters.serializers import PerfilAcademicoSerializer
from apps.academico.domain.perfil import PerfilAcademico
from apps.academico.ports.fuente_academica import (
    FuenteAcademicaNoConfiguradaError,
    FuenteAcademicaNoDisponibleError,
)
from apps.academico.services.perfil_academico import get_academic_profile_service
from apps.authentication.adapters.permissions import HasRolePermission
from core.adapters.api_errors import ServicioNoDisponibleAPI

MOTIVO_EXPEDIENTE_ACTIVO = {
    "codigo": "expediente_activo_existente",
    "mensaje": (
        "Ya tiene un expediente de titulación activo; no puede iniciar otro "
        "trámite mientras esté en curso."
    ),
}


def error_fuente_academica(error: FuenteAcademicaNoDisponibleError):
    """503 con código estable según el fallo de la fuente académica."""
    if isinstance(error, FuenteAcademicaNoConfiguradaError):
        return ServicioNoDisponibleAPI(
            "El servicio de información académica no está habilitado en este "
            "entorno.",
            code="servicio_academico_no_configurado",
        )
    return ServicioNoDisponibleAPI(
        "No fue posible consultar su información académica en este momento. "
        "Intente nuevamente en unos minutos.",
        code="servicio_academico_no_disponible",
    )


def presentar_perfil(perfil: PerfilAcademico, *, expediente_activo: bool) -> dict:
    motivos = [{"codigo": m.codigo, "mensaje": m.mensaje} for m in perfil.motivos]
    if expediente_activo:
        motivos.append(dict(MOTIVO_EXPEDIENTE_ACTIVO))
    return {
        "estudiante": asdict(perfil.estudiante) if perfil.estudiante else None,
        "carrera": asdict(perfil.carrera) if perfil.carrera else None,
        "facultad": asdict(perfil.facultad) if perfil.facultad else None,
        "fuente": asdict(perfil.fuente),
        "consultado_en": perfil.consultado_en,
        "estado_perfil": perfil.estado.value,
        "perfil_validado": perfil.validado,
        "puede_iniciar_tramite": perfil.validado and not expediente_activo,
        "motivos_bloqueo": motivos,
    }


class PerfilAcademicoView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    rbac_resource = "perfil_academico"
    openapi_respuestas_extra = {
        "get": {
            "503": (
                "servicio_academico_no_configurado (sin fuente académica "
                "habilitada) o servicio_academico_no_disponible (la fuente no "
                "respondió)."
            ),
        }
    }

    @extend_schema(
        request=None,
        responses={200: PerfilAcademicoSerializer},
        description=(
            "Perfil académico del estudiante autenticado, obtenido de la "
            "fuente académica configurada (hoy la simulación MockSGA: "
            "`fuente.es_simulada = true`) y validado contra el catálogo "
            "interno. No recibe parámetros: siempre es el del propio usuario. "
            "Un perfil no validado responde 200 con `perfil_validado = false` "
            "y sus `motivos_bloqueo`."
        ),
    )
    def get(self, request):
        from apps.expedientes.services.crear_expediente import (
            tiene_expediente_activo,
        )

        try:
            perfil = get_academic_profile_service().obtener_perfil(request.user)
        except FuenteAcademicaNoDisponibleError as error:
            raise error_fuente_academica(error) from error
        datos = presentar_perfil(
            perfil, expediente_activo=tiene_expediente_activo(request.user)
        )
        return Response(
            PerfilAcademicoSerializer(datos).data, status=status.HTTP_200_OK
        )
