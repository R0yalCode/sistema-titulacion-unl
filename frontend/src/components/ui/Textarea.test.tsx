import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'
import { describe, expect, it } from 'vitest'
import { Textarea } from './Textarea'

describe('Textarea', () => {
  it('asocia la etiqueta con el campo', () => {
    render(<Textarea label="Observaciones" />)

    expect(screen.getByLabelText('Observaciones')).toBeInTheDocument()
  })

  it('marca aria-invalid y asocia el error', () => {
    render(<Textarea error="Máximo 500 caracteres." label="Observaciones" />)

    const textarea = screen.getByLabelText('Observaciones')
    expect(textarea).toHaveAttribute('aria-invalid', 'true')
    expect(textarea).toHaveAccessibleDescription('Máximo 500 caracteres.')
  })

  it('no presenta violaciones de accesibilidad', async () => {
    const { container } = render(<Textarea hint="Opcional." label="Observaciones" />)

    expect(await axe(container)).toHaveNoViolations()
  })
})
