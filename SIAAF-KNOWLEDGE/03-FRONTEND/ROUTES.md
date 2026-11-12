---
system: SGT-SIAAF
type: frontend
area: routes
status: verified
source: verified-code
last_verified: 2026-11-11
---

# Rutas frontend

**Código:** `frontend/src/app/router.tsx` (lazy loading de todas las páginas), guardas en `frontend/src/auth/guards.tsx` (`RequireAuth`, `RequireRole`, `RedirectIfAuthenticated`), roles operativos en `frontend/src/auth/roles.ts`.
**Especificación:** `sgt-siaaf/specs/003-frontend-titulacion/specify.md` §6; lista oficial también en `AGENTS.md` §4.

| Vista | Ruta | Componente | Guarda | Estado real |
|---|---|---|---|---|
| V-01 | `/login` | `features/auth/LoginPage.tsx` | `RedirectIfAuthenticated` | Hecha |
| — | `/` | `IndexRedirect` (en `router.tsx`) | `RequireAuth` | Redirige por rol |
| V-02 | `/estudiante` | `features/dashboard/StudentDashboardPage.tsx` | `RequireRole ['ESTUDIANTE']` | Hecha |
| V-03 | `/estudiante/solicitud/nueva` | `features/solicitud/NuevaSolicitudPage.tsx` | `RequireRole ['ESTUDIANTE']` | Hecha (`carrera_id` UUID manual; sin catálogo BE-10; sin modalidad BE-06) |
| V-04 | `/expedientes/:id` | `features/expediente/ExpedientePage.tsx` | `RequireAuth` | Hecha |
| V-05 | `/expedientes/:id/peticiones` | `features/peticiones/PeticionesPage.tsx` | `RequireAuth` | **Implementada** (FE-T501–506, 2026-11-12) |
| V-06 | `/expedientes/:id/peticiones/:peticionId` | `features/peticiones/SeguimientoPeticionPage.tsx` | `RequireAuth` | **Implementada** (FE-T601–605, 2026-11-12; limitada por BE-02) |
| V-07 | `/bandeja` | `features/bandeja/BandejaPage.tsx` | `RequireRole OPERATIONAL_ROLES` | **Implementada** (FE-T701–706, 2026-11-12; limitada por BE-09) |
| V-08 | `/bandeja/:id` | `features/bandeja/DetalleFuncionarioPage.tsx` | `RequireRole OPERATIONAL_ROLES` | **Implementada** (FE-T801–810, 2026-11-12) |
| V-09 | `/no-habilitado` | `features/no-habilitado/NoHabilitadoPage.tsx` | `RequireAuth` | **Implementada** (FE-T901–904, 2026-11-12): motivo, dependencia `BE-xx`, código de referencia y salidas; destino de `RequireRole` con `?motivo=rol-no-autorizado` |
| 404 | `*` | `app/NotFoundPage.tsx` | — | Hecha (FE-T1211) |

`OPERATIONAL_ROLES` = ADMINISTRADOR, SECRETARIO_ABOGADO, ANALISTA_APOYO, DECANO, SECRETARIA_CARRERA, DIRECTOR_CARRERA. **`RESPONSABLE_DEPENDENCIA` no está incluido** (coherente con que no tiene celdas en el RBAC backend; ver [[PERMISSIONS_ROLES]]).

Los tamaños de los stubs se midieron con `wc -c` el 2026-11-11 (DP2 cita 190/188/175/186 B: cifras de una versión anterior).

Las rutas `/origen` y `/ruta-inexistente` solo aparecen en pruebas (`app/router.test.tsx`, `App.test.tsx`).

## Estados de error (no son rutas)

401 → aviso + redirección a `/login` (sin página); 403 → `ForbiddenState` en vista con destino V-09; 404 → página; 500/503 → `ErrorState` con reintento real (`lib/apiErrorPresentation.ts`). Fuente: `diseno-ui/ui/titulacion-v2/especificaciones/08_UI_ERROR_STATES_SPEC.md`, specify 003 §9.3.

## Relacionado

[[03-FRONTEND/MODULES|Módulos frontend]] · [[COMPONENTS]] · [[FRONTEND_ARCHITECTURE]]
