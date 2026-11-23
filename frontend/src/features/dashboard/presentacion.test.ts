import { describe, expect, it } from 'vitest'
import type { EstadoExpediente } from '@/api/endpoints/expedientes'
import type { ExpedienteResumen, SituacionEtapa } from '@/api/endpoints/miTramite'
import {
  calcularProximoHito,
  construirAccionesPendientes,
  describirMovimiento,
  porcentajeProgreso,
  presentarEstadoExpediente,
} from './presentacion'

const CODIGOS: EstadoExpediente[] = ['BORRADOR', 'ENVIADA', 'EN_VERIFICACION', 'INFORME_EMITIDO', 'DECLARADA_APTA']

function etapas(situaciones: SituacionEtapa[]) {
  return CODIGOS.map((codigo, index) => ({
    codigo,
    nombre: `Etapa ${codigo}`,
    situacion: situaciones[index] ?? 'pendiente',
    fecha: situaciones[index] === 'pendiente' ? null : '2026-11-01T10:00:00Z',
  }))
}

function expediente(overrides: Partial<ExpedienteResumen> = {}): ExpedienteResumen {
  return {
    id: 'exp-1',
    numero_expediente: 'EXP-2026-0001',
    estado: 'BORRADOR',
    activa: true,
    fecha_creacion: '2026-11-01T10:00:00Z',
    fecha_recepcion: null,
    fecha_actualizacion: '2026-11-01T10:00:00Z',
    fecha_limite_atencion: null,
    numero_providencia: null,
    etapas: etapas(['actual']),
    progreso: { etapas_completadas: 0, etapas_totales: 5 },
    peticiones: [
      {
        id: 'p1',
        requisito_codigo: 'R1',
        requisito_nombre: 'Récord académico',
        estado_peticion: 'PENDIENTE',
        dependencia_emisora: 'SECRETARIA_CARRERA',
        fecha_actualizacion: '2026-11-01T10:00:00Z',
      },
      {
        id: 'p2',
        requisito_codigo: 'R2',
        requisito_nombre: 'Prácticas',
        estado_peticion: 'OBSERVADO',
        dependencia_emisora: 'SECRETARIA_CARRERA',
        fecha_actualizacion: '2026-11-01T10:00:00Z',
      },
      {
        id: 'p3',
        requisito_codigo: 'R3',
        requisito_nombre: 'Inglés',
        estado_peticion: 'CARGADO',
        dependencia_emisora: 'SECRETARIA_CARRERA',
        fecha_actualizacion: '2026-11-01T10:00:00Z',
      },
    ],
    requisitos_sin_documento: ['p1', 'p2'],
    puede_enviarse: false,
    observaciones_pendientes: [],
    movimientos: [],
    ...overrides,
  }
}

describe('presentarEstadoExpediente', () => {
  it('traduce cada estado real a lenguaje claro sin exponer solo el código', () => {
    expect(presentarEstadoExpediente('OBSERVADA')).toMatchObject({ label: 'Con observaciones', variant: 'warning' })
    expect(presentarEstadoExpediente('DECLARADA_APTA')).toMatchObject({ label: 'Declarado apto', variant: 'success' })
    expect(presentarEstadoExpediente('CANCELADA').variant).toBe('danger')
  })

  it('no inventa etiquetas para un estado desconocido', () => {
    expect(presentarEstadoExpediente('NUEVO_ESTADO')).toMatchObject({ label: 'NUEVO_ESTADO', variant: 'neutral' })
  })
})

describe('porcentajeProgreso', () => {
  it('usa las etapas completadas que informa el backend', () => {
    expect(porcentajeProgreso(expediente({ progreso: { etapas_completadas: 2, etapas_totales: 5 } }))).toBe(40)
  })

  it('devuelve null cuando el backend no da progreso (trámite fuera del flujo)', () => {
    expect(porcentajeProgreso(expediente({ progreso: null }))).toBeNull()
  })
})

describe('construirAccionesPendientes', () => {
  it('sin expediente propone registrar la solicitud', () => {
    const acciones = construirAccionesPendientes(null)
    expect(acciones).toHaveLength(1)
    expect(acciones[0]?.href).toBe('/estudiante/solicitud/nueva')
  })

  it('en BORRADOR lista solo los requisitos sin documento que indica el backend', () => {
    const acciones = construirAccionesPendientes(expediente())
    expect(acciones.map((accion) => accion.id)).toEqual(['requisito-p1', 'requisito-p2'])
    expect(acciones[0]?.href).toBe('/expedientes/exp-1/peticiones/p1')
    expect(acciones[1]?.tono).toBe('warning')
  })

  it('no cuenta dos veces una petición observada que además no tiene documento', () => {
    const acciones = construirAccionesPendientes(
      expediente({
        observaciones_pendientes: [
          {
            id: 'o1',
            peticion_id: 'p2',
            requisito_nombre: 'Prácticas',
            motivo_observacion: 'Falta la firma',
            fecha_registro: '2026-11-02T10:00:00Z',
          },
        ],
      }),
    )
    expect(acciones.map((accion) => accion.id)).toEqual(['observacion-o1', 'requisito-p1'])
    expect(acciones[0]?.motivo).toBe('Falta la firma')
  })

  it('propone enviar solo cuando el backend indica que puede enviarse', () => {
    const lista = construirAccionesPendientes(expediente({ requisitos_sin_documento: [], puede_enviarse: true }))
    expect(lista.map((accion) => accion.id)).toEqual(['enviar-solicitud'])
    expect(lista[0]?.href).toBe('/expedientes/exp-1')
  })

  it('fuera de BORRADOR no pide documentos ni envío, aunque haya peticiones sin documento', () => {
    expect(
      construirAccionesPendientes(expediente({ estado: 'EN_VERIFICACION', etapas: etapas(['completada', 'completada', 'actual']) })),
    ).toEqual([])
  })

  it('con un expediente inactivo ofrece registrar una nueva solicitud', () => {
    const acciones = construirAccionesPendientes(
      expediente({ estado: 'CANCELADA', activa: false, progreso: null, requisitos_sin_documento: [] }),
    )
    expect(acciones.map((accion) => accion.id)).toEqual(['registrar-solicitud'])
  })
})

describe('calcularProximoHito', () => {
  it('muestra la fecha límite institucional solo mientras corre el plazo', () => {
    const hito = calcularProximoHito(
      expediente({
        estado: 'ENVIADA',
        etapas: etapas(['completada', 'actual']),
        fecha_limite_atencion: '2026-11-12T17:00:00Z',
      }),
    )
    expect(hito).toMatchObject({ nombre: 'Etapa EN_VERIFICACION', fecha: '2026-11-12T17:00:00Z' })
  })

  it('no muestra fecha en OBSERVADA aunque exista una fecha límite', () => {
    const hito = calcularProximoHito(
      expediente({
        estado: 'OBSERVADA',
        etapas: etapas(['completada', 'completada', 'actual']),
        fecha_limite_atencion: '2026-11-12T17:00:00Z',
      }),
    )
    expect(hito?.nombre).toBe('Etapa INFORME_EMITIDO')
    expect(hito?.fecha).toBeNull()
  })

  it('no hay próximo hito cuando el trámite concluyó o fue cancelado', () => {
    expect(
      calcularProximoHito(
        expediente({ estado: 'DECLARADA_APTA', etapas: etapas(Array(5).fill('completada') as SituacionEtapa[]) }),
      ),
    ).toBeNull()
    expect(calcularProximoHito(expediente({ estado: 'CANCELADA', progreso: null }))).toBeNull()
    expect(calcularProximoHito(null)).toBeNull()
  })
})

describe('describirMovimiento', () => {
  it('explica un cambio de estado y la vuelta a verificación tras subsanar', () => {
    expect(
      describirMovimiento({
        tipo: 'cambio_estado',
        fecha: '2026-11-02T10:00:00Z',
        estado_anterior: 'BORRADOR',
        estado_nuevo: 'ENVIADA',
        requisito_nombre: null,
        version: null,
      }).titulo,
    ).toBe('Estado: Solicitud enviada')
    expect(
      describirMovimiento({
        tipo: 'cambio_estado',
        fecha: '2026-11-03T10:00:00Z',
        estado_anterior: 'OBSERVADA',
        estado_nuevo: 'EN_VERIFICACION',
        requisito_nombre: null,
        version: null,
      }).titulo,
    ).toBe('Observaciones atendidas')
  })

  it('indica la versión del documento solo cuando es una nueva versión', () => {
    const base = {
      tipo: 'documento_cargado' as const,
      fecha: '2026-11-02T10:00:00Z',
      estado_anterior: null,
      estado_nuevo: null,
      requisito_nombre: 'Inglés',
    }
    expect(describirMovimiento({ ...base, version: 1 }).descripcion).toBe('Inglés')
    expect(describirMovimiento({ ...base, version: 2 }).descripcion).toBe('Inglés (versión 2)')
  })
})
