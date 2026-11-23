import type { BadgeVariant } from '@/components/ui/Badge'

/**
 * Fuente única de presentación de estados (Design System §Estados). Solo
 * traduce valores REALES del backend a etiqueta + tono semántico; un valor
 * desconocido se muestra tal cual en tono neutral (no se inventan estados).
 *
 * Significado de los tonos en todo el sistema:
 *  - success: concluido o validado.
 *  - info:    en curso / en manos de la institución.
 *  - warning: requiere corrección o atención.
 *  - danger:  cancelado, vencido o error.
 *  - neutral: sin iniciar o pendiente de gestión.
 */
export type DominioEstado = 'expediente' | 'peticion' | 'checklist'

export type PresentacionEstado = { label: string; variant: BadgeVariant }

const ESTADOS: Record<DominioEstado, Record<string, PresentacionEstado>> = {
  expediente: {
    BORRADOR: { label: 'Borrador', variant: 'neutral' },
    ENVIADA: { label: 'Enviada', variant: 'info' },
    EN_VERIFICACION: { label: 'En verificación', variant: 'info' },
    OBSERVADA: { label: 'Observada', variant: 'warning' },
    INFORME_EMITIDO: { label: 'Informe emitido', variant: 'info' },
    DECLARADA_APTA: { label: 'Declarada apta', variant: 'success' },
    CANCELADA: { label: 'Cancelada', variant: 'danger' },
  },
  peticion: {
    PENDIENTE: { label: 'Pendiente', variant: 'neutral' },
    SOLICITADO: { label: 'Solicitado', variant: 'info' },
    CARGADO: { label: 'Cargado', variant: 'success' },
    LEGALIZADO: { label: 'Legalizado', variant: 'success' },
    VERIFICADO: { label: 'Verificado', variant: 'success' },
    OBSERVADO: { label: 'Observado', variant: 'warning' },
  },
  checklist: {
    PENDIENTE: { label: 'Pendiente', variant: 'neutral' },
    VERIFICADO: { label: 'Verificado', variant: 'success' },
    OBSERVADO: { label: 'Observado', variant: 'warning' },
  },
}

export function presentarEstado(dominio: DominioEstado, valor: string): PresentacionEstado {
  return ESTADOS[dominio][valor] ?? { label: valor, variant: 'neutral' }
}

/** Nombres legibles de dependencias/roles emisores (valores reales de ROLE_CHOICES). */
const ROLES: Record<string, string> = {
  ESTUDIANTE: 'Estudiante',
  SECRETARIA_CARRERA: 'Secretaría de carrera',
  SECRETARIO_ABOGADO: 'Secretaría abogada',
  ANALISTA_APOYO: 'Analista de apoyo',
  DECANO: 'Decanato',
  DIRECTOR_CARRERA: 'Dirección de carrera',
  RESPONSABLE_DEPENDENCIA: 'Responsable de dependencia',
  ADMINISTRADOR: 'Administración',
}

export function nombreRol(codigo: string): string {
  return ROLES[codigo] ?? codigo
}
