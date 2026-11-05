import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'
import { describe, expect, it } from 'vitest'
import { Radio } from './Radio'

describe('Radio', () => {
  it('asocia la etiqueta y se puede seleccionar', async () => {
    const user = userEvent.setup()
    render(
      <>
        <Radio label="Opción A" name="grupo" value="A" />
        <Radio label="Opción B" name="grupo" value="B" />
      </>,
    )

    await user.click(screen.getByLabelText('Opción B'))

    expect(screen.getByLabelText('Opción B')).toBeChecked()
    expect(screen.getByLabelText('Opción A')).not.toBeChecked()
  })

  it('no presenta violaciones de accesibilidad', async () => {
    const { container } = render(
      <>
        <Radio label="Opción A" name="grupo" value="A" />
        <Radio label="Opción B" name="grupo" value="B" />
      </>,
    )

    expect(await axe(container)).toHaveNoViolations()
  })
})
