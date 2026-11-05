import { useContext } from 'react'
import { useNavigate } from 'react-router-dom'
import { AuthContext } from '@/auth/AuthContext'
import { getHomeRouteForRoles } from '@/auth/redirect'
import { Button } from '@/components/ui/Button'
import { NotFoundState } from '@/components/ui/NotFoundState'
import styles from './NotFoundPage.module.css'

export default function NotFoundPage() {
  const auth = useContext(AuthContext)
  const navigate = useNavigate()
  const isAuthenticated = auth?.isAuthenticated ?? false
  const primaryRoute = isAuthenticated ? getHomeRouteForRoles(auth?.user?.roles ?? []) : '/login'
  const primaryLabel = isAuthenticated ? 'Ir a mi inicio' : 'Ir a iniciar sesión'

  return (
    <main className={styles.page}>
      <h1 className={styles.heading}>Error 404</h1>
      <img alt="" className={styles.mascot} src="/assets/mascotas/mascota-404.png" />
      <NotFoundState
        action={
          <div className={styles.actions}>
            <Button onClick={() => navigate(primaryRoute)}>{primaryLabel}</Button>
            <Button onClick={() => navigate(-1)} variant="secondary">
              Volver atrás
            </Button>
          </div>
        }
        description="La página que busca no existe o no está disponible. Si llegó por un enlace, el recurso podría haberse movido, eliminado o no estar disponible para su cuenta."
        title="Página no encontrada"
      />
    </main>
  )
}
