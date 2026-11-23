import { request } from '../client'

export type EstadoPerfilAcademico =
  | 'VALIDADO'
  | 'NO_ASOCIADO'
  | 'INCOMPLETO'
  | 'INCONSISTENTE'
  | 'CARRERA_INACTIVA'

export type MotivoBloqueo = {
  codigo: string
  mensaje: string
}

export type PerfilAcademico = {
  estudiante: {
    identificacion: string
    nombres: string
    apellidos: string
    correo_institucional: string
  } | null
  carrera: { id: string; codigo: string; nombre: string; activa: boolean } | null
  facultad: { id: string; codigo: string; nombre: string; activa: boolean } | null
  /** Fuente que produjo el perfil; `es_simulada` indica datos de demostración. */
  fuente: { codigo: string; nombre: string; es_simulada: boolean }
  consultado_en: string
  estado_perfil: EstadoPerfilAcademico
  perfil_validado: boolean
  puede_iniciar_tramite: boolean
  motivos_bloqueo: MotivoBloqueo[]
}

/**
 * `GET /api/v1/perfil-academico/`: perfil académico del estudiante autenticado
 * (sin parámetros: siempre el propio). El frontend no conoce el proveedor
 * (hoy la simulación MockSGA del backend); solo muestra `fuente`. Un perfil no
 * validado responde 200 con `motivos_bloqueo`; 503 si no hay fuente académica.
 */
export function getPerfilAcademico(): Promise<PerfilAcademico> {
  return request<PerfilAcademico>('/api/v1/perfil-academico/')
}
