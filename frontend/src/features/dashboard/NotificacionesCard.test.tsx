import type { UseQueryResult } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import type { ListNotificacionesResponse } from '@/api/endpoints/notificaciones'
import { ApiRequestError } from '@/api/errors'
import { NotificacionesCard } from './NotificacionesCard'

type Query = UseQueryResult<ListNotificacionesResponse, ApiRequestError>

describe('NotificacionesCard', () => {
  it('muestra ForbiddenState ante un 403', () => {
    const query = {
      isError: true,
      isLoading: false,
      error: new ApiRequestError({
        status: 403,
        code: 'FORBIDDEN',
        message: 'Prohibido',
        isNetworkError: false,
        isTimeout: false,
      }),
      refetch: vi.fn(),
    } as unknown as Query

    render(<NotificacionesCard pendingId={null} query={query} onMarkRead={vi.fn()} />)

    expect(screen.getByRole('status')).toHaveTextContent('Acceso restringido')
  })

  it('permite reintentar ante un error de servidor', async () => {
    const refetch = vi.fn()
    const query = {
      isError: true,
      isLoading: false,
      error: new ApiRequestError({
        status: 500,
        code: 'INTERNAL_SERVER_ERROR',
        message: 'Error',
        isNetworkError: false,
        isTimeout: false,
      }),
      refetch,
    } as unknown as Query

    const user = userEvent.setup()
    render(<NotificacionesCard pendingId={null} query={query} onMarkRead={vi.fn()} />)

    await user.click(screen.getByRole('button', { name: 'Reintentar' }))

    expect(refetch).toHaveBeenCalledTimes(1)
  })

  it('muestra un estado vacío sin notificaciones', () => {
    const query = {
      isError: false,
      isLoading: false,
      data: { results: [] },
    } as unknown as Query

    render(<NotificacionesCard pendingId={null} query={query} onMarkRead={vi.fn()} />)

    expect(screen.getByText('Sin notificaciones')).toBeInTheDocument()
  })

  it('muestra el indicador de carga', () => {
    const query = { isError: false, isLoading: true } as unknown as Query

    render(<NotificacionesCard pendingId={null} query={query} onMarkRead={vi.fn()} />)

    expect(screen.getByRole('status')).toHaveTextContent('Cargando notificaciones…')
  })
})
