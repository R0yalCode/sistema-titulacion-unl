---
system: SGT-SIAAF
type: current-state
status: active
source: verified-code + tasks.md + test-runs
last_verified: 2026-11-11
---

# Estado actual del proyecto

> Instantánea verificada el **2026-11-11**. Actualizar al cerrar cada tarea ([[KNOWLEDGE_MAINTENANCE]]).

## Resumen

| Área | Estado | Detalle |
|---|---|---|
| Backend Fase 1 | **Implementado con brechas** | 6 apps, 17 operaciones API, 12 migraciones → [[02-BACKEND/MODULES|Módulos backend]] |
| Frontend | **F0, F1, F2, F2.5, V-01…V-04 cerradas**; V-05…V-09 y transversales pendientes | [[TASKS]], [[ROUTES]] |
| Seguridad | Controles base implementados (ECLIPSE v0.4.0); VULN-001/002/003 cerradas el 2026-11-11 (INC-01, rama `security/inc-01-endurecimiento-backend`, sin commit); VULN-005/006/010 abiertas. Plan backend nuevo: `docs/planificacion-backend/` (etapas E0–E7, decisiones DP-01…DP-17) | [[06-AUDITS/SECURITY/SECURITY_AUDIT|Auditoría de seguridad]] |
| Modalidades TIC/EC | **No implementadas**; normativa sin validar | [[COMPREHENSIVE_EXAMINATION]] |
| KPIs/dashboards | **No implementados** (solo V-02 con datos reales) | [[KPI_CATALOG]] |
| Planificación | DP2: INC-01…INC-09; ruta crítica INC-01→03→04→08/07→09 | [[DP2-PLAN_MAESTRO]] |
| Bóveda SIAAF-KNOWLEDGE | Construida el 2026-11-11 | [[BUILD_REPORT]] |

## Pruebas (última ejecución)

Frontend: 328/328 en la 3.ª ejecución; **1 de 3 ejecuciones falló (6 pruebas): intermitencia sin diagnosticar** → [[REGRESSION_TESTS]]. Backend: 497 según la documentación, no reejecutado.

## Bloqueos y decisiones humanas pendientes

1. **GAP-STATE-01**: no existe la transición `ENVIADA→EN_VERIFICACION` por API → ¿se autoriza una tarea backend? ([[BLOCKED_TASKS]])
2. RBAC de `RESPONSABLE_DEPENDENCIA` (emite 3 de los 5 requisitos) y `CANCELADA` sin operación.
3. BE-01…BE-11 no autorizadas; FE-T1213 bloqueada (BE-11).
4. Validación normativa de los Arts. 39, 40, 212, 216 y 233 para las modalidades.
5. Autorización para iniciar V-05 (siguiente lote del frontend) o INC-01 (seguridad P0).
6. ~~Confirmar la política Git~~ → **confirmada** (DK-008): flujo `main` → `develop` → ramas; preguntar siempre antes de fusionar en `main`.
7. Versionar `DOCUMENTACION/` y `.github/workflows/` (hoy sin seguimiento Git).

## Próximo paso recomendado por el plan

INC-01 (seguridad P0) en el backend; en el frontend, el siguiente lote de `tasks.md` §18 (V-05), con autorización.
