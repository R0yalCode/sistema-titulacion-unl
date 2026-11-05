import { useMutation, useQueryClient } from '@tanstack/react-query'
import { crearExpediente, type ExpedienteBorrador } from '@/api/endpoints/expedientes'
import type { ApiRequestError } from '@/api/errors'
import { BANDEJA_ESTUDIANTE_QUERY_KEY } from '@/features/dashboard'

export function useCrearExpediente() {
  const queryClient = useQueryClient()

  return useMutation<ExpedienteBorrador, ApiRequestError, string>({
    mutationFn: (carreraId: string) => crearExpediente({ carrera_id: carreraId }),
    retry: false,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [BANDEJA_ESTUDIANTE_QUERY_KEY] })
    },
  })
}
