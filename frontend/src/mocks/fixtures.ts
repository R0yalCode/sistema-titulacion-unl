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

// Segundo factor (AUTH-C): valores ficticios solo para pruebas.
export const fixtureMfaChallenge = {
  challenge: 'fixture-reto-mfa',
  expires_in: 300,
}

export const fixtureMfaSetup = {
  qr_svg:
    'data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2010%2010%22%2F%3E',
  manual_key: 'ABCD EFGH IJKL MNOP QRST UVWX YZ23 4567',
  issuer: 'SGT-SIAAF UNL',
  account: 'mfa.registro',
}

export const fixtureRecoveryCodes = ['ABCDE-FGHJK', 'LMNPQ-RSTUV']

export const mfaInvalidCodeBody = {
  detail: 'El código no es válido. Verifique e intente nuevamente.',
  code: 'codigo_mfa_invalido',
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

/** Perfil académico de prueba (datos ficticios, fuente simulada). */
export const fixturePerfilAcademico = {
  estudiante: {
    identificacion: '1104567890',
    nombres: 'Estudiante',
    apellidos: 'De Prueba',
    correo_institucional: 'estudiante.prueba@unl.edu.ec',
  },
  carrera: {
    id: fixtureBandejaExpediente.carrera_id,
    codigo: 'MOCK-COMPUTACION',
    nombre: 'Computación',
    activa: true,
  },
  facultad: {
    id: fixtureBandejaExpediente.facultad_id,
    codigo: 'MOCK-FEIRNNR',
    nombre: 'Facultad de prueba',
    activa: true,
  },
  fuente: {
    codigo: 'MOCK_SGA',
    nombre: 'MockSGA (simulación del SGA, prototipo sin conexión institucional)',
    es_simulada: true,
  },
  consultado_en: '2026-11-22T10:00:00Z',
  estado_perfil: 'VALIDADO' as const,
  perfil_validado: true,
  puede_iniciar_tramite: true,
  motivos_bloqueo: [] as Array<{ codigo: string; mensaje: string }>,
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

/**
 * Solo pruebas (MSW): respuesta de `GET /expedientes/mi-tramite/` para un
 * expediente en BORRADOR con dos requisitos sin documento. No es dato de
 * producción ni se usa fuera de la suite.
 */
export const fixtureMiTramite = {
  estudiante: {
    nombre_completo: 'Estudiante de Prueba',
    email: 'estudiante.prueba@unl.edu.ec',
    cedula: '1104567890',
  },
  total_expedientes: 1,
  expediente: {
    id: fixtureExpedienteDetalle.id,
    numero_expediente: fixtureExpedienteDetalle.numero_expediente,
    estado: 'BORRADOR' as const,
    activa: true,
    fecha_creacion: '2026-10-20T08:00:00Z',
    fecha_recepcion: null,
    fecha_actualizacion: '2026-10-22T10:00:00Z',
    fecha_limite_atencion: null,
    numero_providencia: null,
    etapas: [
      { codigo: 'BORRADOR' as const, nombre: 'Solicitud registrada', situacion: 'actual' as const, fecha: '2026-10-20T08:00:00Z' },
      { codigo: 'ENVIADA' as const, nombre: 'Solicitud enviada', situacion: 'pendiente' as const, fecha: null },
      { codigo: 'EN_VERIFICACION' as const, nombre: 'Verificación de requisitos', situacion: 'pendiente' as const, fecha: null },
      { codigo: 'INFORME_EMITIDO' as const, nombre: 'Informe emitido', situacion: 'pendiente' as const, fecha: null },
      { codigo: 'DECLARADA_APTA' as const, nombre: 'Declaratoria de aptitud', situacion: 'pendiente' as const, fecha: null },
    ],
    progreso: { etapas_completadas: 0, etapas_totales: 5 },
    peticiones: fixtureExpedienteBorrador.peticiones.map((peticion, index) => ({
      id: peticion.id,
      requisito_codigo: peticion.requisito_codigo,
      requisito_nombre: peticion.requisito_nombre,
      estado_peticion: index < 2 ? 'PENDIENTE' : 'CARGADO',
      dependencia_emisora: peticion.dependencia_emisora,
      fecha_actualizacion: '2026-10-22T10:00:00Z',
    })),
    requisitos_sin_documento: fixtureExpedienteBorrador.peticiones.slice(0, 2).map((peticion) => peticion.id),
    puede_enviarse: false,
    observaciones_pendientes: [],
    movimientos: [
      {
        tipo: 'documento_cargado' as const,
        fecha: '2026-10-22T10:00:00Z',
        estado_anterior: null,
        estado_nuevo: null,
        requisito_nombre: fixtureExpedienteBorrador.peticiones[2]?.requisito_nombre ?? null,
        version: 1,
      },
      {
        tipo: 'creacion' as const,
        fecha: '2026-10-20T08:00:00Z',
        estado_anterior: null,
        estado_nuevo: 'BORRADOR' as const,
        requisito_nombre: null,
        version: null,
      },
    ],
  },
}
