import { useId, type ReactNode } from 'react'
import styles from './HeroPanel.module.css'

export type HeroMetaItem = {
  /** Clave estable para la lista. */
  id: string
  icon?: ReactNode
  label: ReactNode
}

export type HeroPanelProps = {
  /** Contexto breve sobre el título (expediente, rol, unidad). */
  eyebrow?: ReactNode
  title: ReactNode
  description?: ReactNode
  /** Datos reales en forma de chips (fechas, etapa, ámbito). */
  meta?: HeroMetaItem[]
  /** Contenido flotante a la derecha (p. ej. ActionCard). */
  aside?: ReactNode
  /** Acciones en la cabecera (botones). */
  actions?: ReactNode
  headingLevel?: 1 | 2
  className?: string
}

/**
 * Encabezado contextual con el degradado institucional (identidad UNL) y
 * capas translúcidas. Es puramente presentacional: el título y los chips
 * llegan ya resueltos desde datos reales de la vista que lo usa.
 */
export function HeroPanel({
  eyebrow,
  title,
  description,
  meta = [],
  aside,
  actions,
  headingLevel = 1,
  className,
}: HeroPanelProps) {
  const titleId = useId()
  const Heading = headingLevel === 1 ? 'h1' : 'h2'
  return (
    <section aria-labelledby={titleId} className={[styles.hero, className].filter(Boolean).join(' ')}>
      <span aria-hidden="true" className={styles.glowA} />
      <span aria-hidden="true" className={styles.glowB} />
      <div className={styles.inner}>
        <div className={styles.main}>
          {eyebrow && <p className={`${styles.eyebrow} glass-on-brand`}>{eyebrow}</p>}
          <Heading className={styles.title} id={titleId}>
            {title}
          </Heading>
          {description && <p className={styles.description}>{description}</p>}
          {meta.length > 0 && (
            <ul className={styles.meta}>
              {meta.map((item) => (
                <li className={styles.chip} key={item.id}>
                  {item.icon && (
                    <span aria-hidden="true" className={styles.chipIcon}>
                      {item.icon}
                    </span>
                  )}
                  <span>{item.label}</span>
                </li>
              ))}
            </ul>
          )}
          {actions && <div className={styles.actions}>{actions}</div>}
        </div>
        {aside && <div className={styles.aside}>{aside}</div>}
      </div>
    </section>
  )
}
