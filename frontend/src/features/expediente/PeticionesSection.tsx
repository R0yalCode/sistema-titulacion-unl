import type { PeticionInicializada } from '@/api/endpoints/expedientes'
import { Badge } from '@/components/ui/Badge'
import { Table, type TableColumn } from '@/components/ui/Table'
import { puedeDescargar } from './accionesPorRolEstado'
import { DescargaButton } from './DescargaButton'
import styles from './PeticionesSection.module.css'

type PeticionesSectionProps = {
  peticiones: PeticionInicializada[]
  roles: string[]
  numeroExpediente: string
}

export function PeticionesSection({ peticiones, roles, numeroExpediente }: PeticionesSectionProps) {
  const puedeDescargarDocumentos = puedeDescargar(roles)
  const esEstudiante = roles.includes('ESTUDIANTE')

  const columns: Array<TableColumn<PeticionInicializada>> = [
    { key: 'requisito_nombre', header: 'Requisito', render: (row) => row.requisito_nombre },
    {
      key: 'estado_peticion',
      header: 'Estado',
      render: (row) => (
        <Badge variant={row.estado_peticion === 'OBSERVADO' ? 'warning' : 'neutral'}>
          {row.estado_peticion}
        </Badge>
      ),
    },
    { key: 'dependencia_emisora', header: 'Dependencia emisora', render: (row) => row.dependencia_emisora },
    {
      key: 'acciones',
      header: 'Acciones',
      render: (row) => (
        <div className={styles.acciones}>
          {puedeDescargarDocumentos && (
            <DescargaButton
              fallbackFilename={`${numeroExpediente}-${row.requisito_codigo}.pdf`}
              peticionId={row.id}
            />
          )}
          {esEstudiante && row.estado_peticion === 'OBSERVADO' && (
            <p className={styles.subsanarNote}>
              Esta petición fue observada. Por una limitación del sistema, la subsanación en línea no está
              disponible todavía para su rol; comuníquese con la dependencia correspondiente.
            </p>
          )}
        </div>
      ),
    },
  ]

  return (
    <Table
      caption="Peticiones documentales"
      columns={columns}
      emptyDescription="Este expediente no tiene peticiones registradas."
      emptyTitle="Sin peticiones"
      rowKey={(row) => row.id}
      rows={peticiones}
    />
  )
}
