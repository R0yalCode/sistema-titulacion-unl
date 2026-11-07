# Plan Técnico — Frontend de Titulación (SGT-SIAAF)

**Feature ID:** `003-frontend-titulacion`
**Documento:** `plan.md`
**Versión:** 1.1.0
**Fecha:** 2026-11-04
**Estado:** Plan aprobado. F0 está mayormente implementado con evidencia del 2026-11-04 (lint ✅, typecheck ✅, build ✅ 12 chunks lazy, pruebas 23/24; ver `clarify.md` CL-21 y §2.bis). Este ajuste documenta las desviaciones reales del andamiaje y los estados de error aprobados (F2.5); no cambia las decisiones de arquitectura.
**Naturaleza:** Documento de arquitectura y planificación. Los fragmentos de configuración y las firmas de tipos son ilustrativos; no constituyen implementación.

---

## 1. Objetivo

Definir la arquitectura, el stack, la estructura de carpetas, las convenciones y la estrategia de implementación del frontend de titulación, de forma que las tareas de `tasks.md` puedan ejecutarse sin ambigüedad y sin modificar el backend.

El plan respeta:

- **P-01** (simulación): la UI no simula datos ni estados no soportados.
- **P-02** (autoridad humana): las decisiones sensibles requieren confirmación y quedan en el backend.
- **P-06** (mínimo privilegio): guardas de UI y autorización server-side.
- **P-07** (defensa en profundidad): validación cliente + servidor.
- **P-08** (trazabilidad): acciones y errores con contexto.
- **P-16** (accesibilidad): WCAG 2.1 AA.
- **P-17** (incremental): entrega por fases, sin romper lo existente.

---

## 2. Stack propuesto

> **No se instala nada en esta etapa.** Las versiones son objetivos; se fijan al iniciar la implementación autorizada.

| Capa | Tecnología | Justificación | Obligatoria |
|------|------------|---------------|-------------|
| Build | **Vite 5+** | Rápido, SPA, variables `VITE_*`, proxy de desarrollo. | Sí |
| UI | **React 18+** | Decisión del usuario. | Sí |
| Lenguaje | **TypeScript 5+** (`strict`) | Tipado de contratos y refactors seguros. | Sí |
| Rutas | **React Router 6+** | Rutas anidadas, lazy loading, guardas. | Sí |
| Server state | **TanStack Query 5+** | Caché, reintentos, invalidación, estados de carga/error. | Sí |
| Formularios | **React Hook Form 7+** | Formularios performantes y accesibles. | Recomendada |
| Validación | **Zod 3+** | Esquemas tipados, mensajes en español, reutilizables. | Recomendada |
| HTTP | **`fetch` nativo + wrapper tipado** | Menos dependencias; control de errores y auth. | Sí |
| Estilos | **CSS Modules + tokens CSS** | Aislamiento, sin framework pesado, fiel al diseño. | Sí |
| Fechas | **`Intl.DateTimeFormat`** | Sin dependencia; locale `es-EC`. | Sí |
| Pruebas unitarias | **Vitest + React Testing Library** | Estándar con Vite. | Sí |
| Pruebas de red | **MSW 2+** | Mock de API a nivel de red; contrato realista. | Sí |
| A11y en pruebas | **`vitest-axe`** (o `axe-core`) | Verificación automatizada. | Recomendada |
| Lint/format | **ESLint + Prettier + typescript-eslint** | Consistencia y detección temprana. | Sí |
| E2E | **Playwright** (opcional) | Flujos críticos; no bloquea el MVP. | Opcional |

**No se usará:** Next.js, Redux, Axios, Moment.js, Bootstrap, Material UI, Tailwind (salvo decisión posterior), ni librerías de gráficos.

### 2.bis Versiones reales instaladas en F0 (evidencia 2026-11-04)

La implementación iniciada ya instaló (derivadas de la instrucción inicial, dentro de las oportunidades de DEC-09 para el andamio F0 existente): React **19.3**, React DOM 19.3, React Router DOM **7.18**, TanStack Query **5.105**, TypeScript **5.9**, Vite **8.3**, Vitest **5.1** (+coverage-v8), MSW **3.0**, ESLint 9 (flat config) + typescript-eslint + jsx-a11y + react-hooks, Testing Library 16 + jest-dom 7 + user-event, jsdom 30, `vitest-axe` 0.1 (con workaround documentado en `setup.ts` por bug de empaquetado), Prettier 3.9. React Hook Form y Zod **no están instalados** aún: FE-T019 decidir si los usa al implementar F2 (no instalan en esta etapa documental).

Configuración real: `tsconfig.json` con referencias a `tsconfig.app.json`/`tsconfig.node.json` (strict + `noUncheckedIndexedAccess` + `noImplicitOverride`), alias `@/ → src/`, `vitest.config.ts` (jsdom, globals, setupFiles, css), `eslint.config.js` flat con `no-console: error` (excepto `src/lib/logger.ts`) y `no-restricted-imports` que prohíbe imports profundos `@/features/*`.

### 2.ter Desviaciones corregidas en el cierre de F0 (evidencia 2026-11-04)

1. `src/index.css` (tema demo de la plantilla Vite) → **eliminado**; import retirado de `main.tsx` (FE-T1210, D-FE-02).
2. `index.html` con `lang="en"` y `<title>frontend` → **corregido** a `lang="es"` + `<title>SGT-SIAAF</title>` (FE-T1210, D-FE-04).
3. `frontend/README.md` era la plantilla de Vite → **reemplazado** por documentación real (FE-T010, D-FE-03).
4. `AppLayout.test.tsx` tenía 1 test fallido → **resuelto**: causa raíz = botón móvil-only (`@media (max-width:768px)`) evaluado en el viewport desktop fijo de jsdom (sin `window.matchMedia`); nombre accesible de un elemento oculto computa `""` por especificación WAI-ARIA, no por bug de jsdom. Corregido solo en el test (D-FE-01, FE-T008).

---

## 3. Principios de arquitectura

1. **Feature-based:** cada vista/dominio vive en `src/features/<feature>/`.
2. **Separación de capas:** componentes no llaman a `fetch`; usan hooks de `src/api/` o `src/features/*/api.ts`.
3. **Server state ≠ client state:** TanStack Query para datos del servidor; Context para sesión; estado local para formularios/UI.
4. **Tipos primero:** los modelos se derivan del OpenAPI y del código real; se documentan las discrepancias.
5. **Errores normalizados:** un único `ApiError` con `status`, `code`, `message`, `fieldErrors`.
6. **Guardas de UI, no de seguridad:** el backend sigue siendo la autoridad.
7. **Sin datos simulados:** los mocks solo existen en pruebas (`src/mocks/`), nunca en producción.
8. **Accesibilidad por defecto:** HTML semántico, foco, etiquetas y `aria-live`.
9. **Lazy loading por ruta:** reduce el bundle inicial.
10. **Trazabilidad:** cada mutación invalida las queries afectadas y registra un evento seguro.

---

## 4. Estructura de carpetas

```text
frontend/
├── index.html
├── package.json
├── tsconfig.json
├── tsconfig.app.json      ← real (F0); referencias de proyecto TS
├── tsconfig.node.json
├── vite.config.ts
├── vitest.config.ts       ← real (F0)
├── eslint.config.js       ← real (F0, flat config; sustituye a .eslintrc.cjs)
├── .prettierrc
├── .env.example
├── README.md              ← FE-T010 pendiente (hoy es plantilla)
├── public/
│   ├── favicon.svg
│   ├── icons.svg
│   └── (assets de errores, si FE-T1214 se aprueba; NO copiar HTML/CSS/JS de los prototipos)
└── src/
    ├── main.tsx
    ├── app/
    │   ├── App.tsx
    │   ├── router.tsx
    │   ├── providers.tsx
    │   ├── NotFoundPage.tsx          ← real (F0); se reestiliza con el kit de errores (FE-T1211)
    │   └── errors/                   ← F2.5: páginas de error globales 404/500/503 + estados 401/403 reutilizando componentes
    │       └── (401 no es página: redirect a /login con aviso; 403 usa ForbiddenState + V-09)
    ├── api/
    │   ├── client.ts
    │   ├── errors.ts
    │   ├── queryKeys.ts
    │   ├── endpoints/
    │   │   ├── auth.ts
    │   │   ├── expedientes.ts
    │   │   ├── peticiones.ts
    │   │   ├── checklist.ts
    │   │   ├── informes.ts
    │   │   ├── declaratorias.ts
    │   │   └── notificaciones.ts
    │   └── types/
    │       ├── api.ts
    │       ├── models.ts
    │       └── payloads.ts
    ├── auth/
    │   ├── AuthContext.tsx
    │   ├── useAuth.ts
    │   ├── jwt.ts
    │   ├── storage.ts
    │   └── guards.tsx
    ├── assets/            ← real (F0)
    ├── components/
    │   ├── ui/
    │   │   ├── Button.tsx
    │   │   ├── Input.tsx
    │   │   ├── Select.tsx
    │   │   ├── Textarea.tsx
    │   │   ├── Badge.tsx
    │   │   ├── Card.tsx
    │   │   ├── Table.tsx
    │   │   ├── Modal.tsx
    │   │   ├── Alert.tsx
    │   │   ├── InlineAlert.tsx        ← F2.5: para escenarios propuestos 409/412/428 (Solo si BE-11; FE-T1213 Bloqueada)
    │   │   ├── Spinner.tsx
    │   │   ├── EmptyState.tsx
    │   │   ├── ErrorState.tsx
    │   │   ├── NotFoundState.tsx      ← ya especificado en FE-T021
    │   │   ├── ForbiddenState.tsx     ← ya especificado en FE-T021
    │   │   ├── Pagination.tsx
    │   │   ├── Tabs.tsx
    │   │   ├── Timeline.tsx
    │   │   └── FileUpload.tsx
    │   ├── layout/
    │   │   ├── AppLayout.tsx
    │   │   ├── Header.tsx
    │   │   ├── Sidebar.tsx
    │   │   ├── SkipLink.tsx
    │   │   └── DemoBanner.tsx
    │   └── feedback/
    │       ├── ErrorBoundary.tsx
    │       └── ToastProvider.tsx
    ├── features/
    │   ├── auth/
    │   │   └── LoginPage.tsx
    │   ├── dashboard/
    │   │   └── StudentDashboardPage.tsx
    │   ├── solicitud/
    │   │   ├── NuevaSolicitudPage.tsx
    │   │   └── NuevaSolicitudForm.tsx
    │   ├── expediente/
    │   │   ├── ExpedientePage.tsx
    │   │   ├── ExpedienteHeader.tsx
    │   │   ├── PeticionesList.tsx
    │   │   ├── ChecklistPanel.tsx
    │   │   ├── ChecklistItem.tsx
    │   │   ├── EnviarExpedienteDialog.tsx
    │   │   ├── ObservarExpedienteDialog.tsx
    │   │   └── SubsanarDialog.tsx
    │   ├── peticiones/
    │   │   ├── PeticionesPage.tsx
    │   │   ├── SolicitarEmisionButton.tsx
    │   │   ├── CargarDocumentoDialog.tsx
    │   │   └── SeguimientoPeticionPage.tsx
    │   ├── bandeja/
    │   │   ├── BandejaPage.tsx
    │   │   ├── BandejaTable.tsx
    │   │   ├── BandejaFilters.tsx
    │   │   └── DetalleFuncionarioPage.tsx
    │   ├── informes/
    │   │   ├── EmitirInformeDialog.tsx
    │   │   └── DeclararAptitudDialog.tsx
    │   └── no-habilitado/
    │       └── NoHabilitadoPage.tsx
    ├── lib/
    │   ├── format.ts
    │   ├── validation.ts
    │   ├── files.ts
    │   ├── storage.ts
    │   ├── queryClient.ts
    │   ├── env.ts
    │   └── logger.ts
    ├── styles/
    │   ├── tokens.css
    │   ├── global.css
    │   └── utilities.css
    ├── types/
    │   └── global.d.ts
    ├── mocks/
    │   ├── browser.ts
    │   ├── handlers.ts
    │   └── fixtures.ts
    └── test/
        ├── setup.ts
        ├── renderWithProviders.tsx
        └── server.ts
```

Notas de la auditoría (2026-11-04) sobre la estructura real vs. esta propuesta: la real ≈ coincide (features, auth, api, components/{feedback,layout,ui}, lib, mocks, styles, test, types, assets) con extras (`src/features/index.ts`, `src/styles/TokensShowcase.test.tsx`, `src/app/NotFoundPage.tsx`) y faltantes (`features/informes/`, `mocks/browser.ts`/`fixtures.ts`, `lib/format|validation|files|storage.ts`, API client). `src/index.css` (residuo de plantilla) se elimina en FE-T1210. Los prototipos A/B se conservan en sus carpetas de raíz del repositorio como material de referencia; nunca se mueven ni se copian a `frontend/src/`.

**Regla:** `src/mocks/` solo se importa en pruebas o en desarrollo con `VITE_USE_MOCKS=true`. Nunca en producción.

---

## 5. Configuración y variables de entorno

`.env.example`:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_DEMO_MODE=false
VITE_USE_MOCKS=false
VITE_APP_NAME=SGT-SIAAF
```

| Variable | Uso | Obligatoria |
|----------|-----|-------------|
| `VITE_API_BASE_URL` | Origen/base de la API. Sin barra final. | Sí |
| `VITE_DEMO_MODE` | Muestra `DemoBanner` (P-01). | No |
| `VITE_USE_MOCKS` | Activa MSW en desarrollo. **Nunca en producción.** | No |
| `VITE_APP_NAME` | Título visible. | No |

**Reglas:**
- No hay secretos en el frontend. Todo `VITE_*` es público.
- `VITE_API_BASE_URL` se valida al arrancar; si falta, la app muestra un error de configuración.
- En desarrollo, `vite.config.ts` puede usar `server.proxy` para evitar CORS (BE-08 en producción).

---

## 6. Autenticación y sesión

### 6.1 Flujo

1. `LoginPage` envía `POST /api/v1/auth/token/`.
2. Se valida la respuesta (`access` string no vacío).
3. Se decodifica el `access` (payload base64url) para leer `cedula` y `roles`.
4. Se guarda `access` en `sessionStorage` (clave `sgt.access`).
5. Se guarda en memoria el usuario (`cedula`, `roles`) en `AuthContext`.
6. Se redirige según el rol (ver `specify.md` §6).
7. Cada petición añade `Authorization: Bearer <access>`.
8. Ante 401: limpiar sesión, redirigir a `/login` con aviso.

### 6.2 Almacenamiento

- **`access`:** `sessionStorage` (se borra al cerrar la pestaña).
- **`refresh`:** **no se persiste**. Se descarta; no hay endpoint de refresh (BE-03). Si en el futuro se habilita, se usará rotación y cookies `httpOnly` (requiere backend).
- **Riesgo documentado:** `sessionStorage` es accesible por JS; mitigar con CSP, sanitización y auditoría de dependencias (RSK-FE-02).

### 6.3 Guardas

| Guarda | Comportamiento |
|--------|----------------|
| `RequireAuth` | Sin sesión → `/login` con `returnTo`. |
| `RequireRole` | Rol no incluido → `/no-habilitado`. |
| `RedirectIfAuthenticated` | Con sesión → inicio por rol. |
| `RequireScope` | No aplica en cliente; el backend decide. La UI solo oculta acciones. |

### 6.4 Expiración

- No hay refresh. Al recibir 401, se muestra "Su sesión expiró. Inicie sesión nuevamente."
- Se conserva el borrador de formulario en `sessionStorage` (sin datos sensibles) para recuperarlo tras el login.
- No se reintenta automáticamente el 401.

### 6.5 Cierre de sesión

- Botón "Cerrar sesión" → confirmación → limpiar `sessionStorage`, `queryClient.clear()`, redirigir a `/login`.
- No hay llamada al backend (no existe endpoint de logout; BE-03).

---

## 7. Cliente HTTP

### 7.1 Responsabilidades

- Construir URL con `VITE_API_BASE_URL`.
- Añadir `Authorization` si hay sesión.
- Serializar JSON o `FormData` según corresponda.
- Parsear respuestas (JSON, blob, vacío).
- Normalizar errores a `ApiError`.
- Manejar 401 globalmente.
- Aplicar timeout con `AbortController` (por defecto 30 s; descargas 60 s).
- No registrar tokens ni cuerpos sensibles.

### 7.2 `ApiError`

```ts
type ApiError = {
  status: number;
  code: string;
  message: string;
  fieldErrors?: Record<string, string[]>;
  isNetworkError: boolean;
  isTimeout: boolean;
  raw?: unknown;
};
```

Mapeo de errores DRF:
- `{ detail: string }` → `message`.
- `{ non_field_errors: string[] }` → `message`.
- `{ campo: string[] }` → `fieldErrors`.
- HTML/inesperado → mensaje genérico; no mostrar HTML.

### 7.3 Endpoints tipados

Cada archivo de `src/api/endpoints/` expone funciones tipadas:

```ts
// auth.ts
login(payload: LoginRequest): Promise<TokenPair>
// expedientes.ts
crearExpediente(payload: CrearExpedienteRequest): Promise<Expediente>
getExpediente(id: string): Promise<ExpedienteDetalle>
enviarExpediente(id: string): Promise<Expediente>
observarExpediente(id: string, payload: ObservacionRequest): Promise<Observacion>
getBandeja(params: BandejaParams): Promise<Paginated<BandejaExpediente>>
getChecklist(expedienteId: string): Promise<ChecklistItem[]>
// peticiones.ts
solicitarEmision(peticionId: string): Promise<Peticion>
cargarDocumento(peticionId: string, archivo: File): Promise<DocumentoEntregado>
descargarDocumento(peticionId: string, version?: number): Promise<Blob>
// checklist.ts
evaluarChecklist(id: string, payload: EvaluacionRequest): Promise<ChecklistItem>
subsanarChecklist(id: string, archivo: File): Promise<ChecklistItem>
// informes.ts
emitirInforme(payload: InformeRequest): Promise<Informe>
// declaratorias.ts
declararAptitud(payload: DeclaratoriaRequest): Promise<Declaratoria>
// notificaciones.ts
getNotificaciones(params): Promise<Paginated<Notificacion>>
marcarLeida(id: string): Promise<Notificacion>
```

> Los tipos se basan en el **comportamiento real** (serializers/views), no solo en el OpenAPI. Las discrepancias se documentan en `clarify.md` (INC-05, INC-06).

### 7.4 Descargas

- `fetch` con `Authorization`.
- `response.blob()`.
- Leer `Content-Disposition` para el nombre; fallback `documento-{version}.pdf`.
- Crear `URL.createObjectURL`, `<a download>`, revocar después.
- Manejar 404/403 con mensaje.

### 7.5 Subidas

- `FormData` con `archivo`.
- **No** fijar `Content-Type`; el navegador añade el boundary.
- Validación cliente: extensión `.pdf`, MIME `application/pdf`, tamaño ≤ 10 MB, magic bytes `%PDF-` (lectura de los primeros 5 bytes).
- Mostrar progreso (si se usa `XMLHttpRequest`) o estado indeterminado (con `fetch`).
- Reintento manual; no automático para evitar duplicados.

---

## 8. Server state (TanStack Query)

### 8.1 Configuración

```ts
new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: (failureCount, error) =>
        error.status >= 500 && failureCount < 2,
      refetchOnWindowFocus: false,
    },
    mutations: { retry: 0 },
  },
});
```

### 8.2 Query keys

```ts
export const queryKeys = {
  me: ['me'] as const,
  bandeja: (params: BandejaParams) => ['bandeja', params] as const,
  expediente: (id: string) => ['expediente', id] as const,
  checklist: (id: string) => ['checklist', id] as const,
  notificaciones: (params) => ['notificaciones', params] as const,
  peticion: (expedienteId: string, peticionId: string) =>
    ['expediente', expedienteId, 'peticion', peticionId] as const,
};
```

### 8.3 Invalidación

| Mutación | Invalida |
|----------|----------|
| Crear expediente | `bandeja`, `expediente(nuevoId)` |
| Enviar expediente | `expediente(id)`, `bandeja` |
| Observar expediente | `expediente(id)`, `checklist(id)`, `bandeja` |
| Evaluar checklist | `checklist(id)`, `expediente(id)` |
| Subsanar checklist | `checklist(id)`, `expediente(id)` |
| Solicitar emisión | `expediente(id)` |
| Cargar documento | `expediente(id)`, `peticion(...)` |
| Emitir informe | `expediente(id)`, `bandeja` |
| Declarar aptitud | `expediente(id)`, `bandeja` |
| Marcar notificación | `notificaciones` |

### 8.4 Estados

Cada query expone `isLoading`, `isError`, `error`, `data`, `isFetching`. Los componentes usan `<LoadingState>`, `<ErrorState>`, `<EmptyState>`.

---

## 9. Formularios y validación

- **React Hook Form** + **Zod** (recomendado) o formularios controlados con validadores puros.
- Esquemas en `src/lib/validation.ts` o junto a cada feature.
- Mensajes en español, claros y accionables.
- Validación al enviar y al perder foco (no en cada tecla, salvo campos simples).
- Errores asociados con `aria-describedby` y `aria-invalid`.
- Foco en el primer campo con error.
- Prevención de doble envío (`isSubmitting`).
- Confirmación en acciones sensibles.
- Borradores en `sessionStorage` solo para V-03 y V-05 (sin datos sensibles).

---

## 10. Sistema de UI

### 10.1 Tokens

Tomar de `especificaciones/01_UI_DESIGN_SYSTEM.md` (referencia no normativa):

- Colores primario/secundario/estado (`success`, `warning`, `danger`, `info`, `neutral`).
- Tipografía, tamaños, pesos.
- Espaciado (escala 4/8 px).
- Radios, sombras, bordes.
- Breakpoints: 320, 480, 768, 1024, 1280, 1440.

Se implementan en `src/styles/tokens.css` como variables CSS. Si el documento visual no define un token, se usa un valor neutro y se marca `TODO` de diseño.

### 10.2 Componentes base

`Button`, `Input`, `Select`, `Textarea`, `Checkbox`, `Radio`, `Badge`, `Card`, `Table`, `Modal`, `Alert`, `Spinner`, `EmptyState`, `ErrorState`, `Pagination`, `Tabs`, `Timeline`, `FileUpload`, `Toast`.

Requisitos:
- Props tipadas.
- Variantes (`primary`, `secondary`, `ghost`, `danger`).
- Tamaños (`sm`, `md`, `lg`).
- Estados (`disabled`, `loading`, `error`).
- Accesibilidad: roles, `aria-*`, foco.
- Sin lógica de negocio.

### 10.3 Layout

- `AppLayout`: skip link, header, sidebar/nav, main, footer.
- Header: nombre de la app, cédula, roles, botón de sesión.
- Sidebar: enlaces por rol; en móvil, menú colapsable.
- `DemoBanner` si `VITE_DEMO_MODE`.
- `ErrorBoundary` global.

### 10.4 Badges de estado

Mapeo:

| Estado | Variante | Texto |
|--------|----------|-------|
| `BORRADOR` | neutral | Borrador |
| `ENVIADA` | info | Enviada |
| `EN_VERIFICACION` | info | En verificación |
| `OBSERVADA` | warning | Observada |
| `INFORME_EMITIDO` | info | Informe emitido |
| `DECLARADA_APTA` | success | Declarada apta |
| `CANCELADA` | danger | Cancelada (no producida) |
| `PENDIENTE` | neutral | Pendiente |
| `SOLICITADO` | info | Solicitado |
| `CARGADO` | info | Cargado |
| `VERIFICADO` | success | Verificado |
| `OBSERVADO` | warning | Observado |
| `LEGALIZADO` | success | Legalizado (no producido) |

---

## 11. Manejo de errores y estados

### 11.1 Matriz de errores

| HTTP | UI | Acción |
|------|----|--------|
| 400 | `Alert` con mensaje y errores de campo | Corregir y reenviar |
| 401 | Aviso de sesión expirada | Limpiar sesión, `/login` |
| 403 | V-09 o panel de limitación | No reintentar; explicar |
| 404 | `NotFoundState` | Volver |
| 409 | ⚠️ **Escenario propuesto**: `InlineAlert` de conflicto (visible en `409.html` del prototipo B) | Requiere BE-11 (ETag/código); mientras: 400 genérico |
| 412 | ⚠️ **Escenario propuesto**: `InlineAlert` "información desactualizada" (`412.html`) | Requiere BE-11; mientras: error genérico con refresco manual |
| 428 | ⚠️ **Escenario propuesto**: `InlineAlert` "versión requerida" (`428.html`) | Requiere BE-11; mientras: error genérico con refresco manual |
| 422 | `Alert` con detalle | Corregir requisitos |
| 429 | `Alert` "Demasiadas solicitudes" | Esperar (no representado en prototipos ni requisitos: **pendiente de definición**, no inventado) |
| 500 | `ErrorState` | Reintentar |
| 502/503/504 | `ErrorState` | Reintentar |
| Red/timeout | `ErrorState` | Reintentar |

**Nota aclaratoria (MOMENTO 2):** que el OpenAPI no declare explícitamente respuestas de error **no significa que el frontend no pueda recibir errores HTTP estándar**: DRF los produce de facto (400/401/403/404/422/500; ver CL-22 en `clarify.md`). La distinción relevante es otra: 409/412/428 requieren comportamiento/contrato específico (BE-11) y, sin él, se degradan a error genérico.

Organización de estados de error (DEC-13): **errores globales** (401/403/404/500/503 — páginas o componentes de app), **errores de formularios** (400/422 inline; 409/412/428 inline solo si BE-11), **estados operativos reutilizables** (`LoadingState`, `EmptyState` —incluida "sin asignación"—, `ErrorState`, `ForbiddenState`, `NotFoundState`, read-only). La referencia visual completa vive en `especificaciones/08_UI_ERROR_STATES_SPEC.md`, y las páginas 404/500/503 del kit de errores (prototipo B) definen el tono visual; no se copia su HTML/CSS/JS.

### 11.2 Reglas

- No mostrar `stack`, HTML ni mensajes internos.
- Un mensaje principal + detalle accionable.
- `aria-live="polite"` para errores de formulario; `assertive` para errores globales.
- Un error de una sección no debe tumbar toda la página (aislar con `ErrorBoundary` por feature cuando sea posible).
- Los errores 403 no revelan la existencia de recursos.

### 11.3 Estados de vista

Componentes:
- `<LoadingState label="Cargando expediente…" />`
- `<EmptyState title="..." description="..." action={...} />`
- `<ErrorState error={...} onRetry={...} />`
- `<NotFoundState />`
- `<ForbiddenState />`

---

## 12. Accesibilidad

- HTML semántico (`main`, `nav`, `header`, `section`, `table`).
- Un solo `h1` por página; jerarquía de encabezados.
- Etiquetas explícitas en todos los campos; sin placeholders como única etiqueta.
- Foco visible; `:focus-visible`.
- Navegación por teclado completa.
- Skip link al contenido.
- Modales con focus trap, `aria-modal`, cierre con `Esc`, retorno de foco.
- Tablas con `<caption>`, `scope`, y vista de tarjetas en móvil.
- Contraste ≥ 4.5:1 (texto normal) y ≥ 3:1 (texto grande).
- `aria-live` para cambios de estado y errores.
- No depender solo del color para estados.
- Respetar `prefers-reduced-motion`.
- Pruebas con `vitest-axe` y revisión manual.

---

## 13. Seguridad

| Control | Implementación |
|---------|----------------|
| Tokens | `sessionStorage`; nunca en URL ni logs. |
| XSS | Sin `dangerouslySetInnerHTML`; sanitizar contenido externo; CSP. |
| CSRF | No aplica con Bearer; no se usan cookies. |
| Autorización | Server-side; UI solo oculta acciones. |
| Archivos | Validación cliente + servidor; no ejecutar PDFs; descargar como adjunto. |
| Dependencias | `npm audit`; versiones fijadas; revisión de licencias. |
| Errores | Sin filtrar detalles internos. |
| Logs | Sin PII; solo códigos y contexto técnico. |
| Red | HTTPS en producción; HSTS; CORS restringido (BE-08). |
| CSP sugerida | `default-src 'self'; connect-src 'self' <API>; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'` (ajustar a Vite). |

---

## 14. Rendimiento

- Lazy loading de rutas con `React.lazy` + `Suspense`.
- Code splitting por feature.
- `staleTime` para evitar refetch innecesario.
- Evitar renderizados masivos; paginación de 10–50.
- Imágenes optimizadas; sin librerías pesadas.
- `React.memo` solo donde se mida necesidad.
- Bundle inicial objetivo < 300 KB gzip.
- Medición con Lighthouse; LCP < 2.5 s en 3G rápida.
- Precarga de la ruta probable tras login.

---

## 15. Pruebas

### 15.1 Pirámide

| Nivel | Herramienta | Cobertura |
|-------|-------------|-----------|
| Unitarias | Vitest | Utilidades, validaciones, mapeos, componentes puros. |
| Integración | Vitest + RTL + MSW | Vistas con API simulada, roles, estados, errores. |
| Contrato | MSW + fixtures derivados del OpenAPI/código | Formas de request/response. |
| A11y | vitest-axe | Componentes y vistas críticas. |
| E2E (opcional) | Playwright | Login → crear → enviar → bandeja → observar. |

### 15.2 Cobertura mínima

- Lógica y utilidades: ≥ 90%.
- Componentes críticos: ≥ 80%.
- Vistas: al menos un caso feliz, un error y un estado vacío.
- Global: ≥ 80% (RNFF-007).

### 15.3 MSW

- Handlers en `src/mocks/handlers.ts`.
- Fixtures en `src/mocks/fixtures.ts` (solo pruebas).
- Casos: 200, 201, 400, 401, 403, 404, 422, 500, red.
- No se usan datos reales de estudiantes.

### 15.4 Comandos

```bash
npm run dev
npm run build
npm run preview
npm run lint
npm run typecheck
npm run test
npm run test:coverage
```

---

## 16. Observabilidad

- `ErrorBoundary` global y por feature.
- `logger.ts`: `info`, `warn`, `error` con contexto técnico; sin tokens/PII.
- En producción, enviar errores a un colector (a definir) o a consola controlada.
- No usar `console.log` en código productivo; ESLint lo prohíbe salvo en `logger.ts`.

---

## 17. Despliegue

- Build estático (`dist/`) servido por Nginx/CDN.
- Fallback SPA a `index.html`.
- Variables de entorno inyectadas en build (`VITE_*`).
- HTTPS obligatorio.
- Cache: `index.html` sin cache; assets con hash, cache largo.
- CORS: BE-08 debe permitir el origen del frontend.
- No se despliega en esta etapa.

---

## 18. Riesgos y mitigaciones

| Riesgo | Mitigación |
|--------|------------|
| Sin CORS (BE-08) | Proxy en Vite para desarrollo; documentar bloqueo de producción. |
| Token en `sessionStorage` | CSP, sanitización, auditoría; evaluar cookies httpOnly con BE-03. |
| Sin refresh (BE-03) | Aviso de expiración; borradores locales; re-login. |
| Sin catálogo (BE-10) | UUID manual o V-09; no inventar carreras. |
| Sin `GET /peticiones/{id}` (BE-02) | Usar detalle del expediente; refrescar. |
| Checklist estudiante 403 (BE-04) | Panel de limitación; no reintentar. |
| OpenAPI divergente (INC-05/06) | Tipos desde serializers reales; pruebas de contrato. |
| Assets no finales | Tokens y placeholders; sustitución posterior. |
| Deuda `pypdf` | No afecta al frontend; registrar como contexto. |
| D-04 (historial) | No mostrar historial no soportado. |

---

## 19. Fases de implementación

| Fase | Objetivo | Entregable | Depende de |
|------|----------|------------|------------|
| **F0** | Andamiaje | Vite + TS + lint + test + estructura + tokens + layout vacío. | Nada |
| **F1** | Auth y API | Login, sesión, guardas, cliente HTTP, MSW base. **Hecha** (2026-11-04: FE-T011…T017, 81/81 pruebas; V-01/FE-T101…T104 —formulario, integración, errores/accesibilidad y pruebas de la vista de login— cerrado 2026-11-05, ver `tasks.md` §6 y §18.5). | F0 |
| **F2** | Componentes base | UI kit, estados, badges, formularios, accesibilidad. **Hecha** (2026-11-04: FE-T019…T028, 170/170 pruebas, cobertura `components/ui` 96,12%). | F0 |
| **F2.5** | Estados de error y limpieza | Error pages 404/500/503, estados 401/403, `ForbiddenState`/`NotFoundState` alineados con el kit de errores (DEC-13); limpieza de plantilla. **Hecha** (2026-11-05: FE-T1210/1211/1212/1214; FE-T1213 sigue Bloqueada por BE-11; mascotas 404/403 integradas, 401/500/503 copiadas y documentadas sin integrar visualmente — ver `tasks.md` FE-T1214). | F2 |
| **F3** | Vistas estudiante | V-02, V-03, V-04 (parte estudiante), V-05, V-06 y V-09 (degradación temprana). **En curso**: V-02 Hecha (2026-11-05: FE-T201…T206); V-03 Hecha (2026-11-05: FE-T301…T306); V-04 Hecha (2026-11-05: FE-T401…T411, ver `tasks.md` §9 y §18.8 — incluye también las acciones de SECRETARIO_ABOGADO/ANALISTA_APOYO sobre el expediente, no solo la parte estudiante; FE-T407 con limitación real documentada para ESTUDIANTE); V-05/V-06 sin iniciar, requieren autorización independiente. | F1, F2 |
| **F4** | Vistas funcionario | V-07, V-08 (checklist, observar, informe, declaratoria). | F1, F2 |
| **F5** | Transversal | Notificaciones, responsive, a11y, errores, modo demo. | F3, F4 |
| **F6** | Calidad | Pruebas, cobertura, lint, typecheck, documentación. | F5 |

---

## 20. Definición de hecho (DoD)

Una tarea se considera terminada cuando:

1. Cumple sus criterios de aceptación.
2. Tiene pruebas (unitarias/integración) que pasan.
3. `npm run lint`, `npm run typecheck` y `npm run test` pasan.
4. Es accesible (teclado, foco, etiquetas, contraste).
5. Es responsive en los breakpoints definidos.
6. No introduce datos simulados en producción.
7. No registra tokens/PII.
8. Actualiza la documentación si cambia una convención.
9. No modifica backend, OpenAPI ni documentos existentes.
10. La revisión de código aprueba la trazabilidad a `RFF-*` y `CA-*`.

---

## 21. Referencias

- `clarify.md` — decisiones y bloqueos.
- `specify.md` — requisitos y vistas.
- `tasks.md` — tareas atómicas.
- `../../backend/openapi.yaml` — contrato.
- `../../diseno-ui/ui/titulacion-v2/especificaciones/` — referencia visual no normativa.
