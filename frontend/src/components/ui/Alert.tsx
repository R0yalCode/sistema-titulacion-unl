import type { ReactNode } from 'react'
import { AlertCircleIcon, CheckCircleIcon, InfoIcon, XCircleIcon } from './icons'
import styles from './Alert.module.css'

export type AlertVariant = 'info' | 'success' | 'warning' | 'danger'

export type AlertProps = {
  variant?: AlertVariant
  title?: string
  children: ReactNode
}

const CRITICAL_VARIANTS: AlertVariant[] = ['warning', 'danger']

const ICONO: Record<AlertVariant, ReactNode> = {
  info: <InfoIcon size={20} />,
  success: <CheckCircleIcon size={20} />,
  warning: <AlertCircleIcon size={20} />,
  danger: <XCircleIcon size={20} />,
}

export function Alert({ variant = 'info', title, children }: AlertProps) {
  const isCritical = CRITICAL_VARIANTS.includes(variant)

  return (
    <div
      aria-live={isCritical ? 'assertive' : 'polite'}
      className={[styles.alert, styles[variant]].join(' ')}
      role={isCritical ? 'alert' : 'status'}
    >
      <span aria-hidden="true" className={styles.icon}>
        {ICONO[variant]}
      </span>
      <div className={styles.body}>
        {title && <p className={styles.title}>{title}</p>}
        <div>{children}</div>
      </div>
    </div>
  )
}
