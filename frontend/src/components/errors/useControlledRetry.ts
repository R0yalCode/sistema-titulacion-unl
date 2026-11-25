import { useEffect, useRef, useState } from 'react'

/** Espera progresiva para 503: 5 s, 10 s, 20 s, 40 s y como máximo 60 s. */
export const BACKOFF_BASE_S = 5
export const BACKOFF_MAX_S = 60

export function esperaTrasIntento(intento: number): number {
  return Math.min(BACKOFF_BASE_S * 2 ** Math.max(0, intento - 1), BACKOFF_MAX_S)
}

export type ControlledRetry = {
  /** Lanza un reintento; se ignora si hay uno en curso o falta esperar. */
  run: () => void
  pending: boolean
  /** Segundos que faltan para permitir el siguiente intento (0 si ya se puede). */
  waitSeconds: number
}

/**
 * Reintento solo a petición del usuario: nunca automático ni en bucle. Evita
 * dobles envíos mientras hay uno en curso y, con `backoff`, impone una espera
 * creciente tras cada intento para no saturar un servicio no disponible.
 * Pensado para consultas de lectura (refetch): las operaciones de escritura
 * no se reintentan desde aquí.
 */
export function useControlledRetry(retry: () => unknown, { backoff = false }: { backoff?: boolean } = {}): ControlledRetry {
  const [pending, setPending] = useState(false)
  const [waitSeconds, setWaitSeconds] = useState(0)
  const intentos = useRef(0)
  const montado = useRef(true)

  useEffect(() => {
    montado.current = true
    return () => {
      montado.current = false
    }
  }, [])

  useEffect(() => {
    if (waitSeconds <= 0) {
      return
    }
    const id = window.setTimeout(() => setWaitSeconds((s) => Math.max(0, s - 1)), 1000)
    return () => window.clearTimeout(id)
  }, [waitSeconds])

  function run() {
    if (pending || waitSeconds > 0) {
      return
    }
    intentos.current += 1
    setPending(true)
    Promise.resolve()
      .then(retry)
      .catch(() => undefined)
      .finally(() => {
        if (!montado.current) {
          return
        }
        setPending(false)
        if (backoff) {
          setWaitSeconds(esperaTrasIntento(intentos.current))
        }
      })
  }

  return { run, pending, waitSeconds }
}
