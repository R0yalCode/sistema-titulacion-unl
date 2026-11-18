import type { ReactNode } from 'react'
import styles from './AuthLayout.module.css'

type AuthLayoutProps = {
  title: string
  /** Contenido sobre el título de la tarjeta (p. ej. aviso de entorno). */
  notice?: ReactNode
  children: ReactNode
}

/**
 * Marco común de las pantallas públicas de autenticación: banda institucional
 * (identidad UNL sobre la fotografía del campus), tarjeta centrada y pie.
 */
export function AuthLayout({ title, notice, children }: AuthLayoutProps) {
  return (
    <div className={styles.page}>
      <header className={styles.banner}>
        <div className={styles.brand}>
          <img
            alt="Universidad Nacional de Loja"
            className={styles.identity}
            height="118"
            src="/assets/auth/unl-identidad.png"
            width="322"
          />
          <span aria-hidden="true" className={styles.divider} />
          <p className={styles.systemName}>
            Sistema de
            <br />
            Gestión de Titulación
          </p>
        </div>
        <p className={styles.systemTag}>SGT-SIAAF · Trámite de titulación</p>
      </header>

      <main className={styles.main}>
        <section aria-labelledby="auth-card-title" className={styles.card}>
          {notice}
          <h1 className={styles.cardTitle} id="auth-card-title">
            {title}
          </h1>
          {children}
        </section>
      </main>

      <footer className={styles.footer}>
        <p>Universidad Nacional de Loja · Sistema de Gestión de Titulación (SGT-SIAAF)</p>
      </footer>
    </div>
  )
}
