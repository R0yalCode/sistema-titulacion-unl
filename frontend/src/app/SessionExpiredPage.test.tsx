import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom'
import { axe } from 'vitest-axe'
import { describe, expect, it } from 'vitest'
import SessionExpiredPage from './SessionExpiredPage'
import { marcarSesionExpirada, rutaDeRetorno, sesionExpiradaPendiente } from '@/auth/sessionExpiry'

function LoginStub() {
  const location = useLocation()
  const state = location.state as { returnTo?: string } | null
  return <p>Login real · retorno: {state?.returnTo ?? 'ninguno'}</p>
}

function renderVista(state?: unknown) {
  return render(
    <MemoryRouter initialEntries={[{ pathname: '/sesion-expirada', state }]}>
      <Routes>
        <Route element={<SessionExpiredPage />} path="/sesion-expirada" />
        <Route element={<LoginStub />} path="/login" />
        <Route element={<p>Página pública</p>} path="/" />
      </Routes>
    </MemoryRouter>,
  )
}

describe('rutaDeRetorno', () => {
  it('acepta solo rutas internas y descarta la propia vista y el login', () => {
    expect(rutaDeRetorno('/estudiante')).toBe('/estudiante')
    expect(rutaDeRetorno('//evil.example')).toBeNull()
    expect(rutaDeRetorno('https://evil.example')).toBeNull()
    expect(rutaDeRetorno('/sesion-expirada')).toBeNull()
    expect(rutaDeRetorno('/login')).toBeNull()
    expect(rutaDeRetorno(42)).toBeNull()
  })
})

describe('SessionExpiredPage (401)', () => {
  it('explica que debe iniciar sesión, sin campos de contraseña', async () => {
    const { container } = renderVista()
    expect(screen.getByRole('heading', { level: 1, name: 'Necesitas iniciar sesión' })).toBeInTheDocument()
    expect(container.querySelector('input')).toBeNull()
    expect(await axe(container)).toHaveNoViolations()
  })

  it('«Iniciar sesión» abre el login real y conserva la ruta de retorno', async () => {
    const user = userEvent.setup()
    renderVista({ returnTo: '/estudiante/perfil' })
    await user.click(screen.getByRole('button', { name: 'Iniciar sesión' }))
    expect(screen.getByText('Login real · retorno: /estudiante/perfil')).toBeInTheDocument()
  })

  it('descarta un retorno externo o circular', async () => {
    const user = userEvent.setup()
    renderVista({ returnTo: '//evil.example' })
    await user.click(screen.getByRole('button', { name: 'Iniciar sesión' }))
    expect(screen.getByText('Login real · retorno: ninguno')).toBeInTheDocument()
  })

  it('«Ir al inicio» lleva a la página pública', async () => {
    const user = userEvent.setup()
    renderVista()
    await user.click(screen.getByRole('button', { name: 'Ir al inicio' }))
    expect(screen.getByText('Página pública')).toBeInTheDocument()
  })

  it('un 401 tardío con la vista abierta no deja la marca activa al salir', async () => {
    const user = userEvent.setup()
    renderVista()
    marcarSesionExpirada()
    expect(sesionExpiradaPendiente()).toBe(true)
    await user.click(screen.getByRole('button', { name: 'Ir al inicio' }))
    expect(screen.getByText('Página pública')).toBeInTheDocument()
    expect(sesionExpiradaPendiente()).toBe(false)
  })
})
