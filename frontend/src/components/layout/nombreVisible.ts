/**
 * Nombre que se muestra del usuario autenticado (AX-C, DK-010).
 *
 * Solo usa datos reales de la API:
 *  - Estudiante: `perfil-academico` entrega `nombres` y `apellidos` por
 *    separado, así que se puede tomar el primer nombre y el primer apellido
 *    sin adivinar. Si no está disponible, se usa `nombre_completo` de
 *    `mi-tramite` tal cual, **sin partirlo** (una cadena única no permite
 *    saber dónde terminan los nombres).
 *  - Funcionarios: no existe endpoint con su nombre (BE-01), por lo que se
 *    muestra su rol.
 */

/** Partículas que forman parte del apellido ("De la Cruz", "Del Pozo"). */
const PARTICULAS = new Set(['de', 'del', 'la', 'las', 'los', 'y', 'san', 'santa', 'van', 'von', 'da', 'di'])

function palabras(texto: string | null | undefined): string[] {
  return (texto ?? '').trim().split(/\s+/).filter(Boolean)
}

/** Primer nombre de `nombres` ("María José" → "María"). */
export function primerNombre(nombres: string | null | undefined): string | null {
  return palabras(nombres)[0] ?? null
}

/**
 * Primer apellido de `apellidos`, conservando las partículas iniciales:
 * "Pérez López" → "Pérez"; "De la Cruz Torres" → "De la Cruz";
 * "Del Pozo Ruiz" → "Del Pozo".
 */
export function primerApellido(apellidos: string | null | undefined): string | null {
  const partes = palabras(apellidos)
  const resultado: string[] = []
  for (const parte of partes) {
    resultado.push(parte)
    if (!PARTICULAS.has(parte.toLocaleLowerCase('es'))) {
      break
    }
  }
  return resultado.length > 0 ? resultado.join(' ') : null
}

/** "Primer nombre Primer apellido" o `null` si faltan ambos datos. */
export function nombreCorto(nombres: string | null | undefined, apellidos: string | null | undefined): string | null {
  const corto = [primerNombre(nombres), primerApellido(apellidos)].filter(Boolean).join(' ')
  return corto || null
}

export type FuentesNombreEstudiante = {
  perfil?: { nombres: string; apellidos: string } | null
  nombreCompleto?: string | null
}

/** Nombre del estudiante según la fuente disponible, sin inventar ni partir cadenas. */
export function nombreEstudiante({ perfil, nombreCompleto }: FuentesNombreEstudiante): string | null {
  if (perfil) {
    const corto = nombreCorto(perfil.nombres, perfil.apellidos)
    if (corto) {
      return corto
    }
  }
  const completo = nombreCompleto?.trim()
  return completo || null
}

/** Iniciales para el avatar: primera y última palabra con letras ("Ana De Prueba" → "AP"). */
export function iniciales(nombre: string): string {
  const partes = nombre.split(/\s+/).filter((parte) => /\p{L}/u.test(parte))
  const primera = partes[0]?.[0] ?? ''
  const ultima = partes.length > 1 ? (partes[partes.length - 1]?.[0] ?? '') : ''
  return `${primera}${ultima}`.toUpperCase()
}
