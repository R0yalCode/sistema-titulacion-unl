import { Link } from 'react-router-dom'
import type { RecentExpediente } from '@/lib/storage'
import { Badge } from '@/components/ui/Badge'
import { formatFecha } from '@/lib/dates'
import styles from './AccesosRapidos.module.css'

type AccesosRapidosProps = {
  recent: RecentExpediente[]
  bandejaIds: Set<string> | null
}

export function AccesosRapidos({ recent, bandejaIds }: AccesosRapidosProps) {
  return (
    <div className={styles.wrapper}>
      <p className={styles.disclaimer}>
        Estos accesos rápidos recuerdan, solo en este navegador, los expedientes que visitó. No sustituyen un
        historial oficial del estudiante (limitación del backend).
      </p>
      {recent.length === 0 ? (
        <p className={styles.empty}>Todavía no ha visitado ningún expediente en esta sesión.</p>
      ) : (
        <ul className={styles.list}>
          {recent.map((entry) => {
            const faltaEnBandeja = bandejaIds !== null && !bandejaIds.has(entry.id)
            return (
              <li className={styles.item} key={entry.id}>
                <Link to={`/expedientes/${entry.id}`}>{entry.numeroExpediente ?? entry.id}</Link>
                <span className={styles.meta}>Visitado: {formatFecha(entry.visitadoEn)}</span>
                {faltaEnBandeja && (
                  <Badge variant="neutral">No aparece en su bandeja actual; puede haber cambiado de estado</Badge>
                )}
              </li>
            )
          })}
        </ul>
      )}
    </div>
  )
}
