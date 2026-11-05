import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'
import { describe, expect, it } from 'vitest'
import { Table, type TableColumn } from './Table'

type Fila = { id: string; nombre: string; estado: string }

const columns: Array<TableColumn<Fila>> = [
  { key: 'nombre', header: 'Nombre', render: (row) => row.nombre },
  { key: 'estado', header: 'Estado', render: (row) => row.estado },
]

const rows: Fila[] = [
  { id: '1', nombre: 'Petición a Secretaría', estado: 'Solicitado' },
  { id: '2', nombre: 'Petición a Dirección', estado: 'Verificado' },
]

describe('Table', () => {
  it('renderiza encabezados con scope="col" y la caption asociada', () => {
    render(<Table caption="Peticiones del expediente" columns={columns} rowKey={(r) => r.id} rows={rows} />);

    const table = screen.getByRole('table', { name: 'Peticiones del expediente' })
    expect(table).toBeInTheDocument()
    expect(screen.getByRole('columnheader', { name: 'Nombre' })).toHaveAttribute('scope', 'col')
    expect(screen.getByRole('columnheader', { name: 'Estado' })).toHaveAttribute('scope', 'col')
  })

  it('renderiza los mismos datos en la vista de tarjetas móvil (sin pérdida de información)', () => {
    render(<Table caption="Peticiones" columns={columns} rowKey={(r) => r.id} rows={rows} />)

    // La tabla y las tarjetas conviven en el DOM (alternadas por CSS); cada celda aparece dos veces.
    expect(screen.getAllByText('Petición a Secretaría')).toHaveLength(2)
    expect(screen.getAllByText('Solicitado')).toHaveLength(2)
  })

  it('muestra un spinner accesible mientras loading es true', () => {
    render(<Table caption="Peticiones" columns={columns} loading rowKey={(r) => r.id} rows={rows} />)

    expect(screen.getByRole('status')).toHaveTextContent('Cargando datos…')
    expect(screen.queryByRole('table')).not.toBeInTheDocument()
  })

  it('muestra EmptyState cuando no hay filas', () => {
    render(<Table caption="Peticiones" columns={columns} rowKey={(r) => r.id} rows={[]} />)

    expect(screen.getByRole('heading', { name: 'Sin resultados' })).toBeInTheDocument()
    expect(screen.queryByRole('table')).not.toBeInTheDocument()
  })

  it('no presenta violaciones de accesibilidad', async () => {
    const { container } = render(<Table caption="Peticiones" columns={columns} rowKey={(r) => r.id} rows={rows} />)

    expect(await axe(container)).toHaveNoViolations()
  })

  it('el contenedor de desplazamiento horizontal es alcanzable por teclado', async () => {
    const user = userEvent.setup()
    render(<Table caption="Peticiones" columns={columns} rowKey={(r) => r.id} rows={rows} />)

    await user.tab()

    expect(screen.getByRole('region', { name: /desplazamiento horizontal/ })).toHaveFocus()
  })
})
