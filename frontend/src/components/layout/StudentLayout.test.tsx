import { HttpResponse, http } from 'msw'
import { screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'
import { Route, Routes } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { AuthContext, type AuthContextValue } from '@/auth/AuthContext'
import { fixtureMiTramite, fixtureNotificacion } from '@/mocks/fixtures'
import { renderWithProviders } from '@/test/renderWithProviders'
import { server } from '@/test/server'
import { StudentLayout } from './StudentLayout'

const MI_TRAMITE_URL = '*/api/v1/expedientes/mi-tramite/'
const NOTIFICACIONES_URL = '*/api/v1/notificaciones/'
const EXPEDIENTE_ID = fixtureMiTramite.expediente.id

function authValue(signOut = vi.fn()): AuthContextValue {
  return {
    user: { cedula: '1104567890', roles: ['ESTUDIANTE'] },
    isAuthenticated: true,
    isLoading: false,
    login: () => true,
    logout: () => undefined,
    signOut,
    hasRole: (roles) => roles.includes('ESTUDIANTE'),
  }
}

function renderLayout(route = '/estudiante', signOut = vi.fn()) {
  return renderWithProviders(
    <AuthContext.Provider value={authValue(signOut)}>
      <Routes>
        <Route element={<StudentLayout />}>
          <Route element={<p>Contenido de inicio</p>} path="/estudiante" />
          <Route element={<p>Contenido de notificaciones</p>} path="/estudiante/notificaciones" />
          <Route element={<p>Contenido del perfil</p>} path="/estudiante/perfil" />
          <Route element={<p>Contenido del trámite</p>} path="/expedientes/:id" />
          <Route element={<p>Contenido de documentos</p>} path="/expedientes/:id/peticiones" />
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

describe('StudentLayout (portal del estudiante)', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('con expediente enlaza Inicio, Mi trámite, Documentos, Notificaciones y Mi perfil a rutas reales', async () => {
    renderLayout()

    expect(await within(nav()).findByRole('link', { name: 'Mi trámite' })).toHaveAttribute(
      'href',
      `/expedientes/${EXPEDIENTE_ID}`,
    )
    expect(within(nav()).getByRole('link', { name: 'Documentos' })).toHaveAttribute(
      'href',
      `/expedientes/${EXPEDIENTE_ID}/peticiones`,
    )
    expect(within(nav()).getByRole('link', { name: 'Inicio' })).toHaveAttribute('aria-current', 'page')
    expect(within(nav()).getByRole('link', { name: 'Mi perfil' })).toHaveAttribute('href', '/estudiante/perfil')
    expect(screen.getByRole('img', { name: 'Universidad Nacional de Loja' })).toBeInTheDocument()
  })

  it('sin expediente no muestra enlaces que dependan de él y ofrece Nueva solicitud', async () => {
    server.use(http.get(MI_TRAMITE_URL, () => HttpResponse.json({ ...fixtureMiTramite, expediente: null })))
    renderLayout()

    expect(await within(nav()).findByRole('link', { name: 'Nueva solicitud' })).toHaveAttribute(
      'href',
      '/estudiante/solicitud/nueva',
    )
    expect(within(nav()).queryByRole('link', { name: 'Mi trámite' })).not.toBeInTheDocument()
    expect(within(nav()).queryByRole('link', { name: 'Documentos' })).not.toBeInTheDocument()
  })

  it('marca como activa la sección Documentos y no Mi trámite en las rutas de peticiones', async () => {
    renderLayout(`/expedientes/${EXPEDIENTE_ID}/peticiones`)

    expect(await within(nav()).findByRole('link', { name: 'Documentos' })).toHaveAttribute('aria-current', 'page')
    expect(within(nav()).getByRole('link', { name: 'Mi trámite' })).not.toHaveAttribute('aria-current')
  })

  it('muestra el nombre real del estudiante y el contador de notificaciones sin leer', async () => {
    server.use(
      http.get(NOTIFICACIONES_URL, () =>
        HttpResponse.json({ results: [fixtureNotificacion, { ...fixtureNotificacion, id: 'leida', leida: true }] }),
      ),
    )
    renderLayout()

    expect(await screen.findByRole('link', { name: 'Notificaciones, 1 sin leer' })).toHaveAttribute(
      'href',
      '/estudiante/notificaciones',
    )
    const perfil = await screen.findByRole('link', { name: /^Mi perfil:/ })
    expect(perfil).toHaveAttribute('href', '/estudiante/perfil')
    expect(perfil).toHaveTextContent('Mi perfil: Estudiante de Prueba')
    // Iniciales del primer y último nombre.
    expect(within(perfil).getByText('EP')).toBeInTheDocument()
  })

  it('abre y cierra el menú móvil con el botón y con Escape, devolviendo el foco', async () => {
    const user = userEvent.setup()
    renderLayout()

    const abrir = screen.getByLabelText('Abrir menú')
    expect(abrir).toHaveAttribute('aria-expanded', 'false')
    await user.click(abrir)
    expect(abrir).toHaveAttribute('aria-expanded', 'true')
    expect(within(nav()).getByRole('link', { name: 'Inicio' })).toHaveFocus()

    // jsdom no evalúa @media y deja el botón con display:none (D-FE-01), así
    // que no puede recibir el foco real; se verifica que se le devuelve.
    const focusSpy = vi.spyOn(abrir, 'focus')
    await user.keyboard('{Escape}')
    expect(abrir).toHaveAttribute('aria-expanded', 'false')
    expect(focusSpy).toHaveBeenCalled()
  })

  it('cierra el menú móvil al navegar', async () => {
    const user = userEvent.setup()
    renderLayout()

    const abrir = screen.getByLabelText('Abrir menú')
    await user.click(abrir)
    await user.click(within(nav()).getByRole('link', { name: 'Mi perfil' }))
    expect(await screen.findByText('Contenido del perfil')).toBeInTheDocument()
    expect(abrir).toHaveAttribute('aria-expanded', 'false')
  })

  it('cierra la sesión solo tras confirmar en el diálogo', async () => {
    const user = userEvent.setup()
    const signOut = vi.fn()
    renderLayout('/estudiante', signOut)

    await user.click(screen.getByRole('button', { name: 'Cerrar sesión' }))
    await user.click(within(screen.getByRole('alertdialog')).getByRole('button', { name: 'Cancelar' }))
    expect(signOut).not.toHaveBeenCalled()

    await user.click(screen.getByRole('button', { name: 'Cerrar sesión' }))
    await user.click(within(screen.getByRole('alertdialog')).getByRole('button', { name: 'Cerrar sesión' }))
    expect(signOut).toHaveBeenCalledTimes(1)
    expect(await screen.findByText('Pantalla de login')).toBeInTheDocument()
  })

  it('no tiene violaciones de accesibilidad detectables (axe)', async () => {
    const { container } = renderLayout()
    await within(nav()).findByRole('link', { name: 'Mi trámite' })
    expect(await axe(container)).toHaveNoViolations()
  })
})
