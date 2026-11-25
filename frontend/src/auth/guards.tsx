import { useContext, type ReactNode } from 'react'
import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { AuthContext } from './AuthContext'
import { SESSION_EXPIRED_PATH, sesionExpiradaPendiente } from './sessionExpiry'

type GuardProps = {
  children?: ReactNode
}

export function RequireAuth({ children }: GuardProps) {
  const auth = useContext(AuthContext)
  const location = useLocation()

  if (!auth?.isAuthenticated) {
    // Sesión cerrada por un 401 de la API → vista 401; si no, al login.
    const destino = sesionExpiradaPendiente() ? SESSION_EXPIRED_PATH : '/login'
    return <Navigate replace state={{ returnTo: location.pathname }} to={destino} />
  }

  return <>{children ?? <Outlet />}</>
}

type RequireRoleProps = GuardProps & {
  roles: string[]
}

export function RequireRole({ roles, children }: RequireRoleProps) {
  const auth = useContext(AuthContext)

  if (!auth?.hasRole(roles)) {
    // V-09 (FE-T902): motivo explícito, sin revelar la ruta ni la regla de autorización.
    return <Navigate replace to="/no-habilitado?motivo=rol-no-autorizado" />
  }

  return <>{children ?? <Outlet />}</>
}

export function RedirectIfAuthenticated({ children, homeRoute }: GuardProps & { homeRoute: string }) {
  const auth = useContext(AuthContext)

  if (auth?.isAuthenticated) {
    return <Navigate replace to={homeRoute} />
  }

  return <>{children ?? <Outlet />}</>
}
