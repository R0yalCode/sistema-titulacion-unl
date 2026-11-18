import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'
import { describe, expect, it } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import LandingPage from './LandingPage'

function renderLanding() {
  return render(
    <MemoryRouter initialEntries={['/']}>
      <Routes>
        <Route element={<LandingPage />} path="/" />
        <Route element={<h1>Pantalla de ingreso</h1>} path="/login" />
      </Routes>
    </MemoryRouter>,
  )
}

describe('LandingPage (AUTH-E)', () => {
  it('presenta el sistema y el botón de ingreso lleva a /login', async () => {
    const user = userEvent.setup()
    renderLanding()

    expect(screen.getByRole('heading', { level: 1, name: 'Sistema de Gestión de Titulación' })).toBeInTheDocument()
    await user.click(screen.getByRole('link', { name: 'Ingresar al sistema' }))

    expect(screen.getByRole('heading', { name: 'Pantalla de ingreso' })).toBeInTheDocument()
  })

  it('muestra el proceso de arriba hacia abajo con sus ramas', () => {
    renderLanding()

    expect(screen.getByRole('heading', { name: '¿Cómo es el proceso de titulación?' })).toBeInTheDocument()
    const etapas = screen.getAllByRole('heading', { level: 4 }).map((h) => h.textContent)
    expect(etapas.slice(0, 4)).toEqual([
      'Solicitud de titulación',
      'Requisitos documentales',
      'Envío del expediente',
      'Verificación de requisitos',
    ])
    expect(screen.getByText('Con observaciones')).toBeInTheDocument()
    expect(screen.getByText('Trabajo de Integración Curricular')).toBeInTheDocument()
    expect(screen.getByText('Examen Complexivo')).toBeInTheDocument()
  })

  it('distingue lo que gestiona el sistema de las etapas referenciales', () => {
    renderLanding()

    expect(screen.getByText('Disponible en SGT-SIAAF')).toBeInTheDocument()
    expect(screen.getByText('Referencial')).toBeInTheDocument()
    expect(screen.getByText(/pendientes de validación con la normativa institucional/)).toBeInTheDocument()
    // CA-G-01: sin modalidades no documentadas.
    expect(screen.queryByText(/Emprendimiento/i)).not.toBeInTheDocument()
  })

  it('tiene encabezado y pie institucionales', () => {
    renderLanding()

    const banner = screen.getByRole('banner')
    expect(within(banner).getByRole('img', { name: 'Universidad Nacional de Loja' })).toBeInTheDocument()
    expect(screen.getByRole('contentinfo')).toHaveTextContent('Universidad Nacional de Loja')
  })

  it('no presenta violaciones de accesibilidad', async () => {
    const { container } = renderLanding()

    expect(await axe(container)).toHaveNoViolations()
  })
})
