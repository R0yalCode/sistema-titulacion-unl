const ROLE_HOME_ROUTES: Array<{ role: string; path: string }> = [
  { role: 'ADMINISTRADOR', path: '/bandeja' },
  { role: 'SECRETARIO_ABOGADO', path: '/bandeja' },
  { role: 'ANALISTA_APOYO', path: '/bandeja' },
  { role: 'DECANO', path: '/bandeja' },
  { role: 'SECRETARIA_CARRERA', path: '/bandeja' },
  { role: 'DIRECTOR_CARRERA', path: '/bandeja' },
  { role: 'ESTUDIANTE', path: '/estudiante' },
]

export function getHomeRouteForRoles(roles: string[]): string {
  const match = ROLE_HOME_ROUTES.find((entry) => roles.includes(entry.role))
  return match?.path ?? '/no-habilitado'
}
