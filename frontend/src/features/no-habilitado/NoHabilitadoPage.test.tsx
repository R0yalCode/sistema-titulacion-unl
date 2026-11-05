import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Route, Routes } from 'react-router-dom'
import { axe } from 'vitest-axe'
import { describe, expect, it, vi } from 'vitest'
import { AuthContext, type AuthContextValue, type AuthUser } from '@/auth/AuthContext'
import { renderWithProviders } from '@/test/renderWithProviders'
import NoHabilitadoPage from './NoHabilitadoPage'

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

describe('NoHabilitadoPage', () => {
  it('reutiliza ForbiddenState sin revelar detalles de la regla de autorización', () => {
    renderWithProviders(
      <AuthContext.Provider value={authValue({ cedula: '1104567890', roles: ['ESTUDIANTE'] })}>
        <NoHabilitadoPage />
      </AuthContext.Provider>,
    )

    const status = screen.getByRole('status')
    expect(status).toHaveTextContent('Acceso restringido')
    expect(status.textContent).not.toMatch(/rol requerido|RBAC|matriz de permisos/i)
  })

  it('ofrece volver al inicio por rol', () => {
    renderWithProviders(
      <AuthContext.Provider value={authValue({ cedula: '1104567890', roles: ['DECANO'] })}>
        <NoHabilitadoPage />
      </AuthContext.Provider>,
    )

    expect(screen.getByRole('button', { name: 'Volver al inicio' })).toBeInTheDocument()
  })

  it('el botón "Volver al inicio" navega al destino por rol', async () => {
    const user = userEvent.setup()
    renderWithProviders(
      <AuthContext.Provider value={authValue({ cedula: '1104567890', roles: ['DECANO'] })}>
        <Routes>
          <Route element={<NoHabilitadoPage />} path="/no-habilitado" />
          <Route element={<p>Bandeja del funcionario</p>} path="/bandeja" />
        </Routes>
      </AuthContext.Provider>,
      { route: '/no-habilitado' },
    )

    await user.click(screen.getByRole('button', { name: 'Volver al inicio' }))

    expect(screen.getByText('Bandeja del funcionario')).toBeInTheDocument()
  })

  it('muestra la mascota 403 como imagen decorativa', () => {
    const { container } = renderWithProviders(
      <AuthContext.Provider value={authValue({ cedula: '1104567890', roles: ['ESTUDIANTE'] })}>
        <NoHabilitadoPage />
      </AuthContext.Provider>,
    )

    const mascot = container.querySelector('img')
    expect(mascot).toHaveAttribute('src', '/assets/mascotas/mascota-403.png')
    expect(mascot).toHaveAttribute('alt', '')
  })

  it('no presenta violaciones de accesibilidad', async () => {
    const { container } = renderWithProviders(
      <AuthContext.Provider value={authValue({ cedula: '1104567890', roles: ['ESTUDIANTE'] })}>
        <NoHabilitadoPage />
      </AuthContext.Provider>,
    )

    expect(await axe(container)).toHaveNoViolations()
  })

  it('es operable por teclado', async () => {
    const user = userEvent.setup()
    renderWithProviders(
      <AuthContext.Provider value={authValue({ cedula: '1104567890', roles: ['ESTUDIANTE'] })}>
        <NoHabilitadoPage />
      </AuthContext.Provider>,
    )

    await user.tab()
    expect(screen.getByRole('button', { name: 'Volver al inicio' })).toHaveFocus()
  })
})
