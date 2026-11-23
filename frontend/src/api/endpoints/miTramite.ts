import { request } from '../client'
import type { EstadoExpediente } from './expedientes'

/**
 * `GET /api/v1/expedientes/mi-tramite/` (dashboard del estudiante, 2026-11-19;
 * `apps/expedientes/services/resumen_estudiante.py`). Solo ESTUDIANTE y solo
 * su propio trámite: el endpoint no acepta identificadores. Las etapas, el
 * progreso y los requisitos sin documento los calcula el backend con las
 * reglas reales (`TRANSICIONES_PERMITIDAS`, `enviar_expediente`); la interfaz
 * solo los presenta.
 */

export type SituacionEtapa = 'completada' | 'actual' | 'pendiente'

export type EtapaTramite = {
  codigo: EstadoExpediente
  nombre: string
  situacion: SituacionEtapa
  fecha: string | null
}

export type ProgresoTramite = {
  etapas_completadas: number
  etapas_totales: number
}

export type PeticionResumen = {
  id: string
  requisito_codigo: string
  requisito_nombre: string
  estado_peticion: string
  dependencia_emisora: string
  fecha_actualizacion: string
}

export type ObservacionPendiente = {
  id: string
  peticion_id: string
  requisito_nombre: string
  motivo_observacion: string
  fecha_registro: string
}

export type TipoMovimiento = 'creacion' | 'cambio_estado' | 'documento_cargado' | 'observacion'

export type MovimientoTramite = {
  tipo: TipoMovimiento
  fecha: string
  estado_anterior: EstadoExpediente | null
  estado_nuevo: EstadoExpediente | null
  requisito_nombre: string | null
  version: number | null
}

export type ExpedienteResumen = {
  id: string
  numero_expediente: string
  estado: EstadoExpediente
  activa: boolean
  fecha_creacion: string
  fecha_recepcion: string | null
  fecha_actualizacion: string
  fecha_limite_atencion: string | null
  numero_providencia: string | null
  etapas: EtapaTramite[]
  progreso: ProgresoTramite | null
  peticiones: PeticionResumen[]
  requisitos_sin_documento: string[]
  puede_enviarse: boolean
  observaciones_pendientes: ObservacionPendiente[]
  movimientos: MovimientoTramite[]
}

export type EstudianteResumen = {
  nombre_completo: string | null
  email: string | null
  cedula: string | null
}

export type MiTramite = {
  estudiante: EstudianteResumen
  total_expedientes: number
  expediente: ExpedienteResumen | null
}

export function getMiTramite(): Promise<MiTramite> {
  return request<MiTramite>('/api/v1/expedientes/mi-tramite/')
}
