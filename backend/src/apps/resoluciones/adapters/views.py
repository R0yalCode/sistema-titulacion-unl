"""Adaptador HTTP del módulo resoluciones (T034/T035; plan.md 15).

Endpoints:
- POST /api/v1/informes/ (T034, emisión de informe legal por Secretaría-Abogacía)
- POST /api/v1/declaratorias/ (T035, registro de declaratoria por Decano/a)
"""
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.authentication.adapters.permissions import HasRolePermission
from apps.resoluciones.adapters.models import InformeAptitud, DeclaratoriaAptitud
from apps.resoluciones.adapters.serializers import InformeAptitudSerializer, DeclaratoriaAptitudSerializer
from apps.resoluciones.services import (
    emitir_informe,
    declarar_aptitud,
    InformeYaExisteError,
    ExpedienteNoValidoParaInformeError,
    UsuarioNoAutorizadoError,
    DeclaratoriaYaExisteError,
    ExpedienteNoValidoParaDeclaratoriaError,
    UsuarioNoAutorizadoErrorDeclaratoria,
    PDFInvalidoError,
)
from core.adapters.scope_filter import ScopeFilterMixin


class InformeEmitidoAPI(APIException):
    """HTTP 400 para informe ya emitido."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "informe_ya_emitido"


class ExpedienteInvalidoParaInformeAPI(APIException):
    """HTTP 400 para expediente no válido para informe."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "expediente_invalido_para_informe"


class DeclaratoriaEmitidaAPI(APIException):
    """HTTP 400 para declaratoria ya emitida."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "declaratoria_ya_emitida"


class ExpedienteInvalidoParaDeclaratoriaAPI(APIException):
    """HTTP 400 para expediente no válido para declaratoria."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "expediente_invalido_para_declaratoria"


class PDFInvalidoDeclaratoriaAPI(APIException):
    """HTTP 400 para PDF inválido en declaratoria."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "pdf_invalido"


class InformeViewSet(ScopeFilterMixin, viewsets.GenericViewSet):
    """Emisión de informe legal de aptitud (T034)."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    rbac_resource = "informes"
    queryset = InformeAptitud.objects.select_related("expediente", "emisor")
    serializer_class = InformeAptitudSerializer

    def get_serializer_class(self):
        if self.action == "create":
            from rest_framework import serializers

            class InformeCreateSerializer(serializers.Serializer):
                expediente_id = serializers.UUIDField()
                dictamen = serializers.ChoiceField(choices=["APTO", "NO APTO"])
                fundamentacion = serializers.CharField(required=False, allow_blank=True)

            return InformeCreateSerializer
        return InformeAptitudSerializer

    def get_rbac_resource(self):
        return "informes"

    def get_queryset(self):
        return self.scope_queryset(self.queryset, self.request)

    def create(self, request):
        """POST /api/v1/informes/ (T034).

        Emite el informe legal de aptitud (Providencia N° 590):
        - Valida que el checklist esté 100% VERIFICADO (RN-003, T029)
        - Genera PDF de la Providencia N° 590 (T033)
        - Inmutabiliza el registro InformeAptitud
        - Cambia expediente a INFORME_EMITIDO
        - Notifica al Decano/a (DEC-01)
        """
        from rest_framework import serializers

        class InformeCreateSerializer(serializers.Serializer):
            expediente_id = serializers.UUIDField()
            dictamen = serializers.ChoiceField(choices=["APTO", "NO APTO"])
            fundamentacion = serializers.CharField(required=False, allow_blank=True)

        serializer_in = InformeCreateSerializer(data=request.data)
        serializer_in.is_valid(raise_exception=True)

        expediente_id = serializer_in.validated_data["expediente_id"]
        dictamen = serializer_in.validated_data["dictamen"]
        fundamentacion = serializer_in.validated_data.get("fundamentacion", "")

        try:
            informe = emitir_informe(
                usuario=request.user,
                expediente_id=expediente_id,
                dictamen=dictamen,
                fundamentacion=fundamentacion,
            )
        except InformeYaExisteError as error:
            raise InformeEmitidoAPI(str(error))
        except ExpedienteNoValidoParaInformeError as error:
            raise ExpedienteInvalidoParaInformeAPI(str(error))
        except UsuarioNoAutorizadoError as error:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(str(error))
        except validar_checklist_completo.ChecklistIncompletoError as error:
            raise ValidationError({
                "detail": str(error),
                "requisitos_pendientes": error.requisitos_pendientes,
            })
        except ValueError as error:
            raise ValidationError(str(error))

        # Serializer de salida
        serializer_out = InformeAptitudSerializer(
            informe,
            context={"request": request},
        )
        return Response(serializer_out.data, status=status.HTTP_201_CREATED)


class DeclaratoriaViewSet(ScopeFilterMixin, viewsets.GenericViewSet):
    """Registro de declaratoria de aptitud (T035)."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    rbac_resource = "declaratorias"
    queryset = DeclaratoriaAptitud.objects.select_related("expediente", "decano")
    serializer_class = DeclaratoriaAptitudSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action == "create":
            from rest_framework import serializers

            class DeclaratoriaCreateSerializer(serializers.Serializer):
                expediente_id = serializers.UUIDField()
                archivo_memorando = serializers.FileField()
                numero_memorando = serializers.CharField(required=False, allow_blank=True)

            return DeclaratoriaCreateSerializer
        return DeclaratoriaAptitudSerializer

    def get_rbac_resource(self):
        return "declaratorias"

    def get_queryset(self):
        return self.scope_queryset(self.queryset, self.request)

    def create(self, request):
        """POST /api/v1/declaratorias/ (T035).

        Registra la declaratoria de aptitud legal (Memorando N° 162):
        - Valida que el expediente esté en INFORME_EMITIDO
        - Valida que exista InformeAptitud (Providencia N° 590)
        - Valida el PDF del memorando firmado (FirmaEC) - T022
        - Crea registro DeclaratoriaAptitud con número de memorando
        - Cambia expediente a DECLARADA_APTA
        - Notifica con copia a autoridades y estudiante (DEC-04)
        """
        from rest_framework import serializers

        class DeclaratoriaCreateSerializer(serializers.Serializer):
            expediente_id = serializers.UUIDField()
            archivo_memorando = serializers.FileField()
            numero_memorando = serializers.CharField(required=False, allow_blank=True)

        serializer_in = DeclaratoriaCreateSerializer(data=request.data)
        serializer_in.is_valid(raise_exception=True)

        expediente_id = serializer_in.validated_data["expediente_id"]
        archivo_memorando = serializer_in.validated_data["archivo_memorando"]
        numero_memorando = serializer_in.validated_data.get("numero_memorando") or None

        try:
            declaratoria = declarar_aptitud(
                usuario=request.user,
                expediente_id=expediente_id,
                archivo_memorando=archivo_memorando,
                numero_memorando=numero_memorando,
            )
        except DeclaratoriaYaExisteError as error:
            raise DeclaratoriaEmitidaAPI(str(error))
        except ExpedienteNoValidoParaDeclaratoriaError as error:
            raise ExpedienteInvalidoParaDeclaratoriaAPI(str(error))
        except UsuarioNoAutorizadoErrorDeclaratoria as error:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(str(error))
        except PDFInvalidoError as error:
            raise PDFInvalidoDeclaratoriaAPI(str(error))
        except ValueError as error:
            raise ValidationError(str(error))

        # Serializer de salida
        serializer_out = DeclaratoriaAptitudSerializer(
            declaratoria,
            context={"request": request},
        )
        return Response(serializer_out.data, status=status.HTTP_201_CREATED)


# Import para validación de checklist
from apps.verificacion.services import validar_checklist_completo