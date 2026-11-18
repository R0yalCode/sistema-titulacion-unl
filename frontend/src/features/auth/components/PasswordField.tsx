import { useState } from 'react'
import { Input, type InputProps } from '@/components/ui/Input'
import { EyeIcon, EyeOffIcon } from './icons'
import styles from './PasswordField.module.css'

export type PasswordFieldProps = Omit<InputProps, 'type' | 'size'>

/** Campo de contraseña con botón para mostrarla u ocultarla. */
export function PasswordField({ disabled, className, ...rest }: PasswordFieldProps) {
  const [visible, setVisible] = useState(false)

  return (
    <div className={styles.wrapper}>
      <Input
        className={[styles.input, className].filter(Boolean).join(' ')}
        disabled={disabled}
        size="lg"
        type={visible ? 'text' : 'password'}
        {...rest}
      />
      <button
        aria-label={visible ? 'Ocultar contraseña' : 'Mostrar contraseña'}
        aria-pressed={visible}
        className={styles.toggle}
        disabled={disabled}
        type="button"
        onClick={() => setVisible((current) => !current)}
      >
        {visible ? <EyeOffIcon /> : <EyeIcon />}
      </button>
    </div>
  )
}
