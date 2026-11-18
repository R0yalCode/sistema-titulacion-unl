import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import App from './App'

describe('App', () => {
  it('renderiza sin errores y muestra la página pública en / (AUTH-E)', async () => {
    render(<App />)

    expect(await screen.findByRole('heading', { level: 1, name: 'Sistema de Gestión del Trámite de Titulación' })).toBeInTheDocument()
  })
})
