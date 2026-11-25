import { useSyncExternalStore } from 'react'

function suscribir(aviso: () => void): () => void {
  window.addEventListener('online', aviso)
  window.addEventListener('offline', aviso)
  return () => {
    window.removeEventListener('online', aviso)
    window.removeEventListener('offline', aviso)
  }
}

function leer(): boolean {
  return navigator.onLine
}

/**
 * Estado de red que informa el navegador (`online`/`offline`). Un único par de
 * listeners por componente, que React quita al desmontar. `true` solo
 * significa que el dispositivo tiene red, no que el backend responda: la
 * vista nunca lo presenta como conexión restablecida sin una petición real.
 */
export function useOnlineStatus(): boolean {
  return useSyncExternalStore(suscribir, leer, () => true)
}
