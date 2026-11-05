import type { ReactNode } from 'react'
import styles from './Badge.module.css'

export type BadgeVariant = 'neutral' | 'info' | 'warning' | 'success' | 'danger'

export type BadgeProps = {
  variant?: BadgeVariant
  children: ReactNode
}

export function Badge({ variant = 'neutral', children }: BadgeProps) {
  return <span className={[styles.badge, styles[variant]].join(' ')}>{children}</span>
}
