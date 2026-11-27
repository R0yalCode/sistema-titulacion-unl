import { createContext, useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState, type ReactNode } from 'react'
import { dividirEnEnunciados, extraerTextoLegible, lecturaDisponible, raizDeLectura } from './lectorPagina'
import { crearMotorLectura, type CausaErrorLectura, type EstadoLectura } from './motorLectura'
import {
  ESCALA_TEXTO,
  PREFERENCIAS_INICIALES,
  VELOCIDAD_LECTURA,
  aplicarPreferencias,
  guardarPreferencias,
  leerPreferencias,
  limitar,
  type ModoColor,
  type PreferenciasAccesibilidad,
} from './preferencias'

export type AccesibilidadContextValue = {
  preferencias: PreferenciasAccesibilidad
  aumentarTexto: () => void
  disminuirTexto: () => void
  /** Activa `modo` (desactivando el anterior) o lo apaga si ya estaba activo. */
  alternarModoColor: (modo: Exclude<ModoColor, 'ninguno'>) => void
  alternarSubrayarEnlaces: () => void
  alternarFuenteLegible: () => void
  cambiarVelocidadLectura: (velocidad: number) => void
  restablecer: () => void
  lectura: {
    disponible: boolean
    /** Estado real, confirmado por los eventos del motor de voz (INC-23). */
    estado: EstadoLectura
    /** Causa y código del navegador cuando `estado` es `error`. */
    causa?: CausaErrorLectura
    codigo?: string
    /** Lectura en curso: preparando o leyendo. */
    leyendo: boolean
    leerPagina: () => void
    /** `silencioso`: detiene sin anunciarlo (cambio de vista, restablecer). */
    detener: (opciones?: { silencioso?: boolean }) => void
  }
}

type SituacionLectura = { estado: EstadoLectura; causa?: CausaErrorLectura; codigo?: string }

export const AccesibilidadContext = createContext<AccesibilidadContextValue | undefined>(undefined)

/**
 * Servicio global de accesibilidad (AX-A): una sola fuente de verdad para las
 * preferencias, aplicadas al documento completo y persistidas entre
 * navegaciones y recargas.
 */
export function AccesibilidadProvider({ children }: { children: ReactNode }) {
  const [preferencias, setPreferencias] = useState<PreferenciasAccesibilidad>(leerPreferencias)
  const [situacion, setSituacion] = useState<SituacionLectura>({ estado: 'inactiva' })
  const disponible = useMemo(() => typeof window !== 'undefined' && lecturaDisponible(), [])
  const motor = useMemo(() => (disponible ? crearMotorLectura() : null), [disponible])
  // La velocidad se consulta en cada fragmento: mover el control durante la
  // lectura se aplica al fragmento siguiente.
  const velocidadRef = useRef(preferencias.velocidadLectura)
  const leyendo = situacion.estado === 'preparando' || situacion.estado === 'leyendo'

  useEffect(() => {
    velocidadRef.current = preferencias.velocidadLectura
  }, [preferencias.velocidadLectura])

  // Antes de pintar, para que la vista no parpadee con el estilo por defecto.
  useLayoutEffect(() => {
    aplicarPreferencias(preferencias)
  }, [preferencias])

  useEffect(() => {
    guardarPreferencias(preferencias)
  }, [preferencias])

  // Al desmontar (cierre de la aplicación o pruebas) no queda voz sonando.
  useEffect(() => () => motor?.detener(), [motor])

  const actualizar = useCallback((cambio: (previas: PreferenciasAccesibilidad) => PreferenciasAccesibilidad) => {
    setPreferencias((previas) => cambio(previas))
  }, [])

  const detener = useCallback(
    (opciones: { silencioso?: boolean } = {}) => {
      motor?.detener()
      setSituacion((previa) => {
        if (opciones.silencioso) {
          return previa.estado === 'inactiva' ? previa : { estado: 'inactiva' }
        }
        return previa.estado === 'preparando' || previa.estado === 'leyendo' ? { estado: 'detenida' } : previa
      })
    },
    [motor],
  )

  const leerPagina = useCallback(() => {
    if (!motor) {
      setSituacion({ estado: 'error', causa: 'no-soportada' })
      return
    }
    // El texto se toma en el momento de pulsar: el contenido de la vista actual.
    const enunciados = dividirEnEnunciados(extraerTextoLegible(raizDeLectura()))
    void motor.leer(enunciados, () => velocidadRef.current, (cambio) => setSituacion(cambio))
  }, [motor])

  const value = useMemo<AccesibilidadContextValue>(
    () => ({
      preferencias,
      aumentarTexto: () =>
        actualizar((previas) => ({
          ...previas,
          escalaTexto: limitar(previas.escalaTexto + ESCALA_TEXTO.paso, ESCALA_TEXTO.min, ESCALA_TEXTO.max),
        })),
      disminuirTexto: () =>
        actualizar((previas) => ({
          ...previas,
          escalaTexto: limitar(previas.escalaTexto - ESCALA_TEXTO.paso, ESCALA_TEXTO.min, ESCALA_TEXTO.max),
        })),
      alternarModoColor: (modo) =>
        actualizar((previas) => ({ ...previas, modoColor: previas.modoColor === modo ? 'ninguno' : modo })),
      alternarSubrayarEnlaces: () => actualizar((previas) => ({ ...previas, subrayarEnlaces: !previas.subrayarEnlaces })),
      alternarFuenteLegible: () => actualizar((previas) => ({ ...previas, fuenteLegible: !previas.fuenteLegible })),
      cambiarVelocidadLectura: (velocidad) =>
        actualizar((previas) => ({
          ...previas,
          velocidadLectura: limitar(velocidad, VELOCIDAD_LECTURA.min, VELOCIDAD_LECTURA.max),
        })),
      restablecer: () => {
        detener({ silencioso: true })
        setPreferencias({ ...PREFERENCIAS_INICIALES })
      },
      lectura: { disponible, ...situacion, leyendo, leerPagina, detener },
    }),
    [preferencias, actualizar, detener, disponible, situacion, leyendo, leerPagina],
  )

  return <AccesibilidadContext.Provider value={value}>{children}</AccesibilidadContext.Provider>
}
