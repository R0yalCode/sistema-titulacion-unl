import type { ReactNode } from 'react'
import type { EstadoExpediente, ExpedienteDetalle } from '@/api/endpoints/expedientes'
import { CalendarIcon, ClockIcon, FlagIcon, SendIcon } from '@/components/ui/icons'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { Timeline, type TimelineStep } from '@/components/ui/Timeline'
import { formatFecha } from '@/lib/dates'
import styles from './ExpedienteHeader.module.css'

const CANONICAL_STATES: EstadoExpediente[] = ['BORRADOR', 'ENVIADA', 'EN_VERIFICACION', 'INFORME_EMITIDO', 'DECLARADA_APTA']

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
  /** Acciones principales autorizadas para el rol (enviar, observar, iniciar verificación…). */
  actions?: ReactNode
}

export function ExpedienteHeader({ expediente, actions }: ExpedienteHeaderProps) {
  return (
    <div className={styles.wrapper}>
      <section aria-labelledby="expediente-titulo" className={styles.hero}>
        <div className={styles.summary}>
          <div className={styles.identity}>
            <p className={styles.eyebrow}>Expediente de titulación</p>
            <div className={styles.titleRow}>
              <h1 className={styles.titulo} id="expediente-titulo">
                {expediente.numero_expediente}
              </h1>
              <StatusBadge dominio="expediente" valor={expediente.estado} />
            </div>
            {expediente.numero_providencia && (
              <p className={styles.providencia}>Providencia {expediente.numero_providencia}</p>
            )}
          </div>
          {actions && <div className={styles.actions}>{actions}</div>}
        </div>

        <dl className={styles.facts}>
          <div className={styles.fact}>
            <dt>
              <span aria-hidden="true" className={styles.factIcon}>
                <CalendarIcon size={18} />
              </span>
              Creado
            </dt>
            <dd>{formatFecha(expediente.fecha_creacion)}</dd>
          </div>
          <div className={styles.fact}>
            <dt>
              <span aria-hidden="true" className={styles.factIcon}>
                <SendIcon size={18} />
              </span>
              Recepción
            </dt>
            <dd>{formatFecha(expediente.fecha_recepcion)}</dd>
          </div>
          <div className={styles.fact}>
            <dt>
              <span aria-hidden="true" className={styles.factIcon}>
                <FlagIcon size={18} />
              </span>
              Límite de atención
            </dt>
            <dd>{formatFecha(expediente.fecha_limite_atencion)}</dd>
          </div>
          <div className={styles.fact}>
            <dt>
              <span aria-hidden="true" className={styles.factIcon}>
                <ClockIcon size={18} />
              </span>
              Días laborables acumulados
            </dt>
            <dd>{expediente.dias_laborables_acumulados}</dd>
          </div>
        </dl>

        <div className={styles.timeline}>
          <Timeline label="Etapas del expediente" orientation="horizontal" steps={buildTimelineSteps(expediente)} />
        </div>

        <p className={styles.uuidNote}>
          Carrera: <code>{expediente.carrera_id}</code> · Facultad: <code>{expediente.facultad_id}</code>. Se
          muestran como identificadores (UUID); el sistema no tiene todavía un catálogo con sus nombres.
        </p>
      </section>
    </div>
  )
}
