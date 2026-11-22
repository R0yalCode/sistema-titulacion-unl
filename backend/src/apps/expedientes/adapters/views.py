"""Adaptador HTTP del modulo expedientes (T015/T016/T017; plan.md 15).

`ExpedienteViewSet` expone `POST /api/v1/expedientes/` (registro de
solicitud en BORRADOR, HU-001) y `POST /api/v1/expedientes/{id}/enviar/`
(envio formal, HU-004). `BandejaExpedienteViewSet` expone la bandeja
operativa paginada filtrada por rol y dependencia (HU-005; T017).
El detalle por ID (IDOR generalizado) es sucesor (T018).
"""

import uuid

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import (
    pagination,
)
from rest_framework import (
    status,
    viewsets,
)
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.academico.adapters.views import error_fuente_academica
from apps.academico.ports.fuente_academica import FuenteAcademicaNoDisponibleError
from apps.authentication.adapters.permissions import HasRolePermission
from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.expedientes.services import (
    crear_expediente,
    enviar_expediente,
    iniciar_verificacion,
    resumen_estudiante,
)
from apps.expedientes.services.transiciones import TransicionNoPermitidaError
from apps.verificacion.services import registrar_observacion
from core.adapters.api_errors import (
    ConfiguracionInconsistenteAPI,
    PrecondicionNegocioAPI,
    RecursoNoEncontradoAPI,
    RequisitosIncompletosAPI,
    SolicitudInvalidaAPI,
    TransicionInvalidaAPI,
)
from core.adapters.throttling import MutantOperationThrottle
from core.adapters.scope_filter import ScopeFilterMixin

from .serializers import (
    BandejaExpedienteSerializer,
    CrearExpedienteSerializer,
    ExpedienteBorradorSerializer,
    ExpedienteDetalleSerializer,
    ExpedienteEnviadoSerializer,
)
from apps.verificacion.adapters.serializers import (
    ObservacionAccionableSerializer,
    ObservacionRegistroSerializer,
)


#: Campos que el cliente no puede fijar al crear un expediente (V-03): se
#: derivan del usuario autenticado y de su perfil académico validado.
CAMPOS_DERIVADOS_EN_SERVIDOR = frozenset({"carrera_id", "facultad_id", "estudiante_id"})

#: Código de error (422) según el estado del perfil académico no validado.
CODIGO_POR_ESTADO_PERFIL = {
    "NO_ASOCIADO": "perfil_academico_no_asociado",
    "INCOMPLETO": "perfil_academico_incompleto",
    "INCONSISTENTE": "perfil_academico_inconsistente",
    "CARRERA_INACTIVA": "carrera_inactiva",
}


# Compatibilidad: los nombres anteriores apuntan a las clases comunes de
# `core.adapters.api_errors` (PLB-E1-04), que añaden `code` al cuerpo JSON.
ReqIncompletosAPI = RequisitosIncompletosAPI


class ExpedienteViewSet(
    ScopeFilterMixin,
    viewsets.GenericViewSet,
):
    """Registro, envio y consulta de expedientes (T015/T016/T018)."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    throttle_classes = [MutantOperationThrottle]  # VULN-001 (INC-01-T01)
    rbac_resource = "expedientes"
    queryset = ExpedienteTitulacion.objects.select_related("estudiante")
    serializer_class = ExpedienteDetalleSerializer
    scope_owner_field = "estudiante_id"
    scope_carrera_field = "carrera_id"
    scope_facultad_field = "facultad_id"
    # Contrato OpenAPI (core.adapters.openapi.SGTAutoSchema).
    openapi_respuestas_extra = {
        "create": {
            "400": (
                "expediente_activo_existente, o campo_no_permitido (el cuerpo "
                "incluye carrera_id, facultad_id o estudiante_id: se determinan "
                "en el servidor a partir del perfil académico)."
            ),
            "422": (
                "Perfil académico no validado: perfil_academico_no_asociado, "
                "perfil_academico_incompleto, perfil_academico_inconsistente o "
                "carrera_inactiva."
            ),
            "500": (
                "configuracion_catalogo_incompleta: el catálogo base del Art. 235 "
                "no tiene los 5 requisitos vigentes (D-2)."
            ),
            "503": (
                "servicio_academico_no_configurado o "
                "servicio_academico_no_disponible: no se pudo obtener el perfil "
                "académico."
            ),
        },
        "enviar": {
            "400": (
                "estado_invalido (no está en BORRADOR) o transicion_invalida; "
                "sin efectos."
            ),
            "404": "Expediente inexistente o ajeno.",
            "422": "requisitos_incompletos: requisitos sin documento en firme.",
        },
        "iniciar_verificacion": {
            "400": (
                "transicion_invalida: el expediente no esta en ENVIADA (p. ej. ya "
                "en verificacion, incluida una segunda llamada concurrente); "
                "sin efectos."
            ),
            "403": {
                "descripcion": (
                    "Rol sin la celda expedientes:iniciar_verificacion (AUT-02)."
                ),
                "esquema": "simple",
            },
            "404": (
                "expediente_no_encontrado, o expediente fuera de la facultad del "
                "usuario."
            ),
            "500": "configuracion_catalogo_incompleta (D-2).",
        },
        "observar": {
            "400": (
                "expediente_no_en_verificacion, observacion_ya_existe, "
                "peticion_ya_observada o transicion_invalida; sin efectos."
            ),
            "404": "peticion_no_encontrada o expediente_no_encontrado.",
        },
    }

    def get_serializer_class(self):
        if self.action == "create":
            return CrearExpedienteSerializer
        if self.action == "enviar":
            return ExpedienteEnviadoSerializer
        if self.action == "retrieve":
            return ExpedienteDetalleSerializer
        if self.action == "observar":
            from apps.verificacion.adapters.serializers import ObservacionRegistroSerializer
            return ObservacionRegistroSerializer
        return ExpedienteDetalleSerializer

    def get_rbac_resource(self):
        """Celda de la matriz RBAC 6.2 segun la accion invocada."""
        if self.action in ("enviar", "retrieve"):
            return "expedientes"
        if self.action == "iniciar_verificacion":
            return "expedientes:iniciar_verificacion"
        if self.action == "observar":
            return "expedientes:observar"
        return self.rbac_resource

    def get_queryset(self):
        return self.scope_queryset(self.queryset, self.request)

    def create(self, request, *args, **kwargs):
        claves = request.data.keys() if hasattr(request.data, "keys") else ()
        prohibidos = sorted(CAMPOS_DERIVADOS_EN_SERVIDOR.intersection(claves))
        if prohibidos:
            raise SolicitudInvalidaAPI(
                "La carrera, la facultad y el estudiante del expediente se "
                "determinan a partir de su perfil académico; no se aceptan en "
                f"la solicitud ({', '.join(prohibidos)}).",
                code="campo_no_permitido",
            )
        serializer_in = CrearExpedienteSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer_in.is_valid(raise_exception=True)
        try:
            expediente = crear_expediente.execute(estudiante=request.user)
        except FuenteAcademicaNoDisponibleError as error:
            raise error_fuente_academica(error) from error
        except crear_expediente.PerfilAcademicoNoValidoError as error:
            raise PrecondicionNegocioAPI(
                str(error), code=CODIGO_POR_ESTADO_PERFIL[error.perfil.estado.value]
            )
        except crear_expediente.CarreraNoVigenteError as error:
            raise PrecondicionNegocioAPI(str(error), code="carrera_inactiva")
        except crear_expediente.ExpedienteActivoExistenteError as error:
            raise SolicitudInvalidaAPI(str(error), code="expediente_activo_existente")
        except crear_expediente.CatalogoIncompletoError as error:
            # D-2: fallo de configuración institucional, no del cliente.
            raise ConfiguracionInconsistenteAPI(
                str(error),
                code="configuracion_catalogo_incompleta",
                contexto={"operacion": "crear_expediente"},
            )
        serializer_out = ExpedienteBorradorSerializer(
            expediente,
            context={"request": request},
        )
        return Response(serializer_out.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Detalle del expediente con aislamiento por ambito (T018; EX-003, CA-008)."""
        expediente = get_object_or_404(self.get_queryset(), pk=pk)
        serializer_out = ExpedienteDetalleSerializer(
            expediente,
            context={"request": request},
        )
        return Response(serializer_out.data, status=status.HTTP_200_OK)

    def enviar(self, request, pk=None):
        """Accion ENDPOINT `enviar`: alcance `own` (EX-003 via get_object_or_404)."""
        expediente = get_object_or_404(
            ExpedienteTitulacion,
            pk=pk,
            estudiante=request.user,
        )
        try:
            enviado = enviar_expediente.execute(expediente, actor=request.user)
        except enviar_expediente.EstadoInvalidoError as error:
            raise SolicitudInvalidaAPI(str(error), code="estado_invalido")
        except enviar_expediente.RequisitosIncompletosError as error:
            raise RequisitosIncompletosAPI(str(error))
        except TransicionNoPermitidaError as error:
            raise TransicionInvalidaAPI(str(error))
        serializer_out = ExpedienteEnviadoSerializer(
            enviado,
            context={"request": request},
        )
        return Response(serializer_out.data, status=status.HTTP_200_OK)

    @extend_schema(request=None, responses={200: ExpedienteDetalleSerializer})
    def iniciar_verificacion(self, request, pk=None):
        """POST /api/v1/expedientes/{id}/iniciar-verificacion/ (PLB-E2-01).

        Sin cuerpo. Solo SECRETARIO_ABOGADO de la facultad (AUT-02): un
        expediente fuera de su ambito desaparece del queryset (404). Errores
        de estado o de transicion (incluida una llamada concurrente que espera
        el bloqueo) -> 400, sin efectos (rollback).
        """
        expediente = get_object_or_404(self.get_queryset(), pk=pk)
        try:
            actualizado = iniciar_verificacion.execute(
                expediente.pk, actor=request.user
            )
        except (
            iniciar_verificacion.EstadoInvalidoError,
            TransicionNoPermitidaError,
        ) as error:
            raise TransicionInvalidaAPI(str(error))
        except iniciar_verificacion.UsuarioNoAutorizadoError as error:
            raise PermissionDenied(str(error))
        except iniciar_verificacion.ExpedienteNoEncontradoError as error:
            raise RecursoNoEncontradoAPI(str(error), code="expediente_no_encontrado")
        except iniciar_verificacion.CatalogoIncompletoError as error:
            # D-2: 500 explícito, con código y registro técnico.
            raise ConfiguracionInconsistenteAPI(
                str(error),
                code="configuracion_catalogo_incompleta",
                contexto={
                    "operacion": "iniciar_verificacion",
                    "expediente_id": str(expediente.pk),
                },
            )
        serializer_out = ExpedienteDetalleSerializer(
            actualizado,
            context={"request": request},
        )
        return Response(serializer_out.data, status=status.HTTP_200_OK)

    def observar(self, request, pk=None):
        """POST /api/v1/expedientes/{id}/observar/ (T028).

        Registra observación accionable, pausa plazo de 8 días hábiles (AP-01),
        cambia estados a OBSERVADO/OBSERVADA y notifica al estudiante (DEC-01).
        """
        from apps.verificacion.adapters.serializers import ObservacionRegistroSerializer

        expediente = get_object_or_404(self.get_queryset(), pk=pk)

        serializer_in = ObservacionRegistroSerializer(data=request.data)
        serializer_in.is_valid(raise_exception=True)

        motivo = serializer_in.validated_data["motivo_observacion"]
        peticion_id = request.data.get("peticion_id")
        try:
            uuid.UUID(str(peticion_id))
        except (TypeError, ValueError, AttributeError):
            # Antes: el ORM lanzaba ValidationError de Django -> 500 genérico.
            raise RecursoNoEncontradoAPI(
                "La petición no existe o no pertenece al expediente.",
                code="peticion_no_encontrada",
            )

        try:
            observacion = registrar_observacion.execute(
                usuario=request.user,
                expediente_id=expediente.id,
                peticion_id=peticion_id,
                motivo_observacion=motivo,
            )
        except registrar_observacion.ExpedienteNoEnVerificacionError as error:
            raise SolicitudInvalidaAPI(str(error), code="expediente_no_en_verificacion")
        except registrar_observacion.ExpedienteNoEncontradoError as error:
            raise RecursoNoEncontradoAPI(str(error), code="expediente_no_encontrado")
        except registrar_observacion.PeticionNoEncontradaError as error:
            raise RecursoNoEncontradoAPI(str(error), code="peticion_no_encontrada")
        except registrar_observacion.ObservacionYaExisteError as error:
            raise SolicitudInvalidaAPI(str(error), code="observacion_ya_existe")
        except registrar_observacion.PeticionYaObservadaError as error:
            raise SolicitudInvalidaAPI(str(error), code="peticion_ya_observada")
        except registrar_observacion.UsuarioNoAutorizadoError as error:
            raise PermissionDenied(str(error))
        except TransicionNoPermitidaError as error:
            raise TransicionInvalidaAPI(str(error))

        serializer_out = ObservacionAccionableSerializer(
            observacion,
            context={"request": request},
        )
        return Response(serializer_out.data, status=status.HTTP_201_CREATED)


class BandejaPagination(pagination.PageNumberPagination):
    """Paginacion de bandeja (T017): ?page=&page_size= (maximo 50)."""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


# Estados que requieren intervencion del rol (HU-005; mapas documentados):
# - SECRETARIO_ABOGADO / ANALISTA_APOYO: criterio literal T017 y FL-05.
# - DECANO: ejemplo literal de tasks.md (INFORME_EMITIDO para Decanato).
# - ESTUDIANTE: {BORRADOR, OBSERVADA} (FL-01 paso 2 y subsanacion HU-008).
# - ADMINISTRADOR: estados en curso (supervision integral del MVP).
# - SECRETARIA_CARRERA / DIRECTOR_CARRERA / RESPONSABLE_DEPENDENCIA: sin
#   expedientes asignados en las fuentes (su intervencion es sobre
#   peticiones/notificaciones; llegara con T021+).
MAPA_INTERVENCION_POR_ROL = {
    "ESTUDIANTE": ("BORRADOR", "OBSERVADA"),
    "SECRETARIA_CARRERA": (),
    "SECRETARIO_ABOGADO": ("ENVIADA", "EN_VERIFICACION", "OBSERVADA"),
    "ANALISTA_APOYO": ("ENVIADA", "EN_VERIFICACION", "OBSERVADA"),
    "DECANO": ("INFORME_EMITIDO",),
    "DIRECTOR_CARRERA": (),
    "RESPONSABLE_DEPENDENCIA": (),
    "ADMINISTRADOR": (
        "BORRADOR",
        "ENVIADA",
        "EN_VERIFICACION",
        "OBSERVADA",
        "INFORME_EMITIDO",
    ),
}


class BandejaExpedienteViewSet(
    ScopeFilterMixin,
    viewsets.ReadOnlyModelViewSet,
):
    """Bandeja operativa filtrada por rol, estado y ambito (HU-005)."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    rbac_resource = "expedientes"
    queryset = ExpedienteTitulacion.objects.select_related("estudiante")
    serializer_class = BandejaExpedienteSerializer
    pagination_class = BandejaPagination
    http_method_names = ["get"]
    scope_owner_field = "estudiante_id"
    scope_carrera_field = "carrera_id"
    scope_facultad_field = "facultad_id"

    def get_queryset(self):
        queryset = self.scope_queryset(self.queryset, self.request)
        estados = {
            estado
            for rol in self.request.user.get_roles()
            for estado in MAPA_INTERVENCION_POR_ROL.get(rol, ())
        }
        if not estados:
            return queryset.none()
        return queryset.filter(estado__in=estados).order_by(
            "fecha_limite_atencion",
            "fecha_creacion",
        )


class MiTramiteView(APIView):
    """GET /api/v1/expedientes/mi-tramite/ (dashboard del estudiante).

    Solo lectura y solo ESTUDIANTE (celda RBAC `expedientes:mi_tramite`).
    No recibe identificadores: el resumen se construye siempre sobre
    `request.user`, por lo que no puede consultarse el trámite de otro
    estudiante (sin superficie IDOR). Devuelve `expediente: null` si el
    estudiante aún no registró una solicitud.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    rbac_resource = "expedientes:mi_tramite"

    @extend_schema(request=None, responses={200: dict})
    def get(self, request):
        return Response(resumen_estudiante.execute(request.user), status=status.HTTP_200_OK)
