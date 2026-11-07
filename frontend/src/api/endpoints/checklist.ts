import { request } from '../client'

export type EstadoVerificacion = 'PENDIENTE' | 'VERIFICADO' | 'OBSERVADO'

export type ChecklistItem = {
  id: string
  expediente: string
  requisito: string
  requisito_codigo: string
  requisito_nombre: string
  estado_verificacion: EstadoVerificacion
  evaluado_por: string | null
  evaluado_por_username: string | null
  fecha_evaluacion: string | null
  fecha_creacion: string
  fecha_actualizacion: string
}

/**
 * `GET /api/v1/expedientes/{expediente_id}/checklist/` (verificado 2026-11-05
 * contra `ChecklistListViewSet`): array sin envoltorio de paginación
 * (`ReadOnlyModelViewSet.list()` por defecto, sin `pagination_class` propio
 * declarado en esta vista). ESTUDIANTE no está en `RBAC_MATRIX["checklist"]["GET"]`
 * → 403 real con `HasRolePermission.message` ("El rol del usuario no esta
 * autorizado..."). Por eso FE-T403 no ejecuta esta query para ESTUDIANTE.
 */
export function listChecklist(expedienteId: string): Promise<ChecklistItem[]> {
  return request<ChecklistItem[]>(`/api/v1/expedientes/${expedienteId}/checklist/`)
}

export type EvaluarChecklistRequest = {
  estado_verificacion: 'VERIFICADO' | 'OBSERVADO'
  motivo_observacion?: string
}

/**
 * `PUT /api/v1/checklist/{id}/` (verificado contra `ChecklistViewSet.update`
 * + `evaluar_checklist.py`): 200 real. **Discrepancia real documentada**
 * (INC-21): `ChecklistVerificationNotFoundError` se re-lanza como
 * `APIException` genérica → **500**, no 404. `InvalidVerificationStateError`
 * (incl. motivo faltante en OBSERVADO, defensa redundante con la validación
 * del propio serializer) / `ExpedienteNotInVerificationError` /
 * `VerificationAlreadyCompletedError` → 400. `UserNotAuthorizedError` → 403.
 */
export function evaluarChecklist(
  id: string,
  payload: EvaluarChecklistRequest,
): Promise<ChecklistItem> {
  return request<ChecklistItem>(`/api/v1/checklist/${id}/`, { method: 'PUT', body: payload })
}

export type SubsanacionResponse = {
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
 * `POST /api/v1/checklist/{id}/subsanar/` (verificado contra
 * `ChecklistViewSet.subsanar` + `subsanar_requisito.py`): 201 real,
 * `multipart/form-data` con el campo exacto `archivo`. **Discrepancia real
 * documentada** (INC-21): `SubsanacionNoPermitidaError`, `PeticionNoEncontradaError`
 * y `ObservacionNoEncontradaError` se re-lanzan como `APIException` genérica
 * → **500**, no 400/404. Solo `ValidacionPDFError` da 400 y
 * `UsuarioNoAutorizadoError` da 403.
 */
export function subsanarChecklist(id: string, archivo: File): Promise<SubsanacionResponse> {
  const body = new FormData()
  body.append('archivo', archivo)
  return request<SubsanacionResponse>(`/api/v1/checklist/${id}/subsanar/`, {
    method: 'POST',
    body,
  })
}
