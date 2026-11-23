import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { listBandejaEstudiante, type BandejaExpediente } from '@/api/endpoints/expedientes'
import {
  listNotificaciones,
  marcarNotificacionLeida,
  type ListNotificacionesResponse,
} from '@/api/endpoints/notificaciones'
import { getMiTramite, type MiTramite } from '@/api/endpoints/miTramite'
import type { ApiRequestError } from '@/api/errors'
import type { Paginated } from '@/api/types/api'

export const BANDEJA_ESTUDIANTE_QUERY_KEY = 'bandeja-estudiante'
export const NOTIFICACIONES_QUERY_KEY = 'notificaciones'

const PAGE_SIZE = 10

export function useBandejaEstudiante(page: number) {
  return useQuery<Paginated<BandejaExpediente>, ApiRequestError>({
    queryKey: [BANDEJA_ESTUDIANTE_QUERY_KEY, page],
    queryFn: () => listBandejaEstudiante({ page, pageSize: PAGE_SIZE }),
    retry: false,
  })
}

/**
 * Clave anidada bajo `BANDEJA_ESTUDIANTE_QUERY_KEY` a propósito: las
 * mutaciones existentes del estudiante (crear, enviar, cargar documento,
 * solicitar emisión) ya invalidan ese prefijo, de modo que el panel se
 * refresca sin acoplar esos módulos a esta vista.
 */
export const MI_TRAMITE_QUERY_KEY = [BANDEJA_ESTUDIANTE_QUERY_KEY, 'mi-tramite'] as const

export function useMiTramite() {
  return useQuery<MiTramite, ApiRequestError>({
    queryKey: MI_TRAMITE_QUERY_KEY,
    queryFn: getMiTramite,
    retry: false,
    // Al volver al panel tras una acción (p. ej. subsanar), se muestran datos actuales.
    refetchOnMount: 'always',
  })
}

/** `enabled: false` para roles sin acceso RBAC a notificaciones (evita un 403 inútil). */
export function useNotificaciones(options: { enabled?: boolean } = {}) {
  return useQuery<ListNotificacionesResponse, ApiRequestError>({
    queryKey: [NOTIFICACIONES_QUERY_KEY],
    queryFn: listNotificaciones,
    retry: false,
    enabled: options.enabled ?? true,
  })
}

export function useMarcarNotificacionLeida() {
  const queryClient = useQueryClient()

  return useMutation<unknown, ApiRequestError, string>({
    mutationFn: (id: string) => marcarNotificacionLeida(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [NOTIFICACIONES_QUERY_KEY] })
    },
  })
}
