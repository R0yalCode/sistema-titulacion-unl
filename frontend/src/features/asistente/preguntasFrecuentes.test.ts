import { describe, expect, it } from 'vitest'
import fuenteRouter from '@/app/router.tsx?raw'
import { PREGUNTAS_FRECUENTES, preguntasPara } from './preguntasFrecuentes'

/** Rutas estáticas declaradas en el router real (path="…"). */
const RUTAS_REALES = new Set([...fuenteRouter.matchAll(/path="([^"]+)"/g)].map((coincidencia) => coincidencia[1]))

describe('preguntas frecuentes del asistente (AX-D)', () => {
  it('solo enlazan a rutas que existen en el router', () => {
    expect(RUTAS_REALES.size).toBeGreaterThan(5)
    const destinos = PREGUNTAS_FRECUENTES.flatMap((pregunta) => pregunta.enlaces.map((enlace) => enlace.destino))
    expect(destinos.length).toBeGreaterThan(0)
    for (const destino of destinos) {
      expect(RUTAS_REALES, `ruta inexistente: ${destino}`).toContain(destino)
    }
  })

  it('tienen identificador único y respuesta', () => {
    const ids = PREGUNTAS_FRECUENTES.map((pregunta) => pregunta.id)
    expect(new Set(ids).size).toBe(ids.length)
    for (const pregunta of PREGUNTAS_FRECUENTES) {
      expect(pregunta.respuesta.length).toBeGreaterThan(0)
    }
  })

  it('cubren los temas aprobados', () => {
    const ids = PREGUNTAS_FRECUENTES.map((pregunta) => pregunta.id)
    expect(ids).toEqual(
      expect.arrayContaining([
        'iniciar-tramite',
        'estado-tramite',
        'cargar-documentos',
        'consultar-requisitos',
        'navegar-modulos',
        'errores-comunes',
      ]),
    )
  })

  it('no dan plazos, fechas ni días como si fueran normativa', () => {
    const texto = PREGUNTAS_FRECUENTES.flatMap((pregunta) => pregunta.respuesta).join(' ')
    expect(texto).not.toMatch(/\b\d+\s*(días|dias|horas|semanas|meses)\b/i)
    expect(texto).not.toMatch(/\b(art\.|artículo)\s*\d+/i)
  })

  it('filtra por tipo de usuario', () => {
    const estudiante = preguntasPara(true).map((pregunta) => pregunta.id)
    const funcionario = preguntasPara(false).map((pregunta) => pregunta.id)
    expect(estudiante).toContain('cargar-documentos')
    expect(estudiante).not.toContain('bandeja-funcionario')
    expect(funcionario).toContain('bandeja-funcionario')
    expect(funcionario).not.toContain('iniciar-tramite')
    expect(funcionario).toContain('errores-comunes')
  })
})
