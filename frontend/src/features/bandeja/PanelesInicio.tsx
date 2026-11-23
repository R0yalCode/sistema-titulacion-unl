import { Link } from 'react-router-dom'
import { BarChart } from '@/components/ui/BarChart'
import { Card } from '@/components/ui/Card'
import { ErrorState } from '@/components/ui/ErrorState'
import {
  AlertIcon,
  ArrowRightIcon,
  BellIcon,
  ChartIcon,
  ClockIcon,
  ExternalLinkIcon,
  InboxIcon,
  SettingsShieldIcon,
  UsersIcon,
} from '@/components/ui/icons'
import { KpiCard, KpiText } from '@/components/ui/KpiCard'
import { KpiGrid } from '@/components/ui/KpiGrid'
import { Skeleton } from '@/components/ui/Skeleton'
import { useNotificaciones } from '@/features/dashboard'
import { presentApiError } from '@/lib/apiErrorPresentation'
import { formatFecha } from '@/lib/dates'
import { presentarEstado } from '@/lib/estados'
import type { AccionRapida } from './resumen'
import { resumirBandeja } from './resumen'
import { useResumenBandeja } from './queries'
import styles from './PanelesInicio.module.css'

type ResumenPanelProps = {
  accionesRapidas: AccionRapida[]
  onFiltrarEstado: (estado: string) => void
}

/**
 * Indicadores del panel del funcionario con datos reales de su bandeja. Si la
 * bandeja supera el máximo de una página (50), solo se muestra el total: no se
 * presentan cifras parciales como si fueran de toda la bandeja.
 */
export function ResumenPanel({ accionesRapidas, onFiltrarEstado }: ResumenPanelProps) {
  const query = useResumenBandeja()

  if (query.isLoading) {
    return <Skeleton count={1} height="148px" label="Cargando resumen…" variant="card" />
  }
  if (query.isError) {
    const presentation = presentApiError(query.error)
    if (presentation.kind === 'forbidden') {
      // El listado ya muestra el estado 403 con su enlace a V-09.
      return null
    }
    return <ErrorState description={presentation.description} title="No se pudo cargar el resumen" onRetry={() => void query.refetch()} />
  }
  if (!query.data || query.data.count === 0) {
    return null
  }

  const resumen = resumirBandeja(query.data.results, query.data.count, new Date(query.dataUpdatedAt))
  const fechaCorte = formatFecha(new Date(query.dataUpdatedAt).toISOString())

  return (
    <div className={styles.resumen}>
      <KpiGrid columns={3} label="Resumen de la bandeja">
        <KpiCard icon={<InboxIcon />} title="Expedientes en la bandeja" value={resumen.total}>
          <KpiText>Requieren la intervención de su rol.</KpiText>
        </KpiCard>
        {resumen.completo ? (
          <>
            <KpiCard
              icon={<AlertIcon />}
              title="Plazo vencido"
              tone={resumen.vencidos > 0 ? 'danger' : 'success'}
              value={resumen.vencidos}
            >
              <KpiText>
                {resumen.vencidos === 0
                  ? 'Ningún expediente supera su fecha límite de atención.'
                  : 'Superaron la fecha límite de atención (días calendario).'}
              </KpiText>
            </KpiCard>
            <KpiCard
              icon={<ClockIcon />}
              title="Vencen hoy"
              tone={resumen.vencenHoy > 0 ? 'warning' : 'default'}
              value={resumen.vencenHoy}
            >
              <KpiText>Su fecha límite de atención es hoy.</KpiText>
            </KpiCard>
          </>
        ) : (
          <KpiCard icon={<ChartIcon />} title="Indicadores detallados" tone="default">
            <KpiText>
              La bandeja supera {query.data.results.length} expedientes: los indicadores de plazo y la distribución
              por estado requieren un servicio de estadísticas del backend (pendiente).
            </KpiText>
          </KpiCard>
        )}
      </KpiGrid>

      {(resumen.completo && resumen.porEstado.length > 0) || accionesRapidas.length > 0 ? (
        <div className={styles.fila}>
          {resumen.completo && resumen.porEstado.length > 0 && (
            <Card icon={<ChartIcon />} title="Distribución por estado">
              <BarChart
                context={`Bandeja actual · ${fechaCorte}`}
                data={resumen.porEstado.map((dato) => ({
                  label: dato.label,
                  value: dato.cantidad,
                  tone: presentarEstado('expediente', dato.estado).variant,
                }))}
                title="Expedientes por estado"
                unit="expedientes"
              />
            </Card>
          )}
          {accionesRapidas.length > 0 && (
            <Card description="Filtran el listado de la página actual." icon={<ArrowRightIcon />} title="Accesos rápidos">
              <ul className={styles.accesos}>
                {accionesRapidas.map((accion) => {
                  const cantidad = resumen.completo
                    ? (resumen.porEstado.find((dato) => dato.estado === accion.estado)?.cantidad ?? 0)
                    : null
                  return (
                    <li key={accion.estado}>
                      <button className={styles.acceso} type="button" onClick={() => onFiltrarEstado(accion.estado)}>
                        <span className={styles.accesoTexto}>
                          <span className={styles.accesoTitulo}>{accion.label}</span>
                          <span className={styles.accesoDescripcion}>{accion.descripcion}</span>
                        </span>
                        {cantidad !== null && <span className={styles.accesoCantidad}>{cantidad}</span>}
                        <ArrowRightIcon size={16} />
                      </button>
                    </li>
                  )
                })}
              </ul>
            </Card>
          )}
        </div>
      ) : null}
    </div>
  )
}

/**
 * Secretaría de carrera y Dirección de carrera: el backend no les asigna
 * expedientes en la bandeja (BE-09). Su punto de entrada real son las
 * notificaciones (p. ej. solicitudes de emisión dirigidas a la dependencia).
 */
export function PanelSinBandeja({ roles }: { roles: string[] }) {
  const notificaciones = useNotificaciones()
  const esSecretaria = roles.includes('SECRETARIA_CARRERA')
  const recientes = notificaciones.data?.results.slice(0, 5) ?? []
  const noLeidas = notificaciones.data?.results.filter((notificacion) => !notificacion.leida).length ?? 0

  return (
    <div className={styles.sinBandeja}>
      <KpiGrid columns={3} label="Resumen de actividad">
        <KpiCard
          icon={<BellIcon />}
          title="Notificaciones sin leer"
          tone={noLeidas > 0 ? 'warning' : 'default'}
          value={notificaciones.isSuccess ? noLeidas : '—'}
          footer={
            <Link className={styles.link} to="/notificaciones">
              Ver notificaciones <ArrowRightIcon size={16} />
            </Link>
          }
        >
          <KpiText>Avisos dirigidos a su cuenta.</KpiText>
        </KpiCard>
        <KpiCard icon={<InboxIcon />} title="Bandeja de expedientes" tone="default">
          <KpiText>
            El sistema no asigna expedientes a la bandeja de su rol por ahora (dependencia BE-09). Los expedientes se
            consultan desde los avisos recibidos o su enlace directo.
          </KpiText>
        </KpiCard>
        <KpiCard icon={esSecretaria ? <UsersIcon /> : <ChartIcon />} title={esSecretaria ? 'Su gestión' : 'Su consulta'}>
          <KpiText>
            {esSecretaria
              ? 'Cargue los documentos solicitados a la Secretaría desde las peticiones del expediente indicado en cada aviso.'
              : 'Su rol consulta los expedientes de la carrera en modo de solo lectura.'}
          </KpiText>
        </KpiCard>
      </KpiGrid>

      <Card icon={<BellIcon />} title="Avisos recientes">
        {notificaciones.isLoading ? (
          <Skeleton count={3} label="Cargando avisos…" variant="text" />
        ) : notificaciones.isError ? (
          <ErrorState
            description={presentApiError(notificaciones.error).description}
            title="No se pudieron cargar los avisos"
            onRetry={() => void notificaciones.refetch()}
          />
        ) : recientes.length === 0 ? (
          <p className={styles.vacio}>No hay avisos dirigidos a su cuenta por ahora.</p>
        ) : (
          <ul className={styles.avisos}>
            {recientes.map((notificacion) => (
              <li className={notificacion.leida ? styles.aviso : `${styles.aviso} ${styles.avisoNuevo}`} key={notificacion.id}>
                <div className={styles.avisoTexto}>
                  <span className={styles.avisoTitulo}>
                    {notificacion.titulo}
                    {!notificacion.leida && <span className="sr-only"> (no leída)</span>}
                  </span>
                  <span className={styles.avisoMeta}>
                    {notificacion.expediente_numero} · {formatFecha(notificacion.fecha_creacion)}
                  </span>
                </div>
                <Link
                  className={styles.link}
                  to={esSecretaria ? `/expedientes/${notificacion.expediente}/peticiones` : `/bandeja/${notificacion.expediente}`}
                >
                  {esSecretaria ? 'Ver peticiones' : 'Ver expediente'}
                  <span className="sr-only"> {notificacion.expediente_numero}</span>
                  <ArrowRightIcon size={16} />
                </Link>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  )
}

/** Administrador: enlaces a la consola interna existente (Django admin, ADR-0009). */
export function PanelAdministracion({ apiBaseUrl }: { apiBaseUrl: string }) {
  const enlaces = [
    { href: `${apiBaseUrl}/admin/authentication/user/`, titulo: 'Usuarios', descripcion: 'Cuentas del sistema' },
    { href: `${apiBaseUrl}/admin/authentication/role/`, titulo: 'Roles', descripcion: 'Roles institucionales' },
    {
      href: `${apiBaseUrl}/admin/notificaciones/eventoauditoria/`,
      titulo: 'Auditoría',
      descripcion: 'Eventos de auditoría del trámite',
    },
    {
      href: `${apiBaseUrl}/admin/authentication/eventoautenticacion/`,
      titulo: 'Accesos',
      descripcion: 'Eventos de autenticación',
    },
  ]
  return (
    <Card
      description="Se abre en la consola interna (requiere una cuenta con acceso de personal)."
      icon={<SettingsShieldIcon />}
      title="Administración del sistema"
    >
      <ul className={styles.admin}>
        {enlaces.map((enlace) => (
          <li key={enlace.href}>
            <a className={styles.adminEnlace} href={enlace.href}>
              <span className={styles.accesoTexto}>
                <span className={styles.accesoTitulo}>{enlace.titulo}</span>
                <span className={styles.accesoDescripcion}>{enlace.descripcion}</span>
              </span>
              <ExternalLinkIcon size={16} />
            </a>
          </li>
        ))}
      </ul>
    </Card>
  )
}
