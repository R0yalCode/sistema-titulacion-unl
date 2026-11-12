import { HttpResponse, http } from 'msw'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import { AuthContext, type AuthContextValue, type AuthUser } from '@/auth/AuthContext'
import { ToastProvider } from '@/components/feedback/ToastProvider'
import { fixtureExpedienteBorrador, fixtureExpedienteDetalle } from '@/mocks/fixtures'
import { server } from '@/test/server'
import PeticionesPage from './PeticionesPage'

const DETALLE_URL = '*/api/v1/expedientes/:id/'
const SOLICITAR_URL = '*/api/v1/peticiones/:id/solicitar-emision/'
const DOCUMENTO_URL = '*/api/v1/peticiones/:id/documento/'

const EXPEDIENTE_BORRADOR = {
  ...fixtureExpedienteBorrador,
  facultad_id: fixtureExpedienteDetalle.facultad_id,
  fecha_recepcion: null,
  numero_providencia: null,
  fecha_limite_atencion: null,
  dias_laborables_acumulados: 0,
}
const PRIMERA = EXPEDIENTE_BORRADOR.peticiones[0]!

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

/** Sirve el detalle indicado y cuenta las lecturas, para comprobar la invalidación. */
function servirDetalle(detalle: object) {
  const lecturas = { total: 0 }
  server.use(
    http.get(DETALLE_URL, () => {
      lecturas.total += 1
      return HttpResponse.json(detalle)
    }),
  )
  return lecturas
}

function renderAs(roles: string[], expedienteId: string = EXPEDIENTE_BORRADOR.id) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[`/expedientes/${expedienteId}/peticiones`]}>
        <AuthContext.Provider value={authValue({ cedula: '1104567890', roles })}>
          <ToastProvider>
            <Routes>
              <Route element={<PeticionesPage />} path="/expedientes/:id/peticiones" />
            </Routes>
          </ToastProvider>
        </AuthContext.Provider>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

function makePdf(name: string): File {
  const bytes = new Uint8Array(64)
  ;[0x25, 0x50, 0x44, 0x46, 0x2d].forEach((byte, index) => {
    bytes[index] = byte
  })
  return new File([bytes], name, { type: 'application/pdf' })
}

/** `Table` dibuja a la vez la versión de escritorio y la móvil: se usa la primera aparición. */
function primero(elementos: HTMLElement[]): HTMLElement {
  return elementos[0]!
}

describe('PeticionesPage (V-05)', () => {
  it('CA-V05-01: lista las peticiones reales con número, estado y dependencia, sin violaciones de axe', async () => {
    servirDetalle(EXPEDIENTE_BORRADOR)
    const { container } = renderAs(['ESTUDIANTE'])

    expect(await screen.findByRole('heading', { name: 'Peticiones documentales' })).toBeInTheDocument()
    expect(screen.getByText(EXPEDIENTE_BORRADOR.numero_expediente)).toBeInTheDocument()
    for (const peticion of EXPEDIENTE_BORRADOR.peticiones) {
      expect(screen.getAllByText(peticion.requisito_nombre).length).toBeGreaterThan(0)
    }
    expect(screen.getAllByText('Pendiente').length).toBeGreaterThan(0)
    expect(screen.getAllByText('TESORERIA').length).toBeGreaterThan(0)
    expect(await axe(container)).toHaveNoViolations()
  })

  it('CA-V05-05: explica que las peticiones son automáticas y no ofrece "crear petición"', async () => {
    servirDetalle(EXPEDIENTE_BORRADOR)
    renderAs(['ESTUDIANTE'])

    expect(await screen.findByText('Las peticiones se generan automáticamente')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Volver al expediente' })).toHaveAttribute(
      'href',
      `/expedientes/${EXPEDIENTE_BORRADOR.id}`,
    )
    expect(screen.queryByRole('button', { name: /crear petici/i })).not.toBeInTheDocument()
  })

  it('enlaza cada petición con su seguimiento (V-06)', async () => {
    servirDetalle(EXPEDIENTE_BORRADOR)
    renderAs(['ESTUDIANTE'])

    const enlace = primero(await screen.findAllByRole('link', { name: `Ver seguimiento: ${PRIMERA.requisito_nombre}` }))
    expect(enlace).toHaveAttribute('href', `/expedientes/${EXPEDIENTE_BORRADOR.id}/peticiones/${PRIMERA.id}`)
  })

  it('FE-T502: el estudiante confirma la solicitud, se envía el POST real y se refresca el expediente', async () => {
    const user = userEvent.setup()
    const lecturas = servirDetalle(EXPEDIENTE_BORRADOR)
    let peticionSolicitada = ''
    server.use(
      http.post(SOLICITAR_URL, ({ params }) => {
        peticionSolicitada = String(params.id)
        return HttpResponse.json({ ...PRIMERA, estado_peticion: 'SOLICITADO', fecha_solicitud: '2026-11-12T10:00:00Z' })
      }),
    )
    renderAs(['ESTUDIANTE'])

    await user.click(primero(await screen.findAllByRole('button', { name: `Solicitar emisión: ${PRIMERA.requisito_nombre}` })))
    const dialogo = await screen.findByRole('dialog', { name: 'Solicitar emisión' })
    expect(within(dialogo).getByText(/pasará al estado/)).toBeInTheDocument()
    expect(peticionSolicitada).toBe('')

    await user.click(within(dialogo).getByRole('button', { name: 'Confirmar solicitud' }))

    await waitFor(() => expect(peticionSolicitada).toBe(PRIMERA.id))
    expect(await screen.findByText(`Emisión solicitada: ${PRIMERA.requisito_nombre}.`)).toBeInTheDocument()
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
    await waitFor(() => expect(lecturas.total).toBeGreaterThanOrEqual(2))
  })

  it.each([
    [400, 'La petición no está en estado PENDIENTE.', 'estado_peticion_invalido'],
    [403, 'Solo el estudiante propietario puede solicitar la emisión.', 'permission_denied'],
    [404, 'La peticion documental no existe.', 'peticion_no_encontrada'],
  ])('FE-T502: ante un %i muestra el mensaje real del backend y mantiene el diálogo', async (status, detail, code) => {
    const user = userEvent.setup()
    servirDetalle(EXPEDIENTE_BORRADOR)
    server.use(http.post(SOLICITAR_URL, () => HttpResponse.json({ detail, code }, { status })))
    renderAs(['ESTUDIANTE'])

    await user.click(primero(await screen.findAllByRole('button', { name: `Solicitar emisión: ${PRIMERA.requisito_nombre}` })))
    const dialogo = await screen.findByRole('dialog', { name: 'Solicitar emisión' })
    await user.click(within(dialogo).getByRole('button', { name: 'Confirmar solicitud' }))

    expect(await within(dialogo).findByText(detail)).toBeInTheDocument()
    expect(screen.getByRole('dialog', { name: 'Solicitar emisión' })).toBeInTheDocument()
  })

  it('no ofrece solicitar la emisión cuando el expediente ya no está en BORRADOR/OBSERVADA', async () => {
    servirDetalle({ ...EXPEDIENTE_BORRADOR, estado: 'EN_VERIFICACION' })
    renderAs(['ESTUDIANTE'])

    await screen.findAllByText(PRIMERA.requisito_nombre)
    expect(screen.queryByRole('button', { name: /Solicitar emisión/ })).not.toBeInTheDocument()
    expect(screen.getAllByRole('button', { name: /Cargar documento/ }).length).toBeGreaterThan(0)
  })

  it('FE-T503: carga un PDF válido con POST multipart y confirma la versión registrada', async () => {
    const user = userEvent.setup()
    const lecturas = servirDetalle(EXPEDIENTE_BORRADOR)
    let peticionCargada = ''
    server.use(
      http.post(DOCUMENTO_URL, ({ params, request }) => {
        peticionCargada = String(params.id)
        expect(request.headers.get('content-type')).toMatch(/^multipart\/form-data/)
        return HttpResponse.json({ id: 'doc-1', peticion: params.id, version: 2, es_vigente: true }, { status: 201 })
      }),
    )
    const { container } = renderAs(['ESTUDIANTE'])

    await user.click(primero(await screen.findAllByRole('button', { name: `Cargar documento: ${PRIMERA.requisito_nombre}` })))
    const dialogo = await screen.findByRole('dialog', { name: 'Cargar documento' })
    const enviar = within(dialogo).getByRole('button', { name: 'Cargar documento' })
    expect(enviar).toBeDisabled()

    const input = (dialogo.querySelector('input[type="file"]') ?? container.querySelector('input[type="file"]')) as HTMLInputElement
    await user.upload(input, makePdf('record.pdf'))
    await waitFor(() => expect(enviar).toBeEnabled())
    await user.click(enviar)

    await waitFor(() => expect(peticionCargada).toBe(PRIMERA.id))
    expect(await screen.findByText('Documento cargado (versión 2).')).toBeInTheDocument()
    await waitFor(() => expect(lecturas.total).toBeGreaterThanOrEqual(2))
  })

  it('FE-T503: un archivo inválido no se envía, aunque antes se hubiera elegido uno válido', async () => {
    const user = userEvent.setup()
    servirDetalle(EXPEDIENTE_BORRADOR)
    let llamadas = 0
    server.use(
      http.post(DOCUMENTO_URL, () => {
        llamadas += 1
        return HttpResponse.json({}, { status: 201 })
      }),
    )
    renderAs(['ESTUDIANTE'])

    await user.click(primero(await screen.findAllByRole('button', { name: `Cargar documento: ${PRIMERA.requisito_nombre}` })))
    const dialogo = await screen.findByRole('dialog', { name: 'Cargar documento' })
    const input = dialogo.querySelector('input[type="file"]') as HTMLInputElement
    const enviar = within(dialogo).getByRole('button', { name: 'Cargar documento' })

    await user.upload(input, makePdf('valido.pdf'))
    await waitFor(() => expect(enviar).toBeEnabled())
    await user.upload(input, new File(['no es un pdf'], 'falso.pdf', { type: 'application/pdf' }))

    expect(await within(dialogo).findByText('El archivo no parece ser un PDF válido.')).toBeInTheDocument()
    expect(enviar).toBeDisabled()
    expect(llamadas).toBe(0)
  })

  it('FE-T503: un 400 de validación del backend se muestra con su mensaje real', async () => {
    const user = userEvent.setup()
    servirDetalle(EXPEDIENTE_BORRADOR)
    server.use(
      http.post(DOCUMENTO_URL, () =>
        HttpResponse.json({ detail: 'El PDF está protegido.', code: 'pdf_validation_error' }, { status: 400 }),
      ),
    )
    renderAs(['ESTUDIANTE'])

    await user.click(primero(await screen.findAllByRole('button', { name: `Cargar documento: ${PRIMERA.requisito_nombre}` })))
    const dialogo = await screen.findByRole('dialog', { name: 'Cargar documento' })
    await user.upload(dialogo.querySelector('input[type="file"]') as HTMLInputElement, makePdf('record.pdf'))
    const enviar = within(dialogo).getByRole('button', { name: 'Cargar documento' })
    await waitFor(() => expect(enviar).toBeEnabled())
    await user.click(enviar)

    expect(await within(dialogo).findByText('El PDF está protegido.')).toBeInTheDocument()
  })

  it('la Secretaría de Carrera solo puede cargar en peticiones asignadas a la Secretaría y no solicita emisiones', async () => {
    servirDetalle(EXPEDIENTE_BORRADOR)
    renderAs(['SECRETARIA_CARRERA'])

    await screen.findAllByText(PRIMERA.requisito_nombre)
    expect(screen.getAllByRole('button', { name: `Cargar documento: ${PRIMERA.requisito_nombre}` }).length).toBeGreaterThan(0)
    expect(screen.queryByRole('button', { name: 'Cargar documento: Tesorería' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /Solicitar emisión/ })).not.toBeInTheDocument()
  })

  it('un funcionario sin permisos de carga solo ve descarga y seguimiento en peticiones cargadas', async () => {
    servirDetalle(fixtureExpedienteDetalle)
    renderAs(['SECRETARIO_ABOGADO'], fixtureExpedienteDetalle.id)

    await screen.findAllByText(fixtureExpedienteDetalle.peticiones[0]!.requisito_nombre)
    expect(screen.queryByRole('button', { name: /Cargar documento/ })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /Solicitar emisión/ })).not.toBeInTheDocument()
    expect(screen.getAllByRole('button', { name: 'Descargar' }).length).toBeGreaterThan(0)
  })

  it('no ofrece descarga mientras la petición no tiene documento', async () => {
    servirDetalle(EXPEDIENTE_BORRADOR)
    renderAs(['ESTUDIANTE'])

    await screen.findAllByText(PRIMERA.requisito_nombre)
    expect(screen.queryByRole('button', { name: 'Descargar' })).not.toBeInTheDocument()
  })

  it('muestra "no encontrado" ante un 404 real del expediente', async () => {
    server.use(http.get(DETALLE_URL, () => HttpResponse.json({ detail: 'No encontrado.' }, { status: 404 })))
    renderAs(['ESTUDIANTE'])

    expect(await screen.findByText('Expediente no encontrado')).toBeInTheDocument()
  })

  it('muestra el estado de acceso restringido ante un 403 real', async () => {
    server.use(
      http.get(DETALLE_URL, () =>
        HttpResponse.json({ detail: 'No tiene permiso para realizar esta acción.' }, { status: 403 }),
      ),
    )
    renderAs(['ESTUDIANTE'])

    expect(await screen.findByRole('heading', { name: /acceso|permiso/i })).toBeInTheDocument()
    expect(screen.queryByText('Expediente no encontrado')).not.toBeInTheDocument()
  })

  it('ante un 500 ofrece reintentar y vuelve a consultar el expediente', async () => {
    const user = userEvent.setup()
    let llamadas = 0
    server.use(
      http.get(DETALLE_URL, () => {
        llamadas += 1
        return llamadas === 1
          ? HttpResponse.json({ detail: 'Error interno.' }, { status: 500 })
          : HttpResponse.json(EXPEDIENTE_BORRADOR)
      }),
    )
    renderAs(['ESTUDIANTE'])

    await user.click(await screen.findByRole('button', { name: /reintentar/i }))

    expect(await screen.findByRole('heading', { name: 'Peticiones documentales' })).toBeInTheDocument()
    expect(llamadas).toBe(2)
  })
})
