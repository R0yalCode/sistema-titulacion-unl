import { useState, type FormEvent } from 'react'
import { recoverMfa, verifyMfa, type AuthResult } from '@/api/endpoints/auth'
import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { Checkbox } from '@/components/ui/Checkbox'
import { Input } from '@/components/ui/Input'
import { describeMfaError, isMfaRestartError } from './authErrors'
import { MfaCodeField, validateMfaCode } from './components/MfaCodeField'
import styles from './components/authForm.module.css'

const CODE_FIELD_ID = 'mfa-verify-code'
const RECOVERY_FIELD_ID = 'mfa-recovery-code'

type MfaVerifyStepProps = {
  challenge: string
  onResult: (result: AuthResult) => void
  onRestart: (message: string) => void
  onCancel: () => void
}

/** Segundo factor en cada ingreso; incluye el uso de un código de recuperación. */
export function MfaVerifyStep({ challenge, onResult, onRestart, onCancel }: MfaVerifyStepProps) {
  const [mode, setMode] = useState<'totp' | 'recovery'>('totp')
  const [code, setCode] = useState('')
  const [recoveryCode, setRecoveryCode] = useState('')
  const [trustDevice, setTrustDevice] = useState(false)
  const [fieldError, setFieldError] = useState<string | undefined>()
  const [serverError, setServerError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function run(action: () => Promise<AuthResult>, fieldId: string, reset: () => void) {
    setSubmitting(true)
    setServerError(null)
    try {
      onResult(await action())
    } catch (err) {
      if (isMfaRestartError(err)) {
        onRestart(describeMfaError(err))
        return
      }
      setServerError(describeMfaError(err))
      reset()
      document.getElementById(fieldId)?.focus()
    } finally {
      setSubmitting(false)
    }
  }

  function handleTotp(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (submitting) return
    const error = validateMfaCode(code)
    setFieldError(error)
    if (error) {
      document.getElementById(CODE_FIELD_ID)?.focus()
      return
    }
    void run(() => verifyMfa({ challenge, code, trustDevice }), CODE_FIELD_ID, () => setCode(''))
  }

  function handleRecovery(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (submitting) return
    const normalized = recoveryCode.replace(/[^0-9a-z]/gi, '')
    const error = normalized.length === 10 ? undefined : 'Ingrese un código de recuperación de 10 caracteres.'
    setFieldError(error)
    if (error) {
      document.getElementById(RECOVERY_FIELD_ID)?.focus()
      return
    }
    void run(() => recoverMfa(challenge, recoveryCode.trim()), RECOVERY_FIELD_ID, () => setRecoveryCode(''))
  }

  function switchMode(next: 'totp' | 'recovery') {
    setMode(next)
    setFieldError(undefined)
    setServerError(null)
  }

  if (mode === 'recovery') {
    return (
      <form className={styles.form} noValidate onSubmit={handleRecovery}>
        <p className={styles.intro}>
          Si perdió su teléfono, ingrese uno de los códigos de recuperación que guardó al activar la verificación. El
          autenticador anterior quedará anulado y deberá registrar uno nuevo.
        </p>
        <Input
          autoCapitalize="characters"
          autoComplete="off"
          className={styles.field}
          disabled={submitting}
          error={fieldError}
          id={RECOVERY_FIELD_ID}
          label="Código de recuperación"
          maxLength={16}
          name="recovery_code"
          required
          size="lg"
          spellCheck={false}
          value={recoveryCode}
          onChange={(event) => setRecoveryCode(event.target.value)}
        />
        {serverError && <Alert variant="danger">{serverError}</Alert>}
        <Button className={styles.submit} loading={submitting} size="lg" type="submit">
          Usar código de recuperación
        </Button>
        <Button disabled={submitting} variant="ghost" onClick={() => switchMode('totp')}>
          Volver al código de la aplicación
        </Button>
        <p className={styles.helpText}>
          Si tampoco tiene sus códigos de recuperación, solicite a la administración del sistema el restablecimiento
          del doble factor; se verificará su identidad antes de hacerlo.
        </p>
      </form>
    )
  }

  return (
    <form className={styles.form} noValidate onSubmit={handleTotp}>
      <p className={styles.intro}>Abra Google Authenticator e ingrese el código actual de SGT-SIAAF.</p>
      <MfaCodeField disabled={submitting} error={fieldError} id={CODE_FIELD_ID} value={code} onChange={setCode} />
      <Checkbox
        checked={trustDevice}
        disabled={submitting}
        label="Confiar en este dispositivo durante 5 días"
        onChange={(event) => setTrustDevice(event.target.checked)}
      />
      {serverError && <Alert variant="danger">{serverError}</Alert>}
      <Button className={styles.submit} loading={submitting} size="lg" type="submit">
        Verificar
      </Button>
      <Button disabled={submitting} variant="ghost" onClick={onCancel}>
        Cancelar
      </Button>
      <div className={styles.links}>
        <button className={styles.link} disabled={submitting} type="button" onClick={() => switchMode('recovery')}>
          ¿Perdió su teléfono? Use un código de recuperación
        </button>
      </div>
    </form>
  )
}
