---
title: "Seguridad — Autorización"
---

# Autorización

## Modelo: RBAC de mundo cerrado

Toda autorización pasa por `RBAC_MATRIX` (`apps/authentication/adapters/permissions.py:24-115`): recurso × método HTTP → conjunto de scopes por rol. **Una celda vacía deniega**; una vista que no declare recurso RBAC también deniega (`HasRolePermission`).

## Scopes

| Scope | Significado |
|---|---|
| `allow` | Paso libre (el queryset filtra después) |
| `own` | Solo objetos propios |
| `carrera` | Objetos de su carrera |
| `facultad` | Objetos de su facultad |
| `asignado` | Objetos donde el rol del usuario es la dependencia emisora |
| `borrador` | Solo operaciones en fase de borrador (Analista de Apoyo) |
| `deny` | Denegado explícito |

Orden restrictivo al acumular roles: `own > asignado > borrador > carrera > facultad > allow`.

## Aislamiento de datos (anti-IDOR)

`ScopeFilterMixin` (`core/adapters/scope_filter.py`) traduce el scope del rol a filtros ORM sobre `estudiante_id`/`carrera_id`/`facultad_id`. Los detalles y acciones usan `get_object_or_404(self.get_queryset())`: **un objeto ajeno responde 404**, no 403 (no se filtra su existencia). Casos especiales con autorización manual equivalente: descarga de documentos (con soporte `asignado`) y marcar-leída (doble verificación de propiedad).

## Excepciones declaradas

- `ANALISTA_APOYO` tiene scope `borrador` en checklist/informes: evalúa y emite solo en fase de borrador.
- `RESPONSABLE_DEPENDENCIA` tiene bandeja denegada (su interacción es por peticiones asignadas).
- El servicio de declaratoria admite Analista en código, pero la matriz RBAC lo deniega antes (inconsistencia latente AUD-P2-07).

## Verificación

17 pruebas de la matriz (incluida su igualdad con el literal 6.2 de la spec) + 13 pruebas de aislamiento IDOR por los 8 roles + 4 pruebas E2E.
