---
system: SGT-SIAAF
type: source-note
source_file: Documentacion-parte-2/ARQUITECTURA_DASHBOARDS_POR_ROL.md
source_copy: 90-ORIGINAL-SOURCES/DOCUMENTATION-PART-2/ARQUITECTURA_DASHBOARDS_POR_ROL.md
source_version: "1.0"
source_date: 2026-11-09
nature: architecture (proposal)
vigencia: propuesta; depende-de-INC-04
last_verified: 2026-11-11
---

# DP2 · Arquitectura de dashboards por rol

**Original:** [[ARQUITECTURA_DASHBOARDS_POR_ROL]] · Basado en `docs/indicadores/INFORME_DISENO_KPI.md` y el [[DP2-PLAN_MAESTRO]] §6.

## Contenido

- **Endpoint unificado** `GET /api/v1/dashboard/me/` con secciones `resumen`, `tarjetas_p0`, `grafico_principal`, `tabla_trabajo`, `actividad_reciente`, `notificaciones_no_leidas` y `modalidad_titulacion`.
- **Principios UX (§1.3):** comprensible en ≤ 5 s; máximo 6 tarjetas P0; estados loading/empty/error/forbidden/read-only; AA + axe; responsive desde 320 px; **sin cálculos de negocio en el cliente**.
- **Dashboards por rol (§2):** ESTUDIANTE (`/estudiante`); SECRETARIA_CARRERA, SECRETARIO_ABOGADO/ANALISTA, DECANO, DIRECTOR_CARRERA, RESPONSABLE_DEPENDENCIA y ADMINISTRADOR (todos en `/bandeja`).
- **Componentes (§3):** `KPICard`, `ChartWidget`, `WorkTable`, `ModalidadPanel`.

## Verificación

| Afirmación | Resultado |
|---|---|
| V-02 hecha (`StudentDashboardPage`) | ✅ Usa `GET /expedientes/bandeja/` + `GET /notificaciones/` (no `/dashboard/me/`) |
| V-07/V-08 stubs | ✅ |
| "Componentes base listos: KPICard… — por crear en F3" (§6) | ❌ Contradicción interna: **no existen** |
| Dashboard de Dependencia en `/bandeja` | ⚠️ `RESPONSABLE_DEPENDENCIA` no está en `OPERATIONAL_ROLES` ni en `RBAC_MATRIX` |

## Relacionado

[[DASHBOARD_ARCHITECTURE]] · [[DP2-ESPECIFICACION_SERVICIOS_DASHBOARD]] · [[ROUTES]]
