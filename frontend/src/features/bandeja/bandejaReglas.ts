import type { EstadoExpediente } from '@/api/endpoints/expedientes'

/**
 * Espejo de solo lectura de `MAPA_INTERVENCION_POR_ROL`
 * (`backend/src/apps/expedientes/adapters/views.py`, verificado 2026-11-12).
 * Solo se usa para explicar una bandeja vacía: quien filtra es el backend.
 */
const ESTADOS_POR_ROL: Record<string, EstadoExpediente[]> = {
  SECRETARIO_ABOGADO: ['ENVIADA', 'EN_VERIFICACION', 'OBSERVADA'],
  ANALISTA_APOYO: ['ENVIADA', 'EN_VERIFICACION', 'OBSERVADA'],
  DECANO: ['INFORME_EMITIDO'],
  ADMINISTRADOR: ['BORRADOR', 'ENVIADA', 'EN_VERIFICACION', 'OBSERVADA', 'INFORME_EMITIDO'],
  SECRETARIA_CARRERA: [],
  DIRECTOR_CARRERA: [],
}

/** Estados que el backend incluye en la bandeja para los roles del usuario. */
export function estadosAtendidos(roles: string[]): EstadoExpediente[] {
  const estados = new Set<EstadoExpediente>()
  for (const rol of roles) {
    for (const estado of ESTADOS_POR_ROL[rol] ?? []) {
      estados.add(estado)
    }
  }
  return [...estados]
}

/**
 * Mensaje de bandeja vacía (FE-T704, CA-V07-03). Distingue el rol que nunca
 * recibe expedientes en la bandeja (BE-09) del rol que simplemente no tiene
 * expedientes pendientes en este momento.
 */
export function explicarBandejaVacia(roles: string[]): { titulo: string; descripcion: string } {
  const estados = estadosAtendidos(roles)
  if (estados.length === 0) {
    return {
      titulo: 'Su rol no tiene expedientes en la bandeja',
      descripcion:
        'La bandeja del sistema no asigna expedientes a su rol por ahora (dependencia BE-09). Puede consultar un expediente desde su enlace directo.',
    }
  }
  return {
    titulo: 'No hay expedientes pendientes',
    descripcion: `No hay expedientes en los estados que atiende su rol (${estados.join(', ')}).`,
  }
}

export type Vencimiento =
  | { tipo: 'sin-fecha' }
  | { tipo: 'vencido'; dias: number }
  | { tipo: 'hoy' }
  | { tipo: 'pendiente'; dias: number }

function inicioDelDia(fecha: Date): number {
  return new Date(fecha.getFullYear(), fecha.getMonth(), fecha.getDate()).getTime()
}

const MS_POR_DIA = 24 * 60 * 60 * 1000

/**
 * FE-T704: cálculo local sobre `fecha_limite_atencion` (specify.md, V-07).
 * Solo hechos exactos, sin un umbral de "próximo a vencer" que la spec no
 * define: vencido, vence hoy o días **calendario** restantes. El backend
 * computa los plazos en días laborables (COA Art. 160); esto es una ayuda
 * visual y no sustituye ese cómputo.
 */
export function calcularVencimiento(fechaLimite: string | null, ahora: Date = new Date()): Vencimiento {
  if (!fechaLimite) {
    return { tipo: 'sin-fecha' }
  }
  const limite = new Date(fechaLimite)
  if (Number.isNaN(limite.getTime())) {
    return { tipo: 'sin-fecha' }
  }
  if (limite.getTime() < ahora.getTime()) {
    const dias = Math.round((inicioDelDia(ahora) - inicioDelDia(limite)) / MS_POR_DIA)
    return dias === 0 ? { tipo: 'vencido', dias: 0 } : { tipo: 'vencido', dias }
  }
  const dias = Math.round((inicioDelDia(limite) - inicioDelDia(ahora)) / MS_POR_DIA)
  return dias === 0 ? { tipo: 'hoy' } : { tipo: 'pendiente', dias }
}

/** Identificador abreviado: la bandeja solo trae UUID, nunca nombres (BE-01/BE-05). */
export function abreviarId(id: string | null): string {
  return id ? id.slice(0, 8) : '—'
}
