import type { PeticionInicializada } from '@/api/endpoints/expedientes'

/**
 * V-06 (FE-T601): no existe `GET /api/v1/peticiones/{id}/` (BE-02, verificado
 * 2026-11-12: `PeticionDocumentalViewSet` existe en `views.py` pero no está
 * registrado en `config/urls.py`). La petición se resuelve desde las
 * peticiones anidadas en `GET /api/v1/expedientes/{id}/`.
 */
export function buscarPeticion(
  peticiones: PeticionInicializada[],
  peticionId: string | undefined,
): PeticionInicializada | undefined {
  if (!peticionId) {
    return undefined
  }
  return peticiones.find((peticion) => peticion.id === peticionId)
}

const DESCRIPCION_ESTADO: Record<string, string> = {
  PENDIENTE: 'La emisión del documento todavía no se ha solicitado a la dependencia emisora.',
  SOLICITADO: 'Se solicitó la emisión del documento a la dependencia emisora; todavía no hay un documento cargado.',
  CARGADO: 'Hay un documento cargado para este requisito.',
  LEGALIZADO: 'El documento de este requisito consta como legalizado.',
  VERIFICADO: 'El documento de este requisito consta como verificado.',
  OBSERVADO:
    'La petición fue observada. El motivo de la observación no se muestra aquí porque la API no lo incluye en esta respuesta (BE-07).',
}

/**
 * Explica solo el estado actual real. No se infieren estados anteriores ni
 * hitos futuros: el backend no expone el historial de la petición (BE-02) y,
 * por ejemplo, una petición puede pasar a CARGADO sin haber estado SOLICITADO.
 */
export function describirEstadoPeticion(estado: string): string {
  return DESCRIPCION_ESTADO[estado] ?? `Estado informado por el sistema: ${estado}.`
}
