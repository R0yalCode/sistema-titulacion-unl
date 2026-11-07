import { HttpResponse, http } from 'msw'
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'
import { Route, Routes } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { AuthContext, type AuthContextValue, type AuthUser } from '@/auth/AuthContext'
import { fixtureExpedienteBorrador } from '@/mocks/fixtures'
import { getNuevaSolicitudDraft, getRecentExpedientes } from '@/lib/storage'
import { renderWithProviders } from '@/test/renderWithProviders'
import { server } from '@/test/server'
import NuevaSolicitudPage from './NuevaSolicitudPage'

const EXPEDIENTES_URL = '*/api/v1/expedientes/'
const VALID_UUID = '11111111-1111-1111-1111-111111111111'

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

function renderPage() {
  return renderWithProviders(
    <AuthContext.Provider value={authValue({ cedula: '1104567890', roles: ['ESTUDIANTE'] })}>
      <Routes>
        <Route element={<NuevaSolicitudPage />} path="/estudiante/solicitud/nueva" />
        <Route element={<p>Dashboard del estudiante (V-02)</p>} path="/estudiante" />
        <Route element={<p>Detalle del expediente (V-04)</p>} path="/expedientes/:id" />
        <Route element={<p>No habilitado (V-09)</p>} path="/no-habilitado" />
      </Routes>
    </AuthContext.Provider>,
    { route: '/estudiante/solicitud/nueva' },
  )
}

async function fillAndSubmit(carreraId: string) {
  const user = userEvent.setup()
  await user.type(screen.getByLabelText(/^Identificador de carrera/), carreraId)
  await user.click(screen.getByRole('button', { name: 'Enviar solicitud' }))
}

describe('NuevaSolicitudPage (V-03)', () => {
  afterEach(() => {
    sessionStorage.clear()
    vi.restoreAllMocks()
  })

  it('CA: crea el expediente, muestra un toast, registra el ID y redirige a /expedientes/:id', async () => {
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    renderPage()

    await fillAndSubmit(VALID_UUID)

    expect(await screen.findByText('Detalle del expediente (V-04)')).toBeInTheDocument()
    expect(getRecentExpedientes()).toEqual([
      {
        id: fixtureExpedienteBorrador.id,
        numeroExpediente: fixtureExpedienteBorrador.numero_expediente,
        visitadoEn: expect.any(String),
      },
    ])
    expect(getNuevaSolicitudDraft()).toBeNull()
  })

  it('error: expediente activo existente muestra el mensaje real y ofrece volver al panel', async () => {
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    server.use(
      http.post(EXPEDIENTES_URL, () =>
        HttpResponse.json(
          { detail: 'El estudiante ya posee un expediente de titulacion activo; no se permite iniciar otro tramite en curso (HU-001).' },
          { status: 400 },
        ),
      ),
    )
    const user = userEvent.setup()
    renderPage()

    await fillAndSubmit(VALID_UUID)

    expect(await screen.findByRole('alert')).toHaveTextContent(/ya posee un expediente de titulacion activo/i)
    await user.click(screen.getByRole('button', { name: 'Ir a mi panel' }))

    expect(await screen.findByText('Dashboard del estudiante (V-02)')).toBeInTheDocument()
  })

  it('error: 400 genérico de validación muestra el mensaje real sin botón de panel', async () => {
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    server.use(
      http.post(EXPEDIENTES_URL, () =>
        HttpResponse.json({ carrera_id: ['carrera_id debe ser un UUID institucional valido (HU-001).'] }, { status: 400 }),
      ),
    )
    renderPage()

    await fillAndSubmit(VALID_UUID)

    expect(await screen.findByRole('alert')).toHaveTextContent('Revise los campos marcados.')
    expect(screen.queryByRole('button', { name: 'Ir a mi panel' })).not.toBeInTheDocument()
  })

  it('error: un código no mapeado (p. ej. 404) muestra un mensaje genérico', async () => {
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    server.use(http.post(EXPEDIENTES_URL, () => HttpResponse.json({ detail: 'No encontrado.' }, { status: 404 })))
    renderPage()

    await fillAndSubmit(VALID_UUID)

    expect(await screen.findByRole('alert')).toHaveTextContent('No se pudo crear la solicitud. Intente nuevamente.')
  })

  it('borrador local: se limpia si el estudiante borra el campo por completo', async () => {
    const user = userEvent.setup()
    renderPage()

    const input = screen.getByLabelText(/^Identificador de carrera/)
    await user.type(input, VALID_UUID)
    expect(getNuevaSolicitudDraft()).toBe(VALID_UUID)

    await user.clear(input)

    expect(getNuevaSolicitudDraft()).toBeNull()
  })

  it('error: 403 redirige al flujo existente de V-09', async () => {
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    server.use(http.post(EXPEDIENTES_URL, () => HttpResponse.json({ detail: 'Prohibido.' }, { status: 403 })))
    renderPage()

    await fillAndSubmit(VALID_UUID)

    expect(await screen.findByText('No habilitado (V-09)')).toBeInTheDocument()
  })

  it('error: 500 muestra un mensaje comprensible', async () => {
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    server.use(http.post(EXPEDIENTES_URL, () => HttpResponse.json({ detail: 'Error interno.' }, { status: 500 })))
    renderPage()

    await fillAndSubmit(VALID_UUID)

    expect(await screen.findByRole('alert')).toHaveTextContent(/problema al procesar/i)
  })

  it('error de red/timeout: advierte resultado ambiguo y ofrece ir al panel en lugar de reintentar automáticamente', async () => {
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    server.use(http.post(EXPEDIENTES_URL, () => HttpResponse.error()))
    const user = userEvent.setup()
    renderPage()

    await fillAndSubmit(VALID_UUID)

    expect(await screen.findByRole('alert')).toHaveTextContent(/no se pudo confirmar si la solicitud se creó/i)
    expect(screen.queryByRole('button', { name: 'Reintentar' })).not.toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Ir a mi panel' }))
    expect(await screen.findByText('Dashboard del estudiante (V-02)')).toBeInTheDocument()
  })

  it('protección ante doble creación: un segundo envío no dispara una segunda petición mientras la primera está en curso', async () => {
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    let attempts = 0
    server.use(
      http.post(EXPEDIENTES_URL, async () => {
        attempts += 1
        await new Promise((resolve) => setTimeout(resolve, 60))
        return HttpResponse.json(fixtureExpedienteBorrador, { status: 201 })
      }),
    )
    const user = userEvent.setup()
    renderPage()

    await user.type(screen.getByLabelText(/^Identificador de carrera/), VALID_UUID)
    const button = screen.getByRole('button', { name: 'Enviar solicitud' })
    await user.click(button)
    await user.click(button)

    expect(await screen.findByText('Detalle del expediente (V-04)')).toBeInTheDocument()
    expect(attempts).toBe(1)
  })

  it('borrador local: persiste al escribir y se restaura al volver a montar la página', async () => {
    const user = userEvent.setup()
    const { unmount } = renderPage()

    await user.type(screen.getByLabelText(/^Identificador de carrera/), VALID_UUID)
    expect(getNuevaSolicitudDraft()).toBe(VALID_UUID)

    unmount()
    renderPage()

    expect(await screen.findByLabelText(/^Identificador de carrera/)).toHaveValue(VALID_UUID)
  })

  it('no presenta violaciones de accesibilidad', async () => {
    const { container } = renderPage()
    await screen.findByLabelText(/^Identificador de carrera/)

    expect(await axe(container)).toHaveNoViolations()
  })
})
