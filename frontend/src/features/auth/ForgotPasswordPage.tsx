import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { requestPasswordReset } from '@/api/endpoints/auth'
import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { describeTransportError } from './authErrors'
import { AuthLayout } from './components/AuthLayout'
import { ArrowLeftIcon, MailIcon } from '@/components/ui/icons'
import styles from './components/authForm.module.css'
import { EMAIL_MAX_LENGTH, validateEmail } from './validation'

const EMAIL_FIELD_ID = 'recuperar-email'

function BackToLoginLink() {
  return (
    <Link className={styles.link} to="/login">
      <ArrowLeftIcon />
      Volver al ingreso
    </Link>
  )
}

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [fieldError, setFieldError] = useState<string | undefined>()
  const [serverError, setServerError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [sent, setSent] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (submitting) {
      return
    }

    const error = validateEmail(email)
    setFieldError(error)
    setServerError(null)
    if (error) {
      document.getElementById(EMAIL_FIELD_ID)?.focus()
      return
    }

    setSubmitting(true)
    try {
      await requestPasswordReset(email.trim())
      setSent(true)
    } catch (requestError) {
      setServerError(
        describeTransportError(requestError) ?? 'No se pudo procesar la solicitud. Intente nuevamente.',
      )
    } finally {
      setSubmitting(false)
    }
  }

  if (sent) {
    // Mismo texto exista o no la cuenta: no se revela si el correo está registrado.
    return (
      <AuthLayout title="Revise su correo">
        <div className={styles.result} role="status">
          <span className={[styles.resultIcon, styles.resultInfo].join(' ')}>
            <MailIcon />
          </span>
          <p className={styles.resultText}>
            Si existe una cuenta asociada al correo indicado, recibirá un mensaje con las instrucciones para
            restablecer su contraseña.
          </p>
          <p className={styles.resultText}>
            El enlace tiene una vigencia limitada. Si no encuentra el mensaje, revise la carpeta de correo no
            deseado.
          </p>
          <div className={styles.links}>
            <BackToLoginLink />
          </div>
        </div>
      </AuthLayout>
    )
  }

  return (
    <AuthLayout title="Recuperar contraseña">
      <form className={styles.form} noValidate onSubmit={handleSubmit}>
        <p className={styles.intro}>
          Ingrese el correo electrónico institucional asociado a su cuenta y le enviaremos las instrucciones para
          restablecer su contraseña.
        </p>

        <Input
          autoCapitalize="none"
          autoComplete="email"
          className={styles.field}
          disabled={submitting}
          error={fieldError}
          id={EMAIL_FIELD_ID}
          inputMode="email"
          label="Correo electrónico institucional"
          maxLength={EMAIL_MAX_LENGTH}
          name="email"
          required
          size="lg"
          spellCheck={false}
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
        />

        {serverError && <Alert variant="danger">{serverError}</Alert>}

        <Button className={styles.submit} loading={submitting} size="lg" type="submit">
          Enviar instrucciones
        </Button>

        <div className={styles.links}>
          <BackToLoginLink />
        </div>
      </form>
    </AuthLayout>
  )
}
