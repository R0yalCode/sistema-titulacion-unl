import type { ReactNode } from 'react'
import { SearchIcon } from './icons'
import styles from './StateMessage.module.css'

export type NotFoundStateProps = {
  title?: string
  description?: string
  action?: ReactNode
}

export function NotFoundState({
  title = 'No encontrado',
  description = 'El recurso solicitado no existe o no está disponible.',
  action,
}: NotFoundStateProps) {
  return (
    <div className={styles.wrapper} role="status">
      <span aria-hidden="true" className={`${styles.icon} ${styles.iconNeutral}`}>
        <SearchIcon size={24} />
      </span>
      <h2 className={styles.title}>{title}</h2>
      <p className={styles.description}>{description}</p>
      {action}
    </div>
  )
}
