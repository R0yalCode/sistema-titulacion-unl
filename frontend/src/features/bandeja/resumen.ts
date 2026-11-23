import type { BandejaOperativaItem } from '@/api/endpoints/expedientes'
import { presentarEstado } from '@/lib/estados'
import { calcularVencimiento } from './bandejaReglas'

/**
 * Indicadores del panel del funcionario calculados SOLO con los expedientes
 * reales de su bandeja. `completo` indica si se recibieron todos (el resumen
 * se pide con el tamaño máximo de página que admite el backend, 50): si la
 * bandeja es mayor, no se presentan cifras parciales como si fueran totales.
 */
export type ResumenBandeja = {
  total: number
  completo: boolean
  vencidos: number
  vencenHoy: number
  porEstado: Array<{ estado: string; label: string; cantidad: number }>
}

export function resumirBandeja(items: BandejaOperativaItem[], total: number, ahora: Date): ResumenBandeja {
  const conteo = new Map<string, number>()
  let vencidos = 0
  let vencenHoy = 0
  for (const item of items) {
    conteo.set(item.estado, (conteo.get(item.estado) ?? 0) + 1)
    const vencimiento = calcularVencimiento(item.fecha_limite_atencion, ahora)
    if (vencimiento.tipo === 'vencido') {
      vencidos += 1
    } else if (vencimiento.tipo === 'hoy') {
      vencenHoy += 1
    }
  }
  return {
    total,
    completo: items.length >= total,
    vencidos,
    vencenHoy,
    porEstado: [...conteo.entries()]
      .map(([estado, cantidad]) => ({ estado, label: presentarEstado('expediente', estado).label, cantidad }))
      .sort((a, b) => b.cantidad - a.cantidad),
  }
}

export type AccionRapida = { label: string; estado: string; descripcion: string }

export type ContextoRol = {
  titulo: string
  subtitulo: string
  accionesRapidas: AccionRapida[]
}

/**
 * Textos y accesos rápidos por rol. Las acciones rápidas solo aplican el
 * filtro de estado existente sobre estados que el backend incluye en la
 * bandeja de ese rol (`MAPA_INTERVENCION_POR_ROL`).
 */
export function contextoRol(roles: string[]): ContextoRol {
  if (roles.includes('SECRETARIO_ABOGADO')) {
    return {
      titulo: 'Verificación de expedientes',
      subtitulo: 'Expedientes de su facultad que requieren verificación, observación o informe.',
      accionesRapidas: [
        { label: 'Por iniciar verificación', estado: 'ENVIADA', descripcion: 'Expedientes enviados' },
        { label: 'En verificación', estado: 'EN_VERIFICACION', descripcion: 'Checklist en curso' },
        { label: 'Con observaciones', estado: 'OBSERVADA', descripcion: 'Esperan subsanación' },
      ],
    }
  }
  if (roles.includes('ANALISTA_APOYO')) {
    return {
      titulo: 'Apoyo a la verificación',
      subtitulo: 'Expedientes de su facultad en los que puede apoyar la revisión.',
      accionesRapidas: [
        { label: 'Enviados', estado: 'ENVIADA', descripcion: 'Pendientes de verificación' },
        { label: 'En verificación', estado: 'EN_VERIFICACION', descripcion: 'Checklist en curso' },
        { label: 'Con observaciones', estado: 'OBSERVADA', descripcion: 'Esperan subsanación' },
      ],
    }
  }
  if (roles.includes('DECANO')) {
    return {
      titulo: 'Decisiones pendientes',
      subtitulo: 'Expedientes con informe emitido que esperan la declaratoria de aptitud.',
      accionesRapidas: [{ label: 'Informes por resolver', estado: 'INFORME_EMITIDO', descripcion: 'Requieren declaratoria' }],
    }
  }
  if (roles.includes('ADMINISTRADOR')) {
    return {
      titulo: 'Supervisión del trámite',
      subtitulo: 'Vista integral de los expedientes en curso y acceso a la consola de administración.',
      accionesRapidas: [
        { label: 'Enviados', estado: 'ENVIADA', descripcion: 'Esperan verificación' },
        { label: 'Con observaciones', estado: 'OBSERVADA', descripcion: 'Esperan subsanación' },
        { label: 'Informes emitidos', estado: 'INFORME_EMITIDO', descripcion: 'Esperan declaratoria' },
      ],
    }
  }
  if (roles.includes('DIRECTOR_CARRERA')) {
    return {
      titulo: 'Seguimiento de la carrera',
      subtitulo: 'Consulta de los expedientes de su carrera (solo lectura).',
      accionesRapidas: [],
    }
  }
  return {
    titulo: 'Gestión documental de la carrera',
    subtitulo: 'Documentos asignados a la Secretaría de carrera y avisos del sistema.',
    accionesRapidas: [],
  }
}
