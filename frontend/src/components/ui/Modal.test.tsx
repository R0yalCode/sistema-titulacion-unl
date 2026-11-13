import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useState } from 'react'
import { axe } from 'vitest-axe'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { Modal } from './Modal'

function TriggerAndModal({ initialOpen = false }: { initialOpen?: boolean }) {
  const [open, setOpen] = useState(initialOpen)

  return (
    <div>
      <button onClick={() => setOpen(true)} type="button">
        Abrir
      </button>
      <Modal onClose={() => setOpen(false)} open={open} title="Confirmar envío">
        <p>¿Desea enviar el expediente?</p>
        <button type="button">Cancelar</button>
        <button type="button">Confirmar</button>
      </Modal>
    </div>
  )
}

describe('Modal', () => {
  afterEach(() => {
    document.body.style.overflow = ''
  })

  it('no renderiza nada cuando open es false', () => {
    render(
      <Modal onClose={() => undefined} open={false} title="Título">
        <p>Contenido</p>
      </Modal>,
    )

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('expone role="dialog", aria-modal y el título asociado', () => {
    render(
      <Modal onClose={() => undefined} open title="Confirmar envío">
        <p>Contenido</p>
      </Modal>,
    )

    const dialog = screen.getByRole('dialog', { name: 'Confirmar envío' })
    expect(dialog).toHaveAttribute('aria-modal', 'true')
  })

  it('mueve el foco al primer elemento enfocable al abrir', async () => {
    const user = userEvent.setup()
    render(<TriggerAndModal />)

    await user.click(screen.getByRole('button', { name: 'Abrir' }))

    expect(screen.getByRole('button', { name: 'Cerrar' })).toHaveFocus()
  })

  it('atrapa el foco: Tab desde el último elemento vuelve al primero', async () => {
    const user = userEvent.setup()
    render(<TriggerAndModal />)
    await user.click(screen.getByRole('button', { name: 'Abrir' }))

    const closeBtn = screen.getByRole('button', { name: 'Cerrar' })
    const cancelBtn = screen.getByRole('button', { name: 'Cancelar' })
    const confirmBtn = screen.getByRole('button', { name: 'Confirmar' })

    expect(closeBtn).toHaveFocus()
    await user.tab()
    expect(cancelBtn).toHaveFocus()
    await user.tab()
    expect(confirmBtn).toHaveFocus()
    await user.tab()
    expect(closeBtn).toHaveFocus()
  })

  it('atrapa el foco: Shift+Tab desde el primer elemento va al último', async () => {
    const user = userEvent.setup()
    render(<TriggerAndModal />)
    await user.click(screen.getByRole('button', { name: 'Abrir' }))

    expect(screen.getByRole('button', { name: 'Cerrar' })).toHaveFocus()
    await user.tab({ shift: true })

    expect(screen.getByRole('button', { name: 'Confirmar' })).toHaveFocus()
  })

  it('Escape cierra el modal', async () => {
    const user = userEvent.setup()
    const onClose = vi.fn()
    render(
      <Modal onClose={onClose} open title="Confirmar envío">
        <p>Contenido</p>
      </Modal>,
    )

    await user.keyboard('{Escape}')

    expect(onClose).toHaveBeenCalledOnce()
  })

  it('al cerrarse, devuelve el foco al elemento que abrió el modal', async () => {
    const user = userEvent.setup()
    render(<TriggerAndModal />)

    const trigger = screen.getByRole('button', { name: 'Abrir' })
    await user.click(trigger)
    expect(screen.getByRole('dialog')).toBeInTheDocument()

    await user.keyboard('{Escape}')

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(trigger).toHaveFocus()
  })

  it('bloquea el scroll del body mientras está abierto y lo restaura al cerrar', async () => {
    const user = userEvent.setup()
    render(<TriggerAndModal />)

    expect(document.body.style.overflow).not.toBe('hidden')

    await user.click(screen.getByRole('button', { name: 'Abrir' }))
    expect(document.body.style.overflow).toBe('hidden')

    await user.keyboard('{Escape}')
    expect(document.body.style.overflow).not.toBe('hidden')
  })

  it('no presenta violaciones de accesibilidad', async () => {
    const { baseElement } = render(
      <Modal onClose={() => undefined} open title="Confirmar envío">
        <p>Contenido</p>
      </Modal>,
    )

    expect(await axe(baseElement)).toHaveNoViolations()
  })
})

/**
 * Formulario cuyo estado vive en el **padre** y que pasa `onClose` como función
 * en línea: cada tecla re-renderiza el padre y crea un `onClose` nuevo. Es la
 * condición que provocó el defecto de V-08b (salto de foco en cada pulsación).
 */
function FormularioEnPadre({ onCerrado }: { onCerrado?: () => void }) {
  const [open, setOpen] = useState(false)
  const [nombre, setNombre] = useState('')
  const [nota, setNota] = useState('')

  return (
    <div>
      <button onClick={() => setOpen(true)} type="button">
        Abrir formulario
      </button>
      <Modal
        onClose={() => {
          setOpen(false)
          onCerrado?.()
        }}
        open={open}
        title="Formulario"
      >
        <label>
          Nombre
          <input value={nombre} onChange={(event) => setNombre(event.target.value)} />
        </label>
        <label>
          Nota
          <textarea value={nota} onChange={(event) => setNota(event.target.value)} />
        </label>
        <button type="button">Guardar</button>
      </Modal>
    </div>
  )
}

describe('Modal: estabilidad frente a re-renders del consumidor (FE transversal)', () => {
  afterEach(() => {
    document.body.style.overflow = ''
    vi.restoreAllMocks()
  })

  it('DEFECTO V-08b: con onClose cambiante, escribir en input y textarea no pierde el foco ni caracteres', async () => {
    const user = userEvent.setup()
    render(<FormularioEnPadre />)
    await user.click(screen.getByRole('button', { name: 'Abrir formulario' }))

    const nombre = screen.getByLabelText('Nombre')
    await user.click(nombre)
    await user.keyboard('Ana María')
    expect(nombre).toHaveValue('Ana María')
    expect(nombre).toHaveFocus()

    const nota = screen.getByLabelText('Nota')
    await user.click(nota)
    await user.keyboard('Texto largo de prueba')
    expect(nota).toHaveValue('Texto largo de prueba')
    expect(nota).toHaveFocus()
    expect(screen.getByRole('dialog')).toBeInTheDocument()
  })

  it('un cambio de estado del padre con el diálogo abierto no mueve el foco', async () => {
    const user = userEvent.setup()
    function ConContador() {
      const [open, setOpen] = useState(true)
      const [, setContador] = useState(0)
      return (
        <>
          <button onClick={() => setContador((valor) => valor + 1)} type="button">
            Externo
          </button>
          <Modal onClose={() => setOpen(false)} open={open} title="Contador">
            <input aria-label="Campo" />
            <button onClick={() => setContador((valor) => valor + 1)} type="button">
              Incrementar
            </button>
          </Modal>
        </>
      )
    }
    render(<ConContador />)

    const incrementar = screen.getByRole('button', { name: 'Incrementar' })
    incrementar.focus()
    await user.click(incrementar)
    await user.click(incrementar)

    expect(incrementar).toHaveFocus()
  })

  it('registra un único listener de teclado por apertura y Escape usa el onClose más reciente', async () => {
    const user = userEvent.setup()
    const add = vi.spyOn(document, 'addEventListener')
    const altasTeclado = () => add.mock.calls.filter(([tipo]) => tipo === 'keydown').length
    const primero = vi.fn()
    const { rerender } = render(
      <Modal onClose={primero} open title="Listener">
        <input aria-label="Campo" />
      </Modal>,
    )
    const altasTrasAbrir = altasTeclado()

    const ultimos = [vi.fn(), vi.fn(), vi.fn()]
    for (const onClose of ultimos) {
      rerender(
        <Modal onClose={onClose} open title="Listener">
          <input aria-label="Campo" />
        </Modal>,
      )
    }
    expect(altasTeclado()).toBe(altasTrasAbrir)

    await user.keyboard('{Escape}')

    expect(primero).not.toHaveBeenCalled()
    expect(ultimos[0]).not.toHaveBeenCalled()
    expect(ultimos[1]).not.toHaveBeenCalled()
    expect(ultimos[2]).toHaveBeenCalledOnce()
  })

  it('Escape invoca el onClose más reciente y devuelve el foco al botón que abrió el diálogo', async () => {
    const user = userEvent.setup()
    const onCerrado = vi.fn()
    render(<FormularioEnPadre onCerrado={onCerrado} />)
    const abrir = screen.getByRole('button', { name: 'Abrir formulario' })
    await user.click(abrir)
    await user.click(screen.getByLabelText('Nombre'))
    await user.keyboard('xyz')

    await user.keyboard('{Escape}')

    expect(onCerrado).toHaveBeenCalledOnce()
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(abrir).toHaveFocus()
    expect(document.body.style.overflow).not.toBe('hidden')
  })

  it('apertura, cierre y reapertura: foco inicial, bloqueo de scroll y retorno del foco consistentes', async () => {
    const user = userEvent.setup()
    render(<FormularioEnPadre />)
    const abrir = screen.getByRole('button', { name: 'Abrir formulario' })

    for (let vuelta = 0; vuelta < 3; vuelta += 1) {
      await user.click(abrir)
      expect(screen.getByRole('button', { name: 'Cerrar' })).toHaveFocus()
      expect(document.body.style.overflow).toBe('hidden')
      await user.click(screen.getByRole('button', { name: 'Cerrar' }))
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
      expect(abrir).toHaveFocus()
      expect(document.body.style.overflow).not.toBe('hidden')
    }
  })

  it('al desmontarse abierto retira el listener y restaura el scroll; Escape ya no cierra nada', async () => {
    const user = userEvent.setup()
    const onClose = vi.fn()
    const remove = vi.spyOn(document, 'removeEventListener')
    const { unmount } = render(
      <Modal onClose={onClose} open title="Desmontaje">
        <input aria-label="Campo" />
      </Modal>,
    )
    expect(document.body.style.overflow).toBe('hidden')

    unmount()
    await user.keyboard('{Escape}')

    expect(remove.mock.calls.some(([tipo]) => tipo === 'keydown')).toBe(true)
    expect(document.body.style.overflow).not.toBe('hidden')
    expect(onClose).not.toHaveBeenCalled()
  })

  it('si el elemento que abrió el diálogo ya no existe, cerrar no falla', async () => {
    const user = userEvent.setup()
    function OpenerQueDesaparece() {
      const [open, setOpen] = useState(false)
      return (
        <>
          {!open && (
            <button onClick={() => setOpen(true)} type="button">
              Abrir y desaparecer
            </button>
          )}
          <Modal onClose={() => setOpen(false)} open={open} title="Sin opener">
            <p>Contenido</p>
          </Modal>
        </>
      )
    }
    render(<OpenerQueDesaparece />)
    await user.click(screen.getByRole('button', { name: 'Abrir y desaparecer' }))

    await act(async () => {
      await user.keyboard('{Escape}')
    })

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('con el formulario escrito no presenta violaciones de accesibilidad', async () => {
    const user = userEvent.setup()
    const { baseElement } = render(<FormularioEnPadre />)
    await user.click(screen.getByRole('button', { name: 'Abrir formulario' }))
    await user.click(screen.getByLabelText('Nombre'))
    await user.keyboard('Ana')

    expect(await axe(baseElement)).toHaveNoViolations()
  })
})

