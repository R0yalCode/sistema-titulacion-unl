import { describe, expect, it } from 'vitest'
import { HttpResponse, http } from 'msw'
import { listBandejaOperativa } from '@/api/endpoints/expedientes'
import { server } from '@/test/server'
import { aplicarFiltros } from './BandejaFilters'
import { abreviarId, calcularVencimiento, estadosAtendidos, explicarBandejaVacia } from './bandejaReglas'

const AHORA = new Date(2026, 10, 12, 10, 0, 0)

describe('calcularVencimiento', () => {
  it('sin fecha límite o con una fecha inválida no inventa plazos', () => {
    expect(calcularVencimiento(null, AHORA)).toEqual({ tipo: 'sin-fecha' })
    expect(calcularVencimiento('no-es-fecha', AHORA)).toEqual({ tipo: 'sin-fecha' })
  })

  it('cuenta días calendario restantes y vencidos sin umbrales arbitrarios', () => {
    expect(calcularVencimiento(new Date(2026, 10, 17, 9, 0).toISOString(), AHORA)).toEqual({ tipo: 'pendiente', dias: 5 })
    expect(calcularVencimiento(new Date(2026, 10, 9, 18, 0).toISOString(), AHORA)).toEqual({ tipo: 'vencido', dias: 3 })
  })

  it('distingue "vence hoy" de "vencido hoy"', () => {
    expect(calcularVencimiento(new Date(2026, 10, 12, 18, 0).toISOString(), AHORA)).toEqual({ tipo: 'hoy' })
    expect(calcularVencimiento(new Date(2026, 10, 12, 8, 0).toISOString(), AHORA)).toEqual({ tipo: 'vencido', dias: 0 })
  })
})

describe('estadosAtendidos y explicarBandejaVacia', () => {
  it('reflejan el mapa real del backend por rol', () => {
    expect(estadosAtendidos(['DECANO'])).toEqual(['INFORME_EMITIDO'])
    expect(estadosAtendidos(['SECRETARIO_ABOGADO'])).toEqual(['ENVIADA', 'EN_VERIFICACION', 'OBSERVADA'])
    expect(estadosAtendidos(['SECRETARIA_CARRERA', 'DIRECTOR_CARRERA'])).toEqual([])
  })

  it('explica BE-09 para roles sin bandeja y un vacío normal para el resto', () => {
    expect(explicarBandejaVacia(['DIRECTOR_CARRERA']).descripcion).toContain('BE-09')
    expect(explicarBandejaVacia(['DECANO'])).toEqual({
      titulo: 'No hay expedientes pendientes',
      descripcion: 'No hay expedientes en los estados que atiende su rol (INFORME_EMITIDO).',
    })
  })
})

describe('aplicarFiltros', () => {
  const filas = [
    { estado: 'ENVIADA', numero_expediente: 'EXP-2026-0001' },
    { estado: 'OBSERVADA', numero_expediente: 'EXP-2026-0002' },
  ]

  it('filtra por estado y por número sin distinguir mayúsculas', () => {
    expect(aplicarFiltros(filas, { estado: 'OBSERVADA', numero: '' })).toEqual([filas[1]])
    expect(aplicarFiltros(filas, { estado: '', numero: 'exp-2026-0001' })).toEqual([filas[0]])
    expect(aplicarFiltros(filas, { estado: '', numero: '  ' })).toEqual(filas)
  })
})

describe('abreviarId', () => {
  it('abrevia el UUID real y marca la ausencia', () => {
    expect(abreviarId('88888888-1234-5678-9999-000000000000')).toBe('88888888')
    expect(abreviarId(null)).toBe('—')
  })
})

describe('listBandejaOperativa', () => {
  it('pide la página indicada y nunca supera el máximo de 50 del backend', async () => {
    let url = ''
    server.use(
      http.get('*/api/v1/expedientes/bandeja/', ({ request }) => {
        url = request.url
        return HttpResponse.json({ count: 0, next: null, previous: null, results: [] })
      }),
    )

    await listBandejaOperativa({ page: 3, pageSize: 200 })

    expect(url).toContain('page=3')
    expect(url).toContain('page_size=50')
  })
})
