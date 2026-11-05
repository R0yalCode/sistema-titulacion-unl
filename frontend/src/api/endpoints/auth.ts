import { request } from '../client'

export type LoginRequest = {
  username: string
  password: string
}

export type TokenPair = {
  access: string
  refresh: string
}

export function login(payload: LoginRequest): Promise<TokenPair> {
  // skipAuthHandler: un 401 por credenciales inválidas en login no debe
  // disparar el cierre de sesión global (corrige P2-3, auditoría F1).
  return request<TokenPair>('/api/v1/auth/token/', {
    method: 'POST',
    body: payload,
    skipAuthHandler: true,
  })
}
