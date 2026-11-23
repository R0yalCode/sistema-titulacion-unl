import { lazy, Suspense, useEffect, useRef, useState } from 'react'
import { SearchIcon } from '@/components/ui/icons'
import type { DestinoBusqueda } from './AdminSearchDialog'
import styles from './AdminSearch.module.css'

const AdminSearchDialog = lazy(() => import('./AdminSearchDialog'))

/**
 * Buscador del administrador (Ctrl/Cmd + K). El backend no ofrece búsqueda
 * global (BE-09): localiza secciones reales y expedientes de la bandeja.
 */
export function AdminSearch({ destinos }: { destinos: DestinoBusqueda[] }) {
  const [abierto, setAbierto] = useState(false)
  const triggerRef = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault()
        setAbierto(true)
      }
    }
    document.addEventListener('keydown', onKeyDown)
    return () => document.removeEventListener('keydown', onKeyDown)
  }, [])

  function cerrar() {
    setAbierto(false)
    triggerRef.current?.focus()
  }

  return (
    <>
      <button
        aria-haspopup="dialog"
        aria-keyshortcuts="Control+K Meta+K"
        aria-label="Buscar secciones y expedientes"
        className={styles.trigger}
        ref={triggerRef}
        type="button"
        onClick={() => setAbierto(true)}
      >
        <SearchIcon size={16} />
        <span className={styles.triggerText}>Buscar…</span>
        <kbd className={styles.kbd}>Ctrl K</kbd>
      </button>
      {abierto && (
        <Suspense fallback={null}>
          <AdminSearchDialog destinos={destinos} onClose={cerrar} />
        </Suspense>
      )}
    </>
  )
}
