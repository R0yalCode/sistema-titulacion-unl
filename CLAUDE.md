# CLAUDE.md — Instrucciones para Claude Code (SGT-SIAAF)

Lee primero `AGENTS.md` (raíz). Resumen operativo para ti:

## Antes de trabajar

- Lee, en orden: `AGENTS.md` → `specs/003-frontend-titulacion/clarify.md` → `specify.md` → `plan.md` → `tasks.md` (§18 orden, §19 DoD). Con UI: `diseno-ui/ui/titulacion-v2/especificaciones/01…08`.
- Elige **una tarea** de `tasks.md` del primer lote pendiente de §18; confirma su Estado en §3/§6+ antes de empezar.

## Máximas

1. **Frontend only.** `backend/`, `openapi.yaml`, migraciones Constitución y specs 001 (la `002` y la futura `004` **no existen**; si aparecieran, la prohibición aplica igual) intocables; nada de endpoints/campos/estados inventados.
2. **Cero simulación** (CA-G-01): sin datos/usuarios/estados demo; ni "En revisión" ni "Proyecto de Emprendimiento"; sin porcentajes que el backend no provea.
3. **Prototipos A/B**: solo referencia visual y de tono; prohibido copiar su HTML/CSS/JS. Escribe React desde cero con `tokens.css` (FE-T006) y los tokens de `especificaciones/01`.
4. **Sin dependencias nuevas** sin autorización humana; sin Git (init/commit; el repo no lo usa). Prohibido implementar tareas no autorizadas (las de BE-x nunca; FE-T1213 Bloqueada).
5. **FE-T1213 (409/412/428) bloqueada** por BE-11: no la toques. El backend no ofrece renovación de sesión: no implementes refresh automático ni logout de servidor inventados (re-login al expirar; `plan.md` §6).
6. Estados de error según `especificaciones/08` y `specify.md` §9.3: 401 no es página (aviso + `/login`); 403 en vista (`ForbiddenState`, destino V-09); 404 sí es página; 500/503 `ErrorState` con reintento real; formularios con `InlineAlert` (400/422; 409/412/428 solo si BE-11 se autoriza).

## Flujo de trabajo

1. Implementa la tarea en `frontend/` respetando estructura de `plan.md` §4 y rutas de `specify.md` §6.
2. Verifica: `npm run lint` → `npm run typecheck` → `npm run test` (+ `npm run build` si aplica). Todo verde o no es "Hecha".
3. Actualiza `tasks.md`: Estado + evidencia (comandos/pruebas) + dependencias desbloqueadas.
4. **Detente al final del lote** y resume qué hiciste, qué quedó bloqueado y qué decisión necesitas del humano.

## Estado actual (2026-11-05)

**F0 cerrada.** FE-T001…T010 y FE-T1210: Hechas, con evidencia (lint/typecheck/test/build en verde; 24/24 pruebas). D-FE-01 resuelto: causa raíz = botón `aria-label="Abrir navegación"` visible solo vía `@media (max-width:768px)`; jsdom usa `window.innerWidth=1024` fijo y no implementa `window.matchMedia`, por lo que el elemento queda fuera del árbol de accesibilidad en la suite (nombre accesible computado `""` por la especificación WAI-ARIA para elementos ocultos, no un bug de jsdom/dom-accessibility-api); corregido solo en `AppLayout.test.tsx` (consulta por atributo en vez de rol/nombre para esa aserción). D-FE-02/04 resueltos (`src/index.css` eliminado, `index.html` con `lang="es"`/título institucional). D-FE-03 resuelto (`README.md` real).

**F1 cerrada.** FE-T011…T017 (auth: JWT, `AuthContext`, cliente HTTP, endpoint de login + MSW, guardas de ruta, redirección por rol, logout): Hechas.

**F2 cerrada.** FE-T019…T028 (UI Kit: 170/170 pruebas, cobertura `components/ui` 96,12%): Hechas.

**F2.5 cerrada (2026-11-05).** FE-T1211 (404), FE-T1212 (401/403/500/503 con reintento real vía `presentApiError`), FE-T1214 (mascotas): Hechas. FE-T1213 (409/412/428) sigue **Bloqueada** por BE-11, sin tocar. Mascotas del prototipo B autorizadas bajo condiciones explícitas (DEC-15 en `clarify.md`): 403/404 integradas visualmente; 401/500/503 copiadas y documentadas sin integración visual (no hay páginas independientes para esos códigos). P2-3 (401 de login disparaba cierre de sesión global) corregido vía `skipAuthHandler`.

**V-01 cerrada (2026-11-05).** FE-T101…T104 (formulario de login, integración/persistencia, errores/carga/accesibilidad, pruebas): Hechas. `RedirectIfAuthenticated` conectada a `/login` (pendiente de la auditoría F1, resuelto). 22 pruebas nuevas; 226/226 totales, sin regresiones.

V-02/V-03 y fases posteriores (F3+) **sin iniciar**; requieren autorización explícita independiente. Orden en `tasks.md` §18.
