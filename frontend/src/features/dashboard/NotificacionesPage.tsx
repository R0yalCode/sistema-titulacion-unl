import { useContext, useState } from 'react'
import { ToastContext } from '@/components/feedback/ToastProvider'
import { BellIcon } from '@/components/ui/icons'
import { NotificacionesCard } from './NotificacionesCard'
import { Card } from '@/components/ui/Card'
import { useMarcarNotificacionLeida, useNotificaciones } from './queries'
import styles from './StudentPages.module.css'

type NotificacionesPageProps = {
  /** Destino del expediente relacionado en el portal del rol. */
  expedienteHref?: (expedienteId: string) => string
}

/**
 * Notificaciones reales del usuario autenticado (`GET /notificaciones/`; el
 * backend filtra por `usuario_destino`). La usan el estudiante
 * (`/estudiante/notificaciones`) y los funcionarios con celda RBAC (`/notificaciones`).
 */
export default function NotificacionesPage({ expedienteHref = (id) => `/expedientes/${id}` }: NotificacionesPageProps) {
  const toast = useContext(ToastContext)
  const query = useNotificaciones()
  const markRead = useMarcarNotificacionLeida()
  const [pendingId, setPendingId] = useState<string | null>(null)

  function handleMarkRead(id: string) {
    setPendingId(id)
    markRead.mutate(id, {
      onError: () => toast?.showToast('No se pudo marcar la notificación como leída. Intente nuevamente.', 'danger'),
      onSettled: () => setPendingId(null),
    })
  }

  const noLeidas = query.data?.results.filter((notificacion) => !notificacion.leida).length ?? 0

  return (
    <div className={styles.page}>
      <header>
        <h1 className={styles.title}>Notificaciones</h1>
        <p className={styles.subtitle}>
          {query.isSuccess
            ? noLeidas > 0
              ? `Tienes ${noLeidas} ${noLeidas === 1 ? 'notificación sin leer' : 'notificaciones sin leer'}.`
              : 'Estás al día: no tienes notificaciones sin leer.'
            : 'Avisos sobre los cambios en los expedientes.'}
        </p>
      </header>
      <Card icon={<BellIcon />} title="Bandeja de notificaciones">
        <NotificacionesCard
          expedienteHref={expedienteHref}
          pendingId={pendingId}
          query={query}
          onMarkRead={handleMarkRead}
        />
      </Card>
    </div>
  )
}
