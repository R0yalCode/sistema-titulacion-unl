/**
 * Catálogo único de las ocho vistas de error del SIAAF (referencia visual:
 * prototipos/vistas-errores-unl). Cada vista es una configuración del mismo
 * `ErrorView`: aquí solo viven los textos aprobados, la mascota y las
 * etiquetas de las acciones; la navegación la decide quien lo usa.
 *
 * Mascotas: los cinco PNG autorizados en DEC-15 (`public/assets/mascotas`).
 * Los prototipos de Stitch reutilizan exactamente esas cinco imágenes con
 * el mismo reparto (404 y datos, 500 y sin conexión, 503 y tiempo agotado).
 */

export type ErrorKind =
  | 'not-found'
  | 'unauthorized'
  | 'forbidden'
  | 'server'
  | 'unavailable'
  | 'offline'
  | 'timeout'
  | 'data'

export type ErrorCopy = {
  /** Código HTTP real que representa la vista; `null` si no es un estado HTTP. */
  code: string | null
  /** Contexto breve sobre el título. */
  eyebrow: string
  title: string
  message: string
  mascot: string
  primaryLabel: string
  secondaryLabel: string
}

const MASCOTAS = '/assets/mascotas'

export const ERROR_CATALOG: Record<ErrorKind, ErrorCopy> = {
  'not-found': {
    code: '404',
    eyebrow: 'Error 404 · Navegación',
    title: 'Página no encontrada',
    message:
      'Lo sentimos, no encontramos la página que estás buscando. Es posible que la dirección haya cambiado o que el enlace ya no esté disponible.',
    mascot: `${MASCOTAS}/mascota-404.png`,
    primaryLabel: 'Ir al inicio',
    secondaryLabel: 'Intentar nuevamente',
  },
  unauthorized: {
    code: '401',
    eyebrow: 'Error 401 · Autenticación requerida',
    title: 'Necesitas iniciar sesión',
    message:
      'Tu sesión no está activa o necesitas autenticarte para continuar. Inicia sesión nuevamente para acceder al sistema.',
    mascot: `${MASCOTAS}/mascota-401.png`,
    primaryLabel: 'Iniciar sesión',
    secondaryLabel: 'Ir al inicio',
  },
  forbidden: {
    code: '403',
    eyebrow: 'Error 403 · Acceso restringido',
    title: 'No tienes permisos para acceder',
    message:
      'Tu cuenta no dispone de los permisos necesarios para acceder a esta sección. Si consideras que se trata de un error, contacta con el administrador del sistema.',
    mascot: `${MASCOTAS}/mascota-403.png`,
    primaryLabel: 'Volver a mi panel',
    secondaryLabel: 'Ir al inicio',
  },
  server: {
    code: '500',
    eyebrow: 'Error 500 · Error interno',
    title: 'Algo salió mal',
    message: 'Se produjo un error inesperado al procesar tu solicitud. Puedes intentar nuevamente en unos momentos.',
    mascot: `${MASCOTAS}/mascota-500.png`,
    primaryLabel: 'Intentar nuevamente',
    secondaryLabel: 'Ir al inicio',
  },
  unavailable: {
    code: '503',
    eyebrow: 'Error 503 · Servicio no disponible',
    title: 'El servicio no está disponible',
    message:
      'Estamos teniendo dificultades para atender tu solicitud en este momento. Por favor, inténtalo nuevamente más tarde.',
    mascot: `${MASCOTAS}/mascota-503.png`,
    primaryLabel: 'Reintentar',
    secondaryLabel: 'Ir al inicio',
  },
  offline: {
    code: null,
    eyebrow: 'Conectividad',
    title: 'Sin conexión',
    message: 'Parece que se interrumpió tu conexión. Verifica tu conexión a internet e inténtalo nuevamente.',
    mascot: `${MASCOTAS}/mascota-500.png`,
    primaryLabel: 'Reintentar conexión',
    secondaryLabel: 'Ir al inicio',
  },
  timeout: {
    code: null,
    eyebrow: 'Tiempo de espera agotado',
    title: 'La solicitud está tardando demasiado',
    message: 'No pudimos completar la solicitud dentro del tiempo esperado. Inténtalo nuevamente.',
    mascot: `${MASCOTAS}/mascota-503.png`,
    primaryLabel: 'Intentar nuevamente',
    secondaryLabel: 'Ir al inicio',
  },
  data: {
    code: null,
    eyebrow: 'Carga de información',
    title: 'No pudimos cargar la información',
    message: 'En este momento no es posible mostrar la información solicitada. Inténtalo nuevamente.',
    mascot: `${MASCOTAS}/mascota-404.png`,
    primaryLabel: 'Volver a cargar',
    secondaryLabel: 'Ir al inicio',
  },
}
