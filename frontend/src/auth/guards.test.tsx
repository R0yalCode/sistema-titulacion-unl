import { screen } from '@testing-library/react'
import type { ReactNode } from 'react'
import { Route, Routes, useLocation } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import { renderWithProviders } from '@/test/renderWithProviders'
import { AuthContext, type AuthContextValue, type AuthUser } from './AuthContext'
import { RedirectIfAuthenticated, RequireAuth, RequireRole } from './guards'

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

function renderGuarded(route: string, value: AuthContextValue, guarded: ReactNode) {
  return renderWithProviders(
    <AuthContext.Provider value={value}>
      <Routes>
        <Route element={<p>Pantalla de login</p>} path="/login" />
        <Route element={<p>No habilitado</p>} path="/no-habilitado" />
        <Route element={guarded} path="/protegido" />
      </Routes>
    </AuthContext.Provider>,
    { route },
  )
}

describe('RequireAuth', () => {
  it('redirige a /login cuando no hay sesión', () => {
    renderGuarded(
      '/protegido',
      authValue(null),
      <RequireAuth>
        <p>Contenido protegido</p>
      </RequireAuth>,
    )

    expect(screen.getByText('Pantalla de login')).toBeInTheDocument()
    expect(screen.queryByText('Contenido protegido')).not.toBeInTheDocument()
  })

  it('renderiza el contenido protegido cuando hay sesión', () => {
    renderGuarded(
      '/protegido',
      authValue({ cedula: '1104567890', roles: ['ESTUDIANTE'] }),
      <RequireAuth>
        <p>Contenido protegido</p>
      </RequireAuth>,
    )

    expect(screen.getByText('Contenido protegido')).toBeInTheDocument()
  })
})

describe('RequireRole', () => {
  it('redirige a /no-habilitado si el rol no coincide', () => {
    renderGuarded(
      '/protegido',
      authValue({ cedula: '1104567890', roles: ['ESTUDIANTE'] }),
      <RequireRole roles={['DECANO']}>
        <p>Contenido protegido</p>
      </RequireRole>,
    )

    expect(screen.getByText('No habilitado')).toBeInTheDocument()
    expect(screen.queryByText('Contenido protegido')).not.toBeInTheDocument()
  })

  it('envía a V-09 con el motivo explícito y sin la ruta solicitada (FE-T902)', () => {
    let destino = ''
    renderWithProviders(
      <AuthContext.Provider value={authValue({ cedula: '1104567890', roles: ['ESTUDIANTE'] })}>
        <Routes>
          <Route
            element={
              <RequireRole roles={['DECANO']}>
                <p>Contenido protegido</p>
              </RequireRole>
            }
            path="/protegido"
          />
          <Route element={<UbicacionActual onUbicacion={(valor) => (destino = valor)} />} path="/no-habilitado" />
        </Routes>
      </AuthContext.Provider>,
      { route: '/protegido' },
    )

    expect(destino).toBe('/no-habilitado?motivo=rol-no-autorizado')
  })

  it('renderiza el contenido protegido si el rol coincide', () => {
    renderGuarded(
      '/protegido',
      authValue({ cedula: '1104567890', roles: ['ESTUDIANTE'] }),
      <RequireRole roles={['ESTUDIANTE']}>
        <p>Contenido protegido</p>
      </RequireRole>,
    )

    expect(screen.getByText('Contenido protegido')).toBeInTheDocument()
  })

  it('no renderiza contenido protegido sin sesión', () => {
    renderGuarded(
      '/protegido',
      authValue(null),
      <RequireRole roles={['ESTUDIANTE']}>
        <p>Contenido protegido</p>
      </RequireRole>,
    )

    expect(screen.getByText('No habilitado')).toBeInTheDocument()
    expect(screen.queryByText('Contenido protegido')).not.toBeInTheDocument()
  })
})

describe('RedirectIfAuthenticated', () => {
  it('redirige a homeRoute cuando ya hay sesión', () => {
    renderWithProviders(
      <AuthContext.Provider value={authValue({ cedula: '1104567890', roles: ['ESTUDIANTE'] })}>
        <Routes>
          <Route element={<p>Destino por rol</p>} path="/estudiante" />
          <Route
            element={
              <RedirectIfAuthenticated homeRoute="/estudiante">
                <p>Formulario de login</p>
              </RedirectIfAuthenticated>
            }
            path="/login"
          />
        </Routes>
      </AuthContext.Provider>,
      { route: '/login' },
    )

    expect(screen.getByText('Destino por rol')).toBeInTheDocument()
  })

  it('renderiza el contenido cuando no hay sesión', () => {
    renderWithProviders(
      <AuthContext.Provider value={authValue(null)}>
        <RedirectIfAuthenticated homeRoute="/estudiante">
          <p>Formulario de login</p>
        </RedirectIfAuthenticated>
      </AuthContext.Provider>,
    )

    expect(screen.getByText('Formulario de login')).toBeInTheDocument()
  })
})

function UbicacionActual({ onUbicacion }: { onUbicacion: (valor: string) => void }) {
  const location = useLocation()
  onUbicacion(`${location.pathname}${location.search}`)
  return <p>No habilitado</p>
}
