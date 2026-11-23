import type { ReactNode } from 'react'
import { EmptyState } from './EmptyState'
import styles from './DataList.module.css'

export type DataListField<T> = {
  key: string
  label: string
  render: (item: T) => ReactNode
  /** Dato secundario: se oculta en móvil para priorizar lo esencial. */
  secondary?: boolean
}

export type DataListProps<T> = {
  /** Nombre accesible de la lista. */
  label: string
  items: T[]
  getKey: (item: T) => string
  /** Dato principal de cada elemento (p. ej. número de expediente con enlace). */
  renderTitle: (item: T) => ReactNode
  renderSubtitle?: (item: T) => ReactNode
  renderStatus?: (item: T) => ReactNode
  fields?: Array<DataListField<T>>
  renderActions?: (item: T) => ReactNode
  /** Destaca un elemento (p. ej. vencido u observado). */
  getTone?: (item: T) => 'warning' | 'danger' | undefined
  emptyTitle?: string
  emptyDescription?: string
}

/**
 * Lista de datos adaptable (sustituye a las tablas rígidas): filas compactas
 * y jerarquizadas en escritorio, tarjetas verticales en móvil, sin scroll
 * horizontal. Cada dato lleva su etiqueta (`<dl>`), por lo que se entiende
 * sin cabeceras de columna.
 */
export function DataList<T>({
  label,
  items,
  getKey,
  renderTitle,
  renderSubtitle,
  renderStatus,
  fields = [],
  renderActions,
  getTone,
  emptyTitle = 'Sin resultados',
  emptyDescription,
}: DataListProps<T>) {
  if (items.length === 0) {
    return <EmptyState description={emptyDescription} title={emptyTitle} />
  }

  return (
    <ul aria-label={label} className={styles.list}>
      {items.map((item) => {
        const tone = getTone?.(item)
        return (
          <li className={`${styles.item} ${tone ? styles[tone] : ''}`} key={getKey(item)}>
            <div className={styles.head}>
              <div className={styles.title}>{renderTitle(item)}</div>
              {renderSubtitle && <div className={styles.subtitle}>{renderSubtitle(item)}</div>}
            </div>
            {renderStatus && <div className={styles.status}>{renderStatus(item)}</div>}
            {fields.length > 0 && (
              <dl className={styles.fields}>
                {fields.map((field) => (
                  <div className={field.secondary ? `${styles.field} ${styles.secondary}` : styles.field} key={field.key}>
                    <dt>{field.label}</dt>
                    <dd>{field.render(item)}</dd>
                  </div>
                ))}
              </dl>
            )}
            {renderActions && <div className={styles.actions}>{renderActions(item)}</div>}
          </li>
        )
      })}
    </ul>
  )
}
