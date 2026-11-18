import { describe, expect, it, vi } from 'vitest'
import { fixtureTokenPair } from '@/mocks/fixtures'
import { setUnauthorizedHandler } from '../client'
import { login } from './auth'

describe('login', () => {
  it('devuelve el par de tokens con credenciales válidas', async () => {
    const result = await login({ email: 'estudiante.demo@unl.edu.ec', password: 'demo-valida' })

    expect(result).toEqual({ status: 'authenticated', ...fixtureTokenPair })
  })

  it('devuelve un ApiError normalizado con credenciales inválidas', async () => {
    await expect(login({ email: 'incorrecto@unl.edu.ec', password: 'incorrecto' })).rejects.toMatchObject({
      error: { status: 401, code: 'UNAUTHORIZED' },
    })
  })

  it('un 401 por credenciales inválidas no dispara el cierre de sesión global (P2-3)', async () => {
    const handler = vi.fn()
    setUnauthorizedHandler(handler)

    await login({ email: 'incorrecto@unl.edu.ec', password: 'incorrecto' }).catch(() => undefined)

    expect(handler).not.toHaveBeenCalled()
    setUnauthorizedHandler(null)
  })
})
