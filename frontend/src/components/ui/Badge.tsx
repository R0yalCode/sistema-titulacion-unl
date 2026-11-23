import type { ReactNode } from 'react'
import { AlertCircleIcon, CheckCircleIcon, CircleIcon, ClockIcon, XCircleIcon } from './icons'
import styles from './Badge.module.css'

export type BadgeVariant = 'neutral' | 'info' | 'warning' | 'success' | 'danger'

export type BadgeProps = {
  variant?: BadgeVariant
  children: ReactNode
  /** Añade el icono del tono: el estado no depende solo del color (WCAG 1.4.1). */
  icon?: boolean
}

const ICONO: Record<BadgeVariant, ReactNode> = {
  neutral: <CircleIcon size={12} />,
  info: <ClockIcon size={12} />,
  warning: <AlertCircleIcon size={12} />,
  success: <CheckCircleIcon size={12} />,
  danger: <XCircleIcon size={12} />,
}

export function Badge({ variant = 'neutral', children, icon = false }: BadgeProps) {
  return (
    <span className={[styles.badge, styles[variant]].join(' ')}>
      {icon && <span className={styles.icon}>{ICONO[variant]}</span>}
      {children}
    </span>
  )
}
