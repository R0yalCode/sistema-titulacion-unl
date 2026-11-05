import { describe, expect, it, vi } from 'vitest'
import { fixtureTokenPair } from '@/mocks/fixtures'
import { setUnauthorizedHandler } from '../client'
import { login } from './auth'

describe('login', () => {
  it('devuelve el par de tokens con credenciales válidas', async () => {
    const result = await login({ username: 'estudiante.demo', password: 'demo-valida' })

    expect(result).toEqual(fixtureTokenPair)
  })

  it('devuelve un ApiError normalizado con credenciales inválidas', async () => {
    await expect(login({ username: 'incorrecto', password: 'incorrecto' })).rejects.toMatchObject({
      error: { status: 401, code: 'UNAUTHORIZED' },
    })
  })

  it('un 401 por credenciales inválidas no dispara el cierre de sesión global (P2-3)', async () => {
    const handler = vi.fn()
    setUnauthorizedHandler(handler)

    await login({ username: 'incorrecto', password: 'incorrecto' }).catch(() => undefined)

    expect(handler).not.toHaveBeenCalled()
    setUnauthorizedHandler(null)
  })
})
