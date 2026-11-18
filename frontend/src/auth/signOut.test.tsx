import { HttpResponse, http } from 'msw'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it } from 'vitest'
import { AuthProvider } from './AuthContext'
import { getAccessToken } from './storage'
import { useAuth } from './useAuth'
import { fixtureTokenPair } from '@/mocks/fixtures'
import { server } from '@/test/server'

// AUTH-D: política aprobada el 2026-11-18 — todo cierre de sesión pedido por
// el usuario revoca en el servidor la confianza del dispositivo; la
// expiración del JWT (logout local) no la revoca.

const LOGOUT_URL = '*/api/v1/auth/logout/'

function Consumer() {
  const auth = useAuth()
  return (
    <div>
      <p>Autenticado: {String(auth.isAuthenticated)}</p>
      <button type="button" onClick={() => auth.login(fixtureTokenPair)}>
        Entrar
      </button>
      <button type="button" onClick={auth.signOut}>
        Salir
      </button>
      <button type="button" onClick={auth.logout}>
        Expirar
      </button>
    </div>
  )
}

function renderConsumer() {
  render(
    <AuthProvider>
      <Consumer />
    </AuthProvider>,
  )
}

describe('signOut (AUTH-D)', () => {
  afterEach(() => {
    sessionStorage.clear()
  })

  it('cierra la sesión local y pide al servidor revocar la confianza del dispositivo', async () => {
    let calls = 0
    server.use(
      http.post(LOGOUT_URL, () => {
        calls += 1
        return HttpResponse.json({ detail: 'Sesión cerrada.' })
      }),
    )
    const user = userEvent.setup()
    renderConsumer()
    await user.click(screen.getByRole('button', { name: 'Entrar' }))
    await user.click(screen.getByRole('button', { name: 'Salir' }))

    expect(screen.getByText('Autenticado: false')).toBeInTheDocument()
    expect(getAccessToken()).toBeNull()
    await waitFor(() => expect(calls).toBe(1))
  })

  it('si el servidor no responde, la sesión local se cierra igualmente', async () => {
    server.use(http.post(LOGOUT_URL, () => HttpResponse.error()))
    const user = userEvent.setup()
    renderConsumer()
    await user.click(screen.getByRole('button', { name: 'Entrar' }))
    await user.click(screen.getByRole('button', { name: 'Salir' }))

    expect(screen.getByText('Autenticado: false')).toBeInTheDocument()
  })

  it('la expiración (logout local) no revoca la confianza del dispositivo', async () => {
    let calls = 0
    server.use(
      http.post(LOGOUT_URL, () => {
        calls += 1
        return HttpResponse.json({ detail: 'Sesión cerrada.' })
      }),
    )
    const user = userEvent.setup()
    renderConsumer()
    await user.click(screen.getByRole('button', { name: 'Entrar' }))
    await user.click(screen.getByRole('button', { name: 'Expirar' }))

    expect(screen.getByText('Autenticado: false')).toBeInTheDocument()
    await new Promise((resolve) => setTimeout(resolve, 20))
    expect(calls).toBe(0)
  })
})
