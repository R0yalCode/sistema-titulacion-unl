---
system: SGT-SIAAF
type: evidence-index
status: active
source: knowledge-build-session
last_updated: 2026-11-11
---

# Índice de evidencias

Evidencias **ejecutadas** (no solo documentadas). Añadir una fila por evidencia nueva.

| ID | Fecha | Qué se comprobó | Comando / método | Resultado |
|---|---|---|---|---|
| EV-001 | 2026-11-11 | Integridad de la copia de los 12 MD de DP2 | `sha256sum -c` | 12/12 OK |
| EV-002 | 2026-11-11 | Endpoints reales frente a OpenAPI | `config/urls.py` + parseo de `openapi.yaml` | 16 rutas, 17 operaciones; coinciden |
| EV-003 | 2026-11-11 | `openapi.yaml` frente a `contracts/openapi.yaml` | `cmp` | Idénticos |
| EV-004 | 2026-11-11 | Ausencia de modalidades, `indicadores`, sesiones | `grep`/`ls` en `backend/src` | Ausentes |
| EV-005 | 2026-11-11 | Falta la transición `ENVIADA→EN_VERIFICACION` | `grep -rn EN_VERIFICACION` en servicios/vistas/señales | Solo los tests la asignan |
| EV-006 | 2026-11-11 | RBAC real | Lectura de `RBAC_MATRIX` | [[PERMISSIONS_ROLES]] |
| EV-007 | 2026-11-11 | Suite frontend (ejecución 1) | `npm run test` | 322/328 (6 fallos, 2 archivos) |
| EV-008 | 2026-11-11 | Suite frontend (ejecución 3) | `npx vitest run` | 328/328 |
| EV-009 | 2026-11-11 | MCP de Obsidian conectado | `claude mcp list` / `get obsidian` | Connected, HTTP `localhost:8765` |
| EV-010 | 2026-11-11 | Bóvedas externas | Inspección de la papelera y de `obsidian.json` | Vacías (solo `.obsidian`) |
| EV-011 | 2026-11-11 | Wikilinks y secretos de la bóveda | Script de enlaces + `grep` de patrones de secreto | Ver [[BUILD_REPORT]] §21 |
| EV-012 | 2026-11-11 | Operaciones MCP | `search_notes`, `read_note(heading)`, `patch_note` | Ver [[BUILD_REPORT]] §19 |

Evidencias previas del proyecto (no reejecutadas): `docs/09-calidad/resultados-validacion.md`, `DOCUMENTACION/07_PRUEBAS/RESULTADOS_VALIDACION.md`, `docs/auditoria-backend/INFORME_FINAL_VALIDACION.md`, `docs/auditoria-backend/seguridad/INFORME_PRUEBAS_SEGURIDAD.md`, `docs/10-auditoria-2026-11/pruebas-reales.qmd`, registro de evidencias en `sgt-siaaf/specs/003-frontend-titulacion/tasks.md`.
