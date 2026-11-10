import type { EstadoExpediente } from '@/api/endpoints/expedientes'
import type { EstadoVerificacion } from '@/api/endpoints/checklist'

/**
 * Matriz ROL × ESTADO × ACCIÓN (FE-T409), basada exclusivamente en reglas
 * verificadas en el backend real (ver INC-21 en `clarify.md` para las
 * discrepancias de código HTTP encontradas). Esta matriz es solo una ayuda
 * de interfaz: nunca sustituye el RBAC del backend, que sigue siendo quien
 * autoriza u deniega cada operación.
 */

const ROLES_VER_CHECKLIST = ['SECRETARIO_ABOGADO', 'ANALISTA_APOYO', 'ADMINISTRADOR']
const ROLES_EVALUAR_CHECKLIST = ['SECRETARIO_ABOGADO', 'ANALISTA_APOYO', 'ADMINISTRADOR']
const ROLES_OBSERVAR = ['SECRETARIO_ABOGADO']
const ROLES_SUBSANAR = ['ESTUDIANTE', 'SECRETARIA_CARRERA', 'ADMINISTRADOR']
const ROLES_DESCARGAR = [
  'ESTUDIANTE',
  'SECRETARIA_CARRERA',
  'SECRETARIO_ABOGADO',
  'ANALISTA_APOYO',
  'DIRECTOR_CARRERA',
  'ADMINISTRADOR',
]

function tieneAlgunRol(roles: string[], permitidos: string[]): boolean {
  return roles.some((rol) => permitidos.includes(rol))
}

/** `GET /expedientes/{id}/checklist/`: ESTUDIANTE no está en la matriz RBAC real → 403. */
export function puedeVerChecklist(roles: string[]): boolean {
  return tieneAlgunRol(roles, ROLES_VER_CHECKLIST)
}

/** `POST /expedientes/{id}/enviar/`: solo el propio estudiante, y solo desde BORRADOR. */
export function puedeEnviar(roles: string[], estado: EstadoExpediente, esPropietario: boolean): boolean {
  return esPropietario && roles.includes('ESTUDIANTE') && estado === 'BORRADOR'
}

/** `POST /expedientes/{id}/observar/`: solo SECRETARIO_ABOGADO, y solo con el expediente EN_VERIFICACION. */
export function puedeObservar(roles: string[], estado: EstadoExpediente): boolean {
  return tieneAlgunRol(roles, ROLES_OBSERVAR) && estado === 'EN_VERIFICACION'
}

/** `PUT /checklist/{id}/`: solo si el expediente está EN_VERIFICACION y el ítem sigue PENDIENTE. */
export function puedeEvaluarItem(
  roles: string[],
  estadoExpediente: EstadoExpediente,
  estadoItem: EstadoVerificacion,
): boolean {
  return tieneAlgunRol(roles, ROLES_EVALUAR_CHECKLIST) && estadoExpediente === 'EN_VERIFICACION' && estadoItem === 'PENDIENTE'
}

/**
 * `POST /checklist/{id}/subsanar/`: requiere el ítem OBSERVADO. El rol debe
 * estar autorizado por RBAC para el POST **y**, en la práctica, solo puede
 * actuar si ya tiene a la vista el `id` real del `ChecklistVerification`
 * (ver limitación documentada para ESTUDIANTE en el informe de FE-T407).
 */
export function puedeSubsanarItem(
  roles: string[],
  estadoExpediente: EstadoExpediente,
  estadoItem: EstadoVerificacion,
  esPropietario: boolean,
): boolean {
  const autorizadoPorRol = roles.includes('ESTUDIANTE')
    ? esPropietario
    : tieneAlgunRol(roles, ROLES_SUBSANAR)
  return autorizadoPorRol && estadoExpediente === 'OBSERVADA' && estadoItem === 'OBSERVADO'
}

/** `GET /peticiones/{id}/documento/`: DECANO queda fuera a propósito (no está en la matriz RBAC real). */
export function puedeDescargar(roles: string[]): boolean {
  return tieneAlgunRol(roles, ROLES_DESCARGAR)
}
