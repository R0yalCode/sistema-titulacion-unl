import type { Paginated } from '../types/api'
import { request } from '../client'

export type EstadoBandejaEstudiante = 'BORRADOR' | 'OBSERVADA'

export type BandejaExpediente = {
  id: string
  numero_expediente: string
  estudiante_id: string
  carrera_id: string | null
  facultad_id: string | null
  estado: EstadoBandejaEstudiante
  fecha_creacion: string
  fecha_recepcion: string | null
  numero_providencia: string | null
  fecha_limite_atencion: string | null
}

export type ListBandejaEstudianteParams = {
  page?: number
  pageSize?: number
}

export function listBandejaEstudiante(
  params: ListBandejaEstudianteParams = {},
): Promise<Paginated<BandejaExpediente>> {
  const query = new URLSearchParams()
  if (params.page) {
    query.set('page', String(params.page))
  }
  if (params.pageSize) {
    query.set('page_size', String(params.pageSize))
  }
  const suffix = query.toString()
  return request<Paginated<BandejaExpediente>>(
    `/api/v1/expedientes/bandeja/${suffix ? `?${suffix}` : ''}`,
  )
}

export type PeticionInicializada = {
  id: string
  requisito_codigo: string
  requisito_nombre: string
  estado_peticion: string
  dependencia_emisora: string
}

export type ExpedienteBorrador = {
  id: string
  numero_expediente: string
  estudiante_id: string
  carrera_id: string
  estado: 'BORRADOR'
  activa: boolean
  fecha_creacion: string
  peticiones: PeticionInicializada[]
}

export type CrearExpedienteRequest = {
  carrera_id: string
}

/**
 * `POST /api/v1/expedientes/` (verificado 2026-11-05 contra
 * `apps/expedientes/services/crear_expediente.py` y
 * `apps/expedientes/tests/test_crear_expediente.py`): 201 con el expediente
 * en `BORRADOR` y sus 5 peticiones base inicializadas; 400 (no 409/412/428,
 * BE-11 sigue sin autorizar esa suposición) cuando el estudiante ya tiene un
 * expediente activo (`{"detail": "..."}` con la palabra "activo", RN-001) o
 * cuando el catálogo base está incompleto (error de datos del backend, no
 * del estudiante).
 */
/**
 * Ítem de la bandeja operativa (V-07). Mismo contrato que
 * `BandejaExpedienteSerializer`, pero con cualquier estado que el rol pueda
 * atender. Solo identificadores: el backend no expone nombres de estudiante,
 * carrera ni facultad en la bandeja (BE-01/BE-05).
 */
export type BandejaOperativaItem = Omit<BandejaExpediente, 'estado'> & {
  estado: EstadoExpediente
}

/** Tamaño máximo de página que acepta `BandejaPagination` (`max_page_size = 50`). */
export const BANDEJA_MAX_PAGE_SIZE = 50

/**
 * `GET /api/v1/expedientes/bandeja/` para roles operativos (FE-T701;
 * verificado 2026-11-12 contra `BandejaExpedienteViewSet`): paginado
 * (`page`, `page_size` ≤ 50), filtrado en el servidor por ámbito y por los
 * estados de `MAPA_INTERVENCION_POR_ROL` (SECRETARIA_CARRERA y
 * DIRECTOR_CARRERA → lista vacía, BE-09) y ordenado por
 * `fecha_limite_atencion`, `fecha_creacion`. No admite filtros ni búsqueda.
 */
export function listBandejaOperativa(
  params: ListBandejaEstudianteParams = {},
): Promise<Paginated<BandejaOperativaItem>> {
  const query = new URLSearchParams()
  if (params.page) {
    query.set('page', String(params.page))
  }
  if (params.pageSize) {
    query.set('page_size', String(Math.min(params.pageSize, BANDEJA_MAX_PAGE_SIZE)))
  }
  const suffix = query.toString()
  return request<Paginated<BandejaOperativaItem>>(
    `/api/v1/expedientes/bandeja/${suffix ? `?${suffix}` : ''}`,
  )
}

export function crearExpediente(payload: CrearExpedienteRequest): Promise<ExpedienteBorrador> {
  return request<ExpedienteBorrador>('/api/v1/expedientes/', {
    method: 'POST',
    body: payload,
  })
}

export type EstadoExpediente =
  | 'BORRADOR'
  | 'ENVIADA'
  | 'EN_VERIFICACION'
  | 'OBSERVADA'
  | 'INFORME_EMITIDO'
  | 'DECLARADA_APTA'
  | 'CANCELADA'

/**
 * `GET /api/v1/expedientes/{id}/` (verificado 2026-11-05 contra
 * `ExpedienteViewSet.retrieve` + `ExpedienteDetalleSerializer`): no expone
 * el historial real de transiciones (`HistorialEstado` existe como modelo
 * pero no está serializado aquí) — por eso V-04 construye su timeline solo
 * con `fecha_creacion`/`fecha_recepcion`, sin inventar fechas intermedias.
 */
export type ExpedienteDetalle = {
  id: string
  numero_expediente: string
  estudiante_id: string
  carrera_id: string
  facultad_id: string
  estado: EstadoExpediente
  activa: boolean
  fecha_creacion: string
  fecha_recepcion: string | null
  numero_providencia: string | null
  fecha_limite_atencion: string | null
  dias_laborables_acumulados: number
  peticiones: PeticionInicializada[]
}

export function getExpedienteDetalle(id: string): Promise<ExpedienteDetalle> {
  return request<ExpedienteDetalle>(`/api/v1/expedientes/${id}/`)
}

export type ExpedienteEnviado = ExpedienteDetalle

/**
 * `POST /api/v1/expedientes/{id}/enviar/` (verificado contra
 * `ExpedienteViewSet.enviar` + `enviar_expediente.py`, confirmado también en
 * V-03): 200 real (no 201); 400 si el expediente no está en `BORRADOR`; 422
 * si hay peticiones sin documento en firme (`RequisitosIncompletosError`).
 */
export function enviarExpediente(id: string): Promise<ExpedienteEnviado> {
  return request<ExpedienteEnviado>(`/api/v1/expedientes/${id}/enviar/`, { method: 'POST' })
}

/**
 * `POST /api/v1/expedientes/{id}/iniciar-verificacion/` (E2-01, verificado
 * 2026-11-12): solo SECRETARIO_ABOGADO de la facultad (RBAC
 * `expedientes:iniciar_verificacion`); ENVIADA → EN_VERIFICACION y creación
 * atómica del checklist. 200 con `ExpedienteDetalleSerializer`. Errores:
 * 400 `transicion_invalida`, 403, 404 `expediente_no_encontrado`.
 */
export function iniciarVerificacion(id: string): Promise<ExpedienteDetalle> {
  return request<ExpedienteDetalle>(`/api/v1/expedientes/${id}/iniciar-verificacion/`, { method: 'POST' })
}

export type ObservarExpedienteRequest = {
  motivo_observacion: string
  peticion_id?: string
}

export type ObservacionAccionable = {
  id: string
  expediente: string
  peticion: string
  peticion_requisito_nombre: string
  registrada_por: string
  registrada_por_username: string
  motivo_observacion: string
  fecha_registro: string
  resuelta: boolean
  fecha_resolucion: string | null
  fecha_creacion: string
  fecha_actualizacion: string
}

/**
 * `POST /api/v1/expedientes/{id}/observar/` (verificado 2026-11-05 contra
 * `ExpedienteViewSet.observar` + `registrar_observacion.py`): 201 real (no
 * 200, a pesar de que `specify.md` ya documentaba 201 correctamente).
 * `peticion_id` se lee directo de `request.data` en el backend (no está
 * declarado en `ObservacionRegistroSerializer`), por eso aquí es opcional y
 * se envía solo si el usuario seleccionó una petición real del expediente.
 * **Discrepancia real documentada** (INC-21 en `clarify.md`): dos de las
 * cuatro excepciones de dominio (`ExpedienteNoEnVerificacionError`,
 * `PeticionNoEncontradaError`) se re-lanzan como `APIException` genérica sin
 * `status_code` propio, que en DRF responde **500**, no 400/404. Solo
 * `ObservacionYaExisteError` da 400 y `UsuarioNoAutorizadoError` da 403.
 */
export function observarExpediente(
  id: string,
  payload: ObservarExpedienteRequest,
): Promise<ObservacionAccionable> {
  return request<ObservacionAccionable>(`/api/v1/expedientes/${id}/observar/`, {
    method: 'POST',
    body: payload,
  })
}
