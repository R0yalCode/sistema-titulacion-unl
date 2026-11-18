import { useCallback, useContext, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { AuthContext } from '@/auth/AuthContext'
import { decodeAccessToken } from '@/auth/jwt'
import { getHomeRouteForRoles } from '@/auth/redirect'
import { login, type AuthResult, type TokenPair } from '@/api/endpoints/auth'
import { DemoBanner } from '@/components/layout/DemoBanner'
import { getEnv } from '@/lib/env'
import { describeLoginError } from './authErrors'
import { AuthLayout } from './components/AuthLayout'
import { LoginForm, type LoginFormValues } from './LoginForm'
import { MfaSetupStep } from './MfaSetupStep'
import { MfaVerifyStep } from './MfaVerifyStep'
import { RecoveryCodesStep } from './RecoveryCodesStep'

const GENERIC_LOGIN_ERROR = 'No se pudo iniciar sesión. Intente nuevamente.'

/**
 * Pasos del ingreso (AUTH-C). El reto del segundo factor y los códigos de
 * recuperación viven solo en este estado de React: nunca en almacenamiento
 * del navegador. Ninguna ruta protegida es accesible hasta `authenticated`.
 */
type Step =
  | { kind: 'credentials' }
  | { kind: 'setup'; challenge: string }
  | { kind: 'verify'; challenge: string }
  | { kind: 'recovery-codes'; tokens: TokenPair; codes: string[] }

const TITLES: Record<Step['kind'], string> = {
  credentials: 'Ingreso',
  setup: 'Configurar verificación en dos pasos',
  verify: 'Verificación de seguridad (2FA)',
  'recovery-codes': 'Códigos de recuperación',
}

export default function LoginPage() {
  const auth = useContext(AuthContext)
  const navigate = useNavigate()
  const location = useLocation()
  const [step, setStep] = useState<Step>({ kind: 'credentials' })
  const [submitting, setSubmitting] = useState(false)
  const [serverError, setServerError] = useState<string | null>(null)

  const finish = useCallback(
    (tokens: TokenPair): boolean => {
      const ok = auth?.login(tokens) ?? false
      if (!ok) {
        setStep({ kind: 'credentials' })
        setServerError(GENERIC_LOGIN_ERROR)
        return false
      }
      const user = decodeAccessToken(tokens.access)
      const state = location.state as { returnTo?: string } | null
      navigate(state?.returnTo ?? getHomeRouteForRoles(user?.roles ?? []), { replace: true })
      return true
    },
    [auth, location.state, navigate],
  )

  const handleResult = useCallback(
    (result: AuthResult): boolean => {
      setServerError(null)
      switch (result.status) {
        case 'authenticated': {
          const tokens = { access: result.access, refresh: result.refresh }
          if (result.recovery_codes?.length) {
            setStep({ kind: 'recovery-codes', tokens, codes: result.recovery_codes })
            return true
          }
          return finish(tokens)
        }
        case 'mfa_setup_required':
          setStep({ kind: 'setup', challenge: result.challenge })
          return true
        case 'mfa_required':
          setStep({ kind: 'verify', challenge: result.challenge })
          return true
        default:
          setStep({ kind: 'credentials' })
          setServerError(GENERIC_LOGIN_ERROR)
          return false
      }
    },
    [finish],
  )

  const restart = useCallback((message: string) => {
    setStep({ kind: 'credentials' })
    setServerError(message)
  }, [])

  const cancel = useCallback(() => {
    setStep({ kind: 'credentials' })
    setServerError(null)
  }, [])

  async function handleCredentials(values: LoginFormValues): Promise<boolean> {
    setSubmitting(true)
    setServerError(null)
    try {
      return handleResult(await login(values))
    } catch (error) {
      setServerError(describeLoginError(error))
      return false
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <AuthLayout notice={<DemoBanner show={getEnv().demoMode} />} title={TITLES[step.kind]}>
      {step.kind === 'credentials' && (
        <LoginForm serverError={serverError} submitting={submitting} onSubmit={handleCredentials} />
      )}
      {step.kind === 'setup' && (
        <MfaSetupStep challenge={step.challenge} onCancel={cancel} onRestart={restart} onResult={handleResult} />
      )}
      {step.kind === 'verify' && (
        <MfaVerifyStep challenge={step.challenge} onCancel={cancel} onRestart={restart} onResult={handleResult} />
      )}
      {step.kind === 'recovery-codes' && (
        <RecoveryCodesStep codes={step.codes} onContinue={() => finish(step.tokens)} />
      )}
    </AuthLayout>
  )
}
