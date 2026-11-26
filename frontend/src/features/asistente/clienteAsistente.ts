import { createContext } from 'react'

/**
 * Contrato del cliente del asistente (AX-D). La interfaz queda preparada para
 * el servicio de IA local que diseñe AX-E (Ollama + RAG). Hoy **no existe**
 * ningún endpoint del asistente en el backend (`openapi.yaml`), así que la
 * única implementación es `clienteNoDisponible`: no hace peticiones de red,
 * no inventa una URL ni simula respuestas.
 */

/** Fuente documental de una respuesta (los campos que no existan se omiten). */
export type FuenteAsistente = {
  titulo: string
  version?: string
  pagina?: number
  seccion?: string
  vigente?: boolean
}

export type RespuestaAsistente = {
  texto: string
  fuentes: FuenteAsistente[]
}

export interface ClienteAsistente {
  consultar(pregunta: string): Promise<RespuestaAsistente>
}

export class AsistenteNoDisponibleError extends Error {
  constructor() {
    super('El servicio del asistente con IA aún no está disponible.')
    this.name = 'AsistenteNoDisponibleError'
  }
}

/** Implementación vigente: el servicio no existe todavía. */
export const clienteNoDisponible: ClienteAsistente = {
  consultar: () => Promise.reject(new AsistenteNoDisponibleError()),
}

/**
 * Permite sustituir el cliente (por el real cuando exista, o en pruebas) sin
 * tocar los componentes.
 */
export const ClienteAsistenteContext = createContext<ClienteAsistente>(clienteNoDisponible)
