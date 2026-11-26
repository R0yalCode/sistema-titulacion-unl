import type { ReactNode } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { axe } from 'vitest-axe'
import { AuthContext, type AuthContextValue } from '@/auth/AuthContext'
import { AsistenteFlotante } from './AsistenteFlotante'
import { AsistenteGlobal } from './AsistenteGlobal'
import { ClienteAsistenteContext, clienteNoDisponible, type ClienteAsistente, type RespuestaAsistente } from './clienteAsistente'
import { MENSAJE_CANALES_OFICIALES, MENSAJE_NO_DISPONIBLE } from './consultaNormativa'

function auth(roles: string[] | null): AuthContextValue {
  return {
    user: roles ? { cedula: '1100000000', roles } : null,
    isAuthenticated: roles !== null,
    isLoading: false,
    login: vi.fn().mockReturnValue(true),
    logout: vi.fn(),
    signOut: vi.fn(),
    hasRole: (lista) => (roles ?? []).some((rol) => lista.includes(rol)),
  }
}

function Proveedores({
  children,
  roles = ['ESTUDIANTE'],
  ruta = '/estudiante',
  cliente = clienteNoDisponible,
}: {
  children: ReactNode
  roles?: string[] | null
  ruta?: string
  cliente?: ClienteAsistente
}) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return (
    <QueryClientProvider client={queryClient}>
      <AuthContext.Provider value={auth(roles)}>
        <ClienteAsistenteContext.Provider value={cliente}>
          <MemoryRouter initialEntries={[ruta]}>
            <Routes>
              <Route element={<main><h1>Vista de prueba</h1></main>} path="*" />
            </Routes>
            {children}
          </MemoryRouter>
        </ClienteAsistenteContext.Provider>
      </AuthContext.Provider>
    </QueryClientProvider>
  )
}

function renderAsistente(opciones: { roles?: string[]; cliente?: ClienteAsistente } = {}) {
  return render(
    <Proveedores {...opciones}>
      <AsistenteFlotante />
    </Proveedores>,
  )
}

async function abrir() {
  const user = userEvent.setup()
  await user.click(screen.getByRole('button', { name: 'Abrir el asistente de ayuda' }))
  return { user, panel: screen.getByRole('dialog', { name: 'Asistente SGT-SIAAF' }) }
}

/** Promesa controlable para observar el indicador de procesamiento. */
function diferida() {
  let resolver!: (valor: RespuestaAsistente) => void
  const promesa = new Promise<RespuestaAsistente>((ok) => (resolver = ok))
  return { promesa, resolver }
}

afterEach(() => {
  vi.useRealTimers()
})

describe('AsistenteFlotante (AX-D)', () => {
  it('ofrece un botón flotante con mascota, signo de ayuda y tooltip, que abre un chat sin salir de la vista', async () => {
    renderAsistente()
    const boton = screen.getByRole('button', { name: 'Abrir el asistente de ayuda' })
    expect(boton).toHaveAttribute('aria-expanded', 'false')
    expect(within(boton).getByText('?')).toBeInTheDocument()
    expect(within(boton).getByText('¿Necesitas ayuda?')).toBeInTheDocument()
    // Mascota provisional (mascota-404), decorativa: el botón ya tiene nombre.
    expect(boton.querySelector('img')).toHaveAttribute('src', '/assets/mascotas/mascota-404.png')
    expect(boton.querySelector('img')).toHaveAttribute('alt', '')

    const { panel } = await abrir()
    expect(screen.getByRole('heading', { level: 1, name: 'Vista de prueba' })).toBeInTheDocument()
    expect(within(panel).getByRole('textbox', { name: 'Escribe tu pregunta' })).toHaveFocus()
    expect(screen.getByRole('button', { name: 'Cerrar el asistente de ayuda' })).toHaveAttribute('aria-expanded', 'true')
  })

  it('saluda al estudiante con su primer nombre y primer apellido reales y la fecha actual', async () => {
    vi.useFakeTimers({ toFake: ['Date'] })
    vi.setSystemTime(new Date('2026-11-26T15:00:00-05:00'))
    renderAsistente()
    const { panel } = await abrir()
    expect(await within(panel).findByText('Hola, Estudiante De Prueba.')).toBeInTheDocument()
    expect(within(panel).getByText(/Soy tu asistente de SGT-SIAAF/)).toBeInTheDocument()
    expect(within(panel).getByText('¿En qué puedo ayudarte hoy?')).toBeInTheDocument()
    expect(within(panel).getByText('jueves, 26 de noviembre de 2026')).toHaveAttribute('datetime', '2026-11-26')
  })

  it('con funcionarios no inventa un nombre: saluda y muestra el rol', async () => {
    renderAsistente({ roles: ['DECANO'] })
    const { panel } = await abrir()
    expect(within(panel).getByText('Hola.')).toBeInTheDocument()
    expect(within(panel).getByText('Ingresaste como Decanato.')).toBeInTheDocument()
  })

  it('muestra las preguntas frecuentes del rol y responde con contenido configurado, sin llamar al servicio', async () => {
    const cliente = { consultar: vi.fn() }
    renderAsistente({ cliente })
    const { user, panel } = await abrir()
    expect(within(panel).queryByRole('button', { name: '¿Cómo uso la bandeja de expedientes?' })).not.toBeInTheDocument()

    await user.click(within(panel).getByRole('button', { name: '¿Cómo cargo un documento?' }))
    const registro = within(panel).getByRole('log')
    expect(within(registro).getByText(/archivos PDF de hasta 10 MB/)).toBeInTheDocument()
    expect(within(registro).getByRole('link', { name: 'Ir a Inicio' })).toHaveAttribute('href', '/estudiante')
    expect(cliente.consultar).not.toHaveBeenCalled()
  })

  it('sin servicio, lo informa con honestidad y el reintento vuelve a consultar de verdad', async () => {
    const consultar = vi.fn(clienteNoDisponible.consultar)
    renderAsistente({ cliente: { consultar } })
    const { user, panel } = await abrir()

    await user.type(within(panel).getByRole('textbox', { name: 'Escribe tu pregunta' }), '¿Cómo cambio mi foto?')
    await user.click(within(panel).getByRole('button', { name: 'Enviar pregunta' }))

    const registro = within(panel).getByRole('log')
    expect(within(registro).getByText('¿Cómo cambio mi foto?')).toBeInTheDocument()
    expect(await within(registro).findByText(MENSAJE_NO_DISPONIBLE)).toBeInTheDocument()
    expect(consultar).toHaveBeenCalledTimes(1)
    expect(consultar).toHaveBeenCalledWith('¿Cómo cambio mi foto?')

    await user.click(within(registro).getByRole('button', { name: 'Reintentar' }))
    await waitFor(() => expect(consultar).toHaveBeenCalledTimes(2))
    expect(await within(registro).findAllByText(MENSAJE_NO_DISPONIBLE)).toHaveLength(2)
  })

  it('remite las consultas normativas a los canales oficiales', async () => {
    renderAsistente()
    const { user, panel } = await abrir()
    await user.type(within(panel).getByRole('textbox', { name: 'Escribe tu pregunta' }), '¿Qué dice el reglamento?{Enter}')
    expect(await within(panel).findByText(MENSAJE_CANALES_OFICIALES)).toBeInTheDocument()
  })

  it('queda preparado para el servicio real: indicador de procesamiento, respuesta y fuentes', async () => {
    const { promesa, resolver } = diferida()
    renderAsistente({ cliente: { consultar: () => promesa } })
    const { user, panel } = await abrir()
    await user.type(within(panel).getByRole('textbox', { name: 'Escribe tu pregunta' }), 'Pregunta de prueba{Enter}')

    expect(within(panel).getByText('Procesando tu consulta…')).toHaveAttribute('role', 'status')
    expect(within(panel).getByRole('button', { name: 'Enviar pregunta' })).toBeDisabled()

    resolver({ texto: 'Respuesta de prueba', fuentes: [{ titulo: 'Documento de prueba', version: '2', pagina: 3, vigente: true }] })
    expect(await within(panel).findByText('Respuesta de prueba')).toBeInTheDocument()
    expect(within(panel).getByText('Fuentes consultadas')).toBeInTheDocument()
    expect(within(panel).getByText('Documento de prueba (versión 2, página 3)')).toBeInTheDocument()
    expect(within(panel).queryByText('Procesando tu consulta…')).not.toBeInTheDocument()
  })

  it('no envía preguntas vacías y limita su longitud', async () => {
    renderAsistente()
    const { panel } = await abrir()
    expect(within(panel).getByRole('button', { name: 'Enviar pregunta' })).toBeDisabled()
    expect(within(panel).getByRole('textbox', { name: 'Escribe tu pregunta' })).toHaveAttribute('maxLength', '500')
  })

  it('se cierra con Escape o con el botón de cierre, devolviendo el foco, y conserva la conversación', async () => {
    renderAsistente()
    const { user, panel } = await abrir()
    await user.click(within(panel).getByRole('button', { name: '¿Cómo me muevo por el sistema?' }))
    await user.keyboard('{Escape}')
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Abrir el asistente de ayuda' })).toHaveFocus()

    const reabierto = (await abrir()).panel
    expect(within(within(reabierto).getByRole('log')).getByText('¿Cómo me muevo por el sistema?')).toBeInTheDocument()
    await user.click(within(reabierto).getByRole('button', { name: 'Cerrar el asistente' }))
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('no presenta violaciones de accesibilidad con el chat abierto y una respuesta', async () => {
    const { container } = renderAsistente()
    const { user, panel } = await abrir()
    await user.click(within(panel).getByRole('button', { name: '¿Cómo consulto el estado de mi trámite?' }))
    expect(await axe(container)).toHaveNoViolations()
  })
})

describe('AsistenteGlobal (AX-D)', () => {
  it.each([
    ['/estudiante', ['ESTUDIANTE']],
    ['/expedientes/abc/peticiones', ['ESTUDIANTE']],
    ['/bandeja', ['DECANO']],
    ['/notificaciones', ['DECANO']],
    ['/no-habilitado', ['RESPONSABLE_DEPENDENCIA']],
  ])('aparece con sesión en la ruta principal %s', (ruta, roles) => {
    render(
      <Proveedores roles={roles} ruta={ruta}>
        <AsistenteGlobal />
      </Proveedores>,
    )
    expect(screen.getByRole('button', { name: 'Abrir el asistente de ayuda' })).toBeInTheDocument()
  })

  it.each([
    ['/login', null],
    ['/', null],
    ['/recuperar-contrasena', null],
    ['/sesion-expirada', null],
    ['/ruta-inexistente', ['ESTUDIANTE']],
    ['/estudiantes-falso', ['ESTUDIANTE']],
  ])('no aparece en %s', (ruta, roles) => {
    render(
      <Proveedores roles={roles} ruta={ruta}>
        <AsistenteGlobal />
      </Proveedores>,
    )
    expect(screen.queryByRole('button', { name: 'Abrir el asistente de ayuda' })).not.toBeInTheDocument()
  })
})
