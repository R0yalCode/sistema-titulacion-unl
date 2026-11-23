import { createContext, useCallback, useMemo, useRef, useState, type ReactNode } from 'react'
import { createPortal } from 'react-dom'
import { Button } from '@/components/ui/Button'
import { AlertCircleIcon, CheckCircleIcon, CloseIcon, InfoIcon, XCircleIcon } from '@/components/ui/icons'
import styles from './ToastProvider.module.css'

export type ToastVariant = 'info' | 'success' | 'warning' | 'danger'

export type Toast = {
  id: string
  message: string
  variant: ToastVariant
}

export type ToastContextValue = {
  showToast: (message: string, variant?: ToastVariant) => void
  dismissToast: (id: string) => void
}

export const ToastContext = createContext<ToastContextValue | undefined>(undefined)

const ICONO: Record<ToastVariant, ReactNode> = {
  info: <InfoIcon size={20} />,
  success: <CheckCircleIcon size={20} />,
  warning: <AlertCircleIcon size={20} />,
  danger: <XCircleIcon size={20} />,
}

const DEFAULT_AUTO_DISMISS_MS = 5000
const CRITICAL_VARIANTS: ToastVariant[] = ['warning', 'danger']

type ToastProviderProps = {
  children: ReactNode
  autoDismissMs?: number
}

export function ToastProvider({ children, autoDismissMs = DEFAULT_AUTO_DISMISS_MS }: ToastProviderProps) {
  const [toasts, setToasts] = useState<Toast[]>([])
  const idCounter = useRef(0)
  const timers = useRef(new Map<string, ReturnType<typeof setTimeout>>())

  const dismissToast = useCallback((id: string) => {
    setToasts((current) => current.filter((toast) => toast.id !== id))
    const timer = timers.current.get(id)
    if (timer) {
      clearTimeout(timer)
      timers.current.delete(id)
    }
  }, [])

  const showToast = useCallback((message: string, variant: ToastVariant = 'info') => {
    setToasts((current) => {
      const alreadyQueued = current.some(
        (toast) => toast.message === message && toast.variant === variant,
      )
      if (alreadyQueued) {
        return current
      }

      idCounter.current += 1
      const id = `toast-${idCounter.current}`
      const timer = setTimeout(() => {
        setToasts((latest) => latest.filter((toast) => toast.id !== id))
        timers.current.delete(id)
      }, autoDismissMs)
      timers.current.set(id, timer)

      return [...current, { id, message, variant }]
    })
  }, [autoDismissMs])

  const value = useMemo<ToastContextValue>(() => ({ showToast, dismissToast }), [showToast, dismissToast])

  return (
    <ToastContext.Provider value={value}>
      {children}
      {createPortal(
        <div className={styles.viewport}>
          {toasts.map((toast) => (
            <div
              className={[styles.toast, styles[toast.variant]].join(' ')}
              key={toast.id}
              role={CRITICAL_VARIANTS.includes(toast.variant) ? 'alert' : 'status'}
            >
              <span aria-hidden="true" className={styles.icon}>
                {ICONO[toast.variant]}
              </span>
              <span className={styles.message}>{toast.message}</span>
              <Button
                aria-label="Cerrar notificación"
                onClick={() => dismissToast(toast.id)}
                size="sm"
                variant="ghost"
                className={styles.close}
              >
                <CloseIcon size={16} />
              </Button>
            </div>
          ))}
        </div>,
        document.body,
      )}
    </ToastContext.Provider>
  )
}
