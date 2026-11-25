import { useEffect, useId, useRef, type ReactNode } from 'react'
import { Button } from '@/components/ui/Button'
import { ERROR_CATALOG, type ErrorKind } from './errorCatalog'
import styles from './ErrorView.module.css'

export type ErrorAction = {
  /** Por defecto, la etiqueta del catálogo. */
  label?: string
  onClick?: () => void
  /** Enlace de documento completo (sin router, p. ej. desde el ErrorBoundary). */
  href?: string
  disabled?: boolean
  loading?: boolean
}

export type ErrorViewProps = {
  kind: ErrorKind
  /** `page`: vista completa con `h1` y foco inicial; `inline`: dentro de un layout. */
  variant?: 'page' | 'inline'
  /** Sustituye el título del catálogo cuando el contexto lo precisa (p. ej. «Expediente no encontrado»). */
  title?: string
  message?: string
  /** Mensaje real del backend, si existe (ver `backendDetail`). */
  detail?: string | null
  primaryAction?: ErrorAction
  secondaryAction?: ErrorAction
  /** Estado vivo (conexión, espera del siguiente intento). */
  status?: ReactNode
  className?: string
}

function ActionControl({ action, fallbackLabel, variant }: { action: ErrorAction; fallbackLabel: string; variant: 'primary' | 'secondary' }) {
  const label = action.label ?? fallbackLabel
  if (action.href) {
    return (
      <a className={`${styles.linkButton} ${styles[variant]}`} href={action.href}>
        {label}
      </a>
    )
  }
  return (
    <Button
      className={styles.action}
      disabled={action.disabled}
      loading={action.loading}
      variant={variant}
      onClick={action.onClick}
    >
      {label}
    </Button>
  )
}

/**
 * Vista única del sistema de errores. Las ocho variantes comparten estructura,
 * estilos y accesibilidad; solo cambian los datos de `ERROR_CATALOG`.
 *
 * Accesibilidad: la mascota es decorativa (`alt=""`): el texto da el
 * significado. En `page` el título recibe el foco al montarse para que los
 * lectores de pantalla anuncien el cambio; en `inline` el contenedor es una
 * región viva (`alert`, o `status` para 403, que no es una falla).
 */
export function ErrorView({
  kind,
  variant = 'inline',
  title,
  message,
  detail,
  primaryAction,
  secondaryAction,
  status,
  className,
}: ErrorViewProps) {
  const copy = ERROR_CATALOG[kind]
  const titleId = useId()
  const headingRef = useRef<HTMLHeadingElement>(null)
  const Heading = variant === 'page' ? 'h1' : 'h2'

  useEffect(() => {
    if (variant === 'page') {
      headingRef.current?.focus()
    }
  }, [variant, kind])

  const role = variant === 'inline' ? (kind === 'forbidden' ? 'status' : 'alert') : undefined

  return (
    <section
      aria-labelledby={titleId}
      className={[styles.view, styles[variant], className].filter(Boolean).join(' ')}
      data-kind={kind}
      data-variant={variant}
      role={role}
    >
      <div aria-hidden="true" className={styles.art}>
        {copy.code && <span className={styles.code}>{copy.code}</span>}
        <img alt="" className={styles.mascot} decoding="async" src={copy.mascot} />
      </div>
      <div className={styles.body}>
        <p className={styles.eyebrow}>{copy.eyebrow}</p>
        <Heading className={styles.title} id={titleId} ref={headingRef} tabIndex={variant === 'page' ? -1 : undefined}>
          {title ?? copy.title}
        </Heading>
        <p className={styles.message}>{message ?? copy.message}</p>
        {detail && (
          <p className={styles.detail}>
            <span className={styles.detailLabel}>Detalle del sistema:</span> {detail}
          </p>
        )}
        {status && (
          <div aria-live="polite" className={styles.status}>
            {status}
          </div>
        )}
        {(primaryAction || secondaryAction) && (
          <div className={styles.actions}>
            {primaryAction && <ActionControl action={primaryAction} fallbackLabel={copy.primaryLabel} variant="primary" />}
            {secondaryAction && (
              <ActionControl action={secondaryAction} fallbackLabel={copy.secondaryLabel} variant="secondary" />
            )}
          </div>
        )}
      </div>
    </section>
  )
}
