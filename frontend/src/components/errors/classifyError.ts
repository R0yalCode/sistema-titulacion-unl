import { ApiRequestError, type ApiError } from '@/api/errors'
import type { ErrorKind } from './errorCatalog'

/**
 * Clasifica un error real del cliente HTTP (`request()` lanza
 * `ApiRequestError`) en una de las ocho vistas. No inventa estados: solo usa
 * el código HTTP y las marcas `isTimeout`/`isNetworkError` que ya fija
 * `api/client.ts` (timeout propio de 30 s con AbortController).
 *
 * - 401 → unauthorized, 403 → forbidden, 404 → not-found.
 * - Timeout del cliente, 408 o 504 → timeout.
 * - Error de red: offline solo si el navegador informa que no hay conexión
 *   (`navigator.onLine === false`); si dice que hay red, el servidor no
 *   respondió → unavailable. `onLine` nunca se toma como prueba de que el
 *   backend esté accesible.
 * - 502/503 → unavailable; 500 y demás 5xx → server.
 * - Cualquier otro caso (4xx de datos, respuestas inesperadas, errores que no
 *   son de la API) → data.
 */
export function classifyError(error: unknown, online: boolean = navigatorOnline()): ErrorKind {
  const api = apiErrorOf(error)
  if (!api) {
    return 'data'
  }
  if (api.isTimeout || api.status === 408 || api.status === 504) {
    return 'timeout'
  }
  if (api.isNetworkError) {
    return online ? 'unavailable' : 'offline'
  }
  switch (api.status) {
    case 401:
      return 'unauthorized'
    case 403:
      return 'forbidden'
    case 404:
      return 'not-found'
    case 502:
    case 503:
      return 'unavailable'
  }
  if (api.status >= 500) {
    return 'server'
  }
  return 'data'
}

export function apiErrorOf(error: unknown): ApiError | null {
  return error instanceof ApiRequestError ? error.error : null
}

/**
 * Mensaje del backend apto para el usuario: solo el `detail` textual de DRF
 * (nunca trazas ni cuerpos completos). Varias reglas de negocio responden 500
 * con un mensaje legible (INC-21), así que se conserva también en `server`.
 */
export function backendDetail(error: unknown): string | null {
  const api = apiErrorOf(error)
  if (!api || [401, 403, 404].includes(api.status)) {
    return null
  }
  const raw = api.raw
  if (typeof raw === 'object' && raw !== null && 'detail' in raw) {
    const detail = (raw as { detail: unknown }).detail
    return typeof detail === 'string' && detail.trim() ? detail : null
  }
  return null
}

function navigatorOnline(): boolean {
  return typeof navigator === 'undefined' || navigator.onLine !== false
}
