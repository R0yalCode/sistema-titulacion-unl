import { afterEach, describe, expect, it } from 'vitest'
import {
  CLAVE_ALMACENAMIENTO,
  PREFERENCIAS_INICIALES,
  aplicarPreferencias,
  formatearPorcentaje,
  formatearVelocidad,
  guardarPreferencias,
  leerPreferencias,
  limitar,
  normalizarPreferencias,
} from './preferencias'

afterEach(() => {
  localStorage.clear()
})

describe('preferencias de accesibilidad', () => {
  it('parte de valores neutros con la velocidad de lectura en 0,7x', () => {
    expect(PREFERENCIAS_INICIALES).toEqual({
      escalaTexto: 1,
      modoColor: 'ninguno',
      subrayarEnlaces: false,
      fuenteLegible: false,
      velocidadLectura: 0.7,
    })
  })

  it('limita y redondea sin derivas de coma flotante', () => {
    expect(limitar(1.1 + 0.1, 0.9, 1.6)).toBe(1.2)
    expect(limitar(3, 0.9, 1.6)).toBe(1.6)
    expect(limitar(0.2, 0.9, 1.6)).toBe(0.9)
  })

  it('descarta campos inválidos de un almacenamiento manipulado', () => {
    expect(
      normalizarPreferencias({
        escalaTexto: 'grande',
        modoColor: 'arcoiris',
        subrayarEnlaces: 'sí',
        fuenteLegible: true,
        velocidadLectura: 9,
      }),
    ).toEqual({ ...PREFERENCIAS_INICIALES, fuenteLegible: true, velocidadLectura: 1.5 })
    expect(normalizarPreferencias(null)).toEqual(PREFERENCIAS_INICIALES)
  })

  it('persiste con versión y relee lo guardado', () => {
    const preferencias = { ...PREFERENCIAS_INICIALES, escalaTexto: 1.3, modoColor: 'alto-contraste' as const }
    guardarPreferencias(preferencias)
    expect(JSON.parse(localStorage.getItem(CLAVE_ALMACENAMIENTO) ?? '{}')).toEqual({ version: 1, preferencias })
    expect(leerPreferencias()).toEqual(preferencias)
  })

  it('no deja rastro en el almacenamiento cuando las preferencias son las iniciales', () => {
    guardarPreferencias({ ...PREFERENCIAS_INICIALES, subrayarEnlaces: true })
    guardarPreferencias({ ...PREFERENCIAS_INICIALES })
    expect(localStorage.getItem(CLAVE_ALMACENAMIENTO)).toBeNull()
  })

  it('ignora JSON corrupto o de otra versión del esquema', () => {
    localStorage.setItem(CLAVE_ALMACENAMIENTO, '{no es json')
    expect(leerPreferencias()).toEqual(PREFERENCIAS_INICIALES)
    localStorage.setItem(CLAVE_ALMACENAMIENTO, JSON.stringify({ version: 99, preferencias: { escalaTexto: 1.5 } }))
    expect(leerPreferencias()).toEqual(PREFERENCIAS_INICIALES)
  })

  it('refleja las preferencias en atributos del elemento raíz y los retira al volver al inicio', () => {
    const raiz = document.createElement('html')
    aplicarPreferencias(
      { escalaTexto: 1.2, modoColor: 'grises', subrayarEnlaces: true, fuenteLegible: true, velocidadLectura: 1 },
      raiz,
    )
    expect(raiz.style.getPropertyValue('--a11y-escala-texto')).toBe('1.2')
    expect(raiz).toHaveAttribute('data-a11y-texto', 'escalado')
    expect(raiz).toHaveAttribute('data-a11y-color', 'grises')
    expect(raiz).toHaveAttribute('data-a11y-enlaces', 'subrayados')
    expect(raiz).toHaveAttribute('data-a11y-fuente', 'legible')

    aplicarPreferencias({ ...PREFERENCIAS_INICIALES }, raiz)
    expect(raiz.style.getPropertyValue('--a11y-escala-texto')).toBe('')
    for (const atributo of ['data-a11y-texto', 'data-a11y-color', 'data-a11y-enlaces', 'data-a11y-fuente']) {
      expect(raiz).not.toHaveAttribute(atributo)
    }
  })

  it('formatea porcentaje y velocidad en español', () => {
    expect(formatearPorcentaje(1.1)).toBe('110 %')
    expect(formatearVelocidad(0.7)).toBe('0,7x')
  })
})
