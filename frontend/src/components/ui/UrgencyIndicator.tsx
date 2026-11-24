import styles from './UrgencyIndicator.module.css'

export type UrgencyLevel = 'critical' | 'attention'

export type UrgencyIndicatorProps = {
  /** Cantidad real que origina la alerta (p. ej. expedientes con plazo vencido). */
  count: number
  /** Texto en singular y plural: «vencido» / «vencidos». */
  label: { singular: string; plural: string }
  /**
   * `critical`: urgencia verificable (plazo vencido, documento observado); el
   * punto pulsa unas pocas veces. `attention`: pendiente sin urgencia, sin pulso.
   */
  level?: UrgencyLevel
  className?: string
}

/**
 * Indicador de alerta con microanimación (punto + contador + texto). Solo se
 * muestra con una cantidad real mayor que cero: no hay cifras de ejemplo. La
 * urgencia se comunica con texto y forma, nunca solo con el color rojo, y el
 * pulso respeta prefers-reduced-motion (ver styles/glass.css).
 */
export function UrgencyIndicator({ count, label, level = 'critical', className }: UrgencyIndicatorProps) {
  if (!Number.isFinite(count) || count <= 0) {
    return null
  }
  const texto = `${count} ${count === 1 ? label.singular : label.plural}`
  const pulsa = level === 'critical'
  return (
    <span
      className={[styles.indicator, styles[level], className].filter(Boolean).join(' ')}
      data-level={level}
      data-pulse={pulsa ? 'true' : 'false'}
    >
      <span aria-hidden="true" className={styles.dot}>
        {pulsa && <span className={styles.ring} />}
      </span>
      <span className={styles.text}>{texto}</span>
    </span>
  )
}
