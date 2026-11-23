import { useContext } from 'react'
import { Link } from 'react-router-dom'
import { AuthContext } from '@/auth/AuthContext'
import { ErrorState } from '@/components/ui/ErrorState'
import { Spinner } from '@/components/ui/Spinner'
import { UserIcon } from '@/components/ui/icons'
import { presentApiError } from '@/lib/apiErrorPresentation'
import { Card } from '@/components/ui/Card'
import { useMiTramite } from './queries'
import styles from './StudentPages.module.css'

/**
 * `/estudiante/perfil`: datos de la cuenta autenticada, de solo lectura. El
 * backend no expone carrera ni facultad por nombre (sin catálogo, BE-10), por
 * eso no se muestran; tampoco hay edición de perfil.
 */
export default function PerfilPage() {
  const auth = useContext(AuthContext)
  const query = useMiTramite()
  const estudiante = query.data?.estudiante

  let datos
  if (query.isLoading) {
    datos = <Spinner label="Cargando tu perfil…" />
  } else if (query.isError) {
    const presentation = presentApiError(query.error)
    datos = (
      <ErrorState description={presentation.description} title={presentation.title} onRetry={() => void query.refetch()} />
    )
  } else {
    datos = (
      <dl className={styles.fields}>
        <div>
          <dt>Nombre</dt>
          <dd>{estudiante?.nombre_completo ?? 'No registrado'}</dd>
        </div>
        <div>
          <dt>Correo institucional</dt>
          <dd>{estudiante?.email ?? 'No registrado'}</dd>
        </div>
        <div>
          <dt>Cédula</dt>
          <dd>{estudiante?.cedula ?? auth?.user?.cedula ?? 'No registrada'}</dd>
        </div>
        <div>
          <dt>Rol</dt>
          <dd>Estudiante</dd>
        </div>
      </dl>
    )
  }

  return (
    <div className={styles.page}>
      <header>
        <h1 className={styles.title}>Mi perfil</h1>
        <p className={styles.subtitle}>Datos de tu cuenta en SGT-SIAAF.</p>
      </header>
      <Card icon={<UserIcon />} title="Datos de la cuenta">
        {datos}
      </Card>
      <Card title="Seguridad de la cuenta">
        <ul className={styles.links}>
          <li>
            <Link to="/recuperar-contrasena">Restablecer mi contraseña por correo</Link>
          </li>
          <li>
            <Link to="/restablecer-2fa">Perdí acceso a mi aplicación de autenticación</Link>
          </li>
        </ul>
      </Card>
    </div>
  )
}
