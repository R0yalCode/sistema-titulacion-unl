import { useState, type FormEvent } from 'react'
import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import styles from './LoginForm.module.css'

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
  const [showPassword, setShowPassword] = useState(false)
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({})

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (submitting) {
      return
    }

    const trimmedUsername = username.trim()
    const errors: FieldErrors = {}
    if (!trimmedUsername) {
      errors.username = 'Ingrese su usuario.'
    }
    if (!password) {
      errors.password = 'Ingrese su contraseña.'
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
        autoComplete="username"
        disabled={submitting}
        error={fieldErrors.username}
        id={USERNAME_FIELD_ID}
        label="Usuario"
        name="username"
        required
        value={username}
        onChange={(event) => setUsername(event.target.value)}
      />

      <div className={styles.passwordField}>
        <Input
          autoComplete="current-password"
          disabled={submitting}
          error={fieldErrors.password}
          id={PASSWORD_FIELD_ID}
          label="Contraseña"
          name="password"
          required
          type={showPassword ? 'text' : 'password'}
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />
        <button
          aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
          className={styles.toggleVisibility}
          disabled={submitting}
          type="button"
          onClick={() => setShowPassword((current) => !current)}
        >
          <span aria-hidden="true">{showPassword ? '🙈' : '👁'}</span>
        </button>
      </div>

      {serverError && <Alert variant="danger">{serverError}</Alert>}

      <Button loading={submitting} type="submit">
        Ingresar
      </Button>
    </form>
  )
}
