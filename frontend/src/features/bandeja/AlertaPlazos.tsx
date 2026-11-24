import { ActionCard, actionCardCtaClass } from '@/components/ui/ActionCard'
import { AlertIcon, ArrowRightIcon, CheckCircleIcon, ClockIcon } from '@/components/ui/icons'
import { UrgencyIndicator } from '@/components/ui/UrgencyIndicator'
import { useResumenBandeja } from './queries'
import { resumirBandeja } from './resumen'

const VENCIDOS = { singular: 'vencido', plural: 'vencidos' }
const HOY = { singular: 'vence hoy', plural: 'vencen hoy' }

function expedientes(cantidad: number): string {
  return cantidad === 1 ? '1 expediente' : `${cantidad} expedientes`
}

/**
 * Tarjeta flotante del hero del funcionario y del administrador. Reutiliza la
 * consulta de resumen de la bandeja (misma clave de caché que los KPI, sin
 * peticiones adicionales) y solo alerta con plazos reales: vencidos o que
 * vencen hoy según `fecha_limite_atencion`. Si la bandeja supera la página de
 * resumen no hay cifras completas, así que no se muestra.
 */
export function AlertaPlazos() {
  const query = useResumenBandeja()
  if (!query.data || query.data.count === 0) {
    return null
  }
  const resumen = resumirBandeja(query.data.results, query.data.count, new Date(query.dataUpdatedAt))
  if (!resumen.completo) {
    return null
  }

  const enlace = (
    <a className={actionCardCtaClass} href="#listado-bandeja">
      Ver en el listado <ArrowRightIcon size={16} />
    </a>
  )

  if (resumen.vencidos > 0) {
    return (
      <ActionCard
        action={enlace}
        badge={<UrgencyIndicator count={resumen.vencidos} label={VENCIDOS} />}
        description="Superaron su fecha límite de atención (días calendario). El listado los ordena primero."
        eyebrow="Atención inmediata"
        icon={<AlertIcon />}
        meta={
          resumen.vencenHoy > 0 ? (
            <>
              Además
              <strong>{expedientes(resumen.vencenHoy)} vence hoy</strong>
            </>
          ) : undefined
        }
        title={`${expedientes(resumen.vencidos)} con el plazo vencido`}
        tone="danger"
      />
    )
  }

  if (resumen.vencenHoy > 0) {
    return (
      <ActionCard
        action={enlace}
        badge={<UrgencyIndicator count={resumen.vencenHoy} label={HOY} level="attention" />}
        description="Su fecha límite de atención es hoy."
        eyebrow="Plazos de hoy"
        icon={<ClockIcon />}
        title={`${expedientes(resumen.vencenHoy)} por atender hoy`}
        tone="warning"
      />
    )
  }

  return (
    <ActionCard
      description="Ningún expediente de la bandeja supera su fecha límite de atención."
      eyebrow="Plazos"
      icon={<CheckCircleIcon />}
      title="Plazos al día"
      tone="success"
    />
  )
}
