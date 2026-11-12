import { describe, expect, it } from 'vitest'
import { esEstadoFinal, puedeIniciarVerificacion } from './accionesFuncionario'

describe('accionesFuncionario (V-08a)', () => {
  it('solo SECRETARIO_ABOGADO inicia la verificación y solo desde ENVIADA', () => {
    expect(puedeIniciarVerificacion(['SECRETARIO_ABOGADO'], 'ENVIADA')).toBe(true)
    expect(puedeIniciarVerificacion(['SECRETARIO_ABOGADO'], 'EN_VERIFICACION')).toBe(false)
    for (const rol of ['ANALISTA_APOYO', 'DECANO', 'ADMINISTRADOR', 'SECRETARIA_CARRERA']) {
      expect(puedeIniciarVerificacion([rol], 'ENVIADA')).toBe(false)
    }
  })

  it('DECLARADA_APTA y CANCELADA son estados finales de solo lectura', () => {
    expect(esEstadoFinal('DECLARADA_APTA')).toBe(true)
    expect(esEstadoFinal('CANCELADA')).toBe(true)
    expect(esEstadoFinal('INFORME_EMITIDO')).toBe(false)
  })
})
