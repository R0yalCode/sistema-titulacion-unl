import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useState } from 'react'
import { describe, expect, it, vi } from 'vitest'
import { ErrorBoundary } from './ErrorBoundary'

let fallar = true

function Bomb() {
  if (fallar) {
    throw new Error('Fallo simulado de render con /ruta/interna y token=secreto')
  }
  return <p>Contenido recuperado</p>
}

describe('ErrorBoundary (vista 500 del sistema de errores)', () => {
  it('muestra la vista de recuperación sin detalles técnicos ni pantalla vacía', () => {
    fallar = true
    const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => undefined)

    render(
      <ErrorBoundary>
        <Bomb />
      </ErrorBoundary>,
    )

    expect(screen.getByRole('heading', { level: 1, name: 'Algo salió mal' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Intentar nuevamente' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Ir al inicio' })).toHaveAttribute('href', '/')
    expect(document.body.textContent).not.toMatch(/Fallo simulado|token=|stack/i)
    // Se registra con el logger existente (console.error).
    expect(errorSpy).toHaveBeenCalledWith('Error no controlado en la interfaz.', expect.any(Object))

    errorSpy.mockRestore()
  })

  it('«Intentar nuevamente» reinicia el límite y recupera la vista si el fallo cesó', async () => {
    fallar = true
    const user = userEvent.setup()
    const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => undefined)
    render(
      <ErrorBoundary>
        <Bomb />
      </ErrorBoundary>,
    )
    fallar = false
    await user.click(screen.getByRole('button', { name: 'Intentar nuevamente' }))
    expect(screen.getByText('Contenido recuperado')).toBeInTheDocument()
    errorSpy.mockRestore()
  })

  it('renderiza a los hijos normalmente cuando no hay error', () => {
    function Normal() {
      const [texto] = useState('Contenido normal')
      return <p>{texto}</p>
    }
    render(
      <ErrorBoundary>
        <Normal />
      </ErrorBoundary>,
    )
    expect(screen.getByText('Contenido normal')).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Algo salió mal' })).not.toBeInTheDocument()
  })
})
