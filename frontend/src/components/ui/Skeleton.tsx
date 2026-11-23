import styles from './Skeleton.module.css'

type SkeletonProps = {
  /** Alto de cada bloque (CSS). */
  height?: string
  /** Número de bloques apilados. */
  count?: number
  /** Etiqueta para lectores de pantalla; los bloques son decorativos. */
  label?: string
  variant?: 'block' | 'text' | 'card'
}

/** Marcador de carga con la forma del contenido final; respeta reduced-motion. */
export function Skeleton({ height, count = 1, label = 'Cargando…', variant = 'block' }: SkeletonProps) {
  return (
    <div aria-busy="true" className={styles.group} role="status">
      <span className="sr-only">{label}</span>
      {Array.from({ length: count }, (_, index) => (
        <span aria-hidden="true" className={`${styles.bone} ${styles[variant]}`} key={index} style={height ? { height } : undefined} />
      ))}
    </div>
  )
}
