import { HttpResponse, http, type HttpHandler } from 'msw'
import {
  fixtureBandejaExpediente,
  fixtureChecklist,
  fixtureExpedienteBorrador,
  fixtureExpedienteDetalle,
  fixtureMfaChallenge,
  fixtureMiTramite,
  fixtureMfaSetup,
  fixtureNotificacion,
  fixturePerfilAcademico,
  fixtureRecoveryCodes,
  fixtureTokenPair,
  mfaInvalidCodeBody,
} from './fixtures'

const LOGIN_URL = '*/api/v1/auth/login/'
const MFA_SETUP_URL = '*/api/v1/auth/mfa/setup/'
const MFA_SETUP_CONFIRM_URL = '*/api/v1/auth/mfa/setup/confirm/'
const MFA_VERIFY_URL = '*/api/v1/auth/mfa/verify/'
const MFA_RECOVERY_URL = '*/api/v1/auth/mfa/recovery/'
const LOGOUT_URL = '*/api/v1/auth/logout/'
const MFA_RESET_URL = '*/api/v1/auth/mfa/reset/'
const MFA_RESET_CONFIRM_URL = '*/api/v1/auth/mfa/reset/confirm/'
const PASSWORD_RESET_URL = '*/api/v1/auth/password-reset/'
const PASSWORD_RESET_VALIDATE_URL = '*/api/v1/auth/password-reset/validate/'
const PASSWORD_RESET_CONFIRM_URL = '*/api/v1/auth/password-reset/confirm/'
const BANDEJA_URL = '*/api/v1/expedientes/bandeja/'
const EXPEDIENTES_URL = '*/api/v1/expedientes/'
const MI_TRAMITE_URL = '*/api/v1/expedientes/mi-tramite/'
const PERFIL_ACADEMICO_URL = '*/api/v1/perfil-academico/'
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
  // Flujo en dos pasos (AUTH-B). Solo para pruebas: "estudiante.demo@unl.edu.ec"
  // simula un dispositivo de confianza vigente; "mfa.registro@…" y
  // "mfa.verificar@…" exigen registrar o verificar el segundo factor (123456).
  http.post(LOGIN_URL, async ({ request }) => {
    const body = (await request.json()) as { email?: string; password?: string }
    const user = body.email?.replace(/@unl\.edu\.ec$/, '')

    if (body.password === 'demo-valida') {
      if (user === 'estudiante.demo') {
        return HttpResponse.json({ status: 'authenticated', ...fixtureTokenPair }, { status: 200 })
      }
      if (user === 'mfa.registro') {
        return HttpResponse.json({ status: 'mfa_setup_required', ...fixtureMfaChallenge })
      }
      if (user === 'mfa.verificar') {
        return HttpResponse.json({ status: 'mfa_required', ...fixtureMfaChallenge })
      }
    }

    return HttpResponse.json(
      { detail: 'Usuario o contraseña incorrectos.', code: 'credenciales_invalidas' },
      { status: 401 },
    )
  }),
  http.post(MFA_SETUP_URL, () => HttpResponse.json(fixtureMfaSetup)),
  http.post(MFA_SETUP_CONFIRM_URL, async ({ request }) => {
    const body = (await request.json()) as { code?: string }
    if (body.code === '123456') {
      return HttpResponse.json({
        status: 'authenticated',
        ...fixtureTokenPair,
        recovery_codes: fixtureRecoveryCodes,
      })
    }
    return HttpResponse.json(mfaInvalidCodeBody, { status: 400 })
  }),
  http.post(MFA_VERIFY_URL, async ({ request }) => {
    const body = (await request.json()) as { code?: string }
    if (body.code === '123456') {
      return HttpResponse.json({ status: 'authenticated', ...fixtureTokenPair })
    }
    return HttpResponse.json(mfaInvalidCodeBody, { status: 400 })
  }),
  http.post(MFA_RECOVERY_URL, async ({ request }) => {
    const body = (await request.json()) as { recovery_code?: string }
    if (body.recovery_code?.toUpperCase() === fixtureRecoveryCodes[0]) {
      return HttpResponse.json({ status: 'mfa_setup_required', ...fixtureMfaChallenge })
    }
    return HttpResponse.json(mfaInvalidCodeBody, { status: 400 })
  }),
  http.post(LOGOUT_URL, () => HttpResponse.json({ detail: 'Sesión cerrada.' })),
  http.post(MFA_RESET_URL, () =>
    HttpResponse.json({
      detail:
        'Si los datos corresponden a una cuenta con doble factor activo, enviaremos un enlace de vigencia limitada al correo registrado.',
    }),
  ),
  http.post(MFA_RESET_CONFIRM_URL, async ({ request }) => {
    const body = (await request.json()) as { token?: string }
    if (body.token === 'token-valido') {
      return HttpResponse.json({ detail: 'El doble factor se restableció.' })
    }
    return HttpResponse.json(
      { detail: 'El enlace no es válido.', code: 'enlace_mfa_invalido' },
      { status: 400 },
    )
  }),
  http.post(PASSWORD_RESET_URL, () =>
    HttpResponse.json({
      detail:
        'Si existe una cuenta asociada a ese correo, se enviarán las instrucciones para restablecer la contraseña.',
    }),
  ),
  http.post(PASSWORD_RESET_VALIDATE_URL, () => HttpResponse.json({ detail: 'Enlace válido.' })),
  http.post(PASSWORD_RESET_CONFIRM_URL, () =>
    HttpResponse.json({ detail: 'La contraseña se restableció correctamente.' }),
  ),
  http.get(BANDEJA_URL, () =>
    HttpResponse.json({ count: 1, next: null, previous: null, results: [fixtureBandejaExpediente] }),
  ),
  http.post(EXPEDIENTES_URL, () => HttpResponse.json(fixtureExpedienteBorrador, { status: 201 })),
  // Antes del detalle: `:id/` también coincidiría con `mi-tramite/`.
  http.get(MI_TRAMITE_URL, () => HttpResponse.json(fixtureMiTramite)),
  http.get(PERFIL_ACADEMICO_URL, () => HttpResponse.json(fixturePerfilAcademico)),
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
