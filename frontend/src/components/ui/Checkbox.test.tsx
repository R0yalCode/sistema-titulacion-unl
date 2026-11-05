import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'
import { describe, expect, it } from 'vitest'
import { Checkbox } from './Checkbox'

describe('Checkbox', () => {
  it('asocia la etiqueta y se puede marcar por teclado', async () => {
    const user = userEvent.setup()
    render(<Checkbox label="Acepto los términos" />)

    const checkbox = screen.getByLabelText('Acepto los términos')
    await user.tab()
    await user.keyboard(' ')

    expect(checkbox).toBeChecked()
  })

  it('no presenta violaciones de accesibilidad', async () => {
    const { container } = render(<Checkbox label="Acepto los términos" />)

    expect(await axe(container)).toHaveNoViolations()
  })
})
