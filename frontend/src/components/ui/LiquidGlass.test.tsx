import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'
import { describe, expect, it } from 'vitest'
import { ActionCard, actionCardCtaClass } from './ActionCard'
import { HeroPanel } from './HeroPanel'
import { AlertIcon, CalendarIcon, FolderIcon } from './icons'
import { KpiCard } from './KpiCard'
import { UrgencyIndicator } from './UrgencyIndicator'

const VENCIDOS = { singular: 'vencido', plural: 'vencidos' }

describe('UrgencyIndicator', () => {
  it('muestra la cantidad real con texto en singular o plural', () => {
    const { rerender } = render(<UrgencyIndicator count={1} label={VENCIDOS} />)
    expect(screen.getByText('1 vencido')).toBeInTheDocument()
    rerender(<UrgencyIndicator count={3} label={VENCIDOS} />)
    expect(screen.getByText('3 vencidos')).toBeInTheDocument()
  })

  it('no se muestra sin una cantidad real mayor que cero', () => {
    const { container, rerender } = render(<UrgencyIndicator count={0} label={VENCIDOS} />)
    expect(container).toBeEmptyDOMElement()
    rerender(<UrgencyIndicator count={Number.NaN} label={VENCIDOS} />)
    expect(container).toBeEmptyDOMElement()
  })

  it('solo pulsa con urgencia crítica; «atención» queda estático', () => {
    const { container, rerender } = render(<UrgencyIndicator count={2} label={VENCIDOS} />)
    const indicador = container.firstElementChild as HTMLElement
    expect(indicador).toHaveAttribute('data-pulse', 'true')
    expect(indicador.querySelector('[aria-hidden="true"]')?.childElementCount).toBe(1)

    rerender(<UrgencyIndicator count={2} label={VENCIDOS} level="attention" />)
    const estatico = container.firstElementChild as HTMLElement
    expect(estatico).toHaveAttribute('data-pulse', 'false')
    expect(estatico.querySelector('[aria-hidden="true"]')?.childElementCount).toBe(0)
  })

  it('el punto decorativo queda fuera del árbol accesible', async () => {
    const { container } = render(<UrgencyIndicator count={4} label={VENCIDOS} />)
    expect(container.querySelector('[aria-hidden="true"]')).not.toBeNull()
    expect(await axe(container)).toHaveNoViolations()
  })
})

describe('HeroPanel', () => {
  it('expone una región nombrada por su título y los chips como lista', async () => {
    const { container } = render(
      <HeroPanel
        description="Consulta tu avance."
        eyebrow="Expediente EXP-0001"
        meta={[
          { id: 'fecha', icon: <CalendarIcon size={14} />, label: 'Registrado: 3 nov 2026' },
          { id: 'etapa', label: 'Etapa: Verificación' },
        ]}
        title="Hola, Ana"
      />,
    )
    expect(screen.getByRole('heading', { level: 1, name: 'Hola, Ana' })).toBeInTheDocument()
    expect(screen.getByRole('region', { name: 'Hola, Ana' })).toBeInTheDocument()
    expect(screen.getAllByRole('listitem')).toHaveLength(2)
    expect(screen.getByText('Expediente EXP-0001')).toHaveClass('glass-on-brand')
    expect(await axe(container)).toHaveNoViolations()
  })

  it('admite nivel de encabezado 2 y contenido lateral', () => {
    render(<HeroPanel aside={<p>Lateral</p>} headingLevel={2} title="Panel" />)
    expect(screen.getByRole('heading', { level: 2, name: 'Panel' })).toBeInTheDocument()
    expect(screen.getByText('Lateral')).toBeInTheDocument()
    expect(screen.queryByRole('list')).not.toBeInTheDocument()
  })
})

describe('ActionCard', () => {
  it('presenta categoría, título, contexto y un CTA real', async () => {
    const { container } = render(
      <ActionCard
        action={
          <a className={actionCardCtaClass} href="/expedientes/1">
            Ver y corregir
          </a>
        }
        badge={<UrgencyIndicator count={1} label={{ singular: 'observación', plural: 'observaciones' }} />}
        description="El documento requiere una corrección."
        eyebrow="Acción prioritaria"
        icon={<AlertIcon />}
        meta={<span>Registrada el 3 nov 2026</span>}
        title="Corrige el documento"
        tone="warning"
      />,
    )
    const tarjeta = screen.getByRole('article')
    expect(tarjeta).toHaveClass('glass-floating')
    expect(screen.getByRole('heading', { level: 2, name: 'Corrige el documento' })).toBeInTheDocument()
    expect(screen.getByText('Acción prioritaria')).toBeInTheDocument()
    expect(screen.getByText('1 observación')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Ver y corregir' })).toHaveAttribute('href', '/expedientes/1')
    expect(await axe(container)).toHaveNoViolations()
  })

  it('sin CTA ni contexto no deja un pie vacío', () => {
    render(<ActionCard eyebrow="Estado" icon={<FolderIcon />} title="Sin acciones pendientes" tone="success" />)
    expect(screen.getByRole('article').querySelector('footer')).toBeNull()
  })
})

describe('KpiCard variante glass', () => {
  it('aplica la capa glass solo cuando se pide', () => {
    const { rerender } = render(<KpiCard icon={<FolderIcon />} title="Progreso" value={40} variant="glass" />)
    expect(screen.getByRole('article')).toHaveClass('glass-panel')
    expect(screen.getByRole('article')).toHaveAttribute('data-variant', 'glass')

    rerender(<KpiCard icon={<FolderIcon />} title="Progreso" value={40} />)
    expect(screen.getByRole('article')).not.toHaveClass('glass-panel')
    expect(screen.getByRole('article')).toHaveAttribute('data-variant', 'solid')
  })
})
