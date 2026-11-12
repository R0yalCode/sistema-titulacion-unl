import { describe, expect, it } from 'vitest'
import { ApiRequestError, type ApiError } from '@/api/errors'
import { presentApiError } from './apiErrorPresentation'

function makeError(overrides: Partial<ApiError>): ApiRequestError {
  return new ApiRequestError({
    status: 500,
    code: 'INTERNAL_SERVER_ERROR',
    message: 'Traceback (most recent call last): ...',
    isNetworkError: false,
    isTimeout: false,
    ...overrides,
  })
}

describe('presentApiError', () => {
  it('404 → not-found, sin exponer el mensaje crudo del backend', () => {
    const presentation = presentApiError(makeError({ status: 404, code: 'NOT_FOUND' }))

    expect(presentation).toEqual({
      kind: 'not-found',
      title: 'No encontrado',
      description: 'El recurso solicitado no existe o no está disponible.',
    })
  })

  it('403 → forbidden, sin revelar detalles de la regla RBAC', () => {
    const presentation = presentApiError(makeError({ status: 403, code: 'FORBIDDEN' }))

    expect(presentation.kind).toBe('forbidden')
    expect(presentation.description).not.toMatch(/rol|RBAC|permiso denegado por/i)
  })

  it('500 → error con el mensaje institucional (ERR-07)', () => {
    const presentation = presentApiError(makeError({ status: 500 }))

    expect(presentation).toEqual({
      kind: 'error',
      title: 'Error del servidor',
      description: 'Ocurrió un problema al procesar tu solicitud. Intenta nuevamente.',
    })
  })

  it('503 → error con el mensaje institucional (ERR-08)', () => {
    const presentation = presentApiError(makeError({ status: 503, code: 'SERVICE_UNAVAILABLE' }))

    expect(presentation).toEqual({
      kind: 'error',
      title: 'Servicio no disponible',
      description: 'El servicio no está disponible temporalmente. Intenta nuevamente en unos minutos.',
    })
  })

  it('502 y 504 también se tratan como indisponibilidad (ERR-08)', () => {
    expect(presentApiError(makeError({ status: 502 })).title).toBe('Servicio no disponible')
    expect(presentApiError(makeError({ status: 504 })).title).toBe('Servicio no disponible')
  })

  it('error de red se trata como indisponibilidad, no como autorización', () => {
    const presentation = presentApiError(
      makeError({ status: 0, code: 'NETWORK_ERROR', isNetworkError: true }),
    )

    expect(presentation.title).toBe('Servicio no disponible')
  })

  it('timeout se trata como indisponibilidad', () => {
    const presentation = presentApiError(makeError({ status: 0, code: 'TIMEOUT', isTimeout: true }))

    expect(presentation.title).toBe('Servicio no disponible')
  })

  it('401 se distingue de 403 (autenticación vs autorización)', () => {
    const presentation = presentApiError(makeError({ status: 401, code: 'UNAUTHORIZED' }))

    expect(presentation.title).toBe('Sesión expirada')
    expect(presentation.title).not.toBe('Acceso restringido')
  })

  it('nunca expone el mensaje crudo del backend (sin trazas/SQL/rutas)', () => {
    const presentation = presentApiError(
      makeError({ status: 500, message: 'Traceback: SELECT * FROM auth_user WHERE...' }),
    )

    expect(presentation.description).not.toMatch(/traceback|SELECT|SQL/i)
  })

  it('código no mapeado degrada a un mensaje genérico, sin inventar semántica', () => {
    const presentation = presentApiError(makeError({ status: 418, code: 'HTTP_418' }))

    expect(presentation.kind).toBe('error')
    expect(presentation.title).toBe('Ocurrió un error')
  })
})
