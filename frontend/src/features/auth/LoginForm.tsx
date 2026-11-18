import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { LockIcon, ShieldIcon } from './components/icons'
import { PasswordField } from './components/PasswordField'
import styles from './components/authForm.module.css'
import {
  EMAIL_MAX_LENGTH,
  PASSWORD_MAX_LENGTH,
  normalizeInstitutionalEmail,
  validateInstitutionalUsername,
  validateRequiredPassword,
} from './validation'

const USERNAME_FIELD_ID = 'login-username'
const PASSWORD_FIELD_ID = 'login-password'

export type LoginFormValues = {
  /** Correo institucional normalizado (@unl.edu.ec). */
  email: string
  password: string
}

export type LoginFormProps = {
  submitting: boolean
  serverError: string | null
  onSubmit: (values: LoginFormValues) => Promise<boolean>
}

type FieldErrors = {
  username?: string
  password?: string
}

/**
 * Formulario de acceso con la estructura del SAC: el campo se llama «Nombre
 * de usuario» pero recibe el correo institucional. Los errores aparecen
 * debajo de cada campo solo después de intentar ingresar, y se retiran en
 * cuanto el valor corregido es válido.
 */
export function LoginForm({ submitting, serverError, onSubmit }: LoginFormProps) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({})
  const [attempted, setAttempted] = useState(false)

  function changeUsername(value: string) {
    setUsername(value)
    if (attempted) {
      setFieldErrors((current) => ({ ...current, username: validateInstitutionalUsername(value) }))
    }
  }

  function changePassword(value: string) {
    setPassword(value)
    if (attempted) {
      setFieldErrors((current) => ({ ...current, password: validateRequiredPassword(value) }))
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (submitting) {
      return
    }

    setAttempted(true)
    const errors: FieldErrors = {
      username: validateInstitutionalUsername(username),
      password: validateRequiredPassword(password),
    }
    setFieldErrors(errors)

    if (errors.username) {
      document.getElementById(USERNAME_FIELD_ID)?.focus()
      return
    }
    if (errors.password) {
      document.getElementById(PASSWORD_FIELD_ID)?.focus()
      return
    }

    const ok = await onSubmit({ email: normalizeInstitutionalEmail(username), password })
    if (!ok) {
      setPassword('')
      document.getElementById(PASSWORD_FIELD_ID)?.focus()
    }
  }

  return (
    <form className={styles.form} noValidate onSubmit={handleSubmit}>
      <Input
        autoCapitalize="none"
        autoComplete="username"
        autoCorrect="off"
        className={styles.field}
        disabled={submitting}
        error={fieldErrors.username}
        id={USERNAME_FIELD_ID}
        inputMode="email"
        label="Nombre de usuario"
        maxLength={EMAIL_MAX_LENGTH}
        name="username"
        placeholder="usuario@unl.edu.ec"
        required
        size="lg"
        spellCheck={false}
        type="email"
        value={username}
        onChange={(event) => changeUsername(event.target.value)}
      />

      <PasswordField
        autoComplete="current-password"
        className={styles.field}
        disabled={submitting}
        error={fieldErrors.password}
        id={PASSWORD_FIELD_ID}
        label="Contraseña"
        maxLength={PASSWORD_MAX_LENGTH}
        name="password"
        required
        value={password}
        onChange={(event) => changePassword(event.target.value)}
      />

      {serverError && <Alert variant="danger">{serverError}</Alert>}

      <Button className={styles.submit} disabled={submitting} loading={submitting} size="lg" type="submit">
        Iniciar sesión
      </Button>

      <div className={styles.links}>
        <Link className={styles.sacLink} to="/recuperar-contrasena">
          <LockIcon />
          Restablecer contraseña
        </Link>
        <Link className={styles.sacLink} to="/restablecer-2fa">
          <ShieldIcon />
          Restablecer doble factor de autenticación (2FA)
        </Link>
      </div>
    </form>
  )
}
