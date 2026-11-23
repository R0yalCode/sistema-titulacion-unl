import { Link } from 'react-router-dom'
import type { BandejaOperativaItem } from '@/api/endpoints/expedientes'
import { Badge } from '@/components/ui/Badge'
import { DataList } from '@/components/ui/DataList'
import { ChevronRightIcon } from '@/components/ui/icons'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { formatFecha } from '@/lib/dates'
import { abreviarId, calcularVencimiento } from './bandejaReglas'
import styles from './BandejaTable.module.css'

type BandejaTableProps = {
  filas: BandejaOperativaItem[]
  ahora: Date
  onPrecargar: (id: string) => void
}

function Plazo({ fechaLimite, ahora }: { fechaLimite: string | null; ahora: Date }) {
  const vencimiento = calcularVencimiento(fechaLimite, ahora)
  switch (vencimiento.tipo) {
    case 'sin-fecha':
      return <span>Sin fecha límite</span>
    case 'vencido':
      return (
        <Badge icon variant="danger">
          {vencimiento.dias === 0
            ? 'Vencido hoy'
            : `Vencido hace ${vencimiento.dias} ${vencimiento.dias === 1 ? 'día' : 'días'} calendario`}
        </Badge>
      )
    case 'hoy':
      return (
        <Badge icon variant="warning">
          Vence hoy
        </Badge>
      )
    case 'pendiente':
      return (
        <span>
          {vencimiento.dias === 1 ? 'Falta 1 día calendario' : `Faltan ${vencimiento.dias} días calendario`}
        </span>
      )
  }
}

/**
 * FE-T702/FE-T705: datos reales de `BandejaExpedienteSerializer` en una lista
 * adaptable (filas en escritorio, tarjetas en móvil). Sin acciones de
 * escritura: solo navegación a V-08 (`/bandeja/:id`), con precarga del
 * detalle al enfocar o pasar el puntero sobre el enlace.
 */
export function BandejaTable({ filas, ahora, onPrecargar }: BandejaTableProps) {
  return (
    <DataList
      emptyDescription="Ningún expediente de esta página coincide con los filtros."
      emptyTitle="Sin coincidencias en esta página"
      fields={[
        { key: 'limite', label: 'Fecha límite', render: (row) => formatFecha(row.fecha_limite_atencion) },
        { key: 'plazo', label: 'Plazo', render: (row) => <Plazo ahora={ahora} fechaLimite={row.fecha_limite_atencion} /> },
        { key: 'recepcion', label: 'Recepción', render: (row) => formatFecha(row.fecha_recepcion), secondary: true },
        {
          key: 'estudiante',
          label: 'Estudiante (id)',
          render: (row) => <code className={styles.id}>{abreviarId(row.estudiante_id)}</code>,
          secondary: true,
        },
        {
          key: 'carrera',
          label: 'Carrera / facultad (id)',
          render: (row) => (
            <code className={styles.id}>
              {abreviarId(row.carrera_id)} / {abreviarId(row.facultad_id)}
            </code>
          ),
          secondary: true,
        },
      ]}
      getKey={(row) => row.id}
      getTone={(row) => {
        const tipo = calcularVencimiento(row.fecha_limite_atencion, ahora).tipo
        return tipo === 'vencido' ? 'danger' : tipo === 'hoy' ? 'warning' : undefined
      }}
      items={filas}
      label="Expedientes de la bandeja"
      renderActions={(row) => (
        <Link
          aria-label={`Abrir expediente ${row.numero_expediente}`}
          className={styles.abrir}
          to={`/bandeja/${row.id}`}
          onFocus={() => onPrecargar(row.id)}
          onMouseEnter={() => onPrecargar(row.id)}
        >
          Abrir
          <ChevronRightIcon size={16} />
        </Link>
      )}
      renderStatus={(row) => <StatusBadge dominio="expediente" valor={row.estado} />}
      renderSubtitle={(row) =>
        `${row.numero_providencia ?? 'Sin providencia'} · creado ${formatFecha(row.fecha_creacion)}`
      }
      renderTitle={(row) => row.numero_expediente}
    />
  )
}
