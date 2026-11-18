import { Link } from 'react-router-dom'
import styles from './LandingPage.module.css'

/**
 * Página pública (AUTH-E, rediseño institucional 2026-11-18).
 *
 * Primera pantalla: reproduce la composición de la referencia institucional
 * (docs/autenticacion/referencias/fondo_referencia.jpg) con la fotografía del
 * campus `fondo_landing_page.jpg`: encabezado transparente con logotipo,
 * panel central translúcido con título, filete rojo, subtítulo y botón de
 * acceso. Debajo se conserva el recorrido general del proceso, con etapas
 * tomadas de SIAAF-KNOWLEDGE/12-DEGREE-PROCESSES (sin inventar normativa).
 */

type Stage = {
  title: string
  text: string
}

const PHASE_ONE: Stage[] = [
  { title: 'Solicitud de titulación', text: 'Usted crea su expediente en SGT-SIAAF.' },
  {
    title: 'Requisitos documentales',
    text: 'Solicita a cada dependencia sus certificados: récord académico, prácticas o vinculación, idioma B1, director de trabajo y no adeudar.',
  },
  {
    title: 'Envío del expediente',
    text: 'Con los cinco documentos vigentes, envía el expediente y empieza el plazo de revisión.',
  },
  { title: 'Verificación de requisitos', text: 'Secretaría Abogado/a revisa cada documento.' },
]

const AFTER_REVIEW: Stage[] = [
  { title: 'Informe de aptitud legal', text: 'Secretaría Abogado/a emite el informe.' },
  {
    title: 'Declaratoria de aptitud',
    text: 'El Decanato registra la declaratoria. Aquí concluye lo que hoy gestiona el sistema.',
  },
]

function StageItem({ stage, step }: { stage: Stage; step?: number }) {
  return (
    <li className={styles.stage}>
      <div className={styles.node}>
        {step !== undefined && (
          <span aria-hidden="true" className={styles.stepNumber}>
            {step}
          </span>
        )}
        <h4 className={styles.stageTitle}>{stage.title}</h4>
        <p className={styles.stageText}>{stage.text}</p>
      </div>
    </li>
  )
}

export default function LandingPage() {
  return (
    <div className={styles.page} id="inicio">
      <header className={styles.header}>
        <img
          alt="Universidad Nacional de Loja"
          className={styles.identity}
          height="138"
          src="/assets/auth/logo-unl.png"
          width="415"
        />
        <nav aria-label="Navegación principal" className={styles.nav}>
          <a className={styles.navLink} href="#inicio">
            Inicio
          </a>
          <Link className={`${styles.button} ${styles.buttonCompact}`} to="/login">
            Ingresar al sistema
          </Link>
        </nav>
      </header>

      <main id="contenido">
        <section aria-labelledby="hero-title" className={styles.hero}>
          <div className={styles.panel}>
            <p className={styles.kicker}>SGT-SIAAF</p>
            <h1 className={styles.title} id="hero-title">
              Sistema de Gestión del Trámite de Titulación
            </h1>
            <p className={styles.subtitle}>
              Universidad Nacional de Loja: solicite su titulación, presente sus requisitos y dé
              seguimiento a su expediente
            </p>
            <Link className={`${styles.button} ${styles.buttonHero}`} to="/login">
              Ingresar al sistema
            </Link>
          </div>
        </section>

        <section aria-labelledby="proceso-title" className={styles.process}>
          <h2 className={styles.sectionTitle} id="proceso-title">
            ¿Cómo es el proceso de titulación?
          </h2>
          <span aria-hidden="true" className={styles.sectionRule} />
          <p className={styles.sectionIntro}>
            Recorrido general, de arriba hacia abajo. Los requisitos exactos dependen de su carrera
            y de la normativa vigente de la Universidad.
          </p>

          <h3 className={styles.phaseLabel}>
            Fase 1 · Declaratoria de aptitud legal{' '}
            <span className={styles.badge}>Disponible en SGT-SIAAF</span>
          </h3>
          <ol className={styles.tree}>
            {PHASE_ONE.map((stage, index) => (
              <StageItem key={stage.title} stage={stage} step={index + 1} />
            ))}
            <li className={styles.stage}>
              <div className={styles.branch}>
                <div className={styles.branchCol}>
                  <p className={styles.branchLabel}>Sin observaciones</p>
                  <p className={styles.branchText}>El expediente continúa.</p>
                </div>
                <div className={styles.branchCol}>
                  <p className={styles.branchLabel}>Con observaciones</p>
                  <p className={styles.branchText}>
                    Usted subsana los documentos observados y vuelven a verificación.
                  </p>
                </div>
              </div>
            </li>
            {AFTER_REVIEW.map((stage, index) => (
              <StageItem key={stage.title} stage={stage} step={PHASE_ONE.length + index + 1} />
            ))}
          </ol>

          <h3 className={styles.phaseLabel}>
            Fases 2 y 3 · Sustentación y cierre{' '}
            <span className={styles.badgeMuted}>Referencial</span>
          </h3>
          <ol className={`${styles.tree} ${styles.treeMuted}`}>
            <li className={styles.stage}>
              <div className={styles.branch}>
                <div className={styles.branchCol}>
                  <p className={styles.branchLabel}>Trabajo de Integración Curricular</p>
                  <p className={styles.branchText}>
                    Modalidad ordinaria: trabajo escrito y defensa ante tribunal.
                  </p>
                </div>
                <div className={styles.branchCol}>
                  <p className={styles.branchLabel}>Examen Complexivo</p>
                  <p className={styles.branchText}>
                    Modalidad excepcional, con habilitación institucional: examen integral ante
                    tribunal.
                  </p>
                </div>
              </div>
            </li>
            <StageItem
              stage={{
                title: 'Sustentación y calificación',
                text: 'Tribunal de tres docentes; el acta conserva la firma autógrafa.',
              }}
            />
            <StageItem
              stage={{
                title: 'Cierre del trámite',
                text: 'Acta consolidada, autorización y registro del título.',
              }}
            />
          </ol>
          <p className={styles.disclaimer}>
            Estas etapas aún no se gestionan en SGT-SIAAF y sus reglas están pendientes de
            validación con la normativa institucional. Consulte a la secretaría de su carrera.
          </p>
        </section>
      </main>

      <footer className={styles.footer}>
        <p>
          Universidad Nacional de Loja · Sistema de Gestión del Trámite de Titulación (SGT-SIAAF)
        </p>
      </footer>
    </div>
  )
}
