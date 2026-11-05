function base64UrlEncode(value: string): string {
  return btoa(value).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
}

function buildFixtureJwt(payload: Record<string, unknown>): string {
  const header = base64UrlEncode(JSON.stringify({ alg: 'HS256', typ: 'JWT' }))
  const body = base64UrlEncode(JSON.stringify(payload))
  return `${header}.${body}.fixture-signature`
}

export const fixtureEstudianteAccessToken = buildFixtureJwt({
  cedula: '0000000000',
  roles: ['ESTUDIANTE'],
  exp: Math.floor(Date.now() / 1000) + 3600,
})

export const fixtureTokenPair = {
  access: fixtureEstudianteAccessToken,
  refresh: 'fixture-refresh-no-se-persiste',
}

export const fixtureBandejaExpediente = {
  id: '33333333-3333-3333-3333-333333333333',
  numero_expediente: 'EXP-2026-0001',
  estudiante_id: '44444444-4444-4444-4444-444444444444',
  carrera_id: '11111111-1111-1111-1111-111111111111',
  facultad_id: '22222222-2222-2222-2222-222222222222',
  estado: 'BORRADOR' as const,
  fecha_creacion: '2026-11-01T10:00:00Z',
  fecha_recepcion: null,
  numero_providencia: null,
  fecha_limite_atencion: null,
}

export const fixtureExpedienteBorrador = {
  id: '66666666-6666-6666-6666-666666666666',
  numero_expediente: 'EXP-2026-0002',
  estudiante_id: fixtureBandejaExpediente.estudiante_id,
  carrera_id: fixtureBandejaExpediente.carrera_id,
  estado: 'BORRADOR' as const,
  activa: true,
  fecha_creacion: '2026-11-05T08:00:00Z',
  peticiones: [
    {
      id: '77777777-0000-0000-0000-000000000001',
      requisito_codigo: 'ART235-01-RECORD-ACADEMICO',
      requisito_nombre: 'Récord académico',
      estado_peticion: 'PENDIENTE',
      dependencia_emisora: 'SECRETARIA_CARRERA',
    },
    {
      id: '77777777-0000-0000-0000-000000000002',
      requisito_codigo: 'ART235-02-PRACTICAS-VINCULACION',
      requisito_nombre: 'Prácticas y vinculación',
      estado_peticion: 'PENDIENTE',
      dependencia_emisora: 'SECRETARIA_CARRERA',
    },
    {
      id: '77777777-0000-0000-0000-000000000003',
      requisito_codigo: 'ART235-03-IDIOMA-B1',
      requisito_nombre: 'Idioma B1',
      estado_peticion: 'PENDIENTE',
      dependencia_emisora: 'SECRETARIA_CARRERA',
    },
    {
      id: '77777777-0000-0000-0000-000000000004',
      requisito_codigo: 'ART235-04-DIRECTOR-TRABAJO',
      requisito_nombre: 'Director de trabajo de titulación',
      estado_peticion: 'PENDIENTE',
      dependencia_emisora: 'SECRETARIA_CARRERA',
    },
    {
      id: '77777777-0000-0000-0000-000000000005',
      requisito_codigo: 'ART235-05-TESORERIA',
      requisito_nombre: 'Tesorería',
      estado_peticion: 'PENDIENTE',
      dependencia_emisora: 'TESORERIA',
    },
  ],
}

export const fixtureExpedienteDetalle = {
  id: '88888888-8888-8888-8888-888888888888',
  numero_expediente: 'EXP-2026-0003',
  estudiante_id: fixtureBandejaExpediente.estudiante_id,
  carrera_id: fixtureBandejaExpediente.carrera_id,
  facultad_id: fixtureBandejaExpediente.facultad_id,
  estado: 'EN_VERIFICACION' as const,
  activa: true,
  fecha_creacion: '2026-10-20T08:00:00Z',
  fecha_recepcion: '2026-10-21T09:00:00Z',
  numero_providencia: 'PROV-2026-0003',
  fecha_limite_atencion: '2026-11-03T17:00:00Z',
  dias_laborables_acumulados: 3,
  peticiones: fixtureExpedienteBorrador.peticiones.map((peticion) => ({ ...peticion, estado_peticion: 'CARGADO' })),
}

export const fixtureChecklist = fixtureExpedienteDetalle.peticiones.map((peticion, index) => ({
  id: `99999999-0000-0000-0000-00000000000${index + 1}`,
  expediente: fixtureExpedienteDetalle.id,
  requisito: `aaaaaaaa-0000-0000-0000-00000000000${index + 1}`,
  requisito_codigo: peticion.requisito_codigo,
  requisito_nombre: peticion.requisito_nombre,
  estado_verificacion: 'PENDIENTE' as const,
  evaluado_por: null,
  evaluado_por_username: null,
  fecha_evaluacion: null,
  fecha_creacion: '2026-10-20T08:00:00Z',
  fecha_actualizacion: '2026-10-20T08:00:00Z',
}))

export const fixtureNotificacion = {
  id: '55555555-5555-5555-5555-555555555555',
  expediente: fixtureBandejaExpediente.id,
  expediente_numero: fixtureBandejaExpediente.numero_expediente,
  peticion: null,
  peticion_requisito_nombre: null,
  titulo: 'Documento observado',
  mensaje: 'Revise el requisito observado en su expediente.',
  leida: false,
  fecha_creacion: '2026-11-02T09:00:00Z',
}
