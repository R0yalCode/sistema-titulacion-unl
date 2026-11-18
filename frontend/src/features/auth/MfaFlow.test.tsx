import { HttpResponse, http } from 'msw'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'
import { afterEach, describe, expect, it } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import { AuthProvider } from '@/auth/AuthContext'
import { getAccessToken } from '@/auth/storage'
import { ToastProvider } from '@/components/feedback/ToastProvider'
import { AppRouter } from '@/app/router'
import { fixtureMfaChallenge, fixtureRecoveryCodes } from '@/mocks/fixtures'
import { server } from '@/test/server'

// Pruebas de seguridad del ingreso con segundo factor (AUTH-D).

const MFA_VERIFY_URL = '*/api/v1/auth/mfa/verify/'
const MFA_SETUP_CONFIRM_URL = '*/api/v1/auth/mfa/setup/confirm/'
const [FIRST_RECOVERY_CODE = ''] = fixtureRecoveryCodes

function renderAppAt(route: string) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[route]}>
        <AuthProvider>
          <ToastProvider>
            <AppRouter />
          </ToastProvider>
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

async function loginAs(username: string) {
  const user = userEvent.setup()
  await user.type(await screen.findByLabelText(/^Usuario/), username)
  await user.type(screen.getByLabelText(/^Contraseña/), 'demo-valida')
  await user.click(screen.getByRole('button', { name: 'Ingresar' }))
  return user
}

function storageContains(value: string): boolean {
  const all = [...Object.values({ ...sessionStorage }), ...Object.values({ ...localStorage })]
  return all.some((item) => String(item).includes(value))
}

describe('Ingreso con segundo factor (AUTH-D)', () => {
  afterEach(() => {
    sessionStorage.clear()
    localStorage.clear()
  })

  it('registro: muestra el QR, rechaza un código erróneo y activa con el correcto', async () => {
    renderAppAt('/login')
    const user = await loginAs('mfa.registro')

    expect(await screen.findByRole('heading', { name: 'Configurar verificación en dos pasos' })).toBeInTheDocument()
    expect(await screen.findByRole('img', { name: /Código QR/ })).toHaveAttribute(
      'src',
      expect.stringMatching(/^data:image\/svg\+xml/),
    )
    // Antes de completar el segundo factor no hay sesión ni reto persistido.
    expect(getAccessToken()).toBeNull()
    expect(storageContains(fixtureMfaChallenge.challenge)).toBe(false)

    const codeField = screen.getByLabelText(/Código de 6 dígitos/)
    await user.type(codeField, '000000')
    await user.click(screen.getByRole('button', { name: 'Verificar y activar' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('El código no es válido')
    expect(codeField).toHaveValue('')

    await user.type(codeField, '123456')
    await user.click(screen.getByRole('button', { name: 'Verificar y activar' }))

    expect(await screen.findByRole('heading', { name: 'Códigos de recuperación' })).toBeInTheDocument()
    for (const code of fixtureRecoveryCodes) {
      expect(screen.getByText(code)).toBeInTheDocument()
    }
    // El token no se guarda hasta confirmar que se guardaron los códigos.
    expect(getAccessToken()).toBeNull()
    const continuar = screen.getByRole('button', { name: 'Continuar al sistema' })
    expect(continuar).toBeDisabled()
    await user.click(screen.getByLabelText(/Guardé mis códigos/))
    await user.click(continuar)

    expect(await screen.findByRole('heading', { name: 'Dashboard del estudiante (V-02)' })).toBeInTheDocument()
    expect(getAccessToken()).not.toBeNull()
    expect(storageContains(FIRST_RECOVERY_CODE)).toBe(false)
  })

  it('el campo del código solo acepta 6 dígitos y exige completarlo', async () => {
    renderAppAt('/login')
    const user = await loginAs('mfa.verificar')

    const codeField = await screen.findByLabelText(/Código de 6 dígitos/)
    await user.type(codeField, '12a34 5678')
    expect(codeField).toHaveValue('123456')
    await user.clear(codeField)
    await user.type(codeField, '123')
    await user.click(screen.getByRole('button', { name: 'Verificar' }))
    expect(await screen.findByText('Ingrese los 6 dígitos del código.')).toBeInTheDocument()
  })

  it('verificación: pide el código y solo entonces redirige al inicio del rol', async () => {
    renderAppAt('/login')
    const user = await loginAs('mfa.verificar')

    expect(await screen.findByRole('heading', { name: 'Verificación de seguridad (2FA)' })).toBeInTheDocument()
    expect(getAccessToken()).toBeNull()

    await user.type(screen.getByLabelText(/Código de 6 dígitos/), '123456')
    await user.click(screen.getByRole('button', { name: 'Verificar' }))

    expect(await screen.findByRole('heading', { name: 'Dashboard del estudiante (V-02)' })).toBeInTheDocument()
  })

  it('envía trust_device solo si el usuario marca la confianza del dispositivo', async () => {
    const bodies: unknown[] = []
    server.use(
      http.post(MFA_VERIFY_URL, async ({ request }) => {
        bodies.push(await request.json())
        return HttpResponse.json({ detail: 'x', code: 'codigo_mfa_invalido' }, { status: 400 })
      }),
    )
    renderAppAt('/login')
    const user = await loginAs('mfa.verificar')
    const codeField = await screen.findByLabelText(/Código de 6 dígitos/)

    await user.type(codeField, '111111')
    await user.click(screen.getByRole('button', { name: 'Verificar' }))
    await screen.findByRole('alert')
    await user.click(screen.getByLabelText('Confiar en este dispositivo durante 5 días'))
    await user.type(codeField, '222222')
    await user.click(screen.getByRole('button', { name: 'Verificar' }))

    await waitFor(() => expect(bodies).toHaveLength(2))
    expect(bodies[0]).toMatchObject({ code: '111111', trust_device: false })
    expect(bodies[1]).toMatchObject({ code: '222222', trust_device: true })
  })

  it('un reto caducado devuelve a credenciales con un mensaje claro', async () => {
    server.use(
      http.post(MFA_VERIFY_URL, () =>
        HttpResponse.json({ detail: 'caducó', code: 'reto_mfa_invalido' }, { status: 400 }),
      ),
    )
    renderAppAt('/login')
    const user = await loginAs('mfa.verificar')
    await user.type(await screen.findByLabelText(/Código de 6 dígitos/), '123456')
    await user.click(screen.getByRole('button', { name: 'Verificar' }))

    expect(await screen.findByRole('heading', { name: 'Ingreso' })).toBeInTheDocument()
    expect(screen.getByRole('alert')).toHaveTextContent('La verificación caducó o ya no es válida')
    expect(getAccessToken()).toBeNull()
  })

  it('el bloqueo por intentos se comunica sin revelar detalles', async () => {
    server.use(
      http.post(MFA_VERIFY_URL, () =>
        HttpResponse.json({ detail: 'bloqueado', code: 'mfa_bloqueado' }, { status: 429 }),
      ),
    )
    renderAppAt('/login')
    const user = await loginAs('mfa.verificar')
    await user.type(await screen.findByLabelText(/Código de 6 dígitos/), '123456')
    await user.click(screen.getByRole('button', { name: 'Verificar' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Demasiados intentos fallidos de verificación')
  })

  it('un código de recuperación lleva a registrar un autenticador nuevo', async () => {
    renderAppAt('/login')
    const user = await loginAs('mfa.verificar')
    await user.click(await screen.findByRole('button', { name: /Use un código de recuperación/ }))
    await user.type(screen.getByLabelText(/Código de recuperación/), FIRST_RECOVERY_CODE.toLowerCase())
    await user.click(screen.getByRole('button', { name: 'Usar código de recuperación' }))

    expect(await screen.findByRole('heading', { name: 'Configurar verificación en dos pasos' })).toBeInTheDocument()
    expect(getAccessToken()).toBeNull()
  })

  it('cancelar el segundo factor vuelve al formulario sin sesión', async () => {
    renderAppAt('/login')
    const user = await loginAs('mfa.verificar')
    await user.click(await screen.findByRole('button', { name: 'Cancelar' }))

    expect(await screen.findByRole('heading', { name: 'Ingreso' })).toBeInTheDocument()
    expect(getAccessToken()).toBeNull()
  })

  it('el paso de registro no presenta violaciones de accesibilidad', async () => {
    server.use(http.post(MFA_SETUP_CONFIRM_URL, () => HttpResponse.json({}, { status: 500 })))
    const { container } = renderAppAt('/login')
    await loginAs('mfa.registro')
    await screen.findByRole('img', { name: /Código QR/ })

    expect(await axe(container)).toHaveNoViolations()
  })
})
