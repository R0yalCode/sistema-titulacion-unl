---
system: SGT-SIAAF
type: audit-index
area: backend
status: indexed
source: repository-docs
last_verified: 2026-11-11
aliases: [TECHNICAL_REPORT, REFACTORING_PLAN]
---

# Auditorías técnicas: índice

> Índice de los informes de auditoría existentes. **No se reprodujo su contenido**: leer la sección concreta en el original. El estado real de lo que afirman se contrasta en las notas de módulo.

## Backend (`docs/auditoria-backend/`)

| Documento | Tamaño | Tema |
|---|---|---|
| `INFORME_TECNICO_BACKEND.md` | 28 KB | Informe técnico del backend |
| `PLAN_REFACTORIZACION.md` | 39 KB | Plan de refactorización |
| `MATRIZ_PERMISOS_ROLES.md` | 15 KB | Matriz de permisos (contrastada en [[PERMISSIONS_ROLES]]) |
| `MATRIZ_COMPATIBILIDAD_BACKEND_FRONTEND.md` | 24 KB | Compatibilidad de contrato |
| `PLAN_ADAPTACIONES_FRONTEND.md` | 23 KB | Adaptaciones del frontend |
| `REGISTRO_CAMBIOS_BACKEND_FRONTEND.md` | 21 KB | Registro de cambios |
| `AUDITORIA_SEGURIDAD.md`, `INFORME_FINAL_VALIDACION.md`, `TASKS_SEGURIDAD.md`, `seguridad/**` | — | Ver [[06-AUDITS/SECURITY/SECURITY_AUDIT|Auditoría de seguridad]] |

## Auditoría general (`auditoria/`, 8 informes)

`01_AUDITORIA_GENERAL`, `02_INVENTARIO_TECNICO`, `03_MATRIZ_FUNCIONAL`, `04_AUDITORIA_ARQUITECTONICA`, `05_AUDITORIA_SDD`, `06_AUDITORIA_SEGURIDAD_Y_CALIDAD`, `07_DEUDA_TECNICA_Y_RIESGOS`, `08_RECOMENDACIONES_DE_MEJORA`.

## Otras auditorías

| Ubicación | Contenido |
|---|---|
| `docs/auditoria/INFORME_AUDITORIA_TECNICA.md` (47 KB), `PLAN_MEJORA_TECNICA.md`, `matriz-trazabilidad.md` | Auditoría técnica; base del informe KPI |
| `docs/10-auditoria-2026-11/*.qmd` | Auditoría de noviembre 2026 (arquitectura, BPMN, pruebas reales) |
| `docs/sprint-S1/S1_01…S1_06`, `S1_INFORME_IMPLEMENTACION.md` | Validación de hallazgos y diagnóstico del sprint S1 |
| `DOCUMENTACION/00_AUDITORIA/` | Auditoría documental, inventario, cumplimiento inicial (sin seguimiento Git) |

## Frontend

No hay un informe de auditoría propio; la "auditoría con evidencia" del 2026-11-04 está en `sgt-siaaf/specs/003-frontend-titulacion/tasks.md` §1.1.

## Relacionado

[[02-BACKEND/MODULES|Módulos backend]] · [[SOURCE_CATALOG]]
