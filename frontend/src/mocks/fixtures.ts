function base64UrlEncode(value: string): string {
  return btoa(value).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
}

function buildFixtureJwt(payload: Record<string, unknown>): string {
  const header = base64UrlEncode(JSON.stringify({ alg: 'HS256', typ: 'JWT' }))
  const body = base64UrlEncode(JSON.stringify(payload))
  return `${header}.${body}.fixture-signature`
}

export const fixtureEstudianteAccessToken = buildFixtureJwt({
  cedula: '0000000000',
  roles: ['ESTUDIANTE'],
  exp: Math.floor(Date.now() / 1000) + 3600,
})

export const fixtureTokenPair = {
  access: fixtureEstudianteAccessToken,
  refresh: 'fixture-refresh-no-se-persiste',
}
