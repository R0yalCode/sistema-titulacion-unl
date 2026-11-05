import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'
import { describe, expect, it } from 'vitest'
import { ForbiddenState } from './ForbiddenState'

describe('ForbiddenState', () => {
  it('renderiza el mensaje por defecto sin detalles internos', () => {
    render(<ForbiddenState />)

    const status = screen.getByRole('status')
    expect(status).toHaveTextContent('Acceso restringido')
    expect(status.textContent).not.toMatch(/rol|permiso denegado por|RBAC/i)
  })

  it('permite personalizar el mensaje', () => {
    render(<ForbiddenState description="Su rol no puede ver el checklist." title="Sin acceso al checklist" />)

    expect(screen.getByRole('heading', { name: 'Sin acceso al checklist' })).toBeInTheDocument()
  })

  it('renderiza la acción cuando se provee', () => {
    render(<ForbiddenState action={<button type="button">Volver al inicio</button>} />)

    expect(screen.getByRole('button', { name: 'Volver al inicio' })).toBeInTheDocument()
  })

  it('no presenta violaciones de accesibilidad', async () => {
    const { container } = render(<ForbiddenState />)

    expect(await axe(container)).toHaveNoViolations()
  })
})
