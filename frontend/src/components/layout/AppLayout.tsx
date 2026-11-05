import { useContext, useState, type ReactNode } from 'react'
import { Outlet, useNavigate } from 'react-router-dom'
import { AuthContext } from '@/auth/AuthContext'
import { OPERATIONAL_ROLES } from '@/auth/roles'
import { getEnv } from '@/lib/env'
import { queryClient } from '@/lib/queryClient'
import styles from './AppLayout.module.css'
import { DemoBanner } from './DemoBanner'
import { Header } from './Header'
import { Sidebar, type SidebarItem } from './Sidebar'
import { SkipLink } from './SkipLink'

const NAV_ITEMS: SidebarItem[] = [
  { to: '/estudiante', label: 'Mi expediente', roles: ['ESTUDIANTE'] },
  { to: '/bandeja', label: 'Bandeja', roles: OPERATIONAL_ROLES },
]

type AppLayoutProps = {
  children?: ReactNode
}

export function AppLayout({ children }: AppLayoutProps) {
  const auth = useContext(AuthContext)
  const env = getEnv()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const user = auth?.user ?? null

  const handleLogout = () => {
    if (!window.confirm('¿Desea cerrar sesión?')) {
      return
    }

    auth?.logout()
    queryClient.clear()
    navigate('/login', { replace: true })
  }

  return (
    <>
      <SkipLink />
      <DemoBanner show={env.demoMode} />
      <Header
        appName={env.appName}
        sidebarOpen={sidebarOpen}
        user={user}
        onLogout={handleLogout}
        onToggleSidebar={() => setSidebarOpen((previous) => !previous)}
      />
      <div className={styles.body}>
        <Sidebar items={NAV_ITEMS} open={sidebarOpen} roles={user?.roles ?? []} />
        <main className={styles.main} id="main-content" tabIndex={-1}>
          {children ?? <Outlet />}
        </main>
      </div>
    </>
  )
}
