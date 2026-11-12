import { useContext } from 'react'
import { useLocation, useNavigate, useSearchParams } from 'react-router-dom'
import { AuthContext } from '@/auth/AuthContext'
import { getHomeRouteForRoles } from '@/auth/redirect'
import { Button } from '@/components/ui/Button'
import { EmptyState } from '@/components/ui/EmptyState'
import { ForbiddenState } from '@/components/ui/ForbiddenState'
import { resolverMotivo } from './motivos'
import styles from './NoHabilitadoPage.module.css'

const RUTA_NO_HABILITADO = '/no-habilitado'

/**
 * V-09 — Estado no habilitado (FE-T901…FE-T903). Comunica el motivo, la
 * dependencia `BE-xx` cuando aplica y un código de referencia, y siempre
 * ofrece una salida válida sin bucles de redirección:
 * - "Volver al inicio" solo si el rol tiene una página de inicio propia.
 * - "Volver atrás" solo si hay historial dentro de la aplicación.
 * - "Cerrar sesión" si la cuenta no tiene ningún rol reconocido.
 */
export default function NoHabilitadoPage() {
  const auth = useContext(AuthContext)
  const navigate = useNavigate()
  const location = useLocation()
  const [searchParams] = useSearchParams()
  const homeRoute = getHomeRouteForRoles(auth?.user?.roles ?? [])
  const sinRolReconocido = homeRoute === RUTA_NO_HABILITADO
  const motivo = resolverMotivo(searchParams, { sinRolReconocido })
  const hayHistorial = location.key !== 'default'

  function cerrarSesion() {
    auth?.logout()
    navigate('/login', { replace: true })
  }

  const acciones = (
    <div className={styles.acciones}>
      {!sinRolReconocido && <Button onClick={() => navigate(homeRoute)}>Volver al inicio</Button>}
      {hayHistorial && (
        <Button variant="secondary" onClick={() => navigate(-1)}>
          Volver atrás
        </Button>
      )}
      {sinRolReconocido && (
        <Button variant="secondary" onClick={cerrarSesion}>
          Cerrar sesión
        </Button>
      )}
    </div>
  )

  return (
    <div className={styles.page}>
      {motivo.tipo === 'forbidden' && <img alt="" className={styles.mascot} src="/assets/mascotas/mascota-403.png" />}
      {motivo.tipo === 'forbidden' ? (
        <ForbiddenState action={acciones} description={motivo.descripcion} title={motivo.titulo} />
      ) : (
        <EmptyState action={acciones} description={motivo.descripcion} title={motivo.titulo} />
      )}
      {motivo.dependencia && (
        <p className={styles.dependencia}>
          Dependencia pendiente: <strong>{motivo.dependencia.codigo}</strong> — {motivo.dependencia.descripcion}
        </p>
      )}
      <p className={styles.soporte}>
        Si necesita ayuda, comuníquese con la Secretaría de su carrera e indique el código de referencia{' '}
        <strong>{motivo.codigo}</strong>.
      </p>
    </div>
  )
}
