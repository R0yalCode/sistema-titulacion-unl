import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import {
  INVALID_RESET_LINK_CODE,
  confirmPasswordReset,
  validatePasswordResetLink,
  type PasswordResetLink,
} from '@/api/endpoints/auth'
import { ApiRequestError } from '@/api/errors'
import { Button } from '@/components/ui/Button'
import { Spinner } from '@/components/ui/Spinner'
import { describeTransportError } from './authErrors'
import { AuthLayout } from './components/AuthLayout'
import { AlertCircleIcon, ArrowLeftIcon, CheckCircleIcon } from '@/components/ui/icons'
import styles from './components/authForm.module.css'
import { ResetPasswordForm } from './ResetPasswordForm'

type Stage = 'checking' | 'ready' | 'invalid' | 'unavailable' | 'done'

function isInvalidLinkError(error: unknown): boolean {
  if (!(error instanceof ApiRequestError)) {
    return false
  }
  const raw = error.error.raw
  return (
    typeof raw === 'object' && raw !== null && (raw as { code?: unknown }).code === INVALID_RESET_LINK_CODE
  )
}

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams()
  const uid = searchParams.get('uid') ?? ''
  const token = searchParams.get('token') ?? ''
  const link = useMemo<PasswordResetLink | null>(() => (uid && token ? { uid, token } : null), [uid, token])

  const [stage, setStage] = useState<Stage>(link ? 'checking' : 'invalid')
  const [checkAttempt, setCheckAttempt] = useState(0)
  const [unavailableMessage, setUnavailableMessage] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [serverError, setServerError] = useState<string | null>(null)
  const [passwordErrors, setPasswordErrors] = useState<string[]>([])

  useEffect(() => {
    if (!link) {
      return
    }

    let cancelled = false
    validatePasswordResetLink(link)
      .then(() => {
        if (!cancelled) {
          setStage('ready')
        }
      })
      .catch((error: unknown) => {
        if (cancelled) {
          return
        }
        const transportMessage = isInvalidLinkError(error) ? null : describeTransportError(error)
        if (transportMessage) {
          setUnavailableMessage(transportMessage)
          setStage('unavailable')
        } else {
          setStage('invalid')
        }
      })

    return () => {
      cancelled = true
    }
  }, [link, checkAttempt])

  async function handleSubmit(newPassword: string): Promise<boolean> {
    if (!link) {
      return false
    }

    setSubmitting(true)
    setServerError(null)
    setPasswordErrors([])
    try {
      await confirmPasswordReset(link, newPassword)
      setStage('done')
      return true
    } catch (error) {
      if (isInvalidLinkError(error)) {
        setStage('invalid')
        return false
      }
      const fieldErrors = error instanceof ApiRequestError ? error.error.fieldErrors?.new_password : undefined
      if (fieldErrors?.length) {
        setPasswordErrors(fieldErrors)
      } else {
        setServerError(
          describeTransportError(error) ?? 'No se pudo restablecer la contraseña. Intente nuevamente.',
        )
      }
      return false
    } finally {
      setSubmitting(false)
    }
  }

  if (stage === 'checking') {
    return (
      <AuthLayout title="Restablecer contraseña">
        <div className={styles.result}>
          <Spinner label="Comprobando el enlace…" />
          <p className={styles.resultText}>Comprobando el enlace…</p>
        </div>
      </AuthLayout>
    )
  }

  if (stage === 'unavailable') {
    return (
      <AuthLayout title="Restablecer contraseña">
        <div className={styles.result} role="alert">
          <span className={[styles.resultIcon, styles.resultDanger].join(' ')}>
            <AlertCircleIcon />
          </span>
          <p className={styles.resultText}>{unavailableMessage}</p>
          <div className={styles.resultActions}>
            <Button
              variant="secondary"
              onClick={() => {
                setStage('checking')
                setCheckAttempt((current) => current + 1)
              }}
            >
              Reintentar
            </Button>
          </div>
        </div>
      </AuthLayout>
    )
  }

  if (stage === 'invalid') {
    return (
      <AuthLayout title="Enlace no válido">
        <div className={styles.result} role="alert">
          <span className={[styles.resultIcon, styles.resultDanger].join(' ')}>
            <AlertCircleIcon />
          </span>
          <p className={styles.resultText}>
            El enlace de restablecimiento no es válido, ha caducado o ya fue utilizado. Solicite uno nuevo para
            continuar.
          </p>
          <div className={styles.resultActions}>
            <Link className={[styles.link, styles.linkAsButton].join(' ')} to="/recuperar-contrasena">
              Solicitar un nuevo enlace
            </Link>
            <Link className={styles.link} to="/login">
              <ArrowLeftIcon />
              Volver al ingreso
            </Link>
          </div>
        </div>
      </AuthLayout>
    )
  }

  if (stage === 'done') {
    return (
      <AuthLayout title="Contraseña actualizada">
        <div className={styles.result} role="status">
          <span className={[styles.resultIcon, styles.resultSuccess].join(' ')}>
            <CheckCircleIcon />
          </span>
          <p className={styles.resultText}>
            Su contraseña se restableció correctamente. Ya puede ingresar al sistema con la nueva contraseña.
          </p>
          <div className={styles.resultActions}>
            <Link className={[styles.link, styles.linkAsButton].join(' ')} to="/login">
              Ir al ingreso
            </Link>
          </div>
        </div>
      </AuthLayout>
    )
  }

  return (
    <AuthLayout title="Restablecer contraseña">
      <ResetPasswordForm
        passwordErrors={passwordErrors}
        serverError={serverError}
        submitting={submitting}
        onSubmit={handleSubmit}
      />
    </AuthLayout>
  )
}
