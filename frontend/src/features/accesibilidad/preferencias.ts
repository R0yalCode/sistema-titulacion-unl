/**
 * Preferencias globales de accesibilidad (AX-A, DK-010).
 *
 * Fuente única: el proveedor (`AccesibilidadProvider`) las guarda en
 * `localStorage` y las aplica al elemento raíz (`<html>`) mediante atributos
 * `data-a11y-*` y la variable `--a11y-escala-texto`. Las reglas visuales están
 * en `styles/a11y.css`; ninguna página implementa estas herramientas por su
 * cuenta y ninguna preferencia altera datos ni lógica funcional.
 */

/**
 * Los modos de color son excluyentes: combinarlos (p. ej. contraste negativo
 * sobre alto contraste) produce resultados ilegibles, así que solo puede haber
 * uno activo a la vez.
 */
export type ModoColor = 'ninguno' | 'grises' | 'alto-contraste' | 'contraste-negativo' | 'fondo-claro'

export type PreferenciasAccesibilidad = {
  /** Factor sobre el tamaño de texto del navegador (1 = 100 %). */
  escalaTexto: number
  modoColor: ModoColor
  subrayarEnlaces: boolean
  fuenteLegible: boolean
  /** Velocidad de la lectura en voz alta (SpeechSynthesis `rate`). */
  velocidadLectura: number
}

export const CLAVE_ALMACENAMIENTO = 'sgt.a11y.preferencias'
const VERSION_ESQUEMA = 1

export const ESCALA_TEXTO = { min: 0.9, max: 1.6, paso: 0.1 } as const
export const VELOCIDAD_LECTURA = { min: 0.5, max: 1.5, paso: 0.1, inicial: 0.7 } as const

export const MODOS_COLOR: readonly ModoColor[] = [
  'ninguno',
  'grises',
  'alto-contraste',
  'contraste-negativo',
  'fondo-claro',
]

export const PREFERENCIAS_INICIALES: PreferenciasAccesibilidad = {
  escalaTexto: 1,
  modoColor: 'ninguno',
  subrayarEnlaces: false,
  fuenteLegible: false,
  velocidadLectura: VELOCIDAD_LECTURA.inicial,
}

/** Redondea a una décima para evitar derivas de coma flotante (1.1 + 0.1). */
function redondear(valor: number): number {
  return Math.round(valor * 10) / 10
}

export function limitar(valor: number, min: number, max: number): number {
  return redondear(Math.min(max, Math.max(min, valor)))
}

function numeroValido(valor: unknown, min: number, max: number, defecto: number): number {
  return typeof valor === 'number' && Number.isFinite(valor) ? limitar(valor, min, max) : defecto
}

/**
 * Valida un objeto de origen no confiable (almacenamiento local manipulado o
 * de una versión anterior): cada campo inválido vuelve a su valor inicial.
 */
export function normalizarPreferencias(datos: unknown): PreferenciasAccesibilidad {
  if (typeof datos !== 'object' || datos === null) {
    return { ...PREFERENCIAS_INICIALES }
  }
  const fuente = datos as Record<string, unknown>
  return {
    escalaTexto: numeroValido(fuente.escalaTexto, ESCALA_TEXTO.min, ESCALA_TEXTO.max, 1),
    modoColor: MODOS_COLOR.includes(fuente.modoColor as ModoColor)
      ? (fuente.modoColor as ModoColor)
      : 'ninguno',
    subrayarEnlaces: fuente.subrayarEnlaces === true,
    fuenteLegible: fuente.fuenteLegible === true,
    velocidadLectura: numeroValido(
      fuente.velocidadLectura,
      VELOCIDAD_LECTURA.min,
      VELOCIDAD_LECTURA.max,
      VELOCIDAD_LECTURA.inicial,
    ),
  }
}

export function leerPreferencias(): PreferenciasAccesibilidad {
  try {
    const crudo = localStorage.getItem(CLAVE_ALMACENAMIENTO)
    if (!crudo) {
      return { ...PREFERENCIAS_INICIALES }
    }
    const guardado = JSON.parse(crudo) as { version?: unknown; preferencias?: unknown }
    return guardado.version === VERSION_ESQUEMA
      ? normalizarPreferencias(guardado.preferencias)
      : { ...PREFERENCIAS_INICIALES }
  } catch {
    // JSON corrupto o almacenamiento bloqueado (modo privado, política del sitio).
    return { ...PREFERENCIAS_INICIALES }
  }
}

export function sonIniciales(preferencias: PreferenciasAccesibilidad): boolean {
  return (Object.keys(PREFERENCIAS_INICIALES) as (keyof PreferenciasAccesibilidad)[]).every(
    (clave) => preferencias[clave] === PREFERENCIAS_INICIALES[clave],
  )
}

export function guardarPreferencias(preferencias: PreferenciasAccesibilidad): void {
  try {
    if (sonIniciales(preferencias)) {
      localStorage.removeItem(CLAVE_ALMACENAMIENTO)
      return
    }
    localStorage.setItem(
      CLAVE_ALMACENAMIENTO,
      JSON.stringify({ version: VERSION_ESQUEMA, preferencias }),
    )
  } catch {
    // Sin almacenamiento: las preferencias duran mientras la página esté abierta.
  }
}

function alternarAtributo(raiz: HTMLElement, nombre: string, valor: string | null) {
  if (valor === null) {
    raiz.removeAttribute(nombre)
  } else {
    raiz.setAttribute(nombre, valor)
  }
}

/** Refleja las preferencias en el elemento raíz; `styles/a11y.css` hace el resto. */
export function aplicarPreferencias(
  preferencias: PreferenciasAccesibilidad,
  raiz: HTMLElement = document.documentElement,
): void {
  if (preferencias.escalaTexto === 1) {
    raiz.style.removeProperty('--a11y-escala-texto')
    raiz.removeAttribute('data-a11y-texto')
  } else {
    raiz.style.setProperty('--a11y-escala-texto', String(preferencias.escalaTexto))
    raiz.setAttribute('data-a11y-texto', 'escalado')
  }
  alternarAtributo(raiz, 'data-a11y-color', preferencias.modoColor === 'ninguno' ? null : preferencias.modoColor)
  alternarAtributo(raiz, 'data-a11y-enlaces', preferencias.subrayarEnlaces ? 'subrayados' : null)
  alternarAtributo(raiz, 'data-a11y-fuente', preferencias.fuenteLegible ? 'legible' : null)
}

/** Porcentaje legible para la interfaz y los lectores de pantalla ("110 %"). */
export function formatearPorcentaje(escala: number): string {
  return `${Math.round(escala * 100)} %`
}

/** Velocidad con coma decimal ("0,7x"). */
export function formatearVelocidad(velocidad: number): string {
  return `${velocidad.toFixed(1).replace('.', ',')}x`
}
