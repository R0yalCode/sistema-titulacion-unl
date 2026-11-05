import type { UseQueryResult } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import type { BandejaExpediente } from '@/api/endpoints/expedientes'
import { ApiRequestError } from '@/api/errors'
import type { Paginated } from '@/api/types/api'
import { ExpedientesCard } from './ExpedientesCard'

type Query = UseQueryResult<Paginated<BandejaExpediente>, ApiRequestError>

function renderCard(query: Query) {
  return render(
    <MemoryRouter>
      <ExpedientesCard page={1} query={query} onPageChange={vi.fn()} onVisit={vi.fn()} />
    </MemoryRouter>,
  )
}

describe('ExpedientesCard', () => {
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

    renderCard(query)

    expect(screen.getByRole('status')).toHaveTextContent('Acceso restringido')
  })
})
