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
}

export function Timeline({ steps }: TimelineProps) {
  return (
    <ol className={styles.list}>
      {steps.map((step) => (
        <li
          aria-current={step.status === 'current' ? 'step' : undefined}
          className={styles.item}
          key={step.id}
        >
          <span aria-hidden="true" className={[styles.marker, styles[step.status]].join(' ')} />
          <div>
            <p className={styles.label}>{step.label}</p>
            {step.date && <p className={styles.date}>{step.date}</p>}
          </div>
        </li>
      ))}
    </ol>
  )
}
