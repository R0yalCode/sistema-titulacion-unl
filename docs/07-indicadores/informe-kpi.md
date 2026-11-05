---
title: "Informe KPI"
---

# Sistema de indicadores (KPI)

> **Estado**: propuesta técnica. Los endpoints de indicadores no están implementados y requieren autorización expresa (ver informe de auditoría, F-32).

Documento completo: [`docs/indicadores/INFORME_DISENO_KPI.md`](../indicadores/INFORME_DISENO_KPI.md).

## Resumen

| Aspecto | Decisión |
|---|---|
| Roles cubiertos | Los 8 roles reales del código (no se inventaron perfiles) |
| Cálculo | Siempre en backend (capa de servicios de indicadores + agregaciones PostgreSQL) |
| Punto de entrada recomendado | `GET /api/v1/dashboard/me/` — el servidor compone el dashboard según los roles del usuario |
| Endpoints analíticos | `/indicadores/expedientes/`, `/indicadores/culminacion/`, `/indicadores/evolucion/` |
| Permisos | Recurso RBAC `dashboard` (GET) con ámbito own/carrera/facultad/all según rol |
| KPI definidos | 40 |
| Implementables con datos actuales | 33 |
| No implementables hoy | 7 (tutoría, sustentaciones, modalidad, períodos, abandono, usuarios activos, nombres de carrera) |

## Las tres preguntas que responde cada dashboard

1. **¿Cuál es la situación actual?** — tarjetas de estado (expedientes por estado, mi estado, pendientes).
2. **¿Qué requiere atención?** — alertas (plazo vencido, observaciones sin resolver, pendientes de firma/validación).
3. **¿Qué acción debo realizar?** — listas de trabajo enlazadas (cola de atención, checklist, peticiones por emitir).

## Prioridades de implementación

| Fase | Contenido |
|---|---|
| I-1 (P0) | Dashboards de Estudiante, Secretaría, Jurista y Decano con KPIs operativos |
| I-2 (P1) | Director, Dependencia y analíticos de culminación |
| I-3 (P2) | Series de evolución, distribuciones, auditoría |
| I-4 (bloqueado) | KPIs que requieren modelos futuros (tutoría, sustentación, modalidad) |
