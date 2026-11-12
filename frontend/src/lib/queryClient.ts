import { QueryClient } from '@tanstack/react-query'

function hasNumericStatus(error: unknown): error is { status: number } {
  return (
    typeof error === 'object' &&
    error !== null &&
    'status' in error &&
    typeof (error as { status: unknown }).status === 'number'
  )
}

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: (failureCount, error) => hasNumericStatus(error) && error.status >= 500 && failureCount < 2,
      refetchOnWindowFocus: false,
    },
    mutations: { retry: 0 },
  },
})
