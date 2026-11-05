import { screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { renderWithProviders } from '@/test/renderWithProviders'
import { Sidebar, type SidebarItem } from './Sidebar'

const items: SidebarItem[] = [
  { to: '/estudiante', label: 'Mi expediente', roles: ['ESTUDIANTE'] },
  { to: '/bandeja', label: 'Bandeja', roles: ['DECANO'] },
]

describe('Sidebar', () => {
  it('muestra solo los enlaces permitidos para los roles del usuario', () => {
    renderWithProviders(<Sidebar items={items} open={false} roles={['ESTUDIANTE']} />)

    expect(screen.getByRole('link', { name: 'Mi expediente' })).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: 'Bandeja' })).not.toBeInTheDocument()
  })

  it('no muestra ningún enlace cuando no hay roles (sin sesión)', () => {
    renderWithProviders(<Sidebar items={items} open={false} roles={[]} />)

    expect(screen.queryByRole('link')).not.toBeInTheDocument()
  })
})
