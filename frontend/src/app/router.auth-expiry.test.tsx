import { HttpResponse, http } from 'msw'
import { afterEach, describe, expect, it } from 'vitest'
import { AuthProvider } from '@/auth/AuthContext'
import { request } from '@/api/client'
import { server } from '@/test/server'
import { renderWithProviders } from '@/test/renderWithProviders'
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
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

describe('expiración de sesión (401 global)', () => {
  afterEach(() => {
    sessionStorage.clear()
  })

  it('un 401 en cualquier petición limpia la sesión y muestra la vista 401 (DEC-17)', async () => {
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

    expect(await screen.findByRole('heading', { name: 'Mi proceso de titulación' })).toBeInTheDocument()

    await expect(request('/api/v1/test-expiry/')).rejects.toBeDefined()

    expect(await screen.findByRole('heading', { level: 1, name: 'Necesitas iniciar sesión' })).toBeInTheDocument()
    expect(getAccessToken()).toBeNull()

    // «Iniciar sesión» lleva al login real.
    await userEvent.setup().click(screen.getByRole('button', { name: 'Iniciar sesión' }))
    expect(await screen.findByRole('heading', { name: 'Iniciar sesión' })).toBeInTheDocument()
  })

  it('varios 401 seguidos no provocan bucles ni salen de la vista 401', async () => {
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

    expect(await screen.findByRole('heading', { name: 'Mi proceso de titulación' })).toBeInTheDocument()

    await Promise.all([
      expect(request('/api/v1/test-expiry/')).rejects.toBeDefined(),
      expect(request('/api/v1/test-expiry/')).rejects.toBeDefined(),
    ])
    expect(await screen.findByRole('heading', { level: 1, name: 'Necesitas iniciar sesión' })).toBeInTheDocument()

    // Un 401 tardío estando ya en la vista no vuelve a navegar.
    await expect(request('/api/v1/test-expiry/')).rejects.toBeDefined()
    expect(screen.getByRole('heading', { level: 1, name: 'Necesitas iniciar sesión' })).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Iniciar sesión' })).not.toBeInTheDocument()
  })

  it('FE-T1001: un 401 justo después de pintar el dashboard nunca se pierde', async () => {
    for (let intento = 0; intento < 5; intento += 1) {
      sessionStorage.setItem(
        'sgt.access',
        buildToken({ cedula: '1104567890', roles: ['ESTUDIANTE'], exp: Math.floor(Date.now() / 1000) + 3600 }),
      )
      server.use(http.get(EXPIRING_URL, () => HttpResponse.json({ detail: 'Token expirado.' }, { status: 401 })))
      const { unmount } = renderWithProviders(
        <AuthProvider>
          <ToastProvider>
            <AppRouter />
          </ToastProvider>
        </AuthProvider>,
        { route: '/estudiante' },
      )

      await screen.findByRole('heading', { name: 'Mi proceso de titulación' })
      await expect(request('/api/v1/test-expiry/')).rejects.toBeDefined()

      expect(await screen.findByRole('heading', { level: 1, name: 'Necesitas iniciar sesión' })).toBeInTheDocument()
      expect(getAccessToken()).toBeNull()
      unmount()
    }
  })
})

