import { afterEach, describe, expect, it } from 'vitest'
import { dividirEnEnunciados, extraerTextoLegible, lecturaDisponible, raizDeLectura } from './lectorPagina'

afterEach(() => {
  document.body.innerHTML = ''
})

function montar(html: string): HTMLElement {
  document.body.innerHTML = html
  return document.body
}

describe('extraerTextoLegible', () => {
  it('lee el contenido visible por bloques, en orden', () => {
    const raiz = montar(`
      <main id="main-content">
        <h1>Mi proceso de titulación</h1>
        <p>Su expediente está <strong>en verificación</strong>.</p>
        <ul><li>Requisito uno</li><li>Requisito dos</li></ul>
      </main>`)
    expect(extraerTextoLegible(raiz)).toEqual([
      'Mi proceso de titulación',
      'Su expediente está en verificación.',
      'Requisito uno',
      'Requisito dos',
    ])
  })

  it('omite elementos ocultos, decorativos, técnicos y marcados', () => {
    const raiz = montar(`
      <main>
        <p>Visible</p>
        <p hidden>Oculto por atributo</p>
        <p style="display:none">Oculto por estilo</p>
        <p style="visibility:hidden">Invisible</p>
        <span aria-hidden="true">★ decorativo</span>
        <div inert><p>Inerte</p></div>
        <aside data-a11y-omitir><p>Panel de accesibilidad</p></aside>
        <script>var x = 1</script>
        <style>.a{}</style>
        <svg><text>icono</text></svg>
        <img alt="" src="decorativa.png" />
      </main>`)
    expect(extraerTextoLegible(raiz)).toEqual(['Visible'])
  })

  it('anuncia el texto alternativo de las imágenes informativas', () => {
    const raiz = montar('<main><img alt="Logo de la Universidad Nacional de Loja" src="logo.png" /></main>')
    expect(extraerTextoLegible(raiz)).toEqual(['Imagen: Logo de la Universidad Nacional de Loja.'])
    const mixto = montar('<main><p>Sello<img alt="Escudo" src="e.png" />institucional</p></main>')
    expect(extraerTextoLegible(mixto)).toEqual(['Sello Imagen: Escudo. institucional'])
  })

  it('usa #main-content como raíz y, si no existe, el primer <main> o el cuerpo', () => {
    montar('<nav>Menú</nav><main id="main-content"><p>Contenido</p></main>')
    expect(raizDeLectura().id).toBe('main-content')
    montar('<main class="publica"><p>Acceso</p></main>')
    expect(raizDeLectura().tagName).toBe('MAIN')
    montar('<p>Sin main</p>')
    expect(raizDeLectura()).toBe(document.body)
  })
})

describe('dividirEnEnunciados', () => {
  it('respeta el final de las frases y el límite de longitud', () => {
    const enunciados = dividirEnEnunciados(['Primera frase. Segunda frase algo más larga.'], 20)
    // La segunda frase supera el límite sola: se corta por palabras.
    expect(enunciados).toEqual(['Primera frase.', 'Segunda frase algo', 'más larga.'])
  })

  it('agrupa frases cortas en un mismo enunciado', () => {
    expect(dividirEnEnunciados(['Uno. Dos. Tres.'])).toEqual(['Uno. Dos. Tres.'])
  })
})

describe('lecturaDisponible', () => {
  it('detecta la ausencia de SpeechSynthesis (jsdom no la implementa)', () => {
    expect(lecturaDisponible(window)).toBe(false)
  })
})
// La reproducción se prueba en motorLectura.test.ts (INC-23).
