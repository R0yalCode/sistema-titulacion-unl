import { screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { AuthContext, type AuthContextValue, type AuthUser } from '@/auth/AuthContext'
import { renderWithProviders } from '@/test/renderWithProviders'
import { AppRouter } from './router'

function authValue(user: AuthUser | null): AuthContextValue {
  return {
    user,
    isAuthenticated: user !== null,
    isLoading: false,
    login: vi.fn().mockReturnValue(true),
    logout: vi.fn(),
    hasRole: (roles) => user !== null && roles.some((role) => user.roles.includes(role)),
  }
}

function renderRouterAs(user: AuthUser | null, route: string) {
  return renderWithProviders(
    <AuthContext.Provider value={authValue(user)}>
      <AppRouter />
    </AuthContext.Provider>,
    { route },
  )
}

describe('AppRouter', () => {
  it('resuelve /login sin sesión', async () => {
    renderRouterAs(null, '/login')

    expect(await screen.findByRole('heading', { name: 'Iniciar sesión' })).toBeInTheDocument()
  })

  it('redirige / a /login cuando no hay sesión', async () => {
    renderRouterAs(null, '/')

    expect(await screen.findByRole('heading', { name: 'Iniciar sesión' })).toBeInTheDocument()
  })

  it('redirige una ruta protegida a /login cuando no hay sesión', async () => {
    renderRouterAs(null, '/estudiante')

    expect(await screen.findByRole('heading', { name: 'Iniciar sesión' })).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Dashboard del estudiante (V-02)' })).not.toBeInTheDocument()
  })

  it('resuelve una ruta protegida dentro del layout con el rol correcto (/estudiante)', async () => {
    renderRouterAs({ cedula: '1104567890', roles: ['ESTUDIANTE'] }, '/estudiante')

    expect(await screen.findByRole('heading', { name: 'Dashboard del estudiante (V-02)' })).toBeInTheDocument()
  })

  it('redirige a /no-habilitado cuando el rol no coincide con la ruta', async () => {
    renderRouterAs({ cedula: '1104567890', roles: ['ESTUDIANTE'] }, '/bandeja')

    expect(await screen.findByRole('heading', { name: 'Acceso restringido' })).toBeInTheDocument()
  })

  it('resuelve rutas con parámetros para un rol operativo (/bandeja/:id)', async () => {
    renderRouterAs({ cedula: '1104567890', roles: ['DECANO'] }, '/bandeja/abc-123')

    expect(await screen.findByRole('heading', { name: 'Detalle del funcionario (V-08)' })).toBeInTheDocument()
  })

  it('redirige / al inicio por rol cuando hay sesión (ESTUDIANTE)', async () => {
    renderRouterAs({ cedula: '1104567890', roles: ['ESTUDIANTE'] }, '/')

    expect(await screen.findByRole('heading', { name: 'Dashboard del estudiante (V-02)' })).toBeInTheDocument()
  })

  it('redirige / al inicio por rol cuando hay sesión (DECANO → /bandeja)', async () => {
    renderRouterAs({ cedula: '1104567890', roles: ['DECANO'] }, '/')

    expect(await screen.findByRole('heading', { level: 1, name: 'Bandeja de expedientes' })).toBeInTheDocument()
  })

  it('muestra 404 para rutas desconocidas sin exigir sesión', async () => {
    renderRouterAs(null, '/ruta-inexistente')

    expect(await screen.findByRole('heading', { level: 1, name: 'Error 404' })).toBeInTheDocument()
  })
})
