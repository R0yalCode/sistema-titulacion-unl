import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'
import { describe, expect, it } from 'vitest'
import { Card } from './Card'

describe('Card', () => {
  it('renderiza título, acciones y contenido', () => {
    render(
      <Card actions={<button type="button">Editar</button>} title="Expediente">
        Contenido del expediente
      </Card>,
    )

    expect(screen.getByRole('heading', { name: 'Expediente' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Editar' })).toBeInTheDocument()
    expect(screen.getByText('Contenido del expediente')).toBeInTheDocument()
  })

  it('renderiza sin título ni acciones', () => {
    render(<Card>Solo contenido</Card>)

    expect(screen.getByText('Solo contenido')).toBeInTheDocument()
    expect(screen.queryByRole('heading')).not.toBeInTheDocument()
  })

  it('no presenta violaciones de accesibilidad', async () => {
    const { container } = render(<Card title="Expediente">Contenido</Card>)

    expect(await axe(container)).toHaveNoViolations()
  })
})
