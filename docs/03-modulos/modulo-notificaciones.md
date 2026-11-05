---
title: "Módulo: notificaciones"
---

# M-06 — notificaciones

| Campo | Valor |
|---|---|
| Objetivo | Notificaciones internas in-app (DEC-01) y bitácora inmutable de auditoría |
| Roles | Todos (cada usuario ve lo suyo) |

## Modelos

| Modelo | Campos clave | Restricciones |
|---|---|---|
| `NotificacionInterna` | `titulo`, `mensaje`, `leida`, `fecha_creacion` | FK usuario destino + expediente (+ petición opcional); 4 índices |
| `EventoAuditoria` | `accion` (10 valores TextChoices), `rol_usuario`, `ip`, `detalles` JSONB | FK PROTECT usuario/expediente; 4 índices temporales |

## Endpoints

| Método | Ruta | Caso de uso |
|---|---|---|
| GET | `/api/v1/notificaciones/` | Listado propio (`?leida=true|false`); sin paginación |
| PATCH | `/api/v1/notificaciones/{id}/marcar-leida/` | Marcar leída con doble verificación de propiedad |

## Reglas de negocio

1. El listado filtra siempre por `usuario_destino = request.user` (además del scope).
2. Despacho **sincrónico in-process** (sin cola ni correo): helpers por evento (observación, subsanación jurista/estudiante, informe, declaratoria).
3. Auditoría por signals `post_save` sobre Expediente, HistorialEstado, Checklist, Observación, Documento, Informe y Declaratoria; JSONB inmutable.

## Pruebas (71)

Servicio (17), endpoints (12), auditoría (14), integración (28).

## Estado y limitaciones

- **Implementado** con limitaciones conocidas:
  - Eventos `SUBSANACION_REALIZADA`, `EXPEDIENTE_ENVIADO`, `EXPEDIENTE_CANCELADO` definidos pero nunca emitidos (AUD-P3-02).
  - `ip` siempre vacía: `_get_current_request()` devuelve `None` (AUD-P2-06).
  - En cambio de estado por signal, el usuario de respaldo es el estudiante (no el actor real de la operación).
  - Sin paginación en el listado (aceptable con volúmenes actuales; revisar a futuro).
