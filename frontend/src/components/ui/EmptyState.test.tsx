import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'
import { describe, expect, it } from 'vitest'
import { EmptyState } from './EmptyState'

describe('EmptyState', () => {
  it('renderiza título, descripción y acción', () => {
    render(
      <EmptyState
        action={<button type="button">Crear solicitud</button>}
        description="Aún no tiene solicitudes."
        title="Sin solicitudes"
      />,
    )

    expect(screen.getByRole('heading', { name: 'Sin solicitudes' })).toBeInTheDocument()
    expect(screen.getByText('Aún no tiene solicitudes.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Crear solicitud' })).toBeInTheDocument()
  })

  it('no presenta violaciones de accesibilidad', async () => {
    const { container } = render(<EmptyState title="Sin resultados" />)

    expect(await axe(container)).toHaveNoViolations()
  })
})
