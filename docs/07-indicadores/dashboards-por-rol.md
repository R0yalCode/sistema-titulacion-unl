---
title: "Dashboards por rol"
---

# Dashboards por rol

Detalle completo (tarjetas, alertas, acciones, filtros y periodicidad por rol): [`docs/indicadores/INFORME_DISENO_KPI.md` §5](../indicadores/INFORME_DISENO_KPI.md).

## Resumen visual

| Rol | Tarjetas P0 | Alertas | Acción principal |
|---|---|---|---|
| Estudiante | Mi estado, requisitos pendientes, observados, notificaciones | Observación con motivo; fecha límite | Subsanar / cargar documento |
| Secretaría de Carrera | En atención, plazo vencido, certificados por emitir, por validar | Plazo vencido | Atender cola ordenada por fecha límite |
| Secretario Abogado / Analista | En verificación, por evaluar, observaciones abiertas, listos para informe | Checklist incompleto | Evaluar checklist |
| Decano | Pendientes de declaratoria, firmadas en el período | Cola de firma | Firmar declaratoria |
| Director de Carrera | Activos, culminados, vencidos | Plazo vencido | Supervisar y escalar |
| Responsable de Dependencia | Solicitudes a mi dependencia | Pendientes sin solicitud | Emitir documento |
| Administrador | Usuarios, expedientes por estado, culminados | Anomalías de auditoría | Administrar |

## Estados de UI obligatorios

Cada componente del dashboard implementa: carga (Spinner), vacío (EmptyState con acción), error (ErrorState con reintentar), sin permisos (ForbiddenState) — componentes ya existentes en el design system del frontend, probados con axe.
