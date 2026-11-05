# 04 · Guía responsive (SGT-SIAAF)

**Versión:** 1.1.0 · **Fecha:** 2026-11-04 · **Estado:** Referencia visual no normativa (DEC-11).
Reglas de adaptación por tamaño de dispositivo.

## 4.0. Aclaración de breaks (reconciliación, 2026-11-04)

En el repositorio coexisten dos escalas de breakpoints:

- **Oficial del SDD (aprobada):** `plan.md` §10.1 y `tokens.css` (FE-T006) → `sm: 320 px`, `lg: 1440 px`, junto a los intermedios de esta guía. La verificación responsive de las tareas usa 320/768/1024/1440 (DoD §19 en `tasks.md`).
- **Observado en prototipo A (valores medidos):** contenedores ≈ `1190/1000/760/510 px`; son **medidas de cámara del prototipo**, no breakpoints normativos: no se reimplementan literalmente en React.

**Decisión:** los breakpoints de implementación son los del SDD/`tokens.css`; los valores del prototipo sirven solo para reproducir la intención de diseño (cuándo colapsa el sidebar, cuándo se apilan grids), probados en las capturas 320/768/1440 de FE-T008 y vistas.

## 4.1. Escalas del SDD

| Rango | Comportamiento |
|---|---|
| `≥ 1280 px` (desktop) | Layout completo: sidebar fijo 260 px; grids de 2–3 columnas; tablas completas |
| `1024–1279 px` (laptop) | Idéntico con padding de contenido 24 px |
| `768–1023 px` (tablet) | Sidebar colapsable (oculto por defecto, drawer con overlay vía hamburguesa); grids a 1–2 columnas; tablas con scroll horizontal (`overflow-x: auto`), se pueden ocultar columnas secundarias (ej. Observaciones) o convertir filas en tarjetas |
| `< 768 px` (móvil, mínimo verificado 320 px) | Header simplificado (logo, botón menú, avatar); formularios al 100 % del ancho; botones principales a `width: 100%`; vistas de 2 columnas (V-06 y V-08 grids 70/30 y 2x2) apiladas verticalmente (timeline debajo de la info general); stepper de V-04 pasa a texto "Paso 1 de 3" |

## 4.2. Reglas generales

- **Mobile-first no aplica estrictamente** (el sistema está diseñado desktop-first); aun así, todo debe verificarse desde 320 px (DoD).
- La navegación lateral se reemplaza por drawer en ≤768 px con foco hundido y cierre con `Esc` (a11y, doc 05).
- Las páginas de error del kit B (doc 08) se reutilizan en todos los tamaños con el mismo shell (no tienen diseño dedicado por breakpoint).
- 412/428/409 (InlineAlert, si BE-11) garantizan las mismas acciones tanto en tablet como en móvil (documentación InlineAlert del doc 08).

## 4.3. Referencias

- SDD: `specs/003-frontend-titulacion/plan.md` §10.1 (breakpoints oficiales), `tasks.md` §19 (DoD con 320/768/1024/1440).
- Tokens implementados: `frontend/src/styles/tokens.css`.
- Prototipo A (referencia de comportamiento de collapsar/empilar, no de valores): `SGT_SIAAF_Prototipo_Web/app.js` (media queries observadas `1190/1000/760/510`).
