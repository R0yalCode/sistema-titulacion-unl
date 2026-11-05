import { HttpResponse, delay, http } from 'msw'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { clearAccessToken, saveAccessToken } from '@/auth/storage'
import { server } from '@/test/server'
import { request, setUnauthorizedHandler } from './client'
import { ApiRequestError } from './errors'

const TEST_URL = 'http://localhost:8000/api/v1/test/'

describe('request', () => {
  afterEach(() => {
    clearAccessToken()
    setUnauthorizedHandler(null)
  })

  it('devuelve el cuerpo JSON en una respuesta 200', async () => {
    server.use(http.get(TEST_URL, () => HttpResponse.json({ ok: true })))

    const result = await request<{ ok: boolean }>('/api/v1/test/')

    expect(result).toEqual({ ok: true })
  })

  it('devuelve null en una respuesta 204 sin contenido', async () => {
    server.use(http.post(TEST_URL, () => new HttpResponse(null, { status: 204 })))

    const result = await request('/api/v1/test/', { method: 'POST' })

    expect(result).toBeNull()
  })

  it('devuelve null si la respuesta no es JSON', async () => {
    server.use(http.get(TEST_URL, () => new HttpResponse('texto plano', { headers: { 'content-type': 'text/plain' } })))

    const result = await request('/api/v1/test/')

    expect(result).toBeNull()
  })

  it('envía Authorization cuando hay sesión', async () => {
    saveAccessToken('token-de-prueba')
    let receivedAuth: string | null = null
    server.use(
      http.get(TEST_URL, ({ request: req }) => {
        receivedAuth = req.headers.get('authorization')
        return HttpResponse.json({ ok: true })
      }),
    )

    await request('/api/v1/test/')

    expect(receivedAuth).toBe('Bearer token-de-prueba')
  })

  it('normaliza un 400 con errores por campo', async () => {
    server.use(
      http.post(TEST_URL, () => HttpResponse.json({ carrera_id: ['Este campo es obligatorio.'] }, { status: 400 })),
    )

    await expect(request('/api/v1/test/', { method: 'POST', body: {} })).rejects.toMatchObject({
      error: { status: 400, code: 'BAD_REQUEST', fieldErrors: { carrera_id: ['Este campo es obligatorio.'] } },
    })
  })

  it('normaliza un 401 y dispara el manejador global', async () => {
    const handler = vi.fn()
    setUnauthorizedHandler(handler)
    server.use(http.get(TEST_URL, () => HttpResponse.json({ detail: 'No autorizado.' }, { status: 401 })))

    await expect(request('/api/v1/test/')).rejects.toMatchObject({
      error: { status: 401, code: 'UNAUTHORIZED', message: 'No autorizado.' },
    })
    expect(handler).toHaveBeenCalledOnce()
  })

  it('un 401 con skipAuthHandler no dispara el manejador global (P2-3: login)', async () => {
    const handler = vi.fn()
    setUnauthorizedHandler(handler)
    server.use(http.get(TEST_URL, () => HttpResponse.json({ detail: 'Credenciales inválidas.' }, { status: 401 })))

    await expect(request('/api/v1/test/', { skipAuthHandler: true })).rejects.toMatchObject({
      error: { status: 401, code: 'UNAUTHORIZED' },
    })
    expect(handler).not.toHaveBeenCalled()
  })

  it('normaliza un 403', async () => {
    server.use(http.get(TEST_URL, () => HttpResponse.json({ detail: 'Prohibido.' }, { status: 403 })))

    await expect(request('/api/v1/test/')).rejects.toMatchObject({ error: { status: 403, code: 'FORBIDDEN' } })
  })

  it('normaliza un 404', async () => {
    server.use(http.get(TEST_URL, () => HttpResponse.json({ detail: 'No encontrado.' }, { status: 404 })))

    await expect(request('/api/v1/test/')).rejects.toMatchObject({ error: { status: 404, code: 'NOT_FOUND' } })
  })

  it('normaliza un 500 sin exponer detalles internos', async () => {
    server.use(http.get(TEST_URL, () => HttpResponse.json({ detail: 'Traceback interno...' }, { status: 500 })))

    const error = await request('/api/v1/test/').catch((err: unknown) => err)

    expect(error).toBeInstanceOf(ApiRequestError)
    expect((error as ApiRequestError).error.code).toBe('INTERNAL_SERVER_ERROR')
  })

  it('produce un ApiError de red cuando falla la conexión', async () => {
    server.use(http.get(TEST_URL, () => HttpResponse.error()))

    await expect(request('/api/v1/test/')).rejects.toMatchObject({ error: { isNetworkError: true } })
  })

  it('produce un ApiError de timeout cuando se excede el plazo', async () => {
    server.use(
      http.get(TEST_URL, async () => {
        await delay(50)
        return HttpResponse.json({ ok: true })
      }),
    )

    await expect(request('/api/v1/test/', { timeoutMs: 5 })).rejects.toMatchObject({
      error: { isTimeout: true },
    })
  })
})
