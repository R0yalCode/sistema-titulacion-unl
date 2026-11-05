import { describe, expect, it } from 'vitest'
import { networkApiError, normalizeApiError, timeoutApiError } from './errors'

describe('normalizeApiError', () => {
  it('usa el mensaje genérico si el cuerpo no es un objeto', () => {
    expect(normalizeApiError(500, 'texto plano')).toMatchObject({
      status: 500,
      code: 'INTERNAL_SERVER_ERROR',
      message: 'Ocurrió un error inesperado.',
    })
  })

  it('usa non_field_errors cuando está presente', () => {
    expect(normalizeApiError(400, { non_field_errors: ['Las fechas no coinciden.'] })).toMatchObject({
      message: 'Las fechas no coinciden.',
    })
  })

  it('usa el mensaje genérico si el objeto no coincide con ninguna forma conocida', () => {
    expect(normalizeApiError(500, { algo: 123 })).toMatchObject({
      message: 'Ocurrió un error inesperado.',
    })
  })

  it('asigna un código HTTP_xxx para estados sin mapeo conocido', () => {
    expect(normalizeApiError(418, {})).toMatchObject({ code: 'HTTP_418' })
  })
})

describe('networkApiError / timeoutApiError', () => {
  it('produce un error de red marcado como tal', () => {
    expect(networkApiError()).toMatchObject({ isNetworkError: true, isTimeout: false })
  })

  it('produce un error de timeout marcado como tal', () => {
    expect(timeoutApiError()).toMatchObject({ isNetworkError: false, isTimeout: true })
  })
})
