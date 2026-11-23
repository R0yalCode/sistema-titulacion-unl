import { useContext, useEffect, useRef, useState, type ReactNode } from 'react'
import { Link, NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { AuthContext } from '@/auth/AuthContext'
import { useConfirm } from '@/components/ui/ConfirmDialog'
import { BellIcon, CloseIcon, ExternalLinkIcon, LogoutIcon, MenuIcon, SidebarIcon, UserIcon } from '@/components/ui/icons'
import { getEnv } from '@/lib/env'
import { queryClient } from '@/lib/queryClient'
import { DemoBanner } from './DemoBanner'
import { SkipLink } from './SkipLink'
import styles from './AppShell.module.css'

export type ShellNavItem = {
  to: string
  label: string
  icon: ReactNode
  /** Coincidencia exacta de ruta (para que una sección padre no quede activa en sus hijas). */
  end?: boolean
  /** Contador real (p. ej. notificaciones sin leer). */
  count?: number
  /** Enlace fuera de la SPA (p. ej. consola interna de administración). */
  external?: boolean
}

export type AppShellProps = {
  /** Nombre del portal en la barra superior ("Portal del estudiante", "Gestión de titulación"). */
  portalLabel: string
  navItems: ShellNavItem[]
  /** Ruta de la página de perfil, si el rol la tiene. */
  profileTo: string | null
  /** Ruta de notificaciones, si el rol tiene acceso real (RBAC). */
  notificationsTo: string | null
  unreadCount: number
  userName: string
  userRole: string
  children?: ReactNode
}

const COLLAPSE_KEY = 'sgt.sidebar.contraido'

function leerPreferencia(): boolean {
  try {
    return localStorage.getItem(COLLAPSE_KEY) === '1'
  } catch {
    return false
  }
}

function guardarPreferencia(valor: boolean) {
  try {
    localStorage.setItem(COLLAPSE_KEY, valor ? '1' : '0')
  } catch {
    // Sin almacenamiento disponible: la preferencia dura la sesión.
  }
}

function iniciales(nombre: string): string {
  const partes = nombre.split(/\s+/).filter((parte) => /\p{L}/u.test(parte))
  const primera = partes[0]?.[0] ?? ''
  const ultima = partes.length > 1 ? (partes[partes.length - 1]?.[0] ?? '') : ''
  return `${primera}${ultima}`.toUpperCase()
}

/**
 * Estructura común de la aplicación autenticada (Design System §Layout):
 * sidebar institucional (contraíble en escritorio, panel lateral en ≤1024 px),
 * barra superior con notificaciones y perfil, y un único `<main>`. Cada rol
 * la configura con su navegación autorizada (StudentLayout, AppLayout).
 */
export function AppShell({
  portalLabel,
  navItems,
  profileTo,
  notificationsTo,
  unreadCount,
  userName,
  userRole,
  children,
}: AppShellProps) {
  const auth = useContext(AuthContext)
  const env = getEnv()
  const navigate = useNavigate()
  const location = useLocation()
  const { confirm, dialog } = useConfirm()
  // El panel móvil queda abierto solo en la ruta donde se abrió: al navegar se
  // cierra sin sincronizar estado en un efecto.
  const [drawerPath, setDrawerPath] = useState<string | null>(null)
  const drawerOpen = drawerPath === location.pathname
  const [collapsed, setCollapsed] = useState(leerPreferencia)
  const menuButtonRef = useRef<HTMLButtonElement>(null)
  const firstLinkRef = useRef<HTMLAnchorElement>(null)

  useEffect(() => {
    if (!drawerOpen) {
      return
    }
    firstLinkRef.current?.focus()
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        setDrawerPath(null)
        menuButtonRef.current?.focus()
      }
    }
    document.addEventListener('keydown', onKeyDown)
    return () => document.removeEventListener('keydown', onKeyDown)
  }, [drawerOpen])

  function cerrarPanel() {
    setDrawerPath(null)
    menuButtonRef.current?.focus()
  }

  function alternarContraido() {
    setCollapsed((previo) => {
      guardarPreferencia(!previo)
      return !previo
    })
  }

  async function handleLogout() {
    const confirmado = await confirm({
      title: '¿Cerrar sesión?',
      description: 'Se cerrará tu sesión en este dispositivo y el próximo ingreso pedirá el código de verificación.',
      confirmLabel: 'Cerrar sesión',
    })
    if (!confirmado) {
      return
    }
    auth?.signOut()
    queryClient.clear()
    navigate('/login', { replace: true })
  }

  const bellLabel = unreadCount > 0 ? `Notificaciones, ${unreadCount} sin leer` : 'Notificaciones'
  const sidebarClass = [styles.sidebar, drawerOpen && styles.sidebarOpen, collapsed && styles.collapsed]
    .filter(Boolean)
    .join(' ')

  return (
    <div className={styles.shell}>
      <SkipLink />
      <DemoBanner show={env.demoMode} />
      <div className={styles.frame}>
        <aside aria-label="Menú principal" className={sidebarClass} id="menu-principal">
          <div className={styles.brand}>
            <img
              alt="Universidad Nacional de Loja"
              className={styles.logo}
              height="138"
              src="/assets/auth/logo-unl.png"
              width="415"
            />
            <p className={styles.system}>SGT-SIAAF · Titulación</p>
            <button aria-label="Cerrar menú" className={styles.closeButton} type="button" onClick={cerrarPanel}>
              <CloseIcon />
            </button>
          </div>
          <nav aria-label="Navegación principal" className={styles.nav}>
            <ul className={styles.navList}>
              {navItems.map((item, index) => (
                <li key={item.to}>
                  {item.external ? (
                    <a className={styles.navLink} href={item.to} title={collapsed ? item.label : undefined}>
                      <span className={styles.navIcon}>{item.icon}</span>
                      <span className={styles.navLabel}>{item.label}</span>
                      <span aria-hidden="true" className={styles.navExternal}>
                        <ExternalLinkIcon size={14} />
                      </span>
                    </a>
                  ) : (
                    <NavLink
                      className={({ isActive }) => (isActive ? `${styles.navLink} ${styles.navLinkActive}` : styles.navLink)}
                      end={item.end}
                      ref={index === 0 ? firstLinkRef : undefined}
                      title={collapsed ? item.label : undefined}
                      to={item.to}
                    >
                      <span className={styles.navIcon}>{item.icon}</span>
                      <span className={styles.navLabel}>{item.label}</span>
                      {item.count !== undefined && item.count > 0 && (
                        <span className={styles.navCount}>
                          {item.count}
                          <span className="sr-only"> sin leer</span>
                        </span>
                      )}
                    </NavLink>
                  )}
                </li>
              ))}
            </ul>
          </nav>
          <div className={styles.sidebarFooter}>
            <button
              aria-expanded={!collapsed}
              aria-label={collapsed ? 'Expandir menú lateral' : 'Contraer menú lateral'}
              className={`${styles.footerButton} ${styles.collapseButton}`}
              title={collapsed ? 'Expandir menú lateral' : undefined}
              type="button"
              onClick={alternarContraido}
            >
              <span className={styles.navIcon}>
                <SidebarIcon />
              </span>
              <span className={styles.navLabel}>Contraer menú</span>
            </button>
            <button
              className={styles.footerButton}
              title={collapsed ? 'Cerrar sesión' : undefined}
              type="button"
              onClick={() => void handleLogout()}
            >
              <span className={styles.navIcon}>
                <LogoutIcon />
              </span>
              <span className={styles.navLabel}>Cerrar sesión</span>
            </button>
          </div>
        </aside>

        {drawerOpen && (
          <button
            aria-label="Cerrar menú"
            className={styles.backdrop}
            tabIndex={-1}
            type="button"
            onClick={() => setDrawerPath(null)}
          />
        )}

        <div className={styles.column}>
          <header className={styles.topbar}>
            <button
              aria-controls="menu-principal"
              aria-expanded={drawerOpen}
              aria-label="Abrir menú"
              className={styles.menuButton}
              ref={menuButtonRef}
              type="button"
              onClick={() => setDrawerPath(location.pathname)}
            >
              <MenuIcon />
            </button>
            <span className={styles.topbarTitle}>{portalLabel}</span>
            <div className={styles.topbarActions}>
              {notificationsTo && (
                <Link aria-label={bellLabel} className={styles.iconButton} to={notificationsTo}>
                  <BellIcon />
                  {unreadCount > 0 && (
                    <span aria-hidden="true" className={styles.dot}>
                      {unreadCount > 9 ? '9+' : unreadCount}
                    </span>
                  )}
                </Link>
              )}
              {profileTo ? (
                <Link className={styles.profileLink} to={profileTo}>
                  <span aria-hidden="true" className={styles.avatar}>
                    {iniciales(userName) || <UserIcon size={18} />}
                  </span>
                  <span className={styles.profileText}>
                    <span className={styles.profileName}>
                      <span className="sr-only">Mi perfil: </span>
                      {userName}
                    </span>
                    <span className={styles.profileRole}>{userRole}</span>
                  </span>
                </Link>
              ) : (
                <span className={styles.profileLink}>
                  <span className={styles.profileText}>
                    <span className={styles.profileName}>{userName}</span>
                  </span>
                </span>
              )}
            </div>
          </header>
          <main className={styles.main} id="main-content" tabIndex={-1}>
            <div className={styles.content}>{children ?? <Outlet />}</div>
          </main>
        </div>
      </div>
      {dialog}
    </div>
  )
}
