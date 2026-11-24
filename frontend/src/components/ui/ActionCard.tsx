import type { ReactNode } from 'react'
import styles from './ActionCard.module.css'

export type ActionCardTone = 'info' | 'warning' | 'danger' | 'success'

export type ActionCardProps = {
  /** Categoría breve sobre el título («Acción prioritaria»). */
  eyebrow: string
  title: ReactNode
  icon: ReactNode
  tone?: ActionCardTone
  description?: ReactNode
  /** Indicador junto al título (p. ej. UrgencyIndicator). */
  badge?: ReactNode
  /** Dato contextual real (fecha, requisito). */
  meta?: ReactNode
  /** CTA: un enlace o botón real; la tarjeta en sí no es clicable. */
  action?: ReactNode
  headingLevel?: 2 | 3
  className?: string
}

/**
 * Tarjeta flotante de acción (capa glass-floating). Comunica el estado con el
 * icono y el texto de la categoría, no solo con el color. La interacción vive
 * en el CTA, de modo que la semántica sigue siendo un enlace o botón normal.
 */
export function ActionCard({
  eyebrow,
  title,
  icon,
  tone = 'info',
  description,
  badge,
  meta,
  action,
  headingLevel = 2,
  className,
}: ActionCardProps) {
  const Heading = headingLevel === 2 ? 'h2' : 'h3'
  return (
    <article className={['glass-floating', styles.card, styles[tone], className].filter(Boolean).join(' ')}>
      <header className={styles.header}>
        <span aria-hidden="true" className={styles.icon}>
          {icon}
        </span>
        <div className={styles.heading}>
          {/* El indicador comparte la fila de la categoría: el título conserva todo el ancho. */}
          <div className={styles.eyebrowRow}>
            <p className={styles.eyebrow}>{eyebrow}</p>
            {badge && <div className={styles.badge}>{badge}</div>}
          </div>
          <Heading className={styles.title}>{title}</Heading>
        </div>
      </header>
      {description && <div className={styles.description}>{description}</div>}
      {(meta || action) && (
        <footer className={styles.footer}>
          {meta && <div className={styles.meta}>{meta}</div>}
          {action && <div className={styles.action}>{action}</div>}
        </footer>
      )}
    </article>
  )
}

/** Clase compartida para el CTA principal de una ActionCard (enlace con aspecto de botón). */
export const actionCardCtaClass = styles.cta
