import type { ReactNode } from 'react'
import styles from './KpiCard.module.css'

export type KpiTone = 'default' | 'warning' | 'success' | 'danger'

/** `glass`: superficie translúcida (capa Liquid Glass) para KPI destacados. */
export type KpiVariant = 'solid' | 'glass'

export type KpiCardProps = {
  title: string
  icon: ReactNode
  tone?: KpiTone
  variant?: KpiVariant
  /** Cifra o valor principal (opcional: algunos KPI son textuales). */
  value?: ReactNode
  /** Unidad junto al valor (%, días…). */
  unit?: string
  children?: ReactNode
  footer?: ReactNode
  headingLevel?: 2 | 3
  /** Ajuste de composición desde la vista que lo usa. */
  className?: string
}

/**
 * Indicador clave. El tono se expresa con la barra lateral y el icono, nunca
 * solo con color: el texto del cuerpo explica el valor.
 */
export function KpiCard({
  title,
  icon,
  tone = 'default',
  variant = 'solid',
  value,
  unit,
  children,
  footer,
  headingLevel = 3,
  className,
}: KpiCardProps) {
  const Heading = headingLevel === 2 ? 'h2' : 'h3'
  return (
    <article
      className={[styles.kpi, styles[tone], variant === 'glass' && `glass-panel ${styles.glass}`, className]
        .filter(Boolean)
        .join(' ')}
      data-variant={variant}
    >
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
