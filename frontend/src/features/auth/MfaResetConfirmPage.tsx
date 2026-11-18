import { useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { INVALID_MFA_RESET_LINK_CODE, confirmMfaReset } from '@/api/endpoints/auth'
import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { apiErrorCode, describeTransportError } from './authErrors'
import { AuthLayout } from './components/AuthLayout'
import { AlertCircleIcon, CheckCircleIcon } from './components/icons'
import styles from './components/authForm.module.css'

type Stage = 'confirm' | 'done' | 'invalid'

/**
 * Paso 2 del restablecimiento del 2FA: el enlace recibido por correo. La
 * confirmación exige pulsar un botón (POST), para que los analizadores de
 * enlaces de los clientes de correo no consuman el enlace por sí solos.
 */
export default function MfaResetConfirmPage() {
  const [searchParams] = useSearchParams()
  const uid = searchParams.get('uid') ?? ''
  const token = searchParams.get('token') ?? ''
  const [stage, setStage] = useState<Stage>(uid && token ? 'confirm' : 'invalid')
  const [submitting, setSubmitting] = useState(false)
  const [serverError, setServerError] = useState<string | null>(null)

  async function confirm() {
    setSubmitting(true)
    setServerError(null)
    try {
      await confirmMfaReset({ uid, token })
      setStage('done')
    } catch (error) {
      if (apiErrorCode(error) === INVALID_MFA_RESET_LINK_CODE) {
        setStage('invalid')
      } else {
        setServerError(describeTransportError(error) ?? 'No se pudo completar la operación. Intente nuevamente.')
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <AuthLayout title="Restablecimiento de doble factor de autenticación (2FA)" titleStyle="panel">
      {stage === 'confirm' && (
        <div className={styles.form}>
          <p className={styles.intro}>
            Al confirmar, se retirará el autenticador vinculado a su cuenta, se anularán sus códigos de recuperación y
            se revocarán los dispositivos de confianza. En su próximo ingreso deberá registrar Google Authenticator de
            nuevo.
          </p>
          {serverError && <Alert variant="danger">{serverError}</Alert>}
          <Button className={styles.submit} disabled={submitting} loading={submitting} size="lg" onClick={() => void confirm()}>
            Confirmar restablecimiento
          </Button>
          <div className={styles.links}>
            <Link className={styles.link} to="/login">
              Cancelar y regresar al inicio
            </Link>
          </div>
        </div>
      )}
      {stage === 'done' && (
        <div className={styles.result}>
          <span aria-hidden="true" className={`${styles.resultIcon} ${styles.resultSuccess}`}>
            <CheckCircleIcon />
          </span>
          <p className={styles.resultTitle} role="status">
            Doble factor restablecido
          </p>
          <p className={styles.resultText}>
            Inicie sesión con su correo institucional y contraseña para registrar su nuevo autenticador.
          </p>
          <div className={styles.resultActions}>
            <Link className={`${styles.link} ${styles.linkAsButton}`} to="/login">
              Iniciar sesión
            </Link>
          </div>
        </div>
      )}
      {stage === 'invalid' && (
        <div className={styles.result}>
          <span aria-hidden="true" className={`${styles.resultIcon} ${styles.resultDanger}`}>
            <AlertCircleIcon />
          </span>
          <p className={styles.resultTitle} role="status">
            Enlace no válido
          </p>
          <p className={styles.resultText}>El enlace no es válido, ya se utilizó o ha caducado. Solicite uno nuevo.</p>
          <div className={styles.resultActions}>
            <Link className={`${styles.link} ${styles.linkAsButton}`} to="/restablecer-2fa">
              Solicitar un nuevo enlace
            </Link>
          </div>
        </div>
      )}
    </AuthLayout>
  )
}
