import { useContext, type ReactNode } from 'react'
import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { AuthContext } from './AuthContext'

type GuardProps = {
  children?: ReactNode
}

export function RequireAuth({ children }: GuardProps) {
  const auth = useContext(AuthContext)
  const location = useLocation()

  if (!auth?.isAuthenticated) {
    return <Navigate replace state={{ returnTo: location.pathname }} to="/login" />
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
