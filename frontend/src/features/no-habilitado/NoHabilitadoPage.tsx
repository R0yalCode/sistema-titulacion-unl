import { useContext } from 'react'
import { useNavigate } from 'react-router-dom'
import { AuthContext } from '@/auth/AuthContext'
import { getHomeRouteForRoles } from '@/auth/redirect'
import { Button } from '@/components/ui/Button'
import { ForbiddenState } from '@/components/ui/ForbiddenState'
import styles from './NoHabilitadoPage.module.css'

export default function NoHabilitadoPage() {
  const auth = useContext(AuthContext)
  const navigate = useNavigate()
  const homeRoute = getHomeRouteForRoles(auth?.user?.roles ?? [])

  return (
    <div>
      <img alt="" className={styles.mascot} src="/assets/mascotas/mascota-403.png" />
      <ForbiddenState
        action={<Button onClick={() => navigate(homeRoute)}>Volver al inicio</Button>}
        description="No cuenta con los permisos necesarios para ver esta sección. Si considera que esto es un error, comuníquese con la dependencia correspondiente."
        title="Acceso restringido"
      />
    </div>
  )
}
