import { HttpResponse, http } from 'msw'
import { screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'
import { Route, Routes } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import type { BandejaOperativaItem } from '@/api/endpoints/expedientes'
import { AuthContext, type AuthContextValue, type AuthUser } from '@/auth/AuthContext'
import { BarChart } from '@/components/ui/BarChart'
import { fixtureNotificacion } from '@/mocks/fixtures'
import { renderWithProviders } from '@/test/renderWithProviders'
import { server } from '@/test/server'
import BandejaPage from './BandejaPage'
import { contextoRol, resumirBandeja } from './resumen'

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

function renderBandeja(roles: string[]) {
  return renderWithProviders(
    <AuthContext.Provider value={authValue({ cedula: '1100000000', roles })}>
      <Routes>
        <Route element={<BandejaPage />} path="/bandeja" />
        <Route element={<p>Peticiones del expediente</p>} path="/expedientes/:id/peticiones" />
      </Routes>
    </AuthContext.Provider>,
    { route: '/bandeja' },
  )
}

describe('resumirBandeja (indicadores con datos reales)', () => {
  const ahora = new Date()

  it('cuenta vencidos, vencen hoy y distribución por estado cuando la bandeja está completa', () => {
    const finDeHoy = new Date(ahora)
    finDeHoy.setHours(23, 59, 59, 0)
    const resumen = resumirBandeja(
      [
        item(1, { fecha_limite_atencion: new Date(ahora.getTime() - 2 * DIA).toISOString() }),
        item(2, { estado: 'OBSERVADA', fecha_limite_atencion: finDeHoy.toISOString() }),
        item(3, { estado: 'OBSERVADA' }),
      ],
      3,
      ahora,
    )
    expect(resumen).toMatchObject({ total: 3, completo: true, vencidos: 1, vencenHoy: 1 })
    expect(resumen.porEstado[0]).toEqual({ estado: 'OBSERVADA', label: 'Observada', cantidad: 2 })
  })

  it('marca el resumen como incompleto si la bandeja supera la página recibida', () => {
    expect(resumirBandeja([item(1)], 80, ahora).completo).toBe(false)
  })
})

describe('contextoRol', () => {
  it('solo propone accesos rápidos sobre estados que el backend asigna al rol', () => {
    expect(contextoRol(['DECANO']).accionesRapidas.map((a) => a.estado)).toEqual(['INFORME_EMITIDO'])
    expect(contextoRol(['SECRETARIO_ABOGADO']).accionesRapidas.map((a) => a.estado)).toEqual([
      'ENVIADA',
      'EN_VERIFICACION',
      'OBSERVADA',
    ])
    expect(contextoRol(['SECRETARIA_CARRERA']).accionesRapidas).toEqual([])
    expect(contextoRol(['DIRECTOR_CARRERA']).accionesRapidas).toEqual([])
  })
})

describe('Panel de inicio del funcionario', () => {
  it('muestra KPI reales, la distribución por estado y filtra con un acceso rápido', async () => {
    const user = userEvent.setup()
    server.use(
      http.get(BANDEJA_URL, () =>
        HttpResponse.json({
          count: 3,
          next: null,
          previous: null,
          results: [
            item(1, { fecha_limite_atencion: new Date(Date.now() - 3 * DIA).toISOString() }),
            item(2, { estado: 'OBSERVADA' }),
            item(3, { estado: 'EN_VERIFICACION' }),
          ],
        }),
      ),
    )
    const { container } = renderBandeja(['SECRETARIO_ABOGADO'])

    const vencidos = (await screen.findByRole('heading', { name: 'Plazo vencido' })).closest('article') as HTMLElement
    expect(within(vencidos).getByText('1')).toBeInTheDocument()
    const grafico = screen.getByRole('figure')
    expect(within(grafico).getByText('Expedientes por estado')).toBeInTheDocument()
    expect(within(grafico).getByText('Observada')).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: /Con observaciones/ }))
    expect(screen.getByLabelText('Estado (página actual)')).toHaveValue('OBSERVADA')
    expect(await axe(container)).toHaveNoViolations()
  })

  it('con una bandeja mayor que la página de resumen no presenta cifras parciales como totales', async () => {
    server.use(
      http.get(BANDEJA_URL, () => HttpResponse.json({ count: 120, next: 'x', previous: null, results: [item(1)] })),
    )
    renderBandeja(['ADMINISTRADOR'])
    expect(await screen.findByRole('heading', { name: 'Indicadores detallados' })).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Plazo vencido' })).not.toBeInTheDocument()
    expect(screen.queryByRole('figure')).not.toBeInTheDocument()
  })

  it('el administrador ve accesos a la consola interna existente (usuarios, roles, auditoría)', async () => {
    renderBandeja(['ADMINISTRADOR'])
    const panel = (await screen.findByRole('heading', { name: 'Administración del sistema' })).closest('section') as HTMLElement
    expect(within(panel).getByRole('link', { name: /Usuarios/ }).getAttribute('href')).toMatch(/\/admin\/authentication\/user\/$/)
    expect(within(panel).getByRole('link', { name: /Auditoría/ })).toBeInTheDocument()
  })

  it('la Secretaría de carrera ve sus avisos con acceso directo a las peticiones del expediente', async () => {
    const user = userEvent.setup()
    server.use(http.get(NOTIFICACIONES_URL, () => HttpResponse.json({ results: [fixtureNotificacion] })))
    renderBandeja(['SECRETARIA_CARRERA'])

    const avisos = (await screen.findByRole('heading', { name: 'Avisos recientes' })).closest('section') as HTMLElement
    await user.click(await within(avisos).findByRole('link', { name: /Ver peticiones/ }))
    expect(await screen.findByText('Peticiones del expediente')).toBeInTheDocument()
  })
})

describe('BarChart', () => {
  it('ofrece los valores en texto como alternativa accesible', () => {
    renderWithProviders(
      <BarChart context="Bandeja actual" data={[{ label: 'Enviada', value: 3 }, { label: 'Observada', value: 1 }]} title="Por estado" unit="expedientes" />,
    )
    const figura = screen.getByRole('figure', { name: /Por estado/ })
    expect(within(figura).getByText('expedientes (75 %)', { exact: false })).toBeInTheDocument()
  })
})
