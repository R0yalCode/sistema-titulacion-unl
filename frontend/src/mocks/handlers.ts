import { HttpResponse, http, type HttpHandler } from 'msw'
import {
  fixtureBandejaExpediente,
  fixtureChecklist,
  fixtureExpedienteBorrador,
  fixtureExpedienteDetalle,
  fixtureNotificacion,
  fixtureTokenPair,
} from './fixtures'

const TOKEN_URL = '*/api/v1/auth/token/'
const BANDEJA_URL = '*/api/v1/expedientes/bandeja/'
const EXPEDIENTES_URL = '*/api/v1/expedientes/'
const EXPEDIENTE_DETALLE_URL = '*/api/v1/expedientes/:id/'
const EXPEDIENTE_ENVIAR_URL = '*/api/v1/expedientes/:id/enviar/'
const EXPEDIENTE_OBSERVAR_URL = '*/api/v1/expedientes/:id/observar/'
const CHECKLIST_LIST_URL = '*/api/v1/expedientes/:id/checklist/'
const CHECKLIST_UPDATE_URL = '*/api/v1/checklist/:id/'
const CHECKLIST_SUBSANAR_URL = '*/api/v1/checklist/:id/subsanar/'
const PETICION_DOCUMENTO_URL = '*/api/v1/peticiones/:id/documento/'
const NOTIFICACIONES_URL = '*/api/v1/notificaciones/'
const NOTIFICACION_MARCAR_LEIDA_URL = '*/api/v1/notificaciones/:id/marcar-leida/'

export const handlers: HttpHandler[] = [
  http.post(TOKEN_URL, async ({ request }) => {
    const body = (await request.json()) as { username?: string; password?: string }

    if (body.username === 'estudiante.demo' && body.password === 'demo-valida') {
      return HttpResponse.json(fixtureTokenPair, { status: 200 })
    }

    return HttpResponse.json({ detail: 'No se encontró una cuenta activa con las credenciales dadas.' }, { status: 401 })
  }),
  http.get(BANDEJA_URL, () =>
    HttpResponse.json({ count: 1, next: null, previous: null, results: [fixtureBandejaExpediente] }),
  ),
  http.post(EXPEDIENTES_URL, () => HttpResponse.json(fixtureExpedienteBorrador, { status: 201 })),
  http.get(EXPEDIENTE_DETALLE_URL, () => HttpResponse.json(fixtureExpedienteDetalle)),
  http.post(EXPEDIENTE_ENVIAR_URL, () => HttpResponse.json(fixtureExpedienteDetalle)),
  http.post(EXPEDIENTE_OBSERVAR_URL, () =>
    HttpResponse.json(
      {
        id: 'bbbbbbbb-0000-0000-0000-000000000001',
        expediente: fixtureExpedienteDetalle.id,
        peticion: fixtureExpedienteDetalle.peticiones[0]?.id,
        peticion_requisito_nombre: fixtureExpedienteDetalle.peticiones[0]?.requisito_nombre,
        registrada_por: 'cccccccc-0000-0000-0000-000000000001',
        registrada_por_username: 'secretario.demo',
        motivo_observacion: 'Falta firma del director.',
        fecha_registro: '2026-11-05T10:00:00Z',
        resuelta: false,
        fecha_resolucion: null,
        fecha_creacion: '2026-11-05T10:00:00Z',
        fecha_actualizacion: '2026-11-05T10:00:00Z',
      },
      { status: 201 },
    ),
  ),
  http.get(CHECKLIST_LIST_URL, () => HttpResponse.json(fixtureChecklist)),
  http.put(CHECKLIST_UPDATE_URL, async ({ request, params }) => {
    const body = (await request.json()) as { estado_verificacion: string; motivo_observacion?: string }
    const item = fixtureChecklist.find((checklistItem) => checklistItem.id === params.id) ?? fixtureChecklist[0]
    return HttpResponse.json({
      ...item,
      estado_verificacion: body.estado_verificacion,
      evaluado_por_username: 'secretario.demo',
      fecha_evaluacion: '2026-11-05T10:00:00Z',
    })
  }),
  http.post(CHECKLIST_SUBSANAR_URL, () =>
    HttpResponse.json(
      {
        id: 'dddddddd-0000-0000-0000-000000000001',
        peticion: fixtureExpedienteDetalle.peticiones[0]?.id,
        version: 2,
        archivo_path: 'privado/expediente/archivo.pdf',
        nombre_original: 'archivo.pdf',
        tamanio_bytes: 1024,
        hash_sha256: 'hash',
        tipo_mime: 'application/pdf',
        subido_por: fixtureBandejaExpediente.estudiante_id,
        subido_por_username: 'estudiante.demo',
        fecha_carga: '2026-11-05T10:00:00Z',
        es_vigente: true,
      },
      { status: 201 },
    ),
  ),
  http.get(PETICION_DOCUMENTO_URL, () =>
    new HttpResponse(new Blob(['%PDF-1.4 fixture'], { type: 'application/pdf' }), {
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'attachment; filename="documento.pdf"',
      },
    }),
  ),
  http.get(NOTIFICACIONES_URL, () => HttpResponse.json({ results: [fixtureNotificacion] })),
  http.patch(NOTIFICACION_MARCAR_LEIDA_URL, () =>
    HttpResponse.json({ ...fixtureNotificacion, leida: true }),
  ),
]
