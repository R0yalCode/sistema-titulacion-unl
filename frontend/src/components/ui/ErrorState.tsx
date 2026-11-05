import { Button } from './Button'
import styles from './StateMessage.module.css'

export type ErrorStateProps = {
  title?: string
  description?: string
  onRetry?: () => void
}

export function ErrorState({
  title = 'Ocurrió un error',
  description = 'Intente nuevamente. Si el problema persiste, contacte a soporte.',
  onRetry,
}: ErrorStateProps) {
  return (
    <div aria-live="assertive" className={styles.wrapper} role="alert">
      <h2 className={styles.title}>{title}</h2>
      <p className={styles.description}>{description}</p>
      {onRetry && (
        <Button onClick={onRetry} variant="secondary">
          Reintentar
        </Button>
      )}
    </div>
  )
}
