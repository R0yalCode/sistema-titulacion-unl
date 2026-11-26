import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Link, MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { axe } from 'vitest-axe'
import { AccesibilidadProvider } from './AccesibilidadContext'
import { PanelAccesibilidad } from './PanelAccesibilidad'
import { CLAVE_ALMACENAMIENTO } from './preferencias'

const ATRIBUTOS = ['data-a11y-texto', 'data-a11y-color', 'data-a11y-enlaces', 'data-a11y-fuente']

function limpiarRaiz() {
  const raiz = document.documentElement
  ATRIBUTOS.forEach((atributo) => raiz.removeAttribute(atributo))
  raiz.style.removeProperty('--a11y-escala-texto')
}

function Vista({ titulo, destino }: { titulo: string; destino: string }) {
  return (
    <main id="main-content">
      <h1>{titulo}</h1>
      <p>Contenido de la vista.</p>
      <Link to={destino}>Ir a la otra vista</Link>
    </main>
  )
}

function renderPanel() {
  return render(
    <AccesibilidadProvider>
      <MemoryRouter initialEntries={['/uno']}>
        <Routes>
          <Route element={<Vista destino="/dos" titulo="Vista uno" />} path="/uno" />
          <Route element={<Vista destino="/uno" titulo="Vista dos" />} path="/dos" />
        </Routes>
        <PanelAccesibilidad />
      </MemoryRouter>
    </AccesibilidadProvider>,
  )
}

async function abrirPanel() {
  const user = userEvent.setup()
  await user.click(screen.getByRole('button', { name: 'Herramientas de accesibilidad' }))
  return { user, panel: screen.getByRole('dialog', { name: 'Accesibilidad' }) }
}

/** SpeechSynthesis simulado: jsdom no lo implementa. */
function simularVoz() {
  const speechSynthesis = { cancel: vi.fn(), speak: vi.fn(), getVoices: () => [] }
  class Enunciado {
    text: string
    rate = 1
    lang = ''
    onend: (() => void) | null = null
    onerror: (() => void) | null = null
    constructor(text: string) {
      this.text = text
    }
  }
  vi.stubGlobal('speechSynthesis', speechSynthesis)
  vi.stubGlobal('SpeechSynthesisUtterance', Enunciado)
  return speechSynthesis
}

beforeEach(() => {
  localStorage.clear()
  limpiarRaiz()
})

afterEach(() => {
  vi.unstubAllGlobals()
  limpiarRaiz()
  localStorage.clear()
})

describe('PanelAccesibilidad (AX-A)', () => {
  it('ofrece un botón flotante con nombre accesible que abre el panel sin salir de la vista', async () => {
    renderPanel()
    const boton = screen.getByRole('button', { name: 'Herramientas de accesibilidad' })
    expect(boton).toHaveAttribute('aria-expanded', 'false')
    expect(screen.getByRole('complementary', { name: 'Herramientas de accesibilidad' })).toBeInTheDocument()

    const { panel } = await abrirPanel()
    expect(boton).toHaveAttribute('aria-expanded', 'true')
    expect(screen.getByRole('heading', { level: 1, name: 'Vista uno' })).toBeInTheDocument()
    expect(within(panel).getByRole('heading', { level: 2, name: 'Accesibilidad' })).toHaveFocus()
  })

  it('aumenta y disminuye el texto dentro de los límites y lo refleja en <html>', async () => {
    renderPanel()
    const { user, panel } = await abrirPanel()
    await user.click(within(panel).getByRole('button', { name: /Aumentar texto/ }))
    await user.click(within(panel).getByRole('button', { name: /Aumentar texto/ }))
    expect(within(panel).getByText('120 %')).toBeInTheDocument()
    expect(document.documentElement).toHaveAttribute('data-a11y-texto', 'escalado')
    expect(document.documentElement.style.getPropertyValue('--a11y-escala-texto')).toBe('1.2')

    for (let i = 0; i < 4; i++) {
      await user.click(within(panel).getByRole('button', { name: /Disminuir texto/ }))
    }
    expect(within(panel).getByText('90 %')).toBeInTheDocument()
    expect(within(panel).getByRole('button', { name: /Disminuir texto/ })).toBeDisabled()
  })

  it('mantiene un único modo de color activo a la vez', async () => {
    renderPanel()
    const { user, panel } = await abrirPanel()
    const grises = within(panel).getByRole('button', { name: 'Escala de grises' })
    const contraste = within(panel).getByRole('button', { name: 'Alto contraste' })

    await user.click(grises)
    expect(grises).toHaveAttribute('aria-pressed', 'true')
    expect(document.documentElement).toHaveAttribute('data-a11y-color', 'grises')

    await user.click(contraste)
    expect(contraste).toHaveAttribute('aria-pressed', 'true')
    expect(grises).toHaveAttribute('aria-pressed', 'false')
    expect(document.documentElement).toHaveAttribute('data-a11y-color', 'alto-contraste')

    await user.click(contraste)
    expect(document.documentElement).not.toHaveAttribute('data-a11y-color')
  })

  it('activa enlaces subrayados y fuente legible de forma independiente', async () => {
    renderPanel()
    const { user, panel } = await abrirPanel()
    await user.click(within(panel).getByRole('button', { name: 'Enlaces subrayados' }))
    await user.click(within(panel).getByRole('button', { name: 'Fuente legible' }))
    expect(document.documentElement).toHaveAttribute('data-a11y-enlaces', 'subrayados')
    expect(document.documentElement).toHaveAttribute('data-a11y-fuente', 'legible')
  })

  it('conserva las preferencias al navegar y al volver a cargar la aplicación', async () => {
    const { unmount } = renderPanel()
    const { user, panel } = await abrirPanel()
    await user.click(within(panel).getByRole('button', { name: 'Contraste negativo' }))
    await user.click(screen.getByRole('link', { name: 'Ir a la otra vista' }))
    expect(screen.getByRole('heading', { level: 1, name: 'Vista dos' })).toBeInTheDocument()
    expect(document.documentElement).toHaveAttribute('data-a11y-color', 'contraste-negativo')

    unmount()
    limpiarRaiz()
    renderPanel()
    expect(document.documentElement).toHaveAttribute('data-a11y-color', 'contraste-negativo')
    expect(JSON.parse(localStorage.getItem(CLAVE_ALMACENAMIENTO) ?? '{}').preferencias.modoColor).toBe('contraste-negativo')
  })

  it('restablece todas las opciones y borra lo guardado', async () => {
    renderPanel()
    const { user, panel } = await abrirPanel()
    const restablecer = within(panel).getByRole('button', { name: 'Restablecer cambios' })
    expect(restablecer).toBeDisabled()

    await user.click(within(panel).getByRole('button', { name: /Aumentar texto/ }))
    await user.click(within(panel).getByRole('button', { name: 'Fondo claro' }))
    await user.click(within(panel).getByRole('button', { name: 'Fuente legible' }))
    await user.click(restablecer)

    ATRIBUTOS.forEach((atributo) => expect(document.documentElement).not.toHaveAttribute(atributo))
    expect(localStorage.getItem(CLAVE_ALMACENAMIENTO)).toBeNull()
    expect(within(panel).getByText('100 %')).toBeInTheDocument()
    // <output> también tiene rol status: el aviso se localiza por su texto.
    expect(within(panel).getByText('Se restablecieron todas las opciones de accesibilidad.')).toHaveAttribute('role', 'status')
  })

  it('se cierra con Escape devolviendo el foco al botón, y al pulsar fuera', async () => {
    renderPanel()
    const { user } = await abrirPanel()
    await user.keyboard('{Escape}')
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Herramientas de accesibilidad' })).toHaveFocus()

    await abrirPanel()
    await user.click(screen.getByRole('heading', { level: 1, name: 'Vista uno' }))
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('explica que la lectura no está disponible si el navegador no ofrece síntesis de voz', async () => {
    renderPanel()
    const { panel } = await abrirPanel()
    expect(within(panel).getByText(/no permite la lectura en voz alta/)).toBeInTheDocument()
    expect(within(panel).queryByRole('button', { name: /Leer página/ })).not.toBeInTheDocument()
  })

  it('lee el contenido principal a 0,7x por defecto, permite detener y se detiene al navegar', async () => {
    const voz = simularVoz()
    renderPanel()
    const { user, panel } = await abrirPanel()
    expect(within(panel).getByRole('slider', { name: /Velocidad de lectura/ })).toHaveValue('0.7')

    await user.click(within(panel).getByRole('button', { name: /Leer página/ }))
    const leidos = voz.speak.mock.calls.map(([enunciado]) => enunciado as { text: string; rate: number })
    expect(leidos.map((enunciado) => enunciado.text)).toEqual(['Vista uno', 'Contenido de la vista.', 'Ir a la otra vista'])
    expect(leidos.every((enunciado) => enunciado.rate === 0.7)).toBe(true)
    // El propio panel (data-a11y-omitir) no se lee.
    expect(leidos.some((enunciado) => enunciado.text.includes('Accesibilidad'))).toBe(false)

    const detener = within(panel).getByRole('button', { name: /Detener lectura/ })
    expect(detener).toBeEnabled()
    voz.cancel.mockClear()
    await user.click(detener)
    expect(voz.cancel).toHaveBeenCalled()
    expect(within(panel).getByRole('button', { name: /Detener lectura/ })).toBeDisabled()

    await user.click(within(panel).getByRole('button', { name: /Leer página/ }))
    voz.cancel.mockClear()
    await user.click(screen.getByRole('link', { name: 'Ir a la otra vista' }))
    expect(voz.cancel).toHaveBeenCalled()
  })

  it('no presenta violaciones de accesibilidad con el panel abierto', async () => {
    simularVoz()
    const { container } = renderPanel()
    await abrirPanel()
    expect(await axe(container)).toHaveNoViolations()
  })
})
