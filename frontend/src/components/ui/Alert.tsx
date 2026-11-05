import type { ReactNode } from 'react'
import styles from './Alert.module.css'

export type AlertVariant = 'info' | 'success' | 'warning' | 'danger'

export type AlertProps = {
  variant?: AlertVariant
  title?: string
  children: ReactNode
}

const CRITICAL_VARIANTS: AlertVariant[] = ['warning', 'danger']

export function Alert({ variant = 'info', title, children }: AlertProps) {
  const isCritical = CRITICAL_VARIANTS.includes(variant)

  return (
    <div
      aria-live={isCritical ? 'assertive' : 'polite'}
      className={[styles.alert, styles[variant]].join(' ')}
      role={isCritical ? 'alert' : 'status'}
    >
      {title && <p className={styles.title}>{title}</p>}
      <div>{children}</div>
    </div>
  )
}
