import { createContext, useCallback, useEffect, useLayoutEffect, useMemo, useState, type ReactNode } from 'react'
import {
  detenerLectura,
  dividirEnEnunciados,
  extraerTextoLegible,
  leerEnVozAlta,
  lecturaDisponible,
  raizDeLectura,
} from './lectorPagina'
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
    leyendo: boolean
    /** `false` si no había contenido legible que leer. */
    leerPagina: () => boolean
    detener: () => void
  }
}

export const AccesibilidadContext = createContext<AccesibilidadContextValue | undefined>(undefined)

/**
 * Servicio global de accesibilidad (AX-A): una sola fuente de verdad para las
 * preferencias, aplicadas al documento completo y persistidas entre
 * navegaciones y recargas.
 */
export function AccesibilidadProvider({ children }: { children: ReactNode }) {
  const [preferencias, setPreferencias] = useState<PreferenciasAccesibilidad>(leerPreferencias)
  const [leyendo, setLeyendo] = useState(false)
  const disponible = useMemo(() => typeof window !== 'undefined' && lecturaDisponible(), [])

  // Antes de pintar, para que la vista no parpadee con el estilo por defecto.
  useLayoutEffect(() => {
    aplicarPreferencias(preferencias)
  }, [preferencias])

  useEffect(() => {
    guardarPreferencias(preferencias)
  }, [preferencias])

  // Al desmontar (cierre de la aplicación o pruebas) no queda voz sonando.
  useEffect(() => () => detenerLectura(), [])

  const actualizar = useCallback((cambio: (previas: PreferenciasAccesibilidad) => PreferenciasAccesibilidad) => {
    setPreferencias((previas) => cambio(previas))
  }, [])

  const detener = useCallback(() => {
    detenerLectura()
    setLeyendo(false)
  }, [])

  const leerPagina = useCallback(() => {
    const enunciados = dividirEnEnunciados(extraerTextoLegible(raizDeLectura()))
    const iniciada = leerEnVozAlta(enunciados, preferencias.velocidadLectura, () => setLeyendo(false))
    setLeyendo(iniciada)
    return iniciada
  }, [preferencias.velocidadLectura])

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
        detener()
        setPreferencias({ ...PREFERENCIAS_INICIALES })
      },
      lectura: { disponible, leyendo, leerPagina, detener },
    }),
    [preferencias, actualizar, detener, disponible, leyendo, leerPagina],
  )

  return <AccesibilidadContext.Provider value={value}>{children}</AccesibilidadContext.Provider>
}
