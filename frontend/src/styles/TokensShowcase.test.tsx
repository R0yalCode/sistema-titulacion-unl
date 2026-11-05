import { render } from '@testing-library/react'
import { axe } from 'vitest-axe'
import { describe, expect, it } from 'vitest'
import '@/styles/tokens.css'
import '@/styles/global.css'

function TokensShowcase() {
  return (
    <main style={{ backgroundColor: 'var(--color-bg-main)', padding: 'var(--space-6)' }}>
      <h1 style={{ color: 'var(--color-text-primary)' }}>Mis trámites</h1>
      <p style={{ color: 'var(--color-text-secondary)' }}>Resumen del estado de titulación.</p>
      <button
        type="button"
        style={{
          backgroundColor: 'var(--color-brand-red)',
          color: '#ffffff',
          border: 'none',
          borderRadius: 'var(--radius-md)',
          padding: 'var(--space-2) var(--space-4)',
        }}
      >
        Crear solicitud
      </button>
      <span
        role="status"
        style={{
          backgroundColor: 'var(--color-warning-bg)',
          color: 'var(--color-warning-text)',
          borderRadius: 'var(--radius-sm)',
          padding: 'var(--space-1) var(--space-2)',
        }}
      >
        Observada
      </span>
    </main>
  )
}

describe('Tokens de diseño (componente de prueba)', () => {
  it('no presenta violaciones de accesibilidad detectables por axe', async () => {
    const { container } = render(<TokensShowcase />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
