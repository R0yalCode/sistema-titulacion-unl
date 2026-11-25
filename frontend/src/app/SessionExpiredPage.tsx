import { useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { ErrorPage } from '@/components/errors/ErrorPage'
import { limpiarSesionExpirada, rutaDeRetorno } from '@/auth/sessionExpiry'

/**
 * 401 — vista pública a la que lleva el manejador global cuando la API
 * responde 401 (sesión expirada o inválida). Ya se cerró la sesión antes de
 * llegar aquí; la vista no hace peticiones, así que no puede generar otro
 * 401 ni un bucle. «Iniciar sesión» usa el login real y conserva la ruta en
 * la que estaba el usuario (`returnTo`, el mismo mecanismo que RequireAuth).
 */
export default function SessionExpiredPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const returnTo = rutaDeRetorno((location.state as { returnTo?: unknown } | null)?.returnTo)

  // La marca ya cumplió su función: un cierre de sesión posterior vuelve al login.
  useEffect(() => {
    limpiarSesionExpirada()
  }, [])

  return (
    <ErrorPage
      kind="unauthorized"
      primaryAction={{
        onClick: () => navigate('/login', { replace: true, state: returnTo ? { returnTo } : undefined }),
      }}
      secondaryAction={{ onClick: () => navigate('/') }}
    />
  )
}
