import type { ReactNode } from 'react'
import styles from './KpiCard.module.css'

export type KpiTone = 'default' | 'warning' | 'success' | 'danger'

export type KpiCardProps = {
  title: string
  icon: ReactNode
  tone?: KpiTone
  /** Cifra o valor principal (opcional: algunos KPI son textuales). */
  value?: ReactNode
  /** Unidad junto al valor (%, días…). */
  unit?: string
  children?: ReactNode
  footer?: ReactNode
  headingLevel?: 2 | 3
}

/**
 * Indicador clave. El tono se expresa con la barra lateral y el icono, nunca
 * solo con color: el texto del cuerpo explica el valor.
 */
export function KpiCard({ title, icon, tone = 'default', value, unit, children, footer, headingLevel = 3 }: KpiCardProps) {
  const Heading = headingLevel === 2 ? 'h2' : 'h3'
  return (
    <article className={`${styles.kpi} ${styles[tone]}`}>
      <header className={styles.header}>
        <span aria-hidden="true" className={styles.icon}>
          {icon}
        </span>
        <Heading className={styles.title}>{title}</Heading>
      </header>
      <div className={styles.body}>
        {value !== undefined && (
          <p className={styles.value}>
            {value}
            {unit && <span className={styles.unit}>{unit}</span>}
          </p>
        )}
        {children}
      </div>
      {footer && <div className={styles.footer}>{footer}</div>}
    </article>
  )
}

/** Texto secundario dentro de un KPI. */
export function KpiText({ children }: { children: ReactNode }) {
  return <p className={styles.text}>{children}</p>
}

/** Enlace de acción al pie de un KPI (clase compartida). */
export const kpiLinkClass = styles.link
