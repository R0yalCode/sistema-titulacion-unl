# Tareas — Frontend de Titulación (SGT-SIAAF)

**Feature ID:** `003-frontend-titulacion`
**Documento:** `tasks.md`
**Versión:** 1.1.0
**Fecha:** 2026-11-04
**Estado:** Refactorizado tras la auditoría del frontend y los prototipos A/B (2026-11-04). Ver §1.1.
**Naturaleza:** Lista atómica de tareas. **No instala dependencias, no genera código y no modifica el backend.**

---

## 1.1 Registro de la refactorización (auditoría con evidencia, 2026-11-04)

Comandos ejecutados sobre `frontend/`: `npm run lint` ✅ · `npm run typecheck` ✅ · `npm run build` ✅ (12 chunks lazy; ver FE-T009) · `npm run test` → **23/24 pasan, 1 falla** (`AppLayout.test.tsx:27`, ver D-FE-01 en `clarify.md` §7.2).

- Los estados de F0 abajo se actualizaron **solo con esa evidencia**; las tareas se consideran cumplidas en cuanto a sus criterios específicos del andamio (las capacidades pendientes como MSW handlers o Toast se imputan a sus tareas de F1/F2).
- La implementación real y las desviaciones están descritas en `clarify.md` (CL-21, DEC-11…DEC-14, INC-14…INC-18, D-FE-01…D-FE-04).
- Nuevos rangos de ID autorizados en esta refactorización: **FE-T1210…FE-T1219** (fase F2.5: estados de error e higiene) y dependencia **BE-11**. No se reutiliza ningún ID reexistente para un alcance distinto (FE-T018 queda reserveado sin usar; no se asigna).
- Los prototipos A (9 vistas) y B (kit de errores) son referencia visual y de comportamiento no normativa (DEC-11); las tareas que los adaptan requieren traducir diseño a React, **no copiar HTML/CSS/JS**.

---

## 1. Convenciones

- **ID de tarea:** `FE-Tnnn` (frontend) y `BE-nn` (dependencia de backend, **no autorizada**).
- **Estado:** `Pendiente`, `En curso`, `Bloqueada`, `Hecha`, `Cancelada`.
- **Prioridad:** `Must`, `Should`, `Could`.
- **Estimación:** `S` (≤ 0.5 día), `M` (1–2 días), `L` (3–5 días).
- **Regla de atomicidad:** una tarea no implementa una vista completa si puede dividirse en UI, integración, validaciones y pruebas.
- **Regla de no simulación:** ninguna tarea puede crear datos ficticios en producción. Los mocks solo viven en `src/mocks/` y en pruebas.
- **Regla de no modificación:** ninguna tarea toca backend, migraciones, OpenAPI, constitución, `specs/001-tramite-titulacion/` ni documentos existentes.
- **Definición de hecha:** ver §12.

---

## 2. Dependencias de backend (NO AUTORIZADAS)

> Estas tareas pertenecen al backend. **No se ejecutan en esta feature.** Se registran para que el producto y el equipo de backend las prioricen. El frontend debe degradar con elegancia mientras no existan.

| ID | Dependencia | Vistas afectadas | Criterio de aceptación backend | Estado |
|----|-------------|------------------|-------------------------------|--------|
| **BE-01** | Perfil `/me` o claims de `carrera`/`facultad` en el JWT. | V-02, V-03, V-04, V-05, V-06 | Un usuario autenticado puede obtener su perfil (cédula, nombre, roles, carrera, facultad) sin exponer datos de otros. | **NO AUTORIZADA** |
| **BE-02** | `GET /api/v1/peticiones/{id}/` y listado de documentos de la petición. | V-04, V-06, V-08 | Detalle de petición con requisito, estado, dependencia, fechas y documentos; autorización por alcance. | **NO AUTORIZADA** |
| **BE-03** | Refresh token y logout de servidor. | V-01, layout | `POST /auth/refresh/` y `POST /auth/logout/` con revocación; cookies httpOnly si aplica. | **NO AUTORIZADA** |
| **BE-04** | Permitir `GET /expedientes/{id}/checklist/` al rol `ESTUDIANTE` (solo sus expedientes). | V-04 | El estudiante ve el checklist de su expediente sin ver el de otros. | **NO AUTORIZADA** |
| **BE-05** | Perfil e historial del estudiante (expedientes en todos los estados). | V-02, V-03, V-04 | El estudiante puede listar sus expedientes y datos de perfil. | **NO AUTORIZADA** |
| **BE-06** | Campo `opcion_titulacion` en expediente/petición. | V-03, V-04 | El expediente registra y devuelve la opción de titulación. | **NO AUTORIZADA** |
| **BE-07** | Exponer `motivo`/`motivo_observacion` en las respuestas de expediente y petición. | V-04, V-08 | La UI puede mostrar el motivo sin depender de un request. | **NO AUTORIZADA** |
| **BE-08** | CORS para el origen del frontend. | Todas | El navegador puede consumir `/api/v1/` desde el origen del frontend con `Authorization`. | **NO AUTORIZADA** |
| **BE-09** | Ampliar bandeja para roles sin expedientes y filtros server-side si el producto lo requiere. | V-07 | `SECRETARIA_CARRERA`/`DIRECTOR_CARRERA` ven lo que corresponda; filtros por estado/fecha. | **NO AUTORIZADA** |
| **BE-10** | Catálogo de carreras (`GET /api/v1/carreras/`). | V-03 | Lista de carreras activas con `id` y `nombre`. | **NO AUTORIZADA** |
| **BE-11** | Paquete de conflicto/versión para formularios: declarar `409` (petición duplicada), `412` (versión desactualizada) y `428` (versión requerida) con `ETag`/`If-Match` y `error.code` diferenciado. | Formularios V-03/V-04/V-05/V-06 | El OpenAPI documenta los códigos y el frontend puede distinguir cada escenario; sin esto la UI no implementa los inline-alerts del prototipo B. | **NO AUTORIZADA** (conditio de BE-11; representado solo visualmente en el prototipo B) |

---

## 3. Fase F0 — Andamiaje

### FE-T001 — Inicializar proyecto Vite + React + TypeScript

- **Objetivo:** crear la base del proyecto frontend con Vite, React y TypeScript en modo estricto.
- **Depende de:** ninguna.
- **Módulos:** `frontend/package.json`, `vite.config.ts`, `tsconfig.json`, `index.html`, `src/main.tsx`, `src/app/App.tsx`.
- **Pasos:**
  1. Crear proyecto Vite con template `react-ts`.
  2. Activar `strict`, `noUncheckedIndexedAccess`, `noImplicitOverride`.
  3. Configurar `base` y alias `@/` → `src/`.
  4. Verificar `npm run dev` y `npm run build`.
- **Criterios de aceptación:** la app arranca y compila sin errores; `tsc --noEmit` pasa.
- **Pruebas:** smoke de render de `App`.
- **Evidencia:** salida de `npm run build` y `tsc --noEmit`.
- **Estimación:** S. **Prioridad:** Must. **Estado:** **Hecha** (evidencia 2026-11-04: `npm run build` ✅, `tsc -b --noEmit` ✅, strict + `noUncheckedIndexedAccess` + `noImplicitOverride` activos en `tsconfig.app.json`; smoke `App.test.tsx` pasa).

### FE-T002 — Configurar ESLint, Prettier y reglas de código

- **Objetivo:** establecer lint y formato consistentes.
- **Depende de:** FE-T001.
- **Módulos:** `.eslintrc.cjs`, `.prettierrc`, `package.json` (scripts).
- **Pasos:**
  1. Configurar `eslint` con `typescript-eslint`, `react-hooks`, `jsx-a11y`.
  2. Prohibir `console.log` fuera de `src/lib/logger.ts`.
  3. Configurar Prettier y script `format`.
  4. Añadir scripts `lint`, `typecheck`, `test`, `test:coverage`.
- **Criterios de aceptación:** `npm run lint` y `npm run typecheck` pasan en el andamiaje.
- **Pruebas:** ejecución de scripts.
- **Evidencia:** salida de los scripts.
- **Estimación:** S. **Prioridad:** Must. **Estado:** **Hecha** (evidencia 2026-11-04: `eslint .` ✅ y `tsc -b --noEmit` ✅; flat config con jsx-a11y, react-hooks, `no-console` salvo `logger.ts`, `no-restricted-imports` de features; scripts `lint/typecheck/test/test:coverage/format` presentes).

### FE-T003 — Configurar Vitest, React Testing Library y MSW

- **Objetivo:** habilitar pruebas unitarias, de integración y de red.
- **Depende de:** FE-T001.
- **Módulos:** `vitest.config.ts`, `src/test/setup.ts`, `src/test/server.ts`, `src/test/renderWithProviders.tsx`.
- **Pasos:**
  1. Configurar `environment: jsdom`, `globals: true`, `setupFiles`.
  2. Configurar MSW (server en Node, browser en desarrollo).
  3. Añadir `renderWithProviders` con QueryClient y Router.
  4. Verificar una prueba de ejemplo.
- **Criterios de aceptación:** `npm run test` ejecuta y pasa la prueba de ejemplo.
- **Pruebas:** prueba smoke.
- **Evidencia:** salida de `npm run test`.
- **Estimación:** S. **Prioridad:** Must. **Estado:** **Hecha** (evidencia 2026-11-04: 23/24 pruebas pasan; setup con jest-dom + vitest-axe + MSW `onUnhandledRequest: 'error'`; `renderWithProviders` operativo). Nota de alcance: los **handlers MSW** están vacíos `[]` y no existe `public/mockServiceWorker.js` — la integración de mocks corresponde a FE-T014 (F1), no a FE-T003. `vitest-axe@0.1.0` usa un workaround documentado por bug de empaquetado.

### FE-T004 — Crear estructura de carpetas y alias

- **Objetivo:** materializar la estructura de `plan.md` §4.
- **Depende de:** FE-T001.
- **Módulos:** `src/{app,api,auth,components,features,lib,styles,types,mocks,test}`.
- **Pasos:**
  1. Crear carpetas y archivos `index.ts` mínimos donde corresponda.
  2. Configurar alias en `tsconfig` y `vite.config.ts`.
  3. Añadir regla de importación (sin imports profundos entre features).
- **Criterios de aceptación:** la estructura existe y el build resuelve alias.
- **Pruebas:** import de prueba con alias.
- **Evidencia:** árbol de carpetas y build.
- **Estimación:** S. **Prioridad:** Must. **Estado:** **Hecha** (evidencia 2026-11-04: estructura y alias `@/` verificadas). Desviaciones menores registradas en `plan.md` §4: extras (`src/assets/`, `features/index.ts`, `TokensShowcase.test.tsx`) y faltantes respecto al plan (`features/informes/`, `mocks/fixtures.ts`, `lib/format|validation|files|storage.ts`) que corresponden a tareas posteriores, no a FE-T004. `src/index.css` residual se trata en FE-T1210.

### FE-T005 — Validación de variables de entorno

- **Objetivo:** evitar arranques con configuración inválida.
- **Depende de:** FE-T001.
- **Módulos:** `src/lib/env.ts`, `.env.example`.
- **Pasos:**
  1. Leer `VITE_API_BASE_URL`, `VITE_DEMO_MODE`, `VITE_USE_MOCKS`, `VITE_APP_NAME`.
  2. Validar URL absoluta y sin barra final.
  3. Exponer un objeto `env` tipado y congelado.
  4. Mostrar pantalla de error de configuración si falta la URL.
- **Criterios de aceptación:** sin `VITE_API_BASE_URL` la app muestra error claro; con valor válido arranca.
- **Pruebas:** unitarias de validación.
- **Evidencia:** pruebas y `.env.example`.
- **Estimación:** S. **Prioridad:** Must. **Estado:** **Hecha** (evidencia 2026-11-04: `src/lib/env.ts` valida URL absoluta/protocolo/barra final con `EnvError` en español; `main.tsx` fail-fast accesible; `env.test.ts` cubre los casos; `env.test.ts` pasa).

### FE-T006 — Tokens de diseño y estilos globales

- **Objetivo:** implementar el sistema visual base.
- **Depende de:** FE-T001.
- **Módulos:** `src/styles/tokens.css`, `global.css`, `utilities.css`.
- **Pasos:**
  1. Extraer colores, tipografía, espaciado, radios, sombras y breakpoints de `01_UI_DESIGN_SYSTEM.md`.
  2. Definir variables CSS y `prefers-reduced-motion`.
  3. Reset mínimo y estilos de foco visible.
  4. Documentar tokens faltantes con `TODO` de diseño.
- **Criterios de aceptación:** los tokens existen y se usan en un componente de prueba; contraste base cumple AA.
- **Pruebas:** revisión visual y axe en componente de prueba.
- **Evidencia:** captura y lista de tokens.
- **Estimación:** M. **Prioridad:** Must. **Estado:** **Hecha** (evidencia 2026-11-04: `tokens.css` espejo de `01_UI_DESIGN_SYSTEM.md` (94 líneas), `global.css` con reset/foco/reduced-motion, `utilities.css` sr-only, `TokensShowcase.test.tsx` con axe ✅). `TODO` pendiente documentado: token "neutral" de estado (tokens.css:41); breakpoints de `tokens.css` (320/480/1440) alineados con plan.md §10.1, no con `04_UI_RESPONSIVE_GUIDELINES.md` (ver documento 04 reconciliado).

### FE-T007 — Providers globales y ErrorBoundary

- **Objetivo:** centralizar QueryClient, Auth, Router y manejo de errores.
- **Depende de:** FE-T001, FE-T003.
- **Módulos:** `src/app/providers.tsx`, `src/lib/queryClient.ts`, `src/components/feedback/ErrorBoundary.tsx`.
- **Pasos:**
  1. Crear `QueryClient` con la configuración de `plan.md` §8.
  2. Componer `QueryClientProvider`, `AuthProvider`, `ToastProvider`, `BrowserRouter`.
  3. Implementar `ErrorBoundary` con fallback accesible.
- **Criterios de aceptación:** un error de render muestra fallback y no rompe toda la app.
- **Pruebas:** prueba de ErrorBoundary.
- **Evidencia:** prueba y captura.
- **Estimación:** S. **Prioridad:** Must. **Estado:** **Hecha** (evidencia 2026-11-04: `providers.tsx` compone Query/Auth/Toast/BrowserRouter con ErrorBoundary exterior; `ErrorBoundary.tsx` completo con fallback `role="alert"` + "Reintentar"; `ErrorBoundary.test.tsx` pasa). Nota de alcance: `ToastProvider` es un stub con `showToast` vacío — la cola de toasts es la tarea FE-T027 (F2), no parte del CA de FE-T007.

### FE-T008 — Layout base y navegación

- **Objetivo:** crear el esqueleto visual de la aplicación.
- **Depende de:** FE-T006, FE-T007.
- **Módulos:** `src/components/layout/{AppLayout,Header,Sidebar,SkipLink,DemoBanner}.tsx`.
- **Pasos:**
  1. Header con nombre, cédula, roles y botón de sesión.
  2. Sidebar con enlaces por rol; menú colapsable en móvil.
  3. Skip link y `main` con foco.
  4. `DemoBanner` condicionado a `VITE_DEMO_MODE`.
- **Criterios de aceptación:** layout responsive; navegación por teclado; sin overflow a 320 px.
- **Pruebas:** RTL de navegación y axe.
- **Evidencia:** capturas en 320/768/1440.
- **Estimación:** M. **Prioridad:** Must. **Estado:** **Hecha** (evidencia 2026-11-04, cierre de F0: D-FE-01 resuelto — causa raíz confirmada: el botón `aria-label="Abrir navegación"` solo es visible vía `@media (max-width:768px)`; jsdom usa `window.innerWidth=1024` fijo y no implementa `window.matchMedia`, por lo que el elemento queda fuera del árbol de accesibilidad y su nombre accesible computado es `""` conforme a la especificación WAI-ARIA AccName para elementos ocultos — no es un bug de `dom-accessibility-api`/jsdom. Corrección aplicada solo en `AppLayout.test.tsx` (consulta directa por atributo para esa única aserción de estado), sin desactivar ninguna validación. 4/4 tests de `AppLayout.test.tsx` + axe pasan; 24/24 tests de la suite completa. Capturas responsive 320/768/1440 verificadas en navegador real: sin overflow horizontal en ninguna (`scrollWidth === clientWidth`), sidebar colapsa a drawer off-canvas en móvil/tablet y queda fija en escritorio con el botón hamburguesa correctamente oculto (`display:none`) a 1440px; `aria-expanded` alterna `false→true→false` con clics reales). El `onLogout` no-op sigue delegado a FE-T016 (F1) según su propio alcance.

### FE-T009 — Router base con lazy loading y 404

- **Objetivo:** definir rutas de `specify.md` §6 con carga diferida.
- **Depende de:** FE-T007, FE-T008.
- **Módulos:** `src/app/router.tsx`.
- **Pasos:**
  1. Definir rutas y `lazy` por feature.
  2. Añadir `Suspense` con loading accesible.
  3. Ruta `*` → 404.
  4. Placeholders de vistas hasta su implementación.
- **Criterios de aceptación:** todas las rutas resuelven; 404 funciona; lazy split visible en build.
- **Pruebas:** navegación básica.
- **Evidencia:** build con chunks.
- **Estimación:** S. **Prioridad:** Must. **Estado:** **Hecha** (evidencia 2026-11-04: `router.tsx` con las 10 rutas exactas de `specify.md` §6 + 404; `router.test.tsx` y `App.test.tsx` pasan; `npm run build` genera 10 chunks de página + index 291 KB / 91,9 KB gzip). Notas: `NotFoundPage` es un stub mínimo; su estilización con el kit de errores es FE-T1211; guardas de sesión no están incluidas en el CA de FE-T009 (corresponden a FE-T015).

### FE-T010 — README del frontend

- **Objetivo:** documentar arranque, scripts, variables y limitaciones.
- **Depende de:** FE-T001…FE-T009.
- **Módulos:** `frontend/README.md`.
- **Pasos:**
  1. Requisitos, instalación, scripts.
  2. Variables de entorno.
  3. Limitaciones (BE-01…BE-10) y enlaces a `specs/003-frontend-titulacion/`.
- **Criterios de aceptación:** un desarrollador puede arrancar el proyecto siguiendo el README.
- **Pruebas:** revisión manual.
- **Evidencia:** README.
- **Estimación:** S. **Prioridad:** Should. **Estado:** **Hecha** (evidencia 2026-11-04, cierre de F0: D-FE-03 resuelto — `frontend/README.md` reemplazado por documentación real: requisitos/instalación, tabla de variables de entorno, tabla de scripts reales de `package.json`, tabla BE-01…BE-11 con qué falta y a qué vista afecta, aviso explícito de que las 9 vistas son stubs sin lógica, enlaces relativos a `specs/003-frontend-titulacion/*.md` y a la Constitución verificados con `test -f`).

---

## 4. Fase F1 — Autenticación, sesión y cliente HTTP

### FE-T011 — Utilidades JWT y almacenamiento de sesión

- **Objetivo:** decodificar claims y persistir el token de forma controlada.
- **Depende de:** FE-T001.
- **Módulos:** `src/auth/jwt.ts`, `src/auth/storage.ts`.
- **Pasos:**
  1. Decodificar base64url sin verificar firma.
  2. Leer `cedula` y `roles`; validar tipos.
  3. Guardar/leer/borrar `access` en `sessionStorage` con clave `sgt.access`.
  4. No persistir `refresh`.
- **Criterios de aceptación:** token válido → usuario; token inválido → `null`; no se guarda `refresh`.
- **Pruebas:** unitarias de tokens válidos, malformados y expirados.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** **Hecha** (evidencia 2026-11-04: `jwt.ts` decodifica base64url sin verificar firma y valida tipos de `cedula`/`roles`/`exp`; `storage.ts` usa clave `sgt.access` y no expone ninguna función de `refresh`. `jwt.test.ts` (6 casos: válido, expirado, sin 3 segmentos, JSON inválido, sin cedula, roles no-array) y `storage.test.ts` (4 casos) pasan).

### FE-T012 — AuthContext y hook `useAuth`

- **Objetivo:** exponer sesión, usuario, login y logout a la app.
- **Depende de:** FE-T011.
- **Módulos:** `src/auth/AuthContext.tsx`, `src/auth/useAuth.ts`.
- **Pasos:**
  1. Estado `user`, `isAuthenticated`, `isLoading`.
  2. `login(tokens)`, `logout()`, `hasRole()`.
  3. Sincronizar con `storage`.
  4. Escuchar evento `storage` para multi-pestaña (opcional).
- **Criterios de aceptación:** login/logout actualizan el estado y la UI.
- **Pruebas:** RTL del provider.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** **Hecha** (evidencia 2026-11-04: `AuthContext.tsx` expone `user`/`isAuthenticated`/`isLoading`/`login`/`logout`/`hasRole`; inicializa el estado de forma síncrona desde `sessionStorage` (evita falso "no autenticado" antes del primer efecto); `useAuth.ts` lanza error fuera de `AuthProvider`. `AuthContext.test.tsx` (5 casos: sin sesión, login actualiza estado+persiste token, logout limpia estado+storage, restaura sesión al montar, error fuera del provider) pasa. Sincronización multi-pestaña (paso 4, opcional) no implementada — no requerida por el criterio de aceptación).

### FE-T013 — Cliente HTTP tipado y normalización de errores

- **Objetivo:** centralizar las llamadas a la API.
- **Depende de:** FE-T005, FE-T011.
- **Módulos:** `src/api/client.ts`, `src/api/errors.ts`, `src/api/types/api.ts`.
- **Pasos:**
  1. Implementar `request<T>()` con `fetch`, `AbortController` y timeout.
  2. Añadir `Authorization` si hay sesión.
  3. Parsear JSON/blob/vacío.
  4. Normalizar errores DRF a `ApiError`.
  5. Manejar 401 global (callback de logout).
  6. No loggear tokens/PII.
- **Criterios de aceptación:** 200/400/401/403/404/500 y red producen `ApiError` correcto.
- **Pruebas:** unitarias con MSW.
- **Evidencia:** pruebas.
- **Estimación:** M. **Prioridad:** Must. **Estado:** **Hecha** (evidencia 2026-11-04: `client.ts` implementa `request<T>()` con `AbortController`+timeout 30s, `Authorization` condicional, parseo JSON/204/no-JSON, callback global de 401 (`setUnauthorizedHandler`), sin loggear tokens; `errors.ts` normaliza `detail`/`non_field_errors`/campo→`fieldErrors` a `ApiError` con `code` derivado del status. `client.test.ts` (11 casos: 200, Authorization, 204, no-JSON, 400 con fieldErrors, 401+handler, 403, 404, 500, red, timeout) y `errors.test.ts` (6 casos) pasan. Nota técnica: el `fetch` nativo de Node (undici) y jsdom exponen `DOMException` de "realms" distintos — `instanceof DOMException` falla entre ellos; se usa `error.name === 'AbortError'`, estable entre realms).

### FE-T014 — Endpoint de login y handlers MSW base

- **Objetivo:** integrar `POST /auth/token/` y preparar mocks.
- **Depende de:** FE-T013.
- **Módulos:** `src/api/endpoints/auth.ts`, `src/mocks/handlers.ts`, `src/mocks/fixtures.ts`.
- **Pasos:**
  1. Tipos `LoginRequest`, `TokenPair`.
  2. `login()` con `request`.
  3. Handlers MSW para 200/401/500.
  4. Fixtures sin datos reales.
- **Criterios de aceptación:** login devuelve tokens y errores normalizados.
- **Pruebas:** unitarias.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** **Hecha** (evidencia 2026-11-04: `endpoints/auth.ts` tipa `LoginRequest{username,password}`/`TokenPair{access,refresh}` según el contrato real de SimpleJWT; `mocks/handlers.ts` responde 200 con fixture para credenciales de prueba conocidas y 401 en cualquier otro caso (500 se simula en pruebas puntuales vía `server.use()`); `mocks/fixtures.ts` genera un JWT ficticio con cédula/roles de prueba, sin datos reales. `auth.test.ts` (2 casos) pasa).

### FE-T015 — Guardas de ruta

- **Objetivo:** proteger rutas por autenticación y rol.
- **Depende de:** FE-T012, FE-T009.
- **Módulos:** `src/auth/guards.tsx`.
- **Pasos:**
  1. `RequireAuth` con `returnTo`.
  2. `RequireRole` con lista de roles.
  3. `RedirectIfAuthenticated`.
  4. Fallback a `/no-habilitado` o `/login`.
- **Criterios de aceptación:** sin sesión → login; rol incorrecto → no habilitado; no se renderiza contenido protegido.
- **Pruebas:** RTL de cada guarda.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** **Hecha** (evidencia 2026-11-04: `guards.tsx` implementa `RequireAuth` (con `returnTo` en el state de `Navigate`), `RequireRole` y `RedirectIfAuthenticated`, todas usables como ruta de layout (`children ?? <Outlet/>`). Cableadas en `router.tsx`: `RequireAuth` envuelve todo el árbol autenticado; `RequireRole` protege `/estudiante*` (ESTUDIANTE) y `/bandeja*` (roles operativos); `/expedientes/*` solo exige sesión (alcance server-side); `*` (404) queda fuera de cualquier guarda, accesible sin sesión. `guards.test.tsx` (7 casos) y los casos nuevos de `router.test.tsx` (redirección sin sesión, rol incorrecto→no-habilitado, parámetros con rol operativo) pasan).

### FE-T016 — Redirección por rol y cierre de sesión

- **Objetivo:** definir el destino post-login y el logout local.
- **Depende de:** FE-T012, FE-T015.
- **Módulos:** `src/auth/redirect.ts`, `src/components/layout/Header.tsx`.
- **Pasos:**
  1. Implementar el orden de roles de `specify.md` §6.
  2. Botón de logout con confirmación.
  3. Limpiar `sessionStorage` y `queryClient.clear()`.
  4. Redirigir a `/login`.
- **Criterios de aceptación:** cada rol va a su inicio; logout borra sesión y caché.
- **Pruebas:** unitarias de redirección; RTL de logout.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** **Hecha** (evidencia 2026-11-04: `redirect.ts` implementa `getHomeRouteForRoles` con el orden exacto de `specify.md` §6; `/` ahora usa `IndexRedirect` (antes redirigía siempre a `/login`, ya innecesario porque `RequireAuth` lo antecede). `AppLayout.tsx` conecta el logout real: `window.confirm` → `auth.logout()` → `queryClient.clear()` → `navigate('/login', {replace:true})`. También se conectó el manejador global de 401 de FE-T013 (`AuthExpiryBootstrap` en `router.tsx`): limpia sesión, caché y redirige a `/login`. `redirect.test.ts` (4 casos), 2 pruebas RTL de logout (confirmar/cancelar) en `AppLayout.test.tsx`, 2 pruebas de redirección por rol en `/` en `router.test.tsx`, y `router.auth-expiry.test.tsx` (401 real vía MSW → sesión limpia + `/login`) pasan).

### FE-T017 — Pruebas de autenticación

- **Objetivo:** cubrir login, guardas, expiración y logout.
- **Depende de:** FE-T014, FE-T015, FE-T016.
- **Módulos:** `src/auth/__tests__/`, `src/api/__tests__/`.
- **Pasos:**
  1. Casos 200/401/500/red.
  2. Guardas con y sin sesión.
  3. 401 global → logout.
  4. Accesibilidad del formulario de login.
- **Criterios de aceptación:** cobertura de auth ≥ 85%.
- **Pruebas:** `npm run test`.
- **Evidencia:** reporte de cobertura.
- **Estimación:** S. **Prioridad:** Must. **Estado:** **Hecha** (evidencia 2026-11-04: 81/81 pruebas pasan (18 archivos). Cobertura `src/auth/`: 96,87% stmts / 91,89% branch / 100% funcs / 96,77% lines. Cobertura `src/api/`: 96,82% stmts / 92,59% branch / 85,71% funcs / 100% lines. Ambas ≥85% en las cuatro métricas. Pasos 1-3 cubiertos (200/401/500/red en `client.test.ts`+`auth.test.ts`; guardas con/sin sesión en `guards.test.tsx`+`router.test.tsx`; 401 global→logout en `router.auth-expiry.test.tsx`). **Paso 4 (accesibilidad del formulario de login) no aplica todavía**: `LoginPage` sigue siendo el stub de FE-T009 (`<h1>Iniciar sesión (V-01)</h1>`); el formulario real es FE-T101 (vista V-01), fuera del alcance autorizado de este lote (solo FE-T011…FE-T017). Módulos de prueba: se mantuvo la convención de archivos `*.test.ts(x)` co-ubicados ya usada en F0/F1 en vez de crear carpetas `__tests__/` nuevas, por consistencia con el resto del proyecto).

---

## 5. Fase F2 — Componentes base

### FE-T019 — Campos de formulario accesibles

- **Objetivo:** crear `Button`, `Input`, `Select`, `Textarea`, `Checkbox`, `Radio`.
- **Depende de:** FE-T006.
- **Módulos:** `src/components/ui/`.
- **Pasos:**
  1. Props tipadas y variantes.
  2. Asociación `label`/`id`, `aria-describedby`, `aria-invalid`.
  3. Estados `disabled`, `loading`, `error`.
  4. Foco visible.
- **Criterios de aceptación:** axe sin errores críticos; navegación por teclado.
- **Pruebas:** RTL + axe.
- **Evidencia:** pruebas.
- **Estimación:** M. **Prioridad:** Must. **Estado:** **Hecha** (evidencia 2026-11-04: `Button`/`Input`/`Select`/`Textarea`/`Checkbox`/`Radio` en `src/components/ui/`; asociación `label`/`id` vía `useId`, `aria-describedby`/`aria-invalid` en campos de texto, foco visible por tokens. 31 pruebas RTL+axe entre los 6 componentes, 0 violaciones). Nota: `aria-invalid` se omitió en `Radio` por indicación de `jsx-a11y/role-supports-aria-props` (el rol `radio` no lo soporta según ARIA).

### FE-T020 — Badge, Card, Alert y Spinner

- **Objetivo:** componentes de presentación y feedback.
- **Depende de:** FE-T006.
- **Módulos:** `src/components/ui/{Badge,Card,Alert,Spinner}.tsx`.
- **Pasos:**
  1. Badge con variantes de estado.
  2. Card con título/acciones.
  3. Alert con roles `status`/`alert`.
  4. Spinner con texto accesible.
- **Criterios de aceptación:** variantes y accesibilidad correctas.
- **Pruebas:** RTL + axe.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** **Hecha** (evidencia 2026-11-04: `Badge` con variantes neutral/info/warning/success/danger sobre los tokens de FE-T006 (sin mapeo de estados de negocio hardcodeado, eso queda para la feature que lo use); `Alert` con `role="status"`/`role="alert"` según criticidad; `Spinner` con texto accesible configurable. 13 pruebas RTL+axe).

### FE-T021 — Estados vacío, error, no encontrado y prohibido

- **Objetivo:** homogeneizar estados de vista.
- **Depende de:** FE-T020.
- **Módulos:** `src/components/ui/{EmptyState,ErrorState,NotFoundState,ForbiddenState}.tsx`.
- **Pasos:**
  1. Props: título, descripción, acción, reintento.
  2. Mensajes sin detalles internos.
  3. `aria-live` cuando corresponda.
- **Criterios de aceptación:** cada estado es reutilizable y accesible.
- **Pruebas:** RTL + axe.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** **Hecha** (evidencia 2026-11-04: los 4 componentes sin detalles internos en sus mensajes (verificado con test anti-regex `/traceback|stack|SQL/`); `ErrorState` con `role="alert"`+`aria-live="assertive"` y botón "Reintentar" opcional (reutiliza `Button`); el resto con `role="status"`. 14 pruebas RTL+axe).

### FE-T022 — Tabla responsive

- **Objetivo:** mostrar datos tabulares en escritorio y tarjetas en móvil.
- **Depende de:** FE-T020.
- **Módulos:** `src/components/ui/Table.tsx`.
- **Pasos:**
  1. `<caption>`, `scope`, columnas configurables.
  2. Vista de tarjetas a < 768 px.
  3. Estado de carga y vacío.
  4. No romper con textos largos.
- **Criterios de aceptación:** sin scroll horizontal a 320 px; accesible.
- **Pruebas:** RTL + axe; capturas.
- **Evidencia:** pruebas y capturas.
- **Estimación:** M. **Prioridad:** Must. **Estado:** **Hecha** (evidencia 2026-11-04: `<table>` real con `<caption>` (sr-only) y `<th scope="col">` para escritorio + lista `<ul>` de tarjetas con los mismos datos (mismo `columns`/`rows`) para <768px, alternadas por CSS — técnica idéntica a la ya verificada en vivo con capturas reales en FE-T008 para Header/Sidebar, no repetida aquí porque el componente aún no tiene consumidor (tree-shaking lo excluye del build); contenedor de scroll horizontal con `role="region"`+`tabIndex=0` (patrón WCAG/ARIA APG, con `eslint-disable` puntual justificado); loading→`Spinner`, vacío→`EmptyState`. 6 pruebas RTL+axe, incluida alcanzabilidad por teclado del contenedor de scroll).

### FE-T023 — Paginación

- **Objetivo:** navegar resultados paginados.
- **Depende de:** FE-T020.
- **Módulos:** `src/components/ui/Pagination.tsx`.
- **Pasos:**
  1. Anterior/siguiente y número de página.
  2. Deshabilitar en extremos.
  3. Anuncio accesible del cambio.
- **Criterios de aceptación:** funciona con `count`, `next`, `previous`.
- **Pruebas:** RTL.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** **Hecha** (evidencia 2026-11-04: calcula páginas totales desde `count`/`pageSize` (forma de paginación DRF usada en `Paginated<T>`, FE-T013); deshabilita Anterior/Siguiente en los extremos; anuncia el cambio con `aria-live="polite"`. 7 pruebas RTL, incluida operabilidad por teclado Tab+Enter).

### FE-T024 — Modal accesible con focus trap

- **Objetivo:** diálogos para acciones y formularios.
- **Depende de:** FE-T019.
- **Módulos:** `src/components/ui/Modal.tsx`.
- **Pasos:**
  1. `role="dialog"`, `aria-modal`, título.
  2. Focus trap, `Esc`, retorno de foco.
  3. Scroll lock.
- **Criterios de aceptación:** teclado y lector de pantalla funcionan.
- **Pruebas:** RTL + axe.
- **Evidencia:** pruebas.
- **Estimación:** M. **Prioridad:** Must. **Estado:** **Hecha** (evidencia 2026-11-04: gestión real de foco — mueve el foco al primer elemento enfocable al abrir, atrapa Tab/Shift+Tab con envoltura real en los límites, Escape cierra, devuelve el foco al disparador al cerrar, bloquea `overflow` del body mientras está abierto. `role="dialog"`+`aria-modal`+`aria-labelledby`. Sin solución simulada: 9 pruebas RTL verifican `toHaveFocus()` real en cada paso, no solo que existan los atributos ARIA. Se retiró el cierre por clic en overlay del diseño inicial por no ser accesible según `jsx-a11y` y no ser un criterio explícito de la tarea).

### FE-T025 — Timeline de estados

- **Objetivo:** representar la evolución del expediente.
- **Depende de:** FE-T020.
- **Módulos:** `src/components/ui/Timeline.tsx`.
- **Pasos:**
  1. Lista ordenada de pasos con estado actual.
  2. No inventar pasos no soportados.
  3. Accesibilidad semántica.
- **Criterios de aceptación:** muestra solo estados reales; accesible.
- **Pruebas:** RTL + axe.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Should. **Estado:** **Hecha** (evidencia 2026-11-04: componente 100% dirigido por datos (`steps: TimelineStep[]`), no hardcodea ninguna secuencia de estados del dominio — la feature consumidora decide qué pasos reales mostrar; `<ol>` semántico con `aria-current="step"` en el paso actual. 5 pruebas RTL+axe, incluida una que confirma que no se inventan pasos no recibidos).

### FE-T026 — Carga de archivos PDF

- **Objetivo:** componente reutilizable de carga con validación.
- **Depende de:** FE-T019.
- **Módulos:** `src/components/ui/FileUpload.tsx`, `src/lib/files.ts`.
- **Pasos:**
  1. Drag & drop y selector.
  2. Validar `.pdf`, MIME, ≤ 10 MB y magic bytes `%PDF-`.
  3. Mostrar nombre/tamaño y errores.
  4. Accesible por teclado.
- **Criterios de aceptación:** archivo inválido no se envía; válido produce `File`.
- **Pruebas:** unitarias de validación; RTL.
- **Evidencia:** pruebas.
- **Estimación:** M. **Prioridad:** Must. **Estado:** **Hecha** (evidencia 2026-11-04: `src/lib/files.ts` valida extensión `.pdf`, MIME `application/pdf`, tamaño ≤10MB y magic bytes `%PDF-` (lee los primeros 5 bytes vía `file.slice().arrayBuffer()`), con un comentario explícito de que no sustituye los controles de seguridad del servidor. `FileUpload.tsx` rechaza antes de llamar a `onFileSelected`; selector con input oculto (`aria-hidden`+`tabIndex=-1`) disparado por un botón real y accesible por teclado; drag & drop funcional. Sin integración HTTP (correctamente fuera de alcance). 10 pruebas (6 unitarias de validación + 10 de componente incluyendo drag&drop real). Hallazgo documentado: `userEvent.upload()` filtra archivos por el atributo `accept` del input antes de disparar el evento, por lo que las pruebas de rechazo usan extensión/MIME válidos con magic bytes inválidos.).

### FE-T027 — Toasts y feedback de acciones

- **Objetivo:** notificar éxito/error de mutaciones.
- **Depende de:** FE-T020.
- **Módulos:** `src/components/feedback/ToastProvider.tsx`.
- **Pasos:**
  1. Cola de toasts, cierre automático/manual.
  2. `aria-live` y roles.
  3. No duplicar mensajes.
- **Criterios de aceptación:** toasts accesibles y no bloqueantes.
- **Pruebas:** RTL + axe.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Should. **Estado:** **Hecha** (evidencia 2026-11-04: se **amplió** el `ToastProvider` stub de FE-T007 — no se creó un proveedor nuevo; `providers.tsx` sigue siendo la única fuente). Cola de toasts con cierre automático (plazo configurable, 5s por defecto) y manual; `role="status"`/`role="alert"` según criticidad; deduplicación por mensaje+variante; overlay no bloqueante (`position:fixed`, sin overlay de pantalla completa). 7 pruebas RTL+axe. Nota técnica: se evitaron *fake timers* de Vitest por conflicto con `userEvent` (bloqueaba los tests); el cierre automático se probó con un `autoDismissMs` corto inyectado por props y tiempos reales.

### FE-T028 — Pruebas del UI kit

- **Objetivo:** cubrir componentes base y accesibilidad.
- **Depende de:** FE-T019…FE-T027.
- **Módulos:** `src/components/ui/__tests__/`.
- **Pasos:**
  1. Casos de variantes/estados.
  2. axe por componente.
  3. Teclado en modal, tabla, paginación y upload.
- **Criterios de aceptación:** cobertura de UI kit ≥ 80%; axe sin críticos.
- **Pruebas:** `npm run test`.
- **Evidencia:** reporte.
- **Estimación:** M. **Prioridad:** Must. **Estado:** **Hecha** (evidencia 2026-11-04: 39 archivos, 170/170 pruebas. Cobertura `src/components/ui/`: 96,12% stmts / 90,18% branch / 97,36% funcs / 96,12% lines — ninguna métrica reducida artificialmente ni componente excluido (no confundir con la cobertura global del proyecto, que es otro número: 95,34%/89,45%/92,14%/96,6%, mayor porque incluye auth/api/app ya muy cubiertos desde F1). 0 violaciones de axe en los 19 componentes. Teclado verificado explícitamente en Modal (focus trap real), Table (contenedor de scroll `tabIndex=0`), Pagination (Tab+Enter) y FileUpload (Tab al botón + drag&drop). Módulos de prueba co-ubicados (`*.test.tsx`), no en `__tests__/`, por consistencia con F0/F1, igual que se documentó en FE-T017).

---

## 5.bis Fase F2.5 — Estados de error e higiene (nueva, 2026-11-04)

> Derivada de la auditoría de los prototipos A/B y de los estados aprobados en la reorganización documental (DEC-11…DEC-13). Organiza los estados en **globales** (401/403/404/500/503), **de formularios** (400/422; 409/412/428 condicionados a BE-11) y **operativos reutilizables** (loading/empty/forbidden/read-only). Prohíbe crear páginas independientes innecesarias: 401 no es página (redirige a `/login`), 403 usa `ForbiddenState`+V-09 dentro del layout, 500/503 usan `ErrorState` (página solo si el ErrorBoundary global necesita shell). Referencia visual: `especificaciones/08_UI_ERROR_STATES_SPEC.md` y prototipo B. **No se copia HTML/CSS/JS de los prototipos.**

### FE-T1210 — Higiene de la plantilla Vite (residuos)

- **Objetivo:** eliminar residuos de la plantilla que colisionan con el design system.
- **Fase:** F2.5 (cerrar con F0-pending del primer lote).
- **Vista/módulo:** transversal (base de la app).
- **Requisitos:** RFF-011 (contraste/base), RFF-015.
- **Referencia:** `plan.md` §2.ter; `clarify.md` D-FE-02, D-FE-04.
- **Depende de:** ninguna (puede ser la primera del lote).
- **Alcance del resultado:** `frontend/` sin estilos ni metadatos ajenos al design system.
- **Descripción:** (1) eliminar `src/index.css` y su import en `main.tsx`; (2) corregir `index.html`: `lang="es"`, `<title>SGT-SIAAF</title>` (revisar favicon `public/favicon.svg`); (3) verificar que `main.tsx` carga solo tokens/global/utilities.
- **Archivos esperados:** `src/index.css` (se elimina), `src/main.tsx`, `index.html`.
- **Dependencias:** ninguna.
- **Criterios de aceptación:** build y pruebas completas; no hay selectores violeta ni `#root{center…}` de la plantilla en el CSS compilado; `lang="es"` y título institucional correctos.
- **Pruebas:** `npm run build` + suite de pruebas + inspección del CSS.
- **Evidencias:** diff del build CSS y del index.html.
- **Estimación:** S. **Prioridad:** Must. **Estado:** **Hecha** (evidencia 2026-11-04, ejecutada dentro del primer lote de cierre de F0, autorización acotada 2026-11-04: `src/index.css` eliminado y su import retirado de `main.tsx`; `index.html` con `lang="es"` y `<title>SGT-SIAAF</title>`; `favicon.svg` revisado, sin cambios necesarios; `main.tsx` carga solo `tokens.css`/`global.css`/`utilities.css`. CSS compilado: 7.02 KB → 5.23 KB, sin `#aa3bff` ni `#root{...center...}` de la plantilla (`grep` sobre `dist/assets/*.css` sin coincidencias); build y 24/24 pruebas pasan).

### FE-T1211 — Página 404 estilizada con la referencia del kit de errores

- **Objetivo:** reemplazar el stub mínimo de `NotFoundPage` por una página 404 accesible alineada con `paginas/404.html` del prototipo B (traducida a React/CSS Modules, sin copiar código).
- **Fase:** F2.5.
- **Vista/módulo:** transversal (`*`).
- **Requisitos:** RFF-004, RFF-017, RNFF-001.
- **Referencia:** prototipo B `prototipos/vistas-errores-unl/paginas/404.html` (ERR-03 en la especificación 08); `specify.md` §9.3.
- **Depende de:** FE-T009, FE-T006.
- **Descripción:** título/mensaje sin filtrar detalles internos (incl. nota de privacidad: un recurso ajeno puede responder 404); CTA "Volver al inicio por rol" y "Ir a `/login`" según sesión; mensaje accesible (role/aria y jerarquía de encabezados); estructura `src/app/NotFoundPage.tsx` (+ CSS module).
- **Archivos esperados:** `src/app/NotFoundPage.tsx` (+ CSS module).
- **Dependencias:** FE-T009.
- **Criterios de aceptación:** 404 por ruta desconocida muestra la página con CTAs funcionales por rol/sesión; axe sin violaciones; mensajes en español sin tecnicismos.
- **Pruebas:** pruebas del router actualizadas + axe.
- **Evidencias:** pruebas y captura.
- **Estimación:** S. **Prioridad:** Must. **Estado:** **Hecha** (evidencia 2026-11-05: `NotFoundPage.tsx` reutiliza `NotFoundState`+`Button`; CTA "Ir a iniciar sesión"/"Ir a mi inicio" según `isAuthenticated`, más "Volver atrás" (historial real) en ambos casos; nota de privacidad integrada en la descripción sin confirmar existencia de recursos ajenos; jerarquía `h1`("Error 404")→`h2`("Página no encontrada"); mascota `mascota-404.png` decorativa (`alt=""`, FE-T1214). 13 pruebas (incluye navegación real por clic, teclado, jerarquía de encabezados, axe) + `router.test.tsx` actualizado. Verificado en navegador real sin overflow en 320/768/1440 y en ambos contextos de sesión (inyectando JWT válido en `sessionStorage`); capturas de pantalla no disponibles por limitación intermitente del panel de navegador en esta sesión — evidencia por inspección de DOM/`scrollWidth` en su lugar).

### FE-T1212 — Estados de error globales 401 / 403 / 500 / 503

- **Objetivo:** homogeneizar los errores globales según la jerarquía aprobada: 401 → limpieza de sesión + `/login` con aviso; 403 → `ForbiddenState` dentro del layout y V-09 por guardas; 500/503 → `ErrorState` con reintento (páginas dentro del ErrorBoundary solo si el shell lo requiere).
- **Fase:** F2.5.
- **Vista/módulo:** transversal.
- **Requisitos:** RFF-013, RFF-014, RFF-017, RFF-004.
- **Referencia:** prototipo B `paginas/401.html`, `403.html`, `500.html`, `503.html` (ERR-01/02/07/08 en la especificación 08).
- **Depende de:** FE-T013, FE-T015, FE-T021.
- **Descripción:** los mensajes del kit se adaptan (tono institucional dado por la referencia del kit); los 500/503 con "Reintentar" hacen reintento real de query o recarga controlada, no simulado; sin tecnicismos ni rutas internas.
- **Archivos esperados:** extensiones en `src/app/errors/`, `src/components/ui/NotFoundState.tsx`/`ForbiddenState.tsx`, `src/lib/queryClient.ts` (o `api/client.ts`).
- **Dependencias:** FE-T013, FE-T015, FE-T021.
- **Criterios de aceptación:** un 401 limpia la sesión (CA-G-03); un 403 muestra explicación sin filtrar existencia de recursos (CA-G-04); 5xx/red muestran reintento manual (CA-G en RFF-013); todo accesible (axe).
- **Pruebas:** MSW para 401/403/500/503/red; RTL + axe.
- **Evidencias:** pruebas.
- **Estimación:** M. **Prioridad:** Must. **Estado:** **Hecha** (evidencia 2026-11-05: **(A) 401** — `AuthExpiryBootstrap` (`router.tsx`) limpia sesión+caché, muestra toast "Su sesión ha expirado…" (`ToastProvider`, sin tocar `LoginPage`/F1) y redirige a `/login`; **corregida la observación P2-3 de la auditoría F1**: `client.ts` añade `skipAuthHandler` y `endpoints/auth.ts` lo usa en `login()`, así un 401 por credenciales inválidas ya no dispara el cierre de sesión global. **(B) 403** — `NoHabilitadoPage` (destino de `RequireRole`, sin alterar guards.tsx) ahora reutiliza `ForbiddenState` (se le añadió un `action?` opcional, mismo patrón que `EmptyState`/`NotFoundState`) con "Volver al inicio"; las reglas de autorización de `guards.tsx` no cambiaron. **(C/D/E/F)** — nuevo `src/lib/apiErrorPresentation.ts` (`presentApiError(ApiRequestError)`) consolida qué componente (`NotFoundState`/`ForbiddenState`/`ErrorState`) y mensaje institucional usar según status real (404/403/401/500/502-504/red/timeout/genérico), sin exponer el cuerpo crudo del backend; reintento real demostrado con un fixture `useQuery`+MSW (primer intento falla, clic en "Reintentar" dispara `refetch()` real, segundo intento exitoso actualiza la UI; un reintento que vuelve a fallar no simula éxito). 41 pruebas nuevas en este bloque (`client.test.ts`, `auth.test.ts`, `router.auth-expiry.test.tsx`, `apiErrorPresentation.test.ts`, `apiErrorPresentation.integration.test.tsx`, `NoHabilitadoPage.test.tsx`, `ForbiddenState.test.tsx`). Nota de alcance: no se creó ninguna página independiente para 500/503 (prohibido explícitamente); `ErrorState` se mantiene genérico/reutilizable para cuando una vista real (F3+) lo consuma con un `refetch` real).

### FE-T1213 — InlineAlerts para escenarios propuestos 409/412/428

- **Objetivo:** tener especificado (y solo cuando el backend lo declare) el tratamiento inline en formularios de conflicto/versión.
- **Fase:** F2.5 — **Bloqueada**.
- **Vista/módulo:** formularios V-03/V-04/V-05/V-06.
- **Requisitos:** RFF-005; escenario propuesto, no confirmado.
- **Referencia:** prototipo B `paginas/409.html`, `412.html`, `428.html` (ERR-04/05/06 en la especificación 08); `clarify.md` DEC-13/B-11; `plan.md` §11.1.
- **Depende de:** **BE-11** (NO AUTORIZADA) y FE-T019.
- **Descripción (diseño a implementar cuando se autorice):** componente `InlineAlert` sin expulsar al usuario del formulario; 409 → "Ya existe una petición activa de este tipo…" con acción de revisión; 412 → "Alguien actualizó…" con recargar/cancelar conservando texto; 428 → "Se requiere versión vigente" recargar datos. Solo se activan si `error.status` y `error.code` coinciden; caso contrario, degradan a 400 genérico con mensaje del backend.
- **Archivos esperados:** `src/components/ui/InlineAlert.tsx` + pruebas.
- **Dependencias:** BE-11, FE-T019, FE-T021.
- **Criterios de aceptación (futuros):** no se pierde texto al actualizar; `role="alert"` + foco; sin duplicidad con toasts.
- **Pruebas:** MSW con los códigos una vez el backend los declare.
- **Evidencias:** pruebas.
- **Estimación:** M. **Prioridad:** Should. **Estado:** **Bloqueada (BE-11)**. No implementar hasta autorización expresa del backend; la especificación 08 la documenta como propuesta.

### FE-T1214 — Assets visuales del kit de errores (mascotas)

- **Objetivo:** decidir e integrar (si se aprueba) los recursos gráficos del prototipo B (mascotas PNG y favicon) en `frontend/public/`.
- **Fase:** F2.5 — autorizada explícitamente por el usuario el 2026-11-05 (antes "Propuesta, pendiente de decisión").
- **Vista/módulo:** transversal.
- **Requisitos:** ninguno fundamenta el uso de mascotas (RFF-004 solo exige estados claros); los assets son opcionales.
- **Referencia:** prototipo B `assets/img/mascota-*.png`.
- **Depende de:** decisión del usuario (concedida); FE-T1211/FE-T1212.
- **Descripción:** **no se copió HTML/CSS/JS**; solo los 5 PNG, copiados byte a byte (verificado con `sha256sum`) a `frontend/public/assets/mascotas/`, conservando nombres originales. `README.md` del prototipo B actualizado (no reemplazado) para reflejar la autorización, conservando la advertencia original de que son ilustraciones generadas sin sustituir marca oficial.
- **Archivos esperados:** `frontend/public/assets/mascotas/mascota-{401,403,404,500,503}.png`; `frontend/docs/assets-mascotas.md` (inventario).
- **Dependencias:** FE-T1211/1212.
- **Criterios de aceptación:** alt accesible (decorativas `alt=""`), contraste y legibilidad sin afectar, peso sin compresión destructiva, sin cambiar tintas corporativas no confirmadas.
- **Pruebas:** revisión visual + axe.
- **Evidencias:** inventario (`frontend/docs/assets-mascotas.md`), pruebas, verificación en navegador real.
- **Estimación:** S. **Prioridad:** Could. **Estado:** **Hecha, con alcance documentado** (evidencia 2026-11-05: `mascota-404.png` integrada en `NotFoundPage`; `mascota-403.png` integrada en `NoHabilitadoPage`; ambas `alt=""`, verificadas con pruebas dedicadas y en navegador real (carga correcta, `naturalWidth` = dimensión original, sin overflow a 320px). `mascota-401.png` copiada pero **no integrada visualmente** (401 no es página, por diseño — DEC-13). `mascota-500.png`/`mascota-503.png` copiadas y documentadas pero **no integradas visualmente todavía**: `ErrorState` es un componente genérico reutilizado en contextos pequeños y FE-T1212 prohíbe crear páginas independientes para 500/503; forzar la mascota en el componente base la mostraría también en usos inline no apropiados. Su integración queda para cuando una vista real presente un 500/503 a nivel de página (F3+). No se usó el logo "unl" recreado; no se afirmó licencia institucional formal no documentada.

---

## 6. Vista V-01 — Login

### FE-T101 — Formulario de login

- **Objetivo:** construir la UI del formulario con validación.
- **Depende de:** FE-T019, FE-T015.
- **Módulos:** `src/features/auth/LoginPage.tsx`, `LoginForm.tsx`.
- **Pasos:**
  1. Campos `username` y `password`.
  2. Mostrar/ocultar contraseña.
  3. Validación local (obligatorios, trim).
  4. Enter envía; bloqueo de doble envío.
- **Criterios de aceptación:** no se envía inválido; foco en el primer error.
- **Pruebas:** RTL + axe.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** **Hecha** (2026-11-05: `LoginForm.tsx` creado — `username`/`password` con `Input` del UI Kit (sin duplicar), alternancia mostrar/ocultar con `aria-label` dinámico, validación local de obligatorios con `trim()` solo en `username` (la contraseña se conserva exacta), envío por Enter (submit nativo del `<form>`), doble guard contra doble envío (botón deshabilitado vía `Button loading` + guard explícito en el handler ante un evento submit directo), foco en el primer campo inválido vía `id` + `document.getElementById` (no se pudo usar `ref` reenviado a `Input` porque el componente no está envuelto en `forwardRef`/no declara `ref` en sus props — ver `LoginForm.test.tsx`, 10/10 pruebas incl. axe). Verificado manualmente en navegador: validación local, alternancia de contraseña y colapso responsive a 375px sin overflow horizontal).

### FE-T102 — Integración de login y persistencia

- **Objetivo:** consumir el endpoint y guardar la sesión.
- **Depende de:** FE-T014, FE-T101.
- **Módulos:** `src/features/auth/LoginPage.tsx`, `src/auth/*`.
- **Pasos:**
  1. Llamar `login()`.
  2. Validar tokens y claims.
  3. Guardar `access` y actualizar `AuthContext`.
  4. Redirigir según rol.
- **Criterios de aceptación:** 200 → sesión y redirección; 401 → mensaje.
- **Pruebas:** integración MSW.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** **Hecha** (2026-11-05: `LoginPage.tsx` consume `login()` de `src/api/endpoints/auth.ts` (sin modificarlo), valida la respuesta decodificando el `access` con `decodeAccessToken` existente; si la decodificación falla (token malformado) no persiste nada y muestra error genérico (rama cubierta en `LoginPage.test.tsx`). Persiste la sesión vía `AuthContext.login()` existente (sin alterar su contrato) y redirige con `getHomeRouteForRoles` al home del rol real obtenido del JWT, u honra `state.returnTo` si la guarda `RequireAuth` redirigió desde una ruta protegida (mecanismo ya existente en `guards.tsx`, antes sin consumidor). `RedirectIfAuthenticated` quedó conectada a `/login` vía un nuevo wrapper `LoginRoute` en `router.tsx`, resolviendo el pendiente de la auditoría F1 (CA-V01-04 verificado). Solo `access` se persiste; `refresh` se descarta (sin cambios, ya era así). Sin refresh automático ni logout de servidor inventados.).

### FE-T103 — Errores, carga y accesibilidad del login

- **Objetivo:** completar estados y accesibilidad.
- **Depende de:** FE-T102.
- **Módulos:** `src/features/auth/LoginPage.tsx`.
- **Pasos:**
  1. Estado `submitting` con spinner.
  2. Mensajes para 400/401/403/5xx/red.
  3. `aria-live` y foco.
  4. Banner de demo si aplica.
- **Criterios de aceptación:** todos los estados son visibles y accesibles.
- **Pruebas:** RTL + axe.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** **Hecha** (2026-11-05: estado `submitting` con `Button loading` existente (spinner + `aria-busy` + disabled, sin duplicar); mensajes diferenciados por estado vía `describeLoginError()` — 401 "Usuario o contraseña incorrectos." (genérico, CA-V01-02, nunca revela cuál campo falló), 403 "No tiene permisos para iniciar sesión con esta cuenta.", 400/422 usa el mensaje normalizado del backend (`normalizeApiError`, ya existente), 5xx/red/timeout reutiliza `presentApiError()` de F2.5 (sin duplicar lógica); mensajes mostrados en `Alert` (variant danger) del UI Kit, que ya expone `role="alert"`/`aria-live="assertive"` — ninguna lógica de aria-live nueva necesaria. Gestión de foco: tras un error del servidor se limpia y reenfoca la contraseña (no mediante `useEffect` con `setState` —bloqueado por la regla de lint `react-hooks/set-state-in-effect`— sino mediante `onSubmit` devolviendo `Promise<boolean>` y actuando en el propio handler del evento). Banner de demostración: se reutiliza el `DemoBanner` existente (`show={env.demoMode}`), sin banner si la config no lo activa. Un 401 de login confirmado por prueba que no dispara el manejador global (`skipAuthHandler`, F2.5) ni duplica manejadores.).

### FE-T104 — Pruebas de V-01

- **Objetivo:** cubrir login de extremo a extremo en integración.
- **Depende de:** FE-T103.
- **Módulos:** `src/features/auth/__tests__/`.
- **Pasos:**
  1. 200, 401, 500, red.
  2. Redirección por cada rol.
  3. Sesión persistida y logout.
- **Criterios de aceptación:** cobertura de V-01 ≥ 85%.
- **Pruebas:** `npm run test`.
- **Evidencia:** reporte.
- **Estimación:** S. **Prioridad:** Must. **Estado:** **Hecha** (2026-11-05: se mantuvo la convención de archivos `*.test.ts(x)` co-ubicados (no `__tests__/`) por consistencia con F0/F1/F2, mismo criterio ya aplicado y documentado en FE-T017. `LoginForm.test.tsx` (10 pruebas, unitario con `onSubmit` simulado) + `LoginPage.test.tsx` (12 pruebas, integración real: `AuthProvider`+`ToastProvider`+`AppRouter` sobre MSW, sin mocks de `AuthContext`) = 22 pruebas nuevas. Cubren: login exitoso 200 (ESTUDIANTE→`/estudiante` y rol operativo→`/bandeja`), 401/400/403/500(+reintento real)/red, indicador de carga (`aria-busy`), doble envío bloqueado (botón deshabilitado + guard del handler), validación local, mostrar/ocultar contraseña, envío por Enter, persistencia del `access` token, logout local (botón `Cerrar sesión` del `Header` existente), redirección de usuario autenticado fuera de `/login` (CA-V01-04), confirmación de que un 401 de login no dispara el aviso/cierre global, axe. Cobertura real (`npm run test -- --coverage`): `features/auth` combinado 98,48% stmts / 93,02% branch / 100% funcs / 98,46% lines — ≥85% en las cuatro métricas (único hueco: línea 18 de `LoginPage.tsx`, rama defensiva no-`ApiRequestError` no alcanzable sin un mock artificial, documentada y no forzada). Suite completa: 226/226 pruebas, 0 regresiones en F0–F2.5. `npm run lint`/`npm run typecheck`/`npm run build` sin errores. Verificación manual en navegador (`npm run dev`): formulario real renderizado, validación local, alternancia de contraseña y responsive 375px sin overflow horizontal confirmados; el flujo de red contra un backend real no pudo probarse manualmente porque no hay backend Django disponible en este entorno (fuera de alcance de F1-xx; "Frontend only") — se simuló un error de red real (sin backend en `localhost:8000`) y el `Alert` mostró el mensaje genérico esperado, confirmando el camino de error de red end-to-end.).

---

## 7. Vista V-02 — Dashboard del estudiante

### FE-T201 — Estructura del dashboard

- **Objetivo:** crear layout, saludo y tarjetas.
- **Depende de:** FE-T008, FE-T020.
- **Módulos:** `src/features/dashboard/StudentDashboardPage.tsx`.
- **Pasos:**
  1. Saludo con `cedula`.
  2. Tarjetas de borradores, observadas y notificaciones.
  3. CTA "Crear solicitud".
  4. Aviso de limitaciones.
- **Criterios de aceptación:** responsive y accesible.
- **Pruebas:** RTL + axe.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** **Hecha** (2026-11-05: `StudentDashboardPage.tsx` reescrita — saludo con `cedula` del token (separado del `<h1>` por jerarquía de encabezados), 3 tarjetas de resumen (borrador/observadas/no leídas) reutilizando `Card` del UI Kit, CTA "Crear solicitud" dentro del estado vacío de `ExpedientesCard` (CA-V02-02), `Alert` informativo de limitación de perfil/historial (RFF-205). Grid de tarjetas colapsa a 1 columna en móvil (375px, sin overflow horizontal, verificado en navegador). Se mantuvo el texto del `<h1>` ("Dashboard del estudiante (V-02)") para no romper las aserciones de regresión existentes en `router.test.tsx`/`App.test.tsx`/`router.auth-expiry.test.tsx`/`LoginPage.test.tsx`, que usan ese heading como ancla).

### FE-T202 — Query de bandeja del estudiante

- **Objetivo:** listar expedientes `BORRADOR`/`OBSERVADA`.
- **Depende de:** FE-T201, FE-T013.
- **Módulos:** `src/api/endpoints/expedientes.ts`, `src/features/dashboard/`.
- **Pasos:**
  1. Tipos de `BandejaExpediente` y paginación.
  2. Query con `page`/`page_size`.
  3. Render de lista/tabla.
  4. Cálculo de contadores sobre la página.
- **Criterios de aceptación:** muestra datos reales; estado vacío correcto.
- **Pruebas:** integración MSW.
- **Evidencia:** pruebas.
- **Estimación:** M. **Prioridad:** Must. **Estado:** **Hecha** (2026-11-05: contrato real verificado contra `backend/src/apps/expedientes/adapters/views.py` — `GET /api/v1/expedientes/bandeja/` (`BandejaExpedienteViewSet`) existe, tiene `rbac_resource="expedientes"` con `RBAC_MATRIX["expedientes"]["GET"]["ESTUDIANTE"]=SCOPE_OWN` y `MAPA_INTERVENCION_POR_ROL["ESTUDIANTE"]=("BORRADOR","OBSERVADA")`: el estudiante SÍ puede listar sus propios expedientes en esos dos estados — **no bloqueada**, a pesar de que BE-05 (perfil + historial COMPLETO en todos los estados) sigue NO AUTORIZADA/ausente; son limitaciones distintas (BE-05 es más amplia que lo que esta tarea necesita). Paginación real confirmada en `BandejaPagination` (`page`/`page_size`, máx. 50) y en `openapi.yaml` (`PaginatedBandejaExpedienteList`: `count`/`next`/`previous`/`results`). `src/api/endpoints/expedientes.ts` (tipos `BandejaExpediente`/`ListBandejaEstudianteParams`, función `listBandejaEstudiante`) + `src/features/dashboard/queries.ts` (`useBandejaEstudiante`, `retry:false` para evitar depender del reintento automático de `queryClient.ts`, ver hallazgo P2 en el informe) + `ExpedientesCard.tsx` (tabla vía `Table` del UI Kit, contadores sobre la página actual, nota "hay más páginas" cuando `next!==null`, `Pagination` del UI Kit cuando `count>pageSize`). Pruebas: `expedientes.test.ts` (4, construcción de query string) + casos de integración en `StudentDashboardPage.test.tsx`.

### FE-T203 — Notificaciones internas

- **Objetivo:** listar y marcar notificaciones leídas.
- **Depende de:** FE-T202.
- **Módulos:** `src/api/endpoints/notificaciones.ts`, `src/features/dashboard/`.
- **Pasos:**
  1. Query paginada.
  2. Contador de no leídas.
  3. Mutación `marcar-leida` e invalidación.
  4. Estados vacío/error.
- **Criterios de aceptación:** el contador baja al marcar leída.
- **Pruebas:** integración MSW.
- **Evidencia:** pruebas.
- **Estimación:** M. **Prioridad:** Should. **Estado:** **Hecha, con una desviación de contrato documentada** (2026-11-05: `GET /api/v1/notificaciones/` y `PATCH /api/v1/notificaciones/{id}/marcar-leida/` (`NotificacionViewSet`) existen y tienen `RBAC_MATRIX["notificaciones"]["GET"/"PATCH"]["ESTUDIANTE"]=SCOPE_OWN` — **no bloqueada**. **Hallazgo de discrepancia código-vs-documentación** (verificado en `backend/src/apps/notificaciones/adapters/views.py` línea 30 y `backend/openapi.yaml`): la vista fija explícitamente `pagination_class = None` ("Deshabilitar paginación para pruebas simples") y devuelve `{"results": [...]}` — **sin `count`/`next`/`previous` y sin paginar** — a pesar de que `specify.md` §7 (V-02) la describe como "paginado; estructura estándar DRF" y `openapi.yaml` la tipa como `type: array` plano (tampoco coincide con el código real). Se implementó contra el **código real** (jerarquía de `clarify.md` §2): `listNotificaciones()` sin `page`/`page_size`, tipo `ListNotificacionesResponse={results: NotificacionInterna[]}`, con un comentario en el código que documenta la discrepancia. El contador de no leídas se calcula sobre el conjunto completo devuelto (no hay "página" que calcular). Mutación `marcarNotificacionLeida` invalida la query (`useMarcarNotificacionLeida`, TanStack Query) y el contador baja tras el `PATCH` (verificado en `StudentDashboardPage.test.tsx`, caso CA-V02-03, con mocks MSW con estado mutable que simulan el ciclo GET→PATCH→GET real).

### FE-T204 — Persistencia local del último expediente

- **Objetivo:** mitigar la falta de historial del estudiante.
- **Depende de:** FE-T202.
- **Módulos:** `src/lib/storage.ts`, `src/features/dashboard/`.
- **Pasos:**
  1. Guardar IDs de expedientes creados/visitados en `sessionStorage`.
  2. Mostrar accesos directos.
  3. Limpiar al cerrar sesión.
  4. Aviso de que no sustituye un endpoint de historial (BE-05).
- **Criterios de aceptación:** el estudiante puede volver a un expediente `ENVIADA` si conserva el ID.
- **Pruebas:** unitarias de storage.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Should. **Estado:** **Hecha, con alcance acotado documentado** (2026-11-05: `src/lib/storage.ts` — `recordVisitedExpediente`/`getRecentExpedientes`/`clearRecentExpedientes` sobre `sessionStorage` (clave `sgt.recent_expedientes`), dedupe por `id` (revisitar mueve al frente), tope de 5 entradas, descarta JSON inválido o entradas con forma incorrecta sin lanzar. `AuthContext.logout()` extendido para llamar `clearRecentExpedientes()` además de `clearAccessToken()` (aislamiento de sesión). Integrado en `ExpedientesCard`/`StudentDashboardPage` al hacer clic en "Ver expediente" (enlace real a la ruta `/expedientes/:id`, ya wireada sin `RequireRole` adicional). `AccesosRapidos.tsx` muestra el disclaimer explícito de que no sustituye un historial oficial (BE-05) y marca con una insignia los accesos cuyo `id` no está en la página actual de la bandeja ("No aparece en su bandeja actual; puede haber cambiado de estado"), cubriendo CA-V02-05. **Alcance acotado:** solo se registran expedientes **visitados** (clic real desde la bandeja); el registro al **crear** un expediente queda pendiente de V-03 (FE-T301+, `NuevaSolicitudPage` sigue siendo el stub de FE-T009 y no está autorizada en este lote) — no es un bloqueo de backend, es una dependencia de una tarea de frontend no autorizada todavía. Pruebas: `storage.test.ts` (9) + 2 casos en `AuthContext.test.tsx` + casos de integración en `StudentDashboardPage.test.tsx`.

### FE-T205 — Estados y errores del dashboard

- **Objetivo:** cubrir carga, vacío, error y parcial.
- **Depende de:** FE-T202, FE-T203.
- **Módulos:** `src/features/dashboard/`.
- **Pasos:**
  1. Loading por tarjeta.
  2. Error con reintento.
  3. Parcial si una query falla.
  4. No mostrar datos ficticios.
- **Criterios de aceptación:** cada estado es visible y accesible.
- **Pruebas:** RTL + MSW.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** **Hecha** (2026-11-05: `ExpedientesCard`/`NotificacionesCard` manejan `loading` (vía `Table`/`Spinner` existentes), `empty` (`EmptyState`), `error` (`presentApiError()` + `ErrorState` con `onRetry={() => query.refetch()}` real, o `ForbiddenState` si `presentApiError(...).kind==='forbidden'`), sin duplicar `apiErrorPresentation.ts` ni los manejadores globales de F2.5/V-01. Estado parcial implementado en `StudentDashboardPage.tsx`: cuando exactamente una de las dos queries falla y la otra tiene éxito, se muestra un aviso explícito ("Algunos datos no se pudieron cargar. El resto del panel sigue disponible.") y la sección que sí cargó permanece funcional (verificado en `StudentDashboardPage.test.tsx`). Ningún estado muestra datos ficticios: los contadores de resumen muestran "—" en vez de "0" mientras la query respectiva no haya tenido éxito, para no insinuar "cero expedientes" cuando en realidad es "desconocido/error".).

### FE-T206 — Pruebas de V-02

- **Objetivo:** cubrir dashboard.
- **Depende de:** FE-T205.
- **Módulos:** `src/features/dashboard/__tests__/`.
- **Pasos:**
  1. Con y sin expedientes.
  2. Notificaciones no leídas.
  3. Error y reintento.
  4. Aviso de limitación.
- **Criterios de aceptación:** cobertura ≥ 80%.
- **Pruebas:** `npm run test`.
- **Evidencia:** reporte.
- **Estimación:** S. **Prioridad:** Must. **Estado:** **Hecha** (2026-11-05: se mantuvo la convención de archivos `*.test.ts(x)` co-ubicados en vez de `__tests__/`, por consistencia con F0-V01 (mismo criterio documentado en FE-T017/FE-T104). 29 pruebas nuevas: `storage.test.ts` (9), `expedientes.test.ts` (4), `ExpedientesCard.test.tsx` (1), `NotificacionesCard.test.tsx` (4), `StudentDashboardPage.test.tsx` (10, integración real con MSW: con/sin expedientes, contadores, notificaciones no leídas, marcado como leída con invalidación real, error 500 + reintento real, estado parcial, acceso rápido registrado al visitar, aviso CA-V02-05, aviso de limitación RFF-205, axe), más 1 prueba añadida a `AuthContext.test.tsx` (limpieza de accesos rápidos al cerrar sesión). Cobertura real (`npm run test -- --coverage`): `features/dashboard` 96,34% stmts / 89,06% branch / 94,28% funcs / 97,46% lines — ≥80% en las cuatro métricas, sin reducir umbrales globales ni excluir archivos. Suite completa: 255/255 pruebas, sin regresiones en F0–V01 (se corrigió `LoginPage.test.tsx`, que no envolvía `AppRouter` en `QueryClientProvider`, porque antes `StudentDashboardPage` era un stub sin queries; también se añadió un `<h2>Resumen</h2>` en el dashboard para no romper el orden de encabezados WCAG al introducir las tarjetas `<h3>` de `Card`). `npm run lint`/`typecheck`/`build` sin errores. Verificación manual en navegador (`npm run dev`, sesión inyectada vía `sessionStorage`): estructura accesible completa (landmarks/headings/alerts correctos), botón "Reintentar" dispara una petición real a `GET http://localhost:8000/api/v1/expedientes/bandeja/?page=1&page_size=10` (falla con `ERR_CONNECTION_REFUSED` por ausencia de backend en este entorno, confirmando que el reintento es real y no simulado), y colapso responsive a 375px sin overflow horizontal.).

---

## 8. Vista V-03 — Crear solicitud

### FE-T301 — Formulario de nueva solicitud

- **Objetivo:** capturar `carrera_id` con validación.
- **Depende de:** FE-T019, FE-T015.
- **Módulos:** `src/features/solicitud/NuevaSolicitudPage.tsx`, `NuevaSolicitudForm.tsx`.
- **Pasos:**
  1. Campo `carrera_id` (UUID) con ayuda contextual.
  2. Validación de UUID.
  3. Aviso de que no hay catálogo (BE-10).
  4. Confirmación antes de crear.
- **Criterios de aceptación:** UUID inválido bloquea el envío; no se inventan carreras.
- **Notas DEC-14 (corregidas, MOMENTO 2 — 2026-11-04):** `carrera_id` (carrera) y `opcion_titulacion` (modalidad) son conceptos distintos. **Esta tarea se implementa solo con `carrera_id`** (obligatorio, UUID, sin catálogo —BE-10). El selector de modalidades del prototipo A **no está descartado definitivamente, pero está sin implementar**: queda condicionado a (1) human decision, (2) validación del RRA-UNL (arts. 39/40/212/216/233 señalados; fuente primaria no verificada) y (3) contrato backend aprobado (BE-06: solo dependencia solicitada, no autorización de modificar el backend). "Proyecto de Emprendimiento" **no confirmado** — no se muestra como opción. Detalle en `specify.md` §9.2 (puntos a–f).
- **Pruebas:** RTL + unitarias de validación.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** **Hecha** (2026-11-05: `NuevaSolicitudForm.tsx` — campo `carrera_id` con `Input` del UI Kit, hint explicando que no hay catálogo (BE-10) y que debe usarse el UUID proporcionado por la institución, validación estricta con regex de UUID canónico (`isValidCarreraId`, exportada y probada por separado), obligatorio, foco en el error, confirmación real vía `window.confirm` antes de enviar (mismo patrón ya usado y probado en el logout de `AppLayout`), doble guard contra doble envío. Sin selector de modalidad, sin TIC/Examen Complexivo/Proyecto de Emprendimiento, sin inferencia de elegibilidad — DEC-14 respetada sin cambios.).

### FE-T302 — Integración de creación de expediente

- **Objetivo:** consumir `POST /expedientes/`.
- **Depende de:** FE-T301, FE-T013.
- **Módulos:** `src/api/endpoints/expedientes.ts`, `src/features/solicitud/`.
- **Pasos:**
  1. Tipos de request/response.
  2. Mutación con manejo de `isSubmitting`.
  3. Guardar ID local y redirigir a V-04.
  4. Invalidar bandeja.
- **Criterios de aceptación:** 201 → expediente creado y redirección; 400 → mensaje.
- **Pruebas:** integración MSW.
- **Evidencia:** pruebas.
- **Estimación:** M. **Prioridad:** Must. **Estado:** **Hecha** (2026-11-05: contrato real verificado directamente contra `backend/src/apps/expedientes/services/crear_expediente.py` + `backend/src/apps/expedientes/tests/test_crear_expediente.py` (pruebas reales del backend, no solo `specify.md`/`openapi.yaml`): `POST /api/v1/expedientes/` con `{"carrera_id": "<uuid>"}`, `RBAC_MATRIX["expedientes"]["POST"]["ESTUDIANTE"]=ALLOW`, 201 con `ExpedienteBorradorSerializer` (`id, numero_expediente, estudiante_id, carrera_id, estado, activa, fecha_creacion, peticiones[5]`). `crearExpediente()` añadida a `src/api/endpoints/expedientes.ts` (sin duplicar el archivo ni tocar `listBandejaEstudiante`). `useCrearExpediente()` en `src/features/solicitud/queries.ts` (`useMutation`, `retry:false` explícito —ver hallazgo P2 de `queryClient.ts`, heredado de V-02, no corregido aquí—), invalida `BANDEJA_ESTUDIANTE_QUERY_KEY` de V-02 en `onSuccess` reexportada desde un nuevo barrel `src/features/dashboard/index.ts` (la regla de lint `no-restricted-imports` del proyecto prohíbe importar módulos internos de otra feature; se creó el barrel mínimo necesario, sin tocar el resto de V-02). Sin reintentos automáticos del `POST` (operación de escritura; además `queryClient.ts` ya fija `mutations:{retry:0}` globalmente). Registro del `id`/`numero_expediente` creado vía `recordVisitedExpediente()` de `src/lib/storage.ts` (reutilizado de FE-T204, sin romperlo).).

### FE-T303 — Manejo de errores de creación

- **Objetivo:** tratar expediente activo y catálogo incompleto.
- **Depende de:** FE-T302.
- **Módulos:** `src/features/solicitud/`.
- **Pasos:**
  1. Mapear mensajes 400.
  2. Ofrecer enlace al expediente activo si el backend lo indica.
  3. 403 → V-09.
  4. 5xx/red → reintento.
- **Criterios de aceptación:** el usuario entiende el error y tiene una acción.
- **Pruebas:** RTL + MSW.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** **Hecha** (2026-11-05: `describeError()` en `NuevaSolicitudPage.tsx` clasifica la respuesta real —no se inventó 409/412/428, BE-11 sigue sin autorizar esa suposición, confirmado: el backend real devuelve **400** para expediente activo/catálogo incompleto—. **Expediente activo existente**: detectado por la palabra "activo" en `detail` (mismo criterio literal que usa la prueba real del backend, `test_creacion_rechazada_con_expediente_activo_previo_400`); el backend **no** incluye el `id` del expediente activo en esta respuesta (solo `{"detail": "..."}"`), por lo que en vez de inventar un enlace directo inexistente se ofrece el botón real "Ir a mi panel" → `/estudiante`, donde la bandeja de V-02 (ya funcional) permite verlo. **403**: `navigate('/no-habilitado')` (flujo V-09 existente, igual que las guardas de ruta — no se usó `ForbiddenState` inline como en los cards de V-02, por instrucción explícita de esta autorización). **5xx**: reutiliza `presentApiError()` sin duplicar lógica. **Red/timeout**: NO se ofrece un botón "Reintentar" que repita el `POST` (protección ante duplicados, ver FE-T302); se muestra un aviso de resultado ambiguo + el mismo botón "Ir a mi panel" para verificar la bandeja antes de cualquier nuevo intento manual. Mensajes mostrados en `Alert` (ya accesible, `role="alert"`), sin componentes nuevos.).

### FE-T304 — Borrador local del formulario

- **Objetivo:** conservar datos al recargar.
- **Depende de:** FE-T301.
- **Módulos:** `src/lib/storage.ts`, `src/features/solicitud/`.
- **Pasos:**
  1. Guardar `carrera_id` en `sessionStorage`.
  2. Restaurar al montar.
  3. Limpiar al crear o cerrar sesión.
- **Criterios de aceptación:** recargar conserva el valor; enviar lo limpia.
- **Pruebas:** RTL.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Should. **Estado:** **Hecha** (2026-11-05: `getNuevaSolicitudDraft`/`saveNuevaSolicitudDraft`/`clearNuevaSolicitudDraft` añadidas a `src/lib/storage.ts` (clave `sgt.nueva_solicitud_draft`, independiente de `sgt.recent_expedientes` de FE-T204 — no se tocó ni rompió esa funcionalidad). Se restaura al montar (`useState(() => getNuevaSolicitudDraft() ?? '')`), se actualiza en cada cambio del campo (y se limpia si el campo queda vacío), se limpia al crear con éxito y `AuthContext.logout()` fue extendido para llamar también `clearNuevaSolicitudDraft()` junto a `clearRecentExpedientes()` (aislamiento de sesión, mecanismo existente). Solo se guarda `carrera_id`; nunca contraseñas ni tokens.).

### FE-T305 — Éxito y redirección

- **Objetivo:** confirmar creación y llevar al expediente.
- **Depende de:** FE-T302.
- **Módulos:** `src/features/solicitud/`.
- **Pasos:**
  1. Toast de éxito con número de expediente.
  2. Redirección a `/expedientes/:id`.
  3. Prefetch del detalle.
- **Criterios de aceptación:** el usuario llega a V-04 con datos.
- **Pruebas:** integración.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** **Hecha, con la limitación de V-04 documentada** (2026-11-05: tras un 201 real se registra el `id`/`numero_expediente` (`recordVisitedExpediente`), se invalida la bandeja (en `useCrearExpediente`), se muestra un toast de éxito con el `numero_expediente` **real** devuelto por el backend (nunca inventado) vía `ToastProvider` existente, y se navega a `/expedientes/:id`. **Estado real de la ruta V-04 verificado**: `/expedientes/:id` está registrada en `router.tsx` (sin `RequireRole` adicional más allá de `RequireAuth`, por lo que es alcanzable) pero `ExpedientePage.tsx` sigue siendo el stub de FE-T009 ("Vista pendiente de implementación"); no se implementó ni se amplió V-04. **No se implementó prefetch**: aunque `GET /api/v1/expedientes/{id}/` es un endpoint real y accesible (`SCOPE_OWN`, verificado en `ExpedienteViewSet.retrieve`), construir una query de detalle para prefetch equivaldría a adelantar la capa de datos de V-04, fuera del alcance autorizado; se documenta como dependencia pendiente, no como funcionalidad faltante de V-03.).

### FE-T306 — Pruebas de V-03

- **Objetivo:** cubrir creación.
- **Depende de:** FE-T305.
- **Módulos:** `src/features/solicitud/__tests__/`.
- **Pasos:**
  1. 201, 400, 403, red.
  2. UUID inválido.
  3. Borrador.
- **Criterios de aceptación:** cobertura ≥ 80%.
- **Pruebas:** `npm run test`.
- **Evidencia:** reporte.
- **Estimación:** S. **Prioridad:** Must. **Estado:** **Hecha** (2026-11-05: convención `*.test.ts(x)` co-ubicados, igual que V-01/V-02. `NuevaSolicitudForm.test.tsx` (13, unitario) + `NuevaSolicitudPage.test.tsx` (11, integración real con MSW sobre contratos verificados contra el backend) = 24 pruebas nuevas. Cubren: formulario válido, UUID inválido, campo obligatorio, confirmación antes de enviar (aceptada/cancelada), prevención de doble envío (guard de botón + guard del handler + protección real ante doble `POST` concurrente), creación exitosa 201 verificado, 400 genérico, 400 "expediente activo" con botón real a la bandeja, 403→V-09, 500, red/timeout con aviso de ambigüedad y sin botón de reintento automático, persistencia/restauración/limpieza del borrador (incl. al borrar el campo), registro del ID creado, toast + navegación a `/expedientes/:id`, axe. Cobertura real (`npm run test -- --coverage`): `features/solicitud` 97,1% stmts / 97,29% branch / 100% funcs / 97,05% lines — ≥80% en las cuatro métricas (único hueco: rama defensiva no-`ApiRequestError`, mismo patrón ya aceptado en V-01/V-02). Suite completa: 277/277 pruebas, sin regresiones en F0–V02. `npm run lint`/`typecheck`/`build` sin errores. Verificación manual en navegador (`npm run dev`, sesión inyectada): formulario real, validación local, `window.confirm` real (cancelar bloquea el envío; aceptar lo dispara), POST real a `http://localhost:8000/api/v1/expedientes/` (falla con `ERR_CONNECTION_REFUSED` por ausencia de backend, confirmando que no es simulado), aviso de ambigüedad real sin reintento automático, navegación real a `/estudiante` desde "Ir a mi panel", responsive 375px sin overflow.).

---

## 9. Vista V-04 — Expediente y requisitos

### FE-T401 — Cabecera y timeline del expediente

- **Objetivo:** mostrar datos generales y estado.
- **Depende de:** FE-T020, FE-T025.
- **Módulos:** `src/features/expediente/ExpedienteHeader.tsx`, `ExpedientePage.tsx`.
- **Pasos:**
  1. Número, estado, fechas, días acumulados.
  2. Badge de estado.
  3. Timeline solo con estados reales.
  4. UUIDs de carrera/facultad con nota de limitación.
- **Criterios de aceptación:** datos correctos y accesibles.
- **Pruebas:** RTL + axe.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** **Hecha** (2026-11-05: `ExpedienteHeader.tsx` — número real, `Badge` de estado (7 estados reales de `ExpedienteTitulacion.ESTADOS_CHOICES`), fechas reales (`fecha_creacion`/`fecha_recepcion`/`fecha_limite_atencion`) y `dias_laborables_acumulados` (campo real del modelo, sin fórmula inventada). **Timeline construido solo con datos reales** (`buildTimelineSteps`): se verificó que `HistorialEstado` existe como modelo en el backend pero `ExpedienteDetalleSerializer` no lo serializa — por eso el timeline usa únicamente `fecha_creacion`/`fecha_recepcion` como fechas reales; los demás pasos del timeline muestran el estado (completado/actual/pendiente) sin fecha inventada. UUID de `carrera_id`/`facultad_id` mostrados con nota explícita de que no hay catálogo de nombres. `Badge`/`Card`/`Timeline` reutilizados del UI Kit sin duplicar.).

### FE-T402 — Carga de detalle y peticiones

- **Objetivo:** consumir `GET /expedientes/{id}/`.
- **Depende de:** FE-T401, FE-T013.
- **Módulos:** `src/api/endpoints/expedientes.ts`, `src/features/expediente/`.
- **Pasos:**
  1. Tipos de `ExpedienteDetalle` y `Peticion`.
  2. Query por ID.
  3. Render de peticiones.
  4. Manejo 404/403.
- **Criterios de aceptación:** detalle y peticiones visibles; 404/403 correctos.
- **Pruebas:** integración MSW.
- **Evidencia:** pruebas.
- **Estimación:** M. **Prioridad:** Must. **Estado:** **Hecha** (2026-11-05: `GET /api/v1/expedientes/{id}/` verificado contra `ExpedienteViewSet.retrieve` + `ExpedienteDetalleSerializer` (código real, no solo `openapi.yaml`): campos reales `id, numero_expediente, estudiante_id, carrera_id, facultad_id, estado, activa, fecha_creacion, fecha_recepcion, numero_providencia, fecha_limite_atencion, dias_laborables_acumulados, peticiones[]`; aislamiento real por `scope_queryset` (ESTUDIANTE→`SCOPE_OWN`, operativos→`SCOPE_FACULTAD`/`SCOPE_CARRERA`, ADMINISTRADOR→`ALLOW`) — un expediente ajeno responde 404 real (vía `get_object_or_404` sobre el queryset ya filtrado), no simulado. `getExpedienteDetalle()` añadida a `src/api/endpoints/expedientes.ts` (sin duplicar `listBandejaEstudiante`/`crearExpediente`). `useExpedienteDetalle()` en `src/features/expediente/queries.ts`, `retry:false` explícito. `PeticionesSection.tsx` renderiza `peticiones[]` reutilizando `Table`/`Badge`. 404/403 manejados vía `presentApiError()` existente (sin duplicar), con `NotFoundState`/`ForbiddenState` del UI Kit.).

### FE-T403 — Checklist con manejo de 403

- **Objetivo:** cargar checklist solo para roles autorizados.
- **Depende de:** FE-T402.
- **Módulos:** `src/api/endpoints/checklist.ts`, `ChecklistPanel.tsx`, `ChecklistItem.tsx`.
- **Pasos:**
  1. Query condicionada por rol.
  2. Render de requisitos y estados.
  3. Para estudiante, no llamar o manejar 403 como panel informativo.
  4. No reintentar en bucle.
- **Criterios de aceptación:** roles autorizados ven checklist; estudiante ve limitación sin error no controlado.
- **Pruebas:** integración por rol.
- **Evidencia:** pruebas.
- **Estimación:** M. **Prioridad:** Must. **Estado:** **Hecha** (2026-11-05: `GET /api/v1/expedientes/{expediente_id}/checklist/` verificado contra `ChecklistListViewSet`: `RBAC_MATRIX["checklist"]["GET"]` solo concede `SECRETARIO_ABOGADO`/`ANALISTA_APOYO` (`SCOPE_FACULTAD`) y `ADMINISTRADOR` (`ALLOW`) — **ESTUDIANTE no está en la matriz**, por lo que recibe 403 real con el mensaje de `HasRolePermission` ("El rol del usuario no esta autorizado..."). `useChecklist()` usa `enabled: puedeVerChecklist(roles)` (TanStack Query) para **no ejecutar la petición en absoluto** para ESTUDIANTE, verificado con una prueba que confirma que el handler MSW nunca se invoca. `ChecklistSection.tsx` muestra `ForbiddenState` ("No disponible para su rol") sin siquiera consultar la API para ese rol; para roles autorizados muestra los ítems reales (`id, requisito_codigo, requisito_nombre, estado_verificacion, evaluado_por_username, fecha_evaluacion`). Sin bucle de reintento (`retry:false`).).

### FE-T404 — Acción enviar expediente

- **Objetivo:** enviar un expediente en `BORRADOR`.
- **Depende de:** FE-T402.
- **Módulos:** `EnviarExpedienteDialog.tsx`, `src/api/endpoints/expedientes.ts`.
- **Pasos:**
  1. Botón visible solo para estudiante en `BORRADOR`.
  2. Confirmación con resumen.
  3. `POST /enviar/`.
  4. Manejar 400/422.
  5. Invalidar y refrescar.
- **Criterios de aceptación:** 200 → `ENVIADA`; 422 → mensaje de requisitos incompletos.
- **Pruebas:** integración MSW.
- **Evidencia:** pruebas.
- **Estimación:** M. **Prioridad:** Must. **Estado:** **Hecha** (2026-11-05: `enviarExpediente()` reutiliza el endpoint ya verificado en V-03 (`ExpedienteViewSet.enviar`, `POST /expedientes/{id}/enviar/`, **200 real**, no 201). Botón "Enviar expediente" condicionado por `puedeEnviar(roles, estado, esPropietario)` (FE-T409): solo visible para ESTUDIANTE con el expediente en `BORRADOR`. Confirmación real vía `window.confirm` (mismo patrón que V-03). `useEnviarExpediente()` sin reintentos automáticos (`retry:false`), invalida `expediente-detalle` y `BANDEJA_ESTUDIANTE_QUERY_KEY` (de V-02, vía el barrel `@/features/dashboard`) en `onSuccess`. 422 (`RequisitosIncompletosError`) muestra el mensaje real del backend sin inventar una lista de errores — verificado con `CA-V04-03`.).

### FE-T405 — Acción observar expediente

- **Objetivo:** registrar observación con motivo.
- **Depende de:** FE-T402.
- **Módulos:** `ObservarExpedienteDialog.tsx`.
- **Pasos:**
  1. Visible solo para `SECRETARIO_ABOGADO`.
  2. Campo `motivo_observacion` obligatorio.
  3. `POST /observar/` con `peticion_id` opcional.
  4. Manejar 400/403.
  5. Invalidar y refrescar.
- **Criterios de aceptación:** 201 → `OBSERVADA` y motivo visible.
- **Pruebas:** integración MSW.
- **Evidencia:** pruebas.
- **Estimación:** M. **Prioridad:** Must. **Estado:** **Hecha, con discrepancia real documentada (INC-21)** (2026-11-05: `observarExpediente()` verificado contra `ExpedienteViewSet.observar` (ruta real wireada en `urls.py`; se confirmó además que `ObservacionViewSet` —con un método `crear_observacion` similar— existe en el código pero **no está mapeada a ninguna URL real**, por lo que no es el contrato vigente). **201 real** (no 200). Body real `{motivo_observacion, peticion_id?}` — `peticion_id` se lee directo de `request.data` en el backend (no está en `ObservacionRegistroSerializer`), por eso es opcional y se construye con las `peticiones[]` ya disponibles del detalle (sin endpoint adicional). `ObservarDialog.tsx` (Modal accesible del UI Kit) exige `motivo_observacion`; botón "Observar" condicionado por `puedeObservar(roles, estado)`: solo `SECRETARIO_ABOGADO` con el expediente `EN_VERIFICACION` (confirmado en `RBAC_MATRIX["expedientes:observar"]`, que NO concede a `ANALISTA_APOYO`). **Discrepancia real (INC-21):** dos de las cuatro excepciones de dominio (`ExpedienteNoEnVerificacionError`, `PeticionNoEncontradaError`) se re-lanzan como `APIException` genérica sin `status_code` propio → **HTTP 500**, no 400/404 como asumiría la documentación; se implementó mostrando siempre el mensaje real del backend (`describeAccionError()`) sin importar si llega como 400 o 500, en vez de tratar todo 500 como "error de servidor genérico".).

### FE-T406 — Evaluar checklist

- **Objetivo:** marcar requisito como `VERIFICADO` u `OBSERVADO`.
- **Depende de:** FE-T403.
- **Módulos:** `ChecklistItem.tsx`, `src/api/endpoints/checklist.ts`.
- **Pasos:**
  1. Acciones por rol/estado.
  2. Si `OBSERVADO`, exigir `motivo_observacion`.
  3. `PUT /checklist/{id}/`.
  4. Manejar 400/403.
  5. Invalidar checklist y expediente.
- **Criterios de aceptación:** evaluación persiste; sin motivo no se envía.
- **Pruebas:** integración MSW.
- **Evidencia:** pruebas.
- **Estimación:** M. **Prioridad:** Must. **Estado:** **Hecha, con discrepancia real documentada (INC-21)** (2026-11-05: `evaluarChecklist()` verificado contra `ChecklistViewSet.update` (`PUT /checklist/{id}/`), **200 real**. Acciones "Verificar"/"Observar" por ítem condicionadas por `puedeEvaluarItem(roles, estadoExpediente, estadoItem)`: solo `SECRETARIO_ABOGADO`/`ANALISTA_APOYO`/`ADMINISTRADOR`, expediente `EN_VERIFICACION` e ítem `PENDIENTE` (confirmado: `VerificationAlreadyCompletedError` real si se reevalúa). Motivo obligatorio para `OBSERVADO` validado **localmente antes de llamar a la API** (no solo visualmente: la UI nunca construye ni envía la petición sin motivo) y también por el propio `ChecklistEvaluationSerializer` del backend como defensa real. **Discrepancia (INC-21):** `ChecklistVerificationNotFoundError` → 500 real (no 404); se muestra igualmente el mensaje real del backend. `onSuccess` invalida `checklist` y `expediente-detalle` (FE-T410).).

### FE-T407 — Subsanar checklist

- **Objetivo:** cargar un PDF para un requisito observado.
- **Depende de:** FE-T403, FE-T026.
- **Módulos:** `SubsanarDialog.tsx`.
- **Pasos:**
  1. Visible para estudiante (own), secretaria y admin según RBAC.
  2. Validar PDF.
  3. `POST /checklist/{id}/subsanar/` multipart.
  4. Manejar 200/400/403.
  5. Invalidar checklist y expediente.
- **Criterios de aceptación:** PDF válido subsana; inválido no se envía.
- **Pruebas:** integración MSW.
- **Evidencia:** pruebas.
- **Estimación:** M. **Prioridad:** Must. **Estado:** **Hecha, con una limitación real severa documentada para el actor principal** (2026-11-05: `subsanarChecklist()` verificado contra `ChecklistViewSet.subsanar` (`POST /checklist/{id}/subsanar/`, **201 real**, `multipart/form-data` con el campo exacto `archivo`). Reutiliza `FileUpload` de F2 **sin modificar sus reglas** (misma validación de extensión/MIME/magic-bytes/10 MB de `src/lib/files.ts`, ya alineada con el límite real del backend `SubsanacionSerializer`). Un PDF inválido se rechaza localmente y **no llama a la API** (verificado, CA-V04-07). RBAC real: `RBAC_MATRIX["checklist"]["POST"]` concede `ESTUDIANTE`(own)/`SECRETARIA_CARRERA`(carrera)/`ADMINISTRADOR`(all). **Hallazgo crítico (documentado, no resuelto modificando el backend):** el endpoint requiere el `id` de un `ChecklistVerification`, pero **ESTUDIANTE y SECRETARIA_CARRERA —los dos roles reales autorizados a subsanar— no tienen ningún endpoint accesible para descubrir ese `id`**: el único listado (`GET /expedientes/{id}/checklist/`) es 403 para ambos roles (FE-T403), y ni la respuesta de `peticiones[]` del detalle ni las notificaciones exponen el `checklist_verification_id` (solo el `id` de la petición, que el servicio `subsanar_requisito.py` no acepta). Se implementó el flujo completo y correcto dondequiera que el `id` SÍ esté disponible (la sección de checklist, visible solo a roles con acceso de lista — en la práctica, solo `ADMINISTRADOR` reúne lista+escritura); para `ESTUDIANTE`, `PeticionesSection.tsx` muestra una nota honesta en vez de un botón roto cuando `estado_peticion==='OBSERVADO'`. No se modificó el backend para resolver esto, conforme a la restricción explícita de esta autorización.).

### FE-T408 — Descarga de documentos

- **Objetivo:** descargar el documento de una petición.
- **Depende de:** FE-T402.
- **Módulos:** `src/api/endpoints/peticiones.ts`, `src/lib/files.ts`.
- **Pasos:**
  1. `fetch` con auth y blob.
  2. Leer `Content-Disposition`.
  3. Crear enlace temporal y revocar.
  4. Manejar 404/403.
- **Criterios de aceptación:** el PDF se descarga con nombre correcto.
- **Pruebas:** integración MSW.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** **Hecha** (2026-11-05: contrato verificado contra `PeticionViewSet.descargar_documento` real (`GET /peticiones/{id}/documento/` y `/{id}/documento/{version}/`): `FileResponse` con `Content-Type` real del documento (`tipo_mime` o `application/pdf` — **no se asume que todo sea PDF**) y `Content-Disposition: attachment; filename="..."`; 404 real (`Http404`) si no hay acceso o no existe el archivo. Utilidad reutilizable nueva `src/lib/download.ts` (`fetchAuthenticatedFile`/`triggerBlobDownload`, no existía ninguna previa): usa el mismo mecanismo de sesión que `api/client.ts` (Bearer en `Authorization`, **nunca en la URL**), obtiene el `Blob` real, lee el nombre de `Content-Disposition` con respaldo si falta, crea un enlace temporal y lo revoca tras usarlo. `DescargaButton.tsx` condicionado por `puedeDescargar(roles)` — excluye a `DECANO` a propósito (no está en `RBAC_MATRIX["peticiones:documento"]["GET"]`, confirmado en el código real).).

### FE-T409 — Visibilidad de acciones por rol/estado

- **Objetivo:** evitar acciones no permitidas.
- **Depende de:** FE-T404…FE-T408.
- **Módulos:** `src/features/expediente/actions.ts`.
- **Pasos:**
  1. Matriz rol × estado × acción.
  2. Ocultar/deshabilitar con explicación.
  3. No confiar en la UI como seguridad.
- **Criterios de aceptación:** cada rol ve solo sus acciones.
- **Pruebas:** unitarias de la matriz.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** **Hecha** (2026-11-05: `src/features/expediente/accionesPorRolEstado.ts` — matriz explícita ROL×ESTADO×ACCIÓN (`puedeVerChecklist`, `puedeEnviar`, `puedeObservar`, `puedeEvaluarItem`, `puedeSubsanarItem`, `puedeDescargar`), basada únicamente en las reglas verificadas en el backend real durante la auditoría (ver matriz de contratos en el informe final). 20 pruebas unitarias exhaustivas (`accionesPorRolEstado.test.ts`) cubriendo combinaciones rol×estado relevantes, incl. negativos explícitos (p. ej. `ANALISTA_APOYO` no puede observar aunque sí evaluar; `SECRETARIO_ABOGADO`/`ANALISTA_APOYO` no pueden subsanar aunque vean el checklist; `DECANO` no puede descargar). Acciones no autorizadas se **ocultan** (no solo se deshabilitan) con las secciones de estado/panel informativo correspondientes. La matriz es solo ayuda de interfaz: el backend sigue aplicando su propio RBAC real independientemente (verificado con las pruebas de 403 reales de `ExpedientePage.test.tsx`).).

### FE-T410 — Invalidación y refresco

- **Objetivo:** mantener consistencia tras mutaciones.
- **Depende de:** FE-T404…FE-T408.
- **Módulos:** `src/lib/queryClient.ts`, `src/features/expediente/`.
- **Pasos:**
  1. Invalidar `expediente`, `checklist`, `bandeja`.
  2. Refrescar datos visibles.
  3. Evitar refetch en bucle.
- **Criterios de aceptación:** tras cada acción, la UI refleja el nuevo estado.
- **Pruebas:** integración.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** **Hecha** (2026-11-05: cada mutación (`useEnviarExpediente`, `useObservarExpediente`, `useEvaluarChecklist`, `useSubsanarChecklist` en `src/features/expediente/queries.ts`) invalida en `onSuccess` exactamente las claves reales afectadas: `expediente-detalle` (siempre), `checklist` (observar/evaluar/subsanar) y `BANDEJA_ESTUDIANTE_QUERY_KEY` de V-02 (solo enviar, porque mover a `ENVIADA` hace que el expediente desaparezca de la bandeja del estudiante). Ninguna mutación tiene reintento automático (`retry:false` explícito en las cuatro; además `queryClient.ts` ya fija `mutations:{retry:0}` globalmente — hallazgo P2 heredado de V-02/V-03, no corregido aquí por instrucción explícita de esta autorización). Sin refetch en bucle: las invalidaciones son puntuales por clave, no un `invalidateQueries()` global.).

### FE-T411 — Pruebas de V-04

- **Objetivo:** cubrir los flujos del expediente.
- **Depende de:** FE-T410.
- **Módulos:** `src/features/expediente/__tests__/`.
- **Pasos:**
  1. Por rol y estado.
  2. 400/403/404/422.
  3. Checklist 403 del estudiante.
  4. Upload inválido.
- **Criterios de aceptación:** cobertura ≥ 80%.
- **Pruebas:** `npm run test`.
- **Evidencia:** reporte.
- **Estimación:** M. **Prioridad:** Must. **Estado:** **Hecha** (2026-11-05: convención `*.test.ts(x)` co-ubicados, igual que V-01/V-02/V-03. `ExpedientePage.test.tsx` (16, integración real multi-rol con MSW sobre contratos verificados) + `ChecklistSection.test.tsx` (5) + `accionesPorRolEstado.test.ts` (20) + `errors.test.ts` (5) + `checklist.test.ts` (1) + `download.test.ts` (4) = 51 pruebas nuevas. Cubren: detalle por rol/estado, 404, 403 real, timeline/cabecera, peticiones, checklist autorizado, checklist 403 del estudiante **sin ejecutar la query** (verificado que el handler MSW nunca se invoca), enviar desde BORRADOR, 422 real sin enviar, observar con motivo, validación local sin motivo, evaluar VERIFICADO/OBSERVADO, PDF inválido sin llamar a la API, descarga real (Blob + Content-Disposition), error 404 de descarga, discrepancia real INC-21 (500 de regla de negocio con mensaje real), axe. Cobertura real (`npm run test -- --coverage`): `features/expediente` **85,78% stmts / 86,36% branch / 84,37% funcs / 85,63% lines** — ≥80% en las cuatro métricas. Suite completa: 328/328 pruebas, sin regresiones en F0–V03. `npm run lint`/`typecheck`/`build` sin errores. Verificación manual en navegador (`npm run dev`, sesión SECRETARIO_ABOGADO inyectada): estructura accesible completa, botón "Reintentar" dispara peticiones reales a `GET http://localhost:8000/api/v1/expedientes/{id}/` y `.../checklist/` (fallan con `ERR_CONNECTION_REFUSED` por ausencia de backend, confirmando que no es simulado), responsive 375px sin overflow.).

---

## 10. Vista V-05 — Gestión de peticiones

### FE-T501 — Lista de peticiones y estados

- **Objetivo:** mostrar peticiones del expediente.
- **Depende de:** FE-T402, FE-T022.
- **Módulos:** `src/features/peticiones/PeticionesPage.tsx`.
- **Pasos:**
  1. Listar desde el detalle.
  2. Badge de estado y dependencia.
  3. Enlace a V-06.
  4. Estado vacío.
- **Criterios de aceptación:** lista correcta y accesible.
- **Pruebas:** RTL + axe.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** Hecha (2026-11-12): `PeticionesTabla` con #, requisito, estado legible, dependencia, acciones y enlace a V-06; vacío con `Table`. Pruebas RTL + axe en `PeticionesPage.test.tsx`.

### FE-T502 — Solicitar emisión

- **Objetivo:** cambiar `PENDIENTE` → `SOLICITADO`.
- **Depende de:** FE-T501.
- **Módulos:** `SolicitarEmisionButton.tsx`, `src/api/endpoints/peticiones.ts`.
- **Pasos:**
  1. Visible para roles autorizados y estado `PENDIENTE`.
  2. Confirmación.
  3. `POST /solicitar-emision/`.
  4. Manejar 400/403/404.
  5. Invalidar expediente.
- **Criterios de aceptación:** 200 → `SOLICITADO`; errores claros.
- **Pruebas:** integración MSW.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** Hecha (2026-11-12): `api/endpoints/peticiones.ts` (`solicitarEmision`) + `SolicitarEmisionDialog` (confirmación) + invalidación del expediente. Visible solo para ESTUDIANTE con expediente BORRADOR/OBSERVADA y petición PENDIENTE (RBAC `peticiones` POST excluye a SECRETARIA_CARRERA aunque el servicio la admita: discrepancia registrada). 400/403/404 con el mensaje real.

### FE-T503 — Cargar documento

- **Objetivo:** subir PDF de una petición.
- **Depende de:** FE-T501, FE-T026.
- **Módulos:** `CargarDocumentoDialog.tsx`.
- **Pasos:**
  1. Visible para roles autorizados y estado válido.
  2. Validación PDF.
  3. `POST /documento/` multipart.
  4. Progreso y manejar 201/400/403.
  5. Invalidar expediente.
- **Criterios de aceptación:** PDF válido se registra; inválido no se envía.
- **Pruebas:** integración MSW.
- **Evidencia:** pruebas.
- **Estimación:** M. **Prioridad:** Must. **Estado:** Hecha (2026-11-12): `CargarDocumentoDialog` con `FileUpload` (+ prop `onInvalidFile`) y POST multipart `archivo`. Estados PENDIENTE/SOLICITADO/OBSERVADO/CARGADO; ESTUDIANTE o SECRETARIA_CARRERA solo en peticiones de la Secretaría (regla del servicio, más estricta que la matriz RBAC: discrepancia registrada). Sin porcentaje de progreso (`fetch` no lo expone): estado «Subiendo…».

### FE-T504 — Descargar documento

- **Objetivo:** descargar la versión vigente.
- **Depende de:** FE-T501.
- **Módulos:** `src/api/endpoints/peticiones.ts`.
- **Pasos:**
  1. Botón de descarga.
  2. `fetch` blob con auth.
  3. Manejar 404/403.
- **Criterios de aceptación:** descarga correcta.
- **Pruebas:** integración MSW.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** Hecha (2026-11-12): reutiliza `DescargaButton` de V-04 (`lib/download`, blob con `Authorization`), solo cuando el estado implica documento; 403/404 con el mensaje real.

### FE-T505 — Aviso de limitación de creación

- **Objetivo:** explicar que las peticiones se generan automáticamente.
- **Depende de:** FE-T501.
- **Módulos:** `src/features/peticiones/PeticionesPage.tsx`.
- **Pasos:**
  1. Texto informativo.
  2. Sin botón "Crear petición".
  3. Enlace a V-04.
- **Criterios de aceptación:** no se ofrece una acción inexistente.
- **Pruebas:** RTL.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** Hecha (2026-11-12): aviso «Las peticiones se generan automáticamente», sin botón de creación y con enlace a V-04.

### FE-T506 — Pruebas de V-05

- **Objetivo:** cubrir peticiones.
- **Depende de:** FE-T505.
- **Módulos:** `src/features/peticiones/__tests__/`.
- **Pasos:**
  1. Solicitar y cargar.
  2. 400/403/404.
  3. Archivo inválido.
- **Criterios de aceptación:** cobertura ≥ 80%.
- **Pruebas:** `npm run test`.
- **Evidencia:** reporte.
- **Estimación:** S. **Prioridad:** Must. **Estado:** Hecha (2026-11-12): `accionesPeticion.test.ts`, `api/endpoints/peticiones.test.ts`, `PeticionesPage.test.tsx` (30 pruebas nuevas, incluida 1 de `FileUpload`). Suite 358/358; typecheck, lint y build en verde; 3 mutaciones de salvaguardas detectadas.

---

## 11. Vista V-06 — Seguimiento de petición

### FE-T601 — Resolver petición desde el expediente

- **Objetivo:** obtener la petición sin `GET /peticiones/{id}/`.
- **Depende de:** FE-T402.
- **Módulos:** `src/features/peticiones/SeguimientoPeticionPage.tsx`.
- **Pasos:**
  1. Leer `id` de la ruta.
  2. Buscar en `peticiones[]` del detalle.
  3. Si no está, mostrar no encontrado.
- **Criterios de aceptación:** petición existente se muestra; inexistente → no encontrado.
- **Pruebas:** integración MSW.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** Hecha (2026-11-12): `seguimiento.ts` (`buscarPeticion`) resuelve la petición entre las anidadas en `GET /expedientes/{id}/`; si no pertenece al expediente → «Petición no encontrada» con salidas. **BE-02 verificado:** no existe `GET /peticiones/{id}/` (`PeticionDocumentalViewSet` está en `views.py` pero no se registra en `config/urls.py`).

### FE-T602 — Resumen de la petición

- **Objetivo:** mostrar estado, dependencia y fechas.
- **Depende de:** FE-T601.
- **Módulos:** `SeguimientoPeticionPage.tsx`.
- **Pasos:**
  1. Badge de estado.
  2. Requisito y dependencia.
  3. Fechas formateadas.
  4. Aviso de falta de historial (BE-02).
- **Criterios de aceptación:** datos correctos y accesibles.
- **Pruebas:** RTL + axe.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** Hecha (2026-11-12) con desviación documentada: badge y descripción del estado **actual** real, requisito/código, dependencia y expediente; aviso «Historial no disponible» (BE-02). La API no devuelve fechas de la petición: solo se muestra la fecha de registro del expediente, rotulada «creada junto con el expediente» (las peticiones se crean con `bulk_create` en `crear_expediente`). Sin hitos inferidos (una petición puede pasar a CARGADO sin SOLICITADO); motivo de observación no disponible (BE-07).

### FE-T603 — Descarga vigente y por versión

- **Objetivo:** permitir descargar el documento.
- **Depende de:** FE-T602.
- **Módulos:** `src/api/endpoints/peticiones.ts`.
- **Pasos:**
  1. Descarga vigente.
  2. Selector de versión solo si se conoce.
  3. Manejar 404/403.
- **Criterios de aceptación:** descarga correcta; sin versiones inventadas.
- **Pruebas:** integración MSW.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** Hecha (2026-11-12): descarga de la versión **vigente** con `DescargaButton` (`GET /peticiones/{id}/documento/`), solo si hay documento y el rol puede descargar. **Sin selector de versión:** no hay endpoint para listar versiones ni la descarga informa la versión (BE-02); no se inventan versiones. 404/403 con el mensaje real.

### FE-T604 — Estados de error y no encontrado

- **Objetivo:** cubrir fallos y ausencia.
- **Depende de:** FE-T601.
- **Módulos:** `SeguimientoPeticionPage.tsx`.
- **Pasos:**
  1. Loading, error, 404.
  2. Reintento.
  3. Enlace al expediente.
- **Criterios de aceptación:** el usuario siempre tiene salida.
- **Pruebas:** RTL + MSW.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** Hecha (2026-11-12): carga, 404 de expediente, 403 (`ForbiddenState`), 500 y error de red con reintento real; enlaces «Volver a las peticiones» y «Volver al expediente».

### FE-T605 — Pruebas de V-06

- **Objetivo:** cubrir seguimiento.
- **Depende de:** FE-T604.
- **Módulos:** `src/features/peticiones/__tests__/`.
- **Pasos:**
  1. Encontrada/no encontrada.
  2. Descarga.
  3. Error de red.
- **Criterios de aceptación:** cobertura ≥ 80%.
- **Pruebas:** `npm run test`.
- **Evidencia:** reporte.
- **Estimación:** S. **Prioridad:** Must. **Estado:** Hecha (2026-11-12): `seguimiento.test.ts` y `SeguimientoPeticionPage.test.tsx` (16 pruebas: encontrada/no encontrada, axe, descarga vigente sin versión, 404 de descarga, roles, 403/404/500 y error de red). Suite 374/374; typecheck, lint y build en verde; 3 mutaciones detectadas.

---

## 12. Vista V-07 — Bandeja del funcionario

### FE-T701 — Query de bandeja y paginación

- **Objetivo:** listar expedientes según rol.
- **Depende de:** FE-T013, FE-T023.
- **Módulos:** `src/api/endpoints/expedientes.ts`, `src/features/bandeja/BandejaPage.tsx`.
- **Pasos:**
  1. Tipos de `BandejaExpediente`.
  2. Query con `page`/`page_size`.
  3. Paginación.
  4. Manejar 401/403.
- **Criterios de aceptación:** datos paginados correctos.
- **Pruebas:** integración MSW.
- **Evidencia:** pruebas.
- **Estimación:** M. **Prioridad:** Must. **Estado:** Hecha (2026-11-12): `listBandejaOperativa()` (tipos reales de `BandejaExpedienteSerializer`; `page_size` ≤ 50) + `useBandejaOperativa`; paginación real; 403 → `ForbiddenState` con enlace a V-09; 401 por el manejador global; 500/red con reintento.

### FE-T702 — Tabla y tarjetas de bandeja

- **Objetivo:** mostrar columnas requeridas.
- **Depende de:** FE-T701, FE-T022.
- **Módulos:** `BandejaTable.tsx`.
- **Pasos:**
  1. Columnas: número, estudiante, carrera, facultad, estado, fechas, providencia.
  2. Vista de tarjetas en móvil.
  3. Badge de estado.
- **Criterios de aceptación:** sin overflow; accesible.
- **Pruebas:** RTL + axe.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** Hecha (2026-11-12): `BandejaTable` con número (enlace), estado, fecha límite, plazo, recepción, providencia, ids abreviados de estudiante/carrera/facultad y creación; tabla en escritorio y tarjetas en móvil (`Table`). **Desviación documentada:** la API solo da UUID, no nombres de estudiante/carrera/facultad (BE-01/BE-05).

### FE-T703 — Filtros de página

- **Objetivo:** ofrecer filtros limitados a la página actual.
- **Depende de:** FE-T702.
- **Módulos:** `BandejaFilters.tsx`.
- **Pasos:**
  1. Filtro por estado/número.
  2. Etiqueta "filtra la página actual".
  3. No prometer búsqueda global.
- **Criterios de aceptación:** el filtro no induce a error.
- **Pruebas:** RTL.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Should. **Estado:** Hecha (2026-11-12): `BandejaFilters` por estado y número, rotulados «solo actúan sobre la página actual (N de M)», sin búsqueda global ni peticiones al backend (BE-09: sin filtros en servidor).

### FE-T704 — Estados vacíos y vencimientos

- **Objetivo:** explicar bandeja vacía y resaltar plazos.
- **Depende de:** FE-T701.
- **Módulos:** `BandejaPage.tsx`.
- **Pasos:**
  1. Vacío por rol.
  2. Cálculo local de vencimiento próximo.
  3. No inventar datos.
- **Criterios de aceptación:** vacío claro; vencimientos correctos.
- **Pruebas:** RTL.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Should. **Estado:** Hecha (2026-11-12): vacío por rol (BE-09 para SECRETARIA_CARRERA/DIRECTOR_CARRERA, cuya bandeja el backend devuelve siempre vacía; «sin pendientes» para el resto) y plazos locales sobre `fecha_limite_atencion`: vencido, vence hoy o días calendario restantes. Sin umbral de «próximo a vencer» porque la spec no lo define; el backend cuenta días laborables.

### FE-T705 — Navegación a detalle

- **Objetivo:** abrir V-08.
- **Depende de:** FE-T702.
- **Módulos:** `BandejaTable.tsx`, `router.tsx`.
- **Pasos:**
  1. Fila clicable y enlace accesible.
  2. Navegación a `/bandeja/:id`.
  3. Prefetch del detalle.
- **Criterios de aceptación:** navegación funciona con teclado.
- **Pruebas:** RTL.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** Hecha (2026-11-12): enlace accesible por teclado a `/bandeja/:id` (V-08) con precarga de `GET /expedientes/{id}/` al enfocar o pasar el puntero.

### FE-T706 — Pruebas de V-07

- **Objetivo:** cubrir bandeja por rol.
- **Depende de:** FE-T705.
- **Módulos:** `src/features/bandeja/__tests__/`.
- **Pasos:**
  1. Roles con/sin expedientes.
  2. Paginación.
  3. Error.
- **Criterios de aceptación:** cobertura ≥ 80%.
- **Pruebas:** `npm run test`.
- **Evidencia:** reporte.
- **Estimación:** S. **Prioridad:** Must. **Estado:** Hecha (2026-11-12): `bandejaReglas.test.ts` y `BandejaPage.test.tsx` (20 pruebas: CA-V07-01…05, filtros locales, vencimientos, precarga, sin escritura, 403/500/red, axe). Ajuste de `router.test.tsx` y `LoginPage.test.tsx` al h1 real (antes buscaban el título del stub). Suite 394/394; 4 mutaciones detectadas.

---

## 13. Vista V-08 — Detalle del funcionario

### FE-T801 — Carga de detalle y checklist

- **Objetivo:** reutilizar V-04 con acciones de funcionario.
- **Depende de:** FE-T402, FE-T403.
- **Módulos:** `src/features/bandeja/DetalleFuncionarioPage.tsx`.
- **Pasos:**
  1. Cargar detalle y checklist.
  2. Mostrar datos y peticiones.
  3. Manejar 403/404.
- **Criterios de aceptación:** detalle completo para roles operativos.
- **Pruebas:** integración MSW.
- **Evidencia:** pruebas.
- **Estimación:** M. **Prioridad:** Must. **Estado:** Hecha (2026-11-12, V-08a): `DetalleFuncionarioPage` reutiliza `ExpedienteHeader`, `PeticionesSection` y `ChecklistSection` de V-04 (barrel `@/features/expediente`); checklist solo para roles con RBAC; 404 con salida a la bandeja, 403 con enlace a V-09 y 500 con reintento.

### FE-T802 — Evaluar checklist (funcionario)

- **Objetivo:** reutilizar FE-T406 en V-08.
- **Depende de:** FE-T801, FE-T406.
- **Módulos:** `DetalleFuncionarioPage.tsx`.
- **Pasos:**
  1. Integrar `ChecklistPanel`.
  2. Acciones por rol/estado.
  3. Invalidar.
- **Criterios de aceptación:** evaluación funciona desde V-08.
- **Pruebas:** integración.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** Hecha (2026-11-12, V-08a): evaluación del checklist con `ChecklistSection` de V-04 (SECRETARIO_ABOGADO, ANALISTA_APOYO, ADMINISTRADOR en EN_VERIFICACION).

### FE-T803 — Observar expediente (funcionario)

- **Objetivo:** reutilizar FE-T405.
- **Depende de:** FE-T801, FE-T405.
- **Módulos:** `DetalleFuncionarioPage.tsx`.
- **Pasos:**
  1. Integrar diálogo.
  2. Mostrar estado resultante.
- **Criterios de aceptación:** observación funciona desde V-08.
- **Pruebas:** integración.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** Hecha (2026-11-12, V-08a): observar con `ObservarDialog` (solo SECRETARIO_ABOGADO en EN_VERIFICACION). **Ampliación verificada:** también «Iniciar verificación» (`POST /expedientes/{id}/iniciar-verificacion/`, E2-01, posterior a esta spec; solo SECRETARIO_ABOGADO, ENVIADA → EN_VERIFICACION).

### FE-T804 — Emitir informe

- **Objetivo:** registrar dictamen `APTO`/`NO APTO`.
- **Depende de:** FE-T801.
- **Módulos:** `src/features/informes/EmitirInformeDialog.tsx`, `src/api/endpoints/informes.ts`.
- **Pasos:**
  1. Visible para `SECRETARIO_ABOGADO`/`ANALISTA_APOYO`.
  2. Campos `dictamen`, `fundamentacion`.
  3. `POST /informes/`.
  4. Manejar 201/400/403.
  5. Invalidar.
- **Criterios de aceptación:** informe registrado; estado refrescado.
- **Pruebas:** integración MSW.
- **Evidencia:** pruebas.
- **Estimación:** M. **Prioridad:** Must. **Estado:** Hecha (2026-11-12, V-08b) con desviaciones verificadas: solo SECRETARIO_ABOGADO en EN_VERIFICACION (el servicio rechaza a ANALISTA_APOYO aunque RBAC le dé ámbito BORRADOR); dictamen **solo APTO** («NO APTO» siempre devuelve 400, así que no se ofrece); deshabilitado con explicación si el checklist no está 100 % VERIFICADO; desde OBSERVADA el backend responde 409 `regla_pendiente_o1` (O-1) y no se ofrece. **Sin GET ni descarga del informe:** el resultado solo se muestra con la respuesta de creación.

### FE-T805 — Declarar aptitud

- **Objetivo:** registrar declaratoria con memorando firmado.
- **Depende de:** FE-T801, FE-T026.
- **Módulos:** `DeclararAptitudDialog.tsx`, `src/api/endpoints/declaratorias.ts`.
- **Pasos:**
  1. Visible para `DECANO` en `INFORME_EMITIDO`.
  2. Campos `expediente_id`, `archivo_memorando`, `numero_memorando`.
  3. Validar PDF.
  4. `POST /declaratorias/` multipart.
  5. Manejar 201/400/403.
  6. Invalidar.
- **Criterios de aceptación:** declaratoria registrada; expediente `DECLARADA_APTA`.
- **Pruebas:** integración MSW.
- **Evidencia:** pruebas.
- **Estimación:** M. **Prioridad:** Must. **Estado:** Hecha (2026-11-12, V-08b): DECANO en INFORME_EMITIDO; multipart `expediente_id`, `archivo_memorando` (PDF validado) y `numero_memorando` opcional (si se omite, lo genera el backend); 400/403/404 con el mensaje real. **Sin GET ni descarga de la declaratoria.**

### FE-T806 — Descarga de documentos (funcionario)

- **Objetivo:** descargar documentos desde V-08.
- **Depende de:** FE-T801, FE-T408.
- **Módulos:** `DetalleFuncionarioPage.tsx`.
- **Pasos:**
  1. Reutilizar descarga.
  2. Manejar 403/404.
- **Criterios de aceptación:** descarga correcta.
- **Pruebas:** integración.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** Hecha (2026-11-12, V-08a): descarga con `DescargaButton` de V-04 (sin DECANO, que no está en la matriz RBAC).

### FE-T807 — Visibilidad de acciones por rol/estado

- **Objetivo:** matriz de acciones de V-08.
- **Depende de:** FE-T802…FE-T806.
- **Módulos:** `src/features/bandeja/actions.ts`.
- **Pasos:**
  1. Matriz rol × estado × acción.
  2. Ocultar/deshabilitar con explicación.
  3. No asumir permisos.
- **Criterios de aceptación:** cada rol ve solo lo permitido.
- **Pruebas:** unitarias.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** Hecha (2026-11-12, V-08a): `accionesFuncionario.ts` (iniciar verificación, observar, evaluar, descargar) con explicación cuando el rol no tiene acciones de estado.

### FE-T808 — Estado solo lectura

- **Objetivo:** bloquear acciones en `DECLARADA_APTA` y estados finales.
- **Depende de:** FE-T807.
- **Módulos:** `DetalleFuncionarioPage.tsx`.
- **Pasos:**
  1. Detectar estados finales.
  2. Ocultar acciones de escritura.
  3. Mostrar aviso.
- **Criterios de aceptación:** no se ofrecen acciones inválidas.
- **Pruebas:** RTL.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** Hecha (2026-11-12, V-08a): DECLARADA_APTA y CANCELADA son de solo lectura, con aviso.

### FE-T809 — Invalidación y refresco

- **Objetivo:** mantener consistencia tras acciones.
- **Depende de:** FE-T802…FE-T805.
- **Módulos:** `src/features/bandeja/`.
- **Pasos:**
  1. Invalidar `expediente`, `checklist`, `bandeja`.
  2. Refrescar.
- **Criterios de aceptación:** la UI refleja el nuevo estado.
- **Pruebas:** integración.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** Hecha (2026-11-12, V-08a): `useInvalidarTrasAccion` invalida detalle, checklist y bandeja operativa (`staleTime` 30 s).

### FE-T810 — Pruebas de V-08

- **Objetivo:** cubrir flujo operativo.
- **Depende de:** FE-T809.
- **Módulos:** `src/features/bandeja/__tests__/`.
- **Pasos:**
  1. Por rol/estado.
  2. Checklist, observar, informe, declaratoria.
  3. 400/403/404.
- **Criterios de aceptación:** cobertura ≥ 80%.
- **Pruebas:** `npm run test`.
- **Evidencia:** reporte.
- **Estimación:** M. **Prioridad:** Must. **Estado:** Hecha (2026-11-12): `DetalleFuncionarioPage.test.tsx`, `accionesFuncionario.test.ts` (V-08a, 14) y `ResolucionesSection.test.tsx` (V-08b, 11); `router.test.tsx` adaptado. Suite 431/431; axe; mutaciones detectadas. Las pruebas de V-08b hallaron y corrigieron dos defectos reales (salto de foco por `onClose` inestable en `Modal` y pérdida del resultado de la declaratoria al pasar a estado final).

---

## 14. Vista V-09 — Estado no habilitado

### FE-T901 — Página de estado no habilitado

- **Objetivo:** comunicar limitaciones sin simular.
- **Depende de:** FE-T021.
- **Módulos:** `src/features/no-habilitado/NoHabilitadoPage.tsx`.
- **Pasos:**
  1. Título, descripción, motivo.
  2. Dependencia `BE-xx` cuando aplique.
  3. Alternativas de navegación.
  4. Código de referencia.
- **Criterios de aceptación:** mensaje claro y accesible.
- **Pruebas:** RTL + axe.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** Hecha (2026-11-12): `motivos.ts`, un catálogo cerrado de motivos (`rol-no-autorizado`, `sin-rol`, `no-disponible` con `BE-xx` en lista blanca BE-01…BE-11) con título, descripción, dependencia y código de referencia (`V09-…`). Sin datos de contacto inventados.

### FE-T902 — Integración con guardas y vistas parciales

- **Objetivo:** reutilizar V-09 desde guardas y paneles.
- **Depende de:** FE-T901, FE-T015.
- **Módulos:** `guards.tsx`, `ChecklistPanel.tsx`.
- **Pasos:**
  1. Pasar motivo/dependencia por props o query.
  2. No revelar recursos no autorizados.
  3. Evitar bucles de redirección.
- **Criterios de aceptación:** 403 y rutas no soportadas muestran V-09.
- **Pruebas:** integración.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** Hecha (2026-11-12): `RequireRole` redirige a `/no-habilitado?motivo=rol-no-autorizado`; V-07 enlaza con el mismo motivo ante un 403. No se repite la ruta pedida ni la regla; los parámetros desconocidos se ignoran. Sin bucles de redirección.

### FE-T903 — Navegación de retorno

- **Objetivo:** ofrecer salidas válidas.
- **Depende de:** FE-T901.
- **Módulos:** `NoHabilitadoPage.tsx`.
- **Pasos:**
  1. Volver atrás.
  2. Ir al inicio por rol.
  3. Contacto de soporte.
- **Criterios de aceptación:** el usuario no queda atrapado.
- **Pruebas:** RTL.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** Hecha (2026-11-12): «Volver al inicio» solo si el rol tiene inicio propio; «Volver atrás» solo con historial en la aplicación; «Cerrar sesión» para una cuenta sin rol reconocido; contacto con la Secretaría citando el código de referencia.

### FE-T904 — Pruebas de V-09

- **Objetivo:** cubrir contenido y accesibilidad.
- **Depende de:** FE-T903.
- **Módulos:** `src/features/no-habilitado/__tests__/`.
- **Pasos:**
  1. Render por motivo.
  2. Navegación.
  3. axe.
- **Criterios de aceptación:** cobertura ≥ 80%.
- **Pruebas:** `npm run test`.
- **Evidencia:** reporte.
- **Estimación:** S. **Prioridad:** Must. **Estado:** Hecha (2026-11-12): `motivos.test.ts`, `NoHabilitadoPage.test.tsx` (+6, se conservan las 6 previas) y `guards.test.tsx` (+1): CA-V09-01…04, axe y lista blanca. Suite 406/406; 4 mutaciones detectadas.

---

## 15. Fase transversal

### FE-T1001 — Normalización global de errores y ErrorBoundary

- **Objetivo:** unificar el manejo de errores.
- **Depende de:** FE-T013, FE-T021.
- **Módulos:** `src/api/errors.ts`, `ErrorBoundary.tsx`.
- **Pasos:**
  1. Revisar mapeo de todos los códigos.
  2. Mensajes consistentes.
  3. Aislar errores por sección.
- **Criterios de aceptación:** no hay mensajes duplicados ni detalles internos.
- **Pruebas:** unitarias/integración.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** Pendiente.

### FE-T1002 — Auditoría de accesibilidad

- **Objetivo:** cumplir WCAG 2.1 AA.
- **Depende de:** FE-T101…FE-T904.
- **Módulos:** todas las vistas.
- **Pasos:**
  1. axe en cada vista.
  2. Navegación por teclado.
  3. Contraste y foco.
  4. Corregir hallazgos.
- **Criterios de aceptación:** sin errores críticos; informe de auditoría.
- **Pruebas:** `vitest-axe` + revisión manual.
- **Evidencia:** informe.
- **Estimación:** M. **Prioridad:** Must. **Estado:** Pendiente.

### FE-T1003 — Auditoría responsive

- **Objetivo:** cumplir breakpoints.
- **Depende de:** FE-T101…FE-T904.
- **Módulos:** todas las vistas.
- **Pasos:**
  1. Revisar 320/480/768/1024/1440.
  2. Corregir overflow y tablas.
  3. Capturas.
- **Criterios de aceptación:** sin scroll horizontal; usabilidad móvil.
- **Pruebas:** revisión visual.
- **Evidencia:** capturas.
- **Estimación:** M. **Prioridad:** Must. **Estado:** Pendiente.

### FE-T1004 — Modo demostración

- **Objetivo:** cumplir P-01.
- **Depende de:** FE-T008.
- **Módulos:** `DemoBanner.tsx`, `env.ts`.
- **Pasos:**
  1. Banner visible con `VITE_DEMO_MODE`.
  2. Texto claro de entorno.
  3. No alterar datos.
- **Criterios de aceptación:** el modo es evidente y no intrusivo.
- **Pruebas:** RTL.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Should. **Estado:** Pendiente.

### FE-T1005 — Endurecimiento de seguridad

- **Objetivo:** reducir riesgos XSS/CSRF/token.
- **Depende de:** FE-T013, FE-T016.
- **Módulos:** `logger.ts`, `client.ts`, configuración CSP.
- **Pasos:**
  1. Prohibir `dangerouslySetInnerHTML`.
  2. Revisar logs.
  3. Añadir CSP en despliegue.
  4. `npm audit`.
- **Criterios de aceptación:** sin tokens/PII en logs; sin HTML inseguro.
- **Pruebas:** revisión y `npm audit`.
- **Evidencia:** informe.
- **Estimación:** S. **Prioridad:** Must. **Estado:** Pendiente.

### FE-T1006 — Rendimiento y code splitting

- **Objetivo:** cumplir RNFF-004.
- **Depende de:** FE-T009.
- **Módulos:** `router.tsx`, `vite.config.ts`.
- **Pasos:**
  1. Verificar lazy loading.
  2. Medir bundle.
  3. Optimizar imports.
  4. Lighthouse.
- **Criterios de aceptación:** bundle inicial < 300 KB gzip; LCP < 2.5 s.
- **Pruebas:** build + Lighthouse.
- **Evidencia:** reporte.
- **Estimación:** S. **Prioridad:** Should. **Estado:** Pendiente.

### FE-T1007 — Centro de notificaciones

- **Objetivo:** centralizar notificaciones en el layout.
- **Depende de:** FE-T203.
- **Módulos:** `Header.tsx`, `NotificacionesPanel.tsx`.
- **Pasos:**
  1. Icono con contador.
  2. Panel con lista.
  3. Marcar leída.
- **Criterios de aceptación:** accesible y consistente.
- **Pruebas:** RTL.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Should. **Estado:** Pendiente.

### FE-T1008 — Estrategia de invalidación y refetch

- **Objetivo:** documentar y verificar invalidaciones.
- **Depende de:** FE-T410, FE-T809.
- **Módulos:** `queryKeys.ts`, `queryClient.ts`.
- **Pasos:**
  1. Revisar matriz de invalidación.
  2. Evitar refetch en bucle.
  3. Pruebas de consistencia.
- **Criterios de aceptación:** datos consistentes tras mutaciones.
- **Pruebas:** integración.
- **Evidencia:** pruebas.
- **Estimación:** S. **Prioridad:** Must. **Estado:** Pendiente.

### FE-T1009 — Documentar limitaciones en la app

- **Objetivo:** hacer visibles las dependencias BE.
- **Depende de:** FE-T901.
- **Módulos:** `NoHabilitadoPage.tsx`, `README.md`.
- **Pasos:**
  1. Catálogo de limitaciones con BE-xx.
  2. Enlaces contextuales.
  3. Texto sin tecnicismos.
- **Criterios de aceptación:** cada limitación tiene explicación y alternativa.
- **Pruebas:** revisión.
- **Evidencia:** documento.
- **Estimación:** S. **Prioridad:** Should. **Estado:** Pendiente.

### FE-T1010 — Checklist de QA manual

- **Objetivo:** validar flujos críticos antes de entrega.
- **Depende de:** FE-T1001…FE-T1009.
- **Módulos:** `docs/qa-frontend.md`.
- **Pasos:**
  1. Matriz de flujos por rol.
  2. Casos de error.
  3. Accesibilidad y responsive.
  4. Evidencia.
- **Criterios de aceptación:** checklist ejecutado y firmado.
- **Pruebas:** manual.
- **Evidencia:** checklist.
- **Estimación:** M. **Prioridad:** Must. **Estado:** Pendiente.

---

## 16. Fase de calidad

### FE-T1101 — Cobertura de pruebas ≥ 80%

- **Objetivo:** alcanzar la meta de cobertura.
- **Depende de:** FE-T101…FE-T1010.
- **Módulos:** `vitest.config.ts`, pruebas.
- **Pasos:**
  1. Medir cobertura.
  2. Cubrir brechas críticas.
  3. Excluir mocks/config.
- **Criterios de aceptación:** cobertura global ≥ 80%; auth y expediente ≥ 85%.
- **Pruebas:** `npm run test:coverage`.
- **Evidencia:** reporte.
- **Estimación:** M. **Prioridad:** Must. **Estado:** Pendiente.

### FE-T1102 — Lint y typecheck finales

- **Objetivo:** entregar sin errores estáticos.
- **Depende de:** FE-T1101.
- **Módulos:** todo el proyecto.
- **Pasos:**
  1. `npm run lint`.
  2. `npm run typecheck`.
  3. Corregir.
- **Criterios de aceptación:** ambos comandos pasan sin errores.
- **Pruebas:** comandos.
- **Evidencia:** salida.
- **Estimación:** S. **Prioridad:** Must. **Estado:** Pendiente.

### FE-T1103 — Pruebas de contrato con fixtures

- **Objetivo:** verificar formas de request/response.
- **Depende de:** FE-T013.
- **Módulos:** `src/mocks/fixtures.ts`, `src/api/__tests__/contract.test.ts`.
- **Pasos:**
  1. Fixtures por endpoint.
  2. Validar con Zod o tipos.
  3. Casos de discrepancia documentados.
- **Criterios de aceptación:** los fixtures cumplen los tipos y el comportamiento real.
- **Pruebas:** `npm run test`.
- **Evidencia:** reporte.
- **Estimación:** M. **Prioridad:** Should. **Estado:** Pendiente.

### FE-T1104 — E2E opcional

- **Objetivo:** validar flujo crítico completo.
- **Depende de:** FE-T1010.
- **Módulos:** `e2e/`.
- **Pasos:**
  1. Login → crear → enviar → bandeja → observar.
  2. Datos de prueba.
- **Criterios de aceptación:** flujo pasa en CI local.
- **Pruebas:** Playwright.
- **Evidencia:** reporte.
- **Estimación:** L. **Prioridad:** Could. **Estado:** Pendiente.

### FE-T1105 — Revisión final y trazabilidad

- **Objetivo:** verificar que todo requisito tiene tarea y prueba.
- **Depende de:** FE-T1101…FE-T1103.
- **Módulos:** `specs/003-frontend-titulacion/`.
- **Pasos:**
  1. Revisar matriz de trazabilidad.
  2. Verificar criterios de aceptación.
  3. Confirmar que no se modificó backend/documentos.
- **Criterios de aceptación:** matriz completa; sin cambios prohibidos.
- **Pruebas:** revisión.
- **Evidencia:** informe de cierre.
- **Estimación:** S. **Prioridad:** Must. **Estado:** Pendiente.

---

## 17. Matriz de trazabilidad vista ↔ tareas

| Vista | Tareas |
|-------|--------|
| V-01 | FE-T011…FE-T017, FE-T101…FE-T104 |
| V-02 | FE-T201…FE-T206 |
| V-03 | FE-T301…FE-T306 (DEC-14 corregida: sin selector ni elegibilidad **mientras no se aprueben** validación RRA-UNL + BE-06 + decisión humana; ver `specify.md` §9.2) |
| V-04 | FE-T401…FE-T411 |
| V-05 | FE-T501…FE-T506 |
| V-06 | FE-T601…FE-T605 |
| V-07 | FE-T701…FE-T706 |
| V-08 | FE-T801…FE-T810 |
| V-09 | FE-T901…FE-T904 (también aplica a 403 con `ForbiddenState`, FE-T1212) |
| Transversal (bases) | FE-T001…FE-T010, FE-T019…FE-T028 |
| Transversal (estados de error F2.5) | FE-T1210…FE-T1214 |
| Transversal | FE-T1001…FE-T1010 |
| Calidad | FE-T1101…FE-T1105 |

> Nota de trazabilidad del prototipo B: `401.html` → FE-T1212 (aviso + `/login`), `403.html` → FE-T1212/V-09, `404.html` → FE-T1211/`NotFoundPage`, `409.html`/`412.html`/`428.html` → FE-T1213 (**Bloqueada**, BE-11), `500.html`/`503.html` → FE-T1212/`ErrorState`. Todos son referencia visual no normativa (DEC-11); la correspondencia funcional está en `especificaciones/08_UI_ERROR_STATES_SPEC.md` y `specify.md` §9.3.

---

### 17.1 Requisitos por tarea

> Cada tarea hereda los requisitos de su vista; esta tabla fija el vínculo explícito para la revisión de trazabilidad. `N/A` indica tarea de infraestructura sin requisito funcional directo.

| Tarea | Requisito(s) |
|-------|--------------|
| FE-T001…FE-T010 | N/A (infraestructura) |
| FE-T011 | RFF-001, RFF-103 |
| FE-T012 | RFF-001, RFF-103, RFF-106 |
| FE-T013 | RFF-001, RFF-002, RFF-014, RFF-020 |
| FE-T014 | RFF-001, RFF-102 |
| FE-T015 | RFF-002, RFF-014 |
| FE-T016 | RFF-104, RFF-106 |
| FE-T017 | RFF-001, RFF-002, RFF-014, RFF-101…107 |
| FE-T019 | RFF-005, RFF-011 |
| FE-T020 | RFF-004, RFF-011 |
| FE-T021 | RFF-004, RFF-017 |
| FE-T022 | RFF-009, RFF-012 |
| FE-T023 | RFF-009 |
| FE-T024 | RFF-011, RFF-016 |
| FE-T025 | RFF-410 |
| FE-T026 | RFF-006, RFF-011 |
| FE-T027 | RFF-004, RFF-011 |
| FE-T028 | RFF-011, RFF-012 |
| FE-T101 | RFF-101, RFF-105 |
| FE-T102 | RFF-102, RFF-103, RFF-104 |
| FE-T103 | RFF-105, RFF-107 |
| FE-T104 | RFF-101…107 |
| FE-T201 | RFF-201 |
| FE-T202 | RFF-202 |
| FE-T203 | RFF-203 |
| FE-T204 | RFF-205 |
| FE-T205 | RFF-004, RFF-205 |
| FE-T206 | RFF-201…205 |
| FE-T301 | RFF-301, RFF-302, RFF-306 |
| FE-T302 | RFF-303, RFF-305 |
| FE-T303 | RFF-304 |
| FE-T304 | RFF-018 |
| FE-T305 | RFF-305 |
| FE-T306 | RFF-301…306 |
| FE-T401 | RFF-401, RFF-410 |
| FE-T402 | RFF-401, RFF-402 |
| FE-T403 | RFF-403, RFF-404 |
| FE-T404 | RFF-405 |
| FE-T405 | RFF-406 |
| FE-T406 | RFF-407 |
| FE-T407 | RFF-408 |
| FE-T408 | RFF-409 |
| FE-T409 | RFF-004, RFF-016 |
| FE-T410 | RFF-411 |
| FE-T411 | RFF-401…411 |
| FE-T501 | RFF-501, RFF-506 |
| FE-T502 | RFF-502 |
| FE-T503 | RFF-503, RFF-504 |
| FE-T504 | RFF-409 |
| FE-T505 | RFF-506 |
| FE-T506 | RFF-501…506 |
| FE-T601 | RFF-601 |
| FE-T602 | RFF-602 |
| FE-T603 | RFF-603 |
| FE-T604 | RFF-604, RFF-605 |
| FE-T605 | RFF-601…605 |
| FE-T701 | RFF-701 |
| FE-T702 | RFF-702 |
| FE-T703 | RFF-703 |
| FE-T704 | RFF-705 |
| FE-T705 | RFF-704 |
| FE-T706 | RFF-701…706 |
| FE-T801 | RFF-801 |
| FE-T802 | RFF-802 |
| FE-T803 | RFF-803 |
| FE-T804 | RFF-804 |
| FE-T805 | RFF-805 |
| FE-T806 | RFF-806 |
| FE-T807 | RFF-807 |
| FE-T808 | RFF-808 |
| FE-T809 | RFF-809 |
| FE-T810 | RFF-801…809 |
| FE-T901 | RFF-901 |
| FE-T902 | RFF-902, RFF-904 |
| FE-T903 | RFF-903 |
| FE-T904 | RFF-901…904 |
| FE-T1001 | RFF-004, RFF-017 |
| FE-T1002 | RFF-011 |
| FE-T1003 | RFF-012 |
| FE-T1004 | RFF-010 |
| FE-T1005 | RFF-020 |
| FE-T1006 | RNFF-004 |
| FE-T1007 | RFF-008 |
| FE-T1008 | RFF-004, RFF-411, RFF-809 |
| FE-T1009 | RFF-019 |
| FE-T1010 | Todos los RFF aplicables |
| FE-T1101 | RNFF-007 |
| FE-T1102 | RNFF-008 |
| FE-T1103 | RNFF-013 |
| FE-T1104 | RNFF-007 |
| FE-T1105 | Todos los RFF aplicables |
| FE-T1210 | N/A (higiene; soporta RFF-011) |
| FE-T1211 | RFF-004, RFF-017, RNFF-001 |
| FE-T1212 | RFF-004, RFF-013, RFF-014, RFF-017 |
| FE-T1213 | RFF-005 (escenario propuesto; condicionado a BE-11) |
| FE-T1214 | N/A (asset opcional, pendiente de decisión) |

---

## 18. Orden de ejecución recomendado

0. **Primer lote (cierre de F0, 2026-11-04): completado.** D-FE-01 resuelto y FE-T008 cerrada (capturas 320/768/1440 entregadas) → FE-T1210 (higiene plantilla) cerrada → sin ajustes adicionales necesarios en FE-T007/FE-T008 → FE-T010 (README) cerrada → suite completa re-ejecutada en verde (24/24) como evidencia final de F0.
1. **F0:** FE-T001 → FE-T010 — **Hechas** (ver §3). FE-T1210 también Hecha.
2. **F1:** FE-T011 → FE-T017.
3. **F2:** FE-T019 → FE-T028.
4. **F2.5:** FE-T1211 → FE-T1212 → FE-T1214 — **Hechas** (2026-11-05; FE-T1210 ya Hecha en el primer lote). FE-T1213 sigue **Bloqueada por BE-11**.
5. **V-01:** FE-T101 → FE-T104 — Hechas (2026-11-05: formulario, integración, errores/accesibilidad y pruebas de login; 22 pruebas nuevas, 226/226 totales).
6. **V-09:** FE-T901 → FE-T904 — Hechas (2026-11-12: motivo, dependencia `BE-xx`, código de referencia y salidas sin bucles; integrada con `RequireRole` y V-07; 12 pruebas nuevas; responsable Dan1el17, implementación centralizada DK-010).
7. **V-03:** FE-T301 → FE-T306 — Hechas (2026-11-05: formulario, integración, errores/protección ante duplicados, borrador local, éxito/redirección y pruebas; V-04 confirmada como stub, sin ampliar su alcance).
8. **V-04:** FE-T401 → FE-T411 — Hechas (2026-11-05: cabecera/timeline, detalle/peticiones, checklist con 403 real, enviar/observar/evaluar/subsanar, descarga, matriz de acciones, invalidación y pruebas; FE-T407 con limitación real severa documentada para ESTUDIANTE —sin `checklist_verification_id` descubrible—, sin modificar el backend; INC-21 documenta discrepancias de código HTTP en observar/evaluar/subsanar).
9. **V-05:** FE-T501 → FE-T506 — Hechas (2026-11-12: lista, solicitar emisión, carga y descarga de PDF, aviso de creación automática y pruebas; 30 pruebas nuevas, 358/358 totales; responsable 7777-C, implementación centralizada DK-010; discrepancias RBAC/servicio en carga y solicitud registradas en `SIAAF-KNOWLEDGE/03-FRONTEND/PLAN_VISTAS_V05_V09.md` §2).
10. **V-06:** FE-T601 → FE-T605 — Hechas (2026-11-12: seguimiento desde el detalle del expediente, estado actual real, descarga vigente y errores; 16 pruebas nuevas, 374/374; responsable JuanCalopinoo, implementación centralizada DK-010). **BE-02 sigue sin autorizar**: sin detalle, historial ni versiones de la petición.
11. **V-02:** FE-T201 → FE-T206 — Hechas (2026-11-05: dashboard del estudiante completo; FE-T203 con desviación de contrato documentada —notificaciones sin paginar en el backend real—; FE-T204 con alcance acotado a expedientes visitados, el registro al crear queda pendiente de V-03).
12. **V-07:** FE-T701 → FE-T706 — Hechas (2026-11-12: bandeja real paginada, filtros de página, vacíos por rol, plazos locales y navegación a V-08 con precarga; 20 pruebas nuevas; responsable Dan1el17, implementación centralizada DK-010). **BE-09** sigue sin autorizar.
13. **V-08:** FE-T801 → FE-T810 — Hechas (2026-11-12: V-08a, detalle, checklist, observar, iniciar verificación, descargas, solo lectura e invalidación, responsable JJOC3S; V-08b, informe APTO y declaratoria, responsable R0yalCode; implementación centralizada DK-010). Dependencias: sin GET ni descarga de informes y declaratorias (nueva, sin ID), BE-07.
14. **Transversal:** FE-T1001 → FE-T1010.
15. **Calidad:** FE-T1101 → FE-T1105.

> Las vistas pueden paralelizarse por feature una vez completados F0–F2.5 y V-01. Las dependencias de backend (`BE-xx`, incluida BE-11) no bloquean la UI salvo FE-T1213: se degrada con V-09 o estados vacíos.

---

## 19. Definición de hecha (DoD)

Una tarea está hecha cuando:

1. Cumple sus criterios de aceptación.
2. Tiene pruebas que pasan.
3. `npm run lint`, `npm run typecheck` y `npm run test` pasan.
4. Es accesible (teclado, foco, etiquetas, contraste).
5. Es responsive en 320/768/1024/1440.
6. No introduce datos simulados en producción.
7. No registra tokens/PII.
8. No modifica backend, OpenAPI, constitución ni documentos existentes.
9. Actualiza la documentación si cambia una convención.
10. La trazabilidad a `RFF-*`, `CA-*` y endpoint está registrada.

---

## 20. Referencias

- `clarify.md` — decisiones y bloqueos.
- `specify.md` — requisitos y vistas.
- `plan.md` — arquitectura y stack.
- `../../backend/openapi.yaml` — contrato.
- `../../diseno-ui/ui/titulacion-v2/especificaciones/` — referencia visual no normativa.
