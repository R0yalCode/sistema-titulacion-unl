import { HttpResponse, http } from 'msw'
import { afterEach, describe, expect, it } from 'vitest'
import { AuthProvider } from '@/auth/AuthContext'
import { request } from '@/api/client'
import { server } from '@/test/server'
import { renderWithProviders } from '@/test/renderWithProviders'
import { screen } from '@testing-library/react'
import { getAccessToken } from '@/auth/storage'
import { ToastProvider } from '@/components/feedback/ToastProvider'
import { AppRouter } from './router'

function base64UrlEncode(value: string): string {
  return btoa(value).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
}

function buildToken(payload: Record<string, unknown>): string {
  const header = base64UrlEncode(JSON.stringify({ alg: 'HS256', typ: 'JWT' }))
  const body = base64UrlEncode(JSON.stringify(payload))
  return `${header}.${body}.fixture-signature`
}

const EXPIRING_URL = 'http://localhost:8000/api/v1/test-expiry/'

/**
 * FE-T1001/FE-T1008: archivo propio a propósito. Vitest aísla los módulos por
 * archivo, así que aquí la ruta lazy del dashboard **todavía no está cargada**
 * (en el otro archivo, `lazy()` ya la tiene en caché y la carrera no se da).
 */
describe('expiración de sesión durante la inicialización (401 global)', () => {
  afterEach(() => {
    sessionStorage.clear()
  })

  it('FE-T1001: un 401 que llega mientras la ruta lazy todavía carga también cierra la sesión', async () => {
    sessionStorage.setItem(
      'sgt.access',
      buildToken({ cedula: '1104567890', roles: ['ESTUDIANTE'], exp: Math.floor(Date.now() / 1000) + 3600 }),
    )
    server.use(http.get(EXPIRING_URL, () => HttpResponse.json({ detail: 'Token expirado.' }, { status: 401 })))

    renderWithProviders(
      <AuthProvider>
        <ToastProvider>
          <AppRouter />
        </ToastProvider>
      </AuthProvider>,
      { route: '/estudiante' },
    )

    // Sin esperar al dashboard: la ruta lazy aún no se ha resuelto (condición de carrera de la inicialización).
    await expect(request('/api/v1/test-expiry/')).rejects.toBeDefined()

    expect(await screen.findByRole('heading', { name: 'Iniciar sesión' })).toBeInTheDocument()
    expect(getAccessToken()).toBeNull()
  })
})
