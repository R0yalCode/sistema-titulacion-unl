import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  getExpedienteDetalle,
  listBandejaOperativa,
  type BandejaOperativaItem,
} from '@/api/endpoints/expedientes'
import type { ApiRequestError } from '@/api/errors'
import type { Paginated } from '@/api/types/api'
import { EXPEDIENTE_DETALLE_QUERY_KEY } from '@/features/expediente'

export const BANDEJA_OPERATIVA_QUERY_KEY = 'bandeja-operativa'

/** FE-T701: página real de la bandeja; la paginación y el filtrado los hace el backend. */
export function useBandejaOperativa(page: number, pageSize: number) {
  return useQuery<Paginated<BandejaOperativaItem>, ApiRequestError>({
    queryKey: [BANDEJA_OPERATIVA_QUERY_KEY, page, pageSize],
    queryFn: () => listBandejaOperativa({ page, pageSize }),
    retry: false,
  })
}

/** FE-T705: precarga el detalle (`GET /expedientes/{id}/`) que usará V-08 al navegar. */
export function usePrecargarExpediente() {
  const queryClient = useQueryClient()
  return (id: string) => {
    void queryClient.prefetchQuery({
      queryKey: [EXPEDIENTE_DETALLE_QUERY_KEY, id],
      queryFn: () => getExpedienteDetalle(id),
      retry: false,
    })
  }
}
