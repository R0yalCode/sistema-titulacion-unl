---
title: "Endpoints: Notificaciones"
---

# Notificaciones

## GET /api/v1/notificaciones/

Listado de notificaciones del usuario autenticado (T038). **Sin paginación** (intencional); respuesta envuelta en `results`.

- **Parámetro de consulta**: `leida` (boolean opcional: `true`/`false`).
- **Roles**: todos los autenticados (siempre ámbito `own`: `usuario_destino = request.user`).
- **200**: `{ "results": [NotificacionInterna] }` con `id, expediente, expediente_numero, peticion, peticion_requisito_nombre, titulo, mensaje, leida, fecha_creacion`. Orden descendente por `fecha_creacion`.
- **401** si no hay token.

## PATCH /api/v1/notificaciones/{id}/marcar-leida/

Marca una notificación como leída.

- **Parámetro de ruta**: `id` UUID.
- **Cuerpo**: vacío (`NotificacionMarcarLeidaRequest` sin campos).
- **Roles**: únicamente el destinatario (doble verificación: scope + propiedad explícita).
- **Respuestas**:

| Código | Cuerpo |
|---|---|
| 200 | `NotificacionInterna` con `leida: true` |
| 404 | inexistente o de otro usuario |
| 401 | sin token |
