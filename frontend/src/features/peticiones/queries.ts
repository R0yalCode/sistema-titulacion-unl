import { useMutation, useQueryClient } from '@tanstack/react-query'
import {
  cargarDocumento,
  solicitarEmision,
  type DocumentoCargado,
  type PeticionSolicitada,
} from '@/api/endpoints/peticiones'
import type { ApiRequestError } from '@/api/errors'
import { BANDEJA_ESTUDIANTE_QUERY_KEY } from '@/features/dashboard'
import { EXPEDIENTE_DETALLE_QUERY_KEY } from '@/features/expediente'

function useInvalidarExpediente(expedienteId: string) {
  const queryClient = useQueryClient()
  return () => {
    queryClient.invalidateQueries({ queryKey: [EXPEDIENTE_DETALLE_QUERY_KEY, expedienteId] })
    queryClient.invalidateQueries({ queryKey: [BANDEJA_ESTUDIANTE_QUERY_KEY] })
  }
}

/** FE-T502: tras el 200 se invalida el detalle del expediente (fuente de las peticiones). */
export function useSolicitarEmision(expedienteId: string) {
  const invalidar = useInvalidarExpediente(expedienteId)
  return useMutation<PeticionSolicitada, ApiRequestError, string>({
    mutationFn: (peticionId) => solicitarEmision(peticionId),
    retry: false,
    onSuccess: invalidar,
  })
}

/** FE-T503: tras el 201 se invalida el detalle del expediente. */
export function useCargarDocumento(expedienteId: string) {
  const invalidar = useInvalidarExpediente(expedienteId)
  return useMutation<DocumentoCargado, ApiRequestError, { peticionId: string; archivo: File }>({
    mutationFn: ({ peticionId, archivo }) => cargarDocumento(peticionId, archivo),
    retry: false,
    onSuccess: invalidar,
  })
}
