import { useEffect, useState, type CSSProperties } from 'react'

/**
 * Área visible real mientras el chat está abierto (mejora responsive de AX-D).
 *
 * En móviles, el teclado virtual reduce el *visual viewport*. En iOS no
 * cambia el alto del layout, así que un panel fijo al borde inferior quedaría
 * detrás del teclado. Con `window.visualViewport` se expone, como variables
 * CSS del asistente:
 *  - `--asistente-alto-visible`: alto visible disponible;
 *  - `--asistente-teclado`: cuánto tapa el teclado el borde inferior.
 * Sin `visualViewport` (navegadores antiguos o jsdom) no se define nada y el
 * CSS usa `100dvh`.
 */
export function useViewportVisible(activo: boolean): CSSProperties | undefined {
  const [estilo, setEstilo] = useState<CSSProperties | undefined>(undefined)

  useEffect(() => {
    const viewport = typeof window !== 'undefined' ? window.visualViewport : null
    if (!activo || !viewport) {
      return
    }
    function medir() {
      if (!viewport) {
        return
      }
      const teclado = Math.max(0, window.innerHeight - (viewport.height + viewport.offsetTop))
      setEstilo({
        ['--asistente-alto-visible' as string]: `${Math.round(viewport.height)}px`,
        ['--asistente-teclado' as string]: `${Math.round(teclado)}px`,
      })
    }
    medir()
    viewport.addEventListener('resize', medir)
    viewport.addEventListener('scroll', medir)
    return () => {
      viewport.removeEventListener('resize', medir)
      viewport.removeEventListener('scroll', medir)
      setEstilo(undefined)
    }
  }, [activo])

  return activo ? estilo : undefined
}
