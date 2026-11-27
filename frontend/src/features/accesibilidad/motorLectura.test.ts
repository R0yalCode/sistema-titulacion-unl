/**
 * Pruebas del motor de lectura (INC-23). La síntesis es SIMULADA, modelada
 * sobre el comportamiento observado en Chrome 156 y Brave 155 reales con CDP
 * (start/end asíncronos; cancel() emite «interrupted»/«canceled» después;
 * Brave sin voces responde «synthesis-failed» al instante). Comprueban la
 * lógica y los estados: NO demuestran que se oiga audio.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { ESPERA_INICIO_MS, ESPERA_VOCES_MS, crearMotorLectura, elegirVozEspanol, type CambioLectura } from './motorLectura'

type Voz = { name: string; lang: string; localService: boolean; default: boolean; voiceURI: string }
const voz = (name: string, lang: string, localService: boolean): Voz => ({ name, lang, localService, default: false, voiceURI: name })

const GOOGLE_ES = voz('Google español', 'es-ES', false)
const GOOGLE_US = voz('Google español de Estados Unidos', 'es-US', false)
const ESPEAK_419 = voz('Spanish (Latin America) espeak-ng', 'es-419', true)
const ESPEAK_419_VARIANTE = voz('Spanish (Latin America)+Adam espeak-ng', 'es-419', true)
const ESPEAK_ES = voz('Spanish (Spain) espeak-ng', 'es', true)
const INGLES = voz('English espeak-ng', 'en-US', true)

type Modo = 'ok' | 'silencio' | { error: string }

class Fragmento {
  text: string
  rate = 1
  lang = ''
  voice: Voz | null = null
  onstart: (() => void) | null = null
  onend: (() => void) | null = null
  onerror: ((evento: { error: string }) => void) | null = null
  constructor(text: string) {
    this.text = text
  }
}

function crearSintesis({ voces = [GOOGLE_ES] as Voz[], modo = 'ok' as Modo, duracion = 100 } = {}) {
  let lista = voces
  const oyentes = new Set<() => void>()
  let cola: Fragmento[] = []
  let actual: Fragmento | null = null
  const hablados: Fragmento[] = []

  function siguiente() {
    actual = cola.shift() ?? null
    const fragmento = actual
    if (!fragmento) return
    setTimeout(() => {
      if (actual !== fragmento) return
      if (modo === 'silencio') return
      if (typeof modo === 'object') {
        actual = null
        fragmento.onerror?.({ error: modo.error })
        if (!actual) siguiente()
        return
      }
      fragmento.onstart?.()
      setTimeout(() => {
        if (actual !== fragmento) return
        actual = null
        fragmento.onend?.()
        // Si el manejador ya encoló y arrancó otro fragmento, no se pisa.
        if (!actual) siguiente()
      }, duracion)
    }, 0)
  }

  const sintesis = {
    getVoices: () => lista,
    addEventListener: (_: string, fn: () => void) => oyentes.add(fn),
    removeEventListener: (_: string, fn: () => void) => oyentes.delete(fn),
    speak: vi.fn((fragmento: Fragmento) => {
      hablados.push(fragmento)
      cola.push(fragmento)
      if (!actual) siguiente()
    }),
    cancel: vi.fn(() => {
      const interrumpido = actual
      const cancelados = cola
      actual = null
      cola = []
      // Como en Chrome: los errores de la cancelación llegan después.
      setTimeout(() => {
        interrumpido?.onerror?.({ error: 'interrupted' })
        cancelados.forEach((fragmento) => fragmento.onerror?.({ error: 'canceled' }))
      }, 0)
    }),
    get speaking() {
      return actual !== null
    },
  }
  return {
    ventana: { speechSynthesis: sintesis, SpeechSynthesisUtterance: Fragmento } as unknown as Window & typeof globalThis,
    sintesis,
    hablados,
    cargarVoces(nuevas: Voz[]) {
      lista = nuevas
      oyentes.forEach((fn) => fn())
    },
    oyentes,
  }
}

function registrar() {
  const cambios: CambioLectura[] = []
  return { cambios, alCambiar: (cambio: CambioLectura) => cambios.push(cambio), estados: () => cambios.map((c) => c.estado) }
}

beforeEach(() => {
  vi.useFakeTimers()
})

afterEach(() => {
  vi.useRealTimers()
})

describe('elegirVozEspanol', () => {
  it('prefiere voces locales y, entre ellas, la variante más cercana a Ecuador y la voz base', () => {
    expect(elegirVozEspanol([GOOGLE_ES, ESPEAK_ES, ESPEAK_419_VARIANTE, ESPEAK_419, INGLES] as never)?.name).toBe(
      ESPEAK_419.name,
    )
    expect(elegirVozEspanol([GOOGLE_ES, GOOGLE_US] as never)?.name).toBe(GOOGLE_US.name)
    expect(elegirVozEspanol([INGLES] as never)).toBeUndefined()
    expect(elegirVozEspanol([])).toBeUndefined()
  })
})

describe('crearMotorLectura (INC-23)', () => {
  it('solo informa «leyendo» tras el inicio real y lee todos los fragmentos en orden, una vez', async () => {
    const { ventana, hablados } = crearSintesis()
    const motor = crearMotorLectura(ventana)
    const r = registrar()

    await motor.leer(['Uno.', 'Dos.', 'Tres.'], () => 0.7, r.alCambiar)
    expect(r.estados()).toEqual(['preparando'])
    expect(hablados).toHaveLength(1)

    await vi.advanceTimersByTimeAsync(0)
    expect(r.estados()).toEqual(['preparando', 'leyendo'])

    await vi.advanceTimersByTimeAsync(1000)
    expect(hablados.map((f) => f.text)).toEqual(['Uno.', 'Dos.', 'Tres.'])
    expect(r.estados()).toEqual(['preparando', 'leyendo', 'finalizada'])
  })

  it('usa la voz española elegida, su idioma y la velocidad, consultada en cada fragmento', async () => {
    const { ventana, hablados } = crearSintesis({ voces: [GOOGLE_ES, ESPEAK_419] })
    const motor = crearMotorLectura(ventana)
    let velocidad = 0.7
    await motor.leer(['Uno.', 'Dos.'], () => velocidad, registrar().alCambiar)
    velocidad = 1.3
    await vi.advanceTimersByTimeAsync(1000)
    expect(hablados.map((f) => [f.voice?.name, f.lang, f.rate])).toEqual([
      [ESPEAK_419.name, 'es-419', 0.7],
      [ESPEAK_419.name, 'es-419', 1.3],
    ])
  })

  it('navegador sin voces (Brave en Linux): informa «sin-voces» con el código real y nunca «leyendo»', async () => {
    const { ventana } = crearSintesis({ voces: [], modo: { error: 'synthesis-failed' } })
    const motor = crearMotorLectura(ventana)
    const r = registrar()
    const lectura = motor.leer(['Uno.', 'Dos.'], () => 1, r.alCambiar)
    await vi.advanceTimersByTimeAsync(ESPERA_VOCES_MS)
    await lectura
    await vi.advanceTimersByTimeAsync(10)
    expect(r.cambios).toEqual([
      { estado: 'preparando' },
      { estado: 'error', causa: 'sin-voces', codigo: 'synthesis-failed' },
    ])
  })

  it('espera la carga asíncrona de voces (voiceschanged) y retira su oyente', async () => {
    const entorno = crearSintesis({ voces: [] })
    const motor = crearMotorLectura(entorno.ventana)
    const r = registrar()
    const lectura = motor.leer(['Uno.'], () => 1, r.alCambiar)
    expect(entorno.sintesis.speak).not.toHaveBeenCalled()
    expect(entorno.oyentes.size).toBe(1)

    entorno.cargarVoces([GOOGLE_ES, ESPEAK_ES])
    await lectura
    expect(entorno.oyentes.size).toBe(0)
    expect(entorno.hablados[0]?.voice?.name).toBe(ESPEAK_ES.name)
    await vi.advanceTimersByTimeAsync(500)
    expect(r.estados()).toEqual(['preparando', 'leyendo', 'finalizada'])
  })

  it('si las voces no llegan, no se bloquea: intenta con el idioma tras la espera máxima', async () => {
    const { ventana, hablados } = crearSintesis({ voces: [] })
    const motor = crearMotorLectura(ventana)
    const lectura = motor.leer(['Uno.'], () => 1, registrar().alCambiar)
    await vi.advanceTimersByTimeAsync(ESPERA_VOCES_MS)
    await lectura
    expect(hablados[0]?.lang).toBe('es-ES')
    expect(hablados[0]?.voice).toBeNull()
  })

  it('bloqueo del navegador (not-allowed) se informa como tal', async () => {
    const { ventana } = crearSintesis({ modo: { error: 'not-allowed' } })
    const motor = crearMotorLectura(ventana)
    const r = registrar()
    await motor.leer(['Uno.'], () => 1, r.alCambiar)
    await vi.advanceTimersByTimeAsync(10)
    expect(r.cambios.at(-1)).toEqual({ estado: 'error', causa: 'no-permitida', codigo: 'not-allowed' })
  })

  it('si el motor nunca empieza, falla de forma explícita tras la espera máxima y cancela', async () => {
    const { ventana, sintesis } = crearSintesis({ modo: 'silencio' })
    const motor = crearMotorLectura(ventana)
    const r = registrar()
    await motor.leer(['Uno.'], () => 1, r.alCambiar)
    await vi.advanceTimersByTimeAsync(ESPERA_INICIO_MS - 1)
    expect(r.estados()).toEqual(['preparando'])
    sintesis.cancel.mockClear()
    await vi.advanceTimersByTimeAsync(1)
    expect(r.cambios.at(-1)).toEqual({ estado: 'error', causa: 'sin-inicio' })
    expect(sintesis.cancel).toHaveBeenCalled()
  })

  it('detener corta de inmediato y los errores tardíos de la cancelación se ignoran', async () => {
    const { ventana, sintesis, hablados } = crearSintesis()
    const motor = crearMotorLectura(ventana)
    const r = registrar()
    await motor.leer(['Uno.', 'Dos.', 'Tres.'], () => 1, r.alCambiar)
    await vi.advanceTimersByTimeAsync(50)
    sintesis.cancel.mockClear()
    motor.detener()
    expect(sintesis.cancel).toHaveBeenCalledTimes(1)
    await vi.advanceTimersByTimeAsync(1000)
    expect(hablados).toHaveLength(1)
    expect(r.estados()).toEqual(['preparando', 'leyendo'])
  })

  it('una nueva lectura reemplaza a la anterior: sin duplicados ni eventos cruzados', async () => {
    const { ventana, hablados } = crearSintesis()
    const motor = crearMotorLectura(ventana)
    const primera = registrar()
    const segunda = registrar()
    await motor.leer(['A1.', 'A2.'], () => 1, primera.alCambiar)
    await vi.advanceTimersByTimeAsync(50)
    await motor.leer(['B1.', 'B2.'], () => 1, segunda.alCambiar)
    await vi.advanceTimersByTimeAsync(1000)

    expect(hablados.map((f) => f.text)).toEqual(['A1.', 'B1.', 'B2.'])
    expect(primera.estados()).toEqual(['preparando', 'leyendo'])
    expect(segunda.estados()).toEqual(['preparando', 'leyendo', 'finalizada'])
  })

  it('tras detener, otra lectura funciona con normalidad (recuperación)', async () => {
    const { ventana } = crearSintesis()
    const motor = crearMotorLectura(ventana)
    await motor.leer(['Uno.'], () => 1, registrar().alCambiar)
    await vi.advanceTimersByTimeAsync(20)
    motor.detener()
    const r = registrar()
    await motor.leer(['Otra.'], () => 1, r.alCambiar)
    await vi.advanceTimersByTimeAsync(1000)
    expect(r.estados()).toEqual(['preparando', 'leyendo', 'finalizada'])
  })

  it('un fin sin inicio (motores que no emiten onstart) también cuenta como lectura real', async () => {
    const entorno = crearSintesis()
    entorno.sintesis.speak.mockImplementation((f: Fragmento) => {
      entorno.hablados.push(f)
      setTimeout(() => f.onend?.(), 5)
    })
    const motor = crearMotorLectura(entorno.ventana)
    const r = registrar()
    await motor.leer(['Uno.'], () => 1, r.alCambiar)
    await vi.advanceTimersByTimeAsync(10)
    expect(r.estados()).toEqual(['preparando', 'leyendo', 'finalizada'])
  })

  it('sin contenido o sin API informa la causa sin llamar a speak', async () => {
    const { ventana, sintesis } = crearSintesis()
    const r = registrar()
    await crearMotorLectura(ventana).leer([], () => 1, r.alCambiar)
    expect(r.cambios).toEqual([{ estado: 'error', causa: 'sin-contenido' }])
    expect(sintesis.speak).not.toHaveBeenCalled()

    const r2 = registrar()
    await crearMotorLectura(window).leer(['Uno.'], () => 1, r2.alCambiar)
    expect(r2.cambios).toEqual([{ estado: 'error', causa: 'no-soportada' }])
  })
})
