import { request } from '../client'

export type LoginRequest = {
  username: string
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

export function login(payload: LoginRequest): Promise<TokenPair> {
  // skipAuthHandler: un 401 por credenciales inválidas en login no debe
  // disparar el cierre de sesión global (corrige P2-3, auditoría F1).
  return request<TokenPair>('/api/v1/auth/token/', {
    method: 'POST',
    body: payload,
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
