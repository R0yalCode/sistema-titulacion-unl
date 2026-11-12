const RECENT_EXPEDIENTES_KEY = 'sgt.recent_expedientes'
const MAX_RECENT_EXPEDIENTES = 5

export type RecentExpediente = {
  id: string
  numeroExpediente?: string
  visitadoEn: string
}

function isRecentExpediente(value: unknown): value is RecentExpediente {
  return (
    typeof value === 'object' &&
    value !== null &&
    typeof (value as Record<string, unknown>).id === 'string' &&
    typeof (value as Record<string, unknown>).visitadoEn === 'string' &&
    ((value as Record<string, unknown>).numeroExpediente === undefined ||
      typeof (value as Record<string, unknown>).numeroExpediente === 'string')
  )
}

/**
 * Accesos rápidos locales (FE-T204): mitigan la ausencia de un endpoint de
 * historial del estudiante (BE-05). No sustituyen un historial oficial: solo
 * recuerdan, en esta sesión del navegador, qué expedientes visitó el
 * estudiante para poder volver a abrirlos por su `id` real.
 */
export function getRecentExpedientes(): RecentExpediente[] {
  const raw = sessionStorage.getItem(RECENT_EXPEDIENTES_KEY)
  if (!raw) {
    return []
  }

  try {
    const parsed = JSON.parse(raw)
    if (!Array.isArray(parsed)) {
      return []
    }
    return parsed.filter(isRecentExpediente)
  } catch {
    return []
  }
}

export function recordVisitedExpediente(id: string, numeroExpediente?: string): void {
  const current = getRecentExpedientes().filter((entry) => entry.id !== id)
  const next: RecentExpediente[] = [
    { id, numeroExpediente, visitadoEn: new Date().toISOString() },
    ...current,
  ].slice(0, MAX_RECENT_EXPEDIENTES)

  sessionStorage.setItem(RECENT_EXPEDIENTES_KEY, JSON.stringify(next))
}

export function clearRecentExpedientes(): void {
  sessionStorage.removeItem(RECENT_EXPEDIENTES_KEY)
}

const NUEVA_SOLICITUD_DRAFT_KEY = 'sgt.nueva_solicitud_draft'

/**
 * Borrador local del formulario de nueva solicitud (FE-T304): solo guarda
 * `carrera_id`, nunca credenciales ni tokens.
 */
export function getNuevaSolicitudDraft(): string | null {
  return sessionStorage.getItem(NUEVA_SOLICITUD_DRAFT_KEY)
}

export function saveNuevaSolicitudDraft(carreraId: string): void {
  sessionStorage.setItem(NUEVA_SOLICITUD_DRAFT_KEY, carreraId)
}

export function clearNuevaSolicitudDraft(): void {
  sessionStorage.removeItem(NUEVA_SOLICITUD_DRAFT_KEY)
}
