import { HttpResponse, http } from 'msw'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiRequestError } from '@/api/errors'
import { server } from '@/test/server'
import { cargarDocumento, solicitarEmision } from './peticiones'

const SOLICITAR_URL = '*/api/v1/peticiones/:id/solicitar-emision/'
const DOCUMENTO_URL = '*/api/v1/peticiones/:id/documento/'
const PETICION_ID = '77777777-0000-0000-0000-000000000001'

describe('solicitarEmision', () => {
  it('hace POST sin cuerpo a la petición indicada y devuelve la respuesta real', async () => {
    let metodo = ''
    let idRecibido = ''
    let cuerpo = ''
    server.use(
      http.post(SOLICITAR_URL, async ({ request, params }) => {
        metodo = request.method
        idRecibido = String(params.id)
        cuerpo = await request.text()
        return HttpResponse.json({
          id: PETICION_ID,
          requisito_codigo: 'RECORD_ACADEMICO',
          requisito_nombre: 'Récord académico',
          estado_peticion: 'SOLICITADO',
          dependencia_emisora: 'SECRETARIA_CARRERA',
          fecha_solicitud: '2026-11-12T10:00:00Z',
        })
      }),
    )

    const respuesta = await solicitarEmision(PETICION_ID)

    expect(metodo).toBe('POST')
    expect(idRecibido).toBe(PETICION_ID)
    expect(cuerpo).toBe('')
    expect(respuesta.estado_peticion).toBe('SOLICITADO')
  })

  it('propaga el código y el mensaje reales de un 400 del backend', async () => {
    server.use(
      http.post(SOLICITAR_URL, () =>
        HttpResponse.json(
          { detail: 'La petición no está en estado PENDIENTE.', code: 'estado_peticion_invalido' },
          { status: 400 },
        ),
      ),
    )

    const error = await solicitarEmision(PETICION_ID).catch((e: unknown) => e)

    expect(error).toBeInstanceOf(ApiRequestError)
    expect((error as ApiRequestError).error.status).toBe(400)
    expect((error as ApiRequestError).error.message).toBe('La petición no está en estado PENDIENTE.')
  })
})

describe('cargarDocumento', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('envía multipart con el campo exacto "archivo" y sin Content-Type JSON', async () => {
    let tipoContenido = ''
    // MSW no puede leer cuerpos multipart en este entorno de pruebas (jsdom);
    // el nombre del campo se verifica sobre el FormData que construye el cliente.
    const append = vi.spyOn(FormData.prototype, 'append')
    server.use(
      http.post(DOCUMENTO_URL, ({ request }) => {
        tipoContenido = request.headers.get('content-type') ?? ''
        return HttpResponse.json(
          {
            id: 'doc-1',
            peticion: PETICION_ID,
            version: 1,
            archivo_path: 'expedientes/2026/x/doc.pdf',
            nombre_original: 'record.pdf',
            tamanio_bytes: 10,
            hash_sha256: 'abc',
            tipo_mime: 'application/pdf',
            subido_por: 'u1',
            subido_por_username: 'estudiante',
            fecha_carga: '2026-11-12T10:00:00Z',
            es_vigente: true,
          },
          { status: 201 },
        )
      }),
    )

    const archivo = new File(['%PDF-1.4'], 'record.pdf', { type: 'application/pdf' })
    const respuesta = await cargarDocumento(PETICION_ID, archivo)

    expect(tipoContenido).toMatch(/^multipart\/form-data/)
    expect(append).toHaveBeenCalledWith('archivo', archivo)
    expect(respuesta.version).toBe(1)
    expect(respuesta.es_vigente).toBe(true)
  })
})
