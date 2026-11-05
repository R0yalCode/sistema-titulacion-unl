import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { DemoBanner } from './DemoBanner'

describe('DemoBanner', () => {
  it('no renderiza nada cuando show es false', () => {
    render(<DemoBanner show={false} />)

    expect(screen.queryByRole('status')).not.toBeInTheDocument()
  })

  it('muestra el aviso de demostración cuando show es true', () => {
    render(<DemoBanner show={true} />)

    expect(screen.getByRole('status')).toHaveTextContent('Entorno de demostración')
  })
})
