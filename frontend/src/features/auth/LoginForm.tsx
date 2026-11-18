import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { LockIcon } from './components/icons'
import { PasswordField } from './components/PasswordField'
import styles from './components/authForm.module.css'
import { PASSWORD_MAX_LENGTH, USERNAME_MAX_LENGTH, validateUsername } from './validation'

const USERNAME_FIELD_ID = 'login-username'
const PASSWORD_FIELD_ID = 'login-password'

export type LoginFormValues = {
  username: string
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

export function LoginForm({ submitting, serverError, onSubmit }: LoginFormProps) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({})

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (submitting) {
      return
    }

    const trimmedUsername = username.trim()
    const errors: FieldErrors = {
      username: validateUsername(username),
      password: password ? undefined : 'Ingrese su contraseña.',
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

    const ok = await onSubmit({ username: trimmedUsername, password })
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
        label="Usuario"
        maxLength={USERNAME_MAX_LENGTH}
        name="username"
        required
        size="lg"
        spellCheck={false}
        value={username}
        onChange={(event) => setUsername(event.target.value)}
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
        onChange={(event) => setPassword(event.target.value)}
      />

      {serverError && <Alert variant="danger">{serverError}</Alert>}

      <Button className={styles.submit} loading={submitting} size="lg" type="submit">
        Ingresar
      </Button>

      <div className={styles.links}>
        <Link className={styles.link} to="/recuperar-contrasena">
          <LockIcon />
          ¿Olvidaste tu contraseña?
        </Link>
      </div>
    </form>
  )
}
