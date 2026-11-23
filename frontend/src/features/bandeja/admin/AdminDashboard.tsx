import { useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Badge, type BadgeVariant } from '@/components/ui/Badge'
import { BarChart } from '@/components/ui/BarChart'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { ErrorState } from '@/components/ui/ErrorState'
import {
  AlertIcon,
  ArrowRightIcon,
  BellIcon,
  ChartIcon,
  ClockIcon,
  FilterIcon,
  InboxIcon,
  RefreshIcon,
} from '@/components/ui/icons'
import { KpiCard, KpiText } from '@/components/ui/KpiCard'
import { Skeleton } from '@/components/ui/Skeleton'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { useNotificaciones } from '@/features/dashboard'
import { presentApiError } from '@/lib/apiErrorPresentation'
import { formatFecha, formatFechaHora } from '@/lib/dates'
import { presentarEstado } from '@/lib/estados'
import { calcularVencimiento, type Vencimiento } from '../bandejaReglas'
import { PanelAdministracion } from '../PanelesInicio'
import { BANDEJA_OPERATIVA_QUERY_KEY, useResumenBandeja } from '../queries'
import { resumirBandeja, type AccionRapida } from '../resumen'
import styles from './AdminDashboard.module.css'

const MAX_PRIORITARIOS = 5
const MAX_ACTIVIDAD = 5

function presentarPlazo(vencimiento: Vencimiento): { texto: string; variant: BadgeVariant } {
  switch (vencimiento.tipo) {
    case 'vencido':
      return {
        texto:
          vencimiento.dias === 0
            ? 'Venció hoy'
            : `Vencido hace ${vencimiento.dias} ${vencimiento.dias === 1 ? 'día' : 'días'}`,
        variant: 'danger',
      }
    case 'hoy':
      return { texto: 'Vence hoy', variant: 'warning' }
    case 'pendiente':
      return { texto: `Vence en ${vencimiento.dias} ${vencimiento.dias === 1 ? 'día' : 'días'}`, variant: 'neutral' }
    default:
      return { texto: 'Sin fecha límite', variant: 'neutral' }
  }
}

type AdminDashboardProps = {
  apiBaseUrl: string
  accionesRapidas: AccionRapida[]
  onFiltrarEstado: (estado: string) => void
}

/**
 * Panel del ADMINISTRADOR («SIAAF Modern»). Todo proviene de servicios
 * existentes: bandeja (`GET /expedientes/bandeja/`, ordenada por fecha límite)
 * y notificaciones. No hay tendencias ni históricos porque el backend no
 * ofrece un servicio de estadísticas.
 */
export function AdminDashboard({ apiBaseUrl, accionesRapidas, onFiltrarEstado }: AdminDashboardProps) {
  const queryClient = useQueryClient()
  const query = useResumenBandeja()
  const notificaciones = useNotificaciones()
  const ahora = new Date(query.dataUpdatedAt)
  const resumen = query.data ? resumirBandeja(query.data.results, query.data.count, ahora) : null
  const noLeidas = notificaciones.data?.results.filter((notificacion) => !notificacion.leida).length
  const actividad = notificaciones.data?.results.slice(0, MAX_ACTIVIDAD) ?? []
  const prioritarios = (query.data?.results ?? [])
    .filter((item) => item.fecha_limite_atencion)
    .slice(0, MAX_PRIORITARIOS)
  const error = query.isError ? presentApiError(query.error) : null

  function actualizar() {
    void queryClient.invalidateQueries({ queryKey: [BANDEJA_OPERATIVA_QUERY_KEY] })
    void notificaciones.refetch()
  }

  return (
    <div className={styles.dashboard}>
      <header className={styles.header}>
        <div>
          <p className={styles.eyebrow}>Supervisión del trámite</p>
          <h1 className={styles.title}>Panel de administración</h1>
          <p className={styles.subtitle}>Expedientes en curso, plazos y avisos de su cuenta.</p>
        </div>
        <div className={styles.headerActions}>
          {query.dataUpdatedAt > 0 && (
            <p className={styles.updated} role="status">
              Actualizado: {formatFechaHora(ahora.toISOString())}
            </p>
          )}
          <Button disabled={query.isFetching} size="sm" variant="secondary" onClick={actualizar}>
            <RefreshIcon size={16} />
            {query.isFetching ? 'Actualizando…' : 'Actualizar'}
          </Button>
        </div>
      </header>

      {query.isLoading && <Skeleton count={1} height="132px" label="Cargando resumen…" variant="card" />}
      {error && error.kind !== 'forbidden' && (
        <ErrorState description={error.description} title="No se pudo cargar el resumen" onRetry={() => void query.refetch()} />
      )}

      {resumen && (
        <section aria-label="Indicadores de la bandeja" className={styles.kpis}>
          <KpiCard
            className={styles.kpi}
            footer={
              <a className={styles.link} href="#listado-bandeja">
                Ver listado <ArrowRightIcon size={14} />
              </a>
            }
            headingLevel={2}
            icon={<InboxIcon />}
            title="Expedientes en la bandeja"
            value={resumen.total}
          >
            <KpiText>Estados bajo supervisión.</KpiText>
          </KpiCard>
          {resumen.completo ? (
            <>
              <KpiCard
                className={styles.kpi}
                headingLevel={2}
                icon={<AlertIcon />}
                title="Plazo vencido"
                tone={resumen.vencidos > 0 ? 'danger' : 'success'}
                value={resumen.vencidos}
              >
                <KpiText>{resumen.vencidos === 0 ? 'Ninguno supera su fecha límite.' : 'Superaron su fecha límite.'}</KpiText>
              </KpiCard>
              <KpiCard
                className={styles.kpi}
                headingLevel={2}
                icon={<ClockIcon />}
                title="Vencen hoy"
                tone={resumen.vencenHoy > 0 ? 'warning' : 'default'}
                value={resumen.vencenHoy}
              >
                <KpiText>Fecha límite de atención hoy.</KpiText>
              </KpiCard>
            </>
          ) : (
            <KpiCard className={styles.kpi} headingLevel={2} icon={<ChartIcon />} title="Indicadores detallados">
              <KpiText>
                La bandeja supera {query.data?.results.length} expedientes: los plazos y la distribución requieren un
                servicio de estadísticas del backend (pendiente).
              </KpiText>
            </KpiCard>
          )}
          <KpiCard
            className={styles.kpi}
            footer={
              <Link className={styles.link} to="/notificaciones">
                Ver avisos <ArrowRightIcon size={14} />
              </Link>
            }
            headingLevel={2}
            icon={<BellIcon />}
            title="Avisos sin leer"
            tone={noLeidas ? 'warning' : 'default'}
            value={noLeidas ?? '—'}
          >
            <KpiText>Dirigidos a su cuenta.</KpiText>
          </KpiCard>
        </section>
      )}

      {resumen && (
        <div className={styles.grid}>
          {resumen.completo && (
            <Card icon={<ChartIcon />} title="Distribución por estado">
              {resumen.porEstado.length > 0 ? (
                <BarChart
                  context={`Bandeja actual · ${formatFecha(ahora.toISOString())}`}
                  data={resumen.porEstado.map((dato) => ({
                    label: dato.label,
                    value: dato.cantidad,
                    tone: presentarEstado('expediente', dato.estado).variant,
                  }))}
                  title="Expedientes por estado"
                  unit="expedientes"
                />
              ) : (
                <p className={styles.empty}>No hay expedientes en curso.</p>
              )}
            </Card>
          )}

          <Card description="Los más próximos a su fecha límite." icon={<AlertIcon />} title="Atención prioritaria">
            {prioritarios.length === 0 ? (
              <p className={styles.empty}>Ningún expediente tiene fecha límite pendiente.</p>
            ) : (
              <ul className={styles.rows}>
                {prioritarios.map((item) => {
                  const plazo = presentarPlazo(calcularVencimiento(item.fecha_limite_atencion, ahora))
                  return (
                    <li className={styles.row} key={item.id}>
                      <Link className={styles.rowLink} to={`/bandeja/${item.id}`}>
                        {item.numero_expediente}
                      </Link>
                      <StatusBadge dominio="expediente" valor={item.estado} />
                      <Badge icon variant={plazo.variant}>
                        {plazo.texto}
                      </Badge>
                    </li>
                  )
                })}
              </ul>
            )}
          </Card>
        </div>
      )}

      <div className={styles.grid}>
        <Card description="Últimos avisos dirigidos a su cuenta." icon={<BellIcon />} title="Actividad reciente">
          {notificaciones.isLoading ? (
            <Skeleton count={3} label="Cargando actividad…" variant="text" />
          ) : notificaciones.isError ? (
            <ErrorState
              description={presentApiError(notificaciones.error).description}
              title="No se pudo cargar la actividad"
              onRetry={() => void notificaciones.refetch()}
            />
          ) : actividad.length === 0 ? (
            <p className={styles.empty}>Sin actividad reciente en su cuenta.</p>
          ) : (
            <ol className={styles.timeline}>
              {actividad.map((notificacion) => (
                <li className={notificacion.leida ? styles.event : `${styles.event} ${styles.eventNew}`} key={notificacion.id}>
                  <Link className={styles.rowLink} to={`/bandeja/${notificacion.expediente}`}>
                    {notificacion.titulo}
                    {!notificacion.leida && <span className="sr-only"> (no leída)</span>}
                  </Link>
                  <span className={styles.meta}>
                    {notificacion.expediente_numero} · {formatFechaHora(notificacion.fecha_creacion)}
                  </span>
                </li>
              ))}
            </ol>
          )}
        </Card>

        {accionesRapidas.length > 0 && (
          <Card description="Filtran el listado de la página actual." icon={<FilterIcon />} title="Accesos rápidos">
            <ul className={styles.quick}>
              {accionesRapidas.map((accion) => {
                const cantidad = resumen?.completo
                  ? (resumen.porEstado.find((dato) => dato.estado === accion.estado)?.cantidad ?? 0)
                  : null
                return (
                  <li key={accion.estado}>
                    <button className={styles.quickButton} type="button" onClick={() => onFiltrarEstado(accion.estado)}>
                      <span className={styles.quickText}>
                        <span className={styles.quickTitle}>{accion.label}</span>
                        <span className={styles.meta}>{accion.descripcion}</span>
                      </span>
                      {cantidad !== null && <span className={styles.quickCount}>{cantidad}</span>}
                      <ArrowRightIcon size={16} />
                    </button>
                  </li>
                )
              })}
            </ul>
          </Card>
        )}
      </div>

      <PanelAdministracion apiBaseUrl={apiBaseUrl} />
    </div>
  )
}
