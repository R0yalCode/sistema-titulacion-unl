import { screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useState } from 'react'
import { axe } from 'vitest-axe'
import { describe, expect, it, vi } from 'vitest'
import { presentarEstado, nombreRol } from '@/lib/estados'
import { renderWithProviders } from '@/test/renderWithProviders'
import { Breadcrumbs } from './Breadcrumbs'
import { ConfirmDialog, useConfirm } from './ConfirmDialog'
import { DataList } from './DataList'
import { KpiCard } from './KpiCard'
import { Skeleton } from './Skeleton'
import { StatusBadge } from './StatusBadge'

describe('lib/estados (fuente única de estados)', () => {
  it('traduce estados reales con tono semántico coherente', () => {
    expect(presentarEstado('expediente', 'EN_VERIFICACION')).toEqual({ label: 'En verificación', variant: 'info' })
    expect(presentarEstado('expediente', 'OBSERVADA').variant).toBe('warning')
    expect(presentarEstado('expediente', 'DECLARADA_APTA').variant).toBe('success')
    expect(presentarEstado('expediente', 'CANCELADA').variant).toBe('danger')
    expect(presentarEstado('checklist', 'VERIFICADO').variant).toBe('success')
  })

  it('no inventa etiquetas para valores desconocidos', () => {
    expect(presentarEstado('peticion', 'NUEVO')).toEqual({ label: 'NUEVO', variant: 'neutral' })
    expect(nombreRol('SECRETARIA_CARRERA')).toBe('Secretaría de carrera')
    expect(nombreRol('OTRO')).toBe('OTRO')
  })
})

describe('StatusBadge', () => {
  it('muestra la etiqueta legible, no el código interno', () => {
    renderWithProviders(<StatusBadge dominio="expediente" valor="EN_VERIFICACION" />)
    expect(screen.getByText('En verificación')).toBeInTheDocument()
    expect(screen.queryByText('EN_VERIFICACION')).not.toBeInTheDocument()
  })

  it('admite una etiqueta en lenguaje claro sin cambiar el tono', () => {
    renderWithProviders(<StatusBadge dominio="expediente" label="En preparación" valor="BORRADOR" />)
    expect(screen.getByText('En preparación')).toBeInTheDocument()
  })
})

function ConfirmHarness({ onResult }: { onResult: (value: boolean) => void }) {
  const { confirm, dialog } = useConfirm()
  return (
    <>
      <button
        type="button"
        onClick={async () => onResult(await confirm({ title: '¿Enviar expediente?', description: 'No podrá editarlo.', confirmLabel: 'Enviar' }))}
      >
        Abrir
      </button>
      {dialog}
    </>
  )
}

describe('ConfirmDialog / useConfirm', () => {
  it('abre un alertdialog con foco inicial en Cancelar y resuelve true al confirmar', async () => {
    const user = userEvent.setup()
    const onResult = vi.fn()
    renderWithProviders(<ConfirmHarness onResult={onResult} />)

    await user.click(screen.getByRole('button', { name: 'Abrir' }))
    const dialogo = screen.getByRole('alertdialog', { name: '¿Enviar expediente?' })
    expect(dialogo).toHaveAccessibleDescription('No podrá editarlo.')
    expect(within(dialogo).getByRole('button', { name: 'Cancelar' })).toHaveFocus()

    await user.click(within(dialogo).getByRole('button', { name: 'Enviar' }))
    expect(onResult).toHaveBeenCalledWith(true)
    expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Abrir' })).toHaveFocus()
  })

  it('Escape y Cancelar resuelven false', async () => {
    const user = userEvent.setup()
    const onResult = vi.fn()
    renderWithProviders(<ConfirmHarness onResult={onResult} />)

    await user.click(screen.getByRole('button', { name: 'Abrir' }))
    await user.keyboard('{Escape}')
    expect(onResult).toHaveBeenLastCalledWith(false)

    await user.click(screen.getByRole('button', { name: 'Abrir' }))
    await user.click(screen.getByRole('button', { name: 'Cancelar' }))
    expect(onResult).toHaveBeenCalledTimes(2)
    expect(onResult).toHaveBeenLastCalledWith(false)
  })

  it('un doble clic en Confirmar resuelve una sola vez', async () => {
    const user = userEvent.setup()
    const onResult = vi.fn()
    renderWithProviders(<ConfirmHarness onResult={onResult} />)
    await user.click(screen.getByRole('button', { name: 'Abrir' }))
    await user.dblClick(screen.getByRole('button', { name: 'Enviar' }))
    expect(onResult).toHaveBeenCalledTimes(1)
  })

  it('en curso deshabilita ambas acciones (sin dobles envíos)', () => {
    function Ocupado() {
      const [abierto] = useState(true)
      return <ConfirmDialog busy open={abierto} title="Procesando" tone="danger" onCancel={() => undefined} onConfirm={() => undefined} />
    }
    renderWithProviders(<Ocupado />)
    expect(screen.getByRole('button', { name: 'Cancelar' })).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Confirmar' })).toBeDisabled()
  })
})

describe('DataList', () => {
  type Fila = { id: string; numero: string; estado: string }
  const filas: Fila[] = [
    { id: '1', numero: 'EXP-1', estado: 'ENVIADA' },
    { id: '2', numero: 'EXP-2', estado: 'OBSERVADA' },
  ]

  it('presenta cada elemento con datos etiquetados (sin tabla rígida)', async () => {
    const { container } = renderWithProviders(
      <DataList
        fields={[{ key: 'estado', label: 'Estado', render: (f) => f.estado }]}
        getKey={(f) => f.id}
        getTone={(f) => (f.estado === 'OBSERVADA' ? 'warning' : undefined)}
        items={filas}
        label="Expedientes"
        renderActions={(f) => <button type="button">Abrir {f.numero}</button>}
        renderTitle={(f) => f.numero}
      />,
    )
    const lista = screen.getByRole('list', { name: 'Expedientes' })
    expect(within(lista).getAllByRole('listitem')).toHaveLength(2)
    expect(container.querySelector('table')).toBeNull()
    expect(screen.getAllByText('Estado')).toHaveLength(2)
    expect(screen.getByRole('button', { name: 'Abrir EXP-2' })).toBeInTheDocument()
    expect(await axe(container)).toHaveNoViolations()
  })

  it('muestra un estado vacío explicativo', () => {
    renderWithProviders(
      <DataList emptyDescription="Ajuste los filtros." emptyTitle="Sin coincidencias" getKey={() => 'x'} items={[]} label="Vacía" renderTitle={() => null} />,
    )
    expect(screen.getByRole('heading', { name: 'Sin coincidencias' })).toBeInTheDocument()
  })
})

describe('Breadcrumbs, KpiCard y Skeleton', () => {
  it('Breadcrumbs marca la página actual y enlaza las anteriores', () => {
    renderWithProviders(<Breadcrumbs items={[{ label: 'Bandeja', to: '/bandeja' }, { label: 'EXP-1' }]} />)
    const nav = screen.getByRole('navigation', { name: 'Ruta de navegación' })
    expect(within(nav).getByRole('link', { name: 'Bandeja' })).toHaveAttribute('href', '/bandeja')
    expect(within(nav).getByText('EXP-1')).toHaveAttribute('aria-current', 'page')
  })

  it('Breadcrumbs no se dibuja con un solo nivel', () => {
    renderWithProviders(<Breadcrumbs items={[{ label: 'Inicio' }]} />)
    expect(screen.queryByRole('navigation')).not.toBeInTheDocument()
  })

  it('KpiCard expone título, valor y texto', () => {
    renderWithProviders(
      <KpiCard icon={<span />} title="Vencidos" tone="danger" value={3}>
        <p>Requieren atención inmediata.</p>
      </KpiCard>,
    )
    const tarjeta = screen.getByRole('heading', { name: 'Vencidos' }).closest('article') as HTMLElement
    expect(within(tarjeta).getByText('3')).toBeInTheDocument()
  })

  it('Skeleton anuncia la carga a lectores de pantalla', () => {
    renderWithProviders(<Skeleton count={3} label="Cargando bandeja…" />)
    expect(screen.getByRole('status')).toHaveAttribute('aria-busy', 'true')
    expect(screen.getByText('Cargando bandeja…')).toBeInTheDocument()
  })
})
