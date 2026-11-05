export type JwtUser = {
  cedula: string
  roles: string[]
}

function base64UrlDecode(segment: string): string {
  const base64 = segment.replace(/-/g, '+').replace(/_/g, '/')
  const padded = base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), '=')
  return atob(padded)
}

export function decodeAccessToken(token: string): JwtUser | null {
  const parts = token.split('.')
  if (parts.length !== 3) {
    return null
  }

  let payload: unknown
  try {
    payload = JSON.parse(base64UrlDecode(parts[1] as string))
  } catch {
    return null
  }

  if (typeof payload !== 'object' || payload === null) {
    return null
  }

  const { cedula, roles, exp } = payload as Record<string, unknown>

  if (
    typeof cedula !== 'string' ||
    !Array.isArray(roles) ||
    !roles.every((role) => typeof role === 'string')
  ) {
    return null
  }

  if (typeof exp === 'number' && exp * 1000 <= Date.now()) {
    return null
  }

  return { cedula, roles: roles as string[] }
}
