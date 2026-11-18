/**
 * Validaciones de los formularios de autenticación.
 *
 * Reflejan reglas que el backend ya impone (formato de `username` de Django,
 * `EmailField` y los validadores de `AUTH_PASSWORD_VALIDATORS` comprobables
 * en el cliente). El backend sigue siendo la autoridad: similitud con datos
 * del usuario y contraseñas comunes solo se validan allí.
 */

// Mismo alfabeto que el validador de `username` de Django.
const USERNAME_PATTERN = /^[\w.@+-]+$/
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/

export const USERNAME_MAX_LENGTH = 150
export const EMAIL_MAX_LENGTH = 254
export const PASSWORD_MIN_LENGTH = 8
export const PASSWORD_MAX_LENGTH = 128

export function validateUsername(value: string): string | undefined {
  const trimmed = value.trim()
  if (!trimmed) {
    return 'Ingrese su usuario.'
  }
  if (trimmed.length > USERNAME_MAX_LENGTH || !USERNAME_PATTERN.test(trimmed)) {
    return 'El usuario solo puede contener letras, números y los caracteres @ . + - _'
  }
  return undefined
}

export function validateEmail(value: string): string | undefined {
  const trimmed = value.trim()
  if (!trimmed) {
    return 'Ingrese su correo electrónico institucional.'
  }
  if (trimmed.length > EMAIL_MAX_LENGTH || !EMAIL_PATTERN.test(trimmed)) {
    return 'Ingrese un correo electrónico válido.'
  }
  return undefined
}

export type PasswordRule = {
  id: string
  label: string
  met: boolean
}

export function evaluatePasswordRules(password: string): PasswordRule[] {
  return [
    {
      id: 'longitud',
      label: `Al menos ${PASSWORD_MIN_LENGTH} caracteres`,
      met: password.length >= PASSWORD_MIN_LENGTH,
    },
    {
      id: 'no-numerica',
      label: 'No puede ser únicamente numérica',
      met: password.length > 0 && !/^\d+$/.test(password),
    },
  ]
}

export function validateNewPassword(password: string): string | undefined {
  if (!password) {
    return 'Ingrese la nueva contraseña.'
  }
  if (password.length > PASSWORD_MAX_LENGTH) {
    return `La contraseña no puede superar los ${PASSWORD_MAX_LENGTH} caracteres.`
  }
  if (evaluatePasswordRules(password).some((rule) => !rule.met)) {
    return 'La contraseña no cumple los requisitos indicados.'
  }
  return undefined
}

export function validatePasswordConfirmation(password: string, confirmation: string): string | undefined {
  if (!confirmation) {
    return 'Confirme la nueva contraseña.'
  }
  if (password !== confirmation) {
    return 'Las contraseñas no coinciden.'
  }
  return undefined
}

// --- Correo institucional (acceso y restablecimiento del 2FA) -------------
// Misma regla que el backend (apps/authentication/domain/correo_institucional.py);
// el backend sigue siendo la autoridad.

export const INSTITUTIONAL_DOMAIN = 'unl.edu.ec'
export const USERNAME_REQUIRED_MESSAGE = 'El nombre de usuario es un campo requerido.'
export const PASSWORD_REQUIRED_MESSAGE = 'La contraseña es un campo requerido.'
export const INSTITUTIONAL_EMAIL_MESSAGE = 'Ingrese un correo institucional válido (@unl.edu.ec).'

const LOCAL_PART_PATTERN = /^[a-z0-9._%+-]+$/

/** Quita espacios exteriores y pasa a minúsculas. */
export function normalizeInstitutionalEmail(value: string): string {
  return value.trim().toLowerCase()
}

export function isInstitutionalEmail(value: string): boolean {
  const normalized = normalizeInstitutionalEmail(value)
  const parts = normalized.split('@')
  if (parts.length !== 2) return false
  const [local = '', domain = ''] = parts
  return (
    local.length > 0 &&
    normalized.length <= EMAIL_MAX_LENGTH &&
    LOCAL_PART_PATTERN.test(local) &&
    !local.startsWith('.') &&
    !local.endsWith('.') &&
    !local.includes('..') &&
    domain === INSTITUTIONAL_DOMAIN
  )
}

/** Validación del campo «Nombre de usuario» (correo institucional). */
export function validateInstitutionalUsername(value: string): string | undefined {
  if (!value.trim()) {
    return USERNAME_REQUIRED_MESSAGE
  }
  return isInstitutionalEmail(value) ? undefined : INSTITUTIONAL_EMAIL_MESSAGE
}

export function validateRequiredPassword(value: string): string | undefined {
  return value ? undefined : PASSWORD_REQUIRED_MESSAGE
}
