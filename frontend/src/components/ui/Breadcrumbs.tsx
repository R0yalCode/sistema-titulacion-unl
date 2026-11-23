import { Link } from 'react-router-dom'
import { ChevronRightIcon } from './icons'
import styles from './Breadcrumbs.module.css'

export type BreadcrumbItem = {
  label: string
  /** Sin `to`, el elemento es la página actual. */
  to?: string
}

/** Migas de pan (patrón WAI-ARIA): la última es la página actual. */
export function Breadcrumbs({ items }: { items: BreadcrumbItem[] }) {
  if (items.length < 2) {
    return null
  }
  return (
    <nav aria-label="Ruta de navegación" className={styles.nav}>
      <ol className={styles.list}>
        {items.map((item, index) => {
          const actual = index === items.length - 1
          return (
            <li className={styles.item} key={`${item.label}-${index}`}>
              {item.to && !actual ? (
                <Link className={styles.link} to={item.to}>
                  {item.label}
                </Link>
              ) : (
                <span aria-current={actual ? 'page' : undefined} className={styles.current}>
                  {item.label}
                </span>
              )}
              {!actual && (
                <span aria-hidden="true" className={styles.separator}>
                  <ChevronRightIcon size={14} />
                </span>
              )}
            </li>
          )
        })}
      </ol>
    </nav>
  )
}
