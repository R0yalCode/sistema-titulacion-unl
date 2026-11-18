import { createContext, useCallback, useMemo, useState, type ReactNode } from 'react'
import { decodeAccessToken, type JwtUser } from './jwt'
import { clearAccessToken, getAccessToken, saveAccessToken } from './storage'
import { clearNuevaSolicitudDraft, clearRecentExpedientes } from '@/lib/storage'
import { logoutSession } from '@/api/endpoints/auth'

export type AuthUser = JwtUser

export type TokenPair = {
  access: string
  refresh: string
}

export type AuthContextValue = {
  user: AuthUser | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (tokens: TokenPair) => boolean
  /** Limpia la sesión local (p. ej. al expirar el JWT). */
  logout: () => void
  /**
   * Cierre de sesión pedido por el usuario: además de limpiar la sesión local,
   * revoca en el servidor la confianza de este dispositivo (política aprobada
   * el 2026-11-18), así que el próximo ingreso pedirá el código TOTP.
   */
  signOut: () => void
  hasRole: (roles: string[]) => boolean
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined)

type AuthProviderProps = {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<AuthUser | null>(() => {
    const token = getAccessToken()
    return token ? decodeAccessToken(token) : null
  })

  const login = useCallback((tokens: TokenPair): boolean => {
    const decoded = decodeAccessToken(tokens.access)
    if (!decoded) {
      return false
    }

    saveAccessToken(tokens.access)
    setUser(decoded)
    return true
  }, [])

  const logout = useCallback(() => {
    clearAccessToken()
    clearRecentExpedientes()
    clearNuevaSolicitudDraft()
    setUser(null)
  }, [])

  const signOut = useCallback(() => {
    logout()
    // Sin bloquear la salida: si la red falla, la confianza caduca igualmente
    // a los 5 días según el servidor.
    logoutSession().catch(() => undefined)
  }, [logout])

  const hasRole = useCallback(
    (roles: string[]): boolean => user !== null && roles.some((role) => user.roles.includes(role)),
    [user],
  )

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: user !== null,
      isLoading: false,
      login,
      logout,
      signOut,
      hasRole,
    }),
    [user, login, logout, signOut, hasRole],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
