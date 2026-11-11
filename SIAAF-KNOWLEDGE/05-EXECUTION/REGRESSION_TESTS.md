---
system: SGT-SIAAF
type: execution
area: tests
status: verified
source: test-runs
last_verified: 2026-11-11
---

# Pruebas y regresión

## Ejecuciones registradas

| Fecha | Suite | Comando | Resultado | Duración | Contexto |
|---|---|---|---|---|---|
| 2026-11-11 | Frontend | `npm run test` (`vitest run`) | **6 fallidas / 322 aprobadas (328)**; 2 archivos con fallos de 58 | 139,7 s | Rama `docs/siaaf-knowledge`; sin cambios de código |
| 2026-11-11 | Frontend | `npx vitest run` (2.ª ejecución) | Sin líneas `FAIL` en la salida filtrada | — | Ídem |
| 2026-11-11 | Frontend | `npx vitest run` (3.ª ejecución) | **58/58 archivos, 328/328 pruebas aprobadas** | — | Ídem |
| 2026-11-05 | Frontend | — | 328/328 (según `CLAUDE.md`, cierre de V-04) | — | Registro previo, no reejecutado |
| — | Backend | `pytest` | 497 aprobadas, cobertura 93 %; 13 fallos `pypdf` aceptados (DEC-05 de la spec 003) | — | **Según la documentación** (commit ECLIPSE, DP2); **no reejecutado** en esta sesión (necesita entorno con PostgreSQL) |

## Conclusión

La suite frontend tiene **fallos intermitentes**: 1 de 3 ejecuciones consecutivas, sobre el mismo código, falló en 6 pruebas. No se identificaron qué pruebas fallaron (la salida de la primera ejecución solo conservó el resumen). Hipótesis **no verificada**: timeouts bajo carga (la primera ejecución tardó 139,7 s, con una media de ~2 s de arranque por worker). **Pendiente:** reproducir con `npx vitest run --reporter=verbose` y registrar los nombres de las pruebas.

## Comandos de verificación obligatorios (DoD)

Frontend: `npm run lint` → `npm run typecheck` → `npm run test` (+ `npm run build`). Backend: `pytest` (ver `backend/pyproject.toml`).

## Pruebas por módulo

Backend: [[02-BACKEND/MODULES|Módulos backend]] · Frontend: [[03-FRONTEND/MODULES|Módulos frontend]] · E2E backend: `backend/tests/e2e/test_full_workflow.py`.
