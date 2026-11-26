import { describe, expect, it } from 'vitest'
import { iniciales, nombreCorto, nombreEstudiante, primerApellido, primerNombre } from './nombreVisible'

describe('nombre visible (AX-C)', () => {
  it('toma el primer nombre', () => {
    expect(primerNombre('María José')).toBe('María')
    expect(primerNombre('  Ana ')).toBe('Ana')
    expect(primerNombre('')).toBeNull()
    expect(primerNombre(null)).toBeNull()
  })

  it('toma el primer apellido conservando sus partículas', () => {
    expect(primerApellido('Pérez López')).toBe('Pérez')
    expect(primerApellido('De la Cruz Torres')).toBe('De la Cruz')
    expect(primerApellido('Del Pozo Ruiz')).toBe('Del Pozo')
    expect(primerApellido('De Prueba')).toBe('De Prueba')
    expect(primerApellido('San Martín Ochoa')).toBe('San Martín')
    expect(primerApellido(undefined)).toBeNull()
  })

  it('compone primer nombre y primer apellido', () => {
    expect(nombreCorto('Juan Carlos', 'Jiménez Loaiza')).toBe('Juan Jiménez')
    expect(nombreCorto('Juan Carlos', '')).toBe('Juan')
    expect(nombreCorto('', '')).toBeNull()
  })

  it('prefiere el perfil académico y, sin él, usa el nombre completo sin partirlo', () => {
    expect(
      nombreEstudiante({ perfil: { nombres: 'Juan Carlos', apellidos: 'Jiménez Loaiza' }, nombreCompleto: 'Otro Nombre' }),
    ).toBe('Juan Jiménez')
    // Una cadena única no permite saber dónde acaban los nombres: no se recorta.
    expect(nombreEstudiante({ perfil: null, nombreCompleto: 'Juan Carlos Jiménez Loaiza' })).toBe(
      'Juan Carlos Jiménez Loaiza',
    )
    expect(nombreEstudiante({ perfil: { nombres: ' ', apellidos: '' }, nombreCompleto: 'Ana Ruiz' })).toBe('Ana Ruiz')
    expect(nombreEstudiante({ perfil: null, nombreCompleto: '  ' })).toBeNull()
  })

  it('calcula las iniciales del avatar con la primera y la última palabra', () => {
    expect(iniciales('Estudiante De Prueba')).toBe('EP')
    expect(iniciales('Decanato')).toBe('D')
    expect(iniciales('')).toBe('')
  })
})
