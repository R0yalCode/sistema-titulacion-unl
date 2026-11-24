import { useContext, type ReactNode } from 'react'
import { useLocation } from 'react-router-dom'
import { AuthContext } from '@/auth/AuthContext'
import { OPERATIONAL_ROLES, ROLES_CON_NOTIFICACIONES } from '@/auth/roles'
import { BellIcon, InboxIcon, InfoIcon, SettingsShieldIcon, UserIcon } from '@/components/ui/icons'
import { AdminSearch, enlacesConsola, type DestinoBusqueda } from '@/features/bandeja'
import { useNotificaciones } from '@/features/dashboard'
import { getEnv } from '@/lib/env'
import { nombreRol } from '@/lib/estados'
import '@/styles/siaaf-modern.css'
import { AppShell, type ShellNavItem } from './AppShell'

/**
 * Portal de funcionarios. La navegación se construye con las capacidades
 * reales de cada rol (rutas y celdas RBAC existentes); el backend sigue
 * autorizando cada operación.
 */
function buildNavItems(roles: string[], noLeidas: number, apiBaseUrl: string): ShellNavItem[] {
  const tiene = (lista: string[]) => roles.some((rol) => lista.includes(rol))
  const esAdministrador = roles.includes('ADMINISTRADOR')
  const group = esAdministrador ? 'Menú principal' : undefined
  const items: ShellNavItem[] = []
  if (tiene(OPERATIONAL_ROLES)) {
    items.push({ to: '/bandeja', label: 'Bandeja de trabajo', icon: <InboxIcon />, group })
  }
  if (tiene(ROLES_CON_NOTIFICACIONES)) {
    items.push({ to: '/notificaciones', label: 'Notificaciones', icon: <BellIcon />, count: noLeidas, group })
  }
  if (tiene(OPERATIONAL_ROLES)) {
    items.push({ to: '/perfil', label: 'Mi perfil', icon: <UserIcon />, group })
  }
  if (esAdministrador) {
    // Consola interna existente (Django admin, ADR-0009): usuarios, roles y auditoría.
    items.push({
      to: `${apiBaseUrl}/admin/`,
      label: 'Consola de administración',
      icon: <SettingsShieldIcon />,
      external: true,
      group: 'Gestión y control',
    })
  }
  if (items.length === 0) {
    items.push({ to: '/no-habilitado', label: 'Estado de mi acceso', icon: <InfoIcon /> })
  }
  return items
}

function seccionAdministrador(pathname: string): string {
  if (pathname === '/bandeja') return 'Panel'
  if (pathname.startsWith('/bandeja/') || pathname.startsWith('/expedientes/')) return 'Expediente'
  if (pathname.startsWith('/notificaciones')) return 'Notificaciones'
  if (pathname.startsWith('/perfil')) return 'Mi perfil'
  return 'Gestión de titulación'
}

export function AppLayout({ children }: { children?: ReactNode }) {
  const auth = useContext(AuthContext)
  const { pathname } = useLocation()
  const env = getEnv()
  const roles = auth?.user?.roles ?? []
  const conNotificaciones = roles.some((rol) => ROLES_CON_NOTIFICACIONES.includes(rol))
  const notificaciones = useNotificaciones({ enabled: conNotificaciones })
  const noLeidas = notificaciones.data?.results.filter((notificacion) => !notificacion.leida).length ?? 0
  const rolPrincipal = roles.find((rol) => rol !== 'ESTUDIANTE') ?? roles[0]
  const esAdministrador = roles.includes('ADMINISTRADOR')
  const navItems = buildNavItems(roles, noLeidas, env.apiBaseUrl)
  const destinosBusqueda: DestinoBusqueda[] = esAdministrador
    ? [
        ...navItems
          .filter((item) => !item.external)
          .map((item) => ({ label: item.label, to: item.to })),
        ...enlacesConsola(env.apiBaseUrl).map((enlace) => ({
          label: enlace.titulo,
          to: enlace.href,
          detalle: enlace.descripcion,
          external: true,
        })),
      ]
    : []

  return (
    <AppShell
      navItems={navItems}
      notificationsTo={conNotificaciones ? '/notificaciones' : null}
      glass
      portalLabel={esAdministrador ? `Administración · ${seccionAdministrador(pathname)}` : 'Gestión de titulación'}
      profileTo={roles.some((rol) => OPERATIONAL_ROLES.includes(rol)) ? '/perfil' : null}
      topbarSlot={esAdministrador ? <AdminSearch destinos={destinosBusqueda} /> : undefined}
      unreadCount={noLeidas}
      visual={esAdministrador ? 'siaaf-modern' : undefined}
      userName={rolPrincipal ? nombreRol(rolPrincipal) : 'Usuario'}
      userRole={auth?.user?.cedula ? `C.I. ${auth.user.cedula}` : ''}
    >
      {children}
    </AppShell>
  )
}
