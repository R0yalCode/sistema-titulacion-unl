import type { PeticionInicializada } from '@/api/endpoints/expedientes'
import { DataList } from '@/components/ui/DataList'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { nombreRol } from '@/lib/estados'
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

  return (
    <DataList
      emptyDescription="Este expediente no tiene peticiones registradas."
      emptyTitle="Sin peticiones"
      fields={[
        { key: 'dependencia', label: 'Dependencia emisora', render: (row) => nombreRol(row.dependencia_emisora) },
        { key: 'codigo', label: 'Código', render: (row) => <code className={styles.codigo}>{row.requisito_codigo}</code>, secondary: true },
      ]}
      getKey={(row) => row.id}
      getTone={(row) => (row.estado_peticion === 'OBSERVADO' ? 'warning' : undefined)}
      items={peticiones}
      label="Peticiones documentales"
      renderActions={(row) =>
        puedeDescargarDocumentos ? (
          <DescargaButton fallbackFilename={`${numeroExpediente}-${row.requisito_codigo}.pdf`} peticionId={row.id} />
        ) : null
      }
      renderStatus={(row) => <StatusBadge dominio="peticion" valor={row.estado_peticion} />}
      renderSubtitle={(row) =>
        esEstudiante && row.estado_peticion === 'OBSERVADO' ? (
          <span className={styles.subsanarNote}>
            Esta petición fue observada. Por una limitación del sistema, la subsanación en línea no está disponible
            todavía para su rol; comuníquese con la dependencia correspondiente.
          </span>
        ) : null
      }
      renderTitle={(row) => row.requisito_nombre}
    />
  )
}
