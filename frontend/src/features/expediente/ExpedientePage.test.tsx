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
import { fixtureChecklist, fixtureExpedienteBorrador, fixtureExpedienteDetalle } from '@/mocks/fixtures'
import { server } from '@/test/server'
import ExpedientePage from './ExpedientePage'

const DETALLE_URL = '*/api/v1/expedientes/:id/'
const ENVIAR_URL = '*/api/v1/expedientes/:id/enviar/'
const OBSERVAR_URL = '*/api/v1/expedientes/:id/observar/'
const CHECKLIST_LIST_URL = '*/api/v1/expedientes/:id/checklist/'
const CHECKLIST_UPDATE_URL = '*/api/v1/checklist/:id/'
const CHECKLIST_SUBSANAR_URL = '*/api/v1/checklist/:id/subsanar/'
const DOCUMENTO_URL = '*/api/v1/peticiones/:id/documento/'

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

function renderPageAs(roles: string[], route = `/expedientes/${fixtureExpedienteDetalle.id}`) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[route]}>
        <AuthContext.Provider value={authValue({ cedula: '1104567890', roles })}>
          <ToastProvider>
            <Routes>
              <Route element={<ExpedientePage />} path="/expedientes/:id" />
            </Routes>
          </ToastProvider>
        </AuthContext.Provider>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

/** El checklist comparte nombres de requisito con la tabla de peticiones y
 * `Table` renderiza una versión de escritorio y otra móvil a la vez; por eso
 * se busca el primer ítem real dentro de la sección "Checklist de verificación". */
async function findChecklistSection(): Promise<HTMLElement> {
  const heading = await screen.findByText('Checklist de verificación')
  return heading.closest('section') as HTMLElement
}

describe('ExpedientePage (V-04)', () => {
  beforeEach(() => {
    URL.createObjectURL = vi.fn(() => 'blob:fixture-url')
    URL.revokeObjectURL = vi.fn()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('CA-V04-01: carga el detalle real y muestra cabecera, timeline y peticiones', async () => {
    renderPageAs(['ESTUDIANTE'])

    expect(await screen.findByText(fixtureExpedienteDetalle.numero_expediente)).toBeInTheDocument()
    expect(screen.getByText('EN_VERIFICACION')).toBeInTheDocument()
    expect(screen.getAllByText(fixtureExpedienteDetalle.peticiones[0]!.requisito_nombre).length).toBeGreaterThan(0)
  })

  it('muestra "no encontrado" ante un 404 real', async () => {
    server.use(http.get(DETALLE_URL, () => HttpResponse.json({ detail: 'No encontrado.' }, { status: 404 })))
    renderPageAs(['ESTUDIANTE'])

    expect(await screen.findByText('Expediente no encontrado')).toBeInTheDocument()
  })

  it('muestra ForbiddenState ante un 403 real en el detalle', async () => {
    server.use(http.get(DETALLE_URL, () => HttpResponse.json({ detail: 'Prohibido.' }, { status: 403 })))
    renderPageAs(['SECRETARIO_ABOGADO'])

    expect(await screen.findByText('Acceso restringido')).toBeInTheDocument()
  })

  it('CA-V04-06: el checklist para ESTUDIANTE no ejecuta la query (sin 403 real) y muestra el panel informativo', async () => {
    let checklistRequested = false
    server.use(
      http.get(CHECKLIST_LIST_URL, () => {
        checklistRequested = true
        return HttpResponse.json(fixtureChecklist)
      }),
    )
    renderPageAs(['ESTUDIANTE'])

    expect(await screen.findByText('No disponible para su rol')).toBeInTheDocument()
    expect(checklistRequested).toBe(false)
  })

  it('un rol autorizado ve el checklist real', async () => {
    renderPageAs(['SECRETARIO_ABOGADO'])

    const section = await findChecklistSection()
    expect(within(section).getByText(fixtureChecklist[0]!.requisito_nombre)).toBeInTheDocument()
    expect(within(section).getAllByText('PENDIENTE').length).toBeGreaterThan(0)
  })

  it('CA-V04-02: el estudiante propietario puede enviar desde BORRADOR', async () => {
    let enviado = false
    server.use(
      http.get(DETALLE_URL, () =>
        HttpResponse.json(enviado ? fixtureExpedienteDetalle : fixtureExpedienteBorrador),
      ),
      http.post(ENVIAR_URL, () => {
        enviado = true
        return HttpResponse.json(fixtureExpedienteDetalle)
      }),
    )
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    const user = userEvent.setup()
    renderPageAs(['ESTUDIANTE'], `/expedientes/${fixtureExpedienteBorrador.id}`)

    const enviarButton = await screen.findByRole('button', { name: 'Enviar expediente' })
    await user.click(enviarButton)

    await waitFor(() => expect(screen.getByText('EN_VERIFICACION')).toBeInTheDocument())
  })

  it('CA-V04-03: un envío con requisitos incompletos (422) muestra el mensaje real sin enviar', async () => {
    server.use(http.get(DETALLE_URL, () => HttpResponse.json(fixtureExpedienteBorrador)))
    server.use(
      http.post(ENVIAR_URL, () =>
        HttpResponse.json({ detail: 'Envio incompleto: requisitos sin documento en firme.' }, { status: 422 }),
      ),
    )
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    const user = userEvent.setup()
    renderPageAs(['ESTUDIANTE'], `/expedientes/${fixtureExpedienteBorrador.id}`)

    await user.click(await screen.findByRole('button', { name: 'Enviar expediente' }))

    expect(await screen.findByText('Envio incompleto: requisitos sin documento en firme.')).toBeInTheDocument()
  })

  it('CA-V04-04: SECRETARIO_ABOGADO observa con motivo y el expediente refleja el cambio', async () => {
    const user = userEvent.setup()
    renderPageAs(['SECRETARIO_ABOGADO'])

    await user.click((await screen.findAllByRole('button', { name: 'Observar' }))[0]!)
    await user.type(screen.getByLabelText(/^Motivo de la observación/), 'Falta firma del director.')
    await user.click(screen.getByRole('button', { name: 'Confirmar observación' }))

    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
  })

  it('no observa sin motivo (validación local) en el diálogo del expediente', async () => {
    const user = userEvent.setup()
    renderPageAs(['SECRETARIO_ABOGADO'])

    await user.click((await screen.findAllByRole('button', { name: 'Observar' }))[0]!)
    await user.click(screen.getByRole('button', { name: 'Confirmar observación' }))

    expect(screen.getByText('Ingrese el motivo de la observación.')).toBeInTheDocument()
  })

  it('CA-V04-05: evaluar un ítem del checklist como OBSERVADO sin motivo bloquea el envío localmente', async () => {
    const user = userEvent.setup()
    renderPageAs(['SECRETARIO_ABOGADO'])

    const section = await findChecklistSection()
    await user.click(within(section).getAllByRole('button', { name: 'Observar' })[0]!)
    await user.click(within(section).getByRole('button', { name: 'Confirmar observación' }))

    expect(within(section).getByText('Ingrese el motivo de la observación.')).toBeInTheDocument()
  })

  it('evalúa un ítem del checklist como VERIFICADO', async () => {
    let checklistState: ChecklistItem[] = fixtureChecklist.map((item) => ({ ...item }))
    server.use(
      http.get(CHECKLIST_LIST_URL, () => HttpResponse.json(checklistState)),
      http.put(CHECKLIST_UPDATE_URL, async ({ request, params }) => {
        const body = (await request.json()) as { estado_verificacion: ChecklistItem['estado_verificacion'] }
        checklistState = checklistState.map((item) =>
          item.id === params.id ? { ...item, estado_verificacion: body.estado_verificacion } : item,
        )
        return HttpResponse.json(checklistState.find((item) => item.id === params.id))
      }),
    )
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    const user = userEvent.setup()
    renderPageAs(['SECRETARIO_ABOGADO'])

    const section = await findChecklistSection()
    await user.click(within(section).getAllByRole('button', { name: 'Verificar' })[0]!)

    await waitFor(() => expect(within(section).getAllByText('VERIFICADO').length).toBeGreaterThan(0))
  })

  it('CA-V04-07: un PDF inválido en subsanación no llama a la API', async () => {
    let subsanarRequested = false
    server.use(
      http.get(DETALLE_URL, () => HttpResponse.json({ ...fixtureExpedienteDetalle, estado: 'OBSERVADA' })),
      http.get(CHECKLIST_LIST_URL, () =>
        HttpResponse.json([{ ...fixtureChecklist[0]!, estado_verificacion: 'OBSERVADO' }, ...fixtureChecklist.slice(1)]),
      ),
      http.post(CHECKLIST_SUBSANAR_URL, () => {
        subsanarRequested = true
        return HttpResponse.json({}, { status: 201 })
      }),
    )
    const user = userEvent.setup()
    renderPageAs(['ADMINISTRADOR'])

    await findChecklistSection()
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement
    const archivoInvalido = new File(['no es un pdf'], 'nota.txt', { type: 'text/plain' })
    await user.upload(fileInput, archivoInvalido)

    expect(subsanarRequested).toBe(false)
  })

  it('descarga un documento real (Blob + Content-Disposition)', async () => {
    const user = userEvent.setup()
    renderPageAs(['ESTUDIANTE'])

    await screen.findAllByText(fixtureExpedienteDetalle.peticiones[0]!.requisito_nombre)
    const descargarButtons = screen.getAllByRole('button', { name: 'Descargar' })
    await user.click(descargarButtons[0]!)

    await waitFor(() => expect(URL.createObjectURL).toHaveBeenCalled())
  })

  it('muestra un error real si la descarga no está disponible (404)', async () => {
    server.use(http.get(DOCUMENTO_URL, () => HttpResponse.json({ detail: 'No hay documento vigente.' }, { status: 404 })))
    const user = userEvent.setup()
    renderPageAs(['ESTUDIANTE'])

    await screen.findAllByText(fixtureExpedienteDetalle.peticiones[0]!.requisito_nombre)
    await user.click(screen.getAllByRole('button', { name: 'Descargar' })[0]!)

    expect(await screen.findByText('No hay documento vigente.')).toBeInTheDocument()
  })

  it('discrepancia real (INC-21): un 500 de regla de negocio en observar muestra el mensaje real del backend', async () => {
    server.use(
      http.post(OBSERVAR_URL, () =>
        HttpResponse.json(
          { detail: 'El expediente debe estar en EN_VERIFICACION. Estado actual: OBSERVADA' },
          { status: 500 },
        ),
      ),
    )
    const user = userEvent.setup()
    renderPageAs(['SECRETARIO_ABOGADO'])

    await user.click((await screen.findAllByRole('button', { name: 'Observar' }))[0]!)
    await user.type(screen.getByLabelText(/^Motivo de la observación/), 'Motivo de prueba.')
    await user.click(screen.getByRole('button', { name: 'Confirmar observación' }))

    expect(
      await screen.findByText('El expediente debe estar en EN_VERIFICACION. Estado actual: OBSERVADA'),
    ).toBeInTheDocument()
  })

  it('no presenta violaciones de accesibilidad', async () => {
    const { container } = renderPageAs(['SECRETARIO_ABOGADO'])
    await findChecklistSection()

    expect(await axe(container)).toHaveNoViolations()
  })
})
