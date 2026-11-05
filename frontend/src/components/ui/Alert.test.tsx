import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'
import { describe, expect, it } from 'vitest'
import { Alert } from './Alert'

describe('Alert', () => {
  it('usa role="status" para variantes no críticas', () => {
    render(<Alert variant="info">Operación en curso.</Alert>)

    expect(screen.getByRole('status')).toHaveTextContent('Operación en curso.')
  })

  it('usa role="alert" para variantes críticas', () => {
    render(<Alert variant="danger">No se pudo completar la operación.</Alert>)

    expect(screen.getByRole('alert')).toHaveTextContent('No se pudo completar la operación.')
  })

  it('renderiza el título cuando se provee', () => {
    render(
      <Alert title="Error de validación" variant="danger">
        Revise los campos marcados.
      </Alert>,
    )

    expect(screen.getByText('Error de validación')).toBeInTheDocument()
  })

  it('no presenta violaciones de accesibilidad en ninguna variante', async () => {
    const { container } = render(
      <>
        <Alert variant="info">Info</Alert>
        <Alert variant="success">Éxito</Alert>
        <Alert variant="warning">Advertencia</Alert>
        <Alert variant="danger">Error</Alert>
      </>,
    )

    expect(await axe(container)).toHaveNoViolations()
  })
})
