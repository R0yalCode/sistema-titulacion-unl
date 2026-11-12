import { getAccessToken } from '@/auth/storage'
import { ApiRequestError, networkApiError, normalizeApiError } from '@/api/errors'
import { getEnv } from './env'

function extractFilename(contentDisposition: string | null, fallback: string): string {
  if (!contentDisposition) {
    return fallback
  }
  const match = /filename="?([^";]+)"?/i.exec(contentDisposition)
  return match?.[1] ?? fallback
}

async function parseErrorBody(response: Response): Promise<unknown> {
  try {
    return await response.json()
  } catch {
    return null
  }
}

/**
 * Descarga autenticada reutilizable (FE-T408): usa el mismo mecanismo de
 * sesión que `api/client.ts` (Bearer en `Authorization`, nunca en la URL),
 * obtiene el `Blob` real y lee el nombre de archivo de `Content-Disposition`
 * cuando el backend lo envía. No asume que la respuesta es siempre un PDF:
 * el `Content-Type` real del documento se conserva en el `Blob`.
 */
export async function fetchAuthenticatedFile(
  path: string,
  fallbackFilename: string,
): Promise<{ blob: Blob; filename: string }> {
  const env = getEnv()
  const token = getAccessToken()
  const headers: Record<string, string> = {}
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  let response: Response
  try {
    response = await fetch(`${env.apiBaseUrl}${path}`, { headers })
  } catch {
    throw new ApiRequestError(networkApiError())
  }

  if (!response.ok) {
    const parsedBody = await parseErrorBody(response)
    throw new ApiRequestError(normalizeApiError(response.status, parsedBody))
  }

  const blob = await response.blob()
  const filename = extractFilename(response.headers.get('content-disposition'), fallbackFilename)
  return { blob, filename }
}

/** Dispara la descarga de un `Blob` ya obtenido, mediante un enlace temporal revocado tras usarlo. */
export function triggerBlobDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
