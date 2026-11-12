import { HttpResponse, http } from 'msw'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { AuthContext, type AuthContextValue, type AuthUser } from '@/auth/AuthContext'
import type { ChecklistItem } from '@/api/endpoints/checklist'
import { ToastProvider } from '@/components/feedback/ToastProvider'
import { fixtureChecklist, fixtureExpedienteDetalle } from '@/mocks/fixtures'
import { server } from '@/test/server'
import DetalleFuncionarioPage from './DetalleFuncionarioPage'
import { BANDEJA_OPERATIVA_QUERY_KEY } from './queries'

const DETALLE_URL = '*/api/v1/expedientes/:id/'
const CHECKLIST_URL = '*/api/v1/expedientes/:id/checklist/'
const CHECKLIST_UPDATE_URL = '*/api/v1/checklist/:id/'
const INICIAR_URL = '*/api/v1/expedientes/:id/iniciar-verificacion/'
const OBSERVAR_URL = '*/api/v1/expedientes/:id/observar/'
const DOCUMENTO_URL = '*/api/v1/peticiones/:id/documento/'

const ID = fixtureExpedienteDetalle.id

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

/** Sirve el detalle con el estado indicado y cuenta las lecturas (invalidación). */
function servirDetalle(estado: string) {
  const lecturas = { total: 0, estado }
  server.use(
    http.get(DETALLE_URL, () => {
      lecturas.total += 1
      return HttpResponse.json({ ...fixtureExpedienteDetalle, estado: lecturas.estado })
    }),
  )
  return lecturas
}

function renderAs(roles: string[]) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  const utils = render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[`/bandeja/${ID}`]}>
        <AuthContext.Provider value={authValue({ cedula: '1104567890', roles })}>
          <ToastProvider>
            <Routes>
              <Route element={<DetalleFuncionarioPage />} path="/bandeja/:id" />
              <Route element={<p>Bandeja</p>} path="/bandeja" />
            </Routes>
          </ToastProvider>
        </AuthContext.Provider>
      </MemoryRouter>
    </QueryClientProvider>,
  )
  return { ...utils, queryClient }
}

async function seccion(titulo: string): Promise<HTMLElement> {
  return (await screen.findByRole('heading', { name: titulo })).closest('section') as HTMLElement
}

describe('DetalleFuncionarioPage (V-08a)', () => {
  beforeEach(() => {
    URL.createObjectURL = vi.fn(() => 'blob:fixture-url')
    URL.revokeObjectURL = vi.fn()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('FE-T801: carga el detalle real con cabecera, peticiones y checklist, sin violaciones de axe', async () => {
    servirDetalle('EN_VERIFICACION')
    const { container } = renderAs(['SECRETARIO_ABOGADO'])

    expect(await screen.findByText(fixtureExpedienteDetalle.numero_expediente)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Volver a la bandeja' })).toHaveAttribute('href', '/bandeja')
    const checklist = await seccion('Checklist de verificación')
    expect((await within(checklist).findAllByRole('button', { name: 'Verificar' })).length).toBeGreaterThan(0)
    expect(await axe(container)).toHaveNoViolations()
  })

  it('E2-01: el secretario inicia la verificación de un expediente ENVIADA y se refrescan detalle y bandeja', async () => {
    const user = userEvent.setup()
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    const lecturas = servirDetalle('ENVIADA')
    let iniciado = ''
    server.use(
      http.post(INICIAR_URL, ({ params }) => {
        iniciado = String(params.id)
        lecturas.estado = 'EN_VERIFICACION'
        return HttpResponse.json({ ...fixtureExpedienteDetalle, estado: 'EN_VERIFICACION' })
      }),
    )
    const { queryClient } = renderAs(['SECRETARIO_ABOGADO'])
    queryClient.setQueryData([BANDEJA_OPERATIVA_QUERY_KEY, 1, 10], { count: 0, next: null, previous: null, results: [] })

    await user.click(await screen.findByRole('button', { name: 'Iniciar verificación' }))

    await waitFor(() => expect(iniciado).toBe(ID))
    expect(await screen.findByText('Verificación iniciada.')).toBeInTheDocument()
    await waitFor(() => expect(lecturas.total).toBeGreaterThanOrEqual(2))
    expect(queryClient.getQueryState([BANDEJA_OPERATIVA_QUERY_KEY, 1, 10])?.isInvalidated).toBe(true)
  })

  it('E2-01: un error de transición muestra el mensaje real del backend', async () => {
    const user = userEvent.setup()
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    servirDetalle('ENVIADA')
    server.use(
      http.post(INICIAR_URL, () =>
        HttpResponse.json(
          { detail: 'Transición de estado no permitida.', code: 'transicion_invalida' },
          { status: 400 },
        ),
      ),
    )
    renderAs(['SECRETARIO_ABOGADO'])

    await user.click(await screen.findByRole('button', { name: 'Iniciar verificación' }))

    expect(await screen.findByText('Transición de estado no permitida.')).toBeInTheDocument()
  })

  it('FE-T803: el secretario observa el expediente EN_VERIFICACION desde V-08', async () => {
    const user = userEvent.setup()
    const lecturas = servirDetalle('EN_VERIFICACION')
    let motivo = ''
    server.use(
      http.post(OBSERVAR_URL, async ({ request }) => {
        motivo = ((await request.json()) as { motivo_observacion: string }).motivo_observacion
        lecturas.estado = 'OBSERVADA'
        return HttpResponse.json({ id: 'obs-1' }, { status: 201 })
      }),
    )
    const { queryClient } = renderAs(['SECRETARIO_ABOGADO'])
    queryClient.setQueryData([BANDEJA_OPERATIVA_QUERY_KEY, 1, 10], { count: 0, next: null, previous: null, results: [] })

    await user.click((await screen.findAllByRole('button', { name: 'Observar' }))[0]!)
    const dialogo = await screen.findByRole('dialog', { name: 'Registrar observación' })
    await user.type(within(dialogo).getByLabelText(/Motivo de la observación/), 'Falta la firma del director.')
    await user.click(within(dialogo).getByRole('button', { name: 'Confirmar observación' }))

    await waitFor(() => expect(motivo).toBe('Falta la firma del director.'))
    expect(await screen.findByText('Observación registrada.')).toBeInTheDocument()
    await waitFor(() => expect(lecturas.total).toBeGreaterThanOrEqual(2))
    expect(queryClient.getQueryState([BANDEJA_OPERATIVA_QUERY_KEY, 1, 10])?.isInvalidated).toBe(true)
  })

  it('FE-T802: el funcionario evalúa un ítem del checklist desde V-08', async () => {
    const user = userEvent.setup()
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    servirDetalle('EN_VERIFICACION')
    let evaluado = ''
    let items: ChecklistItem[] = fixtureChecklist.map((item) => ({ ...item }))
    server.use(
      http.get(CHECKLIST_URL, () => HttpResponse.json(items)),
      http.put(CHECKLIST_UPDATE_URL, ({ params }) => {
        evaluado = String(params.id)
        items = items.map((item) => (item.id === params.id ? { ...item, estado_verificacion: 'VERIFICADO' } : item))
        return HttpResponse.json(items.find((item) => item.id === params.id))
      }),
    )
    renderAs(['ANALISTA_APOYO'])

    const checklist = await seccion('Checklist de verificación')
    await user.click((await within(checklist).findAllByRole('button', { name: 'Verificar' }))[0]!)

    await waitFor(() => expect(evaluado).toBe(fixtureChecklist[0]!.id))
  })

  it('FE-T807: la analista no ve acciones de estado y se le explica por qué', async () => {
    servirDetalle('EN_VERIFICACION')
    renderAs(['ANALISTA_APOYO'])

    expect(await screen.findByText(/No hay acciones de estado disponibles para su rol/)).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Iniciar verificación' })).not.toBeInTheDocument()
  })

  it('FE-T807: el decano no consulta el checklist (403 por RBAC) ni ve descargas', async () => {
    servirDetalle('INFORME_EMITIDO')
    let checklistPedido = false
    server.use(
      http.get(CHECKLIST_URL, () => {
        checklistPedido = true
        return HttpResponse.json([])
      }),
    )
    renderAs(['DECANO'])

    await screen.findByText(fixtureExpedienteDetalle.numero_expediente)
    expect(checklistPedido).toBe(false)
    expect(screen.queryByRole('button', { name: 'Descargar' })).not.toBeInTheDocument()
  })

  it('FE-T806: descarga el documento de una petición desde V-08', async () => {
    const user = userEvent.setup()
    servirDetalle('EN_VERIFICACION')
    let descargado = ''
    server.use(
      http.get(DOCUMENTO_URL, ({ params }) => {
        descargado = String(params.id)
        return new HttpResponse(new Blob(['%PDF-1.4'], { type: 'application/pdf' }), {
          headers: { 'Content-Type': 'application/pdf' },
        })
      }),
    )
    renderAs(['SECRETARIO_ABOGADO'])

    const peticiones = await seccion('Peticiones documentales')
    await user.click(within(peticiones).getAllByRole('button', { name: 'Descargar' })[0]!)

    await waitFor(() => expect(descargado).toBe(fixtureExpedienteDetalle.peticiones[0]!.id))
  })

  it('FE-T808: en DECLARADA_APTA es solo de lectura', async () => {
    servirDetalle('DECLARADA_APTA')
    renderAs(['SECRETARIO_ABOGADO'])

    expect(await screen.findByText('Expediente en estado final')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Iniciar verificación' })).not.toBeInTheDocument()
    expect(screen.queryByText(/No hay acciones de estado disponibles/)).not.toBeInTheDocument()
    const checklist = await seccion('Checklist de verificación')
    expect(within(checklist).queryByRole('button', { name: 'Verificar' })).not.toBeInTheDocument()
  })

  it('un 404 muestra "no encontrado" con salida a la bandeja', async () => {
    server.use(http.get(DETALLE_URL, () => HttpResponse.json({ detail: 'No encontrado.' }, { status: 404 })))
    renderAs(['SECRETARIO_ABOGADO'])

    expect(await screen.findByText('Expediente no encontrado')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Volver a la bandeja' })).toBeInTheDocument()
  })

  it('un 403 muestra acceso restringido con enlace a V-09', async () => {
    server.use(
      http.get(DETALLE_URL, () =>
        HttpResponse.json({ detail: 'No tiene permiso para realizar esta acción.' }, { status: 403 }),
      ),
    )
    renderAs(['DIRECTOR_CARRERA'])

    expect(await screen.findByRole('link', { name: 'Más información' })).toHaveAttribute(
      'href',
      '/no-habilitado?motivo=rol-no-autorizado',
    )
  })

  it('un 500 ofrece reintentar y vuelve a consultar', async () => {
    const user = userEvent.setup()
    let llamadas = 0
    server.use(
      http.get(DETALLE_URL, () => {
        llamadas += 1
        return llamadas === 1
          ? HttpResponse.json({ detail: 'Error interno.' }, { status: 500 })
          : HttpResponse.json(fixtureExpedienteDetalle)
      }),
    )
    renderAs(['SECRETARIO_ABOGADO'])

    await user.click(await screen.findByRole('button', { name: /reintentar/i }))

    expect(await screen.findByText(fixtureExpedienteDetalle.numero_expediente)).toBeInTheDocument()
    expect(llamadas).toBe(2)
  })
})
