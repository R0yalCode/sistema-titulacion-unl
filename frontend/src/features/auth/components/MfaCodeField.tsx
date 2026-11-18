import { Input } from '@/components/ui/Input'
import styles from './authForm.module.css'

export const MFA_CODE_LENGTH = 6

type MfaCodeFieldProps = {
  id: string
  value: string
  error?: string
  disabled?: boolean
  onChange: (value: string) => void
}

/** Campo del código de 6 dígitos de Google Authenticator. */
export function MfaCodeField({ id, value, error, disabled, onChange }: MfaCodeFieldProps) {
  return (
    <Input
      autoComplete="one-time-code"
      className={`${styles.field} ${styles.codeInput}`}
      disabled={disabled}
      error={error}
      id={id}
      inputMode="numeric"
      label="Código de 6 dígitos de su aplicación de autenticación"
      maxLength={MFA_CODE_LENGTH}
      name="code"
      pattern="[0-9]*"
      required
      size="lg"
      value={value}
      onChange={(event) => onChange(event.target.value.replace(/\D/g, '').slice(0, MFA_CODE_LENGTH))}
    />
  )
}

export function validateMfaCode(code: string): string | undefined {
  return code.length === MFA_CODE_LENGTH ? undefined : 'Ingrese los 6 dígitos del código.'
}
