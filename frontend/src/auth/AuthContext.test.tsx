import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { AuthProvider } from './AuthContext'
import { clearAccessToken, getAccessToken } from './storage'
import { useAuth } from './useAuth'

function base64UrlEncode(value: string): string {
  return btoa(value).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
}

function buildToken(payload: Record<string, unknown>): string {
  const header = base64UrlEncode(JSON.stringify({ alg: 'HS256', typ: 'JWT' }))
  const body = base64UrlEncode(JSON.stringify(payload))
  return `${header}.${body}.fixture-signature`
}

const validToken = buildToken({
  cedula: '1104567890',
  roles: ['ESTUDIANTE'],
  exp: Math.floor(Date.now() / 1000) + 3600,
})

function Consumer() {
  const auth = useAuth()

  return (
    <div>
      <p>Autenticado: {String(auth.isAuthenticated)}</p>
      <p>Cédula: {auth.user?.cedula ?? 'ninguna'}</p>
      <button type="button" onClick={() => auth.login({ access: validToken, refresh: 'no-se-persiste' })}>
        Iniciar sesión
      </button>
      <button type="button" onClick={auth.logout}>
        Cerrar sesión
      </button>
    </div>
  )
}

describe('AuthProvider / useAuth', () => {
  afterEach(() => {
    sessionStorage.clear()
  })

  it('arranca sin sesión cuando no hay token guardado', () => {
    render(
      <AuthProvider>
        <Consumer />
      </AuthProvider>,
    )

    expect(screen.getByText('Autenticado: false')).toBeInTheDocument()
  })

  it('login actualiza el estado, la UI y persiste el access token', async () => {
    const user = userEvent.setup()
    render(
      <AuthProvider>
        <Consumer />
      </AuthProvider>,
    )

    await user.click(screen.getByRole('button', { name: 'Iniciar sesión' }))

    expect(screen.getByText('Autenticado: true')).toBeInTheDocument()
    expect(screen.getByText('Cédula: 1104567890')).toBeInTheDocument()
    expect(getAccessToken()).toBe(validToken)
  })

  it('logout limpia el estado y el storage', async () => {
    const user = userEvent.setup()
    render(
      <AuthProvider>
        <Consumer />
      </AuthProvider>,
    )

    await user.click(screen.getByRole('button', { name: 'Iniciar sesión' }))
    await user.click(screen.getByRole('button', { name: 'Cerrar sesión' }))

    expect(screen.getByText('Autenticado: false')).toBeInTheDocument()
    expect(getAccessToken()).toBeNull()
  })

  it('restaura la sesión desde sessionStorage al montar', () => {
    sessionStorage.setItem('sgt.access', validToken)

    render(
      <AuthProvider>
        <Consumer />
      </AuthProvider>,
    )

    expect(screen.getByText('Autenticado: true')).toBeInTheDocument()
    clearAccessToken()
  })

  it('useAuth lanza un error fuera de AuthProvider', () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => undefined)
    function Broken() {
      useAuth()
      return null
    }

    expect(() => render(<Broken />)).toThrow('useAuth debe usarse dentro de un AuthProvider.')
    consoleSpy.mockRestore()
  })
})
