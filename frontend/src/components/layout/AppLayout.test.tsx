import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'
import { describe, expect, it, vi } from 'vitest'
import { AuthContext, type AuthContextValue, type AuthUser } from '@/auth/AuthContext'
import { queryClient } from '@/lib/queryClient'
import { renderWithProviders } from '@/test/renderWithProviders'
import { AppLayout } from './AppLayout'

function mockAuthValue(user: AuthUser): AuthContextValue {
  return {
    user,
    isAuthenticated: true,
    isLoading: false,
    login: vi.fn().mockReturnValue(true),
    logout: vi.fn(),
    hasRole: (roles) => roles.some((role) => user.roles.includes(role)),
  }
}

describe('AppLayout', () => {
  it('expone un skip link y un main enfocable para navegación por teclado', async () => {
    renderWithProviders(<AppLayout>Contenido</AppLayout>)

    const skipLink = screen.getByRole('link', { name: 'Saltar al contenido principal' })
    expect(skipLink).toHaveAttribute('href', '#main-content')

    const main = document.getElementById('main-content')
    expect(main).toHaveAttribute('tabindex', '-1')

    await userEvent.tab()
    expect(skipLink).toHaveFocus()
  })

  it('el botón de menú alterna el estado abierto/cerrado del sidebar', async () => {
    const user = userEvent.setup()
    const { container } = renderWithProviders(<AppLayout>Contenido</AppLayout>)

    // Oculto vía @media (max-width:768px); jsdom no reevalúa esa regla (D-FE-01), así que se consulta por atributo en vez de rol/nombre.
    const menuButton = container.querySelector(
      'button[aria-label="Abrir navegación"]',
    ) as HTMLButtonElement
    expect(menuButton).toHaveAttribute('aria-expanded', 'false')

    await user.click(menuButton)
    expect(menuButton).toHaveAttribute('aria-expanded', 'true')

    await user.click(menuButton)
    expect(menuButton).toHaveAttribute('aria-expanded', 'false')
  })

  it('muestra solo los enlaces de navegación correspondientes al rol autenticado', () => {
    renderWithProviders(
      <AuthContext.Provider value={mockAuthValue({ cedula: '1234567890', roles: ['ESTUDIANTE'] })}>
        <AppLayout>Contenido</AppLayout>
      </AuthContext.Provider>,
    )

    expect(screen.getByRole('link', { name: 'Mi expediente' })).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: 'Bandeja' })).not.toBeInTheDocument()
    expect(screen.getByText('1234567890')).toBeInTheDocument()
  })

  it('el botón de cerrar sesión pide confirmación y, al aceptar, cierra sesión y limpia la caché', async () => {
    const user = userEvent.setup()
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true)
    const clearSpy = vi.spyOn(queryClient, 'clear')
    const authValue = mockAuthValue({ cedula: '1234567890', roles: ['ESTUDIANTE'] })

    renderWithProviders(
      <AuthContext.Provider value={authValue}>
        <AppLayout>Contenido</AppLayout>
      </AuthContext.Provider>,
    )

    await user.click(screen.getByRole('button', { name: 'Cerrar sesión' }))

    expect(confirmSpy).toHaveBeenCalledWith('¿Desea cerrar sesión?')
    expect(authValue.logout).toHaveBeenCalledOnce()
    expect(clearSpy).toHaveBeenCalledOnce()

    confirmSpy.mockRestore()
    clearSpy.mockRestore()
  })

  it('si se cancela la confirmación, no cierra sesión', async () => {
    const user = userEvent.setup()
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(false)
    const authValue = mockAuthValue({ cedula: '1234567890', roles: ['ESTUDIANTE'] })

    renderWithProviders(
      <AuthContext.Provider value={authValue}>
        <AppLayout>Contenido</AppLayout>
      </AuthContext.Provider>,
    )

    await user.click(screen.getByRole('button', { name: 'Cerrar sesión' }))

    expect(authValue.logout).not.toHaveBeenCalled()

    confirmSpy.mockRestore()
  })

  it('no presenta violaciones de accesibilidad detectables por axe', async () => {
    const { container } = renderWithProviders(
      <AuthContext.Provider value={mockAuthValue({ cedula: '1234567890', roles: ['ESTUDIANTE'] })}>
        <AppLayout>Contenido</AppLayout>
      </AuthContext.Provider>,
    )

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
