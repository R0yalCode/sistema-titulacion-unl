import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { crearExpediente, type ExpedienteBorrador } from '@/api/endpoints/expedientes'
import { getPerfilAcademico, type PerfilAcademico } from '@/api/endpoints/perfilAcademico'
import type { ApiRequestError } from '@/api/errors'
import { BANDEJA_ESTUDIANTE_QUERY_KEY } from '@/features/dashboard'

export const PERFIL_ACADEMICO_QUERY_KEY = ['perfil-academico'] as const

export function usePerfilAcademico() {
  return useQuery<PerfilAcademico, ApiRequestError>({
    queryKey: PERFIL_ACADEMICO_QUERY_KEY,
    queryFn: getPerfilAcademico,
    // Cada visita a V-03 consulta de nuevo la fuente: el perfil puede cambiar
    // (p. ej. la Secretaría corrige la carrera) y no debe usarse uno viejo.
    staleTime: 0,
    retry: false,
  })
}

export function useCrearExpediente() {
  const queryClient = useQueryClient()

  return useMutation<ExpedienteBorrador, ApiRequestError, void>({
    mutationFn: () => crearExpediente(),
    retry: false,
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: [BANDEJA_ESTUDIANTE_QUERY_KEY] })
      queryClient.invalidateQueries({ queryKey: PERFIL_ACADEMICO_QUERY_KEY })
    },
  })
}
