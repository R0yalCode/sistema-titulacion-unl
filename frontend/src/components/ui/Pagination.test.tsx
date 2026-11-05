import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'
import { describe, expect, it, vi } from 'vitest'
import { Pagination } from './Pagination'

describe('Pagination', () => {
  it('muestra la página actual y el total calculado con count/pageSize', () => {
    render(<Pagination count={45} page={2} pageSize={10} onPageChange={() => undefined} />)

    expect(screen.getByText('Página 2 de 5')).toBeInTheDocument()
  })

  it('deshabilita "Anterior" en la primera página', () => {
    render(<Pagination count={45} page={1} pageSize={10} onPageChange={() => undefined} />)

    expect(screen.getByRole('button', { name: 'Anterior' })).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Siguiente' })).toBeEnabled()
  })

  it('deshabilita "Siguiente" en la última página', () => {
    render(<Pagination count={45} page={5} pageSize={10} onPageChange={() => undefined} />)

    expect(screen.getByRole('button', { name: 'Siguiente' })).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Anterior' })).toBeEnabled()
  })

  it('llama a onPageChange con la página siguiente/anterior', async () => {
    const user = userEvent.setup()
    const onPageChange = vi.fn()
    render(<Pagination count={45} page={2} pageSize={10} onPageChange={onPageChange} />)

    await user.click(screen.getByRole('button', { name: 'Siguiente' }))
    expect(onPageChange).toHaveBeenCalledWith(3)

    await user.click(screen.getByRole('button', { name: 'Anterior' }))
    expect(onPageChange).toHaveBeenCalledWith(1)
  })

  it('anuncia el cambio de página de forma accesible', () => {
    render(<Pagination count={45} page={1} pageSize={10} onPageChange={() => undefined} />)

    expect(screen.getByText('Página 1 de 5')).toHaveAttribute('aria-live', 'polite')
  })

  it('no presenta violaciones de accesibilidad', async () => {
    const { container } = render(<Pagination count={45} page={2} pageSize={10} onPageChange={() => undefined} />)

    expect(await axe(container)).toHaveNoViolations()
  })

  it('es operable por teclado (Tab + Enter)', async () => {
    const user = userEvent.setup()
    const onPageChange = vi.fn()
    render(<Pagination count={45} page={2} pageSize={10} onPageChange={onPageChange} />)

    await user.tab()
    expect(screen.getByRole('button', { name: 'Anterior' })).toHaveFocus()

    await user.tab()
    expect(screen.getByRole('button', { name: 'Siguiente' })).toHaveFocus()

    await user.keyboard('{Enter}')
    expect(onPageChange).toHaveBeenCalledWith(3)
  })
})
