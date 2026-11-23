import { useId, type ReactNode } from 'react'
import styles from './KpiGrid.module.css'

type KpiGridProps = {
  /** Título de la región: se expone como h2 visualmente oculto (h1 → h2 → h3 de cada KPI). */
  label: string
  columns?: 3 | 4
  children: ReactNode
}

export function KpiGrid({ label, columns = 4, children }: KpiGridProps) {
  const headingId = useId()
  return (
    <section aria-labelledby={headingId} className={`${styles.grid} ${columns === 3 ? styles.grid3 : ''}`}>
      <h2 className="sr-only" id={headingId}>
        {label}
      </h2>
      {children}
    </section>
  )
}
