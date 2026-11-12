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

## Comandos de verificación obligatorios (DoD)

Frontend: `npm run lint` → `npm run typecheck` → `npm run test` (+ `npm run build`). Backend: `pytest` (ver `backend/pyproject.toml`).

## Pruebas por módulo

Backend: [[02-BACKEND/MODULES|Módulos backend]] · Frontend: [[03-FRONTEND/MODULES|Módulos frontend]] · E2E backend: `backend/tests/e2e/test_full_workflow.py`.
