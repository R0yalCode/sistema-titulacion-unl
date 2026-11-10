import type { UseQueryResult } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'
import type { BandejaExpediente } from '@/api/endpoints/expedientes'
import type { ApiRequestError } from '@/api/errors'
import type { Paginated } from '@/api/types/api'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { EmptyState } from '@/components/ui/EmptyState'
import { ErrorState } from '@/components/ui/ErrorState'
import { ForbiddenState } from '@/components/ui/ForbiddenState'
import { Pagination } from '@/components/ui/Pagination'
import { Table, type TableColumn } from '@/components/ui/Table'
import { presentApiError } from '@/lib/apiErrorPresentation'
import { formatFecha } from '@/lib/dates'
import styles from './ExpedientesCard.module.css'

const PAGE_SIZE = 10

type ExpedientesCardProps = {
  query: UseQueryResult<Paginated<BandejaExpediente>, ApiRequestError>
  page: number
  onPageChange: (page: number) => void
  onVisit: (expediente: BandejaExpediente) => void
}

export function ExpedientesCard({ query, page, onPageChange, onVisit }: ExpedientesCardProps) {
  const navigate = useNavigate()

  if (query.isError) {
    const presentation = presentApiError(query.error)
    if (presentation.kind === 'forbidden') {
      return <ForbiddenState description={presentation.description} title={presentation.title} />
    }
    return (
      <ErrorState
        description={presentation.description}
        title={presentation.title}
        onRetry={() => query.refetch()}
      />
    )
  }

  if (query.isLoading) {
    return <Table caption="Mis expedientes" columns={columns(onVisit)} loading rowKey={(row) => row.id} rows={[]} />
  }

  const data = query.data
  if (!data || data.results.length === 0) {
    return (
      <EmptyState
        action={<Button onClick={() => navigate('/estudiante/solicitud/nueva')}>Crear solicitud</Button>}
        description="No tiene expedientes en Borrador u Observada. Puede crear una nueva solicitud."
        title="Sin expedientes"
      />
    )
  }

  return (
    <div className={styles.wrapper}>
      <Table
        caption="Mis expedientes"
        columns={columns(onVisit)}
        rowKey={(row) => row.id}
        rows={data.results}
      />
      {data.next !== null && (
        <p className={styles.pageNote}>Los contadores se calculan sobre la página actual. Hay más páginas disponibles.</p>
      )}
      {data.count > PAGE_SIZE && (
        <Pagination count={data.count} page={page} pageSize={PAGE_SIZE} onPageChange={onPageChange} />
      )}
    </div>
  )
}

function columns(onVisit: (expediente: BandejaExpediente) => void): Array<TableColumn<BandejaExpediente>> {
  return [
    { key: 'numero_expediente', header: 'Expediente', render: (row) => row.numero_expediente },
    {
      key: 'estado',
      header: 'Estado',
      render: (row) => <Badge variant={row.estado === 'OBSERVADA' ? 'warning' : 'neutral'}>{row.estado}</Badge>,
    },
    { key: 'fecha_creacion', header: 'Creado', render: (row) => formatFecha(row.fecha_creacion) },
    {
      key: 'fecha_limite_atencion',
      header: 'Límite de atención',
      render: (row) => formatFecha(row.fecha_limite_atencion),
    },
    {
      key: 'accion',
      header: 'Acción',
      render: (row) => (
        <Link to={`/expedientes/${row.id}`} onClick={() => onVisit(row)}>
          Ver expediente
        </Link>
      ),
    },
  ]
}
