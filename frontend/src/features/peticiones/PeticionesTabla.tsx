import { Link } from 'react-router-dom'
import type { EstadoExpediente, PeticionInicializada } from '@/api/endpoints/expedientes'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Table, type TableColumn } from '@/components/ui/Table'
import { DescargaButton, puedeDescargar } from '@/features/expediente'
import {
  presentarEstadoPeticion,
  puedeCargarDocumento,
  puedeSolicitarEmision,
  tieneDocumento,
} from './accionesPeticion'
import styles from './PeticionesTabla.module.css'

type PeticionesTablaProps = {
  expedienteId: string
  numeroExpediente: string
  estadoExpediente: EstadoExpediente
  peticiones: PeticionInicializada[]
  roles: string[]
  onSolicitar: (peticion: PeticionInicializada) => void
  onCargar: (peticion: PeticionInicializada) => void
}

/** FE-T501: lista de peticiones con estado, dependencia, acciones por rol/estado y enlace a V-06. */
export function PeticionesTabla({
  expedienteId,
  numeroExpediente,
  estadoExpediente,
  peticiones,
  roles,
  onSolicitar,
  onCargar,
}: PeticionesTablaProps) {
  const descargaPermitida = puedeDescargar(roles)

  const columns: Array<TableColumn<PeticionInicializada>> = [
    { key: 'numero', header: '#', render: (row) => peticiones.indexOf(row) + 1 },
    { key: 'requisito_nombre', header: 'Requisito', render: (row) => row.requisito_nombre },
    {
      key: 'estado_peticion',
      header: 'Estado',
      render: (row) => {
        const { label, variant } = presentarEstadoPeticion(row.estado_peticion)
        return <Badge variant={variant}>{label}</Badge>
      },
    },
    { key: 'dependencia_emisora', header: 'Dependencia emisora', render: (row) => row.dependencia_emisora },
    {
      key: 'acciones',
      header: 'Acciones',
      render: (row) => (
        <div className={styles.acciones}>
          {puedeSolicitarEmision(roles, estadoExpediente, row.estado_peticion) && (
            <Button
              aria-label={`Solicitar emisión: ${row.requisito_nombre}`}
              size="sm"
              onClick={() => onSolicitar(row)}
            >
              Solicitar emisión
            </Button>
          )}
          {puedeCargarDocumento(roles, row.estado_peticion, row.dependencia_emisora) && (
            <Button
              aria-label={`Cargar documento: ${row.requisito_nombre}`}
              size="sm"
              variant="secondary"
              onClick={() => onCargar(row)}
            >
              Cargar documento
            </Button>
          )}
          {descargaPermitida && tieneDocumento(row.estado_peticion) && (
            <DescargaButton
              fallbackFilename={`${numeroExpediente}-${row.requisito_codigo}.pdf`}
              peticionId={row.id}
            />
          )}
          <Link
            aria-label={`Ver seguimiento: ${row.requisito_nombre}`}
            className={styles.enlace}
            to={`/expedientes/${expedienteId}/peticiones/${row.id}`}
          >
            Ver seguimiento
          </Link>
        </div>
      ),
    },
  ]

  return (
    <Table
      caption="Peticiones documentales del expediente"
      columns={columns}
      emptyDescription="Este expediente no tiene peticiones registradas."
      emptyTitle="Sin peticiones"
      rowKey={(row) => row.id}
      rows={peticiones}
    />
  )
}
