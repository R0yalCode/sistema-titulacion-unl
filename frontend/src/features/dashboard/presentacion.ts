import type { EstadoExpediente } from '@/api/endpoints/expedientes'
import type { ExpedienteResumen, MovimientoTramite } from '@/api/endpoints/miTramite'
import type { BadgeVariant } from '@/components/ui/Badge'

/**
 * Presentación del panel del estudiante. Solo traduce a lenguaje claro los
 * datos reales de `GET /expedientes/mi-tramite/`: no calcula etapas, progreso
 * ni completitud (los da el backend) y nunca inventa fechas ni estados.
 */

export type PresentacionEstado = {
  label: string
  descripcion: string
  variant: BadgeVariant
}

const ESTADO_EXPEDIENTE: Record<EstadoExpediente, PresentacionEstado> = {
  BORRADOR: {
    label: 'En preparación',
    descripcion: 'Completa los documentos requeridos y envía tu solicitud.',
    variant: 'neutral',
  },
  ENVIADA: {
    label: 'Solicitud enviada',
    descripcion: 'Tu solicitud fue recibida y espera el inicio de la verificación.',
    variant: 'info',
  },
  EN_VERIFICACION: {
    label: 'En verificación',
    descripcion: 'La facultad está verificando tus requisitos.',
    variant: 'info',
  },
  OBSERVADA: {
    label: 'Con observaciones',
    descripcion: 'Hay requisitos que necesitas corregir para continuar.',
    variant: 'warning',
  },
  INFORME_EMITIDO: {
    label: 'Informe emitido',
    descripcion: 'Se emitió el informe de verificación; falta la declaratoria de aptitud.',
    variant: 'info',
  },
  DECLARADA_APTA: {
    label: 'Declarado apto',
    descripcion: 'Tu trámite concluyó con la declaratoria de aptitud.',
    variant: 'success',
  },
  CANCELADA: {
    label: 'Cancelado',
    descripcion: 'Este trámite fue cancelado y ya no avanza.',
    variant: 'danger',
  },
}

export function presentarEstadoExpediente(estado: string): PresentacionEstado {
  return (
    ESTADO_EXPEDIENTE[estado as EstadoExpediente] ?? {
      label: estado,
      descripcion: `Estado informado por el sistema: ${estado}.`,
      variant: 'neutral',
    }
  )
}

export function porcentajeProgreso(expediente: ExpedienteResumen): number | null {
  const progreso = expediente.progreso
  if (!progreso || progreso.etapas_totales <= 0) {
    return null
  }
  return Math.round((progreso.etapas_completadas / progreso.etapas_totales) * 100)
}

// --- Acciones pendientes ---------------------------------------------------

export type AccionPendiente = {
  id: string
  titulo: string
  descripcion: string
  motivo?: string
  fecha?: string
  tono: 'warning' | 'info'
  href: string
  accionLabel: string
}

const DESCRIPCION_REQUISITO: Record<string, string> = {
  PENDIENTE: 'Solicita su emisión a la dependencia o carga el documento.',
  SOLICITADO: 'La emisión ya fue solicitada. Carga el documento cuando lo recibas.',
  OBSERVADO: 'El documento fue observado. Carga una versión corregida.',
  CANCELADA: 'La petición fue cancelada. Revisa el detalle del requisito.',
}

/**
 * Cada acción aparece una sola vez: una observación pendiente y el requisito
 * sin documento de la misma petición se cuentan como una única acción.
 */
export function construirAccionesPendientes(expediente: ExpedienteResumen | null): AccionPendiente[] {
  if (!expediente) {
    return [
      {
        id: 'registrar-solicitud',
        titulo: 'Registra tu solicitud de titulación',
        descripcion: 'Todavía no tienes un trámite registrado. Créalo para empezar.',
        tono: 'info',
        href: '/estudiante/solicitud/nueva',
        accionLabel: 'Crear solicitud',
      },
    ]
  }

  const acciones: AccionPendiente[] = []
  const atendidas = new Set<string>()
  const baseDocumento = `/expedientes/${expediente.id}/peticiones`

  for (const observacion of expediente.observaciones_pendientes) {
    atendidas.add(observacion.peticion_id)
    acciones.push({
      id: `observacion-${observacion.id}`,
      titulo: `Corrige el documento: ${observacion.requisito_nombre}`,
      descripcion: 'El documento requiere una corrección. Consulta el detalle y carga una nueva versión.',
      motivo: observacion.motivo_observacion,
      fecha: observacion.fecha_registro,
      tono: 'warning',
      href: `${baseDocumento}/${observacion.peticion_id}`,
      accionLabel: 'Ver y corregir',
    })
  }

  if (expediente.estado === 'BORRADOR') {
    const sinDocumento = new Set(expediente.requisitos_sin_documento)
    for (const peticion of expediente.peticiones) {
      if (!sinDocumento.has(peticion.id) || atendidas.has(peticion.id)) {
        continue
      }
      atendidas.add(peticion.id)
      acciones.push({
        id: `requisito-${peticion.id}`,
        titulo: `Completa el documento: ${peticion.requisito_nombre}`,
        descripcion:
          DESCRIPCION_REQUISITO[peticion.estado_peticion] ?? 'Este requisito todavía no tiene un documento en firme.',
        tono: peticion.estado_peticion === 'OBSERVADO' ? 'warning' : 'info',
        href: `${baseDocumento}/${peticion.id}`,
        accionLabel: 'Gestionar documento',
      })
    }

    if (expediente.puede_enviarse) {
      acciones.push({
        id: 'enviar-solicitud',
        titulo: 'Envía tu solicitud',
        descripcion: 'Todos los requisitos tienen documento. Revisa tu expediente y envíalo para su verificación.',
        tono: 'info',
        href: `/expedientes/${expediente.id}`,
        accionLabel: 'Revisar y enviar',
      })
    }
  }

  // El backend devuelve primero el expediente activo: si el devuelto está
  // inactivo, no hay ninguno activo y `POST /expedientes/` lo permite (HU-001).
  if (!expediente.activa) {
    acciones.push({
      id: 'registrar-solicitud',
      titulo: 'Registra una nueva solicitud',
      descripcion: 'Tu trámite anterior ya no está activo. Puedes registrar una nueva solicitud de titulación.',
      tono: 'info',
      href: '/estudiante/solicitud/nueva',
      accionLabel: 'Crear solicitud',
    })
  }

  return acciones
}

// --- Próximo hito ----------------------------------------------------------

export type ProximoHito = {
  nombre: string
  contexto: string
  fecha: string | null
  fechaLabel: string | null
}

const CONTEXTO_HITO: Partial<Record<EstadoExpediente, string>> = {
  BORRADOR: 'Se alcanza cuando envías tu solicitud con todos los requisitos completos.',
  ENVIADA: 'La facultad iniciará la verificación de tus requisitos.',
  EN_VERIFICACION: 'Al concluir la verificación se emite el informe correspondiente.',
  OBSERVADA: 'La verificación continúa cuando corrijas los documentos observados.',
  INFORME_EMITIDO: 'El Decanato emite la declaratoria de aptitud.',
}

const ESTADOS_CON_PLAZO: EstadoExpediente[] = ['ENVIADA', 'EN_VERIFICACION']

/** Siguiente etapa real del flujo; `null` si el trámite concluyó o no avanza. */
export function calcularProximoHito(expediente: ExpedienteResumen | null): ProximoHito | null {
  if (!expediente || expediente.progreso === null) {
    return null
  }
  const siguiente = expediente.etapas.find((etapa) => etapa.situacion === 'pendiente')
  if (!siguiente) {
    return null
  }
  // La fecha límite es el plazo institucional de atención que fija el backend
  // al recibir la solicitud; solo se muestra mientras corre.
  const conPlazo = ESTADOS_CON_PLAZO.includes(expediente.estado) && expediente.fecha_limite_atencion !== null
  return {
    nombre: siguiente.nombre,
    contexto: CONTEXTO_HITO[expediente.estado] ?? '',
    fecha: conPlazo ? expediente.fecha_limite_atencion : null,
    fechaLabel: conPlazo ? 'Fecha límite de atención institucional' : null,
  }
}

// --- Movimientos -----------------------------------------------------------

export type MovimientoPresentado = {
  titulo: string
  descripcion: string
  tono: 'success' | 'info' | 'warning' | 'neutral' | 'danger'
}

export function describirMovimiento(movimiento: MovimientoTramite): MovimientoPresentado {
  switch (movimiento.tipo) {
    case 'creacion':
      return { titulo: 'Solicitud registrada', descripcion: 'Se creó tu expediente de titulación.', tono: 'neutral' }
    case 'documento_cargado':
      return {
        titulo: 'Documento cargado',
        descripcion: `${movimiento.requisito_nombre ?? 'Requisito'}${
          movimiento.version && movimiento.version > 1 ? ` (versión ${movimiento.version})` : ''
        }`,
        tono: 'info',
      }
    case 'observacion':
      return {
        titulo: 'Observación registrada',
        descripcion: movimiento.requisito_nombre ?? 'Un requisito fue observado.',
        tono: 'warning',
      }
    case 'cambio_estado': {
      const nuevo = presentarEstadoExpediente(movimiento.estado_nuevo ?? '')
      const subsanado = movimiento.estado_anterior === 'OBSERVADA' && movimiento.estado_nuevo === 'EN_VERIFICACION'
      return {
        titulo: subsanado ? 'Observaciones atendidas' : `Estado: ${nuevo.label}`,
        descripcion: subsanado ? 'Tu trámite volvió a verificación.' : nuevo.descripcion,
        tono: nuevo.variant === 'neutral' ? 'info' : nuevo.variant,
      }
    }
  }
}
