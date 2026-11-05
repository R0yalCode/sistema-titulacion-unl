import { HttpResponse, http, type HttpHandler } from 'msw'
import { fixtureTokenPair } from './fixtures'

const TOKEN_URL = '*/api/v1/auth/token/'

export const handlers: HttpHandler[] = [
  http.post(TOKEN_URL, async ({ request }) => {
    const body = (await request.json()) as { username?: string; password?: string }

    if (body.username === 'estudiante.demo' && body.password === 'demo-valida') {
      return HttpResponse.json(fixtureTokenPair, { status: 200 })
    }

    return HttpResponse.json({ detail: 'No se encontró una cuenta activa con las credenciales dadas.' }, { status: 401 })
  }),
]
