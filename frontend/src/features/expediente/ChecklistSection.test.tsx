import type { UseQueryResult } from '@tanstack/react-query'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import type { ChecklistItem } from '@/api/endpoints/checklist'
import { ApiRequestError } from '@/api/errors'
import { ChecklistSection } from './ChecklistSection'

type Query = UseQueryResult<ChecklistItem[], ApiRequestError>

function renderSection(query: Query, roles: string[] = ['SECRETARIO_ABOGADO']) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <ChecklistSection esPropietario estadoExpediente="EN_VERIFICACION" expedienteId="exp-1" query={query} roles={roles} />
    </QueryClientProvider>,
  )
}

describe('ChecklistSection', () => {
  it('muestra el panel informativo si el rol no está autorizado, sin consultar la query', () => {
    const query = { isError: false, isLoading: true } as unknown as Query
    renderSection(query, ['ESTUDIANTE'])

    expect(screen.getByText('No disponible para su rol')).toBeInTheDocument()
  })

  it('muestra el indicador de carga', () => {
    const query = { isError: false, isLoading: true } as unknown as Query
    renderSection(query)

    expect(screen.getByRole('status')).toHaveTextContent('Cargando checklist…')
  })

  it('muestra ForbiddenState ante un 403 real', () => {
    const query = {
      isError: true,
      isLoading: false,
      error: new ApiRequestError({ status: 403, code: 'FORBIDDEN', message: 'Prohibido', isNetworkError: false, isTimeout: false }),
      refetch: vi.fn(),
    } as unknown as Query
    renderSection(query)

    expect(screen.getByRole('status')).toHaveTextContent('Acceso restringido')
  })

  it('permite reintentar ante un error de servidor', async () => {
    const refetch = vi.fn()
    const query = {
      isError: true,
      isLoading: false,
      error: new ApiRequestError({ status: 500, code: 'INTERNAL_SERVER_ERROR', message: 'Error', isNetworkError: false, isTimeout: false }),
      refetch,
    } as unknown as Query
    const user = userEvent.setup()
    renderSection(query)

    await user.click(screen.getByRole('button', { name: 'Reintentar' }))

    expect(refetch).toHaveBeenCalledTimes(1)
  })

  it('muestra un mensaje cuando el expediente no tiene checklist registrado', () => {
    const query = { isError: false, isLoading: false, data: [] } as unknown as Query
    renderSection(query)

    expect(screen.getByText('Este expediente no tiene checklist registrado todavía.')).toBeInTheDocument()
  })
})
