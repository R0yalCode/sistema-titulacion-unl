---
system: SGT-SIAAF
type: kpi-catalog
status: proposal
source: docs/indicadores/INFORME_DISENO_KPI.md + Documentacion-parte-2
last_verified: 2026-11-11
---

# Catálogo de KPIs

> **Ningún KPI está implementado como servicio o endpoint.** No existe la app `indicadores` (verificado 2026-11-11). La V-02 muestra **datos reales** (bandeja y notificaciones), no KPIs calculados. Regla vinculante: no simular valores (CA-G-01; INFORME_DISENO_KPI §6.8).

**Fuente principal:** `docs/indicadores/INFORME_DISENO_KPI.md` (propuesta, 2026-11-05, basada en el código real). Extensión de modalidades: [[DP2-MATRIZ_KPIS_MODALIDADES]]. Mapeo a endpoints: [[DP2-MATRIZ_INTEGRACION_KPIS]].

## 1. KPIs por rol (identificadores de la fuente)

| Rol | IDs | Nombres |
|---|---|---|
| ESTUDIANTE | KPI-EST-01…08 | Estado actual · Requisitos pendientes · Requisitos observados · Documentos vigentes · Notificaciones sin leer · Fecha límite · Progreso del checklist · Hitos |
| SECRETARIA_CARRERA | KPI-SEC-01…08 | En atención · Plazo vencido · Certificados por emitir · Documentos por validar · Solicitudes del período · Observados abiertos · Culminados del período · Tiempo promedio de atención |
| SECRETARIO_ABOGADO / ANALISTA | KPI-JUR-01…07 | En verificación · Requisitos por evaluar · Observaciones sin resolver · Listos para informe · Informes del período · Observados esperando subsanación · Plazo vencido |
| DECANO | KPI-DEC-01…05 | Pendientes de declaratoria · Declaratorias del período · Activos de la facultad · Tasa de culminación · Distribución por estado |
| DIRECTOR_CARRERA | KPI-DIR-01…07 | Activos · Culminados · Plazo vencido · Tasa de culminación · Tiempo promedio · Distribución por estado · Distribución por período académico |
| RESPONSABLE_DEPENDENCIA | KPI-DEP-01…03 | Solicitudes a mi dependencia · Pendientes sin solicitud · Observadas por corregir |
| ADMINISTRADOR | KPI-ADM-01…09 | Usuarios · Expedientes por estado · Culminados · Tasa global · Tiempo promedio · Evolución mensual · Por carrera · Auditoría por acción · Usuarios activos |
| Modalidades | KPI-MOD-01…08 | Ver [[DP2-MATRIZ_KPIS_MODALIDADES]] |

**Inconsistencia de la fuente:** §16 dice "40 KPI definidos (EST 8, SEC 8, JUR 7, DEC 5, DIR 7, DEP 3, ADM 9…)", pero esa suma da **47**; la fuente lo atribuye a "solapamientos de fórmula reutilizados por ámbito". DP2 repite "40" y "33 implementables". Pendiente de aclarar por su autor.

## 2. No implementables hoy (INFORME_DISENO_KPI §6.8)

| KPI solicitado | Dependencia |
|---|---|
| Tutores y cargas de tutor | Modelo de tutoría (no existe) |
| Sustentaciones y resultados | Modelo de sustentación (Fase 2) |
| Distribución por modalidad | `opcion_titulacion` (BE-06) |
| Período académico oficial | Catálogo de períodos o SGA |
| Nombres de carrera/facultad | Catálogo de carreras (BE-10) |
| Procesos abandonados | Definición institucional |
| Usuarios activos reales (KPI-ADM-09) | Registro de sesiones (INC-02) |

## 3. Endpoints propuestos

`GET /api/v1/dashboard/me/`, `/indicadores/modalidades/`, `/indicadores/culminacion/`, `/indicadores/evolucion/`, `/indicadores/elegibilidad-ec/`, `/indicadores/cambios-modalidad/`, `/indicadores/usuarios-activos/`. Ninguno existe ([[API_CONTRACTS]] §3).

## Relacionado

[[DASHBOARD_ARCHITECTURE]] · [[DP2-ESPECIFICACION_SERVICIOS_DASHBOARD]] · Documentación previa: `docs/07-indicadores/`
