---
system: SGT-SIAAF
type: source-note
source_file: Documentacion-parte-2/MATRIZ_KPIS_MODALIDADES_TITULACION.md
source_copy: 90-ORIGINAL-SOURCES/DOCUMENTATION-PART-2/MATRIZ_KPIS_MODALIDADES_TITULACION.md
source_version: "1.0"
source_date: 2026-11-09
nature: kpi-spec (proposal)
vigencia: propuesta; depende-de-INC-03-e-INC-04
last_verified: 2026-11-11
---

# DP2 · Matriz de KPIs de modalidades

**Original:** [[MATRIZ_KPIS_MODALIDADES_TITULACION]]

| ID | Nombre | Prioridad | Fórmula | Endpoint | Roles |
|---|---|---|---|---|---|
| KPI-MOD-01 | Total TIC | P0 | `count(opcion_titulacion='TIC')` | `/indicadores/modalidades/` | Todos |
| KPI-MOD-02 | Total EC | P0 | `count(opcion_titulacion='EC')` | `/indicadores/modalidades/` | Todos |
| KPI-MOD-03 | % TIC / % EC | P0 | `MOD-01/total·100`, `MOD-02/total·100` | `/indicadores/modalidades/` | Todos |
| KPI-MOD-04 | Distribución por carrera | P1 | `group by carrera_id, opcion` | `?agrupar=carrera` | Director, Decano, Admin |
| KPI-MOD-05 | Distribución por período | P1 | `group by year(fecha_recepcion), opcion` | `?agrupar=periodo` | Director, Decano, Admin |
| KPI-MOD-06 | Elegibles para EC | P1 | 2 reprobaciones + 3.ª matrícula (mock SGA) | `/indicadores/elegibilidad-ec/` | Secretario, Decano, Admin |
| KPI-MOD-07 | Habilitados para EC | P1 | `opcion='EC' ∧ estado≠BORRADOR` | `/indicadores/modalidades/` | Secretario, Decano, Admin |
| KPI-MOD-08 | Cambios autorizados | P1 | `count(HistorialModalidad nueva='EC')` | `/indicadores/cambios-modalidad/` | Admin, Decano |

**Regla de no duplicación:** contar por la modalidad **actual**; el historial solo sirve para KPI-MOD-08.

## Observaciones

- Ningún KPI es calculable hoy (no existe el campo ni la app `indicadores`). No deben mostrarse valores simulados (CA-G-01).
- KPI-MOD-05 usa el año de `fecha_recepcion` como "período"; no existe un modelo de período académico (KPI-05 de [[DP2-MATRIZ_BRECHAS]]).
- Diferencia de roles: en el [[DP2-PLAN_MAESTRO]] §5, KPI-MOD-06/07 son para "Secretario, Decano"; aquí se añade Admin.

## Relacionado

[[KPI_CATALOG]] · [[DP2-MATRIZ_INTEGRACION_KPIS]]
