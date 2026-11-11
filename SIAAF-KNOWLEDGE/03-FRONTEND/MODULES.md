---
system: SGT-SIAAF
type: module-catalog
area: frontend
status: verified
source: verified-code
last_verified: 2026-11-11
---

# Módulos frontend

Ruta base: `frontend/src/`. Estructura definida en `sgt-siaaf/specs/003-frontend-titulacion/plan.md` §4.

| Módulo | Archivos principales | Endpoints consumidos | Estado |
|---|---|---|---|
| `api/` | `endpoints/{auth,expedientes,checklist,notificaciones}.ts`, `types/` | Los de [[API_CONTRACTS]] salvo peticiones (aún sin `endpoints/peticiones.ts`) | Implementado para V-01…V-04 |
| `auth/` | `AuthContext.tsx`, `useAuth.ts`, `jwt.ts`, `storage.ts`, `guards.tsx`, `redirect.ts`, `roles.ts` | `POST /auth/token/` | Hecho (F1). Sin refresh: re-login al expirar (plan 003 §6) |
| `app/` | `router.tsx`, `providers.tsx`, `App.tsx`, `NotFoundPage.tsx` | — | Hecho (F0, FE-T1211) |
| `components/ui/` | Alert, Badge, Button, Card, Checkbox, EmptyState, ErrorState, FileUpload, ForbiddenState, Input, Modal, NotFoundState, Pagination, Radio, Select, Spinner, Table, Textarea, Timeline | — | Hecho (F2; 170 pruebas; cobertura 96,12 % según `CLAUDE.md`) |
| `components/feedback/` | `ErrorBoundary.tsx`, `ToastProvider.tsx` | — | Hecho |
| `components/layout/` | `AppLayout`, `Header`, `Sidebar`, `SkipLink`, `DemoBanner` | — | Hecho |
| `features/auth/` | `LoginPage`, `LoginForm` | login | V-01 Hecha |
| `features/dashboard/` | `StudentDashboardPage`, `ExpedientesCard`, `NotificacionesCard`, `AccesosRapidos`, `queries.ts` | bandeja, notificaciones | V-02 Hecha |
| `features/solicitud/` | `NuevaSolicitudPage`, `NuevaSolicitudForm`, `queries.ts` | `POST /expedientes/` | V-03 Hecha (sin catálogo de carreras ni modalidad) |
| `features/expediente/` | `ExpedientePage`, `ExpedienteHeader`, `ChecklistSection`, `PeticionesSection`, `ObservarDialog`, `DescargaButton`, `accionesPorRolEstado.ts`, `errors.ts`, `queries.ts` | detalle, enviar, checklist, observar, subsanar, descarga | V-04 Hecha |
| `features/peticiones/` | `PeticionesPage`, `SeguimientoPeticionPage` | — | **Stubs** (V-05/V-06, FE-T501…T605 pendientes) |
| `features/bandeja/` | `BandejaPage`, `DetalleFuncionarioPage` | — | **Stubs** (V-07/V-08, FE-T701…T810 pendientes) |
| `features/no-habilitado/` | `NoHabilitadoPage` | — | V-09 Hecha |
| `lib/` | `apiErrorPresentation.ts`, `dates.ts`, `download.ts`, `env.ts`, `files.ts`, `logger.ts`, `queryClient.ts`, `storage.ts` | — | Hecho |
| `mocks/` | Handlers MSW para pruebas | — | Hecho |
| `styles/` | `tokens.css` (FE-T006) | — | Hecho |

## Dependencias reales (`frontend/package.json`)

- Runtime: `react ^19.3.1`, `react-dom ^19.3.1`, `react-router-dom ^7.18.5`, `@tanstack/react-query ^5.105.3`. **Nada más.**
- Dev: vite, typescript, vitest, @vitest/coverage-v8, jsdom, msw, @testing-library/*, vitest-axe, eslint (+ jsx-a11y, react-hooks, typescript-eslint), prettier.
- **No** están instalados Framer Motion, React Hook Form ni Zod, aunque [[DP2-PLAN_MAESTRO]] §7.3 afirma "Framer Motion (ya en deps)". Agregarlos requiere autorización humana (`AGENTS.md` §3.2).

Scripts: `lint` (`eslint .`), `typecheck` (`tsc -b --noEmit`), `test` (`vitest run`), `test:coverage`, `build` (`tsc -b && vite build`).

## Pruebas

58 archivos de prueba; 328 pruebas. Ejecuciones de esta sesión en [[REGRESSION_TESTS]].

## Relacionado

[[ROUTES]] · [[COMPONENTS]] · [[FRONTEND_ARCHITECTURE]] · [[TASKS]]
