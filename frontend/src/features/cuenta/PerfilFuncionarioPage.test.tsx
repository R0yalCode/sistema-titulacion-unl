import { screen } from '@testing-library/react'
import { axe } from 'vitest-axe'
import { describe, expect, it } from 'vitest'
import { AuthContext, type AuthContextValue, type AuthUser } from '@/auth/AuthContext'
import { renderWithProviders } from '@/test/renderWithProviders'
import PerfilFuncionarioPage from './PerfilFuncionarioPage'

function authValue(user: AuthUser): AuthContextValue {
  return {
    user,
    isAuthenticated: true,
    isLoading: false,
    login: () => true,
    logout: () => undefined,
    signOut: () => undefined,
    hasRole: (roles) => roles.some((role) => user.roles.includes(role)),
  }
}

describe('PerfilFuncionarioPage', () => {
  it('muestra solo los datos de la sesión (cédula y roles legibles)', () => {
    renderWithProviders(
      <AuthContext.Provider value={authValue({ cedula: '1100000000', roles: ['DECANO', 'ANALISTA_APOYO'] })}>
        <PerfilFuncionarioPage />
      </AuthContext.Provider>,
    )
    expect(screen.getByRole('heading', { level: 1, name: 'Mi perfil' })).toBeInTheDocument()
    expect(screen.getByText('1100000000')).toBeInTheDocument()
    expect(screen.getByText('Decanato')).toBeInTheDocument()
    expect(screen.getByText('Analista de apoyo')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Restablecer mi contraseña por correo' })).toHaveAttribute('href', '/recuperar-contrasena')
  })

  it('no tiene violaciones de accesibilidad detectables (axe)', async () => {
    const { container } = renderWithProviders(
      <AuthContext.Provider value={authValue({ cedula: '1100000000', roles: ['DECANO'] })}>
        <PerfilFuncionarioPage />
      </AuthContext.Provider>,
    )
    expect(await axe(container)).toHaveNoViolations()
  })
})
