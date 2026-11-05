# 03 · Catálogo de componentes UI (SGT-SIAAF)

**Versión:** 1.1.0 · **Fecha:** 2026-11-04 · **Estado:** Referencia visual no normativa (DEC-11).
Catálogo de componentes reutilizables a construir en React. La implementación activa vive en `frontend/src/components/{ui,layout,feedback}` (tareas FE-T020…FE-T028 + F2.5). Los prototipos son referencia de variante/comportamiento, no fuente de código.

## 3.1. Bases y layout

| Componente | Variantes / props | Descripción visual | Estado de implementación |
|---|---|---|---|
| `AppLayout` | `children` (con providers) | Sidebar verde profundo + header blanco + contenido; drawer en móvil | **Hecha** (FE-T007; pendiente cerrar FE-T008 por D-FE-01) |
| `Sidebar` | `items: MenuItem[]` | Item activo con fondo rojo; lista de enlaces `@/features` | **Hecha** |
| `Header` | `user: UserProfile` | Toggle sidebar, buscador, notificaciones, avatar/nombre | **Hecha** (logout delegado a FE-T016) |
| `SkipLink` | texto | Enlace "Saltar al contenido" accesible, visible con foco | **Hecha** |
| `DemoBanner` | texto | Banner superior de modo demo de la vista de referencia | **Hecha** (FE-T006) |

## 3.2. UI kit (formularios y datos)

| Componente | Variantes / props | Descripción visual |
|---|---|---|
| `Button` | `variant: 'primary'\|'outline'\|'ghost'`, `size: 'sm'\|'md'\|'lg'` | Primary rojo; outline con borde; ghost sin fondo; estados hover/focus/disabled |
| `Input` / `Select` / `Textarea` | `label`, `error`, `icon` | Altura 40 px; borde gris; focus ring con azul/rojo del sistema; error con mensaje accesible (`aria-describedby`) |
| `Badge` | `status: 'pending'\|'success'\|'info'\|'error'` | Píldora redondeada con colores de `tokens.css`; nunca solo color (texto explícito) |
| `Card` | `title?`, `children` | Blanco, borde gris claro, sombra sutil, radius 8 px |
| `Table` | `columns: Column[]`, `data`, `emptyLabel` | Encabezado claro, filas con borde inferior; scroll horizontal en móvil |
| `Modal` | `isOpen`, `onClose`, `title`, `children` | Overlay oscurecido, caja blanca centrada, focus trap (doc 05) |
| `Timeline` | `events: TimelineEvent[]` | Línea vertical con iconos circulares (verde completado / activo / gris pendiente) |
| `Stepper` | `steps: string[]`, `currentStep` | Círculos numerados unidos; activo en rojo; en móvil, texto "Paso X de N" |
| `ProgressBar` | `value`, `max` | Barra verde sobre pista gris |
| `Pagination` | `page`, `total`, `onPageChange` | "Mostrando X–Y de Z" + botones de página (V-07/V-08); solo con datos reales |
| `Tabs` | `tabs`, `activeId` | Texto/tab activo con borde inferior rojo (V-04) |
| `FileUpload` | `accept`, `maxSizeMB`, `onSelect` | Dropzone con arrastrar y soltar; valida tipo/tamaño antes de enviar (ver RFF-005) |
| `EmptyState` | `icon`, `title`, `description`, `action` | Icono grande gris + texto secundario; reutilizado por vista (ver doc 08, EST-02) |
| `Toast` (ToastProvider) | `variant info/success/error`, texto | Feed accesible con `role="status"`; cierre manual; sin reemplazar al InlineAlert |

## 3.3. Estados de error y operativos (nuevos, F2.5 — especificación en doc 08)

| Componente | Variante / disparador | Descripción visual | Estado |
|---|---|---|---|
| `Spinner` | loading | Indicador de carga junto a `aria-busy="true"` en el contenedor | Propuesto |
| `LoadingState` | loading de sección/página | Skeleton o spinner centrado + texto "Cargando…" | Propuesto |
| `EmptyState` | dato vacío (incl. "sin asignación") | Según 3.2; texto según contexto (ver EST-02) | Propuesto |
| `ErrorState` | 500/503/red | Mensaje "no disponible, reintenta" + botón "Reintentar" (reintento real) | Propuesto |
| `InlineAlert` | 409/412/428 en formulario (BE-11) | Alerta dentro del formulario, `role="alert"`, foco, conserva el texto del usuario | **Bloqueada** (BE-11) |
| `ForbiddenState` | 403 dentro del layout | Explicación sin filtrar detalles + acciones alternativas | Propuesto (FE-T1212) |
| `NotFoundState` | 404 de recurso/menú | "No encontrado" + "Volver" | Propuesto (FE-T1212) |
| `NotFoundPage` | 404 global de ruta | Página fuera del shell solo para ruta desconocida (FE-T1211) | Stub actual → estilizar |
| `Guard` | guarda de ruta | Decide `/login`, `/no-habilitado` o contenido según sesión/rol (no es visual) | Propuesto V-09 |

Reglas de páginas vs. componentes (DEC-13): 401 **no es página** (`/login` con aviso); 403 usa `ForbiddenState`+V-09 dentro del shell; 404 sí es página (404 global FE-T1211) más `NotFoundState` para recursos; 500/503 usan `ErrorState` (página solo si el ErrorBoundary global requiere shell propio); 409/412/428 son `InlineAlert` **solo si BE-11**.

## 3.4. Feedback transversal

| Componente | Uso |
|---|---|
| `ErrorBoundary` | Fallback global `role="alert"` + "Reintentar" — **Hecha** (FE-T007) |
| `ToastProvider` | Cola accesible para mutaciones/stados efímeros — stub actual, implementar FE-T027 |
| `InlineAlert` | Errores de formulario ambos 400/422 y, si BE-11, 409/412/428 |

## 3.5. Referencias

- Implementación: `frontend/src/components/{ui,layout,feedback}`, tokens `frontend/src/styles/tokens.css`.
- Tareas: `specs/003-frontend-titulacion/tasks.md` (FE-T020…FE-T028 y FE-T1210…FE-T1214).
- Estados de error: `08_UI_ERROR_STATES_SPEC.md`.
- A11y: `05_UI_ACCESSIBILITY_GUIDELINES.md`.
