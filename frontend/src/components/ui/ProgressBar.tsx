import styles from './ProgressBar.module.css'

export type ProgressBarProps = {
  /** Valor entre 0 y 100. */
  value: number
  /** Nombre accesible de la barra. */
  label: string
  /** Texto que leen los lectores de pantalla en lugar del porcentaje bruto. */
  valueText?: string
}

export function ProgressBar({ value, label, valueText }: ProgressBarProps) {
  const clamped = Math.min(100, Math.max(0, Math.round(value)))
  return (
    <div
      aria-label={label}
      aria-valuemax={100}
      aria-valuemin={0}
      aria-valuenow={clamped}
      aria-valuetext={valueText}
      className={styles.track}
      role="progressbar"
    >
      <span className={styles.fill} style={{ width: `${clamped}%` }} />
    </div>
  )
}
