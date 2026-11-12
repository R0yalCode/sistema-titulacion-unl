import { useMutation } from '@tanstack/react-query'
import {
  emitirInforme,
  registrarDeclaratoria,
  type DeclaratoriaAptitud,
  type InformeAptitud,
} from '@/api/endpoints/resoluciones'
import type { ApiRequestError } from '@/api/errors'
import { useInvalidarTrasAccion } from './queries'

/** FE-T804: EN_VERIFICACION → INFORME_EMITIDO; refresca detalle, checklist y bandeja. */
export function useEmitirInforme(expedienteId: string) {
  const invalidar = useInvalidarTrasAccion(expedienteId)
  return useMutation<InformeAptitud, ApiRequestError, string>({
    mutationFn: (fundamentacion) => emitirInforme(expedienteId, fundamentacion),
    retry: false,
    onSuccess: invalidar,
  })
}

/** FE-T805: INFORME_EMITIDO → DECLARADA_APTA; refresca detalle, checklist y bandeja. */
export function useRegistrarDeclaratoria(expedienteId: string) {
  const invalidar = useInvalidarTrasAccion(expedienteId)
  return useMutation<DeclaratoriaAptitud, ApiRequestError, { archivo: File; numeroMemorando: string }>({
    mutationFn: ({ archivo, numeroMemorando }) => registrarDeclaratoria(expedienteId, archivo, numeroMemorando),
    retry: false,
    onSuccess: invalidar,
  })
}
