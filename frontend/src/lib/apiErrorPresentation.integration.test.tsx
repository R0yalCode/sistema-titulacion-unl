import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { HttpResponse, http } from 'msw'
import { describe, expect, it } from 'vitest'
import { request } from '@/api/client'
import type { ApiRequestError } from '@/api/errors'
import { server } from '@/test/server'
import { ErrorState } from '@/components/ui/ErrorState'
import { Spinner } from '@/components/ui/Spinner'
import { presentApiError } from './apiErrorPresentation'

const FIXTURE_URL = 'http://localhost:8000/api/v1/expedientes/fixture/'

function Fixture() {
  const query = useQuery<{ nombre: string }, ApiRequestError>({
    queryKey: ['fixture-expediente'],
    queryFn: () => request('/api/v1/expedientes/fixture/'),
    retry: false,
  })

  if (query.isLoading) {
    return <Spinner label="Cargando expediente…" />
  }

  if (query.isError) {
    const presentation = presentApiError(query.error)
    return (
      <ErrorState
        description={presentation.description}
        onRetry={() => query.refetch()}
        title={presentation.title}
      />
    )
  }

  return <p>Expediente: {query.data?.nombre}</p>
}

function renderFixture() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <Fixture />
    </QueryClientProvider>,
  )
}

describe('Reintento real con TanStack Query (FE-T1212.D)', () => {
  it('reintenta de verdad vía refetch() y muestra los datos tras el segundo intento exitoso', async () => {
    const user = userEvent.setup()
    let callCount = 0
    server.use(
      http.get(FIXTURE_URL, () => {
        callCount += 1
        if (callCount === 1) {
          return HttpResponse.json({ detail: 'Traceback interno no expuesto.' }, { status: 500 })
        }
        return HttpResponse.json({ nombre: 'Expediente de prueba' })
      }),
    )

    renderFixture()

    expect(await screen.findByRole('alert')).toHaveTextContent('Error del servidor')
    expect(screen.queryByText(/Traceback/)).not.toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Reintentar' }))

    expect(await screen.findByText('Expediente: Expediente de prueba')).toBeInTheDocument()
    expect(callCount).toBe(2)
  })

  it('un reintento que vuelve a fallar no simula éxito ni oculta el error', async () => {
    const user = userEvent.setup()
    server.use(http.get(FIXTURE_URL, () => HttpResponse.json({ detail: 'Error.' }, { status: 503 })))

    renderFixture()

    expect(await screen.findByRole('alert')).toHaveTextContent('Servicio no disponible')

    await user.click(screen.getByRole('button', { name: 'Reintentar' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Servicio no disponible')
    expect(screen.queryByText(/Expediente:/)).not.toBeInTheDocument()
  })

  it('cada clic en Reintentar produce exactamente una solicitud nueva (sin duplicados)', async () => {
    const user = userEvent.setup()
    let callCount = 0
    server.use(
      http.get(FIXTURE_URL, () => {
        callCount += 1
        if (callCount < 3) {
          return HttpResponse.json({ detail: 'Error.' }, { status: 500 })
        }
        return HttpResponse.json({ nombre: 'Expediente de prueba' })
      }),
    )

    renderFixture()
    expect(await screen.findByRole('alert')).toBeInTheDocument()
    expect(callCount).toBe(1)

    await user.click(screen.getByRole('button', { name: 'Reintentar' }))
    await screen.findByRole('alert')
    expect(callCount).toBe(2)

    await user.click(screen.getByRole('button', { name: 'Reintentar' }))
    await screen.findByText(/Expediente:/)
    expect(callCount).toBe(3)
  })
})
