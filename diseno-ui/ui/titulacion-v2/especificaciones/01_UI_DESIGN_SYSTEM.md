# 01 · Design System — Tokens y reglas globales (SGT-SIAAF)

**Versión:** 1.1.0 · **Fecha:** 2026-11-04 · **Estado:** Referencia visual no normativa (DEC-11).
**Naturaleza:** Especificación de diseño. Define la intención visual; la fuente de verdad implementada es `frontend/src/styles/tokens.css` (FE-T006, Hecha) y el SDD `specs/003-frontend-titulacion/specify.md` + `plan.md`.

> **Regla de trazabilidad cromática (2026-11-04).** Este documento distingue tres niveles de color:
> 1. **Observado en prototipo** — lo que realmente usan los prototipos A/B (valores medidos).
> 2. **Propuesto** — lo que este design system propone normalizar.
> 3. **Institucional confirmado** — **ninguno por ahora**. Los colores oficiales de la UNL solo pueden declararse tras verificar la identidad institucional vigente (pendiente, PQ-13 en `clarify.md`). No se presentan colores "oficiales UNL" sin archivo autorizado.

## 1.1. Paleta cromática (tokens)

| Token | Valor propuesto | Observado en prototipos | Uso |
|---|---|---|---|
| `--color-brand-red` | `#BF0811` | A: `#c9081e` (botones/acento); B: `#bb0920` (kit errores) | Botones primarios, acentos activos, iconos críticos |
| `--color-brand-green` | `#4F8E3A` | A: `#073b2d` (sidebar verde profundo); éxito ≈ verde medio | Sidebar, estados de éxito, indicadores positivos |
| `--color-brand-blue` | `#004C7B` | B: `#155bb7` (kit errores, enlaces/info) | Enlaces secundarios, iconos informativos |
| `--color-bg-main` | `#F6F8FA` | Gris muy claro en ambos prototipos | Fondo principal de la aplicación |
| `--color-surface` | `#FFFFFF` | Blanco en tarjetas/modales/tablas | Tarjetas, modales, tablas |
| `--color-text-primary` | `#1F2937` | Gris oscuro ≈ consenso | Títulos, textos principales |
| `--color-text-secondary` | `#6B7280` | Gris medio ≈ consenso | Subtítulos, ayuda, fechas, labels |
| `--color-border` | `#E5E7EB` | Borde gris claro ≈ consenso | Bordes de tarjetas, separadores, inputs |
| `--color-status-pending` | fondo `#FDE68A` / texto `#92400E` | Ámbar en prototipo A | Badge "Pendiente" |
| `--color-status-success` | fondo `#D1FAE5` / texto `#065F46` | Verde claro en prototipo A | Badge "Completado/Solicitado" |
| `--color-status-info` | fondo `#DBEAFE` / texto `#1E40AF` | Azul claro en prototipo A | Badge "En revisión/En atención" |
| `--color-status-error` | fondo `#FEE2E2` / texto `#991B1B` | Rojo claro en prototipo A | Badge "Rechazado/Observado" |

**Nota de reconciliación.** Los rojos observados (`#c9081e`, `#bb0920`) y el `#BF0811` propuesto son variaciones del mismo rojo institucional; se adopta el propuesto como normalización y se registra que **ninguno está confirmado institucionalmente**. El verde del sidebar observado (`#073b2d`) es el referente visual real; el verde `#4F8E3A` propuesto sirve para semántica de éxito, no para el sidebar.

Contraste verificado en implementación: los tokens de `tokens.css` pasan la prueba axe (`TokensShowcase.test.tsx`, FE-T006).

## 1.2. Tipografía

Familia: Sans-serif del sistema (`Inter`, `Roboto` o equivalente; sin cargar webfonts externas por rendimiento).

| Rol | Tamaño / peso |
|---|---|
| `h1` | 28 px (1.75 rem), 700 |
| `h2` | 24 px (1.5 rem), 600 |
| `h3` | 20 px (1.25 rem), 600 |
| `body` | 14 px (0.875 rem) o 16 px (1 rem), 400 |
| `small`/`label` | 12 px (0.75 rem), 500 |
| `button` | 14 px, 600 |

## 1.3. Espaciado y geometría

- Espaciado en múltiplos de 4 px (4, 8, 12, 16, 24, 32, 48).
- Radios: `--radius-sm` 4 px (badges, inputs), `--radius-md` 8 px (botones, tarjetas), `--radius-lg` 12 px (modales, contenedores grandes).
- Sombras: `--shadow-sm` (tarjetas/tabla), `--shadow-md` (dropdowns, hover), `--shadow-lg` (modales).

## 1.4. Layout global

- **Sidebar:** ancho fijo 260 px; fondo verde profundo (observado `#073b2d`), texto blanco; logo institucional arriba. En < 768 px pasa a drawer con overlay.
- **Header:** altura 64 px; fondo blanco, borde inferior gris claro; menú hamburguesa (responsive), notificaciones, perfil.
- **Contenido principal:** padding 24–32 px; ocupa `calc(100% - 260px)` en desktop.

## 1.5. ¿Qué NO hace este documento?

- No declara colores oficiales de la UNL (pendiente de confirmación institucional; ver PQ-13).
- No es copiable al código "tal cual": la implementación React traduce tokens a `tokens.css`; **prohibido** copiar HTML/CSS/JS de los prototipos (DEC-11).
- Los estados de error tienen su propia especificación: `08_UI_ERROR_STATES_SPEC.md` (colores del kit B observados: rojo `#bb0920`, azul `#155bb7`).

## 1.6. Referencias

- Prototipo A: `SGT_SIAAF_Prototipo_HTML_CSS_JS/SGT_SIAAF_Prototipo_Web/` (vista de referencia).
- Prototipo B: `SGT_SIAAF_8_Vistas_Errores_UNL_HTML_CSS_JS/SGT_SIAAF_Errores_HTML_UNL/` (kit de errores).
- Implementación: `frontend/src/styles/tokens.css`, `global.css`, `utilities.css`.
- SDD: `specs/003-frontend-titulacion/specify.md` (§4, §6.1), `clarify.md` (DEC-11, PQ-13).
