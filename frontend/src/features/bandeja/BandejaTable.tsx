import { Link } from 'react-router-dom'
import type { BandejaOperativaItem } from '@/api/endpoints/expedientes'
import { Badge } from '@/components/ui/Badge'
import { Table, type TableColumn } from '@/components/ui/Table'
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
        <Badge variant="danger">
          {vencimiento.dias === 0 ? 'Vencido hoy' : `Vencido hace ${vencimiento.dias} días calendario`}
        </Badge>
      )
    case 'hoy':
      return <Badge variant="warning">Vence hoy</Badge>
    case 'pendiente':
      return <span>{`Faltan ${vencimiento.dias} días calendario`}</span>
  }
}

/**
 * FE-T702/FE-T705: columnas reales de `BandejaExpedienteSerializer`. `Table`
 * dibuja la tabla en escritorio y tarjetas en móvil. Sin acciones de
 * escritura: solo navegación a V-08 (`/bandeja/:id`), con precarga del
 * detalle al enfocar o pasar el puntero sobre el enlace.
 */
export function BandejaTable({ filas, ahora, onPrecargar }: BandejaTableProps) {
  const columns: Array<TableColumn<BandejaOperativaItem>> = [
    {
      key: 'numero_expediente',
      header: 'Expediente',
      render: (row) => (
        <Link
          aria-label={`Abrir expediente ${row.numero_expediente}`}
          className={styles.enlace}
          to={`/bandeja/${row.id}`}
          onFocus={() => onPrecargar(row.id)}
          onMouseEnter={() => onPrecargar(row.id)}
        >
          {row.numero_expediente}
        </Link>
      ),
    },
    { key: 'estado', header: 'Estado', render: (row) => <Badge variant="info">{row.estado}</Badge> },
    { key: 'fecha_limite_atencion', header: 'Fecha límite', render: (row) => formatFecha(row.fecha_limite_atencion) },
    { key: 'plazo', header: 'Plazo', render: (row) => <Plazo ahora={ahora} fechaLimite={row.fecha_limite_atencion} /> },
    { key: 'fecha_recepcion', header: 'Recepción', render: (row) => formatFecha(row.fecha_recepcion) },
    { key: 'numero_providencia', header: 'Providencia', render: (row) => row.numero_providencia ?? '—' },
    {
      key: 'estudiante_id',
      header: 'Estudiante (id)',
      render: (row) => <code className={styles.id}>{abreviarId(row.estudiante_id)}</code>,
    },
    {
      key: 'carrera_facultad',
      header: 'Carrera / facultad (id)',
      render: (row) => (
        <code className={styles.id}>
          {abreviarId(row.carrera_id)} / {abreviarId(row.facultad_id)}
        </code>
      ),
    },
    { key: 'fecha_creacion', header: 'Creado', render: (row) => formatFecha(row.fecha_creacion) },
  ]

  return (
    <Table
      caption="Expedientes de la bandeja"
      columns={columns}
      emptyDescription="Ningún expediente de esta página coincide con los filtros."
      emptyTitle="Sin coincidencias en esta página"
      rowKey={(row) => row.id}
      rows={filas}
    />
  )
}
