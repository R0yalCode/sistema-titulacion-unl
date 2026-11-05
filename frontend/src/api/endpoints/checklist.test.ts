import { HttpResponse, http } from 'msw'
import { describe, expect, it } from 'vitest'
import { server } from '@/test/server'
import { subsanarChecklist } from './checklist'

const SUBSANAR_URL = '*/api/v1/checklist/:id/subsanar/'

describe('subsanarChecklist', () => {
  it('envía el archivo como multipart/form-data a la ruta real', async () => {
    let contentType: string | null = null
    server.use(
      http.post(SUBSANAR_URL, ({ request }) => {
        contentType = request.headers.get('content-type')
        return HttpResponse.json({}, { status: 201 })
      }),
    )

    const archivo = new File(['%PDF-1.4'], 'documento.pdf', { type: 'application/pdf' })
    await subsanarChecklist('checklist-1', archivo)

    expect(contentType).toMatch(/^multipart\/form-data/)
  })
})
