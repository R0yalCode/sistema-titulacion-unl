---
system: SGT-SIAAF
type: frontend
area: components
status: verified
source: verified-code
last_verified: 2026-11-11
---

# Componentes frontend

## UI Kit existente (`frontend/src/components/ui/`, exportados en `index.ts`)

| Componente | Tarea | Notas |
|---|---|---|
| `Input`, `Textarea`, `Select`, `Checkbox`, `Radio` | FE-T019 | Campos accesibles |
| `Badge`, `Card`, `Alert`, `Spinner` | FE-T020 | — |
| `EmptyState`, `ErrorState`, `NotFoundState`, `ForbiddenState` | FE-T021 | `ErrorState` con reintento real; `ForbiddenState` → V-09 |
| `Table` | FE-T022 | Responsive |
| `Pagination` | FE-T023 | — |
| `Modal` | FE-T024 | Focus trap |
| `Timeline` | FE-T025 | Estados del expediente |
| `FileUpload` | FE-T026 | Solo PDF |
| `Button` | — | — |
| `ToastProvider` (en `components/feedback/`) | FE-T027 | — |

Diseño: tokens en `frontend/src/styles/tokens.css`; especificaciones en `diseno-ui/ui/titulacion-v2/especificaciones/01…08`. Los prototipos A/B son solo referencia visual: **prohibido copiar su código** (`AGENTS.md` §3.4).

## Componentes propuestos (no existen)

Citados en [[DP2-ARQUITECTURA_DASHBOARDS]], [[DP2-MATRIZ_ACCIONES_RAPIDAS]] y [[DP2-PLAN_MAESTRO]]: `KPICard`, `ChartWidget`, `WorkTable`, `ModalidadPanel`, `AccionesRapidas` (genérico), `ExportButton`, `CambiarModalidadDialog`. La ARQUITECTURA_DASHBOARDS §6 dice "Componentes base listos: … por crear en F3": **no existen** en el código (verificado con `ls` el 2026-11-11). Lo que sí existe es `features/dashboard/AccesosRapidos.tsx` (accesos locales del estudiante) y `features/expediente/accionesPorRolEstado.ts` (matriz de acciones por rol/estado de V-04).

## Relacionado

[[03-FRONTEND/MODULES|Módulos frontend]] · [[ROUTES]]
