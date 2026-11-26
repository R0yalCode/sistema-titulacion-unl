import type { ReactNode } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { renderHook, waitFor } from '@testing-library/react'
import { HttpResponse, http } from 'msw'
import { describe, expect, it, vi } from 'vitest'
import { AuthContext, type AuthContextValue } from '@/auth/AuthContext'
import { server } from '@/test/server'
import { useNombreVisible } from './useNombreVisible'

const PERFIL_ACADEMICO_URL = '*/api/v1/perfil-academico/'
const MI_TRAMITE_URL = '*/api/v1/expedientes/mi-tramite/'

function wrapper(roles: string[]) {
  const auth: AuthContextValue = {
    user: { cedula: '1100000000', roles },
    isAuthenticated: true,
    isLoading: false,
    login: vi.fn().mockReturnValue(true),
    logout: vi.fn(),
    signOut: vi.fn(),
    hasRole: (lista) => lista.some((rol) => roles.includes(rol)),
  }
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return function Wrapper({ children }: { children: ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        <AuthContext.Provider value={auth}>{children}</AuthContext.Provider>
      </QueryClientProvider>
    )
  }
}

describe('useNombreVisible (AX-C)', () => {
  it('estudiante: primer nombre y primer apellido del perfil académico', async () => {
    const { result } = renderHook(() => useNombreVisible(), { wrapper: wrapper(['ESTUDIANTE']) })
    await waitFor(() => expect(result.current.nombre).toBe('Estudiante De Prueba'))
    expect(result.current).toMatchObject({ detalle: 'Estudiante', esEstudiante: true })
  })

  it('estudiante sin perfil académico: nombre completo de mi-tramite, sin partirlo', async () => {
    server.use(http.get(PERFIL_ACADEMICO_URL, () => HttpResponse.json({ detail: 'Sin fuente.' }, { status: 503 })))
    const { result } = renderHook(() => useNombreVisible(), { wrapper: wrapper(['ESTUDIANTE']) })
    await waitFor(() => expect(result.current.nombre).toBe('Estudiante de Prueba'))
  })

  it('estudiante sin ninguna fuente: su cédula, nunca un nombre inventado', async () => {
    server.use(
      http.get(PERFIL_ACADEMICO_URL, () => HttpResponse.json({ detail: 'Sin fuente.' }, { status: 503 })),
      http.get(MI_TRAMITE_URL, () => HttpResponse.json({ detail: 'Error.' }, { status: 500 })),
    )
    const { result } = renderHook(() => useNombreVisible(), { wrapper: wrapper(['ESTUDIANTE']) })
    await waitFor(() => expect(result.current.nombre).toBe('1100000000'))
  })

  it('funcionario: su rol y su cédula, sin consultar endpoints del estudiante', async () => {
    const perfil = vi.fn()
    const miTramite = vi.fn()
    server.use(
      http.get(PERFIL_ACADEMICO_URL, () => {
        perfil()
        return HttpResponse.json({}, { status: 403 })
      }),
      http.get(MI_TRAMITE_URL, () => {
        miTramite()
        return HttpResponse.json({}, { status: 403 })
      }),
    )
    const { result } = renderHook(() => useNombreVisible(), { wrapper: wrapper(['SECRETARIO_ABOGADO']) })
    expect(result.current).toEqual({ nombre: 'Secretaría abogada', detalle: 'C.I. 1100000000', esEstudiante: false })
    await new Promise((resolver) => setTimeout(resolver, 50))
    expect(perfil).not.toHaveBeenCalled()
    expect(miTramite).not.toHaveBeenCalled()
  })

  it('estudiante con rol operativo se trata como funcionario (mismo criterio que ExpedienteLayout)', () => {
    const { result } = renderHook(() => useNombreVisible(), { wrapper: wrapper(['ESTUDIANTE', 'DECANO']) })
    expect(result.current).toMatchObject({ nombre: 'Decanato', esEstudiante: false })
  })
})
