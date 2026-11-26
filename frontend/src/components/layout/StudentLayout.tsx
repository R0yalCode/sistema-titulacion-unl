import type { ReactNode } from 'react'
import { BellIcon, DocumentIcon, FolderIcon, HomeIcon, UserIcon } from '@/components/ui/icons'
import { useMiTramite, useNotificaciones } from '@/features/dashboard'
import { AppShell, type ShellNavItem } from './AppShell'
import { useNombreVisible } from './useNombreVisible'

/**
 * Navegación del estudiante. Solo enlaza funcionalidades reales: "Mi trámite"
 * y "Documentos" aparecen cuando existe un expediente (sus rutas dependen del
 * id real); sin expediente se ofrece "Nueva solicitud".
 */
function buildNavItems(expedienteId: string | null, noLeidas: number): ShellNavItem[] {
  const items: ShellNavItem[] = [{ to: '/estudiante', label: 'Inicio', icon: <HomeIcon />, end: true }]
  if (expedienteId) {
    items.push(
      { to: `/expedientes/${expedienteId}`, label: 'Mi trámite', icon: <FolderIcon />, end: true },
      { to: `/expedientes/${expedienteId}/peticiones`, label: 'Documentos', icon: <DocumentIcon /> },
    )
  } else {
    items.push({ to: '/estudiante/solicitud/nueva', label: 'Nueva solicitud', icon: <FolderIcon /> })
  }
  items.push(
    { to: '/estudiante/notificaciones', label: 'Notificaciones', icon: <BellIcon />, count: noLeidas },
    { to: '/estudiante/perfil', label: 'Mi perfil', icon: <UserIcon /> },
  )
  return items
}

export function StudentLayout({ children }: { children?: ReactNode }) {
  const miTramite = useMiTramite()
  const notificaciones = useNotificaciones()
  // AX-C: primer nombre y primer apellido de perfil-academico (o nombre_completo sin partir).
  const usuario = useNombreVisible()

  const expedienteId = miTramite.data?.expediente?.id ?? null
  const noLeidas = notificaciones.data?.results.filter((notificacion) => !notificacion.leida).length ?? 0

  return (
    <AppShell
      navItems={buildNavItems(expedienteId, noLeidas)}
      notificationsTo="/estudiante/notificaciones"
      glass
      portalLabel="Portal del estudiante"
      profileTo="/estudiante/perfil"
      unreadCount={noLeidas}
      userName={usuario.nombre}
      userRole={usuario.detalle}
    >
      {children}
    </AppShell>
  )
}
