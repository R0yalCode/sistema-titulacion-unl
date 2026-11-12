import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  getExpedienteDetalle,
  iniciarVerificacion,
  listBandejaOperativa,
  type BandejaOperativaItem,
  type ExpedienteDetalle,
} from '@/api/endpoints/expedientes'
import type { ApiRequestError } from '@/api/errors'
import type { Paginated } from '@/api/types/api'
import { CHECKLIST_QUERY_KEY, EXPEDIENTE_DETALLE_QUERY_KEY } from '@/features/expediente'

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

/**
 * FE-T809: tras una acción que cambia el estado se refrescan el detalle, el
 * checklist y la bandeja operativa (su `staleTime` de 30 s no basta).
 */
export function useInvalidarTrasAccion(expedienteId: string) {
  const queryClient = useQueryClient()
  return () => {
    void queryClient.invalidateQueries({ queryKey: [EXPEDIENTE_DETALLE_QUERY_KEY, expedienteId] })
    void queryClient.invalidateQueries({ queryKey: [CHECKLIST_QUERY_KEY, expedienteId] })
    void queryClient.invalidateQueries({ queryKey: [BANDEJA_OPERATIVA_QUERY_KEY] })
  }
}

/** E2-01: ENVIADA → EN_VERIFICACION (solo SECRETARIO_ABOGADO). */
export function useIniciarVerificacion(expedienteId: string) {
  const invalidar = useInvalidarTrasAccion(expedienteId)
  return useMutation<ExpedienteDetalle, ApiRequestError, void>({
    mutationFn: () => iniciarVerificacion(expedienteId),
    retry: false,
    onSuccess: invalidar,
  })
}
