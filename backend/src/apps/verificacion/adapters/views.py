"""Adaptador HTTP del módulo verificación (T027/T028; plan.md 15).

Endpoints:
- PUT /api/v1/checklist/{id}/  (T027, evaluación de checklist con bloqueo pesimista)
- POST /api/v1/expedientes/{id}/observar/  (T028, registro de observaciones)
"""
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
from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.verificacion.adapters.models import ChecklistVerification
from apps.verificacion.services import evaluar_checklist, subsanar_requisito
from core.adapters.scope_filter import ScopeFilterMixin

from .serializers import (
    ChecklistVerificationSerializer,
    ChecklistEvaluationSerializer,
    ObservacionRegistroSerializer,
    ObservacionResponseSerializer,
    SubsanacionSerializer,
    SubsanacionResponseSerializer,
)


class InvalidChecklistStateAPI(APIException):
    """HTTP 400 para estado de checklist inválido."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "invalid_checklist_state"


class ExpedienteNotInVerificationAPI(APIException):
    """HTTP 400 para expediente no en verificación."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "expediente_not_in_verification"


class VerificationAlreadyDoneAPI(APIException):
    """HTTP 400 para verificación ya realizada."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "verification_already_done"


class ObservacionRequiredAPI(APIException):
    """HTTP 400 para motivo de observación requerido."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "observacion_required"


class ChecklistViewSet(
    ScopeFilterMixin,
    viewsets.GenericViewSet,
):
    """Gestión de evaluación de checklist (T027/T030)."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    rbac_resource = "checklist"
    queryset = ChecklistVerification.objects.select_related(
        "expediente", "requisito", "evaluado_por"
    )
    serializer_class = ChecklistVerificationSerializer
    scope_owner_field = "expediente__estudiante_id"
    scope_carrera_field = "expediente__carrera_id"
    scope_facultad_field = "expediente__facultad_id"
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.action == "update":
            return ChecklistEvaluationSerializer
        if self.action == "subsanar":
            return SubsanacionSerializer
        return ChecklistVerificationSerializer

    def get_rbac_resource(self):
        return "checklist"

    def get_queryset(self):
        return self.scope_queryset(self.queryset, self.request)

    def update(self, request, pk=None):
        """PUT /api/v1/checklist/{id}/ (T027).

        Evalúa un requisito del checklist (VERIFICADO / OBSERVADO)
        con bloqueo pesimista select_for_update() (ADR-007 / AP-06).
        """
        serializer_in = ChecklistEvaluationSerializer(data=request.data)
        serializer_in.is_valid(raise_exception=True)

        checklist_verif = get_object_or_404(self.get_queryset(), pk=pk)

        nuevo_estado = serializer_in.validated_data["estado_verificacion"]
        motivo_observacion = serializer_in.validated_data.get("motivo_observacion")

        try:
            checklist_actualizada = evaluar_checklist.execute(
                usuario=request.user,
                checklist_verification_id=checklist_verif.id,
                nuevo_estado=nuevo_estado,
                motivo_observacion=motivo_observacion,
            )
        except evaluar_checklist.ChecklistVerificationNotFoundError as error:
            raise APIException(str(error))
        except evaluar_checklist.InvalidVerificationStateError as error:
            raise InvalidChecklistStateAPI(str(error))
        except evaluar_checklist.ExpedienteNotInVerificationError as error:
            raise ExpedienteNotInVerificationAPI(str(error))
        except evaluar_checklist.VerificationAlreadyCompletedError as error:
            raise VerificationAlreadyDoneAPI(str(error))
        except evaluar_checklist.UserNotAuthorizedError as error:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(str(error))

        serializer_out = ChecklistVerificationSerializer(
            checklist_actualizada,
            context={"request": request},
        )
        return Response(serializer_out.data, status=status.HTTP_200_OK)

    def subsanar(self, request, pk=None):
        """POST /api/v1/checklist/{id}/subsanar/ (T030).

        Subsana un requisito observado: carga un nuevo PDF, incrementa versión N+1,
        marca observación como resuelta, reanuda plazo y retorna a EN_VERIFICACION.
        """
        serializer_in = SubsanacionSerializer(data=request.data)
        serializer_in.is_valid(raise_exception=True)

        checklist_verif = get_object_or_404(self.get_queryset(), pk=pk)

        archivo = serializer_in.validated_data["archivo"]
        nombre_original = archivo.name

        try:
            documento = subsanar_requisito.execute(
                usuario=request.user,
                checklist_verification_id=checklist_verif.id,
                archivo=archivo,
                nombre_original=nombre_original,
            )
        except subsanar_requisito.SubsanacionNoPermitidaError as error:
            raise APIException(str(error))
        except subsanar_requisito.PeticionNoEncontradaError as error:
            raise APIException(str(error))
        except subsanar_requisito.ObservacionNoEncontradaError as error:
            raise APIException(str(error))
        except subsanar_requisito.UsuarioNoAutorizadoError as error:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(str(error))
        except subsanar_requisito.ValidacionPDFError as error:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(str(error))

        serializer_out = SubsanacionResponseSerializer(
            documento,
            context={"request": request},
        )
        return Response(serializer_out.data, status=status.HTTP_201_CREATED)


class ObservacionViewSet(
    ScopeFilterMixin,
    viewsets.GenericViewSet,
):
    """Registro de observaciones accionables (T028)."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    rbac_resource = "observaciones"
    queryset = ChecklistVerification.objects.select_related(
        "expediente", "requisito"
    )
    serializer_class = ObservacionRegistroSerializer
    scope_owner_field = "expediente__estudiante_id"
    scope_carrera_field = "expediente__carrera_id"
    scope_facultad_field = "expediente__facultad_id"

    def get_serializer_class(self):
        if self.action == "crear_observacion":
            return ObservacionRegistroSerializer
        return ObservacionRegistroSerializer

    def get_rbac_resource(self):
        return "observaciones"

    def get_queryset(self):
        return self.scope_queryset(self.queryset, self.request)

    def crear_observacion(self, request, pk=None):
        """POST /api/v1/expedientes/{id}/observar/ (T028).

        Registra observación, cambia petición a OBSERVADO,
        expediente a OBSERVADA, pausa plazo y notifica al estudiante.
        """
        serializer_in = ObservacionRegistroSerializer(data=request.data)
        serializer_in.is_valid(raise_exception=True)

        checklist_verif = get_object_or_404(self.get_queryset(), pk=pk)

        # Solo permitir si está en estado VERIFICADO u OBSERVADO
        # (no PENDIENTE para poder observarlo directamente)
        # Pero según FL-04, se observa desde EN_VERIFICACION
        
        expediente = checklist_verif.expediente
        if expediente.estado != ExpedienteTitulacion.ESTADO_EN_VERIFICACION:
            raise ExpedienteNotInVerificationAPI(
                f"El expediente debe estar en EN_VERIFICACION. Estado actual: {expediente.estado}"
            )

        motivo = serializer_in.validated_data["motivo_observacion"]

        try:
            checklist_verif = evaluar_checklist.execute(
                usuario=request.user,
                checklist_verification_id=checklist_verif.id,
                nuevo_estado="OBSERVADO",
                motivo_observacion=motivo,
            )
        except evaluar_checklist.InvalidVerificationStateError as error:
            raise InvalidChecklistStateAPI(str(error))
        except evaluar_checklist.ExpedienteNotInVerificationError as error:
            raise ExpedienteNotInVerificationAPI(str(error))
        except evaluar_checklist.UserNotAuthorizedError as error:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(str(error))

        serializer_out = ObservacionResponseSerializer(
            checklist_verif,
            context={"request": request},
        )
        return Response(serializer_out.data, status=status.HTTP_200_OK)


class ChecklistListViewSet(
    ScopeFilterMixin,
    viewsets.ReadOnlyModelViewSet,
):
    """Consulta de checklist de un expediente (GET /api/v1/expedientes/{id}/checklist/)."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    rbac_resource = "checklist"
    queryset = ChecklistVerification.objects.select_related(
        "expediente", "requisito", "evaluado_por"
    )
    serializer_class = ChecklistVerificationSerializer
    scope_owner_field = "expediente__estudiante_id"
    scope_carrera_field = "expediente__carrera_id"
    scope_facultad_field = "expediente__facultad_id"

    def get_rbac_resource(self):
        return "checklist"

    def get_queryset(self):
        queryset = self.scope_queryset(self.queryset, self.request)
        expediente_id = self.kwargs.get("expediente_id")
        if expediente_id:
            queryset = queryset.filter(expediente_id=expediente_id)
        return queryset