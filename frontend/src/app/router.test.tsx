import { fixtureExpedienteDetalle } from '@/mocks/fixtures'
import { screen, within } from '@testing-library/react'
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
    signOut: vi.fn(),
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

  it('muestra la página pública en / cuando no hay sesión (AUTH-E)', async () => {
    renderRouterAs(null, '/')

    expect(await screen.findByRole('heading', { level: 1, name: 'Sistema de Gestión del Trámite de Titulación' })).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Iniciar sesión' })).not.toBeInTheDocument()
  })

  it('redirige una ruta protegida a /login cuando no hay sesión', async () => {
    renderRouterAs(null, '/estudiante')

    expect(await screen.findByRole('heading', { name: 'Iniciar sesión' })).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Mi proceso de titulación' })).not.toBeInTheDocument()
  })

  it('resuelve una ruta protegida dentro del layout con el rol correcto (/estudiante)', async () => {
    renderRouterAs({ cedula: '1104567890', roles: ['ESTUDIANTE'] }, '/estudiante')

    expect(await screen.findByRole('heading', { name: 'Mi proceso de titulación' })).toBeInTheDocument()
  })

  it('redirige a /no-habilitado cuando el rol no coincide con la ruta', async () => {
    renderRouterAs({ cedula: '1104567890', roles: ['ESTUDIANTE'] }, '/bandeja')

    expect(await screen.findByRole('heading', { name: 'Acceso restringido' })).toBeInTheDocument()
  })

  it('resuelve rutas con parámetros para un rol operativo (/bandeja/:id)', async () => {
    renderRouterAs({ cedula: '1104567890', roles: ['DECANO'] }, '/bandeja/abc-123')

    // V-08 ya no es un stub: la ruta resuelve a la página real, que carga el expediente.
    expect(await screen.findByRole('link', { name: 'Volver a la bandeja' })).toHaveAttribute('href', '/bandeja')
    expect(
      await screen.findByRole('heading', { level: 1, name: fixtureExpedienteDetalle.numero_expediente }),
    ).toBeInTheDocument()
  })

  it('redirige / al inicio por rol cuando hay sesión (ESTUDIANTE)', async () => {
    renderRouterAs({ cedula: '1104567890', roles: ['ESTUDIANTE'] }, '/')

    expect(await screen.findByRole('heading', { name: 'Mi proceso de titulación' })).toBeInTheDocument()
  })

  it('redirige / al inicio por rol cuando hay sesión (DECANO → /bandeja)', async () => {
    renderRouterAs({ cedula: '1104567890', roles: ['DECANO'] }, '/')

    expect(await screen.findByRole('heading', { level: 1, name: 'Bandeja de expedientes' })).toBeInTheDocument()
  })

  it('muestra 404 para rutas desconocidas sin exigir sesión', async () => {
    renderRouterAs(null, '/ruta-inexistente')

    expect(await screen.findByRole('heading', { level: 1, name: 'Error 404' })).toBeInTheDocument()
  })

  describe('portal del estudiante', () => {
    const ESTUDIANTE: AuthUser = { cedula: '1104567890', roles: ['ESTUDIANTE'] }

    it('resuelve /estudiante/notificaciones y /estudiante/perfil dentro del portal', async () => {
      renderRouterAs(ESTUDIANTE, '/estudiante/notificaciones')
      expect(await screen.findByRole('heading', { level: 1, name: 'Notificaciones' })).toBeInTheDocument()
      // Portal del estudiante: su navegación propia (no la del funcionario).
      expect(screen.getByRole('link', { name: 'Mi perfil' })).toHaveAttribute('href', '/estudiante/perfil')
      expect(screen.queryByRole('link', { name: 'Bandeja de trabajo' })).not.toBeInTheDocument()
    })

    it('muestra el perfil con los datos reales del estudiante', async () => {
      renderRouterAs(ESTUDIANTE, '/estudiante/perfil')
      expect(await screen.findByRole('heading', { level: 1, name: 'Mi perfil' })).toBeInTheDocument()
      expect(await screen.findByText('estudiante.prueba@unl.edu.ec')).toBeInTheDocument()
    })

    it('el estudiante ve /expedientes/:id dentro de su portal', async () => {
      renderRouterAs(ESTUDIANTE, `/expedientes/${fixtureExpedienteDetalle.id}`)
      expect(await screen.findByText('Portal del estudiante')).toBeInTheDocument()
      expect(screen.getByRole('link', { name: 'Mi perfil' })).toHaveAttribute('href', '/estudiante/perfil')
    })

    it('un rol operativo ve /expedientes/:id con la navegación de funcionario', async () => {
      renderRouterAs({ cedula: '1104567890', roles: ['SECRETARIO_ABOGADO'] }, `/expedientes/${fixtureExpedienteDetalle.id}`)
      expect(
        await screen.findByRole('heading', { level: 1, name: fixtureExpedienteDetalle.numero_expediente }),
      ).toBeInTheDocument()
      expect(screen.getByText('Gestión de titulación')).toBeInTheDocument()
      const nav = screen.getByRole('navigation', { name: 'Navegación principal' })
      expect(within(nav).getByRole('link', { name: 'Bandeja de trabajo' })).toHaveAttribute('href', '/bandeja')
      expect(within(nav).queryByRole('link', { name: 'Mi trámite' })).not.toBeInTheDocument()
    })

    it('un rol operativo no accede a las rutas del portal del estudiante', async () => {
      renderRouterAs({ cedula: '1104567890', roles: ['DECANO'] }, '/estudiante/perfil')
      expect(await screen.findByRole('heading', { name: 'Acceso restringido' })).toBeInTheDocument()
      expect(screen.queryByRole('heading', { level: 1, name: 'Mi perfil' })).not.toBeInTheDocument()
    })
  })
})
