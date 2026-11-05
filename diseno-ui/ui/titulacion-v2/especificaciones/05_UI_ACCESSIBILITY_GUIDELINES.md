# 05 · Guía de accesibilidad (SGT-SIAAF)

**Versión:** 1.1.0 · **Fecha:** 2026-11-04 · **Estado:** Referencia no normativa en la parte visual; los requisitos verificables son RFF-012, RFF-015-RFF-020 y las tareas con axe del SDD (`tasks.md` §19 DoD item 4).
Objetivo: WCAG 2.1 nivel AA en todo el frontend.

## 5.1. Contraste

- Relación mínima 4.5:1 para texto normal y 3:1 para texto grande, incluyendo badges de estado sobre su fondo y texto blanco sobre `brand-green`/`brand-red`.
- Nota verificada en implementación: el rojo `#BF0811` sobre blanco tiene ≈ 6:1 (aprobado); los pares de badges de `tokens.css` pasan axe (`TokensShowcase.test.tsx`).
- La verificación es automatizada: integra `vitest-axe` (ya con workaround por bug del empaquetado en `setup.test.ts` o su equivalente documentado en `frontend/src/test/setup.ts`) en las pruebas y flujo de axe del DoD.

## 5.2. Navegación por teclado y foco

- Todos los interactivos (botones, inputs, links, celdas con acciones de tabla, tabs, paginación) accesibles con Tab/Shift+Tab; orden lógico sin capturar el foco fuera de modales/drawer abiertos.
- **Focus trap en modales y drawer** (cierre con `Esc` y devolución del foco al disparador).
- Estados de foco visibles: `outline: 2px solid var(--color-brand-blue); outline-offset: 2px;` (revisar: si institucionalmente se decide otro color, mantener el anillo y/o offset; también `:focus-visible`).
- `SkipLink` presente en el shell (ya implementado, FE-T006) y apuntando a `#main`.

## 5.3. Semántica y etiquetas

- Todos los inputs con `<label>` asociado; **no usar placeholder como única etiqueta**.
- Inputs con error: `aria-invalid="true"`, `aria-describedby` con el InlineAlert/mensaje (incluido el `409/412/428` cuando BE-11 lo declare; doc 08).
- Botones con nombre accesible (los botones de icono como "ojo"/hamburguesa usan `aria-label` descriptivo; ver nota D-FE-01 sobre el test de `AppLayout`: el botón `aria-label="Abrir navegación"` existe en el DOM pero `getByRole` no lo resuelve — causa sin diagnosticar, resolver al cerrar FE-T008).
- Badges de estado: color + texto legible ("Pendiente", "En atención", "Completado", "Rechazado") — nunca solo color.
- Tablas con acciones: encabezados asociados (`<th scope="col">`) y filas navegables.

## 5.4. Imágenes, logos y carga

- Logo institucional: `alt="Escudo Universidad Nacional de Loja"`; imágenes decorativas (mascotas del kit, si se aprueba FE-T1214): `alt=""`.
- Contenedores con datos cargando: `aria-busy="true"` (exigido en del doc 08 `LoadingState`).
- Fechas/IDs con formato claro en español (por `lib/format.ts` cuando se cree).
- Timelines: listas semánticas (`<ol>`) con cada hito en texto, no solo iconos.

## 5.5. Verificación obligatoria

- Cada tarea con UI ejecuta axe en su prueba RTL (ya en el DoD), incluyendo foco en estados `not-found/forbidden/partial/error`.
- La verificación de navegación por teclado para formularios críticos (login, nueva solicitud, modal de petición, dialoga de observación) se hace manualmente además de axe (axe evalúa estáticamente la AST, no el foco real).

## 5.6. Referencias

- Prohibiciones del framework: no introducir estilos/colores/breakpoints que rompan estos mínimos (docs 01 y 04).
- Requisitos: `specs/003-frontend-titulacion/specify.md` RFF-012/RFF-015, RNFF-007; tareas axe: FE-T020, FE-T021, FE-T027, FE-T1104.
- Kit B (tono y accesibilidad de páginas de error): `08_UI_ERROR_STATES_SPEC.md` (cada ERR incluye CA a11y).
