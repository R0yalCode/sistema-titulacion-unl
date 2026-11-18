import { useContext, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { AuthContext } from '@/auth/AuthContext'
import { decodeAccessToken } from '@/auth/jwt'
import { getHomeRouteForRoles } from '@/auth/redirect'
import { login } from '@/api/endpoints/auth'
import { DemoBanner } from '@/components/layout/DemoBanner'
import { getEnv } from '@/lib/env'
import { describeLoginError } from './authErrors'
import { AuthLayout } from './components/AuthLayout'
import { LoginForm, type LoginFormValues } from './LoginForm'

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
    <AuthLayout notice={<DemoBanner show={getEnv().demoMode} />} title="Ingreso">
      <LoginForm serverError={serverError} submitting={submitting} onSubmit={handleSubmit} />
    </AuthLayout>
  )
}
