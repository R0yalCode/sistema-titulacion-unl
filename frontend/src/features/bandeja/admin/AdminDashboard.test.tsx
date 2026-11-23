import { HttpResponse, http } from 'msw'
import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Route, Routes } from 'react-router-dom'
import { axe } from 'vitest-axe'
import { describe, expect, it } from 'vitest'
import type { BandejaOperativaItem } from '@/api/endpoints/expedientes'
import { AuthContext, type AuthContextValue, type AuthUser } from '@/auth/AuthContext'
import { AppLayout } from '@/components/layout/AppLayout'
import { fixtureNotificacion } from '@/mocks/fixtures'
import { renderWithProviders } from '@/test/renderWithProviders'
import { server } from '@/test/server'
import BandejaPage from '../BandejaPage'

const BANDEJA_URL = '*/api/v1/expedientes/bandeja/'
const NOTIFICACIONES_URL = '*/api/v1/notificaciones/'
const DIA = 24 * 60 * 60 * 1000

function item(n: number, overrides: Partial<BandejaOperativaItem> = {}): BandejaOperativaItem {
  return {
    id: `00000000-0000-4000-8000-00000000000${n}`,
    numero_expediente: `EXP-2026-000${n}`,
    estudiante_id: '22222222-2222-4222-8222-222222222222',
    carrera_id: null,
    facultad_id: null,
    estado: 'ENVIADA',
    fecha_creacion: '2026-11-01T10:00:00Z',
    fecha_recepcion: '2026-11-02T10:00:00Z',
    numero_providencia: null,
    fecha_limite_atencion: new Date(Date.now() + 5 * DIA).toISOString(),
    ...overrides,
  }
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

function renderPanel(roles: string[] = ['ADMINISTRADOR']) {
  return renderWithProviders(
    <AuthContext.Provider value={authValue({ cedula: '1100000000', roles })}>
      <Routes>
        <Route element={<AppLayout />}>
          <Route element={<BandejaPage />} path="/bandeja" />
          <Route element={<p>Detalle real</p>} path="/bandeja/:id" />
        </Route>
      </Routes>
    </AuthContext.Provider>,
    { route: '/bandeja' },
  )
}

function servirBandeja(results: BandejaOperativaItem[], count = results.length) {
  server.use(http.get(BANDEJA_URL, () => HttpResponse.json({ count, next: null, previous: null, results })))
}

describe('Panel de administración', () => {
  it('muestra indicadores, distribución y prioridad calculados con la bandeja real', async () => {
    servirBandeja([
      item(1, { fecha_limite_atencion: new Date(Date.now() - 3 * DIA).toISOString() }),
      item(2, { estado: 'OBSERVADA' }),
    ])
    server.use(http.get(NOTIFICACIONES_URL, () => HttpResponse.json({ results: [fixtureNotificacion] })))
    const { container } = renderPanel()

    expect(await screen.findByRole('heading', { level: 1, name: 'Panel de administración' })).toBeInTheDocument()
    const vencidos = (await screen.findByRole('heading', { name: 'Plazo vencido' })).closest('article') as HTMLElement
    expect(within(vencidos).getByText('1')).toBeInTheDocument()
    expect(screen.getByRole('figure', { name: /Expedientes por estado/ })).toBeInTheDocument()
    const prioridad = screen.getByRole('heading', { name: 'Atención prioritaria' }).closest('section') as HTMLElement
    expect(within(prioridad).getByText('Vencido hace 3 días')).toBeInTheDocument()
    expect(await screen.findByRole('link', { name: new RegExp(fixtureNotificacion.titulo) })).toBeInTheDocument()
    expect(await axe(container)).toHaveNoViolations()
  })

  it('no presenta tendencias ni cifras parciales si la bandeja supera el resumen', async () => {
    servirBandeja([item(1)], 120)
    renderPanel()

    expect(await screen.findByRole('heading', { name: 'Indicadores detallados' })).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Plazo vencido' })).not.toBeInTheDocument()
    expect(screen.queryByRole('figure')).not.toBeInTheDocument()
  })

  it('un error del resumen ofrece un reintento real', async () => {
    let llamadas = 0
    server.use(
      http.get(BANDEJA_URL, () => {
        llamadas += 1
        return HttpResponse.json({ detail: 'Error' }, { status: 500 })
      }),
    )
    const user = userEvent.setup()
    renderPanel()

    const titulo = await screen.findByText('No se pudo cargar el resumen')
    const antes = llamadas
    const bloque = titulo.closest('[role="alert"], [role="status"]') as HTMLElement
    await user.click(within(bloque).getByRole('button'))
    await waitFor(() => expect(llamadas).toBeGreaterThan(antes))
  })

  it('Ctrl+K busca un expediente real y navega con el teclado', async () => {
    servirBandeja([item(1), item(2, { estado: 'OBSERVADA' })])
    const user = userEvent.setup()
    renderPanel()
    await screen.findByRole('heading', { name: 'Plazo vencido' })

    await user.keyboard('{Control>}k{/Control}')
    const campo = await screen.findByRole('combobox', { name: 'Texto de búsqueda' })
    await screen.findByRole('option', { name: /EXP-2026-0002/ })
    await user.type(campo, '0002')
    expect(within(screen.getByRole('listbox', { name: 'Resultados' })).getAllByRole('option')).toHaveLength(1)
    await user.keyboard('{Enter}')

    expect(await screen.findByText('Detalle real')).toBeInTheDocument()
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('la variante visual y la búsqueda no se aplican a otros roles', async () => {
    servirBandeja([item(1)])
    const { container } = renderPanel(['SECRETARIO_ABOGADO'])

    expect(await screen.findByRole('heading', { level: 1, name: 'Bandeja de expedientes' })).toBeInTheDocument()
    expect(container.querySelector('[data-visual]')).toBeNull()
    expect(screen.queryByRole('button', { name: /Buscar secciones/ })).not.toBeInTheDocument()
  })
})
