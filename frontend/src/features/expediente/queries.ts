import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  enviarExpediente,
  getExpedienteDetalle,
  observarExpediente,
  type ExpedienteDetalle,
  type ExpedienteEnviado,
  type ObservacionAccionable,
  type ObservarExpedienteRequest,
} from '@/api/endpoints/expedientes'
import {
  evaluarChecklist,
  listChecklist,
  subsanarChecklist,
  type ChecklistItem,
  type EvaluarChecklistRequest,
  type SubsanacionResponse,
} from '@/api/endpoints/checklist'
import type { ApiRequestError } from '@/api/errors'
import { BANDEJA_ESTUDIANTE_QUERY_KEY } from '@/features/dashboard'
import { puedeVerChecklist } from './accionesPorRolEstado'

export const EXPEDIENTE_DETALLE_QUERY_KEY = 'expediente-detalle'
export const CHECKLIST_QUERY_KEY = 'checklist'

export function useExpedienteDetalle(id: string) {
  return useQuery<ExpedienteDetalle, ApiRequestError>({
    queryKey: [EXPEDIENTE_DETALLE_QUERY_KEY, id],
    queryFn: () => getExpedienteDetalle(id),
    retry: false,
  })
}

/** FE-T403: no ejecuta la query si la matriz RBAC confirma que el rol carece de permiso (403 real). */
export function useChecklist(expedienteId: string, roles: string[]) {
  return useQuery<ChecklistItem[], ApiRequestError>({
    queryKey: [CHECKLIST_QUERY_KEY, expedienteId],
    queryFn: () => listChecklist(expedienteId),
    enabled: puedeVerChecklist(roles),
    retry: false,
  })
}

export function useEnviarExpediente(id: string) {
  const queryClient = useQueryClient()
  return useMutation<ExpedienteEnviado, ApiRequestError, void>({
    mutationFn: () => enviarExpediente(id),
    retry: false,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [EXPEDIENTE_DETALLE_QUERY_KEY, id] })
      queryClient.invalidateQueries({ queryKey: [BANDEJA_ESTUDIANTE_QUERY_KEY] })
    },
  })
}

export function useObservarExpediente(id: string) {
  const queryClient = useQueryClient()
  return useMutation<ObservacionAccionable, ApiRequestError, ObservarExpedienteRequest>({
    mutationFn: (payload) => observarExpediente(id, payload),
    retry: false,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [EXPEDIENTE_DETALLE_QUERY_KEY, id] })
      queryClient.invalidateQueries({ queryKey: [CHECKLIST_QUERY_KEY, id] })
    },
  })
}

export function useEvaluarChecklist(expedienteId: string) {
  const queryClient = useQueryClient()
  return useMutation<ChecklistItem, ApiRequestError, { id: string; payload: EvaluarChecklistRequest }>({
    mutationFn: ({ id, payload }) => evaluarChecklist(id, payload),
    retry: false,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [CHECKLIST_QUERY_KEY, expedienteId] })
      queryClient.invalidateQueries({ queryKey: [EXPEDIENTE_DETALLE_QUERY_KEY, expedienteId] })
    },
  })
}

export function useSubsanarChecklist(expedienteId: string) {
  const queryClient = useQueryClient()
  return useMutation<SubsanacionResponse, ApiRequestError, { id: string; archivo: File }>({
    mutationFn: ({ id, archivo }) => subsanarChecklist(id, archivo),
    retry: false,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [CHECKLIST_QUERY_KEY, expedienteId] })
      queryClient.invalidateQueries({ queryKey: [EXPEDIENTE_DETALLE_QUERY_KEY, expedienteId] })
    },
  })
}
