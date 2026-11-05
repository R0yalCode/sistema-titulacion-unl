import styles from './Header.module.css'

export type HeaderUser = {
  cedula: string
  roles: string[]
}

type HeaderProps = {
  appName: string
  user: HeaderUser | null
  sidebarOpen: boolean
  onToggleSidebar: () => void
  onLogout: () => void
}

export function Header({ appName, user, sidebarOpen, onToggleSidebar, onLogout }: HeaderProps) {
  return (
    <header className={styles.header}>
      <button
        aria-expanded={sidebarOpen}
        aria-label="Abrir navegación"
        className={styles.menuButton}
        type="button"
        onClick={onToggleSidebar}
      >
        ☰
      </button>
      <span className={styles.appName}>{appName}</span>
      <div className={styles.rightSection}>
        {user && (
          <div className={styles.userInfo}>
            <span>{user.cedula}</span>
            <span>{user.roles.join(', ')}</span>
          </div>
        )}
        <button className={styles.logoutButton} type="button" onClick={onLogout}>
          Cerrar sesión
        </button>
      </div>
    </header>
  )
}
