import { describe, expect, it } from 'vitest'
import { fixtureExpedienteBorrador } from '@/mocks/fixtures'
import { buscarPeticion, describirEstadoPeticion } from './seguimiento'

describe('buscarPeticion', () => {
  const peticiones = fixtureExpedienteBorrador.peticiones

  it('resuelve la petición por id entre las peticiones del expediente', () => {
    expect(buscarPeticion(peticiones, peticiones[2]!.id)).toBe(peticiones[2])
  })

  it('devuelve undefined si el id no pertenece al expediente o falta', () => {
    expect(buscarPeticion(peticiones, '00000000-0000-0000-0000-000000000000')).toBeUndefined()
    expect(buscarPeticion(peticiones, undefined)).toBeUndefined()
  })
})

describe('describirEstadoPeticion', () => {
  it('explica los estados reales del backend', () => {
    for (const estado of ['PENDIENTE', 'SOLICITADO', 'CARGADO', 'LEGALIZADO', 'VERIFICADO', 'OBSERVADO']) {
      expect(describirEstadoPeticion(estado)).not.toContain('Estado informado por el sistema')
    }
    expect(describirEstadoPeticion('OBSERVADO')).toContain('BE-07')
  })

  it('no inventa significado para un estado desconocido', () => {
    expect(describirEstadoPeticion('EN_REVISION')).toBe('Estado informado por el sistema: EN_REVISION.')
  })
})
