/**
 * Detecta preguntas sobre normativa, requisitos oficiales, fechas o
 * resoluciones (AX-D). El asistente no responde esas consultas como si fueran
 * oficiales: hasta que exista un RAG con documentación aprobada, las remite a
 * los canales institucionales.
 *
 * Es una heurística deliberadamente amplia: un falso positivo solo añade la
 * recomendación de acudir a los canales oficiales; un falso negativo nunca
 * produce una respuesta inventada, porque el servicio no está disponible.
 */
const PATRONES_NORMATIVOS = [
  /\breglamentos?\b/,
  /\bnormativas?\b/,
  /\bnormas?\b/,
  /\bresoluci(?:o|ó)n(?:es)?\b/,
  /\brequisitos?\b/,
  /\bart(?:i|í)culos?\b/,
  /\bart\.\s*\d+/,
  /\bley(?:es)?\b/,
  /\bestatutos?\b/,
  /\bdisposici(?:o|ó)n(?:es)?\b/,
  /\bplazos?\b/,
  /\bfechas?\b/,
  /\bcalendario\b/,
  /\bconvocatorias?\b/,
  /\bmodalidad(?:es)?\b/,
  /\bexamen complexivo\b/,
  /\barancel(?:es)?\b/,
]

export function esConsultaNormativa(pregunta: string): boolean {
  const texto = pregunta.toLocaleLowerCase('es')
  return PATRONES_NORMATIVOS.some((patron) => patron.test(texto))
}

export const MENSAJE_CANALES_OFICIALES =
  'Las consultas sobre reglamentos, requisitos oficiales, fechas, resoluciones o normativa deben resolverse en los canales institucionales oficiales de la Universidad Nacional de Loja, como la Secretaría de tu carrera. El asistente todavía no consulta documentación institucional aprobada, así que no puede responderlas con validez oficial.'

export const MENSAJE_NO_DISPONIBLE =
  'El asistente con IA aún no está disponible. Mientras tanto, revisa las preguntas frecuentes o consulta a la Secretaría de tu carrera.'
