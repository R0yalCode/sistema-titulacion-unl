import { HttpResponse, http } from 'msw'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { AuthContext, type AuthContextValue, type AuthUser } from '@/auth/AuthContext'
import type { ChecklistItem } from '@/api/endpoints/checklist'
import { ToastProvider } from '@/components/feedback/ToastProvider'
import { fixtureChecklist, fixtureExpedienteDetalle } from '@/mocks/fixtures'
import { server } from '@/test/server'
import { checklistCompleto, puedeDeclararAptitud, puedeEmitirInforme } from './accionesResolucion'
import DetalleFuncionarioPage from './DetalleFuncionarioPage'
import { BANDEJA_OPERATIVA_QUERY_KEY } from './queries'

const DETALLE_URL = '*/api/v1/expedientes/:id/'
const CHECKLIST_URL = '*/api/v1/expedientes/:id/checklist/'
const INFORMES_URL = '*/api/v1/informes/'
const DECLARATORIAS_URL = '*/api/v1/declaratorias/'
const ID = fixtureExpedienteDetalle.id
const VERIFICADO = fixtureChecklist.map((item) => ({ ...item, estado_verificacion: 'VERIFICADO' as const }))

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

function servir(estado: string, checklist: ChecklistItem[] = VERIFICADO) {
  const lecturas = { total: 0, estado }
  server.use(
    http.get(DETALLE_URL, () => {
      lecturas.total += 1
      return HttpResponse.json({ ...fixtureExpedienteDetalle, estado: lecturas.estado })
    }),
    http.get(CHECKLIST_URL, () => HttpResponse.json(checklist)),
  )
  return lecturas
}

function renderAs(roles: string[]) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  queryClient.setQueryData([BANDEJA_OPERATIVA_QUERY_KEY, 1, 10], { count: 0, next: null, previous: null, results: [] })
  const utils = render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[`/bandeja/${ID}`]}>
        <AuthContext.Provider value={authValue({ cedula: '1104567890', roles })}>
          <ToastProvider>
            <Routes>
              <Route element={<DetalleFuncionarioPage />} path="/bandeja/:id" />
            </Routes>
          </ToastProvider>
        </AuthContext.Provider>
      </MemoryRouter>
    </QueryClientProvider>,
  )
  return { ...utils, queryClient }
}

function makePdf(name: string): File {
  const bytes = new Uint8Array(64)
  ;[0x25, 0x50, 0x44, 0x46, 0x2d].forEach((byte, index) => {
    bytes[index] = byte
  })
  return new File([bytes], name, { type: 'application/pdf' })
}

describe('accionesResolucion (V-08b)', () => {
  it('informe: solo SECRETARIO_ABOGADO en EN_VERIFICACION (el servicio rechaza a la analista)', () => {
    expect(puedeEmitirInforme(['SECRETARIO_ABOGADO'], 'EN_VERIFICACION')).toBe(true)
    expect(puedeEmitirInforme(['SECRETARIO_ABOGADO'], 'OBSERVADA')).toBe(false)
    expect(puedeEmitirInforme(['ANALISTA_APOYO'], 'EN_VERIFICACION')).toBe(false)
  })

  it('declaratoria: solo DECANO en INFORME_EMITIDO', () => {
    expect(puedeDeclararAptitud(['DECANO'], 'INFORME_EMITIDO')).toBe(true)
    expect(puedeDeclararAptitud(['DECANO'], 'EN_VERIFICACION')).toBe(false)
    expect(puedeDeclararAptitud(['ANALISTA_APOYO'], 'INFORME_EMITIDO')).toBe(false)
  })

  it('checklist completo solo con todos los ítems VERIFICADO', () => {
    expect(checklistCompleto(VERIFICADO)).toBe(true)
    expect(checklistCompleto(fixtureChecklist)).toBe(false)
    expect(checklistCompleto([])).toBe(false)
    expect(checklistCompleto(undefined)).toBe(false)
  })
})

describe('ResolucionesSection en V-08 (V-08b)', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('FE-T804: con el checklist incompleto el informe está deshabilitado y se explica por qué', async () => {
    servir('EN_VERIFICACION', fixtureChecklist)
    renderAs(['SECRETARIO_ABOGADO'])

    const boton = await screen.findByRole('button', { name: 'Emitir informe de aptitud' })
    await waitFor(() => expect(boton).toBeDisabled())
    expect(screen.getByText(/todos los requisitos del checklist estén verificados/)).toBeInTheDocument()
  })

  it('FE-T804: emite el informe APTO con el cuerpo real, muestra el resultado y refresca detalle y bandeja', async () => {
    const user = userEvent.setup()
    const lecturas = servir('EN_VERIFICACION')
    let cuerpo: Record<string, unknown> = {}
    server.use(
      http.post(INFORMES_URL, async ({ request }) => {
        cuerpo = (await request.json()) as Record<string, unknown>
        lecturas.estado = 'INFORME_EMITIDO'
        return HttpResponse.json(
          { id: 'inf-1', numero_providencia: 'PROV-590-2026-001', dictamen: 'APTO', fecha_emision: '2026-11-12T10:00:00Z' },
          { status: 201 },
        )
      }),
    )
    const { container, queryClient } = renderAs(['SECRETARIO_ABOGADO'])

    const boton = await screen.findByRole('button', { name: 'Emitir informe de aptitud' })
    await waitFor(() => expect(boton).toBeEnabled())
    await user.click(boton)
    const dialogo = await screen.findByRole('dialog', { name: 'Emitir informe de aptitud' })
    expect(within(dialogo).queryByText(/NO APTO/)).not.toBeInTheDocument()
    expect(await axe(container)).toHaveNoViolations()
    await user.type(within(dialogo).getByLabelText('Fundamentación (opcional)'), 'Cumple el Art. 235.')
    await user.click(within(dialogo).getByRole('button', { name: 'Confirmar informe' }))

    await waitFor(() =>
      expect(cuerpo).toEqual({ expediente_id: ID, dictamen: 'APTO', fundamentacion: 'Cumple el Art. 235.' }),
    )
    expect(await screen.findByText(/Providencia PROV-590-2026-001/)).toBeInTheDocument()
    expect(screen.getByText(/no permite consultar ni descargar después/)).toBeInTheDocument()
    await waitFor(() => expect(lecturas.total).toBeGreaterThanOrEqual(2))
    expect(queryClient.getQueryState([BANDEJA_OPERATIVA_QUERY_KEY, 1, 10])?.isInvalidated).toBe(true)
  })

  it('FE-T804: un 400 de checklist incompleto muestra el mensaje real', async () => {
    const user = userEvent.setup()
    servir('EN_VERIFICACION')
    server.use(
      http.post(INFORMES_URL, () =>
        HttpResponse.json(
          { detail: 'El checklist no está completo.', requisitos_pendientes: ['Idioma B1'] },
          { status: 400 },
        ),
      ),
    )
    renderAs(['SECRETARIO_ABOGADO'])

    const boton = await screen.findByRole('button', { name: 'Emitir informe de aptitud' })
    await waitFor(() => expect(boton).toBeEnabled())
    await user.click(boton)
    const dialogo = await screen.findByRole('dialog', { name: 'Emitir informe de aptitud' })
    await user.click(within(dialogo).getByRole('button', { name: 'Confirmar informe' }))

    expect(await within(dialogo).findByText('El checklist no está completo.')).toBeInTheDocument()
  })

  it('la analista no recibe el botón de informe que el servicio rechazaría', async () => {
    servir('EN_VERIFICACION')
    renderAs(['ANALISTA_APOYO'])

    await screen.findByText(fixtureExpedienteDetalle.numero_expediente)
    expect(screen.queryByRole('button', { name: 'Emitir informe de aptitud' })).not.toBeInTheDocument()
  })

  it('FE-T805: el decano registra la declaratoria por multipart y el expediente se refresca', async () => {
    const user = userEvent.setup()
    const lecturas = servir('INFORME_EMITIDO')
    let tipo = ''
    server.use(
      http.post(DECLARATORIAS_URL, ({ request }) => {
        tipo = request.headers.get('content-type') ?? ''
        lecturas.estado = 'DECLARADA_APTA'
        return HttpResponse.json(
          { id: 'dec-1', numero_memorando: 'MEM-162-2026-007', fecha_declaratoria: '2026-11-12T10:00:00Z' },
          { status: 201 },
        )
      }),
    )
    const append = vi.spyOn(FormData.prototype, 'append')
    renderAs(['DECANO'])

    await user.click(await screen.findByRole('button', { name: 'Registrar declaratoria de aptitud' }))
    const dialogo = await screen.findByRole('dialog', { name: 'Registrar declaratoria de aptitud' })
    const confirmar = within(dialogo).getByRole('button', { name: 'Confirmar declaratoria' })
    expect(confirmar).toBeDisabled()
    const archivo = makePdf('memorando.pdf')
    await user.upload(dialogo.querySelector('input[type="file"]') as HTMLInputElement, archivo)
    await user.type(within(dialogo).getByLabelText('Número de memorando'), 'MEM-162-2026-007')
    await waitFor(() => expect(confirmar).toBeEnabled())
    await user.click(confirmar)

    await waitFor(() => expect(tipo).toMatch(/^multipart\/form-data/))
    expect(append).toHaveBeenCalledWith('expediente_id', ID)
    expect(append).toHaveBeenCalledWith('archivo_memorando', archivo)
    expect(append).toHaveBeenCalledWith('numero_memorando', 'MEM-162-2026-007')
    expect(await screen.findByText(/Memorando MEM-162-2026-007/)).toBeInTheDocument()
    await waitFor(() => expect(lecturas.total).toBeGreaterThanOrEqual(2))
  })

  it('FE-T805: sin número de memorando no se envía el campo (lo genera el backend) y un 400 muestra su mensaje', async () => {
    const user = userEvent.setup()
    servir('INFORME_EMITIDO')
    server.use(
      http.post(DECLARATORIAS_URL, () =>
        HttpResponse.json({ detail: 'El PDF no está firmado.', code: 'pdf_invalido' }, { status: 400 }),
      ),
    )
    const append = vi.spyOn(FormData.prototype, 'append')
    renderAs(['DECANO'])

    await user.click(await screen.findByRole('button', { name: 'Registrar declaratoria de aptitud' }))
    const dialogo = await screen.findByRole('dialog', { name: 'Registrar declaratoria de aptitud' })
    await user.upload(dialogo.querySelector('input[type="file"]') as HTMLInputElement, makePdf('memorando.pdf'))
    const confirmar = within(dialogo).getByRole('button', { name: 'Confirmar declaratoria' })
    await waitFor(() => expect(confirmar).toBeEnabled())
    await user.click(confirmar)

    expect(await within(dialogo).findByText('El PDF no está firmado.')).toBeInTheDocument()
    expect(append.mock.calls.some(([campo]) => campo === 'numero_memorando')).toBe(false)
  })

  it('FE-T805: un archivo que no es PDF no habilita el envío', async () => {
    const user = userEvent.setup()
    servir('INFORME_EMITIDO')
    let llamadas = 0
    server.use(
      http.post(DECLARATORIAS_URL, () => {
        llamadas += 1
        return HttpResponse.json({}, { status: 201 })
      }),
    )
    renderAs(['DECANO'])

    await user.click(await screen.findByRole('button', { name: 'Registrar declaratoria de aptitud' }))
    const dialogo = await screen.findByRole('dialog', { name: 'Registrar declaratoria de aptitud' })
    await user.upload(
      dialogo.querySelector('input[type="file"]') as HTMLInputElement,
      new File(['texto'], 'memorando.pdf', { type: 'application/pdf' }),
    )

    expect(await within(dialogo).findByText('El archivo no parece ser un PDF válido.')).toBeInTheDocument()
    expect(within(dialogo).getByRole('button', { name: 'Confirmar declaratoria' })).toBeDisabled()
    expect(llamadas).toBe(0)
  })

  it('no ofrece resoluciones fuera de su rol y estado ni en estados finales', async () => {
    servir('INFORME_EMITIDO')
    const { unmount } = renderAs(['SECRETARIO_ABOGADO'])
    await screen.findByText(fixtureExpedienteDetalle.numero_expediente)
    expect(screen.queryByRole('heading', { name: 'Resoluciones' })).not.toBeInTheDocument()
    unmount()

    servir('DECLARADA_APTA')
    renderAs(['DECANO'])
    await screen.findByText('Expediente en estado final')
    expect(screen.queryByRole('button', { name: 'Registrar declaratoria de aptitud' })).not.toBeInTheDocument()
  })
})
