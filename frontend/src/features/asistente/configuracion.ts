/**
 * Configuración del asistente institucional (AX-D, DK-010).
 *
 * Mascota PROVISIONAL (decisión del responsable, 2026-11-26): se reutiliza
 * `mascota-404.png` (oso con signos de interrogación), autorizada por DEC-15
 * solo como ilustración complementaria, sin modificar el recurso original.
 * Para sustituirla por una mascota propia del asistente basta con cambiar
 * `src`, `ancho` y `alto` aquí.
 */
export const ASISTENTE = {
  nombre: 'Asistente SGT-SIAAF',
  mascota: {
    src: '/assets/mascotas/mascota-404.png',
    ancho: 693,
    alto: 664,
    provisional: true,
  },
  /** Límite de la pregunta escrita (evita envíos desmesurados al futuro servicio). */
  longitudMaximaPregunta: 500,
} as const

/**
 * Rutas autenticadas donde se ofrece el asistente. Las vistas públicas
 * (landing, login, recuperación) y las de error quedan fuera.
 */
export const PREFIJOS_RUTAS_CON_ASISTENTE = [
  '/estudiante',
  '/expedientes',
  '/bandeja',
  '/notificaciones',
  '/perfil',
  '/no-habilitado',
] as const
