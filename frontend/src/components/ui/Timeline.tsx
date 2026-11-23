import styles from './Timeline.module.css'

export type TimelineStepStatus = 'completed' | 'current' | 'pending'

export type TimelineStep = {
  id: string
  label: string
  status: TimelineStepStatus
  date?: string
}

export type TimelineProps = {
  steps: TimelineStep[]
  /** `horizontal` en escritorio; en ≤768 px siempre se apila en vertical. */
  orientation?: 'vertical' | 'horizontal'
  /** Nombre accesible de la lista de etapas. */
  label?: string
}

const ESTADO_TEXTO: Record<TimelineStepStatus, string> = {
  completed: 'completada',
  current: 'etapa actual',
  pending: 'pendiente',
}

export function Timeline({ steps, orientation = 'vertical', label }: TimelineProps) {
  return (
    <ol aria-label={label} className={`${styles.list} ${orientation === 'horizontal' ? styles.horizontal : ''}`}>
      {steps.map((step) => (
        <li
          aria-current={step.status === 'current' ? 'step' : undefined}
          className={styles.item}
          key={step.id}
        >
          <span aria-hidden="true" className={[styles.marker, styles[step.status]].join(' ')} />
          <div>
            <p className={styles.label}>
              {step.label}
              <span className="sr-only">: {ESTADO_TEXTO[step.status]}</span>
            </p>
            {step.date && <p className={styles.date}>{step.date}</p>}
          </div>
        </li>
      ))}
    </ol>
  )
}
