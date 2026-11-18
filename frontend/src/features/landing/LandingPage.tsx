import { Link } from 'react-router-dom'
import styles from './LandingPage.module.css'

/**
 * Página pública informativa (AUTH-E). No consulta la API ni muestra datos:
 * explica el sistema y el proceso general de titulación.
 *
 * Etapas tomadas de la documentación del proyecto
 * (SIAAF-KNOWLEDGE/12-DEGREE-PROCESSES): la fase 1 (declaratoria de aptitud
 * legal, Art. 235) es la que gestiona hoy SGT-SIAAF; las modalidades y las
 * fases 2 y 3 se muestran como referencia y su normativa sigue pendiente de
 * validación institucional.
 */

type Stage = {
  title: string
  text: string
}

const PHASE_ONE: Stage[] = [
  {
    title: 'Solicitud de titulación',
    text: 'Usted crea su expediente en SGT-SIAAF.',
  },
  {
    title: 'Requisitos documentales',
    text: 'Solicita a cada dependencia sus certificados: récord académico, prácticas o vinculación, idioma B1, director de trabajo y no adeudar.',
  },
  {
    title: 'Envío del expediente',
    text: 'Con los cinco documentos vigentes, envía el expediente y empieza el plazo de revisión.',
  },
  {
    title: 'Verificación de requisitos',
    text: 'Secretaría Abogado/a revisa cada documento.',
  },
]

const AFTER_REVIEW: Stage[] = [
  {
    title: 'Informe de aptitud legal',
    text: 'Secretaría Abogado/a emite el informe.',
  },
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
    <div className={styles.page}>
      <header className={styles.banner}>
        <img
          alt="Universidad Nacional de Loja"
          className={styles.identity}
          height="118"
          src="/assets/auth/unl-identidad.png"
          width="322"
        />
        <Link className={styles.headerLink} to="/login">
          Ingresar
        </Link>
      </header>

      <main id="contenido">
        <section aria-labelledby="hero-title" className={styles.hero}>
          <p className={styles.kicker}>SGT-SIAAF</p>
          <h1 className={styles.heroTitle} id="hero-title">
            Sistema de Gestión de Titulación
          </h1>
          <p className={styles.heroText}>
            Gestione en línea su trámite de titulación en la Universidad Nacional de Loja: solicitud, requisitos
            documentales, verificación y declaratoria de aptitud, con seguimiento del estado de su expediente.
          </p>
          <Link className={styles.cta} to="/login">
            Ingresar al sistema
          </Link>
          <p className={styles.heroNote}>Acceso con su usuario institucional y verificación en dos pasos.</p>
        </section>

        <section aria-labelledby="proceso-title" className={styles.process}>
          <h2 className={styles.sectionTitle} id="proceso-title">
            ¿Cómo es el proceso de titulación?
          </h2>
          <p className={styles.sectionIntro}>
            Recorrido general, de arriba hacia abajo. Los requisitos exactos dependen de su carrera y de la
            normativa vigente de la Universidad.
          </p>

          <h3 className={styles.phaseLabel}>
            Fase 1 · Declaratoria de aptitud legal <span className={styles.badge}>Disponible en SGT-SIAAF</span>
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
            Fases 2 y 3 · Sustentación y cierre <span className={styles.badgeMuted}>Referencial</span>
          </h3>
          <ol className={`${styles.tree} ${styles.treeMuted}`}>
            <li className={styles.stage}>
              <div className={styles.branch}>
                <div className={styles.branchCol}>
                  <p className={styles.branchLabel}>Trabajo de Integración Curricular</p>
                  <p className={styles.branchText}>Modalidad ordinaria: trabajo escrito y defensa ante tribunal.</p>
                </div>
                <div className={styles.branchCol}>
                  <p className={styles.branchLabel}>Examen Complexivo</p>
                  <p className={styles.branchText}>
                    Modalidad excepcional, con habilitación institucional: examen integral ante tribunal.
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
            Estas etapas aún no se gestionan en SGT-SIAAF y sus reglas están pendientes de validación con la normativa
            institucional. Consulte a la secretaría de su carrera.
          </p>
        </section>
      </main>

      <footer className={styles.footer}>
        <p>Universidad Nacional de Loja · Sistema de Gestión de Titulación (SGT-SIAAF)</p>
      </footer>
    </div>
  )
}
