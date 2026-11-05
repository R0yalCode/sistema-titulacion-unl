import { useId, type InputHTMLAttributes } from 'react'
import styles from './Checkbox.module.css'

export type CheckboxProps = Omit<InputHTMLAttributes<HTMLInputElement>, 'id' | 'type'> & {
  label: string
  id?: string
  error?: string
}

export function Checkbox({ label, id, error, className, ...rest }: CheckboxProps) {
  const generatedId = useId()
  const inputId = id ?? generatedId
  const errorId = error ? `${inputId}-error` : undefined

  return (
    <div className={styles.field}>
      <div className={styles.row}>
        <input
          aria-describedby={errorId}
          aria-invalid={error ? true : undefined}
          className={[styles.control, className].filter(Boolean).join(' ')}
          id={inputId}
          type="checkbox"
          {...rest}
        />
        <label className={styles.label} htmlFor={inputId}>
          {label}
        </label>
      </div>
      {error && (
        <p className={styles.error} id={errorId} role="alert">
          {error}
        </p>
      )}
    </div>
  )
}
