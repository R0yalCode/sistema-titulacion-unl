# 08 · Especificación de estados de error y operativos (SGT-SIAAF)

**Versión:** 1.0.0 · **Fecha:** 2026-11-04 · **Estado:** Referencia de diseño no normativa (DEC-11); requisitos funcionales en `specify.md` §9.3 (RFF-004, RFF-005, RFF-013, RFF-014, RFF-017); implementación en fase F2.5 (`tasks.md` FE-T1210…FE-T1214).
Especificación transversal derivada del prototipo B (kit de errores UNL) y de la jerarquía de estados aprobada (DEC-13). **No se copia HTML/CSS/JS de los prototipos**; el kit define tono, mensaje y jerarquía.

## 8.0. Jerarquía de estados (DEC-13)

| Clase | Estados | Presentación |
|---|---|---|
| **G1 · Globales** | 401, 403, 404, 500, 503 | A nivel de app: 401 → aviso + `/login`; 403 → `ForbiddenState` dentro del shell (+V-09 por guardas); 404 → página global + `NotFoundState` en recursos; 500/503 → `ErrorState` con reintento real |
| **G2 · Formularios** | 400, 422 y —condicionados a BE-11— 409, 412, 428 | `InlineAlert` dentro del formulario; **no expulsan al usuario**; el texto no escrito se conserva |
| **G3 · Operativos reutilizables** | loading, empty (incl. "sin asignación"), success, read-only | Componentes del kit (`LoadingState`, `EmptyState`, toasts success, badges read-only) |

Reglas de páginas vs. componentes: 401 **no es página**; 403 no es página (estado dentro de la vista); 404 sí lo es (ruta desconocida); 500/503 usan componente `ErrorState` (página solo si el ErrorBoundary global necesita shell). Nunca duplicar: si un estado se resuelve dentro de la vista, no se navega a una página aparte.

## 8.1. Catálogo errores — ERR-01…ERR-09

Referencia visual: prototipo B `prototipos/vistas-errores-unl/paginas/*.html` (colores observados: rojo `#bb0920`, azul `#155bb7`; ver doc 01).

| ID | Código | Disparador | Presentación (UI) | Acción del usuario | Tarea | Estado |
|---|---|---|---|---|---|---|
| ERR-01 | 401 | Sesión ausente/expirada (CA-G-03) | Aviso "Tu sesión ha expirado…" + redirección a `/login` | Reingresar | FE-T1212 | Implementar |
| ERR-02 | 403 | Rol/alcance sin permiso (CA-G-04, RFF-404) | `ForbiddenState` en la vista dentro del shell (sin detalles internos, sin filtros de existencia); V-09 como destino de guardas de ruta | "Volver al inicio" / acciones alternativas | FE-T1212 | Implementar |
| ERR-03 | 404 | Ruta desconocida (página) o recurso inexistente | Página 404 con CTAs por rol/sesión ("Volver al inicio por rol", "Ir a `/login`") y nota de privacidad; en recursos: `NotFoundState` | Diagnosticar URL o volver | FE-T1211 (página), FE-T1212 (estado) | Implementar |
| ERR-04 | 409 | Petición duplicada en submit | **Escenario propuesto**: `InlineAlert` "Ya existe una petición activa de este tipo…" + acción de revisar la existente | Revisar petición existente | FE-T1213 | **Bloqueada (BE-11)** |
| ERR-05 | 412 | Versión desactualizada (otro usuario cambió datos) | **Escenario propuesto**: `InlineAlert` "Otra persona actualizó esta información…" con "Recargar"/"Cancelar"; el texto del formulario se conserva | Recargar y reenviar | FE-T1213 | **Bloqueada (BE-11)** |
| ERR-06 | 428 | Se requiere versión vigente (If-Match) | **Escenario propuesto**: `InlineAlert` "Se requiere una versión vigente…" con recarga de datos | Recargar y reenviar | FE-T1213 | **Bloqueada (BE-11)** |
| ERR-07 | 500 | Error del servidor | `ErrorState` "No se pudo completar…" + "Reintentar" (reintento real de query o recarga) | Reintentar | FE-T1212 | Implementar |
| ERR-08 | 502/503/504 + red/timeout | Infraestructura/sin conexión | `ErrorState` "Servicio temporalmente no disponible…" + reintento | Reintentar | FE-T1212 | Implementar |
| ERR-09 | 429 | Demasiadas solicitudes | **No definido**: no aparece en requisitos ni prototipos; no inventar. Si el backend lo declara en el futuro, tratarse como `InlineAlert`/toast informativo con acción "esperar" | Esperar | — | **Pendiente de definición** |

Regla común: los `InlineAlert` de G2 solo se activan si `error.status` y `error.code` coinciden con la tabla; de lo contrario degradan a 400 genérico con el mensaje del backend. Sin BE-11 autorizado, 409/412/428 no se incorporan como estados del formulario y también degradan a error genérico.

## 8.2. Estados operativos — EST-01…EST-05

| ID | Estado | Disparador | Presentación | Tarea | Estado |
|---|---|---|---|---|---|
| EST-01 | Loading | Consulta en vuelo | `LoadingState` (skeleton/spinner + `aria-busy="true"`, msg "Cargando…") | FE-T021/FE-T1212 | Implementar |
| EST-02 | Empty | Sin datos | `EmptyState` con texto por contexto: "Sin expediente aún" (V-02), "Sin solicitudes" con CTA de crear, "**Sin asignación**" (roles sin expediente asignado: honesto, sin inventar), "Sin peticiones/documentos" | FE-T021, FE-T201 | Implementar |
| EST-03 | Success/mutada | Mutación 200 | Toast accesible `role="status"` + a veces inline de confirmación; no bloqueante | FE-T027 | Implementar |
| EST-04 | Read-only | Usuario sin permiso de escritura sobre lo que ve | Badge "Solo lectura" + acciones deshabilitadas con `title`/`aria-label` explicativo; nunca toast de error | FE-T021/FE-T1212 | Implementar |
| EST-05 | Partial (403 de checklist) | `GET checklist/` rechaza por RBAC | Sección de checklist omitida o `ForbiddenState` en la pestaña, la vista continua con el resto (RFF-404) | FE-T407 | Implementar con V-04 |

## 8.3. Reglas universales

1. Todos los estados son accesibles: contenedores con `role="alert"` (errores) o `role="status"` (éxito), foco gestionado al aparecer, texto en español sin tecnicismos ni rutas internas. Incluye páginas 404/500/503 con jerarquía de encabezados y CTAs reales.
2. Navegador no desaparece: un error del formulario no navega fuera de la vista ni descarta datos escritos.
3. Reintentos reales: 5xx/red reintentan la consulta; no botones decorativos.
4. Sin detalles internos: nunca exponer stack, SQL, rutas ni nombres de tablas (CA-G-02/RNFF-003); para 403/404 no se confirma la existencia de recursos ajenos.
5. Estilo: colores de marca del doc 01, iconos del kit de sistema (no PNGs del prototipo salvo aprobación FE-T1214); tipografía del doc 01; mensajes cortos (≤ 2 líneas) con acción clara.

## 8.4. Mapeo de tareas y bloqueos

| Tarea | Cubre | Estado |
|---|---|---|
| FE-T1210 | Limpieza de la plantilla Vite (`index.css`, `lang`/`title`) → base del estilo de errores | Pendiente (primer lote) |
| FE-T1211 | ERR-03 página 404 | Pendiente |
| FE-T1212 | ERR-01, ERR-02, ERR-07, ERR-08; EST-01/04 | Pendiente |
| FE-T1213 | ERR-04, ERR-05, ERR-06 (`InlineAlert`) | **Bloqueada (BE-11)** |
| FE-T1214 | Assets gráficos del kit B (mascotas/favicon) | Propuesta (decisión del usuario) |

Bloqueo registrado: OpenAPI (`backend/openapi.yaml`) declara únicamente respuestas `200`; los 4xx/5xx reales de DRF quedan de facto (CL-22 en `clarify.md`) — la **ausencia de documentación explícita no impide que el frontend reciba errores HTTP estándar**, y la UI los trata con esta especificación. Por eso ERR-04/05/06 (409/412/428) son **propuestos** y no se implementan hasta BE-11: requieren contrato, definición y autorización de backend, no solo aparición de facto.

## 8.5. Referencias

- Prototipo B: `prototipos/vistas-errores-unl/` (`paginas/401.html`…`503.html`, `acceso.html`).
- SDD: `specify.md` §9.3 (tabla y reglas), RFF-004/005/013/014/017, CA-G-02…CA-G-04; `clarify.md` DEC-11, DEC-12, DEC-13, CL-21/CL-22, D-FE-01…D-FE-04; `plan.md` §11.1 (fase F2.5) y matriz HTTP; `tasks.md` §5.bis y §17.
