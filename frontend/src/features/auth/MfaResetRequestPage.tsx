import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { requestMfaReset } from '@/api/endpoints/auth'
import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { describeTransportError } from './authErrors'
import { AuthLayout } from './components/AuthLayout'
import { CheckCircleIcon } from './components/icons'
import { PasswordField } from './components/PasswordField'
import styles from './components/authForm.module.css'
import {
  EMAIL_MAX_LENGTH,
  INSTITUTIONAL_EMAIL_MESSAGE,
  PASSWORD_MAX_LENGTH,
  isInstitutionalEmail,
  normalizeInstitutionalEmail,
} from './validation'

const EMAIL_ID = 'mfa-reset-email'
const CEDULA_ID = 'mfa-reset-cedula'
const PASSWORD_ID = 'mfa-reset-password'

type Errors = { email?: string; cedula?: string; password?: string }

function validate(email: string, cedula: string, password: string): Errors {
  return {
    email: !email.trim()
      ? 'El correo institucional es un campo requerido.'
      : isInstitutionalEmail(email)
        ? undefined
        : INSTITUTIONAL_EMAIL_MESSAGE,
    cedula: !cedula.trim()
      ? 'El número de cédula es un campo requerido.'
      : /^\d{10}$/.test(cedula.trim())
        ? undefined
        : 'Ingrese los 10 dígitos de su cédula.',
    password: password ? undefined : 'La contraseña es un campo requerido.',
  }
}

/**
 * Restablecimiento del doble factor (referencia
 * `restablecer_doble_factor.png`). Correo, cédula y contraseña solo permiten
 * solicitar un enlace de un solo uso al correo registrado; el 2FA se retira
 * al confirmar ese enlace. La respuesta es la misma exista o no la cuenta.
 */
export default function MfaResetRequestPage() {
  const [email, setEmail] = useState('')
  const [cedula, setCedula] = useState('')
  const [password, setPassword] = useState('')
  const [errors, setErrors] = useState<Errors>({})
  const [attempted, setAttempted] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [serverError, setServerError] = useState<string | null>(null)
  const [sentMessage, setSentMessage] = useState<string | null>(null)

  function revalidate(next: { email?: string; cedula?: string; password?: string }) {
    if (!attempted) return
    const merged = { email, cedula, password, ...next }
    setErrors(validate(merged.email, merged.cedula, merged.password))
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (submitting) return
    setAttempted(true)
    const found = validate(email, cedula, password)
    setErrors(found)
    const firstInvalid = found.email ? EMAIL_ID : found.cedula ? CEDULA_ID : found.password ? PASSWORD_ID : null
    if (firstInvalid) {
      document.getElementById(firstInvalid)?.focus()
      return
    }
    setSubmitting(true)
    setServerError(null)
    try {
      const response = await requestMfaReset({
        email: normalizeInstitutionalEmail(email),
        cedula: cedula.trim(),
        password,
      })
      setPassword('')
      setSentMessage(response.detail)
    } catch (error) {
      setServerError(describeTransportError(error) ?? 'No se pudo procesar la solicitud. Intente nuevamente.')
    } finally {
      setSubmitting(false)
    }
  }

  const footnote = 'Por seguridad, el enlace enviado a su correo tiene vigencia limitada y solo puede usarse una vez.'

  if (sentMessage) {
    return (
      <AuthLayout
        description="Valide su identidad para restablecer el dispositivo de autenticación vinculado a su cuenta institucional."
        footnote={footnote}
        title="Restablecimiento de doble factor de autenticación (2FA)"
        titleStyle="panel"
      >
        <div className={styles.result}>
          <span aria-hidden="true" className={`${styles.resultIcon} ${styles.resultInfo}`}>
            <CheckCircleIcon />
          </span>
          <p className={styles.resultTitle} role="status">
            Revise su correo
          </p>
          <p className={styles.resultText}>{sentMessage}</p>
          <div className={styles.resultActions}>
            <Link className={`${styles.link} ${styles.linkAsButton}`} to="/login">
              Regresar al inicio
            </Link>
          </div>
        </div>
      </AuthLayout>
    )
  }

  return (
    <AuthLayout
      description="Valide su identidad para restablecer el dispositivo de autenticación vinculado a su cuenta institucional."
      footnote={footnote}
      title="Restablecimiento de doble factor de autenticación (2FA)"
      titleStyle="panel"
    >
      <form className={styles.form} noValidate onSubmit={handleSubmit}>
        <Input
          autoCapitalize="none"
          autoComplete="username"
          className={styles.field}
          disabled={submitting}
          error={errors.email}
          hint="Use su correo institucional (ejemplo: usuario@unl.edu.ec)."
          id={EMAIL_ID}
          inputMode="email"
          label="Correo institucional"
          maxLength={EMAIL_MAX_LENGTH}
          placeholder="usuario@unl.edu.ec"
          required
          size="lg"
          spellCheck={false}
          type="email"
          value={email}
          onChange={(event) => {
            setEmail(event.target.value)
            revalidate({ email: event.target.value })
          }}
        />
        <Input
          autoComplete="off"
          className={styles.field}
          disabled={submitting}
          error={errors.cedula}
          id={CEDULA_ID}
          inputMode="numeric"
          label="Número de cédula"
          maxLength={10}
          placeholder="1104XXXXXX"
          required
          size="lg"
          value={cedula}
          onChange={(event) => {
            const value = event.target.value.replace(/\D/g, '')
            setCedula(value)
            revalidate({ cedula: value })
          }}
        />
        <PasswordField
          autoComplete="current-password"
          className={styles.field}
          disabled={submitting}
          error={errors.password}
          id={PASSWORD_ID}
          label="Contraseña actual"
          maxLength={PASSWORD_MAX_LENGTH}
          placeholder="Ingrese su contraseña actual"
          required
          value={password}
          onChange={(event) => {
            setPassword(event.target.value)
            revalidate({ password: event.target.value })
          }}
        />

        {serverError && <Alert variant="danger">{serverError}</Alert>}

        <Button className={styles.submit} disabled={submitting} loading={submitting} size="lg" type="submit">
          Restablecer el doble factor de autenticación (2FA)
        </Button>
        <Link className={`${styles.link} ${styles.secondaryButton}`} to="/recuperar-contrasena">
          Restablecer contraseña
        </Link>
        <div className={styles.links}>
          <Link className={styles.link} to="/login">
            Regresar al inicio
          </Link>
        </div>
      </form>
    </AuthLayout>
  )
}
