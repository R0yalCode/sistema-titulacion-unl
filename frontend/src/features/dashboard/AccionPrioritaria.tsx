import { Link } from 'react-router-dom'
import type { ExpedienteResumen } from '@/api/endpoints/miTramite'
import { ActionCard, actionCardCtaClass } from '@/components/ui/ActionCard'
import { AlertIcon, ArrowRightIcon, CheckCircleIcon, FolderIcon, ListCheckIcon } from '@/components/ui/icons'
import { UrgencyIndicator } from '@/components/ui/UrgencyIndicator'
import { formatFecha } from '@/lib/dates'
import type { AccionPendiente } from './presentacion'
import { presentarEstadoExpediente } from './presentacion'

const OBSERVACIONES = { singular: 'observación', plural: 'observaciones' }
const PENDIENTES = { singular: 'pendiente', plural: 'pendientes' }

type AccionPrioritariaProps = {
  expediente: ExpedienteResumen | null
  acciones: AccionPendiente[]
}

/**
 * Tarjeta flotante del hero: responde «¿qué debo hacer ahora?» con la primera
 * acción real de `construirAccionesPendientes` (mismo orden que la lista
 * «Necesitas completar»). La urgencia solo se marca con observaciones
 * pendientes reales del backend: es lo único que exige corregir algo.
 */
export function AccionPrioritaria({ expediente, acciones }: AccionPrioritariaProps) {
  if (!expediente) {
    return (
      <ActionCard
        action={
          <Link className={actionCardCtaClass} to="/estudiante/solicitud/nueva">
            Crear solicitud
          </Link>
        }
        description="Registra tu solicitud para iniciar el proceso. Después podrás gestionar tus documentos y seguir cada etapa desde este panel."
        eyebrow="Primer paso"
        icon={<FolderIcon />}
        title="Aún no tienes un trámite de titulación"
      />
    )
  }

  const [primera] = acciones
  if (!primera) {
    const estado = presentarEstadoExpediente(expediente.estado)
    return (
      <ActionCard
        action={
          <Link className={actionCardCtaClass} to={`/expedientes/${expediente.id}`}>
            Ver mi trámite <ArrowRightIcon size={16} />
          </Link>
        }
        description={estado.descripcion}
        eyebrow="Al día"
        icon={<CheckCircleIcon />}
        title="No tienes acciones pendientes"
        tone="success"
      />
    )
  }

  const observaciones = expediente.observaciones_pendientes.length
  const restantes = acciones.length - 1
  return (
    <ActionCard
      action={
        <Link className={actionCardCtaClass} to={primera.href}>
          {primera.accionLabel} <ArrowRightIcon size={16} />
        </Link>
      }
      badge={
        observaciones > 0 ? (
          <UrgencyIndicator count={observaciones} label={OBSERVACIONES} />
        ) : (
          <UrgencyIndicator count={acciones.length} label={PENDIENTES} level="attention" />
        )
      }
      description={primera.motivo ?? primera.descripcion}
      eyebrow={observaciones > 0 ? 'Corrección requerida' : 'Acción prioritaria'}
      icon={primera.tono === 'warning' ? <AlertIcon /> : <ListCheckIcon />}
      meta={
        primera.fecha ? (
          <>
            Registrada el
            <strong>{formatFecha(primera.fecha)}</strong>
          </>
        ) : restantes > 0 ? (
          <a href="#pendientes">
            {restantes === 1 ? 'Ver 1 acción más' : `Ver ${restantes} acciones más`}
          </a>
        ) : undefined
      }
      title={primera.titulo}
      tone={primera.tono === 'warning' ? 'warning' : 'info'}
    />
  )
}
