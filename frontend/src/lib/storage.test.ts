import { afterEach, describe, expect, it } from 'vitest'
import { clearRecentExpedientes, getRecentExpedientes, recordVisitedExpediente } from './storage'

describe('storage (accesos rápidos de expedientes)', () => {
  afterEach(() => {
    sessionStorage.clear()
  })

  it('no tiene accesos rápidos cuando no se registró ninguno', () => {
    expect(getRecentExpedientes()).toEqual([])
  })

  it('registra un expediente visitado', () => {
    recordVisitedExpediente('exp-1', 'EXP-2026-0001')

    const recent = getRecentExpedientes()
    expect(recent).toHaveLength(1)
    expect(recent[0]).toMatchObject({ id: 'exp-1', numeroExpediente: 'EXP-2026-0001' })
  })

  it('permite registrar un expediente sin numero_expediente conocido', () => {
    recordVisitedExpediente('exp-1')

    const recent = getRecentExpedientes()
    expect(recent[0]!.id).toBe('exp-1')
    expect(recent[0]!.numeroExpediente).toBeUndefined()
  })

  it('evita duplicados: revisitar un expediente lo mueve al frente', () => {
    recordVisitedExpediente('exp-1')
    recordVisitedExpediente('exp-2')
    recordVisitedExpediente('exp-1')

    const recent = getRecentExpedientes()
    expect(recent).toHaveLength(2)
    expect(recent[0]!.id).toBe('exp-1')
    expect(recent[1]!.id).toBe('exp-2')
  })

  it('limita la cantidad de accesos rápidos almacenados', () => {
    for (let i = 0; i < 8; i += 1) {
      recordVisitedExpediente(`exp-${i}`)
    }

    expect(getRecentExpedientes()).toHaveLength(5)
    expect(getRecentExpedientes()[0]!.id).toBe('exp-7')
  })

  it('descarta datos inválidos en sessionStorage sin lanzar', () => {
    sessionStorage.setItem('sgt.recent_expedientes', '{no-es-json válido')

    expect(getRecentExpedientes()).toEqual([])
  })

  it('descarta entradas con forma inválida dentro de un array válido', () => {
    sessionStorage.setItem(
      'sgt.recent_expedientes',
      JSON.stringify([{ id: 'exp-1', visitadoEn: '2026-01-01T00:00:00.000Z' }, { sinId: true }, 'texto-suelto']),
    )

    expect(getRecentExpedientes()).toEqual([{ id: 'exp-1', visitadoEn: '2026-01-01T00:00:00.000Z' }])
  })

  it('descarta el valor completo cuando sessionStorage no contiene un array', () => {
    sessionStorage.setItem('sgt.recent_expedientes', JSON.stringify({ id: 'exp-1' }))

    expect(getRecentExpedientes()).toEqual([])
  })

  it('limpia todos los accesos rápidos', () => {
    recordVisitedExpediente('exp-1')
    clearRecentExpedientes()

    expect(getRecentExpedientes()).toEqual([])
  })
})
