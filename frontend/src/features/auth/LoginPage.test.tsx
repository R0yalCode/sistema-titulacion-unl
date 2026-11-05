import { HttpResponse, http } from 'msw'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { AuthProvider } from '@/auth/AuthContext'
import { getAccessToken } from '@/auth/storage'
import { ToastProvider } from '@/components/feedback/ToastProvider'
import { MemoryRouter } from 'react-router-dom'
import { server } from '@/test/server'
import { AppRouter } from '@/app/router'

const TOKEN_URL = '*/api/v1/auth/token/'

function base64UrlEncode(value: string): string {
  return btoa(value).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
}

function buildToken(payload: Record<string, unknown>): string {
  const header = base64UrlEncode(JSON.stringify({ alg: 'HS256', typ: 'JWT' }))
  const body = base64UrlEncode(JSON.stringify(payload))
  return `${header}.${body}.fixture-signature`
}

function renderAppAt(route: string) {
  return render(
    <MemoryRouter initialEntries={[route]}>
      <AuthProvider>
        <ToastProvider>
          <AppRouter />
        </ToastProvider>
      </AuthProvider>
    </MemoryRouter>,
  )
}

async function fillAndSubmit(username: string, password: string) {
  const user = userEvent.setup()
  await user.type(await screen.findByLabelText(/^Usuario/), username)
  await user.type(screen.getByLabelText(/^Contraseña/), password)
  await user.click(screen.getByRole('button', { name: 'Ingresar' }))
}

describe('LoginPage (V-01, integración real)', () => {
  afterEach(() => {
    sessionStorage.clear()
  })

  it('CA-V01-01: credenciales válidas redirigen al inicio del rol y persisten el access token', async () => {
    renderAppAt('/login')

    await fillAndSubmit('estudiante.demo', 'demo-valida')

    expect(await screen.findByRole('heading', { name: 'Dashboard del estudiante (V-02)' })).toBeInTheDocument()
    expect(getAccessToken()).not.toBeNull()
  })

  it('redirige a /bandeja cuando el rol real obtenido es operativo', async () => {
    server.use(
      http.post(TOKEN_URL, () =>
        HttpResponse.json(
          {
            access: buildToken({ cedula: '1104567890', roles: ['DECANO'], exp: Math.floor(Date.now() / 1000) + 3600 }),
            refresh: 'fixture-refresh-no-se-persiste',
          },
          { status: 200 },
        ),
      ),
    )

    renderAppAt('/login')
    await fillAndSubmit('decano.demo', 'cualquiera')

    expect(await screen.findByRole('heading', { name: 'Bandeja del funcionario (V-07)' })).toBeInTheDocument()
  })

  it('CA-V01-02: credenciales inválidas (401) muestran un mensaje genérico, permanece en /login y no dispara el cierre de sesión global (P2-3)', async () => {
    renderAppAt('/login')

    await fillAndSubmit('incorrecto', 'incorrecto')

    expect(await screen.findByRole('alert')).toHaveTextContent('Usuario o contraseña incorrectos.')
    expect(screen.getByRole('heading', { name: 'Iniciar sesión' })).toBeInTheDocument()
    expect(getAccessToken()).toBeNull()
    // Si el 401 del login disparara el manejador global (sin skipAuthHandler),
    // se mostraría este aviso de expiración; su ausencia confirma P2-3.
    expect(screen.queryByText('Su sesión ha expirado. Inicie sesión nuevamente.')).not.toBeInTheDocument()
  })

  it('muestra un mensaje de validación ante un 400 del backend', async () => {
    server.use(
      http.post(TOKEN_URL, () =>
        HttpResponse.json({ non_field_errors: ['Debe proporcionar usuario y contraseña.'] }, { status: 400 }),
      ),
    )

    renderAppAt('/login')
    await fillAndSubmit('estudiante.demo', 'demo-valida')

    expect(await screen.findByRole('alert')).toHaveTextContent('Debe proporcionar usuario y contraseña.')
  })

  it('muestra un mensaje de acceso restringido ante un 403', async () => {
    server.use(http.post(TOKEN_URL, () => HttpResponse.json({ detail: 'Cuenta inactiva.' }, { status: 403 })))

    renderAppAt('/login')
    await fillAndSubmit('estudiante.demo', 'demo-valida')

    expect(await screen.findByRole('alert')).toHaveTextContent('No tiene permisos para iniciar sesión con esta cuenta.')
  })

  it('muestra un mensaje genérico ante un código de estado no mapeado', async () => {
    server.use(http.post(TOKEN_URL, () => HttpResponse.json({ detail: 'Conflicto.' }, { status: 409 })))

    renderAppAt('/login')
    await fillAndSubmit('estudiante.demo', 'demo-valida')

    expect(await screen.findByRole('alert')).toHaveTextContent('No se pudo iniciar sesión. Intente nuevamente.')
  })

  it('muestra un mensaje genérico si el backend devuelve un access token inválido', async () => {
    server.use(
      http.post(TOKEN_URL, () =>
        HttpResponse.json({ access: 'token-invalido', refresh: 'fixture-refresh-no-se-persiste' }, { status: 200 }),
      ),
    )

    renderAppAt('/login')
    await fillAndSubmit('estudiante.demo', 'demo-valida')

    expect(await screen.findByRole('alert')).toHaveTextContent('No se pudo iniciar sesión. Intente nuevamente.')
    expect(getAccessToken()).toBeNull()
  })

  it('CA-V01-03a: muestra un mensaje de error del servidor ante un 500 y permite reintentar', async () => {
    let attempts = 0
    server.use(
      http.post(TOKEN_URL, () => {
        attempts += 1
        if (attempts === 1) {
          return HttpResponse.json({ detail: 'Error interno.' }, { status: 500 })
        }
        return HttpResponse.json(
          {
            access: buildToken({ cedula: '1104567890', roles: ['ESTUDIANTE'], exp: Math.floor(Date.now() / 1000) + 3600 }),
            refresh: 'fixture-refresh-no-se-persiste',
          },
          { status: 200 },
        )
      }),
    )

    renderAppAt('/login')
    await fillAndSubmit('estudiante.demo', 'demo-valida')
    expect(await screen.findByRole('alert')).toHaveTextContent(/problema al procesar/i)

    await fillAndSubmit('estudiante.demo', 'demo-valida')
    expect(await screen.findByRole('heading', { name: 'Dashboard del estudiante (V-02)' })).toBeInTheDocument()
    expect(attempts).toBe(2)
  })

  it('CA-V01-03b: muestra un estado de error ante una falla de red', async () => {
    server.use(http.post(TOKEN_URL, () => HttpResponse.error()))

    renderAppAt('/login')
    await fillAndSubmit('estudiante.demo', 'demo-valida')

    expect(await screen.findByRole('alert')).toHaveTextContent(/servicio no está disponible/i)
  })

  it('muestra el indicador de carga mientras la petición está en curso', async () => {
    server.use(
      http.post(TOKEN_URL, async () => {
        await new Promise((resolve) => setTimeout(resolve, 50))
        return HttpResponse.json(
          {
            access: buildToken({ cedula: '1104567890', roles: ['ESTUDIANTE'], exp: Math.floor(Date.now() / 1000) + 3600 }),
            refresh: 'fixture-refresh-no-se-persiste',
          },
          { status: 200 },
        )
      }),
    )

    renderAppAt('/login')
    await fillAndSubmit('estudiante.demo', 'demo-valida')

    expect(screen.getByRole('button', { name: 'Ingresar' })).toHaveAttribute('aria-busy', 'true')
    await waitFor(() => expect(screen.getByRole('button', { name: 'Ingresar' })).toBeDisabled())

    expect(await screen.findByRole('heading', { name: 'Dashboard del estudiante (V-02)' })).toBeInTheDocument()
  })

  it('CA-V01-05: el logout local borra el token y vuelve a /login', async () => {
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true)
    const user = userEvent.setup()
    renderAppAt('/login')

    await fillAndSubmit('estudiante.demo', 'demo-valida')
    expect(await screen.findByRole('heading', { name: 'Dashboard del estudiante (V-02)' })).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Cerrar sesión' }))

    expect(await screen.findByRole('heading', { name: 'Iniciar sesión' })).toBeInTheDocument()
    expect(getAccessToken()).toBeNull()
    confirmSpy.mockRestore()
  })

  it('CA-V01-04: con sesión activa, visitar /login redirige al inicio por rol', async () => {
    sessionStorage.setItem(
      'sgt.access',
      buildToken({ cedula: '1104567890', roles: ['ESTUDIANTE'], exp: Math.floor(Date.now() / 1000) + 3600 }),
    )

    renderAppAt('/login')

    expect(await screen.findByRole('heading', { name: 'Dashboard del estudiante (V-02)' })).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Iniciar sesión' })).not.toBeInTheDocument()
  })

  it('no presenta violaciones de accesibilidad en el estado inicial', async () => {
    const { container } = renderAppAt('/login')
    await screen.findByRole('heading', { name: 'Iniciar sesión' })

    expect(await axe(container)).toHaveNoViolations()
  })
})
