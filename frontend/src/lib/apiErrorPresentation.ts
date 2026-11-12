import type { ApiRequestError } from '@/api/errors'

export type ApiErrorPresentation = {
  kind: 'not-found' | 'forbidden' | 'error'
  title: string
  description: string
}

const UNAVAILABLE_STATUSES = [502, 503, 504]

/**
 * Traduce el error que realmente lanza `request()` (ApiRequestError, no el
 * ApiError que envuelve) al componente y mensaje que debe mostrarlo. No crea
 * componentes nuevos: solo decide entre NotFoundState/ForbiddenState/ErrorState
 * (08_UI_ERROR_STATES_SPEC §8.1).
 */
export function presentApiError(apiRequestError: ApiRequestError): ApiErrorPresentation {
  const error = apiRequestError.error

  if (error.status === 404) {
    return {
      kind: 'not-found',
      title: 'No encontrado',
      description: 'El recurso solicitado no existe o no está disponible.',
    }
  }

  if (error.status === 403) {
    return {
      kind: 'forbidden',
      title: 'Acceso restringido',
      description: 'No tiene permisos para ver este contenido.',
    }
  }

  if (error.status === 401) {
    return {
      kind: 'error',
      title: 'Sesión expirada',
      description: 'Su sesión ha expirado. Será redirigido para iniciar sesión nuevamente.',
    }
  }

  if (error.status === 500) {
    return {
      kind: 'error',
      title: 'Error del servidor',
      description: 'Ocurrió un problema al procesar tu solicitud. Intenta nuevamente.',
    }
  }

  if (UNAVAILABLE_STATUSES.includes(error.status) || error.isNetworkError || error.isTimeout) {
    return {
      kind: 'error',
      title: 'Servicio no disponible',
      description: 'El servicio no está disponible temporalmente. Intenta nuevamente en unos minutos.',
    }
  }

  return {
    kind: 'error',
    title: 'Ocurrió un error',
    description: 'No se pudo completar la operación. Intenta nuevamente.',
  }
}
