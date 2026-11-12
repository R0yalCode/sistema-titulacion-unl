import { HttpResponse, http } from 'msw'
import { describe, expect, it } from 'vitest'
import { ApiRequestError } from '@/api/errors'
import { server } from '@/test/server'
import { fetchAuthenticatedFile } from './download'

const DOWNLOAD_URL = '*/api/v1/descarga-de-prueba/'

describe('fetchAuthenticatedFile', () => {
  it('obtiene el Blob y lee el nombre de archivo de Content-Disposition', async () => {
    server.use(
      http.get(DOWNLOAD_URL, () =>
        new HttpResponse(new Blob(['%PDF-1.4'], { type: 'application/pdf' }), {
          headers: { 'Content-Disposition': 'attachment; filename="real.pdf"' },
        }),
      ),
    )

    const result = await fetchAuthenticatedFile('/api/v1/descarga-de-prueba/', 'fallback.pdf')

    expect(result.filename).toBe('real.pdf')
    expect(result.blob).toBeInstanceOf(Blob)
  })

  it('usa el nombre de respaldo si no hay Content-Disposition', async () => {
    server.use(http.get(DOWNLOAD_URL, () => new HttpResponse(new Blob(['x']))))

    const result = await fetchAuthenticatedFile('/api/v1/descarga-de-prueba/', 'fallback.pdf')

    expect(result.filename).toBe('fallback.pdf')
  })

  it('lanza un ApiRequestError real ante un 404', async () => {
    server.use(http.get(DOWNLOAD_URL, () => HttpResponse.json({ detail: 'No encontrado.' }, { status: 404 })))

    await expect(fetchAuthenticatedFile('/api/v1/descarga-de-prueba/', 'fallback.pdf')).rejects.toMatchObject({
      error: { status: 404 },
    })
  })

  it('lanza un ApiRequestError de red si el fetch falla', async () => {
    server.use(http.get(DOWNLOAD_URL, () => HttpResponse.error()))

    const promise = fetchAuthenticatedFile('/api/v1/descarga-de-prueba/', 'fallback.pdf')

    await expect(promise).rejects.toBeInstanceOf(ApiRequestError)
    await expect(promise).rejects.toMatchObject({ error: { isNetworkError: true } })
  })
})
