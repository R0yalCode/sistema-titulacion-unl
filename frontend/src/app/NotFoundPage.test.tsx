import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { axe } from 'vitest-axe'
import { describe, expect, it, vi } from 'vitest'
import { AuthContext, type AuthContextValue, type AuthUser } from '@/auth/AuthContext'
import { renderWithProviders } from '@/test/renderWithProviders'
import NotFoundPage from './NotFoundPage'

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

describe('NotFoundPage', () => {
  it('ofrece ir a iniciar sesión cuando no hay sesión', () => {
    renderWithProviders(
      <AuthContext.Provider value={authValue(null)}>
        <NotFoundPage />
      </AuthContext.Provider>,
    )

    expect(screen.getByRole('button', { name: 'Ir a iniciar sesión' })).toBeInTheDocument()
  })

  it('ofrece ir al inicio por rol cuando hay sesión', () => {
    renderWithProviders(
      <AuthContext.Provider value={authValue({ cedula: '1104567890', roles: ['DECANO'] })}>
        <NotFoundPage />
      </AuthContext.Provider>,
    )

    expect(screen.getByRole('button', { name: 'Ir a mi inicio' })).toBeInTheDocument()
  })

  it('ofrece una alternativa de navegación segura (volver atrás) en ambos contextos', () => {
    renderWithProviders(
      <AuthContext.Provider value={authValue(null)}>
        <NotFoundPage />
      </AuthContext.Provider>,
    )

    expect(screen.getByRole('button', { name: 'Volver atrás' })).toBeInTheDocument()
  })

  it('no revela si un recurso pertenece a otro usuario', () => {
    renderWithProviders(<NotFoundPage />)

    expect(document.body.textContent).not.toMatch(/pertenece a otro usuario|no le pertenece/i)
  })

  it('es operable por teclado', async () => {
    const user = userEvent.setup()
    renderWithProviders(
      <AuthContext.Provider value={authValue(null)}>
        <NotFoundPage />
      </AuthContext.Provider>,
    )

    await user.tab()
    expect(screen.getByRole('button', { name: 'Ir a iniciar sesión' })).toHaveFocus()
    await user.tab()
    expect(screen.getByRole('button', { name: 'Volver atrás' })).toHaveFocus()
  })

  it('mantiene una jerarquía de encabezados válida (h1 → h2)', () => {
    renderWithProviders(<NotFoundPage />)

    const h1 = screen.getByRole('heading', { level: 1 })
    const h2 = screen.getByRole('heading', { level: 2 })
    expect(h1).toHaveTextContent('Error 404')
    expect(h2).toHaveTextContent('Página no encontrada')
  })

  it('muestra la mascota 404 como imagen decorativa', () => {
    const { container } = renderWithProviders(
      <AuthContext.Provider value={authValue(null)}>
        <NotFoundPage />
      </AuthContext.Provider>,
    )

    const mascot = container.querySelector('img')
    expect(mascot).toHaveAttribute('src', '/assets/mascotas/mascota-404.png')
    expect(mascot).toHaveAttribute('alt', '')
  })

  it('el botón primario navega a /login cuando no hay sesión', async () => {
    const user = userEvent.setup()
    renderWithProviders(
      <AuthContext.Provider value={authValue(null)}>
        <Routes>
          <Route element={<NotFoundPage />} path="/ruta-inexistente" />
          <Route element={<p>Pantalla de login</p>} path="/login" />
        </Routes>
      </AuthContext.Provider>,
      { route: '/ruta-inexistente' },
    )

    await user.click(screen.getByRole('button', { name: 'Ir a iniciar sesión' }))

    expect(screen.getByText('Pantalla de login')).toBeInTheDocument()
  })

  it('el botón primario navega al inicio por rol cuando hay sesión', async () => {
    const user = userEvent.setup()
    renderWithProviders(
      <AuthContext.Provider value={authValue({ cedula: '1104567890', roles: ['DECANO'] })}>
        <Routes>
          <Route element={<NotFoundPage />} path="/ruta-inexistente" />
          <Route element={<p>Bandeja del funcionario</p>} path="/bandeja" />
        </Routes>
      </AuthContext.Provider>,
      { route: '/ruta-inexistente' },
    )

    await user.click(screen.getByRole('button', { name: 'Ir a mi inicio' }))

    expect(screen.getByText('Bandeja del funcionario')).toBeInTheDocument()
  })

  it('"Volver atrás" usa el historial real (initialIndex con entrada previa)', async () => {
    const user = userEvent.setup()
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/origen', '/ruta-inexistente']} initialIndex={1}>
          <AuthContext.Provider value={authValue(null)}>
            <Routes>
              <Route element={<p>Origen</p>} path="/origen" />
              <Route element={<NotFoundPage />} path="/ruta-inexistente" />
            </Routes>
          </AuthContext.Provider>
        </MemoryRouter>
      </QueryClientProvider>,
    )

    await user.click(screen.getByRole('button', { name: 'Volver atrás' }))

    expect(await screen.findByText('Origen')).toBeInTheDocument()
  })

  it('no presenta violaciones de accesibilidad', async () => {
    const { container } = renderWithProviders(
      <AuthContext.Provider value={authValue(null)}>
        <NotFoundPage />
      </AuthContext.Provider>,
    )

    expect(await axe(container)).toHaveNoViolations()
  })
})
