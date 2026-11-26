import { useEffect, useId, useRef, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { CloseIcon } from '@/components/ui/icons'
import { AltavozIcon, DetenerIcon, EngranajeIcon, RestablecerIcon } from './iconos'
import {
  ESCALA_TEXTO,
  VELOCIDAD_LECTURA,
  formatearPorcentaje,
  formatearVelocidad,
  sonIniciales,
  type ModoColor,
} from './preferencias'
import { useAccesibilidad } from './useAccesibilidad'
import styles from './PanelAccesibilidad.module.css'

const MODOS: { modo: Exclude<ModoColor, 'ninguno'>; etiqueta: string }[] = [
  { modo: 'grises', etiqueta: 'Escala de grises' },
  { modo: 'alto-contraste', etiqueta: 'Alto contraste' },
  { modo: 'contraste-negativo', etiqueta: 'Contraste negativo' },
  { modo: 'fondo-claro', etiqueta: 'Fondo claro' },
]

/**
 * Botón flotante (cuadrante inferior izquierdo) y panel de herramientas de
 * accesibilidad (AX-A). El panel no es modal: se abre sobre la página actual
 * sin abandonarla; se cierra con Escape, con el botón de cierre o al pulsar
 * fuera, y el foco vuelve al botón que lo abrió.
 */
export function PanelAccesibilidad() {
  const a11y = useAccesibilidad()
  const { preferencias, lectura } = a11y
  const { pathname } = useLocation()
  const [abierto, setAbierto] = useState(false)
  const [aviso, setAviso] = useState('')
  const raizRef = useRef<HTMLElement>(null)
  const botonRef = useRef<HTMLButtonElement>(null)
  const tituloRef = useRef<HTMLHeadingElement>(null)
  const idPanel = useId()
  const idTitulo = useId()
  const idVelocidad = useId()
  const { detener } = lectura

  // La lectura pertenece a la vista en la que se pidió: al navegar se detiene.
  useEffect(() => {
    detener()
  }, [pathname, detener])

  useEffect(() => {
    if (!abierto) {
      return
    }
    tituloRef.current?.focus()
    function alPulsarTecla(evento: KeyboardEvent) {
      if (evento.key === 'Escape') {
        setAbierto(false)
        botonRef.current?.focus()
      }
    }
    function alPulsarFuera(evento: PointerEvent) {
      if (raizRef.current && !raizRef.current.contains(evento.target as Node)) {
        setAbierto(false)
      }
    }
    document.addEventListener('keydown', alPulsarTecla)
    document.addEventListener('pointerdown', alPulsarFuera)
    return () => {
      document.removeEventListener('keydown', alPulsarTecla)
      document.removeEventListener('pointerdown', alPulsarFuera)
    }
  }, [abierto])

  function cerrar() {
    setAbierto(false)
    botonRef.current?.focus()
  }

  function leer() {
    setAviso(lectura.leerPagina() ? 'Leyendo el contenido principal de la página.' : 'No hay contenido que leer en esta vista.')
  }

  function detenerLectura() {
    lectura.detener()
    setAviso('Lectura detenida.')
  }

  function restablecer() {
    a11y.restablecer()
    setAviso('Se restablecieron todas las opciones de accesibilidad.')
  }

  const escalaMinima = preferencias.escalaTexto <= ESCALA_TEXTO.min
  const escalaMaxima = preferencias.escalaTexto >= ESCALA_TEXTO.max

  return (
    // `data-a11y-omitir`: el propio panel nunca se lee en voz alta.
    <aside aria-label="Herramientas de accesibilidad" className={styles.raiz} data-a11y-omitir="" ref={raizRef}>
      {abierto && (
        <section aria-labelledby={idTitulo} className={`glass-floating ${styles.panel}`} id={idPanel} role="dialog">
          <header className={styles.cabecera}>
            <h2 className={styles.titulo} id={idTitulo} ref={tituloRef} tabIndex={-1}>
              Accesibilidad
            </h2>
            <button aria-label="Cerrar herramientas de accesibilidad" className={styles.cerrar} type="button" onClick={cerrar}>
              <CloseIcon size={18} />
            </button>
          </header>

          <div aria-labelledby={`${idPanel}-texto`} className={styles.grupo} role="group">
            <h3 className={styles.subtitulo} id={`${idPanel}-texto`}>
              Tamaño del texto
            </h3>
            <div className={styles.filaTexto}>
              <button className={styles.accion} disabled={escalaMinima} type="button" onClick={a11y.disminuirTexto}>
                <span aria-hidden="true" className={styles.glifo}>
                  A−
                </span>
                Disminuir texto
              </button>
              <output aria-live="polite" className={styles.valor}>
                {formatearPorcentaje(preferencias.escalaTexto)}
              </output>
              <button className={styles.accion} disabled={escalaMaxima} type="button" onClick={a11y.aumentarTexto}>
                <span aria-hidden="true" className={styles.glifo}>
                  A+
                </span>
                Aumentar texto
              </button>
            </div>
          </div>

          <div aria-labelledby={`${idPanel}-color`} className={styles.grupo} role="group">
            <h3 className={styles.subtitulo} id={`${idPanel}-color`}>
              Color y contraste
            </h3>
            <p className={styles.ayuda}>Solo un modo de color puede estar activo a la vez.</p>
            <div className={styles.rejilla}>
              {MODOS.map(({ modo, etiqueta }) => (
                <button
                  aria-pressed={preferencias.modoColor === modo}
                  className={styles.interruptor}
                  key={modo}
                  type="button"
                  onClick={() => a11y.alternarModoColor(modo)}
                >
                  {etiqueta}
                </button>
              ))}
            </div>
          </div>

          <div aria-labelledby={`${idPanel}-contenido`} className={styles.grupo} role="group">
            <h3 className={styles.subtitulo} id={`${idPanel}-contenido`}>
              Contenido
            </h3>
            <div className={styles.rejilla}>
              <button
                aria-pressed={preferencias.subrayarEnlaces}
                className={styles.interruptor}
                type="button"
                onClick={a11y.alternarSubrayarEnlaces}
              >
                Enlaces subrayados
              </button>
              <button
                aria-pressed={preferencias.fuenteLegible}
                className={styles.interruptor}
                type="button"
                onClick={a11y.alternarFuenteLegible}
              >
                Fuente legible
              </button>
            </div>
          </div>

          <div aria-labelledby={`${idPanel}-lectura`} className={styles.grupo} role="group">
            <h3 className={styles.subtitulo} id={`${idPanel}-lectura`}>
              Lectura en voz alta
            </h3>
            {lectura.disponible ? (
              <>
                <label className={styles.etiqueta} htmlFor={idVelocidad}>
                  Velocidad de lectura
                  <output className={styles.valor} htmlFor={idVelocidad}>
                    {formatearVelocidad(preferencias.velocidadLectura)}
                  </output>
                </label>
                <input
                  aria-valuetext={formatearVelocidad(preferencias.velocidadLectura)}
                  className={styles.rango}
                  id={idVelocidad}
                  max={VELOCIDAD_LECTURA.max}
                  min={VELOCIDAD_LECTURA.min}
                  step={VELOCIDAD_LECTURA.paso}
                  type="range"
                  value={preferencias.velocidadLectura}
                  onChange={(evento) => a11y.cambiarVelocidadLectura(Number(evento.target.value))}
                />
                <div className={styles.fila}>
                  <button className={styles.accion} disabled={lectura.leyendo} type="button" onClick={leer}>
                    <AltavozIcon />
                    Leer página
                  </button>
                  <button className={styles.accion} disabled={!lectura.leyendo} type="button" onClick={detenerLectura}>
                    <DetenerIcon />
                    Detener lectura
                  </button>
                </div>
              </>
            ) : (
              <p className={styles.ayuda}>
                Este navegador no permite la lectura en voz alta. Puede usar el lector de pantalla de su sistema.
              </p>
            )}
          </div>

          <footer className={styles.pie}>
            <button
              className={styles.restablecer}
              disabled={sonIniciales(preferencias) && !lectura.leyendo}
              type="button"
              onClick={restablecer}
            >
              <RestablecerIcon />
              Restablecer cambios
            </button>
          </footer>
          <p aria-live="polite" className="sr-only" role="status">
            {aviso}
          </p>
        </section>
      )}

      <button
        aria-controls={abierto ? idPanel : undefined}
        aria-expanded={abierto}
        aria-label="Herramientas de accesibilidad"
        className={`glass-floating ${styles.lanzador}`}
        ref={botonRef}
        type="button"
        onClick={() => (abierto ? cerrar() : setAbierto(true))}
      >
        <span className={styles.engranaje}>
          <EngranajeIcon />
        </span>
        <span aria-hidden="true" className={styles.tooltip}>
          Accesibilidad
        </span>
      </button>
    </aside>
  )
}
