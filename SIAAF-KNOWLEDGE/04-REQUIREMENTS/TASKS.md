---
system: SGT-SIAAF
type: requirements
area: tasks
status: verified
source: sgt-siaaf/specs/003-frontend-titulacion/tasks.md
last_verified: 2026-11-11
---

# Tareas (estado resumido)

> **Fuente única de estados:** `sgt-siaaf/specs/003-frontend-titulacion/tasks.md` (frontend) y `sgt-siaaf/specs/001-tramite-titulacion/tasks.md` (backend MVP). Esta nota es un **resumen fechado**; ante cualquier duda, manda `tasks.md`. Orden de lotes: `tasks.md` §18; DoD: §19.

## Frontend (spec 003): recuento del 2026-11-11

Recuento automático de las líneas `**Estado**` por tarea: **53 "Hecha"**, **46 "Pendiente"**, **1 "Bloqueada"** (FE-T1213), y algunas tareas con estado redactado en prosa (FE-T205 parcial, FE-T305, FE-T401, FE-T409, FE-T411, cerradas con evidencia en el texto).

| Fase / vista | Tareas | Estado |
|---|---|---|
| F0 Andamiaje | FE-T001…T010, FE-T1210 | Hecha |
| F1 Auth | FE-T011…T017 | Hecha |
| F2 UI Kit | FE-T019…T028 | Hecha |
| F2.5 Errores | FE-T1211, FE-T1212, FE-T1214 | Hecha |
| F2.5 Errores | **FE-T1213** (409/412/428) | **Bloqueada** (BE-11) |
| V-01 Login | FE-T101…T104 | Hecha |
| V-02 Dashboard | FE-T201…T206 | Hecha |
| V-03 Solicitud | FE-T301…T306 | Hecha |
| V-04 Expediente | FE-T401…T411 | Hecha |
| V-05 Peticiones | FE-T501…T506 | Pendiente |
| V-06 Seguimiento | FE-T601…T605 | Pendiente |
| V-07 Bandeja | FE-T701…T706 | Pendiente |
| V-08 Detalle funcionario | FE-T801…T810 | Pendiente |
| V-09 No habilitado | FE-T901…T904 | Pendiente (la página ya existe) |
| Transversales | FE-T1001…T1010 | Pendiente |
| Calidad final | FE-T1101…T1105 | Pendiente |

**Siguiente lote según `CLAUDE.md`:** V-05 y fases posteriores requieren **autorización explícita independiente**.

## Backend: dependencias no autorizadas

BE-01…BE-11: ver [[BLOCKED_TASKS]].

## Relacionado

[[SPECIFY]] · [[BLOCKED_TASKS]] · [[CURRENT_STATE]]
