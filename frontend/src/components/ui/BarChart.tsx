import { useId } from 'react'
import type { BadgeVariant } from './Badge'
import styles from './BarChart.module.css'

export type BarDatum = {
  label: string
  value: number
  tone?: BadgeVariant
}

type BarChartProps = {
  title: string
  /** Contexto temporal o de alcance ("Bandeja actual", "Al 19/11/2026"). */
  context: string
  data: BarDatum[]
  unit: string
}

/**
 * Barras horizontales accesibles sin librería: la lista con los valores en
 * texto es la alternativa accesible; las barras son decorativas. Solo debe
 * alimentarse con conteos reales.
 */
export function BarChart({ title, context, data, unit }: BarChartProps) {
  const max = Math.max(1, ...data.map((dato) => dato.value))
  const total = data.reduce((suma, dato) => suma + dato.value, 0)
  const titleId = useId()
  return (
    <figure aria-labelledby={titleId} className={styles.figure}>
      <figcaption className={styles.caption}>
        <span className={styles.title} id={titleId}>
          {title}
        </span>
        <span className={styles.context}>{context}</span>
      </figcaption>
      <ul className={styles.list}>
        {data.map((dato) => (
          <li className={styles.row} key={dato.label}>
            <span className={styles.label}>{dato.label}</span>
            <span aria-hidden="true" className={styles.track}>
              <span
                className={`${styles.bar} ${styles[dato.tone ?? 'info']}`}
                style={{ width: `${(dato.value / max) * 100}%` }}
              />
            </span>
            <span className={styles.value}>
              {dato.value}
              <span className="sr-only">
                {' '}
                {unit} ({total > 0 ? Math.round((dato.value / total) * 100) : 0} %)
              </span>
            </span>
          </li>
        ))}
      </ul>
    </figure>
  )
}
