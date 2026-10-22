"""Adaptador HTTP del modulo peticiones (T021/T023/T024; plan.md 15).

Endpoints:
- POST /api/v1/peticiones/{id}/solicitar-emision/  (T021, HU-002)
- POST /api/v1/peticiones/{id}/documento/           (T023, HU-003)
- GET  /api/v1/peticiones/{id}/documento/{version}/ (T024, descarga segura)
"""
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
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.authentication.adapters.permissions import HasRolePermission
from apps.peticiones.adapters.models import DocumentoEntregado, PeticionDocumental
from apps.peticiones.services import cargar_documento, solicitar_emision
from core.adapters.local_storage import archivo_existe, obtener_ruta_absoluta
from core.adapters.scope_filter import ScopeFilterMixin

from .serializers import (
    CargarDocumentoResponseSerializer,
    CargarDocumentoSerializer,
    DocumentoEntregadoSerializer,
    PeticionDocumentalSerializer,
    SolicitarEmisionResponseSerializer,
    SolicitarEmisionSerializer,
)


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
    rbac_resource = "peticiones"
    queryset = PeticionDocumental.objects.select_related(
        "expediente", "requisito"
    )
    scope_owner_field = "expediente__estudiante_id"
    scope_carrera_field = "expediente__carrera_id"
    scope_facultad_field = "expediente__facultad_id"
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_parser_classes(self):
        if self.action == "cargar_documento":
            return [MultiPartParser, FormParser]
        return [JSONParser]

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
        # Para descargar_documento, no aplicar filtro de ámbito (SCOPE_ASIGNADO no soportado por ScopeFilterMixin)
        # La autorización se maneja en el action via HasRolePermission + validación manual
        if self.action == "descargar_documento":
            return self.queryset
        return self.scope_queryset(self.queryset, self.request)

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
        # Obtener la petición SIN filtro de ámbito (la autorización se valida manualmente)
        peticion = get_object_or_404(self.queryset, pk=pk)

        # Validación manual de ámbito (IDOR) - replicar lógica de ScopeFilterMixin
        # pero soportando SCOPE_ASIGNADO para peticiones:documento
        if not self._validar_ambito_descarga(request.user, peticion):
            raise Http404("Petición no encontrada o sin acceso.")

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

    def _validar_ambito_descarga(self, user, peticion):
        """Valida si el usuario tiene acceso a la petición para descarga.

        Replica lógica de ScopeFilterMixin pero soporta SCOPE_ASIGNADO
        según la matriz RBAC para peticiones:documento GET.
        """
        from apps.authentication.adapters.permissions import (
            get_granted_scopes,
            SCOPE_OWN,
            SCOPE_CARRERA,
            SCOPE_FACULTAD,
            SCOPE_ASIGNADO,
        )

        scopes = get_granted_scopes(user, "peticiones:documento", "GET")
        if not scopes:
            return False

        # Si tiene ALLOW (admin), acceso total
        from apps.authentication.adapters.permissions import ALLOW
        if ALLOW in scopes:
            return True

        # SCOPE_OWN: estudiante propietario
        if SCOPE_OWN in scopes:
            return peticion.expediente.estudiante_id == user.pk

        # SCOPE_CARRERA: secretaria/director de carrera
        if SCOPE_CARRERA in scopes:
            return (
                user.carrera_id
                and peticion.expediente.carrera_id == user.carrera_id
            )

        # SCOPE_FACULTAD: secretario/analista/decano
        if SCOPE_FACULTAD in scopes:
            return (
                user.facultad_id
                and peticion.expediente.facultad_id == user.facultad_id
            )

        # SCOPE_ASIGNADO: rol asignado a la petición (secretaria carrera, etc.)
        if SCOPE_ASIGNADO in scopes:
            # Verificar si el usuario tiene un rol que le da acceso a esta petición
            # según la dependencia_emisora de la petición
            from apps.peticiones.adapters.models import PeticionDocumental
            return PeticionDocumental.objects.filter(
                id=peticion.id,
                expediente__carrera_id=user.carrera_id,
                dependencia_emisora__in=user.get_roles(),
            ).exists()

        return False


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