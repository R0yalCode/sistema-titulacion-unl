import type { ReactNode } from 'react'
import styles from './AuthLayout.module.css'

type AuthLayoutProps = {
  title: string
  /** Texto bajo el título (solo con `titleStyle="panel"`). */
  description?: string
  /**
   * `underline`: título centrado en mayúsculas con subrayado dorado dentro de
   * la tarjeta (referencia `sac-login.png`). `panel`: título en un panel azul
   * sobre la tarjeta (referencia `restablecer_doble_factor.png`).
   */
  titleStyle?: 'underline' | 'panel'
  /** Contenido sobre el título de la tarjeta (p. ej. aviso de entorno). */
  notice?: ReactNode
  /** Nota bajo la tarjeta (p. ej. aviso de seguridad). */
  footnote?: ReactNode
  children: ReactNode
}

/**
 * Marco de las pantallas públicas de autenticación con la composición del
 * Servicio de Autenticación Centralizada (SAC) de la UNL: banda con la
 * fotografía del campus (`campus.png`) tratada en azul institucional,
 * logotipo oficial, texto institucional y tarjeta centrada.
 *
 * SGT-SIAAF autentica localmente: esta pantalla reproduce la experiencia
 * visual del SAC, pero no es el SAC ni está integrada con él.
 */
export function AuthLayout({
  title,
  description,
  titleStyle = 'underline',
  notice,
  footnote,
  children,
}: AuthLayoutProps) {
  return (
    <div className={styles.page}>
      <header className={styles.banner}>
        <div className={styles.brand}>
          <img
            alt="Universidad Nacional de Loja"
            className={styles.identity}
            height="138"
            src="/assets/auth/logo-unl.png"
            width="415"
          />
          <span aria-hidden="true" className={styles.divider} />
          <p className={styles.systemName}>
            Servicio de
            <br />
            Autenticación Centralizada
          </p>
        </div>
        <p className={styles.systemTag}>SGT-SIAAF · Sistema de Gestión de Titulación</p>
      </header>

      <main className={styles.main}>
        <div className={styles.column}>
          {titleStyle === 'panel' ? (
            <>
              <section aria-labelledby="auth-card-title" className={styles.titlePanel}>
                {notice}
                <h1 className={styles.panelTitle} id="auth-card-title">
                  {title}
                </h1>
                {description && <p className={styles.panelText}>{description}</p>}
              </section>
              <div className={styles.card}>{children}</div>
            </>
          ) : (
            <section aria-labelledby="auth-card-title" className={styles.card}>
              {notice}
              <h1 className={styles.cardTitle} id="auth-card-title">
                {title}
              </h1>
              {children}
            </section>
          )}
          {footnote && <aside className={styles.footnote}>{footnote}</aside>}
        </div>
      </main>

      <footer className={styles.footer}>
        <p>Universidad Nacional de Loja · Sistema de Gestión de Titulación (SGT-SIAAF)</p>
      </footer>
    </div>
  )
}
