---
title: "Módulo: authentication"
---

# M-01 — authentication

| Campo | Valor |
|---|---|
| Objetivo | Identidad institucional, roles, emisión de JWT y matriz de autorización |
| Responsabilidad | Usuario (UUID, cédula, carrera/facultad), catálogo de roles, asignaciones, claims del token, RBAC de mundo cerrado |
| Procesos | Login; autorización de todas las operaciones de la API |
| Roles | Todos (define la matriz) |

## Modelos (`adapters/models.py`)

| Modelo | Campos clave | Relaciones/Restricciones |
|---|---|---|
| `User` (AbstractUser) | `id` UUID, `cedula` único (validador de dígitos), `carrera_id`, `facultad_id` (UUID indexados) | `has_role()`, `get_roles()` |
| `Role` | `name` unique con choices de 8 roles, `description` | — |
| `UserRole` | `fecha_asignacion` | FK user+role; UniqueConstraint `(user, role)` |

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/v1/auth/token/` | Devuelve `{access, refresh}`; inyecta claims `cedula` y `roles` |

## Reglas de negocio y permisos

- Matriz `RBAC_MATRIX` (permissions.py:24-115): recurso × método → roles con scopes (`allow`, `own`, `carrera`, `facultad`, `asignado`, `borrador`, `deny`). Celda vacía = denegado.
- `HasRolePermission`: deniega si la vista no declara recurso RBAC.
- Orden restrictivo de scopes: `own > asignado > borrador > carrera > facultad > allow`.

## Dependencias

Ninguna externa (es la base). `core.scope_filter` consume los roles para filtrar querysets.

## Pruebas (28)

`test_jwt.py` (7): login válido/inválido, expiración, sin token, firma inválida. `test_rbac_permissions.py` (17): matriz == literal 6.2 de la spec, celdas por rol, mundo cerrado, anon 401, IDOR. `test_django_admin.py` (4): smoke del Admin (ADR-0009).

## Administración

`seed_initial_data` (management command idempotente): 8 cuentas demo (`SgtDemo2026!`) con advertencia explícita de no producción.

## Estado y limitaciones

- **Implementado y verificado.**
- JWT sin rotación ni blacklist (AUD-P2-04); sin throttling en el login (AUD-P0-02).
- Celdas de la matriz sin endpoint asociado (`catalogos:requisitos`) — preparación futura.
