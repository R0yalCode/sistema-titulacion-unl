import { describe, expect, it } from 'vitest'
import { DEPENDENCIAS_BACKEND, resolverMotivo } from './motivos'

function params(query: string) {
  return new URLSearchParams(query)
}

describe('resolverMotivo', () => {
  it('por defecto (o desde la guarda) explica un acceso restringido con su código', () => {
    for (const query of ['', 'motivo=rol-no-autorizado']) {
      const motivo = resolverMotivo(params(query), { sinRolReconocido: false })
      expect(motivo).toMatchObject({ tipo: 'forbidden', titulo: 'Acceso restringido', codigo: 'V09-ROL' })
    }
  })

  it('una cuenta sin rol reconocido recibe su propio motivo', () => {
    expect(resolverMotivo(params(''), { sinRolReconocido: true }).codigo).toBe('V09-SIN-ROL')
    expect(resolverMotivo(params('motivo=sin-rol'), { sinRolReconocido: false }).codigo).toBe('V09-SIN-ROL')
  })

  it('una funcionalidad no disponible muestra la dependencia BE-xx válida', () => {
    const motivo = resolverMotivo(params('motivo=no-disponible&dependencia=BE-09'), { sinRolReconocido: false })
    expect(motivo).toMatchObject({
      tipo: 'info',
      codigo: 'V09-BE-09',
      dependencia: { codigo: 'BE-09', descripcion: DEPENDENCIAS_BACKEND['BE-09'] },
    })
  })

  it('ignora dependencias y motivos fuera de las listas blancas', () => {
    const sinDependencia = resolverMotivo(params('motivo=no-disponible&dependencia=<script>'), {
      sinRolReconocido: false,
    })
    expect(sinDependencia.dependencia).toBeUndefined()
    expect(sinDependencia.codigo).toBe('V09-NO-DISPONIBLE')
    expect(resolverMotivo(params('motivo=inventado'), { sinRolReconocido: false }).codigo).toBe('V09-ROL')
  })

  it('el catálogo cubre las dependencias BE-01 a BE-11 de tasks.md', () => {
    expect(Object.keys(DEPENDENCIAS_BACKEND)).toEqual(
      Array.from({ length: 11 }, (_, index) => `BE-${String(index + 1).padStart(2, '0')}`),
    )
  })
})
