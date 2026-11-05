import styles from './DemoBanner.module.css'

type DemoBannerProps = {
  show: boolean
}

export function DemoBanner({ show }: DemoBannerProps) {
  if (!show) {
    return null
  }

  return (
    <div className={styles.banner} role="status">
      Entorno de demostración
    </div>
  )
}
