import styles from './Spinner.module.css'

export type SpinnerSize = 'sm' | 'md' | 'lg'

export type SpinnerProps = {
  size?: SpinnerSize
  label?: string
}

export function Spinner({ size = 'md', label = 'Cargando…' }: SpinnerProps) {
  return (
    <span className={styles.wrapper} role="status">
      <span aria-hidden="true" className={[styles.spinner, styles[size]].join(' ')} />
      <span className="sr-only">{label}</span>
    </span>
  )
}
