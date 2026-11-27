import { useContext, useEffect, useId, useRef, useState, type FormEvent } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useNombreVisible } from '@/components/layout/useNombreVisible'
import { CloseIcon, SendIcon } from '@/components/ui/icons'
import {
  AsistenteNoDisponibleError,
  ClienteAsistenteContext,
  type FuenteAsistente,
} from './clienteAsistente'
import { ASISTENTE } from './configuracion'
import { MENSAJE_CANALES_OFICIALES, MENSAJE_NO_DISPONIBLE, esConsultaNormativa } from './consultaNormativa'
import { preguntasPara, type EnlacePregunta, type PreguntaFrecuente } from './preguntasFrecuentes'
import { useViewportVisible } from './useViewportVisible'
import styles from './AsistenteFlotante.module.css'

type Mensaje = {
  id: number
  autor: 'usuario' | 'asistente'
  parrafos: string[]
  /** faq: contenido configurado; ia: respuesta del servicio; aviso/error: el servicio no respondió. */
  tipo?: 'faq' | 'ia' | 'aviso' | 'error'
  enlaces?: EnlacePregunta[]
  fuentes?: FuenteAsistente[]
  /** Pregunta que se puede reenviar al servicio (reintento real). */
  reintentar?: string
}

const formatoFecha = new Intl.DateTimeFormat('es-EC', {
  weekday: 'long',
  day: 'numeric',
  month: 'long',
  year: 'numeric',
})

function describirFuente(fuente: FuenteAsistente): string {
  const partes = [
    fuente.version && `versión ${fuente.version}`,
    fuente.seccion && `sección ${fuente.seccion}`,
    fuente.pagina !== undefined && `página ${fuente.pagina}`,
    fuente.vigente === false && 'no vigente',
  ].filter(Boolean)
  return partes.length > 0 ? `${fuente.titulo} (${partes.join(', ')})` : fuente.titulo
}

/**
 * Asistente institucional (AX-D, DK-010): botón flotante con la mascota en
 * el cuadrante inferior derecho y una ventana de chat no modal.
 *
 * - Preguntas frecuentes configurables, solo sobre el uso del sistema.
 * - Las preguntas escritas van al `ClienteAsistente`. Hoy no hay servicio:
 *   se informa con honestidad y se ofrece un reintento real. Las consultas
 *   normativas se remiten a los canales oficiales.
 * - Nunca hay respuestas simuladas, endpoints inventados ni fuentes ficticias.
 */
export function AsistenteFlotante() {
  const usuario = useNombreVisible()
  const cliente = useContext(ClienteAsistenteContext)
  const { pathname } = useLocation()
  // Abierta solo en la ruta donde se abrió: al navegar (p. ej. un enlace de
  // una respuesta) se cierra y la vista queda visible; la conversación se conserva.
  const [abiertaEn, setAbiertaEn] = useState<string | null>(null)
  const abierta = abiertaEn === pathname
  const [mensajes, setMensajes] = useState<Mensaje[]>([])
  const [texto, setTexto] = useState('')
  const [procesando, setProcesando] = useState(false)
  const [fecha, setFecha] = useState(() => new Date())
  const botonRef = useRef<HTMLButtonElement>(null)
  const campoRef = useRef<HTMLInputElement>(null)
  const finRef = useRef<HTMLDivElement>(null)
  const siguienteId = useRef(1)
  // En móvil el lanzador se oculta con el panel abierto: el foco se devuelve
  // después de volver a pintarlo, no en el mismo evento de cierre.
  const devolverFoco = useRef(false)
  const viewport = useViewportVisible(abierta)
  const idPanel = useId()
  const idTitulo = useId()
  const idCampo = useId()

  useEffect(() => {
    if (!abierta) {
      return
    }
    campoRef.current?.focus()
    function alPulsarTecla(evento: KeyboardEvent) {
      if (evento.key === 'Escape') {
        devolverFoco.current = true
        setAbiertaEn(null)
      }
    }
    document.addEventListener('keydown', alPulsarTecla)
    return () => document.removeEventListener('keydown', alPulsarTecla)
  }, [abierta])

  useEffect(() => {
    if (!abierta && devolverFoco.current) {
      devolverFoco.current = false
      botonRef.current?.focus()
    }
  }, [abierta])

  useEffect(() => {
    finRef.current?.scrollIntoView?.({ block: 'end' })
  }, [mensajes, procesando])

  function abrir() {
    setFecha(new Date())
    setAbiertaEn(pathname)
  }

  function cerrar() {
    devolverFoco.current = true
    setAbiertaEn(null)
  }

  function agregar(...nuevos: Omit<Mensaje, 'id'>[]) {
    setMensajes((previos) => [...previos, ...nuevos.map((mensaje) => ({ ...mensaje, id: siguienteId.current++ }))])
  }

  function responderFrecuente(pregunta: PreguntaFrecuente) {
    agregar(
      { autor: 'usuario', parrafos: [pregunta.pregunta] },
      { autor: 'asistente', tipo: 'faq', parrafos: pregunta.respuesta, enlaces: pregunta.enlaces },
    )
  }

  async function consultar(pregunta: string) {
    setProcesando(true)
    try {
      const respuesta = await cliente.consultar(pregunta)
      agregar({ autor: 'asistente', tipo: 'ia', parrafos: [respuesta.texto], fuentes: respuesta.fuentes })
    } catch (error) {
      const normativa = esConsultaNormativa(pregunta)
      const parrafos = normativa
        ? [MENSAJE_CANALES_OFICIALES]
        : [error instanceof AsistenteNoDisponibleError ? MENSAJE_NO_DISPONIBLE : 'No se pudo completar la consulta. Inténtalo de nuevo.']
      agregar({ autor: 'asistente', tipo: normativa ? 'aviso' : 'error', parrafos, reintentar: pregunta })
    } finally {
      setProcesando(false)
    }
  }

  function enviar(evento: FormEvent) {
    evento.preventDefault()
    const pregunta = texto.trim()
    if (!pregunta || procesando) {
      return
    }
    setTexto('')
    agregar({ autor: 'usuario', parrafos: [pregunta] })
    void consultar(pregunta)
  }

  const preguntas = preguntasPara(usuario.esEstudiante)

  return (
    // `data-a11y-omitir`: «Leer página» (AX-A) no lee el asistente.
    <aside
      aria-label="Asistente de ayuda"
      className={styles.raiz}
      data-a11y-omitir=""
      data-abierta={abierta ? 'true' : 'false'}
      style={viewport}
    >
      {abierta && (
        <section aria-labelledby={idTitulo} className={styles.panel} id={idPanel} role="dialog">
          <header className={styles.cabecera}>
            <img
              alt=""
              className={styles.mascotaCabecera}
              decoding="async"
              height={ASISTENTE.mascota.alto}
              src={ASISTENTE.mascota.src}
              width={ASISTENTE.mascota.ancho}
            />
            <div className={styles.titulos}>
              <h2 className={styles.titulo} id={idTitulo}>
                {ASISTENTE.nombre}
              </h2>
              <p className={styles.subtitulo}>Ayuda sobre el uso del sistema</p>
            </div>
            <button aria-label="Cerrar el asistente" className={styles.cerrar} type="button" onClick={cerrar}>
              <CloseIcon size={18} />
            </button>
          </header>

          <div className={styles.cuerpo}>
            <div className={styles.saludo}>
              <p className={styles.hola}>{usuario.esEstudiante ? `Hola, ${usuario.nombre}.` : 'Hola.'}</p>
              {!usuario.esEstudiante && <p className={styles.rol}>Ingresaste como {usuario.nombre}.</p>}
              <p>
                Soy tu asistente de SGT-SIAAF. Estoy aquí para ayudarte a utilizar el sistema de titulación de la
                Universidad Nacional de Loja.
              </p>
              <p>¿En qué puedo ayudarte hoy?</p>
              <p className={styles.fecha}>
                <time dateTime={fecha.toISOString().slice(0, 10)}>{formatoFecha.format(fecha)}</time>
              </p>
            </div>

            <div aria-labelledby={`${idPanel}-faq`} className={styles.frecuentes} role="group">
              <h3 className={styles.subtituloSeccion} id={`${idPanel}-faq`}>
                Preguntas frecuentes
              </h3>
              <ul className={styles.listaFrecuentes}>
                {preguntas.map((pregunta) => (
                  <li key={pregunta.id}>
                    <button className={styles.frecuente} type="button" onClick={() => responderFrecuente(pregunta)}>
                      {pregunta.pregunta}
                    </button>
                  </li>
                ))}
              </ul>
            </div>

            <div aria-label="Conversación" aria-live="polite" className={styles.registro} role="log">
              {mensajes.map((mensaje) => (
                <article
                  className={`${styles.mensaje} ${mensaje.autor === 'usuario' ? styles.usuario : styles.asistente}`}
                  data-tipo={mensaje.tipo}
                  key={mensaje.id}
                >
                  <p className="sr-only">{mensaje.autor === 'usuario' ? 'Tú:' : `${ASISTENTE.nombre}:`}</p>
                  {mensaje.parrafos.map((parrafo) => (
                    <p key={parrafo}>{parrafo}</p>
                  ))}
                  {mensaje.enlaces && mensaje.enlaces.length > 0 && (
                    <ul className={styles.enlaces}>
                      {mensaje.enlaces.map((enlace) => (
                        <li key={enlace.destino}>
                          <Link to={enlace.destino}>{enlace.etiqueta}</Link>
                        </li>
                      ))}
                    </ul>
                  )}
                  {mensaje.fuentes && mensaje.fuentes.length > 0 && (
                    <div className={styles.fuentes}>
                      <p className={styles.fuentesTitulo}>Fuentes consultadas</p>
                      <ul>
                        {mensaje.fuentes.map((fuente) => (
                          <li key={describirFuente(fuente)}>{describirFuente(fuente)}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {mensaje.reintentar && (
                    <button
                      className={styles.reintentar}
                      disabled={procesando}
                      type="button"
                      onClick={() => void consultar(mensaje.reintentar as string)}
                    >
                      Reintentar
                    </button>
                  )}
                </article>
              ))}
              {procesando && (
                <p className={styles.procesando} role="status">
                  <span aria-hidden="true" className={styles.puntos}>
                    <span />
                    <span />
                    <span />
                  </span>
                  Procesando tu consulta…
                </p>
              )}
              <div ref={finRef} />
            </div>
          </div>

          <form className={styles.formulario} onSubmit={enviar}>
            <label className="sr-only" htmlFor={idCampo}>
              Escribe tu pregunta
            </label>
            <input
              autoComplete="off"
              className={styles.campo}
              id={idCampo}
              maxLength={ASISTENTE.longitudMaximaPregunta}
              placeholder="Escribe tu pregunta…"
              ref={campoRef}
              type="text"
              value={texto}
              onChange={(evento) => setTexto(evento.target.value)}
            />
            <button aria-label="Enviar pregunta" className={styles.enviar} disabled={!texto.trim() || procesando} type="submit">
              <SendIcon size={18} />
            </button>
          </form>
          <p className={styles.aviso}>Orientación sobre el uso del sistema. No sustituye la información oficial de la UNL.</p>
        </section>
      )}

      <button
        aria-controls={abierta ? idPanel : undefined}
        aria-expanded={abierta}
        aria-label={abierta ? 'Cerrar el asistente de ayuda' : 'Abrir el asistente de ayuda'}
        className={styles.lanzador}
        ref={botonRef}
        type="button"
        onClick={() => (abierta ? cerrar() : abrir())}
      >
        {/* Recorte circular fijo; dentro, la mascota da un pequeño salto
            periódico (solo con el panel cerrado y sin movimiento reducido). */}
        <span aria-hidden="true" className={styles.recorte}>
          <span className={styles.salto} data-animacion={abierta ? 'pausada' : 'activa'}>
            <img
              alt=""
              className={styles.mascota}
              decoding="async"
              height={ASISTENTE.mascota.alto}
              src={ASISTENTE.mascota.src}
              width={ASISTENTE.mascota.ancho}
            />
          </span>
        </span>
        <span aria-hidden="true" className={styles.interrogacion}>
          ?
        </span>
        <span aria-hidden="true" className={styles.tooltip}>
          ¿Necesitas ayuda?
        </span>
      </button>
    </aside>
  )
}
