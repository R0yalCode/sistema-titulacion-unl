import type { ReactNode } from 'react'
import { LockIcon } from './icons'
import styles from './StateMessage.module.css'

export type ForbiddenStateProps = {
  title?: string
  description?: string
  action?: ReactNode
}

export function ForbiddenState({
  title = 'Acceso restringido',
  description = 'No tiene permisos para ver este contenido.',
  action,
}: ForbiddenStateProps) {
  return (
    <div className={styles.wrapper} role="status">
      <span aria-hidden="true" className={`${styles.icon} ${styles.iconWarning}`}>
        <LockIcon size={24} />
      </span>
      <h2 className={styles.title}>{title}</h2>
      <p className={styles.description}>{description}</p>
      {action}
    </div>
  )
}
