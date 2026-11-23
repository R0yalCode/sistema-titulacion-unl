import type { ReactNode } from 'react'
import styles from './Card.module.css'

export type CardProps = {
  title?: string
  actions?: ReactNode
  children: ReactNode
  /** Nivel del encabezado según la jerarquía de la página (h1 → h2 → h3). */
  headingLevel?: 2 | 3
  icon?: ReactNode
  /** Subtítulo bajo el título. */
  description?: string
  id?: string
}

export function Card({ title, actions, children, headingLevel = 2, icon, description, id }: CardProps) {
  const Heading = headingLevel === 2 ? 'h2' : 'h3'
  const headingId = id && title ? `${id}-titulo` : undefined
  return (
    <section aria-labelledby={headingId} className={styles.card} id={id} tabIndex={id ? -1 : undefined}>
      {(title || actions) && (
        <header className={styles.header}>
          <div className={styles.heading}>
            {title && (
              <Heading className={styles.title} id={headingId}>
                {icon && <span className={styles.icon}>{icon}</span>}
                {title}
              </Heading>
            )}
            {description && <p className={styles.description}>{description}</p>}
          </div>
          {actions && <div className={styles.actions}>{actions}</div>}
        </header>
      )}
      <div className={styles.content}>{children}</div>
    </section>
  )
}
