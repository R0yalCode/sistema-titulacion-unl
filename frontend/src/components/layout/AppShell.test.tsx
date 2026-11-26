import { act, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it } from 'vitest'
import { axe } from 'vitest-axe'
import { FolderIcon, HomeIcon } from '@/components/ui/icons'
import { renderWithProviders } from '@/test/renderWithProviders'
import { AppShell, type ShellNavItem } from './AppShell'

const CLAVE = 'sgt.sidebar.contraido'

const navItems: ShellNavItem[] = [
  { to: '/inicio', label: 'Inicio', icon: <HomeIcon />, end: true },
  { to: '/tramite', label: 'Mi trámite', icon: <FolderIcon /> },
]

function renderShell() {
  return renderWithProviders(
    <AppShell
      glass
      navItems={navItems}
      notificationsTo={null}
      portalLabel="Portal de prueba"
      profileTo={null}
      unreadCount={0}
      userName="Usuario de prueba"
      userRole="Rol"
    >
      <p>Contenido</p>
    </AppShell>,
    { route: '/inicio' },
  )
}

function sidebar() {
  return screen.getByRole('complementary', { name: 'Menú principal' })
}

describe('AppShell: control superior del sidebar (AX-B)', () => {
  afterEach(() => {
    localStorage.clear()
  })

  it('ubica el control junto al logo, antes de la navegación, y ya no en el pie', () => {
    renderShell()
    const boton = within(sidebar()).getByRole('button', { name: 'Contraer menú' })
    const logo = within(sidebar()).getByRole('img', { name: 'Universidad Nacional de Loja' })
    const navegacion = screen.getByRole('navigation', { name: 'Navegación principal' })

    expect(logo.parentElement).toContainElement(boton)
    expect(boton.compareDocumentPosition(navegacion) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    expect(screen.getAllByRole('button', { name: /(Contraer|Expandir) menú/ })).toHaveLength(1)
    expect(screen.queryByText('Contraer menú lateral')).not.toBeInTheDocument()
  })

  it('alterna entre expandido y contraído con nombre y estado accesibles', async () => {
    const user = userEvent.setup()
    renderShell()
    const boton = screen.getByRole('button', { name: 'Contraer menú' })
    expect(boton).toHaveAttribute('aria-expanded', 'true')
    expect(sidebar().className).not.toMatch(/collapsed/)

    await user.click(boton)
    expect(boton).toHaveAccessibleName('Expandir menú')
    expect(boton).toHaveAttribute('aria-expanded', 'false')
    expect(sidebar().className).toMatch(/collapsed/)

    await user.click(boton)
    expect(boton).toHaveAccessibleName('Contraer menú')
    expect(sidebar().className).not.toMatch(/collapsed/)
  })

  it('conserva el estado entre sesiones de la página', async () => {
    const user = userEvent.setup()
    const { unmount } = renderShell()
    await user.click(screen.getByRole('button', { name: 'Contraer menú' }))
    expect(localStorage.getItem(CLAVE)).toBe('1')
    unmount()

    renderShell()
    expect(screen.getByRole('button', { name: 'Expandir menú' })).toHaveAttribute('aria-expanded', 'false')
  })

  it('contraído, cada enlace mantiene su nombre accesible y un título visible al pasar el cursor', async () => {
    localStorage.setItem(CLAVE, '1')
    renderShell()
    const enlace = within(screen.getByRole('navigation', { name: 'Navegación principal' })).getByRole('link', {
      name: 'Mi trámite',
    })
    expect(enlace).toHaveAttribute('title', 'Mi trámite')
  })

  it('muestra el tooltip "Contraer menú" / "Expandir menú" al pasar el cursor o enfocar, y Escape lo descarta', async () => {
    const user = userEvent.setup()
    renderShell()
    const boton = screen.getByRole('button', { name: 'Contraer menú' })

    await user.hover(boton)
    expect(screen.getByRole('tooltip')).toHaveTextContent('Contraer menú')
    expect(boton).toHaveAttribute('aria-describedby', screen.getByRole('tooltip').id)
    // Portal sobre body: el recorte del sidebar no lo oculta.
    expect(sidebar()).not.toContainElement(screen.getByRole('tooltip'))

    await user.keyboard('{Escape}')
    expect(screen.queryByRole('tooltip')).not.toBeInTheDocument()

    await user.click(boton)
    expect(screen.queryByRole('tooltip')).not.toBeInTheDocument()
    await user.unhover(boton)
    // Foco de teclado: el tooltip refleja el nuevo estado y se va al perder el foco.
    act(() => boton.blur())
    act(() => boton.focus())
    expect(screen.getByRole('tooltip')).toHaveTextContent('Expandir menú')
    act(() => boton.blur())
    expect(screen.queryByRole('tooltip')).not.toBeInTheDocument()
  })

  it('no presenta violaciones de accesibilidad expandido ni contraído', async () => {
    const user = userEvent.setup()
    const { container } = renderShell()
    expect(await axe(container)).toHaveNoViolations()
    await user.click(screen.getByRole('button', { name: 'Contraer menú' }))
    expect(await axe(container)).toHaveNoViolations()
  })
})
