import { Link } from 'react-router-dom'
import { ErrorState } from '@/components/ui/ErrorState'
import { ForbiddenState } from '@/components/ui/ForbiddenState'
import { ClockIcon, DocumentIcon, FlagIcon, FolderIcon, ListCheckIcon } from '@/components/ui/icons'
import { presentApiError } from '@/lib/apiErrorPresentation'
import { formatFecha } from '@/lib/dates'
import { KpiResumen } from './KpiResumen'
import { Card } from '@/components/ui/Card'
import { AccionesPendientes, DocumentosResumen, UltimosMovimientos } from './Secciones'
import { SeguimientoTramite } from './SeguimientoTramite'
import { calcularProximoHito, construirAccionesPendientes } from './presentacion'
import { useMiTramite } from './queries'
import styles from './StudentDashboardPage.module.css'

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

export default function StudentDashboardPage() {
  const query = useMiTramite()
  const datos = query.data
  const expediente = datos?.expediente ?? null
  const nombre = datos?.estudiante.nombre_completo ?? null

  let contenido
  if (query.isLoading) {
    contenido = <DashboardSkeleton />
  } else if (query.isError) {
    const presentation = presentApiError(query.error)
    contenido =
      presentation.kind === 'forbidden' ? (
        <ForbiddenState description={presentation.description} title={presentation.title} />
      ) : (
        <div className={styles.errorBox}>
          <ErrorState
            description={presentation.description}
            title="No pudimos cargar tu proceso de titulación"
            onRetry={() => void query.refetch()}
          />
        </div>
      )
  } else if (!expediente) {
    contenido = (
      <section aria-labelledby="sin-tramite-titulo" className={styles.start}>
        <span aria-hidden="true" className={styles.startIcon}>
          <FolderIcon size={28} />
        </span>
        <div>
          <h2 className={styles.startTitle} id="sin-tramite-titulo">
            Aún no tienes un trámite de titulación
          </h2>
          <p className={styles.startText}>
            Registra tu solicitud para iniciar el proceso. Después podrás gestionar tus documentos y seguir cada etapa
            desde este panel.
          </p>
          <Link className={styles.primaryLink} to="/estudiante/solicitud/nueva">
            Crear solicitud
          </Link>
        </div>
      </section>
    )
  } else {
    const acciones = construirAccionesPendientes(expediente)
    const hito = calcularProximoHito(expediente)
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
      <header className={styles.header}>
        <div>
          <h1 className={styles.title}>Mi proceso de titulación</h1>
          <p className={styles.subtitle}>Consulta tu avance, pendientes y próximos pasos.</p>
        </div>
        {(nombre || expediente) && (
          <dl className={styles.identity}>
            {nombre && (
              <div>
                <dt>Estudiante</dt>
                <dd>{nombre}</dd>
              </div>
            )}
            {expediente && (
              <div>
                <dt>Expediente</dt>
                <dd>{expediente.numero_expediente}</dd>
              </div>
            )}
            {expediente && (
              <div>
                <dt>Registrado</dt>
                <dd>{formatFecha(expediente.fecha_creacion)}</dd>
              </div>
            )}
          </dl>
        )}
      </header>
      {contenido}
    </div>
  )
}
