import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'
import { describe, expect, it } from 'vitest'
import { NotFoundState } from './NotFoundState'

describe('NotFoundState', () => {
  it('renderiza el mensaje por defecto', () => {
    render(<NotFoundState />)

    expect(screen.getByRole('heading', { name: 'No encontrado' })).toBeInTheDocument()
  })

  it('permite personalizar título y descripción', () => {
    render(<NotFoundState description="El expediente no existe." title="Expediente no encontrado" />)

    expect(screen.getByRole('heading', { name: 'Expediente no encontrado' })).toBeInTheDocument()
    expect(screen.getByText('El expediente no existe.')).toBeInTheDocument()
  })

  it('no presenta violaciones de accesibilidad', async () => {
    const { container } = render(<NotFoundState />)

    expect(await axe(container)).toHaveNoViolations()
  })
})
