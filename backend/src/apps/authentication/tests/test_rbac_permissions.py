"""Pruebas de la matriz RBAC y del aislamiento por ambito (T012; RNF-002/003).

Cubre: matriz codificada == matriz literal 6.2 de specify.md, evaluacion
server-side (403) del permiso HasRolePermission y filtrado ORM por ambito
(ScopeFilterMixin) con intromision IDOR (404).
"""

from types import SimpleNamespace

import pytest
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.authentication.adapters.models import Role, User, UserRole
from apps.authentication.adapters.permissions import (
    DENY,
    RBAC_MATRIX,
    HasRolePermission,
    get_scope,
)
from apps.authentication.adapters.serializers import TokenObtainPairSerializer
from core.adapters.scope_filter import ScopeFilterMixin

PASSWORD = "pwd_seguro_t012"
C1 = "aaaaaaaa-1111-4111-8111-111111111111"
C2 = "aaaaaaaa-2222-4222-8222-222222222222"
F1 = "aaaaaaaa-3333-4333-8333-333333333333"

# Matriz literal de specify.md 6.2 (fuente de verdad, no derivada del codigo):
# ausencia de rol en una celda es equivalente a DENY (mundo cerrado).
MATRIZ_62_LITERALS = {
    "expedientes": {
        "POST": {
            "ESTUDIANTE": "allow",
            "SECRETARIA_CARRERA": DENY,
            "SECRETARIO_ABOGADO": DENY,
            "ANALISTA_APOYO": DENY,
            "DECANO": DENY,
            "DIRECTOR_CARRERA": DENY,
            "ADMINISTRADOR": "allow",
        },
        "GET": {
            "ESTUDIANTE": "own",
            "SECRETARIA_CARRERA": "carrera",
            "SECRETARIO_ABOGADO": "facultad",
            "ANALISTA_APOYO": "facultad",
            "DECANO": "facultad",
            "DIRECTOR_CARRERA": "carrera",
            "ADMINISTRADOR": "allow",
        },
    },
    "expedientes:enviar": {
        "POST": {
            "ESTUDIANTE": "own",
            "SECRETARIA_CARRERA": DENY,
            "SECRETARIO_ABOGADO": DENY,
            "ANALISTA_APOYO": DENY,
            "DECANO": DENY,
            "DIRECTOR_CARRERA": DENY,
        }
    },
    "peticiones": {
        "POST": {
            "ESTUDIANTE": "own",
            "SECRETARIA_CARRERA": DENY,
            "SECRETARIO_ABOGADO": DENY,
            "ANALISTA_APOYO": DENY,
            "DECANO": DENY,
            "DIRECTOR_CARRERA": DENY,
            "ADMINISTRADOR": "allow",
        }
    },
    "peticiones:documento": {
        "POST": {
            "ESTUDIANTE": "own",
            "SECRETARIA_CARRERA": "asignado",
            "SECRETARIO_ABOGADO": "asignado",
            "ANALISTA_APOYO": "asignado",
            "DECANO": DENY,
            "DIRECTOR_CARRERA": "asignado",
            "ADMINISTRADOR": "allow",
        }
    },
    "checklist": {
        "PUT": {
            "ESTUDIANTE": DENY,
            "SECRETARIA_CARRERA": DENY,
            "SECRETARIO_ABOGADO": "allow",
            "ANALISTA_APOYO": "borrador",
            "DECANO": DENY,
            "DIRECTOR_CARRERA": DENY,
            "ADMINISTRADOR": "allow",
        }
    },
    "expedientes:observar": {
        "POST": {
            "ESTUDIANTE": DENY,
            "SECRETARIA_CARRERA": DENY,
            "SECRETARIO_ABOGADO": "allow",
            "ANALISTA_APOYO": DENY,
            "DECANO": DENY,
            "DIRECTOR_CARRERA": DENY,
        }
    },
    "informes": {
        "POST": {
            "ESTUDIANTE": DENY,
            "SECRETARIA_CARRERA": DENY,
            "SECRETARIO_ABOGADO": "allow",
            "ANALISTA_APOYO": "borrador",
            "DECANO": DENY,
            "DIRECTOR_CARRERA": DENY,
        }
    },
    "declaratorias": {
        "POST": {
            "ESTUDIANTE": DENY,
            "SECRETARIA_CARRERA": DENY,
            "SECRETARIO_ABOGADO": DENY,
            "ANALISTA_APOYO": DENY,
            "DECANO": "allow",
            "DIRECTOR_CARRERA": DENY,
        }
    },
    "catalogos:requisitos": {
        "POST": {
            "ESTUDIANTE": DENY,
            "SECRETARIA_CARRERA": DENY,
            "SECRETARIO_ABOGADO": DENY,
            "ANALISTA_APOYO": DENY,
            "DECANO": DENY,
            "DIRECTOR_CARRERA": DENY,
            "ADMINISTRADOR": "allow",
        }
    },
}


def _privada_codificada(recurso, metodo, rol):
    return RBAC_MATRIX.get(recurso, {}).get(metodo, {}).get(rol, DENY)


def _comparar_matrices(codificadas, literales):
    for recurso, metodos in literales.items():
        for metodo, rol_map in metodos.items():
            for rol, alcance in rol_map.items():
                if _privada_codificada(recurso, metodo, rol) != alcance:
                    return False, f"{recurso}/{metodo}/{rol}"
    return True, "ok"


def test_matriz_codificada_coincide_literal_62(db):
    coincide, detalle = _comparar_matrices(RBAC_MATRIX, MATRIZ_62_LITERALS)
    assert coincide, detalle


@pytest.fixture(name="usuarios")
def fixture_usuarios(db):
    """Cuentas por cada rol institucional del modelo T007 (8 roles)."""
    fabrica = {}
    for rol in (
        "ESTUDIANTE",
        "SECRETARIA_CARRERA",
        "SECRETARIO_ABOGADO",
        "ANALISTA_APOYO",
        "DECANO",
        "DIRECTOR_CARRERA",
        "RESPONSABLE_DEPENDENCIA",
        "ADMINISTRADOR",
    ):
        user = User.objects.create_user(
            username=f"t012_{rol.lower()}", password=PASSWORD
        )
        role, _ = Role.objects.get_or_create(name=rol)
        UserRole.objects.get_or_create(user=user, role=role)
        fabrica[rol] = user
    return fabrica


PARAMETROS_CELDAS = [
    ("expedientes", "POST", "ESTUDIANTE", "allow"),
    ("expedientes", "POST", "DECANO", DENY),
    ("expedientes", "GET", "ESTUDIANTE", "own"),
    ("expedientes", "GET", "SECRETARIA_CARRERA", "carrera"),
    ("expedientes", "GET", "DECANO", "facultad"),
    ("expedientes", "GET", "ADMINISTRADOR", "allow"),
    ("expedientes:enviar", "POST", "ESTUDIANTE", "own"),
    ("expedientes:enviar", "POST", "ANALISTA_APOYO", DENY),
    ("peticiones", "POST", "ESTUDIANTE", "own"),
    ("peticiones", "POST", "SECRETARIO_ABOGADO", DENY),
    ("peticiones:documento", "POST", "ESTUDIANTE", "own"),
    ("peticiones:documento", "POST", "SECRETARIA_CARRERA", "asignado"),
    ("peticiones:documento", "POST", "DECANO", DENY),
    ("peticiones:documento", "POST", "DIRECTOR_CARRERA", "asignado"),
    ("checklist", "PUT", "SECRETARIO_ABOGADO", "allow"),
    ("checklist", "PUT", "ANALISTA_APOYO", "borrador"),
    ("checklist", "PUT", "DECANO", DENY),
    ("expedientes:observar", "POST", "SECRETARIO_ABOGADO", "allow"),
    ("expedientes:observar", "POST", "ESTUDIANTE", DENY),
    ("informes", "POST", "SECRETARIO_ABOGADO", "allow"),
    ("informes", "POST", "ANALISTA_APOYO", "borrador"),
    ("declaratorias", "POST", "DECANO", "allow"),
    ("declaratorias", "POST", "ADMINISTRADOR", DENY),
    ("catalogos:requisitos", "POST", "ADMINISTRADOR", "allow"),
    ("catalogos:requisitos", "POST", "ESTUDIANTE", DENY),
]


@pytest.mark.parametrize("recurso, metodo, rol, esperado", PARAMETROS_CELDAS)
def test_celda_matriz_por_rol(usuarios, recurso, metodo, rol, esperado):
    assert get_scope(usuarios[rol], recurso, metodo) == esperado


def test_rol_fuera_de_matriz_denegado_mundo_cerrado(usuarios):
    responsable = usuarios["RESPONSABLE_DEPENDENCIA"]
    assert get_scope(responsable, "expedientes", "GET") == DENY
    assert get_scope(responsable, "declaratorias", "POST") == DENY
    assert get_scope(responsable, "checklist", "PUT") == DENY


def test_anonimo_sin_token_denegado(db):
    assert get_scope(None, "expedientes", "GET") == DENY


class DeclaratoriasSandbox(APIView):
    """Vista sandbox: endpoint reservado para DECANO (criterio T009)."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [HasRolePermission]
    rbac_resource = "declaratorias"

    def post(self, request, *args, **kwargs):
        return Response({"declaratoria": True})


def _llamar_sandbox(method, user):
    serializador = TokenObtainPairSerializer(
        data={"username": user.username, "password": PASSWORD}
    )
    serializador.is_valid(raise_exception=True)
    access = serializador.validated_data["access"]
    request = method("/", {}, format="json", HTTP_AUTHORIZATION=f"Bearer {access}")
    return DeclaratoriasSandbox.as_view()(request)


def test_estudiante_acceso_recurso_decano_403(usuarios):
    respuesta = _llamar_sandbox(APIRequestFactory().post, usuarios["ESTUDIANTE"])
    assert respuesta.status_code == 403


def test_decano_acceso_recurso_decano_200(usuarios):
    respuesta = _llamar_sandbox(APIRequestFactory().post, usuarios["DECANO"])
    assert respuesta.status_code == 200


def test_rol_responsable_recurso_declaratorias_403(usuarios):
    respuesta = _llamar_sandbox(
        APIRequestFactory().post, usuarios["RESPONSABLE_DEPENDENCIA"]
    )
    assert respuesta.status_code == 403


def test_permiso_sin_rbac_resource_deniega(db):
    class SinRecurso(APIView):
        authentication_classes = []
        permission_classes = [HasRolePermission]

    drf_request = Request(APIRequestFactory().post("/"))
    drf_request.user = AnonymousUser()
    assert HasRolePermission().has_permission(drf_request, SinRecurso()) is False


# --- Aislamiento por ambito (RNF-003 / C-005) ---


class ScopeSandbox(ScopeFilterMixin):
    scope_owner_field = "id"
    scope_carrera_field = "carrera_id"
    scope_facultad_field = "facultad_id"


MIXIN = ScopeSandbox()


def _scoped(user):
    return MIXIN.scope_queryset(User.objects.all(), SimpleNamespace(user=user))


def test_scope_estudiante_solo_lo_propio(usuarios):
    estudiante = usuarios["ESTUDIANTE"]
    assert set(_scoped(estudiante)) == {estudiante}
    assert usuarios["DECANO"] not in set(_scoped(estudiante))


def test_scope_secretaria_carrera(usuarios):
    secretaria = usuarios["SECRETARIA_CARRERA"]
    secretaria.carrera_id = C1
    secretaria.save()
    de_su_carrera = User.objects.create_user(
        username="t012_est_c1", password=PASSWORD, carrera_id=C1
    )
    resultado = set(_scoped(secretaria))
    assert de_su_carrera in resultado
    assert usuarios["DECANO"] not in resultado


def test_scope_decano_facultad(usuarios):
    decano = usuarios["DECANO"]
    decano.facultad_id = F1
    decano.save()
    resultado = set(_scoped(decano))
    assert decano in resultado
    assert usuarios["ESTUDIANTE"] not in resultado


def test_scope_director_carrera(usuarios):
    director = usuarios["DIRECTOR_CARRERA"]
    director.carrera_id = C2
    director.save()
    resultado = set(_scoped(director))
    assert director in resultado
    assert usuarios["DECANO"] not in resultado


def test_scope_admin_ve_todos(usuarios):
    assert _scoped(usuarios["ADMINISTRADOR"]).count() == User.objects.count()


def test_scope_responsable_sin_ambito_vacio(usuarios):
    assert set(_scoped(usuarios["RESPONSABLE_DEPENDENCIA"])) == set()


def test_scope_usuario_sin_rol_vacio(db):
    virgen = User.objects.create_user(username="t012_virgen", password=PASSWORD)
    assert set(_scoped(virgen)) == set()


def test_union_de_scope_con_roles_multiples(usuarios):
    combinado = usuarios["ESTUDIANTE"]
    combinado.carrera_id = C1
    combinado.save()
    usuarios["SECRETARIA_CARRERA"].carrera_id = C1
    usuarios["SECRETARIA_CARRERA"].save()
    role_sec, _ = Role.objects.get_or_create(name="SECRETARIA_CARRERA")
    UserRole.objects.get_or_create(user=combinado, role=role_sec)
    nombres = {u.username for u in set(_scoped(combinado))}
    assert nombres >= {
        "t012_estudiante",
        "t012_secretaria_carrera",
    }


class DetalleSandbox(ScopeSandbox, APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs):
        qs = self.scope_queryset(User.objects.all(), request)
        obj = get_object_or_404(qs, pk=kwargs["pk"])
        return Response({"username": obj.username})


def _token(user):
    serializador = TokenObtainPairSerializer(
        data={"username": user.username, "password": PASSWORD}
    )
    serializador.is_valid(raise_exception=True)
    return serializador.validated_data["access"]


def test_idor_del_ajeno_por_uuid_404_del_propio_200(usuarios):
    factory = APIRequestFactory()
    estudiante = usuarios["ESTUDIANTE"]
    decano = usuarios["DECANO"]

    propio = DetalleSandbox.as_view()(
        factory.get("/", HTTP_AUTHORIZATION=f"Bearer {_token(estudiante)}"),
        pk=estudiante.pk,
    )
    ajeno = DetalleSandbox.as_view()(
        factory.get("/", HTTP_AUTHORIZATION=f"Bearer {_token(estudiante)}"),
        pk=decano.pk,
    )
    assert propio.status_code == 200
    assert ajeno.status_code == 404
