import { describe, expect, it } from 'vitest'
import { ApiRequestError } from '@/api/errors'
import { describeAccionError } from './errors'

describe('describeAccionError', () => {
  it('devuelve un mensaje genérico si el error no es un ApiRequestError', () => {
    expect(describeAccionError(new Error('otro error'))).toBe('No se pudo completar la acción. Intente nuevamente.')
  })

  it('advierte de un resultado ambiguo ante un error de red', () => {
    const error = new ApiRequestError({
      status: 0,
      code: 'NETWORK_ERROR',
      message: 'No se pudo conectar con el servidor. Verifique su conexión.',
      isNetworkError: true,
      isTimeout: false,
    })

    expect(describeAccionError(error)).toMatch(/no se pudo confirmar el resultado/i)
  })

  it('advierte de un resultado ambiguo ante un timeout', () => {
    const error = new ApiRequestError({
      status: 0,
      code: 'TIMEOUT',
      message: 'La solicitud tardó demasiado.',
      isNetworkError: false,
      isTimeout: true,
    })

    expect(describeAccionError(error)).toMatch(/no se pudo confirmar el resultado/i)
  })

  it('muestra el mensaje real del backend cuando existe (incl. discrepancias 500 de INC-21)', () => {
    const error = new ApiRequestError({
      status: 500,
      code: 'INTERNAL_SERVER_ERROR',
      message: 'El requisito debe estar en OBSERVADO. Estado actual: PENDIENTE',
      isNetworkError: false,
      isTimeout: false,
    })

    expect(describeAccionError(error)).toBe('El requisito debe estar en OBSERVADO. Estado actual: PENDIENTE')
  })

  it('usa presentApiError cuando el backend no da un mensaje real', () => {
    const error = new ApiRequestError({
      status: 503,
      code: 'SERVICE_UNAVAILABLE',
      message: 'Ocurrió un error inesperado.',
      isNetworkError: false,
      isTimeout: false,
    })

    expect(describeAccionError(error)).toMatch(/servicio no está disponible/i)
  })
})
