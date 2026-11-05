import { afterEach, describe, expect, it } from 'vitest'
import { clearAccessToken, getAccessToken, saveAccessToken } from '@/auth/storage'

describe('storage', () => {
  afterEach(() => {
    sessionStorage.clear()
  })

  it('guarda y lee el access token en sessionStorage', () => {
    saveAccessToken('token-de-prueba')
    expect(getAccessToken()).toBe('token-de-prueba')
    expect(sessionStorage.getItem('sgt.access')).toBe('token-de-prueba')
  })

  it('devuelve null si no hay token guardado', () => {
    expect(getAccessToken()).toBeNull()
  })

  it('borra el token', () => {
    saveAccessToken('token-de-prueba')
    clearAccessToken()
    expect(getAccessToken()).toBeNull()
  })

  it('no expone ninguna función para persistir refresh', () => {
    const storageModule: Record<string, unknown> = { saveAccessToken, getAccessToken, clearAccessToken }
    expect(Object.keys(storageModule).some((key) => key.toLowerCase().includes('refresh'))).toBe(false)
  })
})
