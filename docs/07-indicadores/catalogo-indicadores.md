---
title: "Catálogo de indicadores"
---

# Catálogo de indicadores

Catálogo formal completo (40 KPI con ID, fórmula, fuente, filtros, visualización y restricciones): [`docs/indicadores/INFORME_DISENO_KPI.md` §6](../indicadores/INFORME_DISENO_KPI.md).

## Índice del catálogo

| Grupo | KPIs | P0 | P1 | P2 |
|---|---|---|---|---|
| Estudiante (KPI-EST-01…08) | 8 | 4 | 3 | 1 |
| Secretaría de Carrera (KPI-SEC-01…08) | 8 | 4 | 3 | 1 |
| Jurista (KPI-JUR-01…07) | 7 | 4 | 3 | 0 |
| Decano (KPI-DEC-01…05) | 5 | 2 | 2 | 1 |
| Director (KPI-DIR-01…07) | 7 | 3 | 2 | 2 |
| Dependencia (KPI-DEP-01…03) | 3 | 1 | 2 | 0 |
| Administrador (KPI-ADM-01…09) | 9 | 3 | 3 | 3 |

## Ejemplos de definición (extracto)

**KPI-SEC-02 — Expedientes con plazo vencido (P0)**
Fórmula: `count(Expediente where carrera_id=mi_carrera and estado not in (DECLARADA_APTA, CANCELADA, BORRADOR) and fecha_limite_atencion < hoy)`. Cuenta **expedientes**, no documentos.

**KPI-DEC-04 — Tasa de culminación (P1)**
Fórmula: `(expedientes DECLARADA_APTA con fecha_recepcion en la cohorte / expedientes con fecha_recepcion en la cohorte) × 100`. Cohorte: trámites enviados formalmente en el rango; BORRADOR excluidos; CANCELADA excluida del numerador y reportada aparte.

**KPI-SEC-08 — Tiempo promedio de atención (P2)**
Fórmula: `avg(fecha_declaratoria − fecha_recepcion)` solo sobre procesos cerrados (DECLARADA_APTA). Los abiertos no se promedian (evita sesgo). Alternativa en días laborables con `dias_laborables_acumulados`.

## Regla de oro

Ningún indicador se calcula con campos inexistentes ni se simula. Los 7 KPI no implementables están documentados con su dependencia explícita (§6.8 del informe).
