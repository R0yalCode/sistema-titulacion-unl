import { Component, type ErrorInfo, type ReactNode } from 'react'
import { logger } from '@/lib/logger'

type ErrorBoundaryProps = {
  children: ReactNode
}

type ErrorBoundaryState = {
  error: Error | null
}

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
      return (
        <div role="alert">
          <h1>Ocurrió un error inesperado</h1>
          <p>Intente nuevamente. Si el problema persiste, contacte a soporte.</p>
          <button type="button" onClick={this.handleRetry}>
            Reintentar
          </button>
        </div>
      )
    }

    return this.props.children
  }
}
