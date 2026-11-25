import { useContext } from 'react'
import { useNavigate } from 'react-router-dom'
import { AuthContext } from '@/auth/AuthContext'
import { getHomeRouteForRoles } from '@/auth/redirect'
import { ErrorPage } from '@/components/errors/ErrorPage'
import { recargarPagina } from '@/lib/recargar'

/**
 * 404 real del router (`path="*"`): no redirige ni oculta el error. «Ir al
 * inicio» lleva al panel del rol con sesión o a la página pública sin ella;
 * «Intentar nuevamente» vuelve a pedir la misma dirección al servidor (por
 * si el recurso se publicó después). No revela si un recurso existe para
 * otra cuenta.
 */
export default function NotFoundPage() {
  const auth = useContext(AuthContext)
  const navigate = useNavigate()
  const inicio = auth?.isAuthenticated ? getHomeRouteForRoles(auth.user?.roles ?? []) : '/'

  return (
    <ErrorPage
      homeHref={inicio}
      kind="not-found"
      primaryAction={{ onClick: () => navigate(inicio) }}
      secondaryAction={{ onClick: recargarPagina }}
    />
  )
}
