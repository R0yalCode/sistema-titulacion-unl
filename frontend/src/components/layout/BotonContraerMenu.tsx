import { useEffect, useId, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { ChevronLeftIcon } from '@/components/ui/icons'
import styles from './BotonContraerMenu.module.css'

type BotonContraerMenuProps = {
  contraido: boolean
  onAlternar: () => void
}

type Posicion = { top: number; left: number }

/**
 * Control para contraer y expandir el sidebar de escritorio (AX-B, DK-010),
 * junto al logo institucional.
 *
 * El tooltip se pinta en un portal sobre `body`: el sidebar recorta su
 * desbordamiento (animación de ancho) y su `backdrop-filter` crea un bloque
 * contenedor que también atraparía un `position: fixed`. Aparece al pasar el
 * cursor o enfocar con teclado, permanece mientras el cursor está sobre él y
 * se descarta con Escape (WCAG 1.4.13).
 */
export function BotonContraerMenu({ contraido, onAlternar }: BotonContraerMenuProps) {
  const etiqueta = contraido ? 'Expandir menú' : 'Contraer menú'
  const botonRef = useRef<HTMLButtonElement>(null)
  const ocultarRef = useRef<number | undefined>(undefined)
  const [posicion, setPosicion] = useState<Posicion | null>(null)
  const idTooltip = useId()

  function mostrar() {
    window.clearTimeout(ocultarRef.current)
    const rect = botonRef.current?.getBoundingClientRect()
    if (rect) {
      // A la derecha del sidebar (no encima de su borde), alineado con el botón.
      const bordeSidebar = botonRef.current?.closest('aside')?.getBoundingClientRect().right ?? 0
      setPosicion({ top: rect.top + rect.height / 2, left: Math.max(rect.right, bordeSidebar) + 8 })
    }
  }

  function ocultarEnBreve() {
    window.clearTimeout(ocultarRef.current)
    ocultarRef.current = window.setTimeout(() => setPosicion(null), 120)
  }

  function ocultar() {
    window.clearTimeout(ocultarRef.current)
    setPosicion(null)
  }

  useEffect(() => {
    if (!posicion) {
      return
    }
    function alPulsarTecla(evento: KeyboardEvent) {
      if (evento.key === 'Escape') {
        ocultar()
      }
    }
    // Si la vista se desplaza o cambia de tamaño, el tooltip ya no está anclado.
    window.addEventListener('scroll', ocultar, true)
    window.addEventListener('resize', ocultar)
    document.addEventListener('keydown', alPulsarTecla)
    return () => {
      window.removeEventListener('scroll', ocultar, true)
      window.removeEventListener('resize', ocultar)
      document.removeEventListener('keydown', alPulsarTecla)
    }
  }, [posicion])

  useEffect(() => () => window.clearTimeout(ocultarRef.current), [])

  function alternar() {
    onAlternar()
    // El ancho cambia con animación: el tooltip se recoloca al volver a pasar.
    ocultar()
  }

  return (
    <>
      <button
        aria-describedby={posicion ? idTooltip : undefined}
        aria-expanded={!contraido}
        aria-label={etiqueta}
        className={styles.boton}
        data-contraido={contraido ? 'true' : undefined}
        ref={botonRef}
        type="button"
        onBlur={ocultar}
        onClick={alternar}
        onFocus={mostrar}
        onMouseEnter={mostrar}
        onMouseLeave={ocultarEnBreve}
      >
        <ChevronLeftIcon className={styles.icono} size={18} />
      </button>
      {posicion &&
        createPortal(
          <div
            className={styles.tooltip}
            id={idTooltip}
            role="tooltip"
            style={{ top: posicion.top, left: posicion.left }}
            onMouseEnter={mostrar}
            onMouseLeave={ocultarEnBreve}
          >
            {etiqueta}
          </div>,
          document.body,
        )}
    </>
  )
}
