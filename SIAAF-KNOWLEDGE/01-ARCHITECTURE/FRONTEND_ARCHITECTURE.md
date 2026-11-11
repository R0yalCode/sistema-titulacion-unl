---
system: SGT-SIAAF
type: architecture
area: frontend
status: verified
source: verified-code
last_verified: 2026-11-11
---

# Arquitectura frontend

SPA React 19 + TypeScript + Vite; enrutado con React Router 7 (lazy loading); estado de servidor con TanStack Query 5; pruebas con Vitest + Testing Library + MSW + vitest-axe.

## Principios vinculantes

Fuente: `AGENTS.md`, `CLAUDE.md`, `sgt-siaaf/specs/003-frontend-titulacion/{clarify,specify,plan,tasks}.md`.

1. **Frontend only**: no se toca `backend/`, OpenAPI, migraciones, Constitución ni spec 001.
2. **Cero simulación (CA-G-01)**: sin datos, usuarios ni estados demo; sin "En revisión" ni "Proyecto de Emprendimiento"; sin porcentajes que el backend no entregue.
3. **El backend es la autoridad** de RBAC y reglas; el frontend solo oculta o muestra acciones (`features/expediente/accionesPorRolEstado.ts`).
4. **Sesión**: JWT en el cliente; sin refresh ni logout de servidor (no existen, BE-03); al expirar, re-login (plan 003 §6).
5. **Errores**: `lib/apiErrorPresentation.ts` normaliza; los errores de formulario usan `InlineAlert` (400/422); 409/412/428 bloqueados (FE-T1213 / BE-11).
6. **Accesibilidad AA** (axe en pruebas) y responsive desde 320 px (DoD, tasks 003 §19).

## Capas

```
features/<vista>  →  api/endpoints/*  →  cliente HTTP (auth/ + lib/)  →  /api/v1 (backend)
        ↓                  ↑
components/ui, layout, feedback      mocks/ (MSW en pruebas)
```

Configuración: `VITE_API_BASE_URL`, `VITE_DEMO_MODE`, `VITE_USE_MOCKS`, `VITE_APP_NAME` (`frontend/.env.example`, validadas en `lib/env.ts`). CORS del backend pendiente (BE-08).

## Relacionado

[[03-FRONTEND/MODULES|Módulos frontend]] · [[ROUTES]] · [[COMPONENTS]] · [[GENERAL_ARCHITECTURE]]
