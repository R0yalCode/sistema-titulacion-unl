import type { ReactNode } from 'react'
import styles from './Card.module.css'

export type CardProps = {
  title?: string
  actions?: ReactNode
  children: ReactNode
}

export function Card({ title, actions, children }: CardProps) {
  return (
    <section className={styles.card}>
      {(title || actions) && (
        <header className={styles.header}>
          {title && <h3 className={styles.title}>{title}</h3>}
          {actions && <div className={styles.actions}>{actions}</div>}
        </header>
      )}
      <div className={styles.content}>{children}</div>
    </section>
  )
}
