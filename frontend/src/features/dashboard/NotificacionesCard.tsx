import type { UseQueryResult } from '@tanstack/react-query'
import type { ListNotificacionesResponse } from '@/api/endpoints/notificaciones'
import type { ApiRequestError } from '@/api/errors'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { EmptyState } from '@/components/ui/EmptyState'
import { ErrorState } from '@/components/ui/ErrorState'
import { ForbiddenState } from '@/components/ui/ForbiddenState'
import { Spinner } from '@/components/ui/Spinner'
import { presentApiError } from '@/lib/apiErrorPresentation'
import { formatFecha } from '@/lib/dates'
import styles from './NotificacionesCard.module.css'

type NotificacionesCardProps = {
  query: UseQueryResult<ListNotificacionesResponse, ApiRequestError>
  onMarkRead: (id: string) => void
  pendingId: string | null
}

export function NotificacionesCard({ query, onMarkRead, pendingId }: NotificacionesCardProps) {
  if (query.isError) {
    const presentation = presentApiError(query.error)
    if (presentation.kind === 'forbidden') {
      return <ForbiddenState description={presentation.description} title={presentation.title} />
    }
    return (
      <ErrorState
        description={presentation.description}
        title={presentation.title}
        onRetry={() => query.refetch()}
      />
    )
  }

  if (query.isLoading) {
    return <Spinner label="Cargando notificaciones…" />
  }

  const results = query.data?.results ?? []
  if (results.length === 0) {
    return <EmptyState description="No tiene notificaciones registradas." title="Sin notificaciones" />
  }

  return (
    <ul className={styles.list}>
      {results.map((notificacion) => (
        <li className={styles.item} key={notificacion.id}>
          <div className={styles.itemHeader}>
            <strong>{notificacion.titulo}</strong>
            {!notificacion.leida && <Badge variant="info">No leída</Badge>}
          </div>
          <p className={styles.message}>{notificacion.mensaje}</p>
          <div className={styles.itemFooter}>
            <span className={styles.meta}>
              {notificacion.expediente_numero} · {formatFecha(notificacion.fecha_creacion)}
            </span>
            {!notificacion.leida && (
              <Button
                disabled={pendingId === notificacion.id}
                loading={pendingId === notificacion.id}
                size="sm"
                variant="secondary"
                onClick={() => onMarkRead(notificacion.id)}
              >
                Marcar como leída
              </Button>
            )}
          </div>
        </li>
      ))}
    </ul>
  )
}
