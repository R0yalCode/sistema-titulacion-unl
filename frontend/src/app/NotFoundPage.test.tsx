import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Route, Routes } from 'react-router-dom'
import { axe } from 'vitest-axe'
import { describe, expect, it, vi } from 'vitest'
import { AuthContext, type AuthContextValue, type AuthUser } from '@/auth/AuthContext'
import { recargarPagina } from '@/lib/recargar'
import { renderWithProviders } from '@/test/renderWithProviders'
import NotFoundPage from './NotFoundPage'

vi.mock('@/lib/recargar', () => ({ recargarPagina: vi.fn() }))

function authValue(user: AuthUser | null): AuthContextValue {
  return {
    user,
    isAuthenticated: user !== null,
    isLoading: false,
    login: vi.fn().mockReturnValue(true),
    logout: vi.fn(),
    signOut: vi.fn(),
    hasRole: (roles) => user !== null && roles.some((role) => user.roles.includes(role)),
  }
}

function renderNotFound(user: AuthUser | null) {
  return renderWithProviders(
    <AuthContext.Provider value={authValue(user)}>
      <Routes>
        <Route element={<NotFoundPage />} path="/ruta-inexistente" />
        <Route element={<p>Página pública</p>} path="/" />
        <Route element={<p>Bandeja del funcionario</p>} path="/bandeja" />
      </Routes>
    </AuthContext.Provider>,
    { route: '/ruta-inexistente' },
  )
}

describe('NotFoundPage (404 del sistema de errores)', () => {
  it('muestra la vista 404 con los textos aprobados y el título como h1 enfocado', () => {
    renderNotFound(null)
    const titulo = screen.getByRole('heading', { level: 1, name: 'Página no encontrada' })
    expect(titulo).toHaveFocus()
    expect(screen.getByText(/no encontramos la página que estás buscando/)).toBeInTheDocument()
  })

  it('sin sesión, «Ir al inicio» lleva a la página pública', async () => {
    const user = userEvent.setup()
    renderNotFound(null)
    await user.click(screen.getByRole('button', { name: 'Ir al inicio' }))
    expect(screen.getByText('Página pública')).toBeInTheDocument()
  })

  it('con sesión, «Ir al inicio» lleva al panel real del rol', async () => {
    const user = userEvent.setup()
    renderNotFound({ cedula: '1104567890', roles: ['DECANO'] })
    expect(screen.getByRole('link', { name: 'Universidad Nacional de Loja' })).toHaveAttribute('href', '/bandeja')
    await user.click(screen.getByRole('button', { name: 'Ir al inicio' }))
    expect(screen.getByText('Bandeja del funcionario')).toBeInTheDocument()
  })

  it('«Intentar nuevamente» vuelve a pedir la misma dirección (sin redirigir ni ocultar el 404)', async () => {
    const user = userEvent.setup()
    renderNotFound(null)
    await user.click(screen.getByRole('button', { name: 'Intentar nuevamente' }))
    expect(recargarPagina).toHaveBeenCalledTimes(1)
    expect(screen.getByRole('heading', { level: 1, name: 'Página no encontrada' })).toBeInTheDocument()
  })

  it('es operable por teclado en orden lógico', async () => {
    const user = userEvent.setup()
    renderNotFound(null)
    // El foco inicial está en el título (h1); el siguiente Tab llega a las acciones.
    expect(screen.getByRole('heading', { level: 1 })).toHaveFocus()
    await user.tab()
    expect(screen.getByRole('button', { name: 'Ir al inicio' })).toHaveFocus()
    await user.tab()
    expect(screen.getByRole('button', { name: 'Intentar nuevamente' })).toHaveFocus()
  })

  it('no revela si un recurso pertenece a otra cuenta y no etiqueta a la mascota', () => {
    const { container } = renderNotFound(null)
    expect(document.body.textContent).not.toMatch(/pertenece a otro usuario|no le pertenece|mascota/i)
    expect(container.querySelector('img[src="/assets/mascotas/mascota-404.png"]')).toHaveAttribute('alt', '')
  })

  it('no presenta violaciones de accesibilidad detectables por axe', async () => {
    const { container } = renderNotFound(null)
    expect(await axe(container)).toHaveNoViolations()
  })
})
