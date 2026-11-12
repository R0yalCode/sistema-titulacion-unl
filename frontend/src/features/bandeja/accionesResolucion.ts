import type { ChecklistItem } from '@/api/endpoints/checklist'
import type { EstadoExpediente } from '@/api/endpoints/expedientes'

/**
 * Matriz de V-08b (FE-T804/FE-T805), verificada el 2026-11-12 contra RBAC,
 * `TRANSICIONES_PERMITIDAS` y los servicios. Solo ayuda de interfaz.
 *
 * | Acción | Rol | Estado | Nota |
 * |---|---|---|---|
 * | Emitir informe | SECRETARIO_ABOGADO | EN_VERIFICACION | checklist 100 % VERIFICADO; desde OBSERVADA el backend responde 409 (O-1) |
 * | Declarar aptitud | DECANO | INFORME_EMITIDO | memorando firmado en PDF |
 */

export function puedeEmitirInforme(roles: string[], estado: EstadoExpediente): boolean {
  return roles.includes('SECRETARIO_ABOGADO') && estado === 'EN_VERIFICACION'
}

/** RN-003: el informe exige todos los ítems del checklist en VERIFICADO. */
export function checklistCompleto(items: ChecklistItem[] | undefined): boolean {
  return items !== undefined && items.length > 0 && items.every((item) => item.estado_verificacion === 'VERIFICADO')
}

export function puedeDeclararAptitud(roles: string[], estado: EstadoExpediente): boolean {
  return roles.includes('DECANO') && estado === 'INFORME_EMITIDO'
}
