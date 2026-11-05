import type { EstadoExpediente, ExpedienteDetalle } from '@/api/endpoints/expedientes'
import { Badge, type BadgeVariant } from '@/components/ui/Badge'
import { Timeline, type TimelineStep } from '@/components/ui/Timeline'
import { formatFecha } from '@/lib/dates'
import styles from './ExpedienteHeader.module.css'

const CANONICAL_STATES: EstadoExpediente[] = ['BORRADOR', 'ENVIADA', 'EN_VERIFICACION', 'INFORME_EMITIDO', 'DECLARADA_APTA']

const BADGE_VARIANT_BY_ESTADO: Record<EstadoExpediente, BadgeVariant> = {
  BORRADOR: 'neutral',
  ENVIADA: 'info',
  EN_VERIFICACION: 'info',
  OBSERVADA: 'warning',
  INFORME_EMITIDO: 'success',
  DECLARADA_APTA: 'success',
  CANCELADA: 'danger',
}

/**
 * Construye el timeline solo con los dos datos reales de fecha que expone
 * el backend (`fecha_creacion`, `fecha_recepcion`): `HistorialEstado` existe
 * como modelo, pero `ExpedienteDetalleSerializer` no lo serializa, por lo
 * que no hay fecha real para las transiciones intermedias (FE-T401: "no
 * inventes eventos históricos ni fechas").
 */
function buildTimelineSteps(expediente: ExpedienteDetalle): TimelineStep[] {
  const { estado, fecha_creacion, fecha_recepcion } = expediente

  if (estado === 'CANCELADA') {
    return [
      { id: 'borrador', label: 'Borrador', status: 'completed', date: formatFecha(fecha_creacion) },
      { id: 'cancelada', label: 'Cancelada', status: 'current' },
    ]
  }

  if (estado === 'OBSERVADA') {
    return [
      { id: 'borrador', label: 'Borrador', status: 'completed', date: formatFecha(fecha_creacion) },
      { id: 'enviada', label: 'Enviada', status: 'completed', date: formatFecha(fecha_recepcion) },
      { id: 'en_verificacion', label: 'En verificación', status: 'completed' },
      { id: 'observada', label: 'Observada', status: 'current' },
    ]
  }

  const currentIndex = CANONICAL_STATES.indexOf(estado)
  const labels: Record<string, string> = {
    BORRADOR: 'Borrador',
    ENVIADA: 'Enviada',
    EN_VERIFICACION: 'En verificación',
    INFORME_EMITIDO: 'Informe emitido',
    DECLARADA_APTA: 'Declarada apta',
  }
  const dates: Record<string, string | null> = {
    BORRADOR: fecha_creacion,
    ENVIADA: fecha_recepcion,
  }

  return CANONICAL_STATES.map((step, index) => ({
    id: step.toLowerCase(),
    label: labels[step] as string,
    status: index < currentIndex ? 'completed' : index === currentIndex ? 'current' : 'pending',
    date: dates[step] ? formatFecha(dates[step]) : undefined,
  }))
}

type ExpedienteHeaderProps = {
  expediente: ExpedienteDetalle
}

export function ExpedienteHeader({ expediente }: ExpedienteHeaderProps) {
  return (
    <div className={styles.wrapper}>
      <div className={styles.summary}>
        <h1 className={styles.titulo}>{expediente.numero_expediente}</h1>
        <Badge variant={BADGE_VARIANT_BY_ESTADO[expediente.estado]}>{expediente.estado}</Badge>
      </div>

      <dl className={styles.facts}>
        <div>
          <dt>Creado</dt>
          <dd>{formatFecha(expediente.fecha_creacion)}</dd>
        </div>
        <div>
          <dt>Recepción</dt>
          <dd>{formatFecha(expediente.fecha_recepcion)}</dd>
        </div>
        <div>
          <dt>Límite de atención</dt>
          <dd>{formatFecha(expediente.fecha_limite_atencion)}</dd>
        </div>
        <div>
          <dt>Días laborables acumulados</dt>
          <dd>{expediente.dias_laborables_acumulados}</dd>
        </div>
      </dl>

      <p className={styles.uuidNote}>
        Carrera: <code>{expediente.carrera_id}</code> · Facultad: <code>{expediente.facultad_id}</code>. Se
        muestran como identificadores (UUID); el sistema no tiene todavía un catálogo con sus nombres.
      </p>

      <Timeline steps={buildTimelineSteps(expediente)} />
    </div>
  )
}
