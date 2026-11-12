import { useContext, useState } from 'react'
import { Link } from 'react-router-dom'
import { AuthContext } from '@/auth/AuthContext'
import { Card } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { ErrorState } from '@/components/ui/ErrorState'
import { ForbiddenState } from '@/components/ui/ForbiddenState'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { presentApiError } from '@/lib/apiErrorPresentation'
import { BandejaFilters, aplicarFiltros, type FiltrosBandeja } from './BandejaFilters'
import { BandejaTable } from './BandejaTable'
import { explicarBandejaVacia } from './bandejaReglas'
import { useBandejaOperativa, usePrecargarExpediente } from './queries'
import styles from './BandejaPage.module.css'

const PAGE_SIZE = 10
const FILTROS_INICIALES: FiltrosBandeja = { estado: '', numero: '' }

/**
 * V-07 — Bandeja del funcionario (FE-T701…FE-T705). Datos reales de
 * `GET /expedientes/bandeja/`: el backend filtra por rol y ámbito; la vista
 * no añade acciones de escritura ni búsqueda global (BE-09).
 */
export default function BandejaPage() {
  const auth = useContext(AuthContext)
  const roles = auth?.user?.roles ?? []
  const [page, setPage] = useState(1)
  const [filtros, setFiltros] = useState<FiltrosBandeja>(FILTROS_INICIALES)
  const bandejaQuery = useBandejaOperativa(page, PAGE_SIZE)
  const precargar = usePrecargarExpediente()

  function cambiarPagina(nueva: number) {
    setFiltros(FILTROS_INICIALES)
    setPage(nueva)
  }

  let contenido
  if (bandejaQuery.isLoading) {
    contenido = <Spinner label="Cargando bandeja…" />
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
    <main className={styles.page}>
      <header>
        <h1 className={styles.title}>Bandeja de expedientes</h1>
        <p className={styles.subtitle}>
          Expedientes que requieren la intervención de su rol, ordenados por fecha límite de atención.
        </p>
      </header>
      <h2 className="sr-only">Listado de la bandeja</h2>
      <Card title="Expedientes">{contenido}</Card>
    </main>
  )
}
