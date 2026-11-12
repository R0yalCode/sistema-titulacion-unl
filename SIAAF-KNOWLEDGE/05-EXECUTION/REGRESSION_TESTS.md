---
system: SGT-SIAAF
type: execution
area: tests
status: verified
source: test-runs
last_verified: 2026-11-12
---

# Pruebas y regresión

## Ejecuciones registradas

| Fecha | Suite | Comando | Resultado | Duración | Contexto |
|---|---|---|---|---|---|
| 2026-11-11 | Frontend | `npm run test` (`vitest run`) | **6 fallidas / 322 aprobadas (328)**; 2 archivos con fallos de 58 | 139,7 s | Rama `docs/siaaf-knowledge`; sin cambios de código |
| 2026-11-11 | Frontend | `npx vitest run` (2.ª ejecución) | Sin líneas `FAIL` en la salida filtrada | — | Ídem |
| 2026-11-11 | Frontend | `npx vitest run` (3.ª ejecución) | **58/58 archivos, 328/328 pruebas aprobadas** | — | Ídem |
| 2026-11-05 | Frontend | — | 328/328 (según `CLAUDE.md`, cierre de V-04) | — | Registro previo, no reejecutado |
| 2026-11-12 | Frontend | `npx vitest run` ×6 sobre `04828d9` (V-07/V-09) | 5×406/406; **1×405/406**: `router.auth-expiry.test.tsx` › «un 401 … redirige a /login» | ~21 s c/u | Rama `feat/v07-bandeja-v09-no-habilitado` |
| 2026-11-12 | Frontend | Suite completa en V-07 antes del commit (×5) | 4×correctas; 1 fallo en la misma prueba | — | Ídem |
| 2026-11-12 | Frontend | `router.auth-expiry.test.tsx` aislada (×3) | 3×2/2 | — | Ídem |
| 2026-11-12 | Frontend | Experimento determinista: 401 lanzado **antes** de que aparezca el dashboard (copia temporal, eliminada) | 3×3 reproduce el síntoma exacto | — | Ídem |
| 2026-11-12 | Backend (SQLite) | `pytest` · `src/core` · `tests` | **625 aprobadas, 13 fallidas** (`pypdf`, misma lista) · 103/103 · 24 + 12 omitidas | ~14 s | I-3, rama `fix/i3-archivos-huerfanos` |
| 2026-11-12 | Backend (PostgreSQL 16.15) | `-m postgres tests/integration` · `tests/` · `src/apps` | **12/12** (C1–C8, infraestructura, 2 de fallo de *commit*) · 36/36 · 21 fallos conocidos (13 `pypdf` + 8 H-30) | ~35 s | Ídem; contenedor desechable |
| 2026-11-11 | Backend (SQLite) | `pytest` | **606 aprobadas, 13 fallidas** (`test_pdf_generator.py`, `pypdf`; lista idéntica a `develop`) | ~10 s | PLB-E1-04 + O-2, rama `fix/e1-04-errores-dominio` |
| 2026-11-11 | Backend (SQLite) | `pytest src/core` · `pytest tests` | 88/88 · 24 aprobadas, 10 omitidas (`postgres`) | — | Ídem |
| 2026-11-11 | Backend (PostgreSQL 16.15) | `DJANGO_SETTINGS_MODULE=config.settings.test_postgres pytest -m postgres tests/integration` | **10/10** (C1–C8 + 2 de infraestructura), varias ejecuciones; `tests/` completo 34/34 | ~9 s | Contenedor desechable `postgres:16`; instrucciones en `backend/tests/integration/README.md` |
| 2026-11-11 | Backend (PostgreSQL 16.15) | `pytest src/apps` | 21 fallos idénticos en `develop` y en la rama (13 `pypdf` + 8 de introspección de índices, H-30) | ~25 s | Auditoría postimplementación |
| 2026-11-11 | Backend | `test_pdf_generator.py` con lector `pdftotext` (plugin de auditoría, sin instalar `pypdf`) | 30/30 en `develop` y en la rama | — | Evidencia de que los 13 fallos son solo la dependencia ausente |
| — | Backend | `pytest` | 497 aprobadas, cobertura 93 %; 13 fallos `pypdf` aceptados (DEC-05 de la spec 003) | — | **Según la documentación** (commit ECLIPSE, DP2); **no reejecutado** en esta sesión (necesita entorno con PostgreSQL) |

## Conclusión

La suite frontend tiene **fallos intermitentes**: 1 de 3 ejecuciones consecutivas, sobre el mismo código, falló en 6 pruebas. No se identificaron qué pruebas fallaron (la salida de la primera ejecución solo conservó el resumen). Hipótesis **no verificada**: timeouts bajo carga (la primera ejecución tardó 139,7 s, con una media de ~2 s de arranque por worker). **Pendiente:** reproducir con `npx vitest run --reporter=verbose` y registrar los nombres de las pruebas.

## Diagnóstico de `router.auth-expiry.test.tsx` (2026-11-12)

- **Prueba afectada:** «un 401 en cualquier petición limpia la sesión y redirige a /login». La segunda prueba del archivo no ha fallado.
- **Frecuencia observada:** 2 fallos en 11 ejecuciones completas; 0 en 3 ejecuciones aisladas. Solo aparece bajo la carga de la suite completa.
- **Síntoma:** expira la espera de «Iniciar sesión» y el DOM sigue mostrando el dashboard **con la sesión activa** (cabecera con ESTUDIANTE). Es decir, el 401 no ejecutó el cierre de sesión.
- **Causa (respaldada, no demostrada al 100 %):** `AuthExpiryBootstrap` (`src/app/router.tsx`) registra el manejador global del 401 en un `useEffect` (efecto pasivo). La prueba lanza `request()` justo cuando aparece el título del dashboard. Como la ruta es `lazy` y se resuelve fuera de `act`, el efecto pasivo puede ejecutarse **después** de que llegue la respuesta 401 de MSW. En ese caso `unauthorizedHandler` todavía es `null` y no se cierra la sesión.
  - **Evidencia:** forzar el 401 antes de que se registre el efecto reproduce el mismo síntoma en 3 de 3 ejecuciones.
  - **Límite del diagnóstico:** una instrumentación con `console.log` no produjo salida y no se usó como evidencia.
- **Impacto:** es una carrera **de la prueba**. En la aplicación, el efecto de `AuthExpiryBootstrap` se ejecuta antes que los efectos de las rutas hermanas que lanzan consultas, así que no hay ventana práctica. No afecta a V-07 ni a V-09: la prueba navega a `/estudiante`.
- **Corrección propuesta** (no aplicada; tarea transversal FE-T1001/FE-T1008, responsable R0yalCode, requiere autorización), una de dos:
  1. Registrar el manejador con `useLayoutEffect`, que se ejecuta en el mismo *commit* que pinta la interfaz.
  2. En la prueba, esperar a que se vacíe la cola de efectos (`await act(async () => {})`) antes de lanzar `request()`.
- **Relación con 2026-11-11:** probablemente explica parte de los 6 fallos sin identificar de esa fecha, pero no está verificado.

## Corrección aplicada (FE-T1001/FE-T1008, 2026-11-12, rama `fix/auth-expiry-401`)

- **Causa decisiva, verificada:** `AuthExpiryBootstrap` estaba **dentro del `Suspense`** de las rutas lazy. Si la ruta inicial suspendía, el componente no se montaba hasta que cargaba la ruta, y un 401 en esa ventana se perdía.
- **Prueba de carrera determinista:** `router.auth-expiry.inicializacion.test.tsx`, en un archivo propio para que la ruta lazy no esté en caché. Lanza el 401 sin esperar al dashboard. Resultados con 3 ejecuciones por variante:

| Variante | Resultado |
|---|---|
| `useEffect` dentro del `Suspense` (anterior) | 0/3 |
| Solo `useLayoutEffect`, dentro del `Suspense` | 0/3: **no basta** |
| Solo fuera del `Suspense` | 3/3 |
| **`useLayoutEffect` + fuera del `Suspense` (adoptada)** | **3/3** |

- **Por qué no se eligió sincronizar la prueba:** solo ocultaba la ventana.
- **Por qué `useLayoutEffect` se mantiene además:** registra el manejador en el mismo *commit* que pinta, antes de cualquier efecto pasivo, también en *commits* fuera de `act`. Así ningún 401 lanzado desde un efecto llega sin manejador.
- **Pruebas nuevas:**
  - La de carrera.
  - Un 401 justo después de pintar el dashboard, repetido 5 veces, en `router.auth-expiry.test.tsx`.
- **Suite completa tras la corrección:** 10 de 10 ejecuciones sin fallos (408/408). Antes fallaba 2 de cada 11 en esta prueba.

## Comandos de verificación obligatorios (DoD)

Frontend: `npm run lint` → `npm run typecheck` → `npm run test` (+ `npm run build`). Backend: `pytest` (ver `backend/pyproject.toml`).

## Pruebas por módulo

Backend: [[02-BACKEND/MODULES|Módulos backend]] · Frontend: [[03-FRONTEND/MODULES|Módulos frontend]] · E2E backend: `backend/tests/e2e/test_full_workflow.py`.
