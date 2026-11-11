---
system: SGT-SIAAF
type: source-note
source_file: Documentacion-parte-2/MATRIZ_INTEGRACION_KPIS_ENDPOINTS.md
source_copy: 90-ORIGINAL-SOURCES/DOCUMENTATION-PART-2/MATRIZ_INTEGRACION_KPIS_ENDPOINTS.md
source_version: "1.0"
source_date: 2026-11-09
nature: integration-matrix (proposal)
vigencia: propuesta; depende-de-INC-04
last_verified: 2026-11-11
---

# DP2 · Matriz de integración KPI → endpoint

**Original:** [[MATRIZ_INTEGRACION_KPIS_ENDPOINTS]]

## Contenido

- **Nueva app `indicadores`** con fórmulas centralizadas (§1).
- **Composición de `/dashboard/me/` (§2.1):** `get_kpi_clave`, `get_alertas`, `get_tarjetas_p0`, `get_grafico_principal`, `get_tabla_trabajo`, `get_actividad_reciente`, `NotificacionService` (no leídas, SCOPE_OWN) y `get_modalidad_dashboard`, con el ámbito resuelto por `ScopeFilterMixin`.
- **Endpoints analíticos (§2.2):** `/indicadores/modalidades/` (KPI-MOD-01…08), `/indicadores/culminacion/` (KPI-SEC-08, DEC-04, DIR-04/05, ADM-04/05), `/indicadores/evolucion/` (KPI-SEC-05, ADM-06, DIR-07), `/indicadores/elegibilidad-ec/` (KPI-MOD-06).
- KPIs por rol (§3), SQL de PostgreSQL optimizado (§5: conteos, serie mensual con `generate_series`, tiempo promedio, listos para informe, modalidades), RBAC (§6), serializers (§7) y estrategia de pruebas (§8).

## Estado (§10, confirmado)

Diseño de 40 KPIs: hecho (en `docs/indicadores/INFORME_DISENO_KPI.md`). App, servicios, endpoints, permisos y tests: **no existen**. Frontend: solo V-02.

> Los identificadores `KPI-DEC-04` y `DEC-04` (decisión de la spec 001) son homónimos sin relación; ver [[GLOSSARY]].

## Relacionado

[[KPI_CATALOG]] · [[DP2-ESPECIFICACION_SERVICIOS_DASHBOARD]]
