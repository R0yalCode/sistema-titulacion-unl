import { HttpResponse, http } from 'msw'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { AuthContext, type AuthContextValue, type AuthUser } from '@/auth/AuthContext'
import { fixtureExpedienteBorrador, fixtureExpedienteDetalle } from '@/mocks/fixtures'
import { formatFecha } from '@/lib/dates'
import { server } from '@/test/server'
import SeguimientoPeticionPage from './SeguimientoPeticionPage'

const DETALLE_URL = '*/api/v1/expedientes/:id/'
const DOCUMENTO_URL = '*/api/v1/peticiones/:id/documento/'

const EXPEDIENTE_BORRADOR = {
  ...fixtureExpedienteBorrador,
  facultad_id: fixtureExpedienteDetalle.facultad_id,
  fecha_recepcion: null,
  numero_providencia: null,
  fecha_limite_atencion: null,
  dias_laborables_acumulados: 0,
}
const PENDIENTE = EXPEDIENTE_BORRADOR.peticiones[0]!
const CARGADA = fixtureExpedienteDetalle.peticiones[1]!

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

function servirDetalle(detalle: object) {
  server.use(http.get(DETALLE_URL, () => HttpResponse.json(detalle)))
}

function renderAs(roles: string[], expedienteId: string, peticionId: string) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[`/expedientes/${expedienteId}/peticiones/${peticionId}`]}>
        <AuthContext.Provider value={authValue({ cedula: '1104567890', roles })}>
          <Routes>
            <Route element={<SeguimientoPeticionPage />} path="/expedientes/:id/peticiones/:peticionId" />
          </Routes>
        </AuthContext.Provider>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('SeguimientoPeticionPage (V-06)', () => {
  beforeEach(() => {
    URL.createObjectURL = vi.fn(() => 'blob:fixture-url')
    URL.revokeObjectURL = vi.fn()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('FE-T601/602: resuelve la petición desde el expediente y muestra solo datos reales, sin violaciones de axe', async () => {
    servirDetalle(EXPEDIENTE_BORRADOR)
    const { container } = renderAs(['ESTUDIANTE'], EXPEDIENTE_BORRADOR.id, PENDIENTE.id)

    expect(await screen.findByRole('heading', { level: 1, name: PENDIENTE.requisito_nombre })).toBeInTheDocument()
    expect(screen.getByText('Pendiente')).toBeInTheDocument()
    expect(screen.getByText(/todavía no se ha solicitado/)).toBeInTheDocument()
    expect(screen.getByText(`(${PENDIENTE.requisito_codigo})`)).toBeInTheDocument()
    expect(screen.getByText(PENDIENTE.dependencia_emisora)).toBeInTheDocument()
    expect(screen.getByText(new RegExp(EXPEDIENTE_BORRADOR.numero_expediente))).toBeInTheDocument()
    expect(
      screen.getByText(`${formatFecha(EXPEDIENTE_BORRADOR.fecha_creacion)} (creada junto con el expediente)`),
    ).toBeInTheDocument()
    expect(await axe(container)).toHaveNoViolations()
  })

  it('FE-T602: avisa de la falta de historial (BE-02) y no muestra hitos ni estados inventados', async () => {
    servirDetalle(EXPEDIENTE_BORRADOR)
    renderAs(['ESTUDIANTE'], EXPEDIENTE_BORRADOR.id, PENDIENTE.id)

    expect(await screen.findByText('Historial no disponible')).toBeInTheDocument()
    expect(screen.getByText(/dependencia BE-02/)).toBeInTheDocument()
    expect(screen.queryByText(/En revisión|En atención/i)).not.toBeInTheDocument()
    expect(screen.queryByRole('list', { name: /historial|línea de tiempo/i })).not.toBeInTheDocument()
  })

  it('FE-T601/604: una petición que no pertenece al expediente muestra "no encontrada" con salidas', async () => {
    servirDetalle(EXPEDIENTE_BORRADOR)
    renderAs(['ESTUDIANTE'], EXPEDIENTE_BORRADOR.id, '00000000-0000-0000-0000-000000000000')

    expect(await screen.findByText('Petición no encontrada')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Volver a las peticiones' })).toHaveAttribute(
      'href',
      `/expedientes/${EXPEDIENTE_BORRADOR.id}/peticiones`,
    )
    expect(screen.getByRole('link', { name: 'Volver al expediente' })).toHaveAttribute(
      'href',
      `/expedientes/${EXPEDIENTE_BORRADOR.id}`,
    )
  })

  it('FE-T603: descarga la versión vigente (sin número de versión) con autenticación', async () => {
    const user = userEvent.setup()
    servirDetalle(fixtureExpedienteDetalle)
    let rutaPedida = ''
    server.use(
      http.get(DOCUMENTO_URL, ({ request }) => {
        rutaPedida = new URL(request.url).pathname
        return new HttpResponse(new Blob(['%PDF-1.4'], { type: 'application/pdf' }), {
          headers: { 'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename="record.pdf"' },
        })
      }),
    )
    renderAs(['ESTUDIANTE'], fixtureExpedienteDetalle.id, CARGADA.id)

    await user.click(await screen.findByRole('button', { name: 'Descargar' }))

    await waitFor(() => expect(rutaPedida).toBe(`/api/v1/peticiones/${CARGADA.id}/documento/`))
    await waitFor(() => expect(URL.createObjectURL).toHaveBeenCalled())
  })

  it('FE-T603: no ofrece un selector de versiones que el backend no permite listar', async () => {
    servirDetalle(fixtureExpedienteDetalle)
    renderAs(['ESTUDIANTE'], fixtureExpedienteDetalle.id, CARGADA.id)

    expect(await screen.findByRole('button', { name: 'Descargar' })).toBeInTheDocument()
    expect(screen.queryByRole('combobox')).not.toBeInTheDocument()
    expect(screen.getByText(/no expone el listado de versiones \(BE-02\)/)).toBeInTheDocument()
  })

  it('FE-T603: un 404 de la descarga muestra el mensaje real', async () => {
    const user = userEvent.setup()
    servirDetalle(fixtureExpedienteDetalle)
    server.use(
      http.get(DOCUMENTO_URL, () =>
        HttpResponse.json({ detail: 'No hay documento vigente para esta petición.' }, { status: 404 }),
      ),
    )
    renderAs(['ESTUDIANTE'], fixtureExpedienteDetalle.id, CARGADA.id)

    await user.click(await screen.findByRole('button', { name: 'Descargar' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('No hay documento vigente para esta petición.')
  })

  it('sin documento cargado no ofrece descarga', async () => {
    servirDetalle(EXPEDIENTE_BORRADOR)
    renderAs(['ESTUDIANTE'], EXPEDIENTE_BORRADOR.id, PENDIENTE.id)

    expect(await screen.findByText('Todavía no hay un documento cargado para esta petición.')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Descargar' })).not.toBeInTheDocument()
  })

  it('un rol sin acceso a la descarga (DECANO) no ve el botón aunque haya documento', async () => {
    servirDetalle(fixtureExpedienteDetalle)
    renderAs(['DECANO'], fixtureExpedienteDetalle.id, CARGADA.id)

    expect(await screen.findByText('Su rol no tiene acceso a la descarga de este documento.')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Descargar' })).not.toBeInTheDocument()
  })

  it('FE-T604: un 404 del expediente muestra "expediente no encontrado"', async () => {
    server.use(http.get(DETALLE_URL, () => HttpResponse.json({ detail: 'No encontrado.' }, { status: 404 })))
    renderAs(['ESTUDIANTE'], EXPEDIENTE_BORRADOR.id, PENDIENTE.id)

    expect(await screen.findByText('Expediente no encontrado')).toBeInTheDocument()
  })

  it('FE-T604: un 403 real muestra el estado de acceso restringido', async () => {
    server.use(
      http.get(DETALLE_URL, () =>
        HttpResponse.json({ detail: 'No tiene permiso para realizar esta acción.' }, { status: 403 }),
      ),
    )
    renderAs(['ESTUDIANTE'], EXPEDIENTE_BORRADOR.id, PENDIENTE.id)

    expect(await screen.findByRole('heading', { name: /acceso|permiso/i })).toBeInTheDocument()
  })

  it.each([
    ['un 500', () => HttpResponse.json({ detail: 'Error interno.' }, { status: 500 })],
    ['un error de red', () => HttpResponse.error()],
  ])('FE-T604: ante %s ofrece reintentar y vuelve a consultar', async (_caso, fallo) => {
    const user = userEvent.setup()
    let llamadas = 0
    server.use(
      http.get(DETALLE_URL, () => {
        llamadas += 1
        return llamadas === 1 ? fallo() : HttpResponse.json(EXPEDIENTE_BORRADOR)
      }),
    )
    renderAs(['ESTUDIANTE'], EXPEDIENTE_BORRADOR.id, PENDIENTE.id)

    await user.click(await screen.findByRole('button', { name: /reintentar/i }))

    expect(await screen.findByRole('heading', { level: 1, name: PENDIENTE.requisito_nombre })).toBeInTheDocument()
    expect(llamadas).toBe(2)
  })
})
