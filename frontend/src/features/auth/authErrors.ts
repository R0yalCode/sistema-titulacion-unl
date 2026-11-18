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

/** `code` estable que el backend adjunta a sus errores de dominio. */
export function apiErrorCode(error: unknown): string | undefined {
  if (!(error instanceof ApiRequestError)) {
    return undefined
  }
  const raw = error.error.raw
  if (typeof raw === 'object' && raw !== null) {
    const code = (raw as { code?: unknown }).code
    return typeof code === 'string' ? code : undefined
  }
  return undefined
}

/**
 * Errores que invalidan el reto en curso: hay que volver a introducir usuario
 * y contraseña (reto caducado, agotado o autenticador en otro estado).
 */
export const MFA_RESTART_CODES = ['reto_mfa_invalido', 'estado_mfa_invalido']

export function isMfaRestartError(error: unknown): boolean {
  const code = apiErrorCode(error)
  return code !== undefined && MFA_RESTART_CODES.includes(code)
}

export function describeMfaError(error: unknown): string {
  const fallback = 'No se pudo verificar el código. Intente nuevamente.'
  if (!(error instanceof ApiRequestError)) {
    return fallback
  }
  const code = apiErrorCode(error)
  if (code === 'codigo_mfa_invalido') {
    return 'El código no es válido. Use el código actual de Google Authenticator y verifique que la hora de su teléfono sea automática.'
  }
  if (code === 'mfa_bloqueado') {
    return 'Demasiados intentos fallidos de verificación. Espere unos minutos antes de volver a intentarlo.'
  }
  if (code && MFA_RESTART_CODES.includes(code)) {
    return 'La verificación caducó o ya no es válida. Inicie sesión nuevamente.'
  }
  if (error.error.status === 400 || error.error.status === 422) {
    return error.error.message
  }
  return describeTransportError(error) ?? fallback
}
