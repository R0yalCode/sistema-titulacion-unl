---
system: SGT-SIAAF
type: source-note
source_file: Documentacion-parte-2/ESPECIFICACION_SERVICIOS_DASHBOARD.md
source_copy: 90-ORIGINAL-SOURCES/DOCUMENTATION-PART-2/ESPECIFICACION_SERVICIOS_DASHBOARD.md
source_version: "1.0"
source_date: 2026-11-09
nature: service-spec (proposal)
vigencia: propuesta; depende-de-INC-04
last_verified: 2026-11-11
---

# DP2 · Especificación de servicios de dashboard

**Original:** [[ESPECIFICACION_SERVICIOS_DASHBOARD]] (el documento más extenso de DP2, 713 líneas, con código de ejemplo).

## Estructura propuesta (`backend/src/apps/indicadores/`, inexistente)

`services/`: `indicadores.py` (base), `kpi_estudiante.py` (KPI-EST-01…08), `kpi_secretaria.py` (KPI-SEC-01…08), `kpi_jurista.py` (KPI-JUR-01…07), `kpi_decano.py` (KPI-DEC-01…05), `kpi_director.py` (KPI-DIR-01…07), `kpi_dependencia.py` (KPI-DEP-01…03), `kpi_admin.py` (KPI-ADM-01…09), `kpi_modalidades.py` (KPI-MOD-01…08), `kpi_general.py`.
Más: viewsets (§4), serializers (§5), RBAC (§6, incluida la adición a `ROW_TO_SCOPE`), URLs (§7), tests (§8) y consumo frontend (`features/dashboard/queries.ts`, §9).

Principios: una función por KPI (`get_kpi_<id>`), firma `(user, ambito, filtros)`, sin lógica HTTP, tests con casos 0, 1, N y vacío.

## Criterios de aceptación (§10, conservados)

1. Un solo endpoint `/dashboard/me/`. 2. Servicios centralizados. 3. Ámbito derivado del JWT, nunca de parámetros del cliente. 4. Agregaciones en BD (sin N+1). 5. Filtros en lista blanca (`meses ≤ 24`). 6. `Cache-Control: no-store`. 7. RBAC `dashboard` + `indicadores:*`. 8. Cobertura ≥ 90 %. 9. TanStack Query con `staleTime` de 30 s. 10. AA.

## Observación

El criterio 3 choca con la realidad del JWT: hoy no lleva `carrera`/`facultad` (BE-01, no autorizada). El ámbito tendría que salir de `User.carrera_id`/`facultad_id` en el servidor.

## Relacionado

[[KPI_CATALOG]] · [[DASHBOARD_ARCHITECTURE]] · [[DP2-MATRIZ_INTEGRACION_KPIS]]
