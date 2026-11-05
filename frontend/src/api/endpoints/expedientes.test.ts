import { HttpResponse, http } from 'msw'
import { describe, expect, it } from 'vitest'
import { server } from '@/test/server'
import { listBandejaEstudiante } from './expedientes'

const BANDEJA_URL = '*/api/v1/expedientes/bandeja/'

function captureUrl() {
  let capturedUrl = ''
  server.use(
    http.get(BANDEJA_URL, ({ request }) => {
      capturedUrl = request.url
      return HttpResponse.json({ count: 0, next: null, previous: null, results: [] })
    }),
  )
  return () => capturedUrl
}

describe('listBandejaEstudiante', () => {
  it('no agrega parámetros de consulta cuando no se solicitan', async () => {
    const getUrl = captureUrl()
    await listBandejaEstudiante()

    expect(getUrl()).not.toContain('?')
  })

  it('agrega solo page cuando pageSize no se especifica', async () => {
    const getUrl = captureUrl()
    await listBandejaEstudiante({ page: 2 })

    expect(getUrl()).toContain('page=2')
    expect(getUrl()).not.toContain('page_size')
  })

  it('agrega solo page_size cuando page no se especifica', async () => {
    const getUrl = captureUrl()
    await listBandejaEstudiante({ pageSize: 25 })

    expect(getUrl()).toContain('page_size=25')
    expect(getUrl()).not.toContain('page=')
  })

  it('agrega page y page_size cuando ambos se especifican', async () => {
    const getUrl = captureUrl()
    await listBandejaEstudiante({ page: 3, pageSize: 10 })

    expect(getUrl()).toContain('page=3')
    expect(getUrl()).toContain('page_size=10')
  })
})
