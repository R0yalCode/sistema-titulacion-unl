import { ApiRequestError } from '@/api/errors'
import { presentApiError } from '@/lib/apiErrorPresentation'

const GENERIC_MESSAGE = 'No se pudo completar la acción. Intente nuevamente.'

/**
 * Clasificación de errores para las mutaciones de V-04 (enviar, observar,
 * evaluar, subsanar). A diferencia de `presentApiError()` (pensado para
 * estados de página completos), aquí se prioriza siempre el mensaje real
 * del backend: varias excepciones de dominio verificadas (INC-21 en
 * `clarify.md`) se re-lanzan como HTTP 500 aunque describen una regla de
 * negocio real, no una falla de servidor, y `normalizeApiError` ya extrae
 * ese texto real en `error.detail` sin importar el código HTTP.
 */
export function describeAccionError(error: unknown): string {
  if (!(error instanceof ApiRequestError)) {
    return GENERIC_MESSAGE
  }

  const { isNetworkError, isTimeout, message } = error.error

  if (isNetworkError || isTimeout) {
    return 'No se pudo confirmar el resultado por un problema de conexión. Verifique el estado actual antes de reintentar.'
  }

  if (message && message !== 'Ocurrió un error inesperado.') {
    return message
  }

  return presentApiError(error).description
}
