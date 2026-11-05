import { useContext, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { AuthContext } from '@/auth/AuthContext'
import { decodeAccessToken } from '@/auth/jwt'
import { getHomeRouteForRoles } from '@/auth/redirect'
import { login } from '@/api/endpoints/auth'
import { ApiRequestError } from '@/api/errors'
import { DemoBanner } from '@/components/layout/DemoBanner'
import { presentApiError } from '@/lib/apiErrorPresentation'
import { getEnv } from '@/lib/env'
import { LoginForm, type LoginFormValues } from './LoginForm'
import styles from './LoginPage.module.css'

const UNAVAILABLE_STATUSES = [500, 502, 503, 504]

function describeLoginError(error: unknown): string {
  if (!(error instanceof ApiRequestError)) {
    return 'No se pudo iniciar sesión. Intente nuevamente.'
  }

  const { status, isNetworkError, isTimeout, message } = error.error

  if (status === 401) {
    return 'Usuario o contraseña incorrectos.'
  }
  if (status === 403) {
    return 'No tiene permisos para iniciar sesión con esta cuenta.'
  }
  if (status === 400 || status === 422) {
    return message
  }
  if (isNetworkError || isTimeout || UNAVAILABLE_STATUSES.includes(status)) {
    return presentApiError(error).description
  }

  return 'No se pudo iniciar sesión. Intente nuevamente.'
}

export default function LoginPage() {
  const auth = useContext(AuthContext)
  const navigate = useNavigate()
  const location = useLocation()
  const [submitting, setSubmitting] = useState(false)
  const [serverError, setServerError] = useState<string | null>(null)

  async function handleSubmit(values: LoginFormValues): Promise<boolean> {
    setSubmitting(true)
    setServerError(null)

    try {
      const tokens = await login(values)
      const ok = auth?.login(tokens) ?? false
      if (!ok) {
        setServerError('No se pudo iniciar sesión. Intente nuevamente.')
        return false
      }

      const user = decodeAccessToken(tokens.access)
      const state = location.state as { returnTo?: string } | null
      const target = state?.returnTo ?? getHomeRouteForRoles(user?.roles ?? [])
      navigate(target, { replace: true })
      return true
    } catch (error) {
      setServerError(describeLoginError(error))
      return false
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className={styles.page}>
      <div aria-hidden="true" className={styles.visual}>
        <p className={styles.visualText}>Tu futuro profesional comienza aquí</p>
      </div>
      <div className={styles.panel}>
        <DemoBanner show={getEnv().demoMode} />
        <h1 className={styles.heading}>Iniciar sesión</h1>
        <p className={styles.subtitle}>SGT-SIAAF — Sistema de Gestión del Trámite de Titulación</p>
        <LoginForm serverError={serverError} submitting={submitting} onSubmit={handleSubmit} />
      </div>
    </main>
  )
}
