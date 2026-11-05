import type { ReactNode } from 'react'
import { EmptyState } from './EmptyState'
import { Spinner } from './Spinner'
import styles from './Table.module.css'

export type TableColumn<T> = {
  key: string
  header: string
  render: (row: T) => ReactNode
}

export type TableProps<T> = {
  caption: string
  columns: Array<TableColumn<T>>
  rows: T[]
  rowKey: (row: T) => string
  loading?: boolean
  emptyTitle?: string
  emptyDescription?: string
}

export function Table<T>({
  caption,
  columns,
  rows,
  rowKey,
  loading = false,
  emptyTitle = 'Sin resultados',
  emptyDescription,
}: TableProps<T>) {
  if (loading) {
    return (
      <div className={styles.loading}>
        <Spinner label="Cargando datos…" />
      </div>
    )
  }

  if (rows.length === 0) {
    return <EmptyState description={emptyDescription} title={emptyTitle} />
  }

  return (
    <div className={styles.wrapper}>
      {/* eslint-disable jsx-a11y/no-noninteractive-tabindex -- patrón WCAG/ARIA APG para regiones con scroll horizontal */}
      <div
        aria-label={`${caption} (desplazamiento horizontal)`}
        className={styles.tableScroll}
        role="region"
        tabIndex={0}
      >
        {/* eslint-enable jsx-a11y/no-noninteractive-tabindex */}
        <table className={styles.table}>
          <caption className="sr-only">{caption}</caption>
          <thead>
            <tr>
              {columns.map((column) => (
                <th key={column.key} scope="col">
                  {column.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={rowKey(row)}>
                {columns.map((column) => (
                  <td key={column.key}>{column.render(row)}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <ul className={styles.cards}>
        {rows.map((row) => (
          <li className={styles.card} key={rowKey(row)}>
            {columns.map((column) => (
              <div className={styles.cardRow} key={column.key}>
                <span className={styles.cardLabel}>{column.header}</span>
                <span className={styles.cardValue}>{column.render(row)}</span>
              </div>
            ))}
          </li>
        ))}
      </ul>
    </div>
  )
}
