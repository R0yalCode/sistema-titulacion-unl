---
title: "Inventario de módulos"
---

# Inventario de módulos

Inventario verificado contra el código (05-11-2026). Detalle por módulo en las páginas enlazadas.

| ID | Módulo | Objetivo | Modelos | Endpoints | Pruebas | Estado |
|---|---|---|---|---|---|---|
| M-01 | [authentication](modulo-authentication.md) | Identidad, roles, JWT, RBAC | 3 | 1 | 28 | Implementado y verificado |
| M-02 | [expedientes](modulo-expedientes.md) | Ciclo de vida del expediente y plazos | 2 | 5 | 73 | Implementado y verificado |
| M-03 | [peticiones](modulo-peticiones.md) | Requisitos Art. 235 y documentos PDF | 3 | 4 | 85 | Implementado y verificado |
| M-04 | [verificacion](modulo-verificacion.md) | Checklist, observaciones, subsanación | 2 | 3 | 72 | Implementado y verificado |
| M-05 | [resoluciones](modulo-resoluciones.md) | Informe 590 y declaratoria 162 | 2 | 2 | 113 | Implementado y verificado |
| M-06 | [notificaciones](modulo-notificaciones.md) | Notificaciones in-app y auditoría | 2 | 2 | 71 | Implementado (con limitaciones) |
| M-07 | [core](modulo-core.md) | Infraestructura compartida | 0 | 0 | 71 | Implementado y verificado |

**Totales**: 14 modelos, 17 operaciones API, 526 pruebas.

## Procesos críticos cubiertos

| Proceso | Módulos | Estado |
|---|---|---|
| Registro de solicitudes | M-02, M-03 | Completo |
| Validación de requisitos | M-03, M-04 | Completo |
| Gestión de propuestas | — | **Fuera de Fase 1** (no existe en el modelo) |
| Asignación de tutores | — | **Fuera de Fase 1** |
| Desarrollo y seguimiento del trabajo | — | **Fuera de Fase 1** |
| Gestión de sustentaciones | — | **Fuera de Fase 1** |
| Registro de calificaciones | — | **Fuera de Fase 1** |
| Finalización del proceso | M-05 | Completo (declaratoria de aptitud legal) |
| Registro de titulados | — | **Fuera de Fase 1** |

> Nota de honestidad documental: la Fase 1 del proyecto cubre únicamente la Declaratoria de Aptitud Legal. Los procesos de propuesta, tutoría, sustentación y titulados pertenecen a fases futuras y **no deben documentarse como implementados**.
