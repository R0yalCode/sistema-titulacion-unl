import { useId, type TextareaHTMLAttributes } from 'react'
import styles from './Input.module.css'

export type TextareaProps = Omit<TextareaHTMLAttributes<HTMLTextAreaElement>, 'id'> & {
  label: string
  id?: string
  error?: string
  hint?: string
}

export function Textarea({ label, id, error, hint, required, className, ...rest }: TextareaProps) {
  const generatedId = useId()
  const textareaId = id ?? generatedId
  const hintId = hint ? `${textareaId}-hint` : undefined
  const errorId = error ? `${textareaId}-error` : undefined
  const describedBy = [hintId, errorId].filter(Boolean).join(' ') || undefined

  return (
    <div className={styles.field}>
      <label className={styles.label} htmlFor={textareaId}>
        {label}
        {required && <span aria-hidden="true"> *</span>}
      </label>
      {hint && (
        <p className={styles.hint} id={hintId}>
          {hint}
        </p>
      )}
      <textarea
        aria-describedby={describedBy}
        aria-invalid={error ? true : undefined}
        className={[styles.input, styles.md, error && styles.inputError, className]
          .filter(Boolean)
          .join(' ')}
        id={textareaId}
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
