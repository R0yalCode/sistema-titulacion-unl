import { describe, expect, it } from 'vitest'
import { EnvError, parseEnv } from '@/lib/env'

describe('parseEnv', () => {
  it('lanza EnvError si falta VITE_API_BASE_URL', () => {
    expect(() => parseEnv({})).toThrow(EnvError)
  })

  it('lanza EnvError si la URL no es absoluta', () => {
    expect(() => parseEnv({ VITE_API_BASE_URL: '/api' })).toThrow(EnvError)
  })

  it('lanza EnvError si la URL usa un protocolo no soportado', () => {
    expect(() => parseEnv({ VITE_API_BASE_URL: 'ftp://localhost:8000' })).toThrow(EnvError)
  })

  it('lanza EnvError si la URL termina en barra', () => {
    expect(() => parseEnv({ VITE_API_BASE_URL: 'http://localhost:8000/' })).toThrow(EnvError)
  })

  it('devuelve un objeto congelado con valores por defecto para los opcionales', () => {
    const env = parseEnv({ VITE_API_BASE_URL: 'http://localhost:8000' })

    expect(env).toEqual({
      apiBaseUrl: 'http://localhost:8000',
      demoMode: false,
      useMocks: false,
      appName: 'SGT-SIAAF',
    })
    expect(Object.isFrozen(env)).toBe(true)
  })

  it('respeta VITE_DEMO_MODE, VITE_USE_MOCKS y VITE_APP_NAME cuando se definen', () => {
    const env = parseEnv({
      VITE_API_BASE_URL: 'https://api.sgt-siaaf.test',
      VITE_DEMO_MODE: 'true',
      VITE_USE_MOCKS: 'true',
      VITE_APP_NAME: 'SGT Demo',
    })

    expect(env).toEqual({
      apiBaseUrl: 'https://api.sgt-siaaf.test',
      demoMode: true,
      useMocks: true,
      appName: 'SGT Demo',
    })
  })
})
