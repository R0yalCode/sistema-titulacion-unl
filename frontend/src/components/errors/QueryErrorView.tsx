import { useContext, type ReactNode } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { AuthContext } from '@/auth/AuthContext'
import { getHomeRouteForRoles } from '@/auth/redirect'
import { backendDetail, classifyError } from './classifyError'
import type { ErrorAction } from './ErrorView'
import { ErrorView } from './ErrorView'
import { useControlledRetry } from './useControlledRetry'
import { useOnlineStatus } from './useOnlineStatus'

export type QueryErrorViewProps = {
  /** Error real de la consulta (ApiRequestError de api/client.ts). */
  error: unknown
  /** Vuelve a ejecutar la consulta (p. ej. `query.refetch`). Solo lecturas. */
  onRetry: () => unknown
  /** Textos de contexto para el 404 del recurso (p. ej. «Expediente no encontrado»). */
  notFoundTitle?: string
  notFoundMessage?: string
}

/**
 * Error de la consulta principal de una vista, dentro de su layout. Elige la
 * variante con `classifyError` y conserva el contexto: un 403 no se trata
 * como 401 ni cierra la sesión, un 404 no se convierte en «error de datos» y
 * el reintento vuelve a consultar solo ese recurso, sin recargar la app.
 * El 401 lo atiende el manejador global (lleva a la vista 401).
 */
export function QueryErrorView({ error, onRetry, notFoundTitle, notFoundMessage }: QueryErrorViewProps) {
  const auth = useContext(AuthContext)
  const navigate = useNavigate()
  const online = useOnlineStatus()
  const kind = classifyError(error, online)
  const panel = getHomeRouteForRoles(auth?.user?.roles ?? [])
  const retry = useControlledRetry(onRetry, { backoff: kind === 'unavailable' })

  const irAlInicio: ErrorAction = { onClick: () => navigate('/') }
  const reintentar: ErrorAction = {
    onClick: retry.run,
    loading: retry.pending,
    disabled: retry.waitSeconds > 0,
  }

  let status: ReactNode = null
  if (retry.waitSeconds > 0) {
    status = `Podrás reintentar en ${retry.waitSeconds} s.`
  } else if (kind === 'offline') {
    status = 'Tu dispositivo indica que no hay conexión de red.'
  } else if (kind === 'unavailable' && !online) {
    status = 'Tu dispositivo indica que no hay conexión de red.'
  }

  switch (kind) {
    case 'unauthorized':
      return <ErrorView kind={kind} primaryAction={{ onClick: () => navigate('/login') }} secondaryAction={irAlInicio} />
    case 'forbidden':
      return (
        <ErrorView
          kind={kind}
          primaryAction={{ onClick: () => navigate(panel) }}
          secondaryAction={irAlInicio}
          status={<Link to="/no-habilitado?motivo=rol-no-autorizado">Más información sobre tu acceso</Link>}
        />
      )
    case 'not-found':
      return (
        <ErrorView
          kind={kind}
          message={notFoundMessage}
          primaryAction={{ onClick: () => navigate(panel) }}
          secondaryAction={reintentar}
          title={notFoundTitle}
        />
      )
    default:
      return (
        <ErrorView
          detail={backendDetail(error)}
          kind={kind}
          primaryAction={reintentar}
          secondaryAction={irAlInicio}
          status={status}
        />
      )
  }
}
