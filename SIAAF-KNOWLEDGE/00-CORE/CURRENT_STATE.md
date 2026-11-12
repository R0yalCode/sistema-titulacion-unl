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
| Seguridad | Controles base implementados (ECLIPSE v0.4.0); VULN-001/002/003 cerradas el 2026-11-11 (INC-01, commit `0a24109`, integrado en `develop`); E2-06 hecha (aprobada con observaciones O-1/O-2/O-3) y E2-01 hecha (inicio de verificación, AUT-02); **PLB-E1-04 + O-2 hecha el 2026-11-11** (errores de dominio sin 500 genéricos, bloqueo expediente → petición → checklist, H-29 corregido; cinco commits en `fix/e1-04-errores-dominio`, modalidad centralizada DK-010; integración local en `develop` sin publicar); VULN-005/006/010 abiertas. Plan backend nuevo: `docs/planificacion-backend/` (etapas E0–E7, decisiones DP-01…DP-17) | [[06-AUDITS/SECURITY/SECURITY_AUDIT|Auditoría de seguridad]] |
| Modalidades TIC/EC | **No implementadas**; normativa sin validar | [[COMPREHENSIVE_EXAMINATION]] |
| KPIs/dashboards | **No implementados** (solo V-02 con datos reales) | [[KPI_CATALOG]] |
| Planificación | DP2: INC-01…INC-09; ruta crítica INC-01→03→04→08/07→09 | [[DP2-PLAN_MAESTRO]] |
| Bóveda SIAAF-KNOWLEDGE | Construida el 2026-11-11 | [[BUILD_REPORT]] |

## Pruebas (última ejecución)

Frontend: 328/328 en la 3.ª ejecución; **1 de 3 ejecuciones falló (6 pruebas): intermitencia sin diagnosticar** → [[REGRESSION_TESTS]]. Backend (2026-11-11, PLB-E1-04 + O-2): `pytest` → 606 aprobadas, 13 fallidas (`test_pdf_generator.py`, `pypdf` ausente, deuda previa); `src/core` 88/88; `tests/` 24 aprobadas + 10 omitidas con SQLite; **PostgreSQL 16.15**: C1–C8 + infraestructura 10/10, `tests/` 34/34. Detalle en [[REGRESSION_TESTS]].

## Bloqueos y decisiones humanas pendientes

1. ~~GAP-STATE-01~~ → **resuelta** por E2-01 (2026-11-11). O-2 → **resuelta** por PLB-E1-04 (2026-11-11). Pendientes: **O-1** (decisión funcional; hoy 409 `regla_pendiente_o1`), H-26 (DP-05b), DP-01b, ~~notificación de cuatro integrantes (DK-010, I-1)~~ (**no requerida** desde la enmienda de DK-010 del 2026-11-12), I-3 (archivos huérfanos) **corregido en `fix/i3-archivos-huerfanos`** (2026-11-12, pendiente de integración), `contracts/openapi.yaml` divergente desde INC-01 (I-4).
2. RBAC de `RESPONSABLE_DEPENDENCIA` (emite 3 de los 5 requisitos) y `CANCELADA` sin operación.
3. BE-01…BE-11 no autorizadas; FE-T1213 bloqueada (BE-11).
4. Validación normativa de los Arts. 39, 40, 212, 216 y 233 para las modalidades.
5. Autorización para iniciar V-05 (siguiente lote del frontend) o INC-01 (seguridad P0).
6. ~~Confirmar la política Git~~ → **confirmada** (DK-008): flujo `main` → `develop` → ramas; preguntar siempre antes de fusionar en `main`.
7. Versionar `DOCUMENTACION/` y `.github/workflows/` (hoy sin seguimiento Git).

## Próximo paso recomendado por el plan

INC-01 (seguridad P0) en el backend; en el frontend, el siguiente lote de `tasks.md` §18 (V-05), con autorización.
