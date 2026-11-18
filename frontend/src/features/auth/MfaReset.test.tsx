import { HttpResponse, http } from 'msw'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'
import { describe, expect, it } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { server } from '@/test/server'
import MfaResetConfirmPage from './MfaResetConfirmPage'
import MfaResetRequestPage from './MfaResetRequestPage'

const MFA_RESET_URL = '*/api/v1/auth/mfa/reset/'

function renderAt(route: string) {
  return render(
    <MemoryRouter initialEntries={[route]}>
      <Routes>
        <Route element={<MfaResetRequestPage />} path="/restablecer-2fa" />
        <Route element={<MfaResetConfirmPage />} path="/restablecer-2fa/confirmar" />
        <Route element={<h1>Pantalla de ingreso</h1>} path="/login" />
      </Routes>
    </MemoryRouter>,
  )
}

async function fill(user: ReturnType<typeof userEvent.setup>, email: string, cedula = '1100000002') {
  await user.type(screen.getByLabelText(/^Correo institucional/), email)
  await user.type(screen.getByLabelText(/^Número de cédula/), cedula)
  await user.type(screen.getByLabelText(/^Contraseña actual/), 'clave')
  await user.click(screen.getByRole('button', { name: 'Restablecer el doble factor de autenticación (2FA)' }))
}

describe('Restablecimiento del 2FA (MFA-RST)', () => {
  it('reproduce la estructura de la referencia institucional', () => {
    renderAt('/restablecer-2fa')

    expect(
      screen.getByRole('heading', { level: 1, name: 'Restablecimiento de doble factor de autenticación (2FA)' }),
    ).toBeInTheDocument()
    expect(screen.getByText(/Valide su identidad/)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Restablecer contraseña' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Regresar al inicio' })).toBeInTheDocument()
    expect(screen.getByText(/vigencia limitada/)).toBeInTheDocument()
  })

  it('exige los tres datos y un correo @unl.edu.ec', async () => {
    let calls = 0
    server.use(
      http.post(MFA_RESET_URL, () => {
        calls += 1
        return HttpResponse.json({ detail: 'x' })
      }),
    )
    const user = userEvent.setup()
    renderAt('/restablecer-2fa')

    await user.click(screen.getByRole('button', { name: 'Restablecer el doble factor de autenticación (2FA)' }))
    expect(screen.getByText('El correo institucional es un campo requerido.')).toBeInTheDocument()
    expect(screen.getByText('El número de cédula es un campo requerido.')).toBeInTheDocument()
    expect(screen.getByText('La contraseña es un campo requerido.')).toBeInTheDocument()

    await user.type(screen.getByLabelText(/^Correo institucional/), 'alguien@gmail.com')
    expect(screen.getByText('Ingrese un correo institucional válido (@unl.edu.ec).')).toBeInTheDocument()
    expect(calls).toBe(0)
  })

  it('envía datos normalizados y muestra la respuesta genérica', async () => {
    let body: unknown = null
    server.use(
      http.post(MFA_RESET_URL, async ({ request }) => {
        body = await request.json()
        return HttpResponse.json({ detail: 'Si los datos corresponden a una cuenta…' })
      }),
    )
    const user = userEvent.setup()
    renderAt('/restablecer-2fa')

    await fill(user, '  Estudiante@UNL.EDU.EC ')

    expect(await screen.findByText('Revise su correo')).toBeInTheDocument()
    expect(screen.getByText('Si los datos corresponden a una cuenta…')).toBeInTheDocument()
    expect(body).toEqual({ email: 'estudiante@unl.edu.ec', cedula: '1100000002', password: 'clave' })
  })

  it('el límite de solicitudes se comunica sin detalles', async () => {
    server.use(http.post(MFA_RESET_URL, () => HttpResponse.json({ detail: 'x' }, { status: 429 })))
    const user = userEvent.setup()
    renderAt('/restablecer-2fa')

    await fill(user, 'estudiante@unl.edu.ec')

    expect(await screen.findByRole('alert')).toHaveTextContent('Demasiados intentos')
  })

  it('confirmar un enlace válido exige pulsar el botón y luego invita a iniciar sesión', async () => {
    const user = userEvent.setup()
    renderAt('/restablecer-2fa/confirmar?uid=abc&token=token-valido')

    expect(screen.queryByText('Doble factor restablecido')).not.toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Confirmar restablecimiento' }))

    expect(await screen.findByText('Doble factor restablecido')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Iniciar sesión' })).toHaveAttribute('href', '/login')
  })

  it('un enlace usado o caducado ofrece solicitar otro', async () => {
    const user = userEvent.setup()
    renderAt('/restablecer-2fa/confirmar?uid=abc&token=usado')

    await user.click(screen.getByRole('button', { name: 'Confirmar restablecimiento' }))

    await waitFor(() => expect(screen.getByText('Enlace no válido')).toBeInTheDocument())
    expect(screen.getByRole('link', { name: 'Solicitar un nuevo enlace' })).toBeInTheDocument()
  })

  it('un enlace sin parámetros es inválido', () => {
    renderAt('/restablecer-2fa/confirmar')

    expect(screen.getByText('Enlace no válido')).toBeInTheDocument()
  })

  it('no presenta violaciones de accesibilidad', async () => {
    const { container } = renderAt('/restablecer-2fa')

    expect(await axe(container)).toHaveNoViolations()
  })
})
