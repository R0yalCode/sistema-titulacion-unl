import { Link } from 'react-router-dom'
import { HeroPanel, type HeroMetaItem } from '@/components/ui/HeroPanel'
import { CalendarIcon, ClockIcon, DocumentIcon, FlagIcon, ListCheckIcon } from '@/components/ui/icons'
import { formatFecha } from '@/lib/dates'
import { AccionPrioritaria } from './AccionPrioritaria'
import { KpiResumen } from './KpiResumen'
import { Card } from '@/components/ui/Card'
import { AccionesPendientes, DocumentosResumen, UltimosMovimientos } from './Secciones'
import { SeguimientoTramite } from './SeguimientoTramite'
import type { ExpedienteResumen } from '@/api/endpoints/miTramite'
import { calcularProximoHito, construirAccionesPendientes, type ProximoHito } from './presentacion'
import { useMiTramite } from './queries'
import styles from './StudentDashboardPage.module.css'
import { QueryErrorView } from '@/components/errors/QueryErrorView'

function DashboardSkeleton() {
  return (
    <div aria-busy="true" className={styles.skeleton} role="status">
      <span className="sr-only">Cargando tu proceso de titulación…</span>
      <div className={styles.skeletonGrid}>
        {[0, 1, 2, 3].map((index) => (
          <div aria-hidden="true" className={styles.skeletonCard} key={index} />
        ))}
      </div>
      <div className={styles.skeletonColumns}>
        <div aria-hidden="true" className={`${styles.skeletonCard} ${styles.skeletonTall}`} />
        <div aria-hidden="true" className={`${styles.skeletonCard} ${styles.skeletonTall}`} />
      </div>
    </div>
  )
}

/** Chips del hero: solo fechas y etapas que devuelve el backend. */
function metaDelTramite(expediente: ExpedienteResumen | null, hito: ProximoHito | null): HeroMetaItem[] {
  if (!expediente) {
    return []
  }
  const meta: HeroMetaItem[] = [
    { id: 'registro', icon: <CalendarIcon size={14} />, label: `Registrado el ${formatFecha(expediente.fecha_creacion)}` },
  ]
  const actual = expediente.etapas.find((etapa) => etapa.situacion === 'actual')
  if (actual && expediente.progreso) {
    meta.push({ id: 'etapa', icon: <FlagIcon size={14} />, label: `Etapa actual: ${actual.nombre}` })
  }
  if (hito?.fecha) {
    meta.push({ id: 'plazo', icon: <ClockIcon size={14} />, label: `Atención institucional hasta el ${formatFecha(hito.fecha)}` })
  }
  return meta
}

export default function StudentDashboardPage() {
  const query = useMiTramite()
  const datos = query.data
  const expediente = datos?.expediente ?? null
  const nombre = datos?.estudiante.nombre_completo ?? null
  const acciones = expediente ? construirAccionesPendientes(expediente) : []
  const hito = expediente ? calcularProximoHito(expediente) : null
  const meta = metaDelTramite(expediente, hito)

  let contenido
  if (query.isLoading) {
    contenido = <DashboardSkeleton />
  } else if (query.isError) {
    contenido = <QueryErrorView error={query.error} onRetry={() => query.refetch()} />
  } else if (!expediente) {
    // La tarjeta del hero ofrece el primer paso (crear la solicitud).
    contenido = null
  } else {
    contenido = (
      <>
        <KpiResumen acciones={acciones} expediente={expediente} hito={hito} />
        {/* Orden del DOM = prioridad de lectura: primero lo accionable. En escritorio,
            el seguimiento ocupa la columna ancha (CSS) sin alterar ese orden. */}
        <div className={styles.layout}>
          <div className={styles.colSide}>
            <Card icon={<ListCheckIcon />} id="pendientes" title="Necesitas completar">
              <AccionesPendientes acciones={acciones} />
            </Card>
            <Card
              actions={
                <Link className={styles.panelLink} to={`/expedientes/${expediente.id}/peticiones`}>
                  Ver documentos
                </Link>
              }
              icon={<DocumentIcon />}
              id="documentos"
              title="Documentación"
            >
              <DocumentosResumen expediente={expediente} />
            </Card>
          </div>
          <div className={styles.colMain}>
            <Card icon={<FlagIcon />} id="seguimiento" title="Mi seguimiento de titulación">
              <SeguimientoTramite expediente={expediente} hito={hito} />
            </Card>
            <Card icon={<ClockIcon />} id="movimientos" title="Últimos movimientos">
              <UltimosMovimientos movimientos={expediente.movimientos} />
            </Card>
          </div>
        </div>
      </>
    )
  }

  return (
    <div className={styles.page}>
      <HeroPanel
        aside={query.isSuccess ? <AccionPrioritaria acciones={acciones} expediente={expediente} /> : undefined}
        description="Consulta tu avance, pendientes y próximos pasos."
        eyebrow={
          expediente ? (
            <>
              Expediente <strong>{expediente.numero_expediente}</strong>
            </>
          ) : (
            'Portal del estudiante'
          )
        }
        meta={meta}
        title={nombre ? `Hola, ${nombre}` : 'Mi proceso de titulación'}
      />
      {contenido}
    </div>
  )
}
