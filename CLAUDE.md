# CLAUDE.md — Instrucciones para Claude Code (SGT-SIAAF)

Lee primero `AGENTS.md` (raíz). Resumen operativo para ti:

## Antes de trabajar

- Lee, en orden: `AGENTS.md` → `specs/003-frontend-titulacion/clarify.md` → `specify.md` → `plan.md` → `tasks.md` (§18 orden, §19 DoD). Con UI: `diseno-ui/ui/titulacion-v2/especificaciones/01…08`.
- Elige **una tarea** de `tasks.md` del primer lote pendiente de §18; confirma su Estado en §3/§6+ antes de empezar.

## Máximas

1. **Frontend only.** `backend/`, `openapi.yaml`, migraciones Constitución y specs 001 (la `002` y la futura `004` **no existen**; si aparecieran, la prohibición aplica igual) intocables; nada de endpoints/campos/estados inventados.
2. **Cero simulación** (CA-G-01): sin datos/usuarios/estados demo; ni "En revisión" ni "Proyecto de Emprendimiento"; sin porcentajes que el backend no provea.
3. **Prototipos A/B**: solo referencia visual y de tono; prohibido copiar su HTML/CSS/JS. Escribe React desde cero con `tokens.css` (FE-T006) y los tokens de `especificaciones/01`.
4. **Sin dependencias nuevas** sin autorización humana. **Git** (commit/push/merge) solo con autorización humana explícita para esa tarea y según `SIAAF-KNOWLEDGE/15-GIT-AND-WORKFLOWS/GIT_POLICY.md` (ramas desde `develop`, nunca sobre `main`, sin `git add .`). Prohibido implementar tareas no autorizadas (las de BE-x nunca; FE-T1213 Bloqueada).
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

**V-01 cerrada (2026-11-05).** FE-T101…T104 (formulario de login, integración/persistencia, errores/carga/accesibilidad, pruebas): Hechas. `RedirectIfAuthenticated` conectada a `/login` (pendiente de la auditoría F1, resuelto). 22 pruebas nuevas.

**V-02 cerrada (2026-11-05).** FE-T201…T206 (dashboard del estudiante: estructura, bandeja BORRADOR/OBSERVADA, notificaciones, accesos rápidos locales, estados/errores, pruebas): Hechas. BE-05 (perfil + historial completo) sigue sin autorizar, pero no bloqueó esta vista porque la bandeja (`GET /expedientes/bandeja/`) y las notificaciones (`GET`/`PATCH /notificaciones/`) ya son accesibles al rol ESTUDIANTE (`RBAC_MATRIX`, verificado contra el código real). Discrepancia documentada: `GET /notificaciones/` no está paginado en el backend real, a diferencia de lo que indican `specify.md` y `openapi.yaml`. 29 pruebas nuevas.

**V-03 cerrada (2026-11-05).** FE-T301…T306 (crear solicitud: formulario con `carrera_id` UUID manual —sin catálogo, BE-10—, integración real con `POST /expedientes/`, manejo de errores incl. "expediente activo" (400, no 409), protección real ante doble creación, borrador local, éxito/redirección, pruebas): Hechas. 24 pruebas nuevas.

**V-04 cerrada (2026-11-05).** FE-T401…T411 (expediente y requisitos: cabecera/timeline con datos reales, detalle+peticiones, checklist con 403 real para ESTUDIANTE, enviar/observar/evaluar/subsanar, descarga autenticada, matriz de acciones por rol/estado, invalidación, pruebas): Hechas. **INC-21**: varias excepciones de dominio en observar/evaluar/subsanar responden HTTP 500 real (no 400/404) aunque describen reglas de negocio — se muestra siempre el mensaje real del backend. **Limitación crítica documentada (no resuelta modificando el backend):** ESTUDIANTE y SECRETARIA_CARRERA no tienen ningún endpoint accesible para descubrir el `checklist_verification_id` que requiere la subsanación (`GET .../checklist/` es 403 para ambos); solo ADMINISTRADOR reúne lista+escritura en la práctica. 51 pruebas nuevas; 328/328 totales, sin regresiones.

V-05 y fases posteriores (F3 restante, F4+) **sin iniciar**; requieren autorización explícita independiente. Orden en `tasks.md` §18.


**Bóveda SIAAF-KNOWLEDGE (2026-11-11).** Construida en `SIAAF-KNOWLEDGE/` (informe: `00-CORE/BUILD_REPORT.md`). Hallazgos sin resolver que afectan a tareas futuras: no existe la transición `ENVIADA→EN_VERIFICACION` por API (GAP-STATE-01); `RESPONSABLE_DEPENDENCIA` no tiene celdas RBAC; la suite frontend mostró intermitencia (1 de 3 ejecuciones con 6 fallos).

## Política de consulta del conocimiento SIAAF-KNOWLEDGE

La bóveda `SIAAF-KNOWLEDGE/` (raíz del repo, bóveda Obsidian oficial) es la fuente central de conocimiento documental. Misma bóveda y mismas reglas para OpenCode (`AGENTS.md`).

Antes de iniciar una tarea (recuperación progresiva; no releas lo que ya está en contexto):

1. `SIAAF-KNOWLEDGE/00-CORE/MASTER_INDEX.md`: localiza el área (arranque mínimo: `00-CORE/SYSTEM.md`).
2. `SIAAF-KNOWLEDGE/00-CORE/CURRENT_STATE.md`: solo el contexto general.
3. La nota específica del módulo o proceso, y desde ella requisitos, decisiones, auditorías o trazabilidad, **solo** si hacen falta.
4. Con el MCP `obsidian` disponible: `search_notes` → `read_note` (`metadataOnly`) → `read_note` (`heading`); edita con `patch_note`/`append_to_note`. Sin MCP: lee directamente los `.md` (grep + rango de líneas). Nunca bloquees una tarea por falta de MCP.
5. Fuentes originales por sección (rutas en `90-ORIGINAL-SOURCES/SOURCE_CATALOG.md`).
6. **Verifica siempre el código real**: el código y las pruebas ejecutadas mandan sobre la documentación para el estado de implementación; la normativa y las specs, para los requisitos. Si chocan, registra la contradicción en `13-TRACEABILITY/DOCUMENT_TRACEABILITY.md`; no la resuelvas inventando.

No leas toda la bóveda ni todo el repositorio. No copies a la bóveda `.env`, secretos, tokens, claves, PDF de `media/private/` ni datos personales.

Al finalizar una tarea, actualiza **solo** las notas afectadas según `15-GIT-AND-WORKFLOWS/KNOWLEDGE_MAINTENANCE.md` (cambios, pruebas con resultados reales, decisiones, evidencias, pendientes, commits).