import { HttpResponse, delay, http } from 'msw'
import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'
import { Route, Routes } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { AuthContext, type AuthContextValue, type AuthUser } from '@/auth/AuthContext'
import { fixtureExpedienteBorrador, fixturePerfilAcademico } from '@/mocks/fixtures'
import { getRecentExpedientes } from '@/lib/storage'
import { confirmarDialogo } from '@/test/confirmar'
import { renderWithProviders } from '@/test/renderWithProviders'
import { server } from '@/test/server'
import NuevaSolicitudPage from './NuevaSolicitudPage'

const EXPEDIENTES_URL = '*/api/v1/expedientes/'
const PERFIL_URL = '*/api/v1/perfil-academico/'

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

function perfil(overrides: Partial<typeof fixturePerfilAcademico> = {}) {
  return { ...fixturePerfilAcademico, ...overrides }
}

function perfilBloqueado(estado: string, codigo: string, mensaje: string, extra = {}) {
  return perfil({
    estado_perfil: estado as typeof fixturePerfilAcademico.estado_perfil,
    perfil_validado: false,
    puede_iniciar_tramite: false,
    motivos_bloqueo: [{ codigo, mensaje }],
    ...extra,
  })
}

async function iniciarTramite() {
  const user = userEvent.setup()
  await user.click(await screen.findByRole('button', { name: 'Iniciar trámite' }))
  await confirmarDialogo(user)
  return user
}

describe('NuevaSolicitudPage (V-03, perfil académico)', () => {
  afterEach(() => {
    sessionStorage.clear()
    vi.restoreAllMocks()
  })

  it('carga: muestra un esqueleto mientras consulta el perfil', async () => {
    server.use(
      http.get(PERFIL_URL, async () => {
        await delay(50)
        return HttpResponse.json(fixturePerfilAcademico)
      }),
    )
    renderPage()
    expect(screen.getByRole('status')).toHaveTextContent('Consultando su información académica…')
    expect(await screen.findByText('Computación')).toBeInTheDocument()
  })

  it('perfil validado: muestra los datos de solo lectura y la fuente simulada, sin campo UUID', async () => {
    renderPage()

    expect(await screen.findByText('Perfil validado')).toBeInTheDocument()
    expect(screen.getByText('Estudiante De Prueba')).toBeInTheDocument()
    expect(screen.getByText('1104567890')).toBeInTheDocument()
    expect(screen.getByText('estudiante.prueba@unl.edu.ec')).toBeInTheDocument()
    expect(screen.getByText('Computación')).toBeInTheDocument()
    expect(screen.getByText('Facultad de prueba')).toBeInTheDocument()
    expect(screen.getByText('Información académica simulada')).toBeInTheDocument()
    expect(screen.getByText('Datos simulados')).toBeInTheDocument()

    expect(screen.queryByRole('textbox')).not.toBeInTheDocument()
    expect(screen.queryByRole('combobox')).not.toBeInTheDocument()
    expect(screen.queryByText(/UUID/i)).not.toBeInTheDocument()
    expect(screen.queryByText(/catálogo de carreras/i)).not.toBeInTheDocument()
  })

  it('fuente no simulada: no muestra el aviso de simulación', async () => {
    server.use(
      http.get(PERFIL_URL, () =>
        HttpResponse.json(perfil({ fuente: { codigo: 'SGA', nombre: 'SGA institucional', es_simulada: false } })),
      ),
    )
    renderPage()
    expect(await screen.findByText('SGA institucional')).toBeInTheDocument()
    expect(screen.queryByText('Información académica simulada')).not.toBeInTheDocument()
  })

  it('CA: crea el expediente con cuerpo vacío, muestra un toast, registra el ID y redirige', async () => {
    let cuerpo: unknown = 'sin-peticion'
    server.use(
      http.post(EXPEDIENTES_URL, async ({ request }) => {
        cuerpo = await request.json()
        return HttpResponse.json(fixtureExpedienteBorrador, { status: 201 })
      }),
    )
    renderPage()

    await iniciarTramite()

    expect(await screen.findByText('Detalle del expediente (V-04)')).toBeInTheDocument()
    expect(cuerpo).toEqual({})
    expect(getRecentExpedientes()).toEqual([
      {
        id: fixtureExpedienteBorrador.id,
        numeroExpediente: fixtureExpedienteBorrador.numero_expediente,
        visitadoEn: expect.any(String),
      },
    ])
  })

  it('limpia el borrador heredado de la versión con UUID al crear la solicitud', async () => {
    sessionStorage.setItem('sgt.nueva_solicitud_draft', '11111111-1111-1111-1111-111111111111')
    renderPage()
    await iniciarTramite()
    expect(await screen.findByText('Detalle del expediente (V-04)')).toBeInTheDocument()
    expect(sessionStorage.getItem('sgt.nueva_solicitud_draft')).toBeNull()
  })

  it.each([
    ['NO_ASOCIADO', 'perfil_academico_no_asociado', 'No encontramos su información académica'],
    ['INCOMPLETO', 'perfil_academico_incompleto', 'Su información académica está incompleta'],
    ['INCONSISTENTE', 'facultad_no_corresponde', 'Su información académica no es coherente'],
    ['CARRERA_INACTIVA', 'carrera_inactiva', 'Su carrera no está vigente'],
  ])('perfil %s: explica el motivo y no permite iniciar el trámite', async (estado, codigo, titulo) => {
    const mensaje = `Mensaje real del backend para ${codigo}.`
    server.use(http.get(PERFIL_URL, () => HttpResponse.json(perfilBloqueado(estado, codigo, mensaje))))
    renderPage()

    const alerta = await screen.findByText(titulo)
    const contenedor = alerta.closest('[role="alert"], [role="status"]') ?? document.body
    expect(within(contenedor as HTMLElement).getByText(mensaje)).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Iniciar trámite' })).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Volver a consultar' })).toBeInTheDocument()
  })

  it('perfil sin asociar: muestra "No registrado" en lugar de datos', async () => {
    server.use(
      http.get(PERFIL_URL, () =>
        HttpResponse.json(
          perfilBloqueado('NO_ASOCIADO', 'perfil_academico_no_asociado', 'Sin registro.', {
            estudiante: null,
            carrera: null,
            facultad: null,
          }),
        ),
      ),
    )
    renderPage()
    expect(await screen.findByText('Sin información académica')).toBeInTheDocument()
    expect(screen.getAllByText('No registrado').length).toBeGreaterThanOrEqual(4)
  })

  it('carrera inactiva: la marca como no vigente', async () => {
    server.use(
      http.get(PERFIL_URL, () =>
        HttpResponse.json(
          perfilBloqueado('CARRERA_INACTIVA', 'carrera_inactiva', 'Carrera no vigente.', {
            carrera: { ...fixturePerfilAcademico.carrera, activa: false },
          }),
        ),
      ),
    )
    renderPage()
    expect(await screen.findByText('(no vigente)')).toBeInTheDocument()
  })

  it('"Volver a consultar" repite la consulta del perfil', async () => {
    let llamadas = 0
    server.use(
      http.get(PERFIL_URL, () => {
        llamadas += 1
        return llamadas === 1
          ? HttpResponse.json(perfilBloqueado('NO_ASOCIADO', 'perfil_academico_no_asociado', 'Sin registro.'))
          : HttpResponse.json(fixturePerfilAcademico)
      }),
    )
    const user = userEvent.setup()
    renderPage()

    await user.click(await screen.findByRole('button', { name: 'Volver a consultar' }))

    expect(await screen.findByRole('button', { name: 'Iniciar trámite' })).toBeInTheDocument()
    expect(llamadas).toBe(2)
  })

  it('expediente activo existente: perfil validado sin botón de inicio y con acceso al panel', async () => {
    server.use(
      http.get(PERFIL_URL, () =>
        HttpResponse.json(
          perfil({
            puede_iniciar_tramite: false,
            motivos_bloqueo: [{ codigo: 'expediente_activo_existente', mensaje: 'Ya tiene un expediente activo.' }],
          }),
        ),
      ),
    )
    const user = userEvent.setup()
    renderPage()

    expect(await screen.findByText('Ya tiene un trámite en curso')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Iniciar trámite' })).not.toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Ir a mi panel' }))
    expect(await screen.findByText('Dashboard del estudiante (V-02)')).toBeInTheDocument()
  })

  it('error de servicio (503): ErrorState con el mensaje real y reintento real', async () => {
    let llamadas = 0
    server.use(
      http.get(PERFIL_URL, () => {
        llamadas += 1
        return llamadas === 1
          ? HttpResponse.json(
              { detail: 'No fue posible consultar su información académica.', code: 'servicio_academico_no_disponible' },
              { status: 503 },
            )
          : HttpResponse.json(fixturePerfilAcademico)
      }),
    )
    const user = userEvent.setup()
    renderPage()

    expect(await screen.findByText('No se pudo consultar su información académica')).toBeInTheDocument()
    expect(screen.getByText('No fue posible consultar su información académica.')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: /reintentar/i }))
    expect(await screen.findByRole('button', { name: 'Iniciar trámite' })).toBeInTheDocument()
  })

  it('403 al consultar el perfil redirige a V-09', async () => {
    server.use(http.get(PERFIL_URL, () => HttpResponse.json({ detail: 'Prohibido.' }, { status: 403 })))
    renderPage()
    expect(await screen.findByText('No habilitado (V-09)')).toBeInTheDocument()
  })

  it('creación: expediente activo (400 con code) muestra el mensaje y ofrece ir al panel', async () => {
    server.use(
      http.post(EXPEDIENTES_URL, () =>
        HttpResponse.json(
          { detail: 'El estudiante ya posee un expediente de titulacion activo.', code: 'expediente_activo_existente' },
          { status: 400 },
        ),
      ),
    )
    renderPage()
    const user = await iniciarTramite()

    expect(await screen.findByText(/ya posee un expediente de titulacion activo/i)).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Ir a mi panel' }))
    expect(await screen.findByText('Dashboard del estudiante (V-02)')).toBeInTheDocument()
  })

  it('creación: 422 de perfil vuelve a consultar el perfil y muestra el bloqueo', async () => {
    let consultas = 0
    server.use(
      http.get(PERFIL_URL, () => {
        consultas += 1
        return consultas === 1
          ? HttpResponse.json(fixturePerfilAcademico)
          : HttpResponse.json(perfilBloqueado('CARRERA_INACTIVA', 'carrera_inactiva', 'Su carrera dejó de estar vigente.'))
      }),
      http.post(EXPEDIENTES_URL, () =>
        HttpResponse.json({ detail: 'Su carrera no está vigente.', code: 'carrera_inactiva' }, { status: 422 }),
      ),
    )
    renderPage()
    await iniciarTramite()

    expect(await screen.findByText('Su carrera no está vigente')).toBeInTheDocument()
    expect(screen.getByText('Su carrera dejó de estar vigente.')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Iniciar trámite' })).not.toBeInTheDocument()
  })

  it('creación: 403 redirige a V-09', async () => {
    server.use(http.post(EXPEDIENTES_URL, () => HttpResponse.json({ detail: 'Prohibido.' }, { status: 403 })))
    renderPage()
    await iniciarTramite()
    expect(await screen.findByText('No habilitado (V-09)')).toBeInTheDocument()
  })

  it('creación: 503 de la fuente muestra el mensaje real del backend', async () => {
    server.use(
      http.post(EXPEDIENTES_URL, () =>
        HttpResponse.json(
          { detail: 'No fue posible consultar su información académica en este momento.', code: 'servicio_academico_no_disponible' },
          { status: 503 },
        ),
      ),
    )
    renderPage()
    await iniciarTramite()
    expect(await screen.findByRole('alert')).toHaveTextContent('No fue posible consultar su información académica en este momento.')
  })

  it('creación: 500 muestra un mensaje comprensible', async () => {
    server.use(http.post(EXPEDIENTES_URL, () => HttpResponse.json({ detail: 'Error interno.' }, { status: 500 })))
    renderPage()
    await iniciarTramite()
    expect(await screen.findByRole('alert')).toBeInTheDocument()
  })

  it('creación: error de red advierte resultado ambiguo y ofrece ir al panel', async () => {
    server.use(http.post(EXPEDIENTES_URL, () => HttpResponse.error()))
    renderPage()
    await iniciarTramite()

    expect(await screen.findByText(/No se pudo confirmar si la solicitud se creó/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Ir a mi panel' })).toBeInTheDocument()
  })

  it('protección ante doble creación: un segundo clic no dispara otra petición', async () => {
    let peticiones = 0
    server.use(
      http.post(EXPEDIENTES_URL, async () => {
        peticiones += 1
        await delay(100)
        return HttpResponse.json(fixtureExpedienteBorrador, { status: 201 })
      }),
    )
    renderPage()
    const user = await iniciarTramite()

    const boton = screen.getByRole('button', { name: /Iniciar trámite/ })
    await waitFor(() => expect(boton).toBeDisabled())
    await user.click(boton)

    expect(await screen.findByText('Detalle del expediente (V-04)')).toBeInTheDocument()
    expect(peticiones).toBe(1)
  })

  it('no presenta violaciones de accesibilidad (perfil validado y bloqueado)', async () => {
    const { container, unmount } = renderPage()
    await screen.findByText('Perfil validado')
    expect(await axe(container)).toHaveNoViolations()
    unmount()

    server.use(
      http.get(PERFIL_URL, () =>
        HttpResponse.json(perfilBloqueado('INCOMPLETO', 'carrera_no_registrada', 'Sin carrera registrada.')),
      ),
    )
    const segundo = renderPage()
    await screen.findByText('Su información académica está incompleta')
    expect(await axe(segundo.container)).toHaveNoViolations()
  })
})
