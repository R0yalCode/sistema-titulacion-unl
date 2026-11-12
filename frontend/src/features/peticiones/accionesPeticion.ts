import type { BadgeVariant } from '@/components/ui/Badge'
import type { EstadoExpediente } from '@/api/endpoints/expedientes'

/**
 * Matriz de acciones de V-05 (FE-T502/FE-T503), basada en las reglas
 * verificadas en el backend real (2026-11-12). Es solo una ayuda de interfaz:
 * el backend sigue autorizando o denegando cada operación.
 *
 * Discrepancia registrada: la matriz RBAC concede `peticiones:documento` POST
 * con ámbito ASIGNADO a varios funcionarios, pero `cargar_documento` solo
 * acepta al estudiante propietario o a la Secretaría de Carrera en peticiones
 * asignadas a la Secretaría. La interfaz aplica la regla más estricta.
 */

const ESTADOS_EXPEDIENTE_SOLICITUD: EstadoExpediente[] = ['BORRADOR', 'OBSERVADA']
const ESTADOS_PETICION_CARGA = ['PENDIENTE', 'SOLICITADO', 'OBSERVADO', 'CARGADO']
const ESTADOS_CON_DOCUMENTO = ['CARGADO', 'LEGALIZADO', 'VERIFICADO', 'OBSERVADO']
const DEPENDENCIA_SECRETARIA = 'SECRETARIA_CARRERA'

/**
 * `POST /peticiones/{id}/solicitar-emision/`: RBAC solo deja pasar al
 * ESTUDIANTE (propietario) y el servicio exige expediente BORRADOR/OBSERVADA y
 * petición PENDIENTE. La propiedad la garantiza el backend: un ESTUDIANTE solo
 * puede cargar el detalle de sus propios expedientes (SCOPE_OWN).
 */
export function puedeSolicitarEmision(
  roles: string[],
  estadoExpediente: EstadoExpediente,
  estadoPeticion: string,
): boolean {
  return (
    roles.includes('ESTUDIANTE') &&
    ESTADOS_EXPEDIENTE_SOLICITUD.includes(estadoExpediente) &&
    estadoPeticion === 'PENDIENTE'
  )
}

/** `POST /peticiones/{id}/documento/`: estados que permiten carga y regla de rol del servicio. */
export function puedeCargarDocumento(
  roles: string[],
  estadoPeticion: string,
  dependenciaEmisora: string,
): boolean {
  if (!ESTADOS_PETICION_CARGA.includes(estadoPeticion)) {
    return false
  }
  if (roles.includes('ESTUDIANTE')) {
    return true
  }
  return roles.includes('SECRETARIA_CARRERA') && dependenciaEmisora === DEPENDENCIA_SECRETARIA
}

/** Solo se ofrece la descarga cuando el estado implica un documento cargado; el 404 se maneja igual. */
export function tieneDocumento(estadoPeticion: string): boolean {
  return ESTADOS_CON_DOCUMENTO.includes(estadoPeticion)
}

const PRESENTACION_ESTADO: Record<string, { label: string; variant: BadgeVariant }> = {
  PENDIENTE: { label: 'Pendiente', variant: 'neutral' },
  SOLICITADO: { label: 'Solicitado', variant: 'info' },
  CARGADO: { label: 'Cargado', variant: 'success' },
  LEGALIZADO: { label: 'Legalizado', variant: 'success' },
  VERIFICADO: { label: 'Verificado', variant: 'success' },
  OBSERVADO: { label: 'Observado', variant: 'warning' },
}

/** Etiqueta legible del estado real; un valor desconocido se muestra tal cual, sin inventar. */
export function presentarEstadoPeticion(estado: string): { label: string; variant: BadgeVariant } {
  return PRESENTACION_ESTADO[estado] ?? { label: estado, variant: 'neutral' }
}
