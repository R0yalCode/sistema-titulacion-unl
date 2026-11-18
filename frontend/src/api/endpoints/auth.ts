import { request } from '../client'

export type LoginRequest = {
  /** Correo institucional @unl.edu.ec (el backend lo vuelve a validar). */
  email: string
  password: string
}

export type TokenPair = {
  access: string
  refresh: string
}

export type PasswordResetLink = {
  uid: string
  token: string
}

type DetailResponse = {
  detail: string
}

/** `code` que el backend devuelve cuando el enlace no puede usarse. */
export const INVALID_RESET_LINK_CODE = 'enlace_restablecimiento_invalido'

/**
 * Resultado de cada paso del inicio de sesión (AUTH-B). El JWT solo llega con
 * `status: 'authenticated'`; los demás estados traen un reto de corta vida que
 * se conserva únicamente en memoria (nunca en localStorage/sessionStorage).
 */
export type AuthenticatedResult = TokenPair & {
  status: 'authenticated'
  /** Solo al completar el registro: se muestran una única vez. */
  recovery_codes?: string[]
}

export type ChallengeResult = {
  status: 'mfa_required' | 'mfa_setup_required'
  challenge: string
  expires_in: number
}

export type AuthResult = AuthenticatedResult | ChallengeResult

export type MfaSetup = {
  /** QR otpauth como `data:image/svg+xml`, generado por el backend. */
  qr_svg: string
  manual_key: string
  issuer: string
  account: string
}

export type MfaCodeRequest = {
  challenge: string
  code: string
  trustDevice: boolean
}

// skipAuthHandler en todo el flujo: un 401 por credenciales inválidas no debe
// disparar el cierre de sesión global (corrige P2-3, auditoría F1).

export function login(payload: LoginRequest): Promise<AuthResult> {
  return request<AuthResult>('/api/v1/auth/login/', {
    method: 'POST',
    body: payload,
    skipAuthHandler: true,
  })
}

export function startMfaSetup(challenge: string): Promise<MfaSetup> {
  return request<MfaSetup>('/api/v1/auth/mfa/setup/', {
    method: 'POST',
    body: { challenge },
    skipAuthHandler: true,
  })
}

export function confirmMfaSetup({ challenge, code, trustDevice }: MfaCodeRequest): Promise<AuthResult> {
  return request<AuthResult>('/api/v1/auth/mfa/setup/confirm/', {
    method: 'POST',
    body: { challenge, code, trust_device: trustDevice },
    skipAuthHandler: true,
  })
}

export function verifyMfa({ challenge, code, trustDevice }: MfaCodeRequest): Promise<AuthResult> {
  return request<AuthResult>('/api/v1/auth/mfa/verify/', {
    method: 'POST',
    body: { challenge, code, trust_device: trustDevice },
    skipAuthHandler: true,
  })
}

export function recoverMfa(challenge: string, recoveryCode: string): Promise<AuthResult> {
  return request<AuthResult>('/api/v1/auth/mfa/recovery/', {
    method: 'POST',
    body: { challenge, recovery_code: recoveryCode },
    skipAuthHandler: true,
  })
}

/** Revoca en el servidor la confianza de este dispositivo (cookie HttpOnly). */
export function logoutSession(): Promise<DetailResponse> {
  return request<DetailResponse>('/api/v1/auth/logout/', {
    method: 'POST',
    skipAuthHandler: true,
  })
}

// Los endpoints de recuperación son públicos: skipAuthHandler evita que una
// respuesta suya pueda interpretarse como expiración de sesión.

export function requestPasswordReset(email: string): Promise<DetailResponse> {
  return request<DetailResponse>('/api/v1/auth/password-reset/', {
    method: 'POST',
    body: { email },
    skipAuthHandler: true,
  })
}

export function validatePasswordResetLink(link: PasswordResetLink): Promise<DetailResponse> {
  return request<DetailResponse>('/api/v1/auth/password-reset/validate/', {
    method: 'POST',
    body: link,
    skipAuthHandler: true,
  })
}

export function confirmPasswordReset(link: PasswordResetLink, newPassword: string): Promise<DetailResponse> {
  return request<DetailResponse>('/api/v1/auth/password-reset/confirm/', {
    method: 'POST',
    body: { ...link, new_password: newPassword },
    skipAuthHandler: true,
  })
}

// --- Restablecimiento del doble factor (MFA-RST) -------------------------

export type MfaResetRequest = {
  email: string
  cedula: string
  password: string
}

/** Paso 1: responde siempre igual; si procede, envía un enlace al correo. */
export function requestMfaReset(payload: MfaResetRequest): Promise<DetailResponse> {
  return request<DetailResponse>('/api/v1/auth/mfa/reset/', {
    method: 'POST',
    body: payload,
    skipAuthHandler: true,
  })
}

/** `code` que el backend devuelve cuando el enlace del 2FA no puede usarse. */
export const INVALID_MFA_RESET_LINK_CODE = 'enlace_mfa_invalido'

/** Paso 2: confirma el enlace y retira el autenticador anterior. */
export function confirmMfaReset(link: PasswordResetLink): Promise<DetailResponse> {
  return request<DetailResponse>('/api/v1/auth/mfa/reset/confirm/', {
    method: 'POST',
    body: link,
    skipAuthHandler: true,
  })
}
