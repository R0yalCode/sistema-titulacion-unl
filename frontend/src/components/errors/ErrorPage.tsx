import type { ErrorViewProps } from './ErrorView'
import { ErrorView } from './ErrorView'
import styles from './ErrorPage.module.css'

export type ErrorPageProps = Omit<ErrorViewProps, 'variant'> & {
  /** Destino del logotipo de la cabecera. */
  homeHref?: string
}

/**
 * Página completa de error: cabecera institucional (logotipo oficial ya
 * versionado en `public/assets/auth`), panel Liquid Glass con `ErrorView` y
 * pie institucional. No depende del router: el ErrorBoundary global también
 * la usa, fuera de BrowserRouter.
 */
export function ErrorPage({ homeHref = '/', ...viewProps }: ErrorPageProps) {
  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <a className={styles.brand} href={homeHref}>
          <img
            alt="Universidad Nacional de Loja"
            className={styles.logo}
            height="138"
            src="/assets/auth/logo-unl.png"
            width="415"
          />
        </a>
        <span className={styles.system}>SGT-SIAAF · Titulación</span>
      </header>
      <main className={styles.main} id="main-content" tabIndex={-1}>
        <div className={`glass-floating ${styles.panel}`}>
          <ErrorView {...viewProps} variant="page" />
        </div>
      </main>
      <footer className={styles.footer}>
        Universidad Nacional de Loja · Sistema de Gestión de Trámites de Titulación (SGT-SIAAF)
      </footer>
    </div>
  )
}
