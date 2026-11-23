import { useContext } from 'react'
import { Link } from 'react-router-dom'
import { AuthContext } from '@/auth/AuthContext'
import { Card } from '@/components/ui/Card'
import { ShieldIcon, UserIcon } from '@/components/ui/icons'
import { nombreRol } from '@/lib/estados'
import styles from './PerfilFuncionarioPage.module.css'

/**
 * `/perfil` para funcionarios: solo los datos que trae el token de sesión
 * (cédula y roles). El backend no expone un endpoint de perfil para estos
 * roles, por lo que no se muestran nombre, correo ni dependencia (pendiente
 * de un contrato de API; no se inventan).
 */
export default function PerfilFuncionarioPage() {
  const auth = useContext(AuthContext)
  const roles = auth?.user?.roles ?? []

  return (
    <div className={styles.page}>
      <header>
        <h1 className={styles.title}>Mi perfil</h1>
        <p className={styles.subtitle}>Datos de tu sesión en SGT-SIAAF.</p>
      </header>
      <Card icon={<UserIcon />} title="Datos de la cuenta">
        <dl className={styles.fields}>
          <div>
            <dt>Cédula</dt>
            <dd>{auth?.user?.cedula ?? 'No disponible'}</dd>
          </div>
          <div>
            <dt>{roles.length === 1 ? 'Rol' : 'Roles'}</dt>
            <dd>
              <ul className={styles.roles}>
                {roles.map((rol) => (
                  <li key={rol}>{nombreRol(rol)}</li>
                ))}
              </ul>
            </dd>
          </div>
        </dl>
      </Card>
      <Card icon={<ShieldIcon />} title="Seguridad de la cuenta">
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
