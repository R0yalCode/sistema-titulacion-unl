import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'
import { describe, expect, it } from 'vitest'
import { Timeline, type TimelineStep } from './Timeline'

const steps: TimelineStep[] = [
  { id: '1', label: 'Enviada', status: 'completed', date: '01/11/2026' },
  { id: '2', label: 'En verificación', status: 'current', date: '03/11/2026' },
  { id: '3', label: 'Informe emitido', status: 'pending' },
]

describe('Timeline', () => {
  it('renderiza una lista ordenada con un elemento por paso', () => {
    render(<Timeline steps={steps} />)

    const list = screen.getByRole('list')
    expect(list.tagName).toBe('OL')
    expect(screen.getAllByRole('listitem')).toHaveLength(3)
  })

  it('marca el paso actual con aria-current="step"', () => {
    render(<Timeline steps={steps} />)

    const current = screen.getByText('En verificación').closest('li')
    expect(current).toHaveAttribute('aria-current', 'step')
  })

  it('no marca aria-current en los pasos que no son el actual', () => {
    render(<Timeline steps={steps} />)

    const completed = screen.getByText('Enviada').closest('li')
    expect(completed).not.toHaveAttribute('aria-current')
  })

  it('solo muestra los pasos recibidos, sin inventar otros', () => {
    render(<Timeline steps={steps} />)

    expect(screen.queryByText('Declarada apta')).not.toBeInTheDocument()
  })

  it('no presenta violaciones de accesibilidad', async () => {
    const { container } = render(<Timeline steps={steps} />)

    expect(await axe(container)).toHaveNoViolations()
  })
})
