import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import { axe } from 'vitest-axe'
import { MenuPerfil, RUTA_CAMBIAR_CONTRASENA } from './MenuPerfil'

function renderMenu({ perfilTo = '/estudiante/perfil' as string | null, onCerrarSesion = vi.fn() } = {}) {
  render(
    <MemoryRouter initialEntries={['/estudiante']}>
      <header>
        <MenuPerfil detalle="Estudiante" nombre="Ana Ruiz" perfilTo={perfilTo} onCerrarSesion={onCerrarSesion} />
      </header>
      <main>
        <Routes>
          <Route element={<h1>Inicio</h1>} path="/estudiante" />
          <Route element={<h1>Perfil</h1>} path="/estudiante/perfil" />
          <Route element={<h1>Recuperar contraseña</h1>} path={RUTA_CAMBIAR_CONTRASENA} />
        </Routes>
      </main>
    </MemoryRouter>,
  )
  return { onCerrarSesion, boton: screen.getByRole('button', { name: 'Menú de usuario: Ana Ruiz, Estudiante' }) }
}

describe('MenuPerfil (AX-C)', () => {
  it('es un botón de menú anclado, no un diálogo centrado', async () => {
    const user = userEvent.setup()
    const { boton } = renderMenu()
    expect(boton).toHaveAttribute('aria-haspopup', 'menu')
    expect(boton).toHaveAttribute('aria-expanded', 'false')
    expect(within(boton).getByText('AR')).toBeInTheDocument()

    await user.click(boton)
    expect(boton).toHaveAttribute('aria-expanded', 'true')
    const menu = screen.getByRole('menu')
    expect(boton).toHaveAttribute('aria-controls', menu.id)
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument()
  })

  it('muestra solo datos reales y las opciones aprobadas', async () => {
    const user = userEvent.setup()
    const { boton } = renderMenu()
    await user.click(boton)

    expect(screen.getAllByText('Ana Ruiz').length).toBeGreaterThan(0)
    const opciones = screen.getAllByRole('menuitem')
    expect(opciones.map((opcion) => opcion.textContent)).toEqual(['Mi perfil', 'Cambiar contraseña', 'Cerrar sesión'])
    expect(screen.getByRole('menuitem', { name: 'Mi perfil' })).toHaveAttribute('href', '/estudiante/perfil')
    // Sin cambio de contraseña con sesión en la API: se usa la recuperación existente.
    expect(screen.getByRole('menuitem', { name: 'Cambiar contraseña' })).toHaveAttribute('href', '/recuperar-contrasena')
    // Sin datos en la API para estos campos: no se muestran.
    expect(screen.queryByText(/último (acceso|inicio)/i)).not.toBeInTheDocument()
    expect(screen.queryByText(/cuenta (activa|verificada)/i)).not.toBeInTheDocument()
  })

  it('omite "Mi perfil" cuando el rol no tiene página de perfil', async () => {
    const user = userEvent.setup()
    const { boton } = renderMenu({ perfilTo: null })
    await user.click(boton)
    expect(screen.queryByRole('menuitem', { name: 'Mi perfil' })).not.toBeInTheDocument()
    expect(screen.getAllByRole('menuitem')).toHaveLength(2)
  })

  it('se recorre con flechas, Inicio y Fin, y la flecha arriba abre en el último elemento', async () => {
    const user = userEvent.setup()
    const { boton } = renderMenu()
    await user.click(boton)
    const [perfil, contrasena, salir] = screen.getAllByRole('menuitem')
    expect(perfil).toHaveFocus()

    await user.keyboard('{ArrowDown}')
    expect(contrasena).toHaveFocus()
    await user.keyboard('{End}')
    expect(salir).toHaveFocus()
    await user.keyboard('{ArrowDown}')
    expect(perfil).toHaveFocus()
    await user.keyboard('{ArrowUp}')
    expect(salir).toHaveFocus()
    await user.keyboard('{Home}')
    expect(perfil).toHaveFocus()

    await user.keyboard('{Escape}')
    expect(boton).toHaveFocus()
    await user.keyboard('{ArrowUp}')
    expect(screen.getByRole('menuitem', { name: 'Cerrar sesión' })).toHaveFocus()
  })

  it('se cierra con Escape devolviendo el foco, con Tab y al pulsar fuera', async () => {
    const user = userEvent.setup()
    const { boton } = renderMenu()

    await user.click(boton)
    await user.keyboard('{Escape}')
    expect(screen.queryByRole('menu')).not.toBeInTheDocument()
    expect(boton).toHaveFocus()

    await user.click(boton)
    await user.tab()
    expect(screen.queryByRole('menu')).not.toBeInTheDocument()

    await user.click(boton)
    await user.click(screen.getByRole('heading', { name: 'Inicio' }))
    expect(screen.queryByRole('menu')).not.toBeInTheDocument()
  })

  it('se cierra al navegar', async () => {
    const user = userEvent.setup()
    const { boton } = renderMenu()
    await user.click(boton)
    await user.click(screen.getByRole('menuitem', { name: 'Mi perfil' }))
    expect(screen.getByRole('heading', { name: 'Perfil' })).toBeInTheDocument()
    expect(screen.queryByRole('menu')).not.toBeInTheDocument()
    expect(boton).toHaveAttribute('aria-expanded', 'false')
  })

  it('"Cerrar sesión" cierra el menú y delega en el cierre de sesión existente', async () => {
    const user = userEvent.setup()
    const { boton, onCerrarSesion } = renderMenu()
    await user.click(boton)
    await user.click(screen.getByRole('menuitem', { name: 'Cerrar sesión' }))
    expect(onCerrarSesion).toHaveBeenCalledOnce()
    expect(screen.queryByRole('menu')).not.toBeInTheDocument()
  })

  it('no presenta violaciones de accesibilidad abierto ni cerrado', async () => {
    const user = userEvent.setup()
    const { boton } = renderMenu()
    expect(await axe(document.body)).toHaveNoViolations()
    await user.click(boton)
    expect(await axe(document.body)).toHaveNoViolations()
  })
})
