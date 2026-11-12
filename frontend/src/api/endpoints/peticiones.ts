import { request } from '../client'

/**
 * Valores reales de `ESTADOS_PETICION_CHOICES`
 * (`backend/src/apps/peticiones/adapters/models.py`, verificado 2026-11-12).
 * No existen estados intermedios como "En revisión" (CA-G-01).
 */
export type EstadoPeticion =
  | 'PENDIENTE'
  | 'SOLICITADO'
  | 'CARGADO'
  | 'LEGALIZADO'
  | 'VERIFICADO'
  | 'OBSERVADO'

/** Salida 200 de `SolicitarEmisionResponseSerializer`. */
export type PeticionSolicitada = {
  id: string
  requisito_codigo: string
  requisito_nombre: string
  estado_peticion: string
  dependencia_emisora: string
  fecha_solicitud: string | null
}

/** Salida 201 de `CargarDocumentoResponseSerializer`. */
export type DocumentoCargado = {
  id: string
  peticion: string
  version: number
  archivo_path: string
  nombre_original: string
  tamanio_bytes: number
  hash_sha256: string
  tipo_mime: string
  subido_por: string
  subido_por_username: string
  fecha_carga: string
  es_vigente: boolean
}

/**
 * `POST /api/v1/peticiones/{id}/solicitar-emision/` (FE-T502; verificado contra
 * `PeticionViewSet.solicitar_emision` y `services/solicitar_emision.py`):
 * 200 con la petición en `SOLICITADO`. Sin cuerpo de entrada.
 * - 400 `expediente_estado_invalido`: el expediente no está en BORRADOR/OBSERVADA.
 * - 400 `estado_peticion_invalido`: la petición no está en PENDIENTE.
 * - 403: RBAC (`peticiones` POST solo ESTUDIANTE propietario o ADMINISTRADOR) o
 *   regla del servicio (solo el estudiante propietario o la Secretaría de Carrera).
 * - 404 `peticion_no_encontrada`: no existe o está fuera del ámbito del usuario.
 */
export function solicitarEmision(peticionId: string): Promise<PeticionSolicitada> {
  return request<PeticionSolicitada>(`/api/v1/peticiones/${peticionId}/solicitar-emision/`, {
    method: 'POST',
  })
}

/**
 * `POST /api/v1/peticiones/{id}/documento/` (FE-T503; verificado contra
 * `PeticionViewSet.cargar_documento` y `services/cargar_documento.py`):
 * 201 con la nueva versión vigente; `multipart/form-data` con el campo exacto
 * `archivo`. La petición pasa a `CARGADO`.
 * - 400: estado no permite carga (permitidos PENDIENTE, SOLICITADO, OBSERVADO,
 *   CARGADO) o PDF inválido (`pdf_validation_error`; máximo 10 MB).
 * - 403: solo el estudiante propietario o la Secretaría de Carrera de la misma
 *   carrera en peticiones asignadas a la Secretaría (VULN-002).
 * - 404 `peticion_no_encontrada`.
 */
export function cargarDocumento(peticionId: string, archivo: File): Promise<DocumentoCargado> {
  const body = new FormData()
  body.append('archivo', archivo)
  return request<DocumentoCargado>(`/api/v1/peticiones/${peticionId}/documento/`, {
    method: 'POST',
    body,
  })
}
