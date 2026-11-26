import { describe, expect, it } from 'vitest'
import { esConsultaNormativa } from './consultaNormativa'

describe('esConsultaNormativa (AX-D)', () => {
  it.each([
    '¿Qué dice el reglamento de titulación?',
    '¿Cuáles son los requisitos para graduarme?',
    '¿Hasta qué fecha puedo presentar la solicitud?',
    '¿Cuál es el plazo para la defensa?',
    '¿Qué establece la resolución del consejo?',
    'Según el Art. 212, ¿qué necesito?',
    '¿Puedo elegir el examen complexivo?',
    '¿Qué modalidades de titulación existen?',
  ])('detecta consultas normativas: %s', (pregunta) => {
    expect(esConsultaNormativa(pregunta)).toBe(true)
  })

  it.each(['¿Cómo cargo un documento?', '¿Dónde veo mis notificaciones?', 'No encuentro el botón de enviar'])(
    'no marca consultas de uso del sistema: %s',
    (pregunta) => {
      expect(esConsultaNormativa(pregunta)).toBe(false)
    },
  )
})
