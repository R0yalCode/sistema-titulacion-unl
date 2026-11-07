import { HttpResponse, http } from 'msw'
import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'
import { Route, Routes } from 'react-router-dom'
import { afterEach, describe, expect, it } from 'vitest'
import { AuthContext, type AuthContextValue, type AuthUser } from '@/auth/AuthContext'
import { fixtureBandejaExpediente, fixtureNotificacion } from '@/mocks/fixtures'
import { getRecentExpedientes, recordVisitedExpediente } from '@/lib/storage'
import { renderWithProviders } from '@/test/renderWithProviders'
import { server } from '@/test/server'
import StudentDashboardPage from './StudentDashboardPage'

const BANDEJA_URL = '*/api/v1/expedientes/bandeja/'
const NOTIFICACIONES_URL = '*/api/v1/notificaciones/'
const MARCAR_LEIDA_URL = '*/api/v1/notificaciones/:id/marcar-leida/'

function authValue(user: AuthUser): AuthContextValue {
  return {
    user,
    isAuthenticated: true,
    isLoading: false,
    login: () => true,
    logout: () => undefined,
    hasRole: (roles) => roles.some((role) => user.roles.includes(role)),
  }
}

function renderDashboard() {
  return renderWithProviders(
    <AuthContext.Provider value={authValue({ cedula: '1104567890', roles: ['ESTUDIANTE'] })}>
      <Routes>
        <Route element={<StudentDashboardPage />} path="/estudiante" />
        <Route element={<p>Crear solicitud (V-03)</p>} path="/estudiante/solicitud/nueva" />
        <Route element={<p>Detalle del expediente (V-04)</p>} path="/expedientes/:id" />
      </Routes>
    </AuthContext.Provider>,
    { route: '/estudiante' },
  )
}

describe('StudentDashboardPage (V-02)', () => {
  afterEach(() => {
    sessionStorage.clear()
  })

  it('RFF-201: muestra el saludo con la cédula del token', async () => {
    renderDashboard()

    expect(await screen.findByText('Hola, 1104567890')).toBeInTheDocument()
  })

  it('CA-V02-01: lista los expedientes BORRADOR/OBSERVADA y calcula los contadores sobre la página', async () => {
    renderDashboard()

    expect((await screen.findAllByText(fixtureBandejaExpediente.numero_expediente)).length).toBeGreaterThan(0)

    const borradorCard = screen.getByText('En borrador').closest('section') as HTMLElement
    expect(within(borradorCard).getByText('1')).toBeInTheDocument()

    const observadaCard = screen.getByText('Observadas').closest('section') as HTMLElement
    expect(within(observadaCard).getByText('0')).toBeInTheDocument()
  })

  it('CA-V02-02: sin expedientes muestra un estado vacío con CTA para crear uno', async () => {
    server.use(
      http.get(BANDEJA_URL, () => HttpResponse.json({ count: 0, next: null, previous: null, results: [] })),
    )
    const user = userEvent.setup()
    renderDashboard()

    expect(await screen.findByText('Sin expedientes')).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Crear solicitud' }))

    expect(await screen.findByText('Crear solicitud (V-03)')).toBeInTheDocument()
  })

  it('CA-V02-03: muestra el contador de no leídas y permite marcarlas como leídas', async () => {
    let leida = false
    server.use(
      http.get(NOTIFICACIONES_URL, () =>
        HttpResponse.json({ results: [{ ...fixtureNotificacion, leida }] }),
      ),
      http.patch(MARCAR_LEIDA_URL, () => {
        leida = true
        return HttpResponse.json({ ...fixtureNotificacion, leida: true })
      }),
    )
    const user = userEvent.setup()
    renderDashboard()

    expect(await screen.findByText('No leída')).toBeInTheDocument()
    const noLeidasCard = screen.getByText('Notificaciones sin leer').closest('section') as HTMLElement
    expect(within(noLeidasCard).getByText('1')).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Marcar como leída' }))

    await waitFor(() => expect(screen.queryByText('No leída')).not.toBeInTheDocument())
    await waitFor(() =>
      expect(
        within(screen.getByText('Notificaciones sin leer').closest('section') as HTMLElement).getByText('0'),
      ).toBeInTheDocument(),
    )
  })

  it('CA-V02-04: un error 500 en la bandeja muestra un estado de error con reintento real', async () => {
    let attempts = 0
    server.use(
      http.get(BANDEJA_URL, () => {
        attempts += 1
        if (attempts === 1) {
          return HttpResponse.json({ detail: 'Error interno.' }, { status: 500 })
        }
        return HttpResponse.json({ count: 1, next: null, previous: null, results: [fixtureBandejaExpediente] })
      }),
    )
    const user = userEvent.setup()
    renderDashboard()

    expect(await screen.findByRole('alert')).toHaveTextContent(/problema al procesar/i)
    expect(screen.queryByText('datos ficticios')).not.toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Reintentar' }))

    expect((await screen.findAllByText(fixtureBandejaExpediente.numero_expediente)).length).toBeGreaterThan(0)
    expect(attempts).toBe(2)
  })

  it('estado parcial: si notificaciones falla pero la bandeja funciona, ambas secciones siguen distinguibles', async () => {
    server.use(http.get(NOTIFICACIONES_URL, () => HttpResponse.json({ detail: 'Error interno.' }, { status: 500 })))
    renderDashboard()

    expect((await screen.findAllByText(fixtureBandejaExpediente.numero_expediente)).length).toBeGreaterThan(0)
    expect(screen.getByText('Algunos datos no se pudieron cargar. El resto del panel sigue disponible.')).toBeInTheDocument()
  })

  it('FE-T204: registra el expediente visitado como acceso rápido', async () => {
    const user = userEvent.setup()
    renderDashboard()

    await user.click(await screen.findByRole('link', { name: 'Ver expediente' }))

    expect(await screen.findByText('Detalle del expediente (V-04)')).toBeInTheDocument()
    expect(getRecentExpedientes()).toEqual([
      { id: fixtureBandejaExpediente.id, numeroExpediente: fixtureBandejaExpediente.numero_expediente, visitadoEn: expect.any(String) },
    ])
  })

  it('CA-V02-05 y FE-T204: avisa cuando un acceso rápido no aparece en la bandeja actual', async () => {
    recordVisitedExpediente('otro-expediente-enviado', 'EXP-2026-0099')
    renderDashboard()

    expect(
      await screen.findByText('No aparece en su bandeja actual; puede haber cambiado de estado'),
    ).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'EXP-2026-0099' })).toHaveAttribute(
      'href',
      '/expedientes/otro-expediente-enviado',
    )
  })

  it('RFF-205: muestra el aviso de limitación de perfil/historial', async () => {
    renderDashboard()

    expect(
      await screen.findByText(/no incluye su perfil completo ni el historial en otros estados/i),
    ).toBeInTheDocument()
    expect(
      screen.getByText(/no sustituyen un historial oficial del estudiante/i),
    ).toBeInTheDocument()
  })

  it('no presenta violaciones de accesibilidad', async () => {
    const { container } = renderDashboard()
    await screen.findAllByText(fixtureBandejaExpediente.numero_expediente)

    expect(await axe(container)).toHaveNoViolations()
  })
})
