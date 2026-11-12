import type { EstadoExpediente } from '@/api/endpoints/expedientes'

/**
 * Matriz rol × estado × acción de V-08a (FE-T807), basada en reglas
 * verificadas el 2026-11-12 (RBAC, `TRANSICIONES_PERMITIDAS` y servicios). Es
 * solo una ayuda de interfaz: el backend autoriza cada operación.
 *
 * | Acción | Rol | Estado |
 * |---|---|---|
 * | Iniciar verificación (E2-01) | SECRETARIO_ABOGADO | ENVIADA |
 * | Observar | SECRETARIO_ABOGADO | EN_VERIFICACION (`puedeObservar` de V-04) |
 * | Evaluar checklist | SECRETARIO_ABOGADO, ANALISTA_APOYO, ADMINISTRADOR | EN_VERIFICACION (`ChecklistSection`) |
 * | Descargar documentos | todos salvo DECANO (`puedeDescargar`) | con documento |
 */

const ESTADOS_FINALES: EstadoExpediente[] = ['DECLARADA_APTA', 'CANCELADA']

/** FE-T808: estados en los que no se ofrece ninguna acción de escritura. */
export function esEstadoFinal(estado: EstadoExpediente): boolean {
  return ESTADOS_FINALES.includes(estado)
}

/** `POST /expedientes/{id}/iniciar-verificacion/`: RBAC `expedientes:iniciar_verificacion` y transición ENVIADA → EN_VERIFICACION. */
export function puedeIniciarVerificacion(roles: string[], estado: EstadoExpediente): boolean {
  return roles.includes('SECRETARIO_ABOGADO') && estado === 'ENVIADA'
}
