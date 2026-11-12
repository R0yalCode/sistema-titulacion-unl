export type Env = {
  readonly apiBaseUrl: string
  readonly demoMode: boolean
  readonly useMocks: boolean
  readonly appName: string
}

export class EnvError extends Error {}

function parseBoolean(value: string | undefined): boolean {
  return value === 'true'
}

function validateApiBaseUrl(value: string | undefined): string {
  if (!value) {
    throw new EnvError('VITE_API_BASE_URL es obligatoria y no fue definida.')
  }

  let url: URL
  try {
    url = new URL(value)
  } catch {
    throw new EnvError(`VITE_API_BASE_URL no es una URL absoluta válida: "${value}".`)
  }

  if (url.protocol !== 'http:' && url.protocol !== 'https:') {
    throw new EnvError(`VITE_API_BASE_URL debe usar http o https: "${value}".`)
  }

  if (value.endsWith('/')) {
    throw new EnvError(`VITE_API_BASE_URL no debe terminar en barra: "${value}".`)
  }

  return value
}

export function parseEnv(source: Record<string, string | undefined>): Env {
  return Object.freeze({
    apiBaseUrl: validateApiBaseUrl(source.VITE_API_BASE_URL),
    demoMode: parseBoolean(source.VITE_DEMO_MODE),
    useMocks: parseBoolean(source.VITE_USE_MOCKS),
    appName: source.VITE_APP_NAME || 'SGT-SIAAF',
  })
}

export function getEnv(): Env {
  return parseEnv(import.meta.env as unknown as Record<string, string | undefined>)
}
