import { Component, type ErrorInfo, type ReactNode } from 'react'
import { ErrorPage } from '@/components/errors/ErrorPage'
import { logger } from '@/lib/logger'

type ErrorBoundaryProps = {
  children: ReactNode
}

type ErrorBoundaryState = {
  error: Error | null
}

/**
 * Límite global de errores de renderizado (envuelve providers y router). Solo
 * captura excepciones de React durante el render: los errores HTTP siguen en
 * sus vistas (QueryErrorView/ErrorState) y el 401 en el manejador global. Se
 * registra con el logger existente y no se muestra ningún detalle técnico.
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  override state: ErrorBoundaryState = { error: null }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { error }
  }

  override componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    logger.error('Error no controlado en la interfaz.', {
      message: error.message,
      componentStack: errorInfo.componentStack,
    })
  }

  private handleRetry = (): void => {
    this.setState({ error: null })
  }

  override render(): ReactNode {
    if (this.state.error) {
      // Fuera del router: las acciones son un reinicio del límite y un enlace de documento.
      return <ErrorPage kind="server" primaryAction={{ onClick: this.handleRetry }} secondaryAction={{ href: '/' }} />
    }

    return this.props.children
  }
}
