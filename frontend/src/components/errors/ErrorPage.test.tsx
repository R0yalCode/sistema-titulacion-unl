import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'
import { describe, expect, it, vi } from 'vitest'
import { ErrorPage } from './ErrorPage'

describe('ErrorPage (página completa Liquid Glass)', () => {
  it('compone cabecera institucional, panel de vidrio, un único main y pie', () => {
    const { container } = render(<ErrorPage kind="not-found" primaryAction={{ href: '/' }} />)
    expect(screen.getByRole('link', { name: 'Universidad Nacional de Loja' })).toHaveAttribute('href', '/')
    expect(screen.getAllByRole('main')).toHaveLength(1)
    expect(screen.getByRole('heading', { level: 1, name: 'Página no encontrada' })).toBeInTheDocument()
    expect(container.querySelector('.glass-floating')).not.toBeNull()
    expect(screen.getByRole('contentinfo')).toHaveTextContent('Universidad Nacional de Loja')
  })

  it('el logotipo puede apuntar al inicio del rol', () => {
    render(<ErrorPage homeHref="/bandeja" kind="forbidden" />)
    expect(screen.getByRole('link', { name: 'Universidad Nacional de Loja' })).toHaveAttribute('href', '/bandeja')
  })

  it('no presenta violaciones de accesibilidad detectables por axe', async () => {
    const { container } = render(
      <ErrorPage kind="unavailable" primaryAction={{ onClick: vi.fn() }} secondaryAction={{ href: '/' }} />,
    )
    expect(await axe(container)).toHaveNoViolations()
  })
})
