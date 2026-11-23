import type { ReactNode } from 'react'
import { InboxIcon } from './icons'
import styles from './StateMessage.module.css'

export type EmptyStateProps = {
  title: string
  description?: string
  action?: ReactNode
}

export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <div className={styles.wrapper} role="status">
      <span aria-hidden="true" className={`${styles.icon} ${styles.iconNeutral}`}>
        <InboxIcon size={24} />
      </span>
      <h2 className={styles.title}>{title}</h2>
      {description && <p className={styles.description}>{description}</p>}
      {action}
    </div>
  )
}
