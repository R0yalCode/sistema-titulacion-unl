import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'
import { describe, expect, it } from 'vitest'
import { Input } from './Input'

describe('Input', () => {
  it('asocia la etiqueta con el campo', () => {
    render(<Input label="Nombre" />)

    expect(screen.getByLabelText('Nombre')).toBeInTheDocument()
  })

  it('marca aria-invalid y asocia el mensaje de error con aria-describedby', () => {
    render(<Input error="Este campo es obligatorio." label="Nombre" />)

    const input = screen.getByLabelText('Nombre')
    expect(input).toHaveAttribute('aria-invalid', 'true')
    expect(input).toHaveAccessibleDescription('Este campo es obligatorio.')
    expect(screen.getByRole('alert')).toHaveTextContent('Este campo es obligatorio.')
  })

  it('asocia el hint cuando no hay error', () => {
    render(<Input hint="Como aparece en su cédula." label="Nombre" />)

    expect(screen.getByLabelText('Nombre')).toHaveAccessibleDescription('Como aparece en su cédula.')
  })

  it('no presenta violaciones de accesibilidad', async () => {
    const { container } = render(
      <>
        <Input label="Nombre" />
        <Input error="Obligatorio." label="Correo" />
        <Input disabled label="Deshabilitado" />
      </>,
    )

    expect(await axe(container)).toHaveNoViolations()
  })
})
