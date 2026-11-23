import { HttpResponse, http } from 'msw'
import { screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'
import { Route, Routes } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import type { MiTramite } from '@/api/endpoints/miTramite'
import { fixtureMiTramite } from '@/mocks/fixtures'
import { renderWithProviders } from '@/test/renderWithProviders'
import { server } from '@/test/server'
import StudentDashboardPage from './StudentDashboardPage'

const MI_TRAMITE_URL = '*/api/v1/expedientes/mi-tramite/'

function responder(datos: MiTramite) {
  server.use(http.get(MI_TRAMITE_URL, () => HttpResponse.json(datos)))
}

function conExpediente(overrides: Partial<NonNullable<MiTramite['expediente']>>): MiTramite {
  return { ...fixtureMiTramite, expediente: { ...fixtureMiTramite.expediente, ...overrides } } as MiTramite
}

function renderDashboard() {
  return renderWithProviders(
    <Routes>
      <Route element={<StudentDashboardPage />} path="/estudiante" />
      <Route element={<p>Crear solicitud (V-03)</p>} path="/estudiante/solicitud/nueva" />
      <Route element={<p>Detalle de la petición</p>} path="/expedientes/:id/peticiones/:peticionId" />
    </Routes>,
    { route: '/estudiante' },
  )
}

function kpi(nombre: string): HTMLElement {
  return screen.getByRole('heading', { level: 3, name: nombre }).closest('article') as HTMLElement
}

describe('StudentDashboardPage (dashboard del estudiante)', () => {
  it('muestra el encabezado con el nombre real del estudiante y su expediente', async () => {
    renderDashboard()

    expect(screen.getByRole('heading', { level: 1, name: 'Mi proceso de titulación' })).toBeInTheDocument()
    expect(screen.getByText('Consulta tu avance, pendientes y próximos pasos.')).toBeInTheDocument()
    expect(await screen.findByText('Estudiante de Prueba')).toBeInTheDocument()
    expect(screen.getByText('EXP-2026-0003')).toBeInTheDocument()
  })

  it('muestra un estado de carga accesible mientras llega el resumen', () => {
    renderDashboard()
    expect(screen.getByRole('status', { name: '' })).toHaveAttribute('aria-busy', 'true')
    expect(screen.getByText('Cargando tu proceso de titulación…')).toBeInTheDocument()
  })

  it('presenta los cuatro KPI con datos reales del backend (BORRADOR)', async () => {
    renderDashboard()
    await screen.findByText('Estudiante de Prueba')

    expect(within(kpi('Estado actual')).getByText('En preparación')).toBeInTheDocument()

    const barra = within(kpi('Progreso general')).getByRole('progressbar', { name: 'Progreso general del trámite' })
    expect(barra).toHaveAttribute('aria-valuenow', '0')
    expect(barra).toHaveAttribute('aria-valuetext', '0 de 5 etapas completadas')

    expect(within(kpi('Acciones pendientes')).getByText('2')).toBeInTheDocument()
    expect(within(kpi('Acciones pendientes')).getByRole('link', { name: /Ver qué hacer/ })).toHaveAttribute(
      'href',
      '#pendientes',
    )

    const hito = kpi('Próximo hito')
    expect(within(hito).getByText('Solicitud enviada')).toBeInTheDocument()
    expect(within(hito).getByText('Sin fecha registrada.')).toBeInTheDocument()
  })

  it('lista las acciones pendientes con enlace directo al requisito', async () => {
    const user = userEvent.setup()
    renderDashboard()

    const pendientes = await screen.findByRole('region', { name: 'Necesitas completar' })
    const acciones = within(pendientes).getAllByRole('listitem')
    expect(acciones).toHaveLength(2)
    expect(within(acciones[0] as HTMLElement).getByRole('heading', { name: 'Completa el documento: Récord académico' })).toBeInTheDocument()

    await user.click(within(acciones[0] as HTMLElement).getByRole('link', { name: /Gestionar documento/ }))
    expect(await screen.findByText('Detalle de la petición')).toBeInTheDocument()
  })

  it('muestra el seguimiento con la etapa actual marcada y las pendientes discretas', async () => {
    renderDashboard()

    const seguimiento = await screen.findByRole('region', { name: 'Mi seguimiento de titulación' })
    const pasos = within(seguimiento).getAllByRole('listitem')
    expect(pasos).toHaveLength(5)
    expect(pasos[0]).toHaveAttribute('aria-current', 'step')
    expect(within(pasos[0] as HTMLElement).getByText('Etapa actual')).toBeInTheDocument()
    expect(within(pasos[1] as HTMLElement).getByText('Próximo hito')).toBeInTheDocument()
    expect(within(pasos[4] as HTMLElement).getByText('Pendiente')).toBeInTheDocument()
  })

  it('resume la documentación por estado real y lista los movimientos', async () => {
    renderDashboard()

    const documentos = await screen.findByRole('region', { name: 'Documentación' })
    const leyenda = within(documentos).getByRole('list', { name: 'Resumen por estado' })
    expect(within(leyenda).getByText(/Pendiente/)).toHaveTextContent('Pendiente: 2')
    expect(within(leyenda).getByText(/Cargado/)).toHaveTextContent('Cargado: 3')
    // Ningún estado inventado (CA-G-01).
    expect(screen.queryByText(/En revisión/)).not.toBeInTheDocument()

    const movimientos = screen.getByRole('region', { name: 'Últimos movimientos' })
    expect(within(movimientos).getByText('Documento cargado')).toBeInTheDocument()
    expect(within(movimientos).getByText('Solicitud registrada')).toBeInTheDocument()
  })

  it('con observaciones muestra el motivo y la acción de corrección', async () => {
    responder(
      conExpediente({
        estado: 'OBSERVADA',
        etapas: fixtureMiTramite.expediente.etapas.map((etapa, index) => ({
          ...etapa,
          situacion: index < 2 ? 'completada' : index === 2 ? 'actual' : 'pendiente',
          fecha: index <= 2 ? '2026-11-01T10:00:00Z' : null,
        })),
        progreso: { etapas_completadas: 2, etapas_totales: 5 },
        requisitos_sin_documento: [],
        observaciones_pendientes: [
          {
            id: 'obs-1',
            peticion_id: fixtureMiTramite.expediente.peticiones[0]?.id as string,
            requisito_nombre: 'Récord académico',
            motivo_observacion: 'El documento no tiene firma de responsabilidad.',
            fecha_registro: '2026-11-03T10:00:00Z',
          },
        ],
      }),
    )
    renderDashboard()

    expect(await screen.findByText('Con observaciones')).toBeInTheDocument()
    const pendientes = screen.getByRole('region', { name: 'Necesitas completar' })
    expect(within(pendientes).getByText('El documento no tiene firma de responsabilidad.')).toBeInTheDocument()
    expect(within(pendientes).getByRole('link', { name: /Ver y corregir/ })).toBeInTheDocument()
    expect(within(kpi('Progreso general')).getByText('40')).toBeInTheDocument()
    expect(screen.getByText('En pausa: con observaciones')).toBeInTheDocument()
  })

  it('trámite finalizado: sin acciones pendientes ni próximo hito', async () => {
    responder(
      conExpediente({
        estado: 'DECLARADA_APTA',
        etapas: fixtureMiTramite.expediente.etapas.map((etapa) => ({
          ...etapa,
          situacion: 'completada',
          fecha: '2026-11-01T10:00:00Z',
        })),
        progreso: { etapas_completadas: 5, etapas_totales: 5 },
        requisitos_sin_documento: [],
      }),
    )
    renderDashboard()

    expect(await screen.findByText('Declarado apto')).toBeInTheDocument()
    expect(within(kpi('Progreso general')).getByText('100')).toBeInTheDocument()
    expect(within(kpi('Acciones pendientes')).getByText('No tienes acciones pendientes actualmente.')).toBeInTheDocument()
    expect(within(kpi('Próximo hito')).getByText('Tu trámite concluyó; no hay hitos pendientes.')).toBeInTheDocument()
  })

  it('en verificación muestra la fecha límite institucional real como próximo hito', async () => {
    responder(
      conExpediente({
        estado: 'EN_VERIFICACION',
        etapas: fixtureMiTramite.expediente.etapas.map((etapa, index) => ({
          ...etapa,
          situacion: index < 2 ? 'completada' : index === 2 ? 'actual' : 'pendiente',
          fecha: index <= 2 ? '2026-11-01T10:00:00Z' : null,
        })),
        progreso: { etapas_completadas: 2, etapas_totales: 5 },
        fecha_limite_atencion: '2026-11-12T17:00:00Z',
        requisitos_sin_documento: [],
      }),
    )
    renderDashboard()

    const hito = await screen.findByRole('heading', { level: 3, name: 'Próximo hito' })
    const tarjeta = hito.closest('article') as HTMLElement
    expect(within(tarjeta).getByText('Informe emitido')).toBeInTheDocument()
    expect(within(tarjeta).getByText(/Fecha límite de atención institucional/)).toBeInTheDocument()
  })

  it('estudiante sin trámite: estado vacío con acceso a crear la solicitud', async () => {
    const user = userEvent.setup()
    responder({ ...fixtureMiTramite, total_expedientes: 0, expediente: null })
    renderDashboard()

    expect(await screen.findByRole('heading', { name: 'Aún no tienes un trámite de titulación' })).toBeInTheDocument()
    expect(screen.queryByRole('progressbar')).not.toBeInTheDocument()
    await user.click(screen.getByRole('link', { name: 'Crear solicitud' }))
    expect(await screen.findByText('Crear solicitud (V-03)')).toBeInTheDocument()
  })

  it('error 500: muestra ErrorState con reintento real', async () => {
    const user = userEvent.setup()
    let llamadas = 0
    server.use(
      http.get(MI_TRAMITE_URL, () => {
        llamadas += 1
        return llamadas === 1
          ? HttpResponse.json({ detail: 'Error interno' }, { status: 500 })
          : HttpResponse.json(fixtureMiTramite)
      }),
    )
    renderDashboard()

    expect(await screen.findByRole('heading', { name: 'No pudimos cargar tu proceso de titulación' })).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Reintentar' }))
    expect(await screen.findByText('Estudiante de Prueba')).toBeInTheDocument()
    expect(llamadas).toBe(2)
  })

  it('error 403: muestra ForbiddenState dentro de la vista', async () => {
    server.use(http.get(MI_TRAMITE_URL, () => HttpResponse.json({ detail: 'Prohibido' }, { status: 403 })))
    renderDashboard()

    expect(await screen.findByRole('heading', { name: 'Acceso restringido' })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Reintentar' })).not.toBeInTheDocument()
  })

  it('no tiene violaciones de accesibilidad detectables (axe)', async () => {
    const { container } = renderDashboard()
    await screen.findByText('Estudiante de Prueba')
    expect(await axe(container)).toHaveNoViolations()
  })
})
