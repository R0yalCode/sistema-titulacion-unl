import { screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'
import { HttpResponse, http } from 'msw'
import { Route, Routes } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { AuthContext, type AuthContextValue, type AuthUser } from '@/auth/AuthContext'
import { fixtureNotificacion } from '@/mocks/fixtures'
import { queryClient } from '@/lib/queryClient'
import { renderWithProviders } from '@/test/renderWithProviders'
import { server } from '@/test/server'
import { AppLayout } from './AppLayout'

const NOTIFICACIONES_URL = '*/api/v1/notificaciones/'

function mockAuthValue(user: AuthUser): AuthContextValue {
  return {
    user,
    isAuthenticated: true,
    isLoading: false,
    login: vi.fn().mockReturnValue(true),
    logout: vi.fn(),
    signOut: vi.fn(),
    hasRole: (roles) => roles.some((role) => user.roles.includes(role)),
  }
}

function renderLayout(authValue: AuthContextValue, route = '/bandeja') {
  return renderWithProviders(
    <AuthContext.Provider value={authValue}>
      <Routes>
        <Route element={<AppLayout />}>
          <Route element={<p>Contenido de la bandeja</p>} path="/bandeja" />
          <Route element={<p>Contenido del perfil</p>} path="/perfil" />
          <Route element={<p>Estado de acceso</p>} path="/no-habilitado" />
        </Route>
        <Route element={<p>Pantalla de login</p>} path="/login" />
      </Routes>
    </AuthContext.Provider>,
    { route },
  )
}

function nav() {
  return screen.getByRole('navigation', { name: 'Navegación principal' })
}

describe('AppLayout (portal de funcionarios sobre AppShell)', () => {
  afterEach(() => {
    vi.restoreAllMocks()
    localStorage.clear()
  })

  it('expone un skip link y un único main enfocable para navegación por teclado', async () => {
    const user = userEvent.setup()
    renderLayout(mockAuthValue({ cedula: '1234567890', roles: ['DECANO'] }))

    const skipLink = screen.getByRole('link', { name: 'Saltar al contenido principal' })
    expect(skipLink).toHaveAttribute('href', '#main-content')
    const mains = screen.getAllByRole('main')
    expect(mains).toHaveLength(1)
    expect(mains[0]).toHaveAttribute('tabindex', '-1')

    await user.tab()
    expect(skipLink).toHaveFocus()
  })

  it('el botón de menú alterna el estado abierto/cerrado del panel lateral', async () => {
    const user = userEvent.setup()
    renderLayout(mockAuthValue({ cedula: '1234567890', roles: ['DECANO'] }))

    // jsdom no evalúa @media: el botón móvil queda oculto por CSS (D-FE-01).
    const menuButton = screen.getByLabelText('Abrir menú')
    expect(menuButton).toHaveAttribute('aria-expanded', 'false')
    await user.click(menuButton)
    expect(menuButton).toHaveAttribute('aria-expanded', 'true')
    await user.click(within(screen.getByRole('complementary', { name: 'Menú principal' })).getAllByLabelText('Cerrar menú')[0] as HTMLElement)
    expect(menuButton).toHaveAttribute('aria-expanded', 'false')
  })

  it('muestra solo la navegación autorizada para un rol operativo', () => {
    renderLayout(mockAuthValue({ cedula: '1234567890', roles: ['SECRETARIO_ABOGADO'] }))

    expect(within(nav()).getByRole('link', { name: 'Bandeja de trabajo' })).toHaveAttribute('href', '/bandeja')
    expect(within(nav()).getByRole('link', { name: /Notificaciones/ })).toHaveAttribute('href', '/notificaciones')
    expect(within(nav()).getByRole('link', { name: 'Mi perfil' })).toHaveAttribute('href', '/perfil')
    expect(within(nav()).queryByRole('link', { name: /Consola de administración/ })).not.toBeInTheDocument()
    expect(within(nav()).queryByRole('link', { name: 'Mi trámite' })).not.toBeInTheDocument()
    // Identidad: rol legible y cédula, no códigos internos.
    expect(screen.getByText('Secretaría abogada')).toBeInTheDocument()
    expect(screen.getByText('C.I. 1234567890')).toBeInTheDocument()
  })

  it('el administrador ve además el acceso a la consola interna existente', () => {
    renderLayout(mockAuthValue({ cedula: '1234567890', roles: ['ADMINISTRADOR'] }))
    const enlace = within(nav()).getByRole('link', { name: /Consola de administración/ })
    expect(enlace.getAttribute('href')).toMatch(/\/admin\/$/)
  })

  it('un rol sin capacidades en el portal (RESPONSABLE_DEPENDENCIA) solo ve el estado de su acceso', () => {
    renderLayout(mockAuthValue({ cedula: '1234567890', roles: ['RESPONSABLE_DEPENDENCIA'] }), '/no-habilitado')
    const enlaces = within(nav()).getAllByRole('link')
    expect(enlaces).toHaveLength(1)
    expect(enlaces[0]).toHaveAttribute('href', '/no-habilitado')
    expect(screen.queryByRole('link', { name: /Notificaciones/ })).not.toBeInTheDocument()
  })

  it('muestra el contador real de notificaciones sin leer', async () => {
    server.use(http.get(NOTIFICACIONES_URL, () => HttpResponse.json({ results: [fixtureNotificacion] })))
    renderLayout(mockAuthValue({ cedula: '1234567890', roles: ['DECANO'] }))
    expect(await screen.findByRole('link', { name: 'Notificaciones, 1 sin leer' })).toHaveAttribute('href', '/notificaciones')
  })

  it('cerrar sesión pide confirmación en un diálogo accesible y, al aceptar, cierra sesión y limpia la caché', async () => {
    const user = userEvent.setup()
    const authValue = mockAuthValue({ cedula: '1234567890', roles: ['DECANO'] })
    const clearSpy = vi.spyOn(queryClient, 'clear')
    renderLayout(authValue)

    await user.click(screen.getByRole('button', { name: 'Cerrar sesión' }))
    const dialogo = screen.getByRole('alertdialog', { name: '¿Cerrar sesión?' })
    await user.click(within(dialogo).getByRole('button', { name: 'Cerrar sesión' }))

    expect(authValue.signOut).toHaveBeenCalledOnce()
    expect(clearSpy).toHaveBeenCalledOnce()
    expect(await screen.findByText('Pantalla de login')).toBeInTheDocument()
  })

  it('si se cancela la confirmación, no cierra sesión', async () => {
    const user = userEvent.setup()
    const authValue = mockAuthValue({ cedula: '1234567890', roles: ['DECANO'] })
    renderLayout(authValue)

    await user.click(screen.getByRole('button', { name: 'Cerrar sesión' }))
    await user.click(within(screen.getByRole('alertdialog')).getByRole('button', { name: 'Cancelar' }))
    expect(authValue.signOut).not.toHaveBeenCalled()
    expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument()
  })

  it('el menú lateral se puede contraer y conserva el nombre accesible de cada enlace', async () => {
    const user = userEvent.setup()
    renderLayout(mockAuthValue({ cedula: '1234567890', roles: ['DECANO'] }))
    const boton = screen.getByRole('button', { name: 'Contraer menú' })
    expect(boton).toHaveAttribute('aria-expanded', 'true')
    await user.click(boton)
    expect(screen.getByRole('button', { name: 'Expandir menú' })).toHaveAttribute('aria-expanded', 'false')
    expect(within(nav()).getByRole('link', { name: 'Bandeja de trabajo' })).toBeInTheDocument()
  })

  it('combina la capa Liquid Glass con la paleta del administrador', () => {
    const { unmount } = renderLayout(mockAuthValue({ cedula: '1234567890', roles: ['ADMINISTRADOR'] }))
    const shellAdmin = screen.getByRole('complementary', { name: 'Menú principal' }).closest('[data-glass]')
    expect(shellAdmin).toHaveAttribute('data-glass', 'on')
    expect(shellAdmin).toHaveAttribute('data-visual', 'siaaf-modern')
    unmount()

    renderLayout(mockAuthValue({ cedula: '1234567890', roles: ['DECANO'] }))
    const shell = screen.getByRole('complementary', { name: 'Menú principal' }).closest('[data-glass]')
    expect(shell).toHaveAttribute('data-glass', 'on')
    expect(shell).not.toHaveAttribute('data-visual')
  })

  it('no presenta violaciones de accesibilidad detectables por axe', async () => {
    const { container } = renderLayout(mockAuthValue({ cedula: '1234567890', roles: ['DECANO'] }))
    expect(await axe(container)).toHaveNoViolations()
  })
})
