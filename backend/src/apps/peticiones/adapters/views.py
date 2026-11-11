"""Adaptador HTTP del modulo peticiones (T021/T023/T024; plan.md 15).

Endpoints:
- POST /api/v1/peticiones/{id}/solicitar-emision/  (T021, HU-002)
- POST /api/v1/peticiones/{id}/documento/           (T023, HU-003)
- GET  /api/v1/peticiones/{id}/documento/{version}/ (T024, descarga segura)
"""
import logging

from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from rest_framework import (
    status,
    viewsets,
)
from rest_framework.exceptions import APIException
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.authentication.adapters.permissions import HasRolePermission
from apps.peticiones.adapters.models import DocumentoEntregado, PeticionDocumental
from apps.peticiones.services import cargar_documento, solicitar_emision
from core.adapters.local_storage import (
    archivo_existe,
    calcular_sha256,
    obtener_ruta_absoluta,
)
from core.adapters.throttling import MutantOperationThrottle
from core.adapters.scope_filter import ScopeFilterMixin

from .serializers import (
    CargarDocumentoResponseSerializer,
    CargarDocumentoSerializer,
    DocumentoEntregadoSerializer,
    PeticionDocumentalSerializer,
    SolicitarEmisionResponseSerializer,
    SolicitarEmisionSerializer,
)


logger = logging.getLogger(__name__)


class EstadoPeticionInvalidoAPI(APIException):
    """HTTP 400 para peticion en estado no valido."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "estado_peticion_invalido"


class ExpedienteEstadoInvalidoAPI(APIException):
    """HTTP 400 para expediente en estado no valido."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "expediente_estado_invalido"


class UsuarioNoAutorizadoAPI(APIException):
    """HTTP 403 para usuario sin permisos."""

    status_code = status.HTTP_403_FORBIDDEN
    default_code = "usuario_no_autorizado"


class DocumentoIntegridadAPI(APIException):
    """HTTP 500: el hash del archivo almacenado no coincide con el registrado."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = (
        "No se puede entregar el documento: falló la verificación de "
        "integridad del archivo almacenado."
    )
    default_code = "documento_integridad_comprometida"


class ValidacionPDF_API(APIException):
    """HTTP 400 para errores de validación PDF."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "pdf_validation_error"


class PeticionViewSet(
    ScopeFilterMixin,
    viewsets.GenericViewSet,
):
    """Gestion de peticiones documentales (T021/T023)."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    throttle_classes = [MutantOperationThrottle]  # VULN-001 (INC-01-T01)
    rbac_resource = "peticiones"
    queryset = PeticionDocumental.objects.select_related(
        "expediente", "requisito"
    )
    serializer_class = PeticionDocumentalSerializer
    scope_owner_field = "expediente__estudiante_id"
    scope_carrera_field = "expediente__carrera_id"
    scope_facultad_field = "expediente__facultad_id"
    # VULN-002 (INC-01-T02): ámbito "asignado" = dependencia emisora de la
    # petición coincide con un rol del usuario, dentro de su ámbito.
    scope_asignado_field = "dependencia_emisora"
    # Contrato OpenAPI (core.adapters.openapi.SGTAutoSchema).
    openapi_respuestas_extra = {
        "descargar_documento": {
            "500": (
                "documento_integridad_comprometida: el SHA-256 del archivo "
                "almacenado no coincide con el registrado en la carga "
                "(VULN-003); el archivo no se entrega."
            ),
        },
    }
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.action == "solicitar_emision":
            return SolicitarEmisionSerializer
        if self.action == "cargar_documento":
            return CargarDocumentoSerializer
        if self.action == "descargar_documento":
            return DocumentoEntregadoSerializer
        return PeticionDocumentalSerializer

    def get_parser_classes(self):
        if self.action == "cargar_documento":
            return [MultiPartParser, FormParser]
        return [JSONParser]

    def get_throttles(self):
        if self.action == "cargar_documento":
            self.throttle_scope = "document_upload"
            return [ScopedRateThrottle()]
        return super().get_throttles()

    def get_rbac_resource(self):
        # En has_permission, self.action puede ser None (se setea en initial() después de check_permissions)
        # Determinar recurso basado en request.method y URL path
        if hasattr(self, 'request') and self.request is not None:
            path = self.request.path
            method = self.request.method
            # Endpoints de documento: /api/v1/peticiones/{pk}/documento/ o /documento/{version}/
            if "/documento/" in path and method == "GET":
                return "peticiones:documento"
            if "/documento/" in path and method == "POST":
                return "peticiones:documento"
        if self.action in ("solicitar_emision", "cargar_documento"):
            return "peticiones"
        if self.action in ("descargar_documento",):
            return "peticiones:documento"
        return self.rbac_resource

    def get_queryset(self):
        return self.scope_queryset(self.queryset, self.request)

    def get_scope_grants(self, user, roles):
        """En la descarga (GET `peticiones:documento`) el ámbito sale de la matriz RBAC.

        Esa celda concede SCOPE_ASIGNADO a funcionarios (la dependencia que
        emite el documento), que `ROW_TO_SCOPE` no puede expresar. La carga
        (POST) conserva el ámbito por rol y su contrato 403: la restricción
        de dependencia se valida en el servicio `cargar_documento`.
        """
        if (
            self.request.method != "GET"
            or self.get_rbac_resource() != "peticiones:documento"
        ):
            return super().get_scope_grants(user, roles)
        from apps.authentication.adapters.permissions import (
            ALLOW,
            get_granted_scopes,
        )
        from core.adapters.scope_filter import SCOPE_ALL

        concedidos = get_granted_scopes(
            user, "peticiones:documento", self.request.method
        )
        return {SCOPE_ALL if s == ALLOW else s for s in concedidos}

    def solicitar_emision(self, request, pk=None):
        """POST /api/v1/peticiones/{id}/solicitar-emision/ (T021; HU-002).

        Cambia estado de PENDIENTE a SOLICITADO y genera NotificacionInterna
        a la dependencia emisora (DEC-01).
        """
        serializer_in = SolicitarEmisionSerializer(data=request.data)
        serializer_in.is_valid(raise_exception=True)

        peticion = get_object_or_404(self.get_queryset(), pk=pk)

        try:
            peticion_actualizada = solicitar_emision.execute(
                usuario=request.user,
                peticion_id=peticion.id,
            )
        except solicitar_emision.PeticionNoEncontradaError as error:
            raise APIException(str(error))
        except solicitar_emision.ExpedienteEstadoInvalidoError as error:
            raise ExpedienteEstadoInvalidoAPI(str(error))
        except solicitar_emision.EstadoPeticionInvalidoError as error:
            raise EstadoPeticionInvalidoAPI(str(error))
        except solicitar_emision.UsuarioNoAutorizadoError as error:
            raise UsuarioNoAutorizadoAPI(str(error))

        serializer_out = SolicitarEmisionResponseSerializer(
            peticion_actualizada,
            context={"request": request},
        )
        return Response(serializer_out.data, status=status.HTTP_200_OK)

    def cargar_documento(self, request, pk=None):
        """POST /api/v1/peticiones/{id}/documento/ (T023; HU-003).

        Carga archivo PDF, valida magic bytes/SHA-256, registra subido_por
        y cambia estado a CARGADO (DEC-02).
        """
        serializer_in = CargarDocumentoSerializer(data=request.data)
        serializer_in.is_valid(raise_exception=True)

        peticion = get_object_or_404(self.get_queryset(), pk=pk)

        archivo = serializer_in.validated_data["archivo"]
        nombre_original = archivo.name

        try:
            documento = cargar_documento.execute(
                usuario=request.user,
                peticion_id=peticion.id,
                archivo=archivo,
                nombre_original=nombre_original,
            )
        except cargar_documento.PeticionNoEncontradaError as error:
            raise APIException(str(error))
        except cargar_documento.EstadoPeticionInvalidoError as error:
            raise ExpedienteEstadoInvalidoAPI(str(error))
        except cargar_documento.UsuarioNoAutorizadoError as error:
            raise UsuarioNoAutorizadoAPI(str(error))
        except cargar_documento.ValidacionPDFError as error:
            raise ValidacionPDF_API(str(error))

        serializer_out = CargarDocumentoResponseSerializer(
            documento,
            context={"request": request},
        )
        return Response(serializer_out.data, status=status.HTTP_201_CREATED)

    def descargar_documento(self, request, pk=None, version=None):
        """GET /api/v1/peticiones/{id}/documento/{version}/ (T024).

        Descarga segura de archivo PDF desde almacenamiento privado.
        Requiere autenticación JWT y permisos RBAC/IDOR (RNF-016).
        """
        # Aislamiento IDOR por el mismo mixin que el resto de vistas
        # (incluye SCOPE_ASIGNADO): un registro ajeno responde 404.
        peticion = get_object_or_404(self.get_queryset(), pk=pk)

        # Obtener el documento específico por versión
        if version is None:
            # Si no se especifica versión, usar la vigente
            documento = peticion.documentos_entregados.filter(es_vigente=True).first()
            if not documento:
                raise Http404("No hay documento vigente para esta petición.")
        else:
            documento = get_object_or_404(
                peticion.documentos_entregados, version=version
            )

        # Verificar que el archivo existe en almacenamiento privado
        if not archivo_existe(documento.archivo_path):
            raise Http404("El archivo no existe en el almacenamiento.")

        # VULN-003 (INC-01-T03): el archivo en disco debe coincidir con el
        # SHA-256 registrado en la carga; si no, no se sirve.
        if calcular_sha256(documento.archivo_path) != documento.hash_sha256:
            logger.error(
                "Integridad comprometida en documento %s (peticion %s, v%s)",
                documento.id,
                peticion.id,
                documento.version,
            )
            raise DocumentoIntegridadAPI()

        # Obtener ruta absoluta
        ruta_absoluta = obtener_ruta_absoluta(documento.archivo_path)

        # Servir archivo con FileResponse (streaming)
        response = FileResponse(
            open(ruta_absoluta, "rb"),
            content_type=documento.tipo_mime or "application/pdf",
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{documento.nombre_original}"'
        )
        response["Content-Length"] = documento.tamanio_bytes
        return response


class PeticionDocumentalViewSet(
    ScopeFilterMixin,
    viewsets.ReadOnlyModelViewSet,
):
    """Consulta de peticiones documentales (T021+)."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    rbac_resource = "peticiones"
    queryset = PeticionDocumental.objects.select_related(
        "expediente", "requisito"
    )
    serializer_class = PeticionDocumentalSerializer
    scope_owner_field = "expediente__estudiante_id"
    scope_carrera_field = "expediente__carrera_id"
    scope_facultad_field = "expediente__facultad_id"

    def get_queryset(self):
        return self.scope_queryset(self.queryset, self.request)