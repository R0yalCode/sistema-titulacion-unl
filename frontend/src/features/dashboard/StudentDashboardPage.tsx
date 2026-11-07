import { useContext, useState } from 'react'
import { AuthContext } from '@/auth/AuthContext'
import { ToastContext } from '@/components/feedback/ToastProvider'
import { Alert } from '@/components/ui/Alert'
import { Card } from '@/components/ui/Card'
import type { BandejaExpediente } from '@/api/endpoints/expedientes'
import { getRecentExpedientes, recordVisitedExpediente } from '@/lib/storage'
import { AccesosRapidos } from './AccesosRapidos'
import { ExpedientesCard } from './ExpedientesCard'
import { NotificacionesCard } from './NotificacionesCard'
import { useBandejaEstudiante, useMarcarNotificacionLeida, useNotificaciones } from './queries'
import styles from './StudentDashboardPage.module.css'

export default function StudentDashboardPage() {
  const auth = useContext(AuthContext)
  const toast = useContext(ToastContext)
  const [page, setPage] = useState(1)
  const [recent, setRecent] = useState(() => getRecentExpedientes())
  const [pendingId, setPendingId] = useState<string | null>(null)

  const bandejaQuery = useBandejaEstudiante(page)
  const notificacionesQuery = useNotificaciones()
  const markReadMutation = useMarcarNotificacionLeida()

  function handleVisit(expediente: BandejaExpediente) {
    recordVisitedExpediente(expediente.id, expediente.numero_expediente)
    setRecent(getRecentExpedientes())
  }

  function handleMarkRead(id: string) {
    setPendingId(id)
    markReadMutation.mutate(id, {
      onError: () => toast?.showToast('No se pudo marcar la notificación como leída. Intente nuevamente.', 'danger'),
      onSettled: () => setPendingId(null),
    })
  }

  const borradorCount = bandejaQuery.isSuccess
    ? bandejaQuery.data.results.filter((expediente) => expediente.estado === 'BORRADOR').length
    : null
  const observadaCount = bandejaQuery.isSuccess
    ? bandejaQuery.data.results.filter((expediente) => expediente.estado === 'OBSERVADA').length
    : null
  const noLeidasCount = notificacionesQuery.isSuccess
    ? notificacionesQuery.data.results.filter((notificacion) => !notificacion.leida).length
    : null
  const bandejaIds = bandejaQuery.isSuccess
    ? new Set(bandejaQuery.data.results.map((expediente) => expediente.id))
    : null
  const isPartial =
    (bandejaQuery.isError && notificacionesQuery.isSuccess) ||
    (notificacionesQuery.isError && bandejaQuery.isSuccess)

  return (
    <main className={styles.page}>
      <h1>Dashboard del estudiante (V-02)</h1>
      <p className={styles.greeting}>Hola, {auth?.user?.cedula ?? 'estudiante'}</p>

      <Alert variant="info">
        Este panel muestra únicamente sus expedientes en estado Borrador u Observada y no incluye su perfil
        completo ni el historial en otros estados (limitación del backend).
      </Alert>

      {isPartial && (
        <p className={styles.partialNotice} role="status">
          Algunos datos no se pudieron cargar. El resto del panel sigue disponible.
        </p>
      )}

      <h2>Resumen</h2>
      <div className={styles.stats}>
        <Card title="En borrador">
          <p className={styles.statNumber}>{borradorCount ?? '—'}</p>
        </Card>
        <Card title="Observadas">
          <p className={styles.statNumber}>{observadaCount ?? '—'}</p>
        </Card>
        <Card title="Notificaciones sin leer">
          <p className={styles.statNumber}>{noLeidasCount ?? '—'}</p>
        </Card>
      </div>

      <Card title="Mis expedientes">
        <ExpedientesCard query={bandejaQuery} page={page} onPageChange={setPage} onVisit={handleVisit} />
      </Card>

      <Card title="Notificaciones">
        <NotificacionesCard pendingId={pendingId} query={notificacionesQuery} onMarkRead={handleMarkRead} />
      </Card>

      <Card title="Accesos rápidos">
        <AccesosRapidos bandejaIds={bandejaIds} recent={recent} />
      </Card>
    </main>
  )
}
