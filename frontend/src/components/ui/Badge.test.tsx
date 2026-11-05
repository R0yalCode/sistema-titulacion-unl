import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'
import { describe, expect, it } from 'vitest'
import { Badge } from './Badge'

describe('Badge', () => {
  it('renderiza el texto', () => {
    render(<Badge variant="success">Verificado</Badge>)

    expect(screen.getByText('Verificado')).toBeInTheDocument()
  })

  it('no presenta violaciones de accesibilidad en ninguna variante', async () => {
    const { container } = render(
      <>
        <Badge variant="neutral">Pendiente</Badge>
        <Badge variant="info">Solicitado</Badge>
        <Badge variant="warning">Observada</Badge>
        <Badge variant="success">Verificado</Badge>
        <Badge variant="danger">Cancelada</Badge>
      </>,
    )

    expect(await axe(container)).toHaveNoViolations()
  })
})
