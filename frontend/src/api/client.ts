import { getAccessToken } from '@/auth/storage'
import { getEnv } from '@/lib/env'
import { ApiRequestError, networkApiError, normalizeApiError, timeoutApiError } from './errors'

const DEFAULT_TIMEOUT_MS = 30_000

type RequestOptions = {
  method?: string
  body?: unknown
  signal?: AbortSignal
  timeoutMs?: number
  /** Omite el manejador global de 401 (p. ej. el propio endpoint de login). */
  skipAuthHandler?: boolean
}

let unauthorizedHandler: (() => void) | null = null

export function setUnauthorizedHandler(handler: (() => void) | null): void {
  unauthorizedHandler = handler
}

async function parseResponseBody(response: Response): Promise<unknown> {
  if (response.status === 204 || response.status === 205) {
    return null
  }

  const contentType = response.headers.get('content-type') ?? ''
  if (!contentType.includes('application/json')) {
    return null
  }

  const text = await response.text()
  return text ? JSON.parse(text) : null
}

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, signal, timeoutMs = DEFAULT_TIMEOUT_MS, skipAuthHandler = false } = options
  const env = getEnv()
  const controller = new AbortController()
  let timedOut = false
  const timeoutId = setTimeout(() => {
    timedOut = true
    controller.abort()
  }, timeoutMs)

  signal?.addEventListener('abort', () => controller.abort())

  const headers: Record<string, string> = {}
  const token = getAccessToken()
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  const isFormData = typeof FormData !== 'undefined' && body instanceof FormData
  if (body !== undefined && !isFormData) {
    headers['Content-Type'] = 'application/json'
  }

  let response: Response
  try {
    response = await fetch(`${env.apiBaseUrl}${path}`, {
      method,
      headers,
      body: isFormData ? (body as FormData) : body !== undefined ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    })
  } catch (error) {
    clearTimeout(timeoutId)
    // El fetch nativo de Node (undici) y jsdom exponen clases DOMException de
    // "realms" distintos; instanceof DOMException falla entre ellas, así que
    // se identifica el abort por error.name, que sí es estable.
    if (error instanceof Error && error.name === 'AbortError') {
      throw new ApiRequestError(timedOut ? timeoutApiError() : networkApiError())
    }
    throw new ApiRequestError(networkApiError())
  }
  clearTimeout(timeoutId)

  if (response.status === 401 && !skipAuthHandler) {
    unauthorizedHandler?.()
  }

  if (!response.ok) {
    const parsedBody = await parseResponseBody(response).catch(() => null)
    throw new ApiRequestError(normalizeApiError(response.status, parsedBody))
  }

  return (await parseResponseBody(response)) as T
}
