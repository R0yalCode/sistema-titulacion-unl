import { Link } from 'react-router-dom'
import styles from './LandingPage.module.css'

/**
 * Página pública. Reproduce la composición de la referencia institucional
 * (docs/autenticacion/referencias/fondo_referencia.jpg) con la fotografía del
 * campus `fondo_landing_page.jpg`: logotipo y navegación sobre la imagen, y
 * panel central translúcido con título, filete rojo, descripción y botón de
 * acceso.
 */
export default function LandingPage() {
  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <img
          alt="Universidad Nacional de Loja"
          className={styles.identity}
          height="138"
          src="/assets/auth/logo-unl.png"
          width="415"
        />
        <nav aria-label="Navegación principal" className={styles.nav}>
          <Link className={styles.navLink} to="/">
            Inicio
          </Link>
          <Link className={styles.navButton} to="/login">
            Acceder al Sistema
          </Link>
        </nav>
      </header>

      <main className={styles.hero} id="contenido">
        <section aria-labelledby="hero-title" className={styles.panel}>
          <p className={styles.kicker}>SGT-SIAAF</p>
          <h1 className={styles.title} id="hero-title">
            Sistema de Gestión del Trámite de Titulación
          </h1>
          <p className={styles.subtitle}>
            Solicite su titulación, presente sus requisitos y dé seguimiento a su expediente
          </p>
          <Link className={styles.button} to="/login">
            Ingresar al sistema
          </Link>
        </section>
      </main>
    </div>
  )
}
