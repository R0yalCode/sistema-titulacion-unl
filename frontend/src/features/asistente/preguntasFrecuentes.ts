/**
 * Preguntas frecuentes del asistente (AX-D). Configurables: se editan aquí
 * sin tocar los componentes.
 *
 * Alcance aprobado por el responsable (2026-11-26): **solo el uso del
 * SGT-SIAAF**. Las respuestas describen pantallas y acciones que existen en
 * la aplicación y enlazan únicamente a rutas reales del router. No contienen
 * requisitos, plazos, fechas ni normativa institucional: esas consultas se
 * remiten a los canales oficiales hasta que exista un RAG con documentación
 * aprobada (AX-E).
 */

export type PublicoPregunta = 'estudiante' | 'funcionario' | 'todos'

export type EnlacePregunta = {
  etiqueta: string
  /** Ruta real de la aplicación (ver app/router.tsx). */
  destino: string
}

export type PreguntaFrecuente = {
  id: string
  pregunta: string
  /** Párrafos de la respuesta. */
  respuesta: string[]
  enlaces: EnlacePregunta[]
  publico: PublicoPregunta
}

export const PREGUNTAS_FRECUENTES: PreguntaFrecuente[] = [
  {
    id: 'iniciar-tramite',
    publico: 'estudiante',
    pregunta: '¿Cómo inicio mi proceso de titulación?',
    respuesta: [
      'En el menú lateral, elige «Nueva solicitud». Verás los datos de tu perfil académico y, si están completos y validados, podrás pulsar «Crear solicitud».',
      'Si el perfil muestra un aviso (por ejemplo, carrera inactiva o datos incompletos), la solicitud no se puede crear desde el sistema: consulta a la Secretaría de tu carrera.',
    ],
    enlaces: [{ etiqueta: 'Ir a Nueva solicitud', destino: '/estudiante/solicitud/nueva' }],
  },
  {
    id: 'estado-tramite',
    publico: 'estudiante',
    pregunta: '¿Cómo consulto el estado de mi trámite?',
    respuesta: [
      'En «Inicio» ves el estado actual, el progreso por etapas y las acciones pendientes. Para el detalle completo, abre «Mi trámite» en el menú lateral: allí está el seguimiento con cada etapa y sus fechas registradas.',
    ],
    enlaces: [{ etiqueta: 'Ir a Inicio', destino: '/estudiante' }],
  },
  {
    id: 'cargar-documentos',
    publico: 'estudiante',
    pregunta: '¿Cómo cargo un documento?',
    respuesta: [
      'Abre «Documentos» en el menú lateral (aparece cuando ya tienes un trámite). En cada requisito encontrarás «Cargar documento» o «Solicitar emisión», según cómo se obtenga ese documento.',
      'El sistema acepta archivos PDF de hasta 10 MB. Cuando cargues todo lo necesario, envía el expediente desde «Mi trámite».',
    ],
    enlaces: [{ etiqueta: 'Ir a Inicio', destino: '/estudiante' }],
  },
  {
    id: 'consultar-requisitos',
    publico: 'estudiante',
    pregunta: '¿Dónde veo qué documentos me faltan?',
    respuesta: [
      'En «Inicio», la sección «Necesitas completar» lista los documentos de tu trámite que aún no tienen archivo. El mismo detalle aparece en «Documentos».',
      'Para conocer qué requisitos exige la normativa de titulación, consulta los canales oficiales de la Universidad Nacional de Loja.',
    ],
    enlaces: [{ etiqueta: 'Ir a Inicio', destino: '/estudiante' }],
  },
  {
    id: 'notificaciones-estudiante',
    publico: 'estudiante',
    pregunta: '¿Cómo sé si tengo avisos nuevos?',
    respuesta: [
      'La campana de la barra superior muestra un contador con tus notificaciones sin leer, y el menú lateral repite el número junto a «Notificaciones». En esa sección, cada aviso sin leer tiene el botón «Marcar como leída».',
    ],
    enlaces: [{ etiqueta: 'Ir a Notificaciones', destino: '/estudiante/notificaciones' }],
  },
  {
    id: 'bandeja-funcionario',
    publico: 'funcionario',
    pregunta: '¿Cómo uso la bandeja de expedientes?',
    respuesta: [
      'La «Bandeja de trabajo» muestra los expedientes que requieren la intervención de tu rol, con su estado y su fecha límite de atención. Abre un expediente para ver su detalle y las acciones que tu rol tiene permitidas.',
    ],
    enlaces: [{ etiqueta: 'Ir a la bandeja', destino: '/bandeja' }],
  },
  {
    id: 'notificaciones-funcionario',
    publico: 'funcionario',
    pregunta: '¿Dónde veo mis notificaciones?',
    respuesta: [
      'La campana de la barra superior muestra el número de notificaciones sin leer. En «Notificaciones» cada aviso enlaza con su expediente y, si no lo has leído, tiene el botón «Marcar como leída».',
    ],
    enlaces: [{ etiqueta: 'Ir a Notificaciones', destino: '/notificaciones' }],
  },
  {
    id: 'navegar-modulos',
    publico: 'todos',
    pregunta: '¿Cómo me muevo por el sistema?',
    respuesta: [
      'El menú lateral reúne las secciones disponibles para tu rol; solo verás las que puedes usar. Puedes contraerlo con el botón junto al logo. Tu nombre, en la esquina superior derecha, abre el menú con «Mi perfil», «Cambiar contraseña» y «Cerrar sesión».',
      'El botón del engranaje, abajo a la izquierda, abre las herramientas de accesibilidad.',
    ],
    enlaces: [],
  },
  {
    id: 'errores-comunes',
    publico: 'todos',
    pregunta: '¿Qué hago si aparece un error o se cierra mi sesión?',
    respuesta: [
      'Si tu sesión expira, el sistema te lo indicará y deberás iniciar sesión de nuevo. Si una vista muestra «No tienes permisos para acceder», esa sección no está disponible para tu rol.',
      'Ante un error temporal, usa el botón «Reintentar» de la propia vista. Si perdiste el acceso a tu código de verificación, en la pantalla de inicio de sesión tienes «Restablecer doble factor de autenticación (2FA)».',
    ],
    enlaces: [],
  },
]

/** Preguntas visibles para el tipo de usuario autenticado. */
export function preguntasPara(esEstudiante: boolean): PreguntaFrecuente[] {
  const publico: PublicoPregunta = esEstudiante ? 'estudiante' : 'funcionario'
  return PREGUNTAS_FRECUENTES.filter((pregunta) => pregunta.publico === 'todos' || pregunta.publico === publico)
}
