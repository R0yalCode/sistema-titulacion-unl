import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'
import { describe, expect, it } from 'vitest'
import { Spinner } from './Spinner'

describe('Spinner', () => {
  it('expone un texto accesible por defecto', () => {
    render(<Spinner />)

    expect(screen.getByRole('status')).toHaveTextContent('Cargando…')
  })

  it('permite personalizar el texto accesible', () => {
    render(<Spinner label="Enviando solicitud…" />)

    expect(screen.getByRole('status')).toHaveTextContent('Enviando solicitud…')
  })

  it('no presenta violaciones de accesibilidad', async () => {
    const { container } = render(<Spinner />)

    expect(await axe(container)).toHaveNoViolations()
  })
})
