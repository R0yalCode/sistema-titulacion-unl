import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { listBandejaEstudiante, type BandejaExpediente } from '@/api/endpoints/expedientes'
import {
  listNotificaciones,
  marcarNotificacionLeida,
  type ListNotificacionesResponse,
} from '@/api/endpoints/notificaciones'
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

export function useNotificaciones() {
  return useQuery<ListNotificacionesResponse, ApiRequestError>({
    queryKey: [NOTIFICACIONES_QUERY_KEY],
    queryFn: listNotificaciones,
    retry: false,
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
