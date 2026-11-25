import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'
import { describe, expect, it, vi } from 'vitest'
import { ApiRequestError, networkApiError, normalizeApiError, timeoutApiError } from '@/api/errors'
import { backendDetail, classifyError } from './classifyError'
import { ERROR_CATALOG, type ErrorKind } from './errorCatalog'
import { ErrorView } from './ErrorView'

const KINDS = Object.keys(ERROR_CATALOG) as ErrorKind[]

function http(status: number, body: unknown = null) {
  return new ApiRequestError(normalizeApiError(status, body))
}

describe('classifyError', () => {
  it('clasifica los códigos HTTP reales', () => {
    expect(classifyError(http(401))).toBe('unauthorized')
    expect(classifyError(http(403))).toBe('forbidden')
    expect(classifyError(http(404))).toBe('not-found')
    expect(classifyError(http(500))).toBe('server')
    expect(classifyError(http(501))).toBe('server')
    expect(classifyError(http(502))).toBe('unavailable')
    expect(classifyError(http(503))).toBe('unavailable')
    expect(classifyError(http(400))).toBe('data')
    expect(classifyError(http(422))).toBe('data')
  })

  it('distingue timeout del cliente, 408 y 504 de los fallos de servidor', () => {
    expect(classifyError(new ApiRequestError(timeoutApiError()))).toBe('timeout')
    expect(classifyError(http(408))).toBe('timeout')
    expect(classifyError(http(504))).toBe('timeout')
  })

  it('solo es «offline» cuando el navegador informa que no hay red', () => {
    const red = new ApiRequestError(networkApiError())
    expect(classifyError(red, false)).toBe('offline')
    expect(classifyError(red, true)).toBe('unavailable')
  })

  it('un error que no viene de la API es un error de carga de datos', () => {
    expect(classifyError(new TypeError('x'))).toBe('data')
    expect(classifyError('texto')).toBe('data')
  })

  it('backendDetail devuelve solo el «detail» textual y nunca para 401/403/404', () => {
    expect(backendDetail(http(500, { detail: 'La transición no está permitida.', code: 'x' }))).toBe(
      'La transición no está permitida.',
    )
    expect(backendDetail(http(500, '<html>Traceback…</html>'))).toBeNull()
    expect(backendDetail(http(403, { detail: 'Regla interna' }))).toBeNull()
    expect(backendDetail(new TypeError('x'))).toBeNull()
  })
})

describe('ErrorView', () => {
  it.each(KINDS)('renderiza la variante %s con sus textos del catálogo', (kind) => {
    const copy = ERROR_CATALOG[kind]
    render(<ErrorView kind={kind} primaryAction={{ onClick: vi.fn() }} secondaryAction={{ onClick: vi.fn() }} />)
    expect(screen.getByRole('heading', { level: 2, name: copy.title })).toBeInTheDocument()
    expect(screen.getByText(copy.message)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: copy.primaryLabel })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: copy.secondaryLabel })).toBeInTheDocument()
  })

  it('la mascota es decorativa y no lleva ninguna etiqueta de texto', () => {
    const { container } = render(<ErrorView kind="not-found" />)
    const img = container.querySelector('img') as HTMLImageElement
    expect(img).toHaveAttribute('alt', '')
    expect(img.getAttribute('src')).toBe('/assets/mascotas/mascota-404.png')
    expect(screen.queryByText(/mascota|panda/i)).not.toBeInTheDocument()
  })

  it('en página usa h1 y le da el foco para anunciar el cambio', () => {
    render(<ErrorView kind="server" variant="page" />)
    const titulo = screen.getByRole('heading', { level: 1, name: 'Algo salió mal' })
    expect(titulo).toHaveFocus()
  })

  it('en línea es una región viva: alert para fallas, status para 403', () => {
    const { rerender } = render(<ErrorView kind="data" />)
    expect(screen.getByRole('alert')).toBeInTheDocument()
    rerender(<ErrorView kind="forbidden" />)
    expect(screen.getByRole('status')).toBeInTheDocument()
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
  })

  it('ejecuta las acciones reales y admite enlaces de documento', async () => {
    const user = userEvent.setup()
    const reintentar = vi.fn()
    render(<ErrorView kind="server" primaryAction={{ onClick: reintentar }} secondaryAction={{ href: '/' }} />)
    await user.click(screen.getByRole('button', { name: 'Intentar nuevamente' }))
    expect(reintentar).toHaveBeenCalledTimes(1)
    expect(screen.getByRole('link', { name: 'Ir al inicio' })).toHaveAttribute('href', '/')
  })

  it('muestra el detalle del backend y el estado vivo cuando existen', () => {
    render(<ErrorView detail="Servicio académico caído." kind="server" status="Próximo intento en 5 s" />)
    expect(screen.getByText('Servicio académico caído.')).toBeInTheDocument()
    expect(screen.getByText('Próximo intento en 5 s').closest('[aria-live]')).toHaveAttribute('aria-live', 'polite')
  })

  it('no presenta violaciones de accesibilidad detectables por axe', async () => {
    const { container } = render(
      <ErrorView kind="offline" primaryAction={{ onClick: vi.fn() }} secondaryAction={{ href: '/' }} variant="page" />,
    )
    expect(await axe(container)).toHaveNoViolations()
  })
})
