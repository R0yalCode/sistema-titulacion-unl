# SGT-SIAAF — Frontend

Interfaz web del Sistema de Gestión del Trámite de Titulación e Integración Académica (SGT-SIAAF), Universidad Nacional de Loja. Es una **simulación académica con datos ficticios**: no está conectada a sistemas institucionales productivos y no tiene validez legal (ver [`../sgt-siaaf/.specify/memory/constitution.md`](../sgt-siaaf/.specify/memory/constitution.md)).

Este README documenta únicamente lo que existe en el código hoy. El contrato funcional vigente está en [`specs/003-frontend-titulacion/`](../sgt-siaaf/specs/003-frontend-titulacion/).

## Estado actual

Fase **F0 (andamiaje)**. Existen el proyecto base, el sistema de tokens, el layout, el router con las 9 vistas y el 404, todos con pruebas. **Ninguna vista tiene lógica real todavía**: las 9 páginas de vista son *stubs* (`<h1>Vista pendiente de implementación.</h1>`), no hay cliente HTTP, no hay autenticación real (solo un `AuthContext` que siempre devuelve `user: null`) y los handlers de MSW están vacíos. Nada de esto se simula como si funcionara: ver [Limitaciones](#limitaciones-de-integración-con-el-backend).

## Requisitos

- Node.js 20+ (verificado con Node 24.22.1 / npm 11.19.1).

## Instalación

```bash
npm ci
```

Si no existe `package-lock.json`, usar `npm install` en su lugar.

## Variables de entorno

Copiar `.env.example` a `.env` antes de ejecutar `dev`/`build`/`preview`:

```bash
cp .env.example .env
```

| Variable | Obligatoria | Uso |
|---|---|---|
| `VITE_API_BASE_URL` | Sí | Origen de la API, sin barra final. Sin este valor, la app muestra una pantalla de error de configuración en vez de arrancar (`src/lib/env.ts`). |
| `VITE_DEMO_MODE` | No | `true` muestra el banner "Entorno de demostración". |
| `VITE_USE_MOCKS` | No | Reservado para activar MSW en desarrollo (F1+). Actualmente no tiene efecto porque los handlers están vacíos. |
| `VITE_APP_NAME` | No | Nombre mostrado en el header. Por defecto `SGT-SIAAF`. |

Todas las variables `VITE_*` son públicas en el bundle; no colocar secretos.

## Scripts disponibles

| Script | Qué hace |
|---|---|
| `npm run dev` | Servidor de desarrollo (Vite). |
| `npm run build` | `tsc -b` (typecheck de build) + `vite build` → `dist/`. |
| `npm run preview` | Sirve `dist/` localmente. |
| `npm run lint` | ESLint (flat config: typescript-eslint, jsx-a11y, react-hooks). |
| `npm run typecheck` | `tsc -b --noEmit` en modo estricto. |
| `npm run format` | Prettier sobre todo el proyecto. |
| `npm run test` | Vitest (jsdom + Testing Library + MSW + vitest-axe). |
| `npm run test:coverage` | Igual que `test`, con reporte de cobertura v8. |

## Estructura

La estructura real sigue `plan.md` §4 (`src/{app,api,auth,components,features,lib,styles,types,mocks,test}`). Alias `@/` → `src/`.

## Limitaciones de integración con el backend

El backend actual **no** expone todo lo que el frontend necesita. Estas dependencias están registradas como `BE-01`…`BE-11` en [`specs/003-frontend-titulacion/tasks.md`](../sgt-siaaf/specs/003-frontend-titulacion/tasks.md) §2 y **no están autorizadas a resolverse modificando el backend**:

| ID | Falta | Afecta a |
|---|---|---|
| BE-01 | Perfil `/me` o claims `carrera`/`facultad` en el JWT (el token solo trae `cedula` y `roles`) | Dashboard, crear solicitud, expediente |
| BE-02 | `GET /api/v1/peticiones/{id}/` (detalle) y listado de documentos | Seguimiento de petición, detalle de funcionario |
| BE-03 | Refresh token y logout de servidor | Sesión: al expirar el access token hay que volver a iniciar sesión |
| BE-04 | El rol `ESTUDIANTE` no puede leer el checklist de su propio expediente (403 por diseño RBAC) | Expediente y requisitos |
| BE-05 | Perfil/historial del estudiante | Dashboard, crear solicitud, expediente |
| BE-06 | Campo `opcion_titulacion` en expediente/petición (no existe en ningún modelo) | Crear solicitud — **sin selector de modalidad de titulación implementado** |
| BE-07 | `motivo`/`motivo_observacion` expuesto en las respuestas de expediente/petición (solo existe en los *request* de observación/checklist) | Expediente, detalle de funcionario |
| BE-08 | CORS para el origen del frontend (no configurado en el backend) | Toda la app, en cuanto se conecte a una API real |
| BE-09 | Bandeja ampliada para roles sin expedientes asignados o filtros server-side | Bandeja del funcionario |
| BE-10 | Catálogo de carreras (`GET /api/v1/carreras/`) | Crear solicitud |
| BE-11 | Paquete de conflicto/versión (409/412/428 con `ETag`/`If-Match`) | Formularios de creación/edición — bloquea la tarea `FE-T1213` |

Además: no hay SAC/OAuth2/OIDC/TOTP (prohibido implementarlos sin autorización); los estados `CANCELADA` y `LEGALIZADO` existen en los enums del contrato pero no se producen en el flujo real, por lo que la UI no ofrece acciones para generarlos.

## Pruebas y accesibilidad

Vitest + React Testing Library + `vitest-axe` (WCAG 2.1 AA). `vitest-axe@0.1.0` tiene un bug de empaquetado (su `extend-expect.js` publicado está vacío); el workaround está documentado en `src/test/setup.ts` y `src/test/vitest-axe.d.ts`.

## Referencias

- [`specs/003-frontend-titulacion/specify.md`](../sgt-siaaf/specs/003-frontend-titulacion/specify.md) — vistas, rutas, requisitos.
- [`specs/003-frontend-titulacion/plan.md`](../sgt-siaaf/specs/003-frontend-titulacion/plan.md) — arquitectura y stack.
- [`specs/003-frontend-titulacion/tasks.md`](../sgt-siaaf/specs/003-frontend-titulacion/tasks.md) — tareas y su estado.
- [`specs/003-frontend-titulacion/clarify.md`](../sgt-siaaf/specs/003-frontend-titulacion/clarify.md) — decisiones, riesgos y bloqueos BE-01…BE-11.
