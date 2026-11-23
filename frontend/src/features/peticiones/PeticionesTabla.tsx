import { Link } from 'react-router-dom'
import type { EstadoExpediente, PeticionInicializada } from '@/api/endpoints/expedientes'
import { Button } from '@/components/ui/Button'
import { DataList } from '@/components/ui/DataList'
import { ChevronRightIcon } from '@/components/ui/icons'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { DescargaButton, puedeDescargar } from '@/features/expediente'
import { nombreRol } from '@/lib/estados'
import {
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

/**
 * FE-T501: lista adaptable de peticiones (filas en escritorio, tarjetas en
 * móvil) con estado, dependencia, acciones por rol/estado y enlace a V-06.
 */
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

  return (
    <DataList
      emptyDescription="Este expediente no tiene peticiones registradas."
      emptyTitle="Sin peticiones"
      fields={[{ key: 'dependencia', label: 'Dependencia emisora', render: (row) => nombreRol(row.dependencia_emisora) }]}
      getKey={(row) => row.id}
      getTone={(row) => (row.estado_peticion === 'OBSERVADO' ? 'warning' : undefined)}
      items={peticiones}
      label="Peticiones documentales del expediente"
      renderActions={(row) => (
        <>
          {puedeSolicitarEmision(roles, estadoExpediente, row.estado_peticion) && (
            <Button aria-label={`Solicitar emisión: ${row.requisito_nombre}`} size="sm" onClick={() => onSolicitar(row)}>
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
            <DescargaButton fallbackFilename={`${numeroExpediente}-${row.requisito_codigo}.pdf`} peticionId={row.id} />
          )}
          <Link
            aria-label={`Ver seguimiento: ${row.requisito_nombre}`}
            className={styles.enlace}
            to={`/expedientes/${expedienteId}/peticiones/${row.id}`}
          >
            Ver seguimiento
            <ChevronRightIcon size={16} />
          </Link>
        </>
      )}
      renderStatus={(row) => <StatusBadge dominio="peticion" valor={row.estado_peticion} />}
      renderSubtitle={(row) => `Requisito ${peticiones.indexOf(row) + 1} de ${peticiones.length}`}
      renderTitle={(row) => row.requisito_nombre}
    />
  )
}
