---
system: SGT-SIAAF
type: architecture
area: api
status: verified
source: verified-code
last_verified: 2026-11-11
---

# Contratos API (verificados contra código)

**Fuentes de verdad:** `backend/src/config/urls.py` (rutas reales) y `backend/openapi.yaml` (contrato). `backend/contracts/openapi.yaml` era idéntico a `backend/openapi.yaml` hasta `467ec3b`; **desde `0a24109` (INC-01) difieren** (verificado 2026-11-11; pendiente decidir si se sincroniza).
Rutas y métodos coinciden entre `urls.py` y OpenAPI: **16 rutas, 17 operaciones** bajo `/api/v1/`.

## 1. Endpoints existentes

| # | Método | Ruta | Vista (`urls.py`) | Recurso RBAC | Roles con acceso real (ver [[PERMISSIONS_ROLES]]) |
|---|---|---|---|---|---|
| 1 | POST | `/api/v1/auth/token/` | `TokenPairView` (throttle `auth`, 5/min por IP) | — (anónimo) | Todos |
| 2 | POST | `/api/v1/expedientes/` | `ExpedienteViewSet.create` | `expedientes` POST | ESTUDIANTE, ADMINISTRADOR |
| 3 | GET | `/api/v1/expedientes/bandeja/` | `BandejaExpedienteViewSet.list` | `expedientes` GET + `MAPA_INTERVENCION_POR_ROL` | Según rol y estado |
| 4 | GET | `/api/v1/expedientes/{id}/` | `ExpedienteViewSet.retrieve` | `expedientes` GET | Todos menos RESPONSABLE_DEPENDENCIA |
| 5 | POST | `/api/v1/expedientes/{id}/enviar/` | `ExpedienteViewSet.enviar` | `expedientes:enviar` | ESTUDIANTE (own) |
| 5a | POST | `/api/v1/expedientes/{id}/iniciar-verificacion/` (sin cuerpo; 200 `ExpedienteDetalle`, 400 `transicion_invalida`, 403, 404, 429) | `ExpedienteViewSet.iniciar_verificacion` (E2-01, 2026-11-11) | `expedientes:iniciar_verificacion` | SECRETARIO_ABOGADO (facultad; AUT-02) |
| 6 | GET | `/api/v1/expedientes/{expediente_id}/checklist/` | `ChecklistListViewSet.list` | `checklist` GET | SECRETARIO_ABOGADO, ANALISTA_APOYO, ADMINISTRADOR |
| 7 | PUT | `/api/v1/checklist/{id}/` | `ChecklistViewSet.update` | `checklist` PUT | SECRETARIO_ABOGADO, ANALISTA_APOYO (borrador), ADMINISTRADOR |
| 8 | POST | `/api/v1/checklist/{id}/subsanar/` | `ChecklistViewSet.subsanar` | `checklist` POST | ESTUDIANTE (own), SECRETARIA_CARRERA (carrera), ADMINISTRADOR |
| 9 | POST | `/api/v1/expedientes/{id}/observar/` | `ExpedienteViewSet.observar` | `expedientes:observar` | SECRETARIO_ABOGADO |
| 10 | POST | `/api/v1/informes/` | `InformeViewSet.create` | `informes` POST | SECRETARIO_ABOGADO, ANALISTA_APOYO (borrador) |
| 11 | POST | `/api/v1/declaratorias/` | `DeclaratoriaViewSet.create` | `declaratorias` POST | DECANO |
| 12 | GET | `/api/v1/notificaciones/` | `NotificacionViewSet.list` | `notificaciones` GET | Todos menos RESPONSABLE_DEPENDENCIA |
| 13 | PATCH | `/api/v1/notificaciones/{id}/marcar-leida/` | `NotificacionViewSet.marcar_leida` | `notificaciones` PATCH | Todos menos RESPONSABLE_DEPENDENCIA |
| 14 | POST | `/api/v1/peticiones/{id}/solicitar-emision/` | `PeticionViewSet.solicitar_emision` | `peticiones` POST | ESTUDIANTE (own), ADMINISTRADOR |
| 15 | POST | `/api/v1/peticiones/{id}/documento/` | `PeticionViewSet.cargar_documento` (throttle `document_upload`, 10/h) | `peticiones:documento` POST | ESTUDIANTE (own), SECRETARIA_CARRERA/SECRETARIO_ABOGADO/ANALISTA_APOYO/DIRECTOR_CARRERA (asignado), ADMINISTRADOR |
| 16 | GET | `/api/v1/peticiones/{id}/documento/` | `PeticionViewSet.descargar_documento` (vigente) | `peticiones:documento` GET | Igual que 15 |
| 17 | GET | `/api/v1/peticiones/{id}/documento/{version}/` | `PeticionViewSet.descargar_documento` (versión) | `peticiones:documento` GET | Igual que 15 |

No pertenecen a la API de negocio: `GET /health/` (sin autenticación, SEC-T001), `/admin/` (consola Django, ADR-0009), `/api/v1/schema/`, `/api/v1/docs/`, `/api/v1/redoc/` (drf-spectacular; protegidos, ver `test_swagger_protection.py`).

## 2. Discrepancias contrato ↔ comportamiento real

Registradas en `sgt-siaaf/specs/003-frontend-titulacion/clarify.md`; el frontend se adapta al comportamiento real y **no** se corrige el backend.

| ID | Discrepancia | Tratamiento |
|---|---|---|
| INC-13 | `POST /auth/token/` devuelve `{access, refresh}`; OpenAPI dice "No response body" | Tipar `TokenPair` |
| INC-19 | `GET /notificaciones/` devuelve `{results: [...]}` **sin paginación**; OpenAPI/`specify.md` indican otra forma | Implementar contra código real |
| INC-21 | `POST /expedientes/{id}/observar/` responde 201 (no 200); excepciones de dominio en observar/evaluar/subsanar respondían **HTTP 500** con mensaje de regla de negocio. **Corregido 2026-11-11 (PLB-E1-04, rama `fix/e1-04-errores-dominio`, sin integrar):** 4xx con `{detail, code}`; ver § Errores de dominio | Mostrar siempre `detail` real |
| FE-T407 | Subsanar requiere `checklist_verification_id`, pero ESTUDIANTE y SECRETARIA_CARRERA reciben 403 en `GET .../checklist/` → no pueden descubrir el ID | Limitación documentada; no se inventa flujo |
| GAP-STATE-01 | **No existe operación API que lleve un expediente de `ENVIADA` a `EN_VERIFICACION`**; evaluar checklist y observar exigen `EN_VERIFICACION` | Ver [[BACKEND_ARCHITECTURE#Máquina de estados]] |

## 2.1 Errores de dominio (PLB-E1-04 + O-2, 2026-11-11)

- Cuerpo común `{"detail": "...", "code": "..."}` (componente OpenAPI `ErrorDominio`); `code` es estable.
- 400 regla/estado o cambio concurrente; 404 recurso inexistente; **409 `regla_pendiente_o1`** en `POST /informes/` desde OBSERVADA (O-1 pendiente; **no es BE-11**: sin ETag/If-Match); 422 `requisitos_incompletos`; 500 **solo explícitos**: `configuracion_catalogo_incompleta`, `emisor_no_configurado`, `inconsistencia_observacion` y `documento_integridad_comprometida` (INC-01, sin cambios, `ErrorSimple`).
- 404 de `get_object_or_404` y 403 siguen como `{detail}` (`ErrorSimple`); errores de validación de campos como `ErrorValidacion`.
- Bitácora: [[2026-11-11-e1-04-o2-implementacion]].

## 3. Endpoints inexistentes citados en la documentación

Ninguno de estos existe en `urls.py` (verificado 2026-11-11). Son **propuestas** de [[DP2-PLAN_MAESTRO]] y documentos relacionados:

| Endpoint propuesto | Incremento | Nota |
|---|---|---|
| `POST /api/v1/auth/token/refresh/` | BE-03 / INC-02 | El plan maestro §8.1 lo llama "implícito": **falso**, no hay ruta |
| `POST /api/v1/auth/logout/` | BE-03 / INC-02 | — |
| `GET/DELETE /api/v1/sesiones/…` | INC-02 | [[DP2-PLAN_SESIONES]] |
| `GET /api/v1/expedientes/{id}/modalidad/`, `…/elegibilidad/`, `POST …/cambiar/`, `GET /api/v1/modalidades/` | BE-06 / INC-03 | [[DP2-ESPECIFICACION_API_MODALIDADES]] |
| `GET /api/v1/dashboard/me/`, `GET /api/v1/indicadores/{modalidades,culminacion,evolucion,elegibilidad-ec,cambios-modalidad}/` | INC-04 | [[DP2-ESPECIFICACION_SERVICIOS_DASHBOARD]] |
| `GET /api/v1/buscar/`, `GET /api/v1/exportar/` | INC-05 | — |
| `POST /api/v1/csp-report/` | INC-05 (VULN-004) | — |
| `GET /api/v1/auditoria/` | — | Citado en [[DP2-MATRIZ_ACCIONES_RAPIDAS]]; sin incremento asignado |
| `GET /api/v1/peticiones/{id}/` | BE-02 | — |
| `GET /api/v1/carreras/` | BE-10 | — |
| `/me` (perfil) | BE-01 / BE-05 | — |

## Relacionado

- [[BACKEND_ARCHITECTURE]] · [[02-BACKEND/MODULES|Módulos backend]] · [[PERMISSIONS_ROLES]] · [[BLOCKED_TASKS]]
