import { useState, type FormEvent } from 'react'
import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { PasswordField } from './components/PasswordField'
import { PasswordRules } from './components/PasswordRules'
import styles from './components/authForm.module.css'
import {
  PASSWORD_MAX_LENGTH,
  evaluatePasswordRules,
  validateNewPassword,
  validatePasswordConfirmation,
} from './validation'

const PASSWORD_FIELD_ID = 'restablecer-nueva'
const CONFIRMATION_FIELD_ID = 'restablecer-confirmacion'
const RULES_ID = 'restablecer-requisitos'

export type ResetPasswordFormProps = {
  submitting: boolean
  serverError: string | null
  /** Rechazos de la política de contraseñas devueltos por el backend. */
  passwordErrors: string[]
  onSubmit: (newPassword: string) => Promise<boolean>
}

export function ResetPasswordForm({ submitting, serverError, passwordErrors, onSubmit }: ResetPasswordFormProps) {
  const [password, setPassword] = useState('')
  const [confirmation, setConfirmation] = useState('')
  const [errors, setErrors] = useState<{ password?: string; confirmation?: string }>({})
  const [edited, setEdited] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (submitting) {
      return
    }

    const nextErrors = {
      password: validateNewPassword(password),
      confirmation: validatePasswordConfirmation(password, confirmation),
    }
    setErrors(nextErrors)

    if (nextErrors.password) {
      document.getElementById(PASSWORD_FIELD_ID)?.focus()
      return
    }
    if (nextErrors.confirmation) {
      document.getElementById(CONFIRMATION_FIELD_ID)?.focus()
      return
    }

    setEdited(false)
    const ok = await onSubmit(password)
    if (!ok) {
      document.getElementById(PASSWORD_FIELD_ID)?.focus()
    }
  }

  // Los rechazos del backend se muestran hasta que el usuario edita el campo.
  const backendPasswordError = !edited && passwordErrors.length > 0 ? passwordErrors.join(' ') : undefined

  return (
    <form className={styles.form} noValidate onSubmit={handleSubmit}>
      <p className={styles.intro}>Defina una nueva contraseña para su cuenta.</p>

      <PasswordField
        aria-describedby={RULES_ID}
        autoComplete="new-password"
        className={styles.field}
        disabled={submitting}
        error={errors.password ?? backendPasswordError}
        id={PASSWORD_FIELD_ID}
        label="Nueva contraseña"
        maxLength={PASSWORD_MAX_LENGTH}
        name="new-password"
        required
        value={password}
        onChange={(event) => {
          setPassword(event.target.value)
          setEdited(true)
        }}
      />

      <PasswordRules id={RULES_ID} rules={evaluatePasswordRules(password)} />

      <PasswordField
        autoComplete="new-password"
        className={styles.field}
        disabled={submitting}
        error={errors.confirmation}
        id={CONFIRMATION_FIELD_ID}
        label="Confirmar contraseña"
        maxLength={PASSWORD_MAX_LENGTH}
        name="confirm-password"
        required
        value={confirmation}
        onChange={(event) => setConfirmation(event.target.value)}
      />

      {serverError && <Alert variant="danger">{serverError}</Alert>}

      <Button className={styles.submit} loading={submitting} size="lg" type="submit">
        Restablecer contraseña
      </Button>
    </form>
  )
}
