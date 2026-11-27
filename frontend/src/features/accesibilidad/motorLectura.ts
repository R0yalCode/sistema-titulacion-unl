/**
 * Motor de lectura en voz alta (corrección de INC-23, AX-A).
 *
 * Causa de INC-23, verificada el 2026-11-26 con CDP sobre la aplicación real:
 * en Brave (navegador predeterminado del responsable) para Linux,
 * `speechSynthesis.getVoices()` devuelve 0 voces y cada `speak()` falla al
 * instante con `error: synthesis-failed`. La implementación anterior marcaba
 * «leyendo» nada más llamar a `speak()`, descartaba el código de error y
 * dejaba el aviso «Leyendo…» aunque no sonaba nada. Además elegía la primera
 * voz española aunque fuera de red, no esperaba a `voiceschanged` y los
 * eventos tardíos de una lectura cancelada podían alterar la siguiente.
 *
 * Este motor:
 *  - espera de forma acotada a que el navegador cargue sus voces;
 *  - prefiere voces españolas LOCALES y recurre a las de red si no hay otras;
 *  - informa «leyendo» solo cuando el motor confirma el inicio (`onstart`),
 *    con un tiempo máximo de espera;
 *  - lee los fragmentos de uno en uno, en orden, sin perder ni repetir;
 *  - aísla cada lectura en una sesión: los eventos de una lectura detenida
 *    o reemplazada se ignoran;
 *  - convierte los errores del navegador en causas comprensibles.
 *
 * No puede producir audio si el navegador no tiene voces: en ese caso lo
 * comunica (`sin-voces`) en lugar de simular que lee.
 */
import { lecturaDisponible } from './lectorPagina'

type Ventana = Window & typeof globalThis

export type EstadoLectura = 'inactiva' | 'preparando' | 'leyendo' | 'finalizada' | 'detenida' | 'error'

export type CausaErrorLectura =
  | 'no-soportada'
  | 'sin-contenido'
  | 'sin-voces'
  | 'no-permitida'
  | 'sin-inicio'
  | 'interrumpida'
  | 'fallo'

export type CambioLectura =
  | { estado: 'preparando' | 'leyendo' | 'finalizada' }
  | { estado: 'error'; causa: CausaErrorLectura; codigo?: string }

/** Tiempo máximo para que el navegador entregue sus voces (`voiceschanged`). */
export const ESPERA_VOCES_MS = 1500
/** Tiempo máximo entre `speak()` y el inicio real (las voces de red tardan ~0,6 s). */
export const ESPERA_INICIO_MS = 8000

/**
 * Voces del navegador. Si aún no están cargadas, espera `voiceschanged` como
 * máximo `esperaMs`. Nunca se queda bloqueada y siempre retira su oyente.
 */
export function esperarVoces(sintesis: SpeechSynthesis, esperaMs = ESPERA_VOCES_MS): Promise<SpeechSynthesisVoice[]> {
  const inmediatas = sintesis.getVoices()
  if (inmediatas.length > 0) {
    return Promise.resolve(inmediatas)
  }
  return new Promise((resolver) => {
    let resuelto = false
    const terminar = () => {
      if (resuelto) {
        return
      }
      resuelto = true
      clearTimeout(limite)
      sintesis.removeEventListener?.('voiceschanged', terminar)
      resolver(sintesis.getVoices())
    }
    const limite = setTimeout(terminar, esperaMs)
    sintesis.addEventListener?.('voiceschanged', terminar)
  })
}

function prioridadIdioma(lang: string): number {
  const codigo = lang.toLowerCase().replace('_', '-')
  if (codigo.startsWith('es-ec')) return 0
  if (codigo.startsWith('es-419')) return 1
  if (codigo.startsWith('es-us') || codigo.startsWith('es-mx') || codigo.startsWith('es-co') || codigo.startsWith('es-pe')) return 2
  if (codigo.startsWith('es-es')) return 3
  return 4
}

/**
 * Mejor voz española disponible: primero las locales (no dependen de la red),
 * después la variante regional más cercana a Ecuador y, en espeak-ng, la voz
 * base antes que sus variantes («Spanish+Adam»). `undefined` si no hay ninguna.
 */
export function elegirVozEspanol(voces: SpeechSynthesisVoice[]): SpeechSynthesisVoice | undefined {
  const puntuar = (voz: SpeechSynthesisVoice) =>
    (voz.localService ? 0 : 100) + prioridadIdioma(voz.lang) * 10 + (voz.name.includes('+') ? 1 : 0)
  return voces
    .filter((voz) => voz.lang.toLowerCase().startsWith('es'))
    .sort((a, b) => puntuar(a) - puntuar(b))[0]
}

function causaDeError(codigo: string, hayVoces: boolean): CausaErrorLectura {
  if (codigo === 'not-allowed') return 'no-permitida'
  if (codigo === 'interrupted' || codigo === 'canceled') return 'interrumpida'
  if (
    !hayVoces &&
    ['synthesis-failed', 'synthesis-unavailable', 'voice-unavailable', 'language-unavailable'].includes(codigo)
  ) {
    return 'sin-voces'
  }
  return 'fallo'
}

export type MotorLectura = {
  /**
   * Lee `enunciados` en orden. `velocidad` se consulta en cada fragmento, así
   * que un cambio del control durante la lectura se aplica al siguiente.
   * Cancela cualquier lectura anterior.
   */
  leer: (enunciados: string[], velocidad: () => number, alCambiar: (cambio: CambioLectura) => void) => Promise<void>
  /** Detiene de inmediato y descarta todos los eventos pendientes. */
  detener: () => void
}

export function crearMotorLectura(ventana: Ventana = window): MotorLectura {
  let sesion = 0
  // Referencias vivas a los fragmentos: en Chromium, un SpeechSynthesisUtterance
  // sin referencias puede recolectarse y perder sus eventos.
  let fragmentos: SpeechSynthesisUtterance[] = []
  let vigilante: ReturnType<typeof setTimeout> | undefined

  function limpiar() {
    clearTimeout(vigilante)
    vigilante = undefined
    fragmentos = []
  }

  function detener() {
    sesion += 1
    limpiar()
    if (lecturaDisponible(ventana)) {
      ventana.speechSynthesis.cancel()
    }
  }

  async function leer(enunciados: string[], velocidad: () => number, alCambiar: (cambio: CambioLectura) => void) {
    detener()
    const propia = sesion
    const vigente = () => propia === sesion
    if (!lecturaDisponible(ventana)) {
      alCambiar({ estado: 'error', causa: 'no-soportada' })
      return
    }
    if (enunciados.length === 0) {
      alCambiar({ estado: 'error', causa: 'sin-contenido' })
      return
    }
    const sintesis = ventana.speechSynthesis
    alCambiar({ estado: 'preparando' })

    // Con voces ya cargadas, speak() se llama en el mismo gesto del usuario
    // (algunos navegadores lo exigen); solo se espera si aún no hay voces.
    let voces = sintesis.getVoices()
    if (voces.length === 0) {
      voces = await esperarVoces(sintesis)
      if (!vigente()) {
        return
      }
    }
    const voz = elegirVozEspanol(voces)
    let iniciada = false

    const confirmarInicio = () => {
      if (!iniciada) {
        iniciada = true
        clearTimeout(vigilante)
        alCambiar({ estado: 'leyendo' })
      }
    }

    const fallar = (cambio: CambioLectura) => {
      detener()
      alCambiar(cambio)
    }

    vigilante = setTimeout(() => {
      if (vigente() && !iniciada) {
        fallar({ estado: 'error', causa: voces.length === 0 ? 'sin-voces' : 'sin-inicio' })
      }
    }, ESPERA_INICIO_MS)

    const hablar = (indice: number) => {
      if (!vigente()) {
        return
      }
      if (indice >= enunciados.length) {
        limpiar()
        alCambiar({ estado: 'finalizada' })
        return
      }
      const fragmento = new ventana.SpeechSynthesisUtterance(enunciados[indice])
      fragmento.lang = voz?.lang ?? 'es-ES'
      if (voz) {
        fragmento.voice = voz
      }
      fragmento.rate = velocidad()
      fragmento.onstart = () => {
        if (vigente()) {
          confirmarInicio()
        }
      }
      fragmento.onend = () => {
        if (!vigente()) {
          return
        }
        // Algún motor no emite onstart: un fin real también prueba que sonó.
        confirmarInicio()
        hablar(indice + 1)
      }
      fragmento.onerror = (evento: SpeechSynthesisErrorEvent) => {
        if (!vigente()) {
          return
        }
        const codigo = evento.error ?? 'desconocido'
        fallar({ estado: 'error', causa: causaDeError(codigo, voces.length > 0), codigo })
      }
      fragmentos.push(fragmento)
      sintesis.speak(fragmento)
    }

    hablar(0)
  }

  return { leer, detener }
}
