import { render, screen } from '@testing-library/react'
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
