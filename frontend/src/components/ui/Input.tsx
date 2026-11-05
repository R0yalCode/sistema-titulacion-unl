import { useId, type InputHTMLAttributes } from 'react'
import styles from './Input.module.css'

export type InputSize = 'sm' | 'md' | 'lg'

export type InputProps = Omit<InputHTMLAttributes<HTMLInputElement>, 'id' | 'size'> & {
  label: string
  id?: string
  error?: string
  hint?: string
  size?: InputSize
}

export function Input({
  label,
  id,
  error,
  hint,
  size = 'md',
  required,
  className,
  ...rest
}: InputProps) {
  const generatedId = useId()
  const inputId = id ?? generatedId
  const hintId = hint ? `${inputId}-hint` : undefined
  const errorId = error ? `${inputId}-error` : undefined
  const describedBy = [hintId, errorId].filter(Boolean).join(' ') || undefined

  return (
    <div className={styles.field}>
      <label className={styles.label} htmlFor={inputId}>
        {label}
        {required && <span aria-hidden="true"> *</span>}
      </label>
      {hint && (
        <p className={styles.hint} id={hintId}>
          {hint}
        </p>
      )}
      <input
        aria-describedby={describedBy}
        aria-invalid={error ? true : undefined}
        className={[styles.input, styles[size], error && styles.inputError, className]
          .filter(Boolean)
          .join(' ')}
        id={inputId}
        required={required}
        {...rest}
      />
      {error && (
        <p className={styles.error} id={errorId} role="alert">
          {error}
        </p>
      )}
    </div>
  )
}
