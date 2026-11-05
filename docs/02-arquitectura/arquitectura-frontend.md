---
title: "Arquitectura del frontend"
---

# Arquitectura del frontend

## Stack

| Capa | Tecnología |
|---|---|
| UI | React 19 + TypeScript 5.9 (estricto) |
| Build | Vite 8 |
| Datos servidor | TanStack Query 5 (`staleTime` 30 s, retry solo 5xx) |
| Routing | react-router-dom 7 (lazy loading por página) |
| Estilos | CSS Modules + tokens (`src/styles/tokens.css`) |
| Pruebas | Vitest + Testing Library + MSW + vitest-axe |
| Calidad | ESLint 9 (flat, regla anti-imports-entre-features), `tsc -b` |

## Estructura

```
frontend/src/
├── app/          # router, providers, App, 404
├── api/          # client (fetch + JWT + timeout), errors, endpoints/
├── auth/         # AuthContext, guards, jwt (decode+exp), storage (sessionStorage)
├── components/
│   ├── ui/       # ~24 componentes base (Button, Table, Modal, FileUpload…)
│   ├── layout/   # AppLayout, Header, Sidebar, DemoBanner, SkipLink
│   └── feedback/ # ErrorBoundary, ToastProvider
├── features/     # 9 páginas V-01…V-09 (stubs en F0–F1)
├── lib/          # env, files (validación PDF), logger, apiErrorPresentation
├── mocks/        # MSW handlers (solo para pruebas)
├── styles/       # tokens.css, global.css
└── test/         # setup (MSW + axe), renderWithProviders
```

## Rutas y guards

| Ruta | Vista | Guard |
|---|---|---|
| `/login` | V-01 | Público |
| `/` | Redirección por rol | Requiere sesión |
| `/estudiante`, `/estudiante/solicitud/nueva` | V-02, V-03 | Rol ESTUDIANTE |
| `/expedientes/:id`, `/expedientes/:id/peticiones`, `/expedientes/:id/peticiones/:peticionId` | V-04…V-06 | Requiere sesión |
| `/bandeja`, `/bandeja/:id` | V-07, V-08 | Roles operativos |
| `/no-habilitado` | V-09 | En sesión |
| `*` | 404 | Público |

Redirección post-login: `ESTUDIANTE → /estudiante`; roles operativos → `/bandeja` (`src/auth/redirect.ts`).

## Manejo de sesión y errores

- Access token en `sessionStorage` (`sgt.access`); expiración validada al decodificar el JWT.
- Handler global de 401: cierra sesión, limpia la caché de Query, notifica y redirige a `/login`.
- `ApiError` normaliza 400/401/403/404/409/412/422/428/429/500/502/503/504 y errores de campo DRF; `apiErrorPresentation` los mapea a estados de UI (404→`NotFoundState`, 403→`ForbiddenState`, 5xx→"Servicio no disponible").

## Estado actual

F0–F1 completos y probados (198 pruebas, axe en componentes). Las 9 vistas de negocio son stubs pendientes del plan FE (`specs/003-frontend-titulacion/tasks.md`).
