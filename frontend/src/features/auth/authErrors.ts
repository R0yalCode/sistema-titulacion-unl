import { ApiRequestError } from '@/api/errors'
import { presentApiError } from '@/lib/apiErrorPresentation'

const UNAVAILABLE_STATUSES = [500, 502, 503, 504]

const THROTTLED_MESSAGE = 'Demasiados intentos. Espere unos minutos antes de volver a intentarlo.'

/**
 * Mensaje para fallos transversales (límite de intentos, red, servidor) de
 * cualquier pantalla de autenticación; `null` si el error no es de ese tipo.
 * Nunca expone el cuerpo técnico de la respuesta.
 */
export function describeTransportError(error: unknown): string | null {
  if (!(error instanceof ApiRequestError)) {
    return null
  }

  const { status, isNetworkError, isTimeout } = error.error
  if (status === 429) {
    return THROTTLED_MESSAGE
  }
  if (isNetworkError || isTimeout || UNAVAILABLE_STATUSES.includes(status)) {
    return presentApiError(error).description
  }
  return null
}

export function describeLoginError(error: unknown): string {
  const fallback = 'No se pudo iniciar sesión. Intente nuevamente.'
  if (!(error instanceof ApiRequestError)) {
    return fallback
  }

  const { status, message } = error.error
  // 401 cubre credenciales erróneas y cuentas inactivas: el backend no las
  // distingue y la interfaz tampoco (antienumeración de usuarios).
  if (status === 401) {
    return 'Usuario o contraseña incorrectos.'
  }
  if (status === 403) {
    return 'No tiene permisos para iniciar sesión con esta cuenta.'
  }
  if (status === 400 || status === 422) {
    return message
  }
  return describeTransportError(error) ?? fallback
}
