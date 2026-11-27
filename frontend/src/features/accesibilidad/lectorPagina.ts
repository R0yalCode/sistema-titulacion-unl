/**
 * Texto legible del contenido principal para la lectura en voz alta (AX-A):
 * extracción, fragmentación y detección de compatibilidad. Sin dependencias
 * ni servicios externos; la reproducción está en `motorLectura.ts`.
 */

/** Elementos cuyo contenido nunca se lee: ocultos, decorativos o técnicos. */
const SELECTOR_EXCLUIDO = [
  'script',
  'style',
  'noscript',
  'template',
  'svg',
  'canvas',
  '[hidden]',
  '[inert]',
  '[aria-hidden="true"]',
  '[data-a11y-omitir]',
].join(',')

/** Contenedores que agrupan el texto en frases independientes. */
const SELECTOR_BLOQUE = [
  'p',
  'h1',
  'h2',
  'h3',
  'h4',
  'h5',
  'h6',
  'li',
  'dt',
  'dd',
  'th',
  'td',
  'caption',
  'figcaption',
  'blockquote',
  'pre',
  'label',
  'legend',
  'summary',
  'button',
  'a',
  'div',
  'section',
  'article',
  'header',
  'footer',
  'nav',
  'aside',
  'main',
  'form',
  'fieldset',
].join(',')

/** `window` con los constructores globales (SpeechSynthesisUtterance) tipados. */
type Ventana = Window & typeof globalThis

/** Longitud máxima de cada enunciado: algunos navegadores cortan los largos. */
const LONGITUD_MAXIMA = 220

/** Raíz de lectura: el contenido principal de la vista, nunca el menú ni la barra. */
export function raizDeLectura(documento: Document = document): Element {
  return documento.getElementById('main-content') ?? documento.querySelector('main') ?? documento.body
}

function estaOculto(elemento: Element, cache: Map<Element, boolean>): boolean {
  const previo = cache.get(elemento)
  if (previo !== undefined) {
    return previo
  }
  let oculto = elemento.matches(SELECTOR_EXCLUIDO)
  if (!oculto) {
    const estilo = elemento.ownerDocument.defaultView?.getComputedStyle(elemento)
    oculto = estilo?.display === 'none' || estilo?.visibility === 'hidden'
  }
  if (!oculto && elemento.parentElement) {
    oculto = estaOculto(elemento.parentElement, cache)
  }
  cache.set(elemento, oculto)
  return oculto
}

function normalizar(texto: string): string {
  return texto.replace(/\s+/g, ' ').trim()
}

/**
 * Devuelve el texto visible y significativo de `raiz`, agrupado por bloques
 * en orden de lectura. Incluye el texto alternativo de las imágenes
 * informativas; omite los elementos ocultos, decorativos o marcados con
 * `data-a11y-omitir`.
 */
export function extraerTextoLegible(raiz: Element): string[] {
  const documento = raiz.ownerDocument
  const cache = new Map<Element, boolean>()
  const bloques: string[] = []
  let bloqueActual: Element | null = null
  let partes: string[] = []

  function cerrarBloque() {
    // Sin separador: los nodos de un mismo bloque ya traen sus espacios
    // ("está <strong>en verificación</strong>." no debe leerse "verificación .").
    const texto = normalizar(partes.join(''))
    if (texto) {
      bloques.push(texto)
    }
    partes = []
  }

  const recorrido = documento.createTreeWalker(raiz, NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT)
  for (let nodo = recorrido.nextNode(); nodo; nodo = recorrido.nextNode()) {
    let texto = ''
    let contenedor: Element | null = null
    if (nodo.nodeType === Node.TEXT_NODE) {
      contenedor = nodo.parentElement
      texto = nodo.textContent ?? ''
    } else if (nodo instanceof HTMLImageElement && nodo.alt.trim()) {
      contenedor = nodo
      // Con espacios: se une sin separador al texto vecino del mismo bloque.
      texto = ` Imagen: ${nodo.alt}. `
    }
    if (!contenedor || !normalizar(texto) || estaOculto(contenedor, cache)) {
      continue
    }
    const bloque = contenedor.closest(SELECTOR_BLOQUE) ?? raiz
    if (bloque !== bloqueActual) {
      cerrarBloque()
      bloqueActual = bloque
    }
    partes.push(texto)
  }
  cerrarBloque()
  return bloques
}

/** Divide los bloques en enunciados cortos, respetando el final de las frases. */
export function dividirEnEnunciados(bloques: string[], maximo = LONGITUD_MAXIMA): string[] {
  const enunciados: string[] = []
  for (const bloque of bloques) {
    let actual = ''
    for (const frase of bloque.split(/(?<=[.!?;:])\s+/)) {
      if (actual && actual.length + frase.length + 1 > maximo) {
        enunciados.push(actual)
        actual = ''
      }
      if (frase.length > maximo) {
        // Frase sin puntuación muy larga: se corta por palabras.
        let trozo = actual
        for (const palabra of frase.split(' ')) {
          if (trozo && trozo.length + palabra.length + 1 > maximo) {
            enunciados.push(trozo)
            trozo = ''
          }
          trozo = trozo ? `${trozo} ${palabra}` : palabra
        }
        actual = trozo
      } else {
        actual = actual ? `${actual} ${frase}` : frase
      }
    }
    if (actual) {
      enunciados.push(actual)
    }
  }
  return enunciados
}

export function lecturaDisponible(ventana: Ventana = window): boolean {
  return 'speechSynthesis' in ventana && typeof ventana.SpeechSynthesisUtterance === 'function'
}

// La reproducción (voces, sesiones, eventos y errores) vive en motorLectura.ts (INC-23).
