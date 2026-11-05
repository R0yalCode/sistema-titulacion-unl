import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'
import { describe, expect, it, vi } from 'vitest'
import { Button } from './Button'

describe('Button', () => {
  it('renderiza y responde a clics', async () => {
    const user = userEvent.setup()
    const onClick = vi.fn()
    render(<Button onClick={onClick}>Guardar</Button>)

    await user.click(screen.getByRole('button', { name: 'Guardar' }))

    expect(onClick).toHaveBeenCalledOnce()
  })

  it('es accesible por teclado (Enter)', async () => {
    const user = userEvent.setup()
    const onClick = vi.fn()
    render(<Button onClick={onClick}>Guardar</Button>)

    await user.tab()
    await user.keyboard('{Enter}')

    expect(onClick).toHaveBeenCalledOnce()
  })

  it('se deshabilita mientras loading es true y no dispara onClick', async () => {
    const user = userEvent.setup()
    const onClick = vi.fn()
    render(
      <Button loading onClick={onClick}>
        Guardar
      </Button>,
    )

    const button = screen.getByRole('button', { name: 'Guardar' })
    expect(button).toBeDisabled()
    expect(button).toHaveAttribute('aria-busy', 'true')

    await user.click(button);
    expect(onClick).not.toHaveBeenCalled()
  })

  it('no presenta violaciones de accesibilidad en ninguna variante', async () => {
    const { container } = render(
      <>
        <Button variant="primary">Primario</Button>
        <Button variant="secondary">Secundario</Button>
        <Button variant="ghost">Fantasma</Button>
        <Button variant="danger">Peligro</Button>
      </>,
    )

    expect(await axe(container)).toHaveNoViolations()
  })
})
