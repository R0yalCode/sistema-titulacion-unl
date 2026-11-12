import { describe, expect, it } from 'vitest'
import {
  presentarEstadoPeticion,
  puedeCargarDocumento,
  puedeSolicitarEmision,
  tieneDocumento,
} from './accionesPeticion'

describe('puedeSolicitarEmision', () => {
  it('solo el ESTUDIANTE, con expediente BORRADOR u OBSERVADA y petición PENDIENTE', () => {
    expect(puedeSolicitarEmision(['ESTUDIANTE'], 'BORRADOR', 'PENDIENTE')).toBe(true)
    expect(puedeSolicitarEmision(['ESTUDIANTE'], 'OBSERVADA', 'PENDIENTE')).toBe(true)
  })

  it('no se ofrece con otro estado de expediente o de petición', () => {
    expect(puedeSolicitarEmision(['ESTUDIANTE'], 'EN_VERIFICACION', 'PENDIENTE')).toBe(false)
    expect(puedeSolicitarEmision(['ESTUDIANTE'], 'BORRADOR', 'SOLICITADO')).toBe(false)
  })

  it('no se ofrece a roles que el RBAC real rechaza (403)', () => {
    for (const rol of ['SECRETARIA_CARRERA', 'SECRETARIO_ABOGADO', 'DECANO', 'ANALISTA_APOYO']) {
      expect(puedeSolicitarEmision([rol], 'BORRADOR', 'PENDIENTE')).toBe(false)
    }
  })
})

describe('puedeCargarDocumento', () => {
  it('el ESTUDIANTE puede cargar en los estados que admite el servicio', () => {
    for (const estado of ['PENDIENTE', 'SOLICITADO', 'OBSERVADO', 'CARGADO']) {
      expect(puedeCargarDocumento(['ESTUDIANTE'], estado, 'DIRECCION_INVESTIGACION')).toBe(true)
    }
  })

  it('no se ofrece en estados que el servicio rechaza', () => {
    expect(puedeCargarDocumento(['ESTUDIANTE'], 'LEGALIZADO', 'SECRETARIA_CARRERA')).toBe(false)
    expect(puedeCargarDocumento(['ESTUDIANTE'], 'VERIFICADO', 'SECRETARIA_CARRERA')).toBe(false)
  })

  it('la Secretaría de Carrera solo en peticiones asignadas a la Secretaría (VULN-002)', () => {
    expect(puedeCargarDocumento(['SECRETARIA_CARRERA'], 'SOLICITADO', 'SECRETARIA_CARRERA')).toBe(true)
    expect(puedeCargarDocumento(['SECRETARIA_CARRERA'], 'SOLICITADO', 'TESORERIA')).toBe(false)
  })

  it('no se ofrece a funcionarios que el servicio rechaza aunque la matriz RBAC los incluya', () => {
    for (const rol of ['SECRETARIO_ABOGADO', 'ANALISTA_APOYO', 'DIRECTOR_CARRERA', 'DECANO']) {
      expect(puedeCargarDocumento([rol], 'SOLICITADO', 'SECRETARIA_CARRERA')).toBe(false)
    }
  })
})

describe('tieneDocumento', () => {
  it('solo los estados posteriores a una carga', () => {
    expect(tieneDocumento('CARGADO')).toBe(true)
    expect(tieneDocumento('OBSERVADO')).toBe(true)
    expect(tieneDocumento('PENDIENTE')).toBe(false)
    expect(tieneDocumento('SOLICITADO')).toBe(false)
  })
})

describe('presentarEstadoPeticion', () => {
  it('traduce los estados reales y no inventa estados desconocidos', () => {
    expect(presentarEstadoPeticion('SOLICITADO')).toEqual({ label: 'Solicitado', variant: 'info' })
    expect(presentarEstadoPeticion('OBSERVADO').variant).toBe('warning')
    expect(presentarEstadoPeticion('ESTADO_NUEVO')).toEqual({ label: 'ESTADO_NUEVO', variant: 'neutral' })
  })
})
