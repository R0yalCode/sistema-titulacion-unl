import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'
import { describe, expect, it, vi } from 'vitest'
import { ErrorState } from './ErrorState'

describe('ErrorState', () => {
  it('usa role="alert" y no expone detalles internos', () => {
    render(<ErrorState />)

    const alert = screen.getByRole('alert')
    expect(alert).toHaveTextContent('Ocurrió un error')
    expect(alert.textContent).not.toMatch(/traceback|stack|SQL/i)
  })

  it('llama a onRetry al hacer clic en Reintentar', async () => {
    const user = userEvent.setup()
    const onRetry = vi.fn()
    render(<ErrorState onRetry={onRetry} />)

    await user.click(screen.getByRole('button', { name: 'Reintentar' }))

    expect(onRetry).toHaveBeenCalledOnce()
  })

  it('no muestra botón de reintentar si no se provee onRetry', () => {
    render(<ErrorState />)

    expect(screen.queryByRole('button')).not.toBeInTheDocument()
  })

  it('no presenta violaciones de accesibilidad', async () => {
    const { container } = render(<ErrorState onRetry={() => undefined} />)

    expect(await axe(container)).toHaveNoViolations()
  })
})
