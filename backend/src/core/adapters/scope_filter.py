"""Filtro ORM de aislamiento por ambito institucional (RNF-003, C-005).

Previene la vulnerabilidad IDOR: cada consulta queda limitada al ambito del
usuario autenticado. Un registro ajeno desaparece del queryset, por lo que
el acceso por ID directo responde 404 (o 403 si hay permisos activos en la
vista). Este modulo de `core` no importa de `apps` (aislamiento hxagonal).
"""

from typing import ClassVar

from django.db.models import Q, QuerySet

SCOPE_ALL = "all"
SCOPE_OWN = "own"
SCOPE_CARRERA = "carrera"
SCOPE_FACULTAD = "facultad"
SCOPE_DENEGADO = "denegado"


class ScopeFilterMixin:
    """Mixin DRF que filtra el QuerySet por ámbito institucional del usuario.

    Uso (T018): la vista declara los nombres de campo del modelo
    (`scope_owner_field`, `scope_carrera_field`, `scope_facultad_field`) y
    su `get_queryset()` retorna `self.scope_queryset(qs, self.request)`.
    """

    scope_owner_field: str = "estudiante_id"
    scope_carrera_field: str = "carrera_id"
    scope_facultad_field: str = "facultad_id"

    ROW_TO_SCOPE: ClassVar[dict] = {
        "ESTUDIANTE": SCOPE_OWN,
        "SECRETARIA_CARRERA": SCOPE_CARRERA,
        "SECRETARIO_ABOGADO": SCOPE_FACULTAD,
        "ANALISTA_APOYO": SCOPE_FACULTAD,
        "DECANO": SCOPE_FACULTAD,
        "DIRECTOR_CARRERA": SCOPE_CARRERA,
        "RESPONSABLE_DEPENDENCIA": SCOPE_DENEGADO,
        "ADMINISTRADOR": SCOPE_ALL,
    }

    def scope_queryset(self, queryset: QuerySet, request) -> QuerySet:
        """Aplica el filtro de ámbito al queryset según los roles del usuario.

        Concesión por union: cada rol del usuario aporta su limite (own,
        carrera o facultad); ADMINISTRADOR concede todo; un rol sin ámbito
        conocido aporta nada (mundo cerrado).
        """
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            return queryset.none()
        scopes = {self.ROW_TO_SCOPE[r] for r in user.get_roles()}
        if not scopes:
            return queryset.none()
        if SCOPE_ALL in scopes:
            return queryset
        predicate = Q()
        if SCOPE_OWN in scopes:
            predicate |= Q(**{self.scope_owner_field: user.pk})
        if SCOPE_CARRERA in scopes and user.carrera_id:
            predicate |= Q(**{self.scope_carrera_field: user.carrera_id})
        if SCOPE_FACULTAD in scopes and user.facultad_id:
            predicate |= Q(**{self.scope_facultad_field: user.facultad_id})
        if not predicate:
            return queryset.none()
        return queryset.filter(predicate)
