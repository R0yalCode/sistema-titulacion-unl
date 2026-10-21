"""Adaptador de permisos RBAC server-side (RNF-002, C-004).

Evalua la combinacion (Rol x Recurso x Accion HTTP) contra la matriz
aprobada en specify.md seccion 6.2. El default es denegar (mundo cerrado).

Los valores de alcance distintos de DENY y ALLOW son contratos para el
filtrado ORM por ambito (core/adapters/scope_filter.py, T010):
o el permiso deja pasar y el queryset es quien aísla los registros.
"""

from rest_framework import permissions

from apps.authentication.adapters.models import User

ALLOW = "allow"
SCOPE_OWN = "own"
SCOPE_CARRERA = "carrera"
SCOPE_FACULTAD = "facultad"
SCOPE_ASIGNADO = "asignado"
SCOPE_BORRADOR = "borrador"
DENY = "deny"


RBAC_MATRIX = {
    "expedientes": {
        "POST": {"ESTUDIANTE": ALLOW, "ADMINISTRADOR": ALLOW},
        "GET": {
            "ESTUDIANTE": SCOPE_OWN,
            "SECRETARIA_CARRERA": SCOPE_CARRERA,
            "SECRETARIO_ABOGADO": SCOPE_FACULTAD,
            "ANALISTA_APOYO": SCOPE_FACULTAD,
            "DECANO": SCOPE_FACULTAD,
            "DIRECTOR_CARRERA": SCOPE_CARRERA,
            "ADMINISTRADOR": ALLOW,
        },
    },
    "expedientes:enviar": {"POST": {"ESTUDIANTE": SCOPE_OWN}},
    "peticiones": {"POST": {"ESTUDIANTE": SCOPE_OWN, "ADMINISTRADOR": ALLOW}},
    "peticiones:documento": {
        "POST": {
            "ESTUDIANTE": SCOPE_OWN,
            "SECRETARIA_CARRERA": SCOPE_ASIGNADO,
            "SECRETARIO_ABOGADO": SCOPE_ASIGNADO,
            "ANALISTA_APOYO": SCOPE_ASIGNADO,
            "DIRECTOR_CARRERA": SCOPE_ASIGNADO,
            "ADMINISTRADOR": ALLOW,
        }
    },
    "checklist": {
        "PUT": {
            "SECRETARIO_ABOGADO": ALLOW,
            "ANALISTA_APOYO": SCOPE_BORRADOR,
            "ADMINISTRADOR": ALLOW,
        },
        "PATCH": {
            "SECRETARIO_ABOGADO": ALLOW,
            "ANALISTA_APOYO": SCOPE_BORRADOR,
            "ADMINISTRADOR": ALLOW,
        },
    },
    "expedientes:observar": {"POST": {"SECRETARIO_ABOGADO": ALLOW}},
    "informes": {
        "POST": {
            "SECRETARIO_ABOGADO": ALLOW,
            "ANALISTA_APOYO": SCOPE_BORRADOR,
        }
    },
    "declaratorias": {
        "POST": {"DECANO": ALLOW},
        "PUT": {"DECANO": ALLOW},
        "PATCH": {"DECANO": ALLOW},
    },
    "catalogos:requisitos": {
        "POST": {"ADMINISTRADOR": ALLOW},
        "PUT": {"ADMINISTRADOR": ALLOW},
    },
}


def get_granted_scopes(user: "User | None", resource: str, method: str) -> set[str]:
    """Scopes concedidos a los roles del usuario sobre (recurso, metodo).

    Devuelve el conjunto con union de concesiones por rol. Conjunto vacio
    significa denegado.
    """
    methods = RBAC_MATRIX.get(resource, {})
    roles_map = methods.get(method.upper(), {})
    if user is None or not user.is_authenticated:
        return set()
    scopes = {roles_map[rol] for rol in user.get_roles() if rol in roles_map}
    return {s for s in scopes if s != DENY}


def get_scope(user: "User | None", resource: str, method: str) -> str:
    """Scope mas restrictivo concedido (para vistas con un solo alcance)."""
    scopes = get_granted_scopes(user, resource, method)
    if not scopes:
        return DENY
    restrictive_order = (
        SCOPE_OWN,
        SCOPE_ASIGNADO,
        SCOPE_BORRADOR,
        SCOPE_CARRERA,
        SCOPE_FACULTAD,
        ALLOW,
    )
    for scope in restrictive_order:
        if scope in scopes:
            return scope
    return DENY


class HasRolePermission(permissions.BasePermission):
    """Permiso DRF que evalua la matriz RBAC 6.2 (denegacion por defecto)."""

    message = (
        "El rol del usuario no esta autorizado para esta operacion sobre " "el recurso."
    )

    def has_permission(self, request, view) -> bool:
        resource = getattr(view, "rbac_resource", None)
        if resource is None:
            return False
        return bool(get_granted_scopes(request.user, resource, request.method))
