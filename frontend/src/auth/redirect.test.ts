import { describe, expect, it } from 'vitest'
import { getHomeRouteForRoles } from './redirect'

describe('getHomeRouteForRoles', () => {
  it('envía a ESTUDIANTE a /estudiante', () => {
    expect(getHomeRouteForRoles(['ESTUDIANTE'])).toBe('/estudiante')
  })

  it.each(['ADMINISTRADOR', 'SECRETARIO_ABOGADO', 'ANALISTA_APOYO', 'DECANO', 'SECRETARIA_CARRERA', 'DIRECTOR_CARRERA'])(
    'envía a %s a /bandeja',
    (role) => {
      expect(getHomeRouteForRoles([role])).toBe('/bandeja')
    },
  )

  it('con varios roles, aplica el primero de la lista oficial (specify.md §6)', () => {
    expect(getHomeRouteForRoles(['ESTUDIANTE', 'DECANO'])).toBe('/bandeja')
  })

  it('devuelve /no-habilitado si no hay ningún rol reconocido', () => {
    expect(getHomeRouteForRoles(['ROL_DESCONOCIDO'])).toBe('/no-habilitado')
    expect(getHomeRouteForRoles([])).toBe('/no-habilitado')
  })
})
