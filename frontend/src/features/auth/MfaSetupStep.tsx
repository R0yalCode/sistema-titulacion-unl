import { useEffect, useRef, useState, type FormEvent } from 'react'
import { confirmMfaSetup, startMfaSetup, type AuthResult, type MfaSetup } from '@/api/endpoints/auth'
import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { Checkbox } from '@/components/ui/Checkbox'
import { Spinner } from '@/components/ui/Spinner'
import { describeMfaError, isMfaRestartError } from './authErrors'
import { MfaCodeField, validateMfaCode } from './components/MfaCodeField'
import styles from './components/authForm.module.css'

const CODE_FIELD_ID = 'mfa-setup-code'

type MfaSetupStepProps = {
  challenge: string
  onResult: (result: AuthResult) => void
  onRestart: (message: string) => void
  onCancel: () => void
}

/**
 * Registro de Google Authenticator: el backend genera el secreto y el QR; el
 * secreto nunca se guarda en el navegador. El primer código válido activa el
 * segundo factor.
 */
export function MfaSetupStep({ challenge, onResult, onRestart, onCancel }: MfaSetupStepProps) {
  const [setup, setSetup] = useState<MfaSetup | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [attempt, setAttempt] = useState(0)
  const [code, setCode] = useState('')
  const [trustDevice, setTrustDevice] = useState(false)
  const [fieldError, setFieldError] = useState<string | undefined>()
  const [serverError, setServerError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  // Una sola petición por reto e intento: cada llamada regenera el secreto,
  // así que una segunda (p. ej. el doble efecto de StrictMode) invalidaría el
  // QR ya mostrado.
  const requests = useRef(new Map<string, Promise<MfaSetup>>())

  useEffect(() => {
    let active = true
    const key = `${challenge}:${attempt}`
    let pending = requests.current.get(key)
    if (!pending) {
      pending = startMfaSetup(challenge)
      requests.current.set(key, pending)
    }
    pending.then(
      (data) => {
        if (active) {
          setSetup(data)
          setLoadError(null)
        }
      },
      (error: unknown) => {
        if (!active) return
        if (isMfaRestartError(error)) {
          onRestart(describeMfaError(error))
        } else {
          setLoadError(describeMfaError(error))
        }
      },
    )
    return () => {
      active = false
    }
  }, [challenge, attempt, onRestart])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (submitting) return
    const error = validateMfaCode(code)
    setFieldError(error)
    if (error) {
      document.getElementById(CODE_FIELD_ID)?.focus()
      return
    }
    setSubmitting(true)
    setServerError(null)
    try {
      onResult(await confirmMfaSetup({ challenge, code, trustDevice }))
    } catch (err) {
      if (isMfaRestartError(err)) {
        onRestart(describeMfaError(err))
        return
      }
      setServerError(describeMfaError(err))
      setCode('')
      document.getElementById(CODE_FIELD_ID)?.focus()
    } finally {
      setSubmitting(false)
    }
  }

  if (loadError) {
    return (
      <div className={styles.form}>
        <Alert variant="danger">{loadError}</Alert>
        <Button className={styles.submit} size="lg" onClick={() => setAttempt((n) => n + 1)}>
          Reintentar
        </Button>
        <Button variant="ghost" onClick={onCancel}>
          Cancelar
        </Button>
      </div>
    )
  }

  if (!setup) {
    return (
      <div className={styles.result}>
        <Spinner label="Preparando el código QR…" />
      </div>
    )
  }

  return (
    <form className={styles.form} noValidate onSubmit={handleSubmit}>
      <p className={styles.intro}>
        Su cuenta requiere verificación en dos pasos. Configúrela una sola vez con Google Authenticator.
      </p>
      <ol className={styles.steps}>
        <li>Instale Google Authenticator en su teléfono.</li>
        <li>Toque «+» y elija «Escanear un código QR».</li>
        <li>Escanee este código e ingrese abajo los 6 dígitos que muestra la aplicación.</li>
      </ol>

      <img
        alt={`Código QR para registrar ${setup.account} en Google Authenticator`}
        className={styles.qr}
        height={220}
        src={setup.qr_svg}
        width={220}
      />

      <details className={styles.manualKey}>
        <summary>¿No puede escanear el código?</summary>
        <p className={styles.intro}>
          En la aplicación elija «Ingresar una clave de configuración», use el nombre <strong>{setup.issuer}</strong> y
          esta clave (basada en el tiempo):
        </p>
        <code className={styles.secret}>{setup.manual_key}</code>
      </details>

      <MfaCodeField
        disabled={submitting}
        error={fieldError}
        id={CODE_FIELD_ID}
        value={code}
        onChange={setCode}
      />
      <Checkbox
        checked={trustDevice}
        disabled={submitting}
        label="Confiar en este dispositivo durante 5 días"
        onChange={(event) => setTrustDevice(event.target.checked)}
      />

      {serverError && <Alert variant="danger">{serverError}</Alert>}

      <Button className={styles.submit} loading={submitting} size="lg" type="submit">
        Verificar y activar
      </Button>
      <Button disabled={submitting} variant="ghost" onClick={onCancel}>
        Cancelar
      </Button>
    </form>
  )
}
