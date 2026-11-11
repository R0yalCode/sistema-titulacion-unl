---
system: SGT-SIAAF
type: source-note
source_file: Documentacion-parte-2/PLAN_INTEGRACION_FRONTEND_BACKEND.md
source_copy: 90-ORIGINAL-SOURCES/DOCUMENTATION-PART-2/PLAN_INTEGRACION_FRONTEND_BACKEND.md
source_version: "1.0"
source_date: 2026-11-09
nature: integration-plan
vigencia: vigente-como-plan
last_verified: 2026-11-11
---

# DP2 · Plan de integración frontend-backend

**Original:** [[PLAN_INTEGRACION_FRONTEND_BACKEND]]

## Contenido

- Estado de la integración (§1) y brechas: modalidades (bloqueante), KPIs/dashboard, vistas de funcionario, búsqueda, exportación, tiempo real y **CORS (BE-08)**.
- Estrategia (§2): el frontend se adapta al comportamiento real; manejo de errores unificado.
- Incrementos INC-01…INC-09 por sprint (§3) y checklists por sprint (§8).
- Tipos compartidos (§4), proxy de Vite y variables de entorno (§5).
- **Discrepancias (§6)** INC-13, INC-19, INC-21 y FE-T407: ver [[API_CONTRACTS]] §2.
- Pruebas de integración (§7): colección Postman/Insomnia, MSW, E2E (Cypress/Playwright: dependencias nuevas).
- Riesgos (§9): CORS, validación normativa, PKI de FirmaEC, SCOPE_ASIGNADO, complejidad de V-07/V-08.

## Verificación

Las discrepancias de §6 coinciden con `clarify.md` (spec 003) y con el código. No menciona GAP-STATE-01, que bloquea el flujo de funcionario (V-08) más allá de `ENVIADA`.

## Relacionado

[[DP2-PLAN_MAESTRO]] · [[FRONTEND_ARCHITECTURE]] · [[BLOCKED_TASKS]]
