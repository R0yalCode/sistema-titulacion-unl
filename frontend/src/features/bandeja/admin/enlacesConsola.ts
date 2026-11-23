export type EnlaceConsola = { href: string; titulo: string; descripcion: string }

/** Secciones reales de la consola interna (Django admin, ADR-0009). */
export function enlacesConsola(apiBaseUrl: string): EnlaceConsola[] {
  return [
    { href: `${apiBaseUrl}/admin/authentication/user/`, titulo: 'Usuarios', descripcion: 'Cuentas del sistema' },
    { href: `${apiBaseUrl}/admin/authentication/role/`, titulo: 'Roles', descripcion: 'Roles institucionales' },
    {
      href: `${apiBaseUrl}/admin/notificaciones/eventoauditoria/`,
      titulo: 'Auditoría',
      descripcion: 'Eventos de auditoría del trámite',
    },
    {
      href: `${apiBaseUrl}/admin/authentication/eventoautenticacion/`,
      titulo: 'Accesos',
      descripcion: 'Eventos de autenticación',
    },
  ]
}
