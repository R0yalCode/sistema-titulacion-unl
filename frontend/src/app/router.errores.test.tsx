import { HttpResponse, http } from 'msw'
import { screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import { AuthProvider } from '@/auth/AuthContext'
import { limpiarSesionExpirada } from '@/auth/sessionExpiry'
import { getAccessToken } from '@/auth/storage'
import { ToastProvider } from '@/components/feedback/ToastProvider'
import { server } from '@/test/server'
import { renderWithProviders } from '@/test/renderWithProviders'
import { AppRouter } from './router'

/**
 * Integración del sistema de errores (ER-E): comprueba, con el router, el
 * AuthProvider y el cliente HTTP reales, que cada error se atiende en su
 * nivel y que ninguno se convierte en otro.
 */

const DETALLE_URL = '*/api/v1/expedientes/:id/'
const ID = '33333333-3333-3333-3333-333333333333'

function base64UrlEncode(value: string): string {
  return btoa(value).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
}

function iniciarSesion(roles: string[]) {
  const header = base64UrlEncode(JSON.stringify({ alg: 'HS256', typ: 'JWT' }))
  const body = base64UrlEncode(JSON.stringify({ cedula: '1104567890', roles, exp: Math.floor(Date.now() / 1000) + 3600 }))
  sessionStorage.setItem('sgt.access', `${header}.${body}.fixture-signature`)
}

function renderApp(route: string) {
  return renderWithProviders(
    <AuthProvider>
      <ToastProvider>
        <AppRouter />
      </ToastProvider>
    </AuthProvider>,
    { route },
  )
}

describe('sistema de errores integrado con la aplicación', () => {
  afterEach(() => {
    sessionStorage.clear()
    limpiarSesionExpirada()
  })

  it('un 403 de la API se muestra en la vista, sin cerrar la sesión ni ir a la vista 401', async () => {
    iniciarSesion(['SECRETARIO_ABOGADO'])
    server.use(http.get(DETALLE_URL, () => HttpResponse.json({ detail: 'Prohibido.' }, { status: 403 })))
    renderApp(`/bandeja/${ID}`)

    expect(await screen.findByRole('heading', { level: 2, name: 'No tienes permisos para acceder' })).toBeInTheDocument()
    // Sigue dentro del portal (navegación del shell) y con sesión.
    expect(screen.getByRole('navigation', { name: 'Navegación principal' })).toBeInTheDocument()
    expect(getAccessToken()).not.toBeNull()
    expect(screen.queryByRole('heading', { name: 'Necesitas iniciar sesión' })).not.toBeInTheDocument()
  })

  it('el 404 de un recurso se queda en su layout y no es la página 404 global', async () => {
    iniciarSesion(['SECRETARIO_ABOGADO'])
    server.use(http.get(DETALLE_URL, () => HttpResponse.json({ detail: 'No encontrado.' }, { status: 404 })))
    renderApp(`/bandeja/${ID}`)

    expect(await screen.findByRole('heading', { level: 2, name: 'Expediente no encontrado' })).toBeInTheDocument()
    expect(screen.getByRole('navigation', { name: 'Navegación principal' })).toBeInTheDocument()
    expect(screen.queryByRole('heading', { level: 1, name: 'Página no encontrada' })).not.toBeInTheDocument()
  })

  it('un 500 de la consulta principal no recarga la aplicación ni cierra la sesión', async () => {
    iniciarSesion(['SECRETARIO_ABOGADO'])
    server.use(http.get(DETALLE_URL, () => HttpResponse.json({ detail: 'Error interno.' }, { status: 500 })))
    renderApp(`/bandeja/${ID}`)

    expect(await screen.findByRole('heading', { level: 2, name: 'Algo salió mal' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Intentar nuevamente' })).toBeEnabled()
    expect(getAccessToken()).not.toBeNull()
  })

  it('sin sesión ni 401 previo, una ruta protegida sigue llevando al login', async () => {
    renderApp('/estudiante')
    expect(await screen.findByRole('heading', { name: 'Iniciar sesión' })).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Necesitas iniciar sesión' })).not.toBeInTheDocument()
  })

  it('la vista 401 es pública y no exige sesión', async () => {
    renderApp('/sesion-expirada')
    expect(await screen.findByRole('heading', { level: 1, name: 'Necesitas iniciar sesión' })).toBeInTheDocument()
  })
})
