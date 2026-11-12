import { request } from '../client'

/** Salida 201 de `InformeAptitudSerializer` (verificado 2026-11-12). */
export type InformeAptitud = {
  id: string
  expediente: string
  expediente_numero: string
  numero_providencia: string
  emisor: string
  emisor_nombre: string
  emisor_username: string
  dictamen: string
  archivo_informe_path: string
  fecha_emision: string
  fecha_actualizacion: string
}

/** Salida 201 de `DeclaratoriaAptitudSerializer` (verificado 2026-11-12). */
export type DeclaratoriaAptitud = {
  id: string
  expediente: string
  expediente_numero: string
  numero_memorando: string
  decano: string
  decano_nombre: string
  decano_username: string
  archivo_memorando_firmado_path: string
  fecha_declaratoria: string
  fecha_actualizacion: string
}

/**
 * `POST /api/v1/informes/` (FE-T804; `InformeViewSet.create` y
 * `services/emitir_informe.py`). Cuerpo `{expediente_id, dictamen,
 * fundamentacion?}`. Solo SECRETARIO_ABOGADO: el servicio rechaza a
 * ANALISTA_APOYO aunque RBAC le dé ámbito BORRADOR. El servicio **solo acepta
 * `APTO`** (con "NO APTO" responde 400 `expediente_invalido_para_informe`).
 * Exige el checklist 100 % VERIFICADO (400 con `requisitos_pendientes`).
 * Desde OBSERVADA responde 409 `regla_pendiente_o1` (O-1, no es BE-11).
 * También puede responder 400 `informe_ya_emitido` o `transicion_invalida` y
 * 404 `expediente_no_encontrado`. 201 → expediente INFORME_EMITIDO.
 */
export function emitirInforme(expedienteId: string, fundamentacion: string): Promise<InformeAptitud> {
  return request<InformeAptitud>('/api/v1/informes/', {
    method: 'POST',
    body: { expediente_id: expedienteId, dictamen: 'APTO', fundamentacion },
  })
}

/**
 * `POST /api/v1/declaratorias/` (FE-T805; `DeclaratoriaViewSet.create` y
 * `services/declarar_aptitud.py`): multipart con `expediente_id`,
 * `archivo_memorando` (PDF firmado) y `numero_memorando` opcional (si se
 * omite, el backend lo genera como MEM-162-AAAA-NNN). Solo DECANO (RBAC) con
 * el expediente en INFORME_EMITIDO y un informe existente. Errores: 400
 * `declaratoria_ya_emitida`, `expediente_invalido_para_declaratoria`,
 * `pdf_invalido` o `transicion_invalida`; 403; 404. 201 → DECLARADA_APTA.
 */
export function registrarDeclaratoria(
  expedienteId: string,
  archivo: File,
  numeroMemorando: string,
): Promise<DeclaratoriaAptitud> {
  const body = new FormData()
  body.append('expediente_id', expedienteId)
  body.append('archivo_memorando', archivo)
  if (numeroMemorando.trim()) {
    body.append('numero_memorando', numeroMemorando.trim())
  }
  return request<DeclaratoriaAptitud>('/api/v1/declaratorias/', { method: 'POST', body })
}
