import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { axe } from 'vitest-axe'
import { AuthContext, type AuthContextValue } from '@/auth/AuthContext'
import { AsistenteFlotante } from './AsistenteFlotante'

const auth: AuthContextValue = {
  user: { cedula: '1100000000', roles: ['ESTUDIANTE'] },
  isAuthenticated: true,
  isLoading: false,
  login: vi.fn().mockReturnValue(true),
  logout: vi.fn(),
  signOut: vi.fn(),
  hasRole: () => true,
}

function renderAsistente() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <AuthContext.Provider value={auth}>
        <MemoryRouter initialEntries={['/estudiante']}>
          <main>
            <h1>Vista</h1>
          </main>
          <AsistenteFlotante />
        </MemoryRouter>
      </AuthContext.Provider>
    </QueryClientProvider>,
  )
}

function lanzador() {
  return screen.getByRole('button', { name: /asistente de ayuda/ })
}

function capaSalto() {
  return lanzador().querySelector('[data-animacion]') as HTMLElement
}

/** visualViewport simulado (jsdom no lo implementa). */
function simularViewport(alto: number) {
  const oyentes = new Set<() => void>()
  const viewport = {
    height: alto,
    offsetTop: 0,
    addEventListener: (_: string, fn: () => void) => oyentes.add(fn),
    removeEventListener: (_: string, fn: () => void) => oyentes.delete(fn),
  }
  vi.stubGlobal('visualViewport', viewport)
  return {
    cambiarAlto(nuevo: number) {
      viewport.height = nuevo
      act(() => oyentes.forEach((fn) => fn()))
    },
  }
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('AsistenteFlotante: presentación y responsive (mejora AX-D)', () => {
  it('la mascota original va en un recorte decorativo, dentro del botón y sin nombre propio', () => {
    renderAsistente()
    const imagen = lanzador().querySelector('img')
    expect(imagen).toHaveAttribute('src', '/assets/mascotas/mascota-404.png')
    expect(imagen).toHaveAttribute('alt', '')
    expect(imagen?.closest('[aria-hidden="true"]')).not.toBeNull()
    expect(lanzador()).toHaveAccessibleName('Abrir el asistente de ayuda')
  })

  it('el salto está activo con el panel cerrado, se detiene al abrir y se reanuda al cerrar', async () => {
    const user = userEvent.setup()
    renderAsistente()
    expect(capaSalto()).toHaveAttribute('data-animacion', 'activa')

    await user.click(lanzador())
    expect(capaSalto()).toHaveAttribute('data-animacion', 'pausada')

    await user.click(screen.getByRole('button', { name: 'Cerrar el asistente' }))
    expect(capaSalto()).toHaveAttribute('data-animacion', 'activa')
  })

  it('la animación no genera anuncios: no hay regiones vivas ni estados con el panel cerrado', () => {
    const { container } = renderAsistente()
    expect(container.querySelectorAll('[aria-live], [role="status"], [role="alert"]')).toHaveLength(0)
  })

  it('expone el estado abierto para el diseño responsive y devuelve el foco al cerrar con el botón', async () => {
    const user = userEvent.setup()
    const { container } = renderAsistente()
    const raiz = container.querySelector('aside') as HTMLElement
    expect(raiz).toHaveAttribute('data-abierta', 'false')

    await user.click(lanzador())
    expect(raiz).toHaveAttribute('data-abierta', 'true')
    await user.click(within(screen.getByRole('dialog')).getByRole('button', { name: 'Cerrar el asistente' }))
    expect(raiz).toHaveAttribute('data-abierta', 'false')
    expect(lanzador()).toHaveFocus()
  })

  it('con el panel abierto sigue el alto visible y el teclado virtual (visualViewport)', async () => {
    vi.stubGlobal('innerHeight', 800)
    const viewport = simularViewport(800)
    const user = userEvent.setup()
    const { container } = renderAsistente()
    const raiz = container.querySelector('aside') as HTMLElement
    expect(raiz.style.getPropertyValue('--asistente-alto-visible')).toBe('')

    await user.click(lanzador())
    expect(raiz.style.getPropertyValue('--asistente-alto-visible')).toBe('800px')
    expect(raiz.style.getPropertyValue('--asistente-teclado')).toBe('0px')

    // Aparece el teclado: el área visible baja a 450 px.
    viewport.cambiarAlto(450)
    expect(raiz.style.getPropertyValue('--asistente-alto-visible')).toBe('450px')
    expect(raiz.style.getPropertyValue('--asistente-teclado')).toBe('350px')
    expect(within(screen.getByRole('dialog')).getByRole('textbox', { name: 'Escribe tu pregunta' })).toBeInTheDocument()

    await user.keyboard('{Escape}')
    expect(raiz.style.getPropertyValue('--asistente-alto-visible')).toBe('')
  })

  it('no presenta violaciones de accesibilidad cerrado ni abierto', async () => {
    const user = userEvent.setup()
    const { container } = renderAsistente()
    expect(await axe(container)).toHaveNoViolations()
    await user.click(lanzador())
    expect(await axe(container)).toHaveNoViolations()
  })
})
