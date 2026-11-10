import { describe, expect, it } from 'vitest'
import {
  puedeDescargar,
  puedeEnviar,
  puedeEvaluarItem,
  puedeObservar,
  puedeSubsanarItem,
  puedeVerChecklist,
} from './accionesPorRolEstado'

describe('puedeVerChecklist', () => {
  it('permite a SECRETARIO_ABOGADO, ANALISTA_APOYO y ADMINISTRADOR', () => {
    expect(puedeVerChecklist(['SECRETARIO_ABOGADO'])).toBe(true)
    expect(puedeVerChecklist(['ANALISTA_APOYO'])).toBe(true)
    expect(puedeVerChecklist(['ADMINISTRADOR'])).toBe(true)
  })

  it('niega a ESTUDIANTE y a otros roles sin acceso real (403 confirmado en RBAC_MATRIX)', () => {
    expect(puedeVerChecklist(['ESTUDIANTE'])).toBe(false)
    expect(puedeVerChecklist(['SECRETARIA_CARRERA'])).toBe(false)
    expect(puedeVerChecklist(['DECANO'])).toBe(false)
    expect(puedeVerChecklist([])).toBe(false)
  })
})

describe('puedeEnviar', () => {
  it('permite al propio estudiante solo desde BORRADOR', () => {
    expect(puedeEnviar(['ESTUDIANTE'], 'BORRADOR', true)).toBe(true)
  })

  it('niega si no es el propietario', () => {
    expect(puedeEnviar(['ESTUDIANTE'], 'BORRADOR', false)).toBe(false)
  })

  it('niega fuera de BORRADOR', () => {
    expect(puedeEnviar(['ESTUDIANTE'], 'ENVIADA', true)).toBe(false)
    expect(puedeEnviar(['ESTUDIANTE'], 'EN_VERIFICACION', true)).toBe(false)
  })

  it('niega a roles distintos de ESTUDIANTE', () => {
    expect(puedeEnviar(['SECRETARIO_ABOGADO'], 'BORRADOR', true)).toBe(false)
  })
})

describe('puedeObservar', () => {
  it('permite a SECRETARIO_ABOGADO solo con el expediente EN_VERIFICACION', () => {
    expect(puedeObservar(['SECRETARIO_ABOGADO'], 'EN_VERIFICACION')).toBe(true)
  })

  it('niega en otros estados', () => {
    expect(puedeObservar(['SECRETARIO_ABOGADO'], 'BORRADOR')).toBe(false)
    expect(puedeObservar(['SECRETARIO_ABOGADO'], 'ENVIADA')).toBe(false)
    expect(puedeObservar(['SECRETARIO_ABOGADO'], 'OBSERVADA')).toBe(false)
  })

  it('niega a otros roles, incluido ANALISTA_APOYO (no concedido en RBAC_MATRIX real)', () => {
    expect(puedeObservar(['ANALISTA_APOYO'], 'EN_VERIFICACION')).toBe(false)
    expect(puedeObservar(['ESTUDIANTE'], 'EN_VERIFICACION')).toBe(false)
  })
})

describe('puedeEvaluarItem', () => {
  it('permite a SECRETARIO_ABOGADO y ANALISTA_APOYO con expediente EN_VERIFICACION e ítem PENDIENTE', () => {
    expect(puedeEvaluarItem(['SECRETARIO_ABOGADO'], 'EN_VERIFICACION', 'PENDIENTE')).toBe(true)
    expect(puedeEvaluarItem(['ANALISTA_APOYO'], 'EN_VERIFICACION', 'PENDIENTE')).toBe(true)
  })

  it('niega si el ítem ya fue evaluado (VerificationAlreadyCompletedError real, 400)', () => {
    expect(puedeEvaluarItem(['SECRETARIO_ABOGADO'], 'EN_VERIFICACION', 'VERIFICADO')).toBe(false)
    expect(puedeEvaluarItem(['SECRETARIO_ABOGADO'], 'EN_VERIFICACION', 'OBSERVADO')).toBe(false)
  })

  it('niega si el expediente no está EN_VERIFICACION', () => {
    expect(puedeEvaluarItem(['SECRETARIO_ABOGADO'], 'OBSERVADA', 'PENDIENTE')).toBe(false)
    expect(puedeEvaluarItem(['SECRETARIO_ABOGADO'], 'BORRADOR', 'PENDIENTE')).toBe(false)
  })

  it('niega a ESTUDIANTE', () => {
    expect(puedeEvaluarItem(['ESTUDIANTE'], 'EN_VERIFICACION', 'PENDIENTE')).toBe(false)
  })
})

describe('puedeSubsanarItem', () => {
  it('permite al estudiante propietario con expediente OBSERVADA e ítem OBSERVADO', () => {
    expect(puedeSubsanarItem(['ESTUDIANTE'], 'OBSERVADA', 'OBSERVADO', true)).toBe(true)
  })

  it('niega al estudiante que no es propietario (aislamiento IDOR)', () => {
    expect(puedeSubsanarItem(['ESTUDIANTE'], 'OBSERVADA', 'OBSERVADO', false)).toBe(false)
  })

  it('permite a SECRETARIA_CARRERA y ADMINISTRADOR sin requisito de "propietario"', () => {
    expect(puedeSubsanarItem(['SECRETARIA_CARRERA'], 'OBSERVADA', 'OBSERVADO', false)).toBe(true)
    expect(puedeSubsanarItem(['ADMINISTRADOR'], 'OBSERVADA', 'OBSERVADO', false)).toBe(true)
  })

  it('niega a SECRETARIO_ABOGADO y ANALISTA_APOYO (evaluadores, no subsanadores en RBAC real)', () => {
    expect(puedeSubsanarItem(['SECRETARIO_ABOGADO'], 'OBSERVADA', 'OBSERVADO', false)).toBe(false)
    expect(puedeSubsanarItem(['ANALISTA_APOYO'], 'OBSERVADA', 'OBSERVADO', false)).toBe(false)
  })

  it('niega si el ítem no está OBSERVADO o el expediente no está OBSERVADA', () => {
    expect(puedeSubsanarItem(['ESTUDIANTE'], 'OBSERVADA', 'PENDIENTE', true)).toBe(false)
    expect(puedeSubsanarItem(['ESTUDIANTE'], 'EN_VERIFICACION', 'OBSERVADO', true)).toBe(false)
  })
})

describe('puedeDescargar', () => {
  it('permite a los roles con acceso real a peticiones:documento GET', () => {
    expect(puedeDescargar(['ESTUDIANTE'])).toBe(true)
    expect(puedeDescargar(['SECRETARIA_CARRERA'])).toBe(true)
    expect(puedeDescargar(['SECRETARIO_ABOGADO'])).toBe(true)
    expect(puedeDescargar(['ANALISTA_APOYO'])).toBe(true)
    expect(puedeDescargar(['DIRECTOR_CARRERA'])).toBe(true)
    expect(puedeDescargar(['ADMINISTRADOR'])).toBe(true)
  })

  it('niega a DECANO (excluido a propósito; sin acceso en la matriz RBAC real)', () => {
    expect(puedeDescargar(['DECANO'])).toBe(false)
  })
})
