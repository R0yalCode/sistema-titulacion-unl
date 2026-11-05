import type { ReactNode } from 'react'
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
      <h2 className={styles.title}>{title}</h2>
      <p className={styles.description}>{description}</p>
      {action}
    </div>
  )
}
