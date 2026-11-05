import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'
import { describe, expect, it } from 'vitest'
import { Select } from './Select'

const options = [
  { value: 'A', label: 'Opción A' },
  { value: 'B', label: 'Opción B' },
]

describe('Select', () => {
  it('asocia la etiqueta y permite elegir una opción', async () => {
    const user = userEvent.setup()
    render(<Select label="Opción" options={options} />)

    const select = screen.getByLabelText('Opción')
    await user.selectOptions(select, 'B')

    expect(select).toHaveValue('B')
  })

  it('muestra el placeholder como opción deshabilitada', () => {
    render(<Select label="Opción" options={options} placeholder="Seleccione…" />)

    expect(screen.getByRole('option', { name: 'Seleccione…' })).toBeDisabled()
  })

  it('marca aria-invalid y asocia el error', () => {
    render(<Select error="Seleccione una opción." label="Opción" options={options} />)

    expect(screen.getByLabelText('Opción')).toHaveAttribute('aria-invalid', 'true')
  })

  it('no presenta violaciones de accesibilidad', async () => {
    const { container } = render(<Select label="Opción" options={options} placeholder="Seleccione…" />)

    expect(await axe(container)).toHaveNoViolations()
  })
})
