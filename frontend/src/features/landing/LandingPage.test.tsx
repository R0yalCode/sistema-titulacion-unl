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

describe('LandingPage', () => {
  it('muestra exactamente el contenido institucional definido', () => {
    renderLanding()

    const main = screen.getByRole('main')
    expect(within(main).getByText('SGT-SIAAF')).toBeInTheDocument()
    expect(
      within(main).getByRole('heading', {
        level: 1,
        name: 'Sistema de Gestión del Trámite de Titulación',
      }),
    ).toBeInTheDocument()
    expect(
      within(main).getByText(
        'Solicite su titulación, presente sus requisitos y dé seguimiento a su expediente',
      ),
    ).toBeInTheDocument()
    expect(main).toHaveTextContent(
      /^SGT-SIAAFSistema de Gestión del Trámite de TitulaciónSolicite su titulación, presente sus requisitos y dé seguimiento a su expedienteIngresar al sistema$/,
    )
  })

  it('conserva el logotipo institucional', () => {
    renderLanding()

    expect(
      within(screen.getByRole('banner')).getByRole('img', { name: 'Universidad Nacional de Loja' }),
    ).toBeInTheDocument()
  })

  it('el encabezado ofrece Inicio y Acceder al Sistema con rutas internas', () => {
    renderLanding()

    const nav = within(screen.getByRole('banner')).getByRole('navigation', {
      name: 'Navegación principal',
    })
    expect(within(nav).getAllByRole('link')).toHaveLength(2)
    expect(within(nav).getByRole('link', { name: 'Inicio' })).toHaveAttribute('href', '/')
    expect(within(nav).getByRole('link', { name: 'Acceder al Sistema' })).toHaveAttribute(
      'href',
      '/login',
    )
  })

  it('«Inicio» permanece en el landing y «Acceder al Sistema» abre /login', async () => {
    const user = userEvent.setup()
    renderLanding()

    await user.click(screen.getByRole('link', { name: 'Inicio' }))
    expect(
      screen.getByRole('heading', {
        level: 1,
        name: 'Sistema de Gestión del Trámite de Titulación',
      }),
    ).toBeInTheDocument()

    await user.click(screen.getByRole('link', { name: 'Acceder al Sistema' }))
    expect(screen.getByRole('heading', { name: 'Pantalla de ingreso' })).toBeInTheDocument()
  })

  it('ningún enlace apunta a un sistema externo', () => {
    renderLanding()

    for (const enlace of screen.getAllByRole('link')) {
      expect(enlace.getAttribute('href')).toMatch(/^\/(login)?$/)
    }
  })

  it('el panel central tiene un único enlace, «Ingresar al sistema», que lleva a /login', async () => {
    const user = userEvent.setup()
    renderLanding()

    const main = within(screen.getByRole('main'))
    expect(main.getAllByRole('link')).toHaveLength(1)
    const enlace = main.getByRole('link', { name: 'Ingresar al sistema' })
    expect(enlace).toHaveAttribute('href', '/login')
    await user.click(enlace)

    expect(screen.getByRole('heading', { name: 'Pantalla de ingreso' })).toBeInTheDocument()
  })

  it('recorre con el teclado Inicio, Acceder al Sistema e Ingresar al sistema', async () => {
    const user = userEvent.setup()
    renderLanding()

    await user.tab()
    expect(screen.getByRole('link', { name: 'Inicio' })).toHaveFocus()
    await user.tab()
    expect(screen.getByRole('link', { name: 'Acceder al Sistema' })).toHaveFocus()
    await user.tab()
    expect(screen.getByRole('link', { name: 'Ingresar al sistema' })).toHaveFocus()
    await user.keyboard('{Enter}')

    expect(screen.getByRole('heading', { name: 'Pantalla de ingreso' })).toBeInTheDocument()
  })

  it('no conserva ningún fragmento del apartado del proceso de titulación', () => {
    const { container } = renderLanding()

    for (const texto of [
      /¿Cómo es el proceso/i,
      /Recorrido general/i,
      /Fase \d/i,
      /Fases 2 y 3/i,
      /Declaratoria/i,
      /Requisitos documentales/i,
      /Envío del expediente/i,
      /Verificación de requisitos/i,
      /Informe de aptitud/i,
      /Trabajo de Integración Curricular/i,
      /Examen Complexivo/i,
    ]) {
      expect(container).not.toHaveTextContent(texto)
    }
    expect(container.querySelector('ol, li, h2, h3, h4')).toBeNull()
  })

  it('no presenta violaciones de accesibilidad', async () => {
    const { container } = renderLanding()

    expect(await axe(container)).toHaveNoViolations()
  })
})
