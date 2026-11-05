import { request } from '../client'

export type NotificacionInterna = {
  id: string
  expediente: string
  expediente_numero: string
  peticion: string | null
  peticion_requisito_nombre: string | null
  titulo: string
  mensaje: string
  leida: boolean
  fecha_creacion: string
}

/**
 * `GET /api/v1/notificaciones/` real (no `openapi.yaml`, que lo declara como
 * array plano, ni `specify.md`, que lo describe como "paginado; estructura
 * estándar DRF"): la vista fija `pagination_class = None` y envuelve el
 * resultado en `{ results: [...] }`, sin `count`/`next`/`previous`. Se
 * implementa contra el código real, no contra la documentación desactualizada.
 */
export type ListNotificacionesResponse = {
  results: NotificacionInterna[]
}

export function listNotificaciones(): Promise<ListNotificacionesResponse> {
  return request<ListNotificacionesResponse>('/api/v1/notificaciones/')
}

export function marcarNotificacionLeida(id: string): Promise<NotificacionInterna> {
  return request<NotificacionInterna>(`/api/v1/notificaciones/${id}/marcar-leida/`, {
    method: 'PATCH',
  })
}
