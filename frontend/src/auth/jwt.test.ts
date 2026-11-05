import { describe, expect, it } from 'vitest'
import { decodeAccessToken } from '@/auth/jwt'

function base64UrlEncode(value: string): string {
  return btoa(value).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
}

function buildToken(payload: Record<string, unknown>): string {
  const header = base64UrlEncode(JSON.stringify({ alg: 'HS256', typ: 'JWT' }))
  const body = base64UrlEncode(JSON.stringify(payload))
  return `${header}.${body}.fixture-signature`
}

describe('decodeAccessToken', () => {
  it('decodifica un token válido con cedula y roles', () => {
    const token = buildToken({
      cedula: '1104567890',
      roles: ['ESTUDIANTE'],
      exp: Math.floor(Date.now() / 1000) + 3600,
    })

    expect(decodeAccessToken(token)).toEqual({ cedula: '1104567890', roles: ['ESTUDIANTE'] })
  })

  it('devuelve null si el token está expirado', () => {
    const token = buildToken({
      cedula: '1104567890',
      roles: ['ESTUDIANTE'],
      exp: Math.floor(Date.now() / 1000) - 10,
    })

    expect(decodeAccessToken(token)).toBeNull()
  })

  it('devuelve null si el token no tiene 3 segmentos', () => {
    expect(decodeAccessToken('solo-un-segmento')).toBeNull()
  })

  it('devuelve null si el payload no es JSON válido', () => {
    expect(decodeAccessToken('header.no-es-base64-json.signature')).toBeNull()
  })

  it('devuelve null si falta cedula', () => {
    const token = buildToken({ roles: ['ESTUDIANTE'] })
    expect(decodeAccessToken(token)).toBeNull()
  })

  it('devuelve null si roles no es un arreglo de strings', () => {
    const token = buildToken({ cedula: '1104567890', roles: 'ESTUDIANTE' })
    expect(decodeAccessToken(token)).toBeNull()
  })
})
