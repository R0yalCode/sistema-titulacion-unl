import { HttpResponse, http } from 'msw'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import { AuthContext, type AuthContextValue, type AuthUser } from '@/auth/AuthContext'
import type { BandejaOperativaItem } from '@/api/endpoints/expedientes'
import { server } from '@/test/server'
import BandejaPage from './BandejaPage'

const BANDEJA_URL = '*/api/v1/expedientes/bandeja/'
const DETALLE_URL = '*/api/v1/expedientes/:id/'
const DIA = 24 * 60 * 60 * 1000

function item(numero: number, overrides: Partial<BandejaOperativaItem> = {}): BandejaOperativaItem {
  return {
    id: `11111111-0000-0000-0000-${String(numero).padStart(12, '0')}`,
    numero_expediente: `EXP-2026-${String(numero).padStart(4, '0')}`,
    estudiante_id: '22222222-aaaa-bbbb-cccc-000000000001',
    carrera_id: '33333333-aaaa-bbbb-cccc-000000000001',
    facultad_id: '44444444-aaaa-bbbb-cccc-000000000001',
    estado: 'ENVIADA',
    fecha_creacion: '2026-11-01T10:00:00Z',
    fecha_recepcion: '2026-11-02T10:00:00Z',
    numero_providencia: `PROV-${numero}`,
    fecha_limite_atencion: new Date(Date.now() + 10 * DIA).toISOString(),
    ...overrides,
  }
}

function pagina(results: BandejaOperativaItem[], count = results.length) {
  return { count, next: null, previous: null, results }
}

/** Sirve la bandeja y registra cada URL pedida (para paginación y "sin peticiones extra"). */
function servirBandeja(responder: (url: URL) => object) {
  const urls: URL[] = []
  server.use(
    http.get(BANDEJA_URL, ({ request }) => {
      const url = new URL(request.url)
      urls.push(url)
      return HttpResponse.json(responder(url))
    }),
  )
  return urls
}

function authValue(user: AuthUser): AuthContextValue {
  return {
    user,
    isAuthenticated: true,
    isLoading: false,
    login: () => true,
    logout: () => undefined,
    signOut: () => undefined,
    hasRole: (roles) => roles.some((role) => user.roles.includes(role)),
  }
}

function renderAs(roles: string[]) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/bandeja']}>
        <AuthContext.Provider value={authValue({ cedula: '1104567890', roles })}>
          <Routes>
            <Route element={<BandejaPage />} path="/bandeja" />
            <Route element={<p>Detalle del expediente (V-08)</p>} path="/bandeja/:id" />
            <Route element={<p>Página no habilitado</p>} path="/no-habilitado" />
          </Routes>
        </AuthContext.Provider>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

function primero(elementos: HTMLElement[]): HTMLElement {
  return elementos[0]!
}

describe('BandejaPage (V-07)', () => {
  it('CA-V07-01: el secretario ve los expedientes reales con total, estado y enlaces, sin violaciones de axe', async () => {
    servirBandeja(() =>
      pagina([item(1), item(2, { estado: 'EN_VERIFICACION' }), item(3, { estado: 'OBSERVADA' })]),
    )
    const { container } = renderAs(['SECRETARIO_ABOGADO'])

    expect(await screen.findByText('3 expedientes en la bandeja · página 1 de 1')).toBeInTheDocument()
    expect(primero(screen.getAllByRole('link', { name: 'Abrir expediente EXP-2026-0001' }))).toHaveAttribute(
      'href',
      `/bandeja/${item(1).id}`,
    )
    expect(screen.getAllByText('En verificación').length).toBeGreaterThan(0)
    expect(screen.queryByText('EN_VERIFICACION')).not.toBeInTheDocument()
    expect(screen.getAllByText(/PROV-3/).length).toBeGreaterThan(0)
    expect(screen.getAllByText('22222222').length).toBeGreaterThan(0)
    expect(await axe(container)).toHaveNoViolations()
  })

  it('CA-V07-02: el decano ve los expedientes en INFORME_EMITIDO que devuelve el backend', async () => {
    servirBandeja(() => pagina([item(7, { estado: 'INFORME_EMITIDO' })]))
    renderAs(['DECANO'])

    expect(await screen.findByText('1 expediente en la bandeja · página 1 de 1')).toBeInTheDocument()
    expect(screen.getAllByText('Informe emitido').length).toBeGreaterThan(0)
  })

  it('CA-V07-03: un rol sin bandeja (BE-09) ve un panel explicativo con sus avisos y no consulta la bandeja', async () => {
    const urls = servirBandeja(() => pagina([], 0))
    renderAs(['SECRETARIA_CARRERA'])

    expect(await screen.findByText(/no asigna expedientes a la bandeja de su rol por ahora \(dependencia BE-09\)/)).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Avisos recientes' })).toBeInTheDocument()
    expect(urls).toHaveLength(0)
  })

  it('un rol con bandeja pero sin pendientes ve un vacío distinto', async () => {
    servirBandeja(() => pagina([], 0))
    renderAs(['SECRETARIO_ABOGADO'])

    expect(await screen.findByText('No hay expedientes pendientes')).toBeInTheDocument()
    expect(screen.queryByText(/BE-09/)).not.toBeInTheDocument()
  })

  it('CA-V07-04: pagina contra el backend con page y page_size reales', async () => {
    const user = userEvent.setup()
    const urls = servirBandeja((url) => {
      const page = Number(url.searchParams.get('page'))
      return pagina([item(page * 100)], 25)
    })
    renderAs(['ADMINISTRADOR'])

    expect(await screen.findByText('25 expedientes en la bandeja · página 1 de 3')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Siguiente' }))

    expect(await screen.findByText('25 expedientes en la bandeja · página 2 de 3')).toBeInTheDocument()
    expect(screen.getAllByText('EXP-2026-0200').length).toBeGreaterThan(0)
    expect(urls.at(-1)?.searchParams.get('page')).toBe('2')
    expect(urls.at(-1)?.searchParams.get('page_size')).toBe('10')
  })

  it('FE-T703: los filtros solo actúan sobre la página actual, lo dicen y no consultan al backend', async () => {
    const user = userEvent.setup()
    const urls = servirBandeja(() => pagina([item(1), item(2, { estado: 'OBSERVADA' })], 30))
    renderAs(['SECRETARIO_ABOGADO'])

    await screen.findByText('30 expedientes en la bandeja · página 1 de 3')
    expect(screen.getByText(/solo actúan sobre la página actual \(2 de 2 expedientes visibles\)/)).toBeInTheDocument()
    const peticionesAntes = urls.length

    await user.selectOptions(screen.getByLabelText('Estado (página actual)'), 'OBSERVADA')

    expect(screen.getByText(/\(1 de 2 expedientes visibles\)/)).toBeInTheDocument()
    expect(screen.queryAllByText('EXP-2026-0001')).toHaveLength(0)
    expect(urls.length).toBe(peticionesAntes)
  })

  it('FE-T704: resalta vencidos y "vence hoy" con cálculo local y muestra días calendario restantes', async () => {
    const finDeHoy = new Date()
    finDeHoy.setHours(23, 59, 59, 0)
    servirBandeja(() =>
      pagina([
        item(1, { fecha_limite_atencion: new Date(Date.now() - 3 * DIA).toISOString() }),
        item(2, { fecha_limite_atencion: finDeHoy.toISOString() }),
        item(3, { fecha_limite_atencion: null }),
      ]),
    )
    renderAs(['SECRETARIO_ABOGADO'])

    expect((await screen.findAllByText('Vencido hace 3 días calendario')).length).toBeGreaterThan(0)
    expect(screen.getAllByText('Vence hoy').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Sin fecha límite').length).toBeGreaterThan(0)
  })

  it('CA-V07-05: navega a V-08 con el teclado y precarga el detalle al enfocar el enlace', async () => {
    const user = userEvent.setup()
    let detallesPedidos = 0
    server.use(
      http.get(DETALLE_URL, () => {
        detallesPedidos += 1
        return HttpResponse.json({ id: item(1).id })
      }),
    )
    // Se registra después: el patrón `:id` del detalle también encajaría con `/bandeja/`.
    servirBandeja(() => pagina([item(1)]))
    renderAs(['SECRETARIO_ABOGADO'])

    const enlace = primero(await screen.findAllByRole('link', { name: 'Abrir expediente EXP-2026-0001' }))
    enlace.focus()
    await waitFor(() => expect(detallesPedidos).toBe(1))
    await user.keyboard('{Enter}')

    expect(await screen.findByText('Detalle del expediente (V-08)')).toBeInTheDocument()
  })

  it('no ofrece acciones de escritura en la bandeja', async () => {
    servirBandeja(() => pagina([item(1)]))
    renderAs(['ADMINISTRADOR'])

    await screen.findByText('1 expediente en la bandeja · página 1 de 1')
    // Solo navegación, paginación y filtros rápidos: ninguna operación de escritura.
    const botones = screen.getAllByRole('button').map((boton) => boton.textContent ?? '')
    expect(botones.length).toBeGreaterThan(0)
    expect(botones.some((texto) => /enviar|observar|verificar|emitir|declarar|eliminar|guardar/i.test(texto))).toBe(false)
  })

  it('un 403 muestra acceso restringido con enlace a V-09 sin revelar la regla', async () => {
    server.use(
      http.get(BANDEJA_URL, () =>
        HttpResponse.json({ detail: 'El rol del usuario no esta autorizado.' }, { status: 403 }),
      ),
    )
    renderAs(['SECRETARIO_ABOGADO'])

    const enlace = await screen.findByRole('link', { name: 'Más información' })
    expect(within(enlace.closest('[role="status"]') as HTMLElement).getByText('Acceso restringido')).toBeInTheDocument()
    expect(enlace).toHaveAttribute(
      'href',
      '/no-habilitado?motivo=rol-no-autorizado',
    )
  })

  it.each([
    ['un 500', () => HttpResponse.json({ detail: 'Error interno.' }, { status: 500 })],
    ['un error de red', () => HttpResponse.error()],
  ])('ante %s ofrece reintentar y vuelve a consultar', async (_caso, fallo) => {
    const user = userEvent.setup()
    let llamadas = 0
    server.use(
      http.get(BANDEJA_URL, ({ request }) => {
        // Solo cuenta las consultas del listado (page_size=10); el resumen usa 50.
        if (new URL(request.url).searchParams.get('page_size') !== '10') {
          return HttpResponse.json(pagina([item(1)]))
        }
        llamadas += 1
        return llamadas === 1 ? fallo() : HttpResponse.json(pagina([item(1)]))
      }),
    )
    renderAs(['SECRETARIO_ABOGADO'])

    await user.click(await screen.findByRole('button', { name: /reintentar/i }))

    expect(await screen.findByText('1 expediente en la bandeja · página 1 de 1')).toBeInTheDocument()
    expect(llamadas).toBe(2)
  })
})

describe('Hero Liquid Glass y alerta de plazos (LG-E)', () => {
  function finDeHoy(): string {
    const fecha = new Date()
    fecha.setHours(23, 59, 59, 0)
    return fecha.toISOString()
  }

  async function hero(): Promise<HTMLElement> {
    return screen.findByRole('region', { name: 'Bandeja de expedientes' })
  }

  it('con plazos vencidos reales la tarjeta del hero pulsa y enlaza al listado', async () => {
    servirBandeja(() =>
      pagina([
        item(1, { fecha_limite_atencion: new Date(Date.now() - 3 * DIA).toISOString() }),
        item(2, { fecha_limite_atencion: finDeHoy() }),
        item(3),
      ]),
    )
    renderAs(['SECRETARIO_ABOGADO'])

    const region = await hero()
    const tarjeta = await within(region).findByRole('article')
    expect(within(tarjeta).getByRole('heading', { name: '1 expediente con el plazo vencido' })).toBeInTheDocument()
    expect(within(tarjeta).getByText('1 vencido').parentElement).toHaveAttribute('data-pulse', 'true')
    expect(within(tarjeta).getByText('1 expediente vence hoy')).toBeInTheDocument()
    expect(within(tarjeta).getByRole('link', { name: /Ver en el listado/ })).toHaveAttribute('href', '#listado-bandeja')
  })

  it('si solo vencen hoy avisa sin pulso (nivel de atención)', async () => {
    servirBandeja(() => pagina([item(1, { fecha_limite_atencion: finDeHoy() }), item(2)]))
    renderAs(['SECRETARIO_ABOGADO'])

    const tarjeta = await within(await hero()).findByRole('article')
    expect(within(tarjeta).getByRole('heading', { name: '1 expediente por atender hoy' })).toBeInTheDocument()
    expect(within(tarjeta).getByText('1 vence hoy').parentElement).toHaveAttribute('data-pulse', 'false')
  })

  it('sin plazos vencidos informa que están al día y no anima nada', async () => {
    servirBandeja(() => pagina([item(1), item(2)]))
    renderAs(['DECANO'])

    const region = await hero()
    const tarjeta = await within(region).findByRole('article')
    expect(within(tarjeta).getByRole('heading', { name: 'Plazos al día' })).toBeInTheDocument()
    expect(region.querySelector('[data-pulse]')).toBeNull()
  })

  it('con una bandeja mayor que la página de resumen no presenta una alerta parcial', async () => {
    servirBandeja(() => pagina([item(1, { fecha_limite_atencion: new Date(Date.now() - DIA).toISOString() })], 120))
    renderAs(['SECRETARIO_ABOGADO'])

    expect(await screen.findByRole('heading', { name: 'Indicadores detallados' })).toBeInTheDocument()
    expect(within(await hero()).queryByRole('article')).not.toBeInTheDocument()
  })
})
