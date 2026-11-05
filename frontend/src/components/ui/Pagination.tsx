import { Button } from './Button'
import styles from './Pagination.module.css'

export type PaginationProps = {
  count: number
  pageSize: number
  page: number
  onPageChange: (page: number) => void
}

export function Pagination({ count, pageSize, page, onPageChange }: PaginationProps) {
  const totalPages = Math.max(1, Math.ceil(count / pageSize))
  const canGoPrevious = page > 1
  const canGoNext = page < totalPages

  return (
    <nav aria-label="Paginación" className={styles.nav}>
      <Button
        disabled={!canGoPrevious}
        onClick={() => onPageChange(page - 1)}
        size="sm"
        variant="secondary"
      >
        Anterior
      </Button>
      <p aria-live="polite" className={styles.status}>
        Página {page} de {totalPages}
      </p>
      <Button disabled={!canGoNext} onClick={() => onPageChange(page + 1)} size="sm" variant="secondary">
        Siguiente
      </Button>
    </nav>
  )
}
