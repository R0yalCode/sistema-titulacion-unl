import type { ReactNode } from 'react'
import { QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { AuthProvider } from '@/auth/AuthContext'
import { ErrorBoundary } from '@/components/feedback/ErrorBoundary'
import { ToastProvider } from '@/components/feedback/ToastProvider'
import { AccesibilidadProvider } from '@/features/accesibilidad'
import { queryClient } from '@/lib/queryClient'

type AppProvidersProps = {
  children: ReactNode
}

export function AppProviders({ children }: AppProvidersProps) {
  return (
    <ErrorBoundary>
      {/* Accesibilidad por fuera del resto: sus preferencias valen en todas
          las vistas, también en las públicas y en las de error. */}
      <AccesibilidadProvider>
        <QueryClientProvider client={queryClient}>
          <AuthProvider>
            <ToastProvider>
              <BrowserRouter>{children}</BrowserRouter>
            </ToastProvider>
          </AuthProvider>
        </QueryClientProvider>
      </AccesibilidadProvider>
    </ErrorBoundary>
  )
}
