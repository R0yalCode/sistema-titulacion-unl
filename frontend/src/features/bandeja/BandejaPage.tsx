import { useContext, useState } from 'react'
import { Link } from 'react-router-dom'
import { AuthContext } from '@/auth/AuthContext'
import { Card } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { ErrorState } from '@/components/ui/ErrorState'
import { ForbiddenState } from '@/components/ui/ForbiddenState'
import { InboxIcon } from '@/components/ui/icons'
import { Pagination } from '@/components/ui/Pagination'
import { Skeleton } from '@/components/ui/Skeleton'
import { presentApiError } from '@/lib/apiErrorPresentation'
import { getEnv } from '@/lib/env'
import { BandejaFilters, aplicarFiltros, type FiltrosBandeja } from './BandejaFilters'
import { BandejaTable } from './BandejaTable'
import { estadosAtendidos, explicarBandejaVacia } from './bandejaReglas'
import { PanelAdministracion, PanelSinBandeja, ResumenPanel } from './PanelesInicio'
import { useBandejaOperativa, usePrecargarExpediente } from './queries'
import { contextoRol } from './resumen'
import styles from './BandejaPage.module.css'

const PAGE_SIZE = 10
const FILTROS_INICIALES: FiltrosBandeja = { estado: '', numero: '' }

/**
 * V-07 — Inicio del funcionario: panel contextual por rol (indicadores reales,
 * distribución por estado y accesos rápidos) y la bandeja de
 * `GET /expedientes/bandeja/`. El backend filtra por rol y ámbito; la vista no
 * añade acciones de escritura ni búsqueda global (BE-09).
 */
export default function BandejaPage() {
  const auth = useContext(AuthContext)
  const roles = auth?.user?.roles ?? []
  const [page, setPage] = useState(1)
  const [filtros, setFiltros] = useState<FiltrosBandeja>(FILTROS_INICIALES)
  const contexto = contextoRol(roles)
  // BE-09: el backend no asigna bandeja a estos roles; no se consulta en vano.
  const sinBandeja = estadosAtendidos(roles).length === 0
  const bandejaQuery = useBandejaOperativa(page, PAGE_SIZE, { enabled: !sinBandeja })
  const precargar = usePrecargarExpediente()

  function cambiarPagina(nueva: number) {
    setFiltros(FILTROS_INICIALES)
    setPage(nueva)
  }

  function filtrarEstado(estado: string) {
    setFiltros({ ...FILTROS_INICIALES, estado })
    document.getElementById('listado-bandeja')?.focus()
  }

  let contenido
  if (bandejaQuery.isLoading) {
    contenido = <Skeleton count={4} label="Cargando bandeja…" />
  } else if (bandejaQuery.isError) {
    const presentation = presentApiError(bandejaQuery.error)
    contenido =
      presentation.kind === 'forbidden' ? (
        <ForbiddenState
          action={<Link to="/no-habilitado?motivo=rol-no-autorizado">Más información</Link>}
          description={presentation.description}
          title={presentation.title}
        />
      ) : (
        <ErrorState
          description={presentation.description}
          title={presentation.title}
          onRetry={() => bandejaQuery.refetch()}
        />
      )
  } else if (bandejaQuery.data) {
    const { count, results } = bandejaQuery.data
    if (count === 0) {
      const vacia = explicarBandejaVacia(roles)
      contenido = <EmptyState description={vacia.descripcion} title={vacia.titulo} />
    } else {
      // Los plazos se calculan respecto del momento en que llegaron los datos.
      const ahora = new Date(bandejaQuery.dataUpdatedAt)
      const visibles = aplicarFiltros(results, filtros)
      const estadosPagina = [...new Set(results.map((fila) => fila.estado))]
      contenido = (
        <>
          <p className={styles.total} role="status">
            {count === 1 ? '1 expediente en la bandeja' : `${count} expedientes en la bandeja`} · página {page} de{' '}
            {Math.max(1, Math.ceil(count / PAGE_SIZE))}
          </p>
          <BandejaFilters
            estadosDisponibles={estadosPagina}
            filtros={filtros}
            totalPagina={results.length}
            visibles={visibles.length}
            onChange={setFiltros}
          />
          <BandejaTable ahora={ahora} filas={visibles} onPrecargar={precargar} />
          <Pagination count={count} page={page} pageSize={PAGE_SIZE} onPageChange={cambiarPagina} />
        </>
      )
    }
  }

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <p className={styles.eyebrow}>{contexto.titulo}</p>
        <h1 className={styles.title}>Bandeja de expedientes</h1>
        <p className={styles.subtitle}>{contexto.subtitulo}</p>
      </header>

      {sinBandeja ? (
        <PanelSinBandeja roles={roles} />
      ) : (
        <ResumenPanel accionesRapidas={contexto.accionesRapidas} onFiltrarEstado={filtrarEstado} />
      )}

      {roles.includes('ADMINISTRADOR') && <PanelAdministracion apiBaseUrl={getEnv().apiBaseUrl} />}

      {!sinBandeja && (
        <Card
          description="Ordenados por fecha límite de atención."
          icon={<InboxIcon />}
          id="listado-bandeja"
          title="Expedientes"
        >
          {contenido}
        </Card>
      )}
    </div>
  )
}
