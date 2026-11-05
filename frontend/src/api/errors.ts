export type ApiError = {
  status: number
  code: string
  message: string
  fieldErrors?: Record<string, string[]>
  isNetworkError: boolean
  isTimeout: boolean
  raw?: unknown
}

const STATUS_CODES: Record<number, string> = {
  400: 'BAD_REQUEST',
  401: 'UNAUTHORIZED',
  403: 'FORBIDDEN',
  404: 'NOT_FOUND',
  409: 'CONFLICT',
  412: 'PRECONDITION_FAILED',
  422: 'UNPROCESSABLE_ENTITY',
  428: 'PRECONDITION_REQUIRED',
  429: 'TOO_MANY_REQUESTS',
  500: 'INTERNAL_SERVER_ERROR',
  502: 'BAD_GATEWAY',
  503: 'SERVICE_UNAVAILABLE',
  504: 'GATEWAY_TIMEOUT',
}

function statusToCode(status: number): string {
  return STATUS_CODES[status] ?? `HTTP_${status}`
}

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

export function normalizeApiError(status: number, body: unknown): ApiError {
  const base: ApiError = {
    status,
    code: statusToCode(status),
    message: 'Ocurrió un error inesperado.',
    isNetworkError: false,
    isTimeout: false,
    raw: body,
  }

  if (!isPlainObject(body)) {
    return base
  }

  if (typeof body.detail === 'string') {
    return { ...base, message: body.detail }
  }

  if (
    Array.isArray(body.non_field_errors) &&
    body.non_field_errors.every((item) => typeof item === 'string')
  ) {
    return { ...base, message: (body.non_field_errors as string[]).join(' ') }
  }

  const fieldErrors: Record<string, string[]> = {}
  for (const [key, value] of Object.entries(body)) {
    if (Array.isArray(value) && value.every((item) => typeof item === 'string')) {
      fieldErrors[key] = value as string[]
    }
  }

  if (Object.keys(fieldErrors).length > 0) {
    return { ...base, message: 'Revise los campos marcados.', fieldErrors }
  }

  return base
}

export function networkApiError(): ApiError {
  return {
    status: 0,
    code: 'NETWORK_ERROR',
    message: 'No se pudo conectar con el servidor. Verifique su conexión.',
    isNetworkError: true,
    isTimeout: false,
  }
}

export function timeoutApiError(): ApiError {
  return {
    status: 0,
    code: 'TIMEOUT',
    message: 'La solicitud tardó demasiado. Intente nuevamente.',
    isNetworkError: false,
    isTimeout: true,
  }
}

export class ApiRequestError extends Error {
  readonly error: ApiError

  constructor(error: ApiError) {
    super(error.message)
    this.error = error
  }
}
