import { useContext, type ReactNode } from 'react'
import { AuthContext } from '@/auth/AuthContext'
import { OPERATIONAL_ROLES, ROLES_CON_NOTIFICACIONES } from '@/auth/roles'
import { BellIcon, InboxIcon, InfoIcon, SettingsShieldIcon, UserIcon } from '@/components/ui/icons'
import { useNotificaciones } from '@/features/dashboard'
import { getEnv } from '@/lib/env'
import { nombreRol } from '@/lib/estados'
import { AppShell, type ShellNavItem } from './AppShell'

/**
 * Portal de funcionarios. La navegación se construye con las capacidades
 * reales de cada rol (rutas y celdas RBAC existentes); el backend sigue
 * autorizando cada operación.
 */
function buildNavItems(roles: string[], noLeidas: number, apiBaseUrl: string): ShellNavItem[] {
  const tiene = (lista: string[]) => roles.some((rol) => lista.includes(rol))
  const items: ShellNavItem[] = []
  if (tiene(OPERATIONAL_ROLES)) {
    items.push({ to: '/bandeja', label: 'Bandeja de trabajo', icon: <InboxIcon /> })
  }
  if (tiene(ROLES_CON_NOTIFICACIONES)) {
    items.push({ to: '/notificaciones', label: 'Notificaciones', icon: <BellIcon />, count: noLeidas })
  }
  if (tiene(OPERATIONAL_ROLES)) {
    items.push({ to: '/perfil', label: 'Mi perfil', icon: <UserIcon /> })
  }
  if (roles.includes('ADMINISTRADOR')) {
    // Consola interna existente (Django admin, ADR-0009): usuarios, roles y auditoría.
    items.push({ to: `${apiBaseUrl}/admin/`, label: 'Consola de administración', icon: <SettingsShieldIcon />, external: true })
  }
  if (items.length === 0) {
    items.push({ to: '/no-habilitado', label: 'Estado de mi acceso', icon: <InfoIcon /> })
  }
  return items
}

export function AppLayout({ children }: { children?: ReactNode }) {
  const auth = useContext(AuthContext)
  const env = getEnv()
  const roles = auth?.user?.roles ?? []
  const conNotificaciones = roles.some((rol) => ROLES_CON_NOTIFICACIONES.includes(rol))
  const notificaciones = useNotificaciones({ enabled: conNotificaciones })
  const noLeidas = notificaciones.data?.results.filter((notificacion) => !notificacion.leida).length ?? 0
  const rolPrincipal = roles.find((rol) => rol !== 'ESTUDIANTE') ?? roles[0]

  return (
    <AppShell
      navItems={buildNavItems(roles, noLeidas, env.apiBaseUrl)}
      notificationsTo={conNotificaciones ? '/notificaciones' : null}
      portalLabel="Gestión de titulación"
      profileTo={roles.some((rol) => OPERATIONAL_ROLES.includes(rol)) ? '/perfil' : null}
      unreadCount={noLeidas}
      userName={rolPrincipal ? nombreRol(rolPrincipal) : 'Usuario'}
      userRole={auth?.user?.cedula ? `C.I. ${auth.user.cedula}` : ''}
    >
      {children}
    </AppShell>
  )
}
