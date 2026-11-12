import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { axe } from 'vitest-axe'
import { describe, expect, it, vi } from 'vitest'
import { AuthContext, type AuthContextValue, type AuthUser } from '@/auth/AuthContext'
import { RequireRole } from '@/auth/guards'
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

  it('CA-V09-01: desde la guarda muestra el motivo y una alternativa, sin revelar la ruta pedida', () => {
    render(
      <AuthContext.Provider value={authValue({ cedula: '1104567890', roles: ['ESTUDIANTE'] })}>
        <MemoryRouter initialEntries={['/bandeja/expediente-secreto']}>
          <Routes>
            <Route element={<RequireRole roles={['DECANO']} />}>
              <Route element={<p>Contenido protegido</p>} path="/bandeja/:id" />
            </Route>
            <Route element={<NoHabilitadoPage />} path="/no-habilitado" />
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>,
    )

    expect(screen.getByRole('status')).toHaveTextContent('Acceso restringido')
    expect(screen.getByText('V09-ROL')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Volver al inicio' })).toBeInTheDocument()
    expect(document.body.textContent).not.toMatch(/expediente-secreto|DECANO/)
  })

  it('CA-V09-02: una funcionalidad no soportada muestra la dependencia BE-xx y su código, sin violaciones de axe', async () => {
    const { container } = renderWithProviders(
      <AuthContext.Provider value={authValue({ cedula: '1104567890', roles: ['SECRETARIA_CARRERA'] })}>
        <Routes>
          <Route element={<NoHabilitadoPage />} path="/no-habilitado" />
        </Routes>
      </AuthContext.Provider>,
      { route: '/no-habilitado?motivo=no-disponible&dependencia=BE-09' },
    )

    expect(screen.getByRole('status')).toHaveTextContent('Funcionalidad no disponible en esta versión')
    expect(screen.getByText('BE-09')).toBeInTheDocument()
    expect(screen.getByText(/filtros en el servidor/)).toBeInTheDocument()
    expect(screen.getByText('V09-BE-09')).toBeInTheDocument()
    expect(container.querySelector('img')).toBeNull()
    expect(await axe(container)).toHaveNoViolations()
  })

  it('CA-V09-03: "Volver atrás" regresa a la ruta válida anterior', async () => {
    const user = userEvent.setup()
    render(
      <AuthContext.Provider value={authValue({ cedula: '1104567890', roles: ['DECANO'] })}>
        <MemoryRouter initialEntries={['/bandeja', '/no-habilitado']} initialIndex={1}>
          <Routes>
            <Route element={<p>Bandeja del funcionario</p>} path="/bandeja" />
            <Route element={<NoHabilitadoPage />} path="/no-habilitado" />
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>,
    )

    await user.click(screen.getByRole('button', { name: 'Volver atrás' }))

    expect(screen.getByText('Bandeja del funcionario')).toBeInTheDocument()
  })

  it('no ofrece "Volver atrás" si no hay historial dentro de la aplicación', () => {
    renderWithProviders(
      <AuthContext.Provider value={authValue({ cedula: '1104567890', roles: ['DECANO'] })}>
        <NoHabilitadoPage />
      </AuthContext.Provider>,
    )

    expect(screen.queryByRole('button', { name: 'Volver atrás' })).not.toBeInTheDocument()
  })

  it('una cuenta sin rol reconocido no recibe un "Volver al inicio" que la devolvería aquí: ofrece cerrar sesión', async () => {
    const user = userEvent.setup()
    const valor = authValue({ cedula: '1104567890', roles: [] })
    renderWithProviders(
      <AuthContext.Provider value={valor}>
        <Routes>
          <Route element={<NoHabilitadoPage />} path="/no-habilitado" />
          <Route element={<p>Pantalla de login</p>} path="/login" />
        </Routes>
      </AuthContext.Provider>,
      { route: '/no-habilitado' },
    )

    expect(screen.getByRole('status')).toHaveTextContent('Cuenta sin rol habilitado')
    expect(screen.queryByRole('button', { name: 'Volver al inicio' })).not.toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Cerrar sesión' }))

    expect(valor.logout).toHaveBeenCalledTimes(1)
    expect(screen.getByText('Pantalla de login')).toBeInTheDocument()
  })

  it('CA-V09-04: el mensaje y el código de referencia se anuncian y no inventan datos de contacto', () => {
    renderWithProviders(
      <AuthContext.Provider value={authValue({ cedula: '1104567890', roles: ['ESTUDIANTE'] })}>
        <NoHabilitadoPage />
      </AuthContext.Provider>,
    )

    expect(screen.getByRole('status')).toHaveAttribute('role', 'status')
    expect(screen.getByText(/indique el código de referencia/)).toBeInTheDocument()
    expect(document.body.textContent).not.toMatch(/@|\+593|teléfono|tel\./i)
  })
})
