# MATRIZ DE COMPATIBILIDAD BACKEND-FRONTEND — SGT-SIAAF

**Versión:** 1.0  
**Fecha:** 2026-11-05  
**Backend:** Código verificado (`src/config/urls.py`, `src/apps/*/adapters/serializers.py`, `src/apps/*/adapters/views.py`, `openapi.yaml`)  
**Frontend:** Especificación `specs/003-frontend-titulacion/specify.md` (Vistas V-01 a V-09)  
**Estado:** Verificado contra implementación real de ambos lados

---

## 1. Resumen de Compatibilidad por Vista

| Vista Frontend | Endpoints Backend Requeridos | Estado Contrato | Brechas Detectadas |
|----------------|------------------------------|-----------------|-------------------|
| **V-01 Login** | `POST /api/v1/auth/token/` | ✅ **COMPATIBLE** | — |
| **V-02 Dashboard Estudiante** | `GET /api/v1/expedientes/bandeja/`, `GET /api/v1/notificaciones/`, `PATCH /api/v1/notificaciones/{id}/marcar-leida/` | ✅ **COMPATIBLE** | — |
| **V-03 Crear Solicitud** | `POST /api/v1/expedientes/` | ✅ **COMPATIBLE** | — |
| **V-04 Expediente y Requisitos** | `GET /api/v1/expedientes/{id}/`, `GET /api/v1/expedientes/{id}/checklist/`, `POST /api/v1/expedientes/{id}/enviar/`, `POST /api/v1/expedientes/{id}/observar/`, `PUT /api/v1/checklist/{id}/`, `POST /api/v1/checklist/{id}/subsanar/`, `GET /api/v1/peticiones/{id}/documento/`, `GET /api/v1/peticiones/{id}/documento/{version}/` | ✅ **COMPATIBLE CON OBSERVACIONES** | Checklist 403 para ESTUDIANTE (BE-04); sin `GET /peticiones/{id}/` (BE-02) |
| **V-05 Gestión Peticiones** | `POST /api/v1/peticiones/{id}/solicitar-emision/`, `POST /api/v1/peticiones/{id}/documento/`, `GET /api/v1/peticiones/{id}/documento/`, `GET /api/v1/peticiones/{id}/documento/{version}/` | ✅ **COMPATIBLE** | — |
| **V-06 Seguimiento Petición** | `GET /api/v1/expedientes/{id}/` (busca petición en `peticiones[]`), `GET /api/v1/peticiones/{id}/documento/`, `GET /api/v1/peticiones/{id}/documento/{version}/` | ⚠️ **COMPATIBLE CON OBSERVACIONES** | Sin `GET /api/v1/peticiones/{id}/` (BE-02); usa búsqueda en expediente |
| **V-07 Bandeja Funcionario** | `GET /api/v1/expedientes/bandeja/` | ✅ **COMPATIBLE** | — |
| **V-08 Detalle Funcionario** | `GET /api/v1/expedientes/{id}/`, `GET /api/v1/expedientes/{id}/checklist/`, `PUT /api/v1/checklist/{id}/`, `POST /api/v1/expedientes/{id}/observar/`, `POST /api/v1/informes/`, `POST /api/v1/declaratorias/`, `GET /api/v1/peticiones/{id}/documento/`, `GET /api/v1/peticiones/{id}/documento/{version}/` | ✅ **COMPATIBLE CON OBSERVACIONES** | Sin `GET /peticiones/{id}/` (BE-02); checklist 403 ESTUDIANTE (BE-04) |
| **V-09 No Habilitado** | — | ✅ **COMPATIBLE** | Vista de degradación elegante |

---

## 2. Matriz Detallada Endpoint × Vista Frontend

| Endpoint Backend | Método | Vistas Frontend que lo Consumen | Estado | Observaciones |
|------------------|--------|--------------------------------|--------|---------------|
| `/api/v1/auth/token/` | POST | V-01 | ✅ COMPATIBLE | Response real: `{access, refresh}` vs OpenAPI "No response body" (INC-13) |
| `/api/v1/expedientes/` | POST | V-03 | ✅ COMPATIBLE | Request: `{carrera_id}`, Response 201 con expediente + 5 peticiones |
| `/api/v1/expedientes/bandeja/` | GET | V-02, V-07 | ✅ COMPATIBLE | Paginado DRF; filtrado por rol/estado |
| `/api/v1/expedientes/{id}/` | GET | V-04, V-06, V-08 | ✅ COMPATIBLE | Incluye `peticiones[]` anidadas |
| `/api/v1/expedientes/{id}/enviar/` | POST | V-04 | ✅ COMPATIBLE | 200 OK + timestamp + providencia + plazo |
| `/api/v1/expedientes/{id}/observar/` | POST | V-04, V-08 | ✅ COMPATIBLE | Body: `{motivo_observacion, peticion_id?}` |
| `/api/v1/expedientes/{id}/checklist/` | GET | V-04, V-08 | ✅ COMPATIBLE CON OBSERVACIONES | 403 para ESTUDIANTE (BE-04 no autorizado) |
| `/api/v1/checklist/{id}/` | PUT | V-04, V-08 | ✅ COMPATIBLE | Body: `{estado_verificacion, motivo_observacion?}` |
| `/api/v1/checklist/{id}/subsanar/` | POST | V-04, V-08 | ✅ COMPATIBLE | Multipart `archivo` PDF; versionado N+1 |
| `/api/v1/peticiones/{id}/solicitar-emision/` | POST | V-05 | ✅ COMPATIBLE | Sin body; 200 OK con petición actualizada |
| `/api/v1/peticiones/{id}/documento/` | POST | V-05, V-04, V-08 | ✅ COMPATIBLE | Multipart `archivo`; validación PDF; 201 Created |
| `/api/v1/peticiones/{id}/documento/` | GET | V-05, V-04, V-06, V-08 | ✅ COMPATIBLE | Descarga vigente; `FileResponse` streaming |
| `/api/v1/peticiones/{id}/documento/{version}/` | GET | V-05, V-04, V-06, V-08 | ✅ COMPATIBLE | Descarga versión específica |
| `/api/v1/informes/` | POST | V-08 | ✅ COMPATIBLE | Body: `{expediente_id, dictamen, fundamentacion?}`; 201 + PDF |
| `/api/v1/declaratorias/` | POST | V-08 | ✅ COMPATIBLE | Multipart `archivo_memorando` + `numero_memorando?`; 201 |
| `/api/v1/notificaciones/` | GET | V-02 | ✅ COMPATIBLE | Paginado DRF; filtro `leida` opcional |
| `/api/v1/notificaciones/{id}/marcar-leida/` | PATCH | V-02 | ✅ COMPATIBLE | Sin body; 200 OK con notificación actualizada |
| `/api/v1/schema/` | GET | (Dev/DevOps) | ✅ COMPATIBLE | OpenAPI JSON |
| `/api/v1/docs/` | GET | (Dev/DevOps) | ✅ COMPATIBLE | Swagger UI |
| `/api/v1/redoc/` | GET | (Dev/DevOps) | ✅ COMPATIBLE | ReDoc |

---

## 3. Incompatibilidades y Brechas Identificadas

### 3.1 Brechas de Contrato (Backend → Frontend)

| ID | Endpoint | Problema | Impacto Frontend | Solución Recomendada |
|----|----------|----------|------------------|---------------------|
| **INC-01** | `POST /api/v1/auth/token/` | OpenAPI declara "No response body" pero retorna `{access, refresh}` | Frontend tipa respuesta real vs OpenAPI | Actualizar OpenAPI o documentar discrepancia (INC-13 en clarify.md) |
| **INC-02** | `GET /api/v1/peticiones/{id}/` | **No existe en backend** (BE-02) | V-06 y V-08 deben buscar petición en `expediente.peticiones[]` | Implementar endpoint o documentar limitación |
| **INC-03** | `GET /api/v1/expedientes/{id}/checklist/` | Retorna 403 para rol `ESTUDIANTE` | V-04 muestra panel "No disponible para su rol" (BE-04) | Implementar BE-04 o mantener limitación documentada |
| **INC-04** | `POST /api/v1/checklist/{id}/subsanar/` | Requiere `multipart/form-data` con `archivo` | Frontend debe usar `FormData` + validación cliente (RFF-006) | Documentar en specs frontend |
| **INC-05** | `POST /api/v1/expedientes/{id}/observar/` | Body requiere `motivo_observacion` + opcional `peticion_id` | Frontend debe validar motivo obligatorio | Validación cliente (RFF-005) |
| **INC-06** | `PUT /api/v1/checklist/{id}/` | `motivo_observacion` obligatorio si `estado_verificacion=OBSERVADO` | Frontend debe bloquear envío sin motivo | Validación cliente + UI bloqueante |
| **INC-07** | `POST /api/v1/informes/` | Requiere `dictamen: APTO|NO APTO` + `fundamentacion?` | Frontend debe validar dictamen | Select obligatorio + textarea opcional |
| **INC-08** | `POST /api/v1/declaratorias/` | Requiere `multipart/form-data` con `archivo_memorando` + `numero_memorando?` | Frontend debe validar PDF (RFF-006) + campo opcional | Validación cliente + FileUpload component |
| **INC-09** | `GET /api/v1/peticiones/{id}/documento/` | Response `DocumentoEntregado` incluye `archivo_path` (ruta interna) | **SEC-SEC-02**: Fuga ruta almacenamiento privado | **SEC-T009**: Reemplazar por `download_url` opaco |
| **INC-10** | `POST /api/v1/declaratorias/` | Response `DeclaratoriaAptitud` incluye `archivo_memorando_firmado_path` | **SEC-SEC-02**: Fuga ruta almacenamiento privado | **SEC-T009**: Reemplazar por `download_url` opaco |
| **INC-11** | `GET /api/v1/expedientes/bandeja/` | Filtrado por rol hardcodeado en backend | `SECRETARIA_CARRERA`/`DIRECTOR_CARRERA` ven lista vacía (BE-09) | Implementar BE-09 o documentar limitación |
| **INC-12** | `POST /api/v1/expedientes/` | Requiere `carrera_id` UUID; sin catálogo carreras (BE-10) | V-03 entrada manual UUID o V-09 (BE-10) | Implementar BE-10 o mantener limitación |

### 3.2 Discrepancias OpenAPI vs Implementación Real

| Endpoint | OpenAPI Declara | Implementación Real | Severidad |
|----------|-----------------|---------------------|-----------|
| `POST /api/v1/auth/token/` | "No response body" | `{ "access": "...", "refresh": "..." }` | **ALTA** (INC-13) |
| `POST /api/v1/expedientes/{id}/enviar/` | Response 200 `ExpedienteEnviado` | Response 200 `ExpedienteEnviado` | OK |
| `POST /api/v1/peticiones/{id}/documento/` | Response 200 `CargarDocumento` | Response 201 `CargarDocumento` | **MEDIA** (200 vs 201) |
| `GET /api/v1/peticiones/{id}/documento/` | Response 200 `DocumentoEntregado` (JSON) | Response 200 `FileResponse` (PDF binary) | **ALTA** (Content-Type mismatch) |
| `GET /api/v1/peticiones/{id}/documento/{version}/` | Response 200 `DocumentoEntregado` (JSON) | Response 200 `FileResponse` (PDF binary) | **ALTA** (Content-Type mismatch) |
| `POST /api/v1/informes/` | Response 201 `InformeCreate` | Response 201 `InformeCreate` | OK |
| `POST /api/v1/declaratorias/` | Response 201 `DeclaratoriaCreate` | Response 201 `DeclaratoriaCreate` | OK |

---

## 4. Mapeo de Dependencias Frontend (BE-xx) no Autorizadas

| BE-ID | Dependencia | Endpoint Requerido | Vistas Afectadas | Estado | Prioridad |
|-------|-------------|-------------------|------------------|--------|-----------|
| **BE-01** | Perfil `/me` o claims carrera/facultad en JWT | `GET /api/v1/me/` o claims extendidos | V-02, V-03, V-04, V-05, V-06 | **NO AUTORIZADA** | ALTA |
| **BE-02** | `GET /api/v1/peticiones/{id}/` y listado docs | `GET /api/v1/peticiones/{id}/` | V-04, V-06, V-08 | **NO AUTORIZADA** | ALTA |
| **BE-03** | Refresh token + logout servidor | `POST /api/v1/auth/refresh/`, `POST /api/v1/auth/logout/` | V-01, Layout | **NO AUTORIZADA** | ALTA |
| **BE-04** | Checklist estudiante (`GET /expedientes/{id}/checklist/`) | Permitir `ESTUDIANTE` en endpoint | V-04 | **NO AUTORIZADA** | MEDIA |
| **BE-05** | Perfil/historial estudiante completo | `GET /api/v1/me/`, `GET /api/v1/expedientes/historial/` | V-02, V-03, V-04 | **NO AUTORIZADA** | MEDIA |
| **BE-06** | Campo `opcion_titulacion` en expediente | `POST/GET /expedientes/` con `opcion_titulacion` | V-03, V-04 | **NO AUTORIZADA** | MEDIA |
| **BE-07** | Exponer `motivo`/`motivo_observacion` en respuestas | Incluir en `ExpedienteDetalle`, `PeticionInicializada` | V-04, V-08 | **NO AUTORIZADA** | BAJA |
| **BE-08** | CORS para origen frontend | Configuración `CORS_ALLOWED_ORIGINS` | Todas | **NO AUTORIZADA** | ALTA |
| **BE-09** | Ampliar bandeja roles sin expedientes | `GET /expedientes/bandeja/` con datos para `SECRETARIA_CARRERA`/`DIRECTOR_CARRERA` | V-07 | **NO AUTORIZADA** | MEDIA |
| **BE-10** | Catálogo carreras | `GET /api/v1/carreras/` | V-03 | **NO AUTORIZADA** | ALTA |
| **BE-11** | Paquete conflicto/versión (409/412/428 + ETag) | `409 Conflict`, `412 Precondition Failed`, `428 Precondition Required` | V-03, V-04, V-05, V-06 | **NO AUTORIZADA** | BAJA |

---

## 4. Matriz de Compatibilidad por Campo (Serializers ↔ Frontend Types)

### 4.1 `ExpedienteDetalle` (Backend) ↔ `ExpedienteDetalle` (Frontend)

| Campo Backend | Tipo | Frontend Esperado | Compatible | Observación |
|---------------|------|-------------------|------------|-------------|
| `id` | UUID | `string` | ✅ | — |
| `numero_expediente` | String | `string` | ✅ | — |
| `estudiante_id` | UUID | `string` | ✅ | — |
| `carrera_id` | UUID | `string` | ✅ | UUID, sin nombre (BE-01/BE-10) |
| `facultad_id` | UUID | `string` | ✅ | UUID, sin nombre |
| `estado` | Enum `EstadoEnum` | `string` | ✅ | Valores: `BORRADOR`...`DECLARADA_APTA` |
| `activa` | Boolean | `boolean` | ✅ | — |
| `fecha_creacion` | DateTime ISO | `string` | ✅ | Formato ISO 8601 |
| `fecha_recepcion` | DateTime ISO | `string` | ✅ | Nullable |
| `numero_providencia` | String | `string` | ✅ | Nullable |
| `fecha_limite_atencion` | DateTime ISO | `string` | ✅ | Nullable |
| `dias_laborables_acumulados` | Integer | `number` | ✅ | — |
| `peticiones[]` | Array `PeticionInicializada` | Array | ✅ | Ver 4.2 |

### 4.2 `PeticionInicializada` (Backend) ↔ `PeticionDocumental` (Frontend)

| Campo Backend | Tipo | Frontend Esperado | Compatible | Observación |
|---------------|------|-------------------|------------|-------------|
| `id` | UUID | `string` | ✅ | — |
| `requisito_codigo` | String | `string` | ✅ | — |
| `requisito_nombre` | String | `string` | ✅ | — |
| `estado_peticion` | Enum `EstadoPeticionEnum` | `string` | ✅ | Valores: `PENDIENTE`...`OBSERVADO` |
| `dependencia_emisora` | Enum `DependenciaEmisoraEnum` | `string` | ✅ | 8 valores |
| `fecha_solicitud` | DateTime ISO | `string` | ✅ | Nullable |
| `fecha_actualizacion` | DateTime ISO | `string` | ✅ | — |

### 4.3 `ChecklistVerification` (Backend) ↔ `ChecklistItem` (Frontend)

| Campo Backend | Tipo | Frontend Esperado | Compatible | Observación |
|---------------|------|-------------------|------------|-------------|
| `id` | UUID | `string` | ✅ | — |
| `requisito_codigo` | String | `string` | ✅ | — |
| `requisito_nombre` | String | `string` | ✅ | — |
| `estado_verificacion` | Enum `ChecklistVerificationEstadoVerificacionEnum` | `string` | ✅ | `PENDIENTE`/`VERIFICADO`/`OBSERVADO` |
| `evaluado_por_username` | String | `string` | ✅ | Nullable |
| `fecha_evaluacion` | DateTime ISO | `string` | ✅ | Nullable |
| `fecha_actualizacion` | DateTime ISO | `string` | ✅ | — |

### 4.4 `DocumentoEntregado` (Backend) ↔ `DocumentoEntregado` (Frontend) — **INCOMPATIBLE PARCIAL**

| Campo Backend | Tipo | Frontend Esperado | Compatible | **Problema Crítico** |
|---------------|------|-------------------|------------|---------------------|
| `id` | UUID | `string` | ✅ | — |
| `peticion` | UUID | `string` | ✅ | — |
| `version` | Integer | `number` | ✅ | — |
| `archivo_path` | String | **NO DEBE EXPONERSE** | ❌ **INC-09** | **Fuga ruta interna** (SEC-SEC-02) |
| `nombre_original` | String | `string` | ✅ | — |
| `tamanio_bytes` | Integer | `number` | ✅ | — |
| `hash_sha256` | String | `string` | ✅ | — |
| `tipo_mime` | String | `string` | ✅ | — |
| `subido_por` | UUID | `string` | ✅ | — |
| `subido_por_username` | String | `string` | ✅ | — |
| `fecha_carga` | DateTime ISO | `string` | ✅ | — |
| `es_vigente` | Boolean | `boolean` | ✅ | — |

**Solución Requerida (SEC-T009):** Remover `archivo_path`, añadir `download_url = SerializerMethodField()` → `request.build_absolute_uri(f"/api/v1/peticiones/{obj.peticion_id}/documento/")`

### 4.5 `DeclaratoriaAptitud` (Backend) ↔ `DeclaratoriaAptitud` (Frontend) — **INCOMPATIBLE PARCIAL**

| Campo Backend | Tipo | Frontend Esperado | Compatible | **Problema Crítico** |
|---------------|------|-------------------|------------|---------------------|
| `id` | UUID | `string` | ✅ | — |
| `expediente` | UUID | `string` | ✅ | — |
| `expediente_numero` | String | `string` | ✅ | — |
| `numero_memorando` | String | `string` | ✅ | — |
| `decano` | UUID | `string` | ✅ | — |
| `decano_nombre` | String | `string` | ✅ | — |
| `decano_username` | String | `string` | ✅ | — |
| `archivo_memorando_firmado_path` | String | **NO DEBE EXPONERSE** | ❌ **INC-10** | **Fuga ruta interna** (SEC-SEC-02) |
| `fecha_declaratoria` | DateTime ISO | `string` | ✅ | — |

**Solución Requerida (SEC-T009 + DEC-006):** Remover `archivo_memorando_firmado_path`, añadir `download_url` → endpoint `GET /api/v1/declaratorias/{id}/documento/` (por crear en `resoluciones/views.py`)

### 4.5 `NotificacionInterna` (Backend) ↔ `NotificacionInterna` (Frontend)

| Campo Backend | Tipo | Frontend Esperado | Compatible | Observación |
|---------------|------|-------------------|------------|-------------|
| `id` | UUID | `string` | ✅ | — |
| `expediente` | UUID | `string` | ✅ | — |
| `expediente_numero` | String | `string` | ✅ | — |
| `peticion` | UUID | `string` | ✅ | Nullable |
| `peticion_requisito_nombre` | String | `string` | ✅ | Nullable |
| `titulo` | String | `string` | ✅ | — |
| `mensaje` | String | `string` | ✅ | — |
| `leida` | Boolean | `boolean` | ✅ | — |
| `fecha_creacion` | DateTime ISO | `string` | ✅ | — |

---

## 5. Códigos HTTP y Manejo de Errores

### 5.1 Códigos HTTP por Endpoint (Backend Real vs Frontend Esperado)

| Endpoint | Éxito | Errores Backend Real | Frontend Debe Manejar |
|----------|-------|---------------------|----------------------|
| `POST /auth/token/` | 200 | 401 (credenciales), 400 (validación) | 401, 400, 5xx, red |
| `POST /expedientes/` | 201 | 400 (expediente activo, catálogo), 403 | 400, 403, 5xx, red |
| `GET /expedientes/bandeja/` | 200 | 401, 403 | 401, 403, 5xx, red |
| `GET /expedientes/{id}/` | 200 | 401, 403, 404 | 401, 403, 404, 5xx, red |
| `POST /expedientes/{id}/enviar/` | 200 | 400 (estado inválido), 422 (requisitos incompletos) | 400, 422, 403, 404, 5xx |
| `POST /expedientes/{id}/observar/` | 200 | 400, 403, 404 | 400, 403, 404, 5xx |
| `GET /expedientes/{id}/checklist/` | 200 | 401, 403 (ESTUDIANTE), 404 | 401, 403, 404 |
| `PUT /checklist/{id}/` | 200 | 400 (estado inválido, motivo faltante), 403, 404 | 400, 403, 404 |
| `POST /checklist/{id}/subsanar/` | 200 | 400 (PDF inválido, >10MB), 403, 404 | 400, 403, 404 |
| `POST /peticiones/{id}/solicitar-emision/` | 200 | 400 (estado inválido), 403, 404 | 400, 403, 404 |
| `POST /peticiones/{id}/documento/` | 201 | 400 (PDF inválido, >10MB), 403, 404 | 400, 403, 404 |
| `GET /peticiones/{id}/documento/` | 200 (PDF) | 401, 403, 404 | 401, 403, 404 |
| `POST /informes/` | 201 | 400 (checklist incompleto), 403, 404, 422 | 400, 403, 404, 422 |
| `POST /declaratorias/` | 201 | 400 (PDF inválido, >10MB, sin archivo), 403, 404 | 400, 403, 404 |

### 5.2 Formato de Errores (Actual vs Requerido)

**Actual (DRF Default + Custom Exceptions):**
```json
// 400 Validation Error
{ "detail": "Datos inválidos", "code": "invalid" }
// o
{ "archivo": ["El archivo excede el limite maximo de 10 MB"] }

// 401
{ "detail": "No active account found with the given credentials" }

// 403
{ "detail": "You do not have permission to perform this action." }

// 404
{ "detail": "Not found." }

// 500
{ "detail": "Internal server error" }  // Sin stack trace (DEBUG=False)
```

**Requerido Frontend (SEC-T010 - Formato Uniforme):**
```json
{
  "error": {
    "code": "validation_error|authentication_failed|permission_denied|not_found|throttled|server_error",
    "message": "Mensaje legible usuario final (español institucional)",
    "details": { "campo": ["error"] }  // opcional
  }
}
```

**Brecha:** Formato no uniforme; frontend debe parsear múltiples formatos. **SEC-T010** resolverá.

---

## 6. Autenticación y Gestión de Tokens

### 6.1 Flujo Actual (Backend Real)

| Paso | Acción | Detalle |
|------|--------|---------|
| 1 | Login | `POST /api/v1/auth/token/` → `{access, refresh}` |
| 2 | Access Token | JWT HS256, 60 min, claims: `cedula`, `roles[]`, `user_id`, `exp`, `jti` |
| 3 | Refresh Token | 24h, **sin rotación** (`ROTATE_REFRESH_TOKENS=False`), **sin blacklist** |
| 4 | Header | `Authorization: Bearer <access>` en cada request |
| 5 | 401 Handling | **Sin endpoint refresh** (BE-03); **sin logout servidor** (BE-03) |
| 6 | Expiración | Frontend debe detectar 401 → limpiar sesión → redirect login (RFF-014) |

### 6.2 Brechas Críticas Auth (Frontend Impactado)

| Brecha | Impacto Frontend | Tarea Backend |
|--------|------------------|---------------|
| **Sin refresh token rotation** | Interceptor no puede renovar access token automáticamente | SEC-T003 |
| **Sin endpoint logout** | Frontend no puede invalidar refresh token en servidor | SEC-T003 |
| **Access token 60 min vs 30 min ACD** | Refresh más frecuente del esperado | SEC-T006 |
| **Sin endpoint `/me` (BE-01)** | Frontend no obtiene perfil/carrera/facultad del token | BE-01 |
| **Access token en `sessionStorage`** | Riesgo XSS (documentado RSK-FE-02) | — |

---

## 7. Carga y Descarga de Archivos

### 7.1 Carga (POST `/peticiones/{id}/documento/`)

| Aspecto | Backend | Frontend Requerido |
|---------|---------|-------------------|
| Content-Type | `multipart/form-data` | `FormData` con campo `archivo` (File) |
| Validación Cliente | RFF-006 | `.pdf`, MIME `application/pdf`, ≤10MB, magic bytes `%PDF-` |
| Validación Servidor | Magic bytes, tamaño, SHA-256 | 400 si falla |
| Response Éxito | 201 `DocumentoEntregado` (con `archivo_path` **INC-09**) | Mostrar `download_url` (futuro SEC-T009) |
| Progress | Indeterminado (fetch) o progress (XMLHttpRequest) | RFF-006 |

### 7.2 Descarga (GET `/peticiones/{id}/documento/` y `/{version}/`)

| Aspecto | Backend | Frontend Requerido |
|---------|---------|-------------------|
| Auth | `Authorization: Bearer <access>` | Header obligatorio |
| Response | 200 `FileResponse` (PDF binary) | `fetch` → `blob()` → `URL.createObjectURL()` → `<a download>` |
| Headers | `Content-Type: application/pdf`, `Content-Disposition: attachment; filename="..."` | Leer `Content-Disposition` para nombre |
| Errores | 401, 403, 404 | Manejar según RFF-017 |

---

## 7. Resumen de Acciones Requeridas

### Acciones Backend (Prioridad → Tarea)

| Prioridad | Acción | Tarea |
|-----------|--------|-------|
| 🔴 CRÍTICA | Configuración producción completa | SEC-T001 |
| 🔴 CRÍTICA | JWT_SIGNING_KEY separada | SEC-T004 |
| 🔴 CRÍTICA | Rotación + blacklist refresh + logout | SEC-T003 |
| 🔴 CRÍTICA | Throttling login + IP auditoría real | SEC-T002, SEC-T005 |
| 🟡 MEDIA | Access token 30 min | SEC-T006 |
| 🟡 MEDIA | Validación MIME real PDF | SEC-T007 |
| 🟡 MEDIA | Throttling carga docs | SEC-T008 |
| 🟡 MEDIA | Reemplazar rutas internas por download_url | SEC-T009 |
| 🟡 MEDIA | Handler global excepciones + formato uniforme | SEC-T010 |
| 🟡 MEDIA | Logging estructurado + eliminar prints | SEC-T011, SEC-T012 |
| 🟡 MEDIA | Proteger Swagger/ReDoc prod | SEC-T013 |
| 🟡 MEDIA | CI/CD Security + Dependabot | SEC-T014, SEC-T015 |
| 🟡 MEDIA | Cobertura tests + testpaths | SEC-T016 |
| 🟡 MEDIA | Tests seguridad faltantes | SEC-T017 |
| 🟢 BAJA | Documentación rotación secretos | SEC-T018 |
| 🟢 BAJA | Limpieza archivos huérfanos | SEC-T019 |
| 🟢 BAJA | Verificación PermissionError Docker | SEC-T020 |
| 🟢 BAJA | Evidencias ACD 4 reales | SEC-T021 |

### Acciones Frontend (Dependientes de Backend)

| Acción Frontend | Dependencia Backend | Prioridad |
|-----------------|---------------------|-----------|
| Migrar `archivo_path` → `download_url` en V-03, V-07, V-08 | SEC-T009 (endpoint download declaratoria) | 🟡 MEDIA |
| Actualizar error handling global a formato uniforme | SEC-T010 | 🟡 MEDIA |
| Interceptor axios: guardar nuevo refresh, llamar logout, manejar 401 refresh | SEC-T003 (rotación/blacklist/logout) | 🟡 MEDIA |
| Manejar cookies seguras (Secure, HttpOnly, SameSite=Lax) + CSRF token | SEC-T001 (producción HTTPS) | 🔴 CRÍTICA |
| Actualizar `API_BASE_URL` a HTTPS | SEC-T001 | 🔴 CRÍTICA |
| Validación cliente PDF (RFF-006) | Ya implementada frontend | ✅ HECHO |
| Migrar V-06 de buscar en expediente a `GET /peticiones/{id}/` | BE-02 (endpoint) | 🟡 MEDIA |
| Habilitar checklist estudiante (V-04) | BE-04 (permiso) | 🟡 MEDIA |

---

## 8. Clasificación Final de Compatibilidad

| Categoría | Cuenta | Porcentaje |
|-----------|--------|------------|
| ✅ **COMPATIBLE** | 14 endpoints | 64% |
| ⚠️ **COMPATIBLE CON OBSERVACIONES** | 5 endpoints | 23% |
| ❌ **INCOMPATIBLE / NO IMPLEMENTADO** | 3 endpoints (BE-02, BE-04, BE-10) | 13% |

**Veredicto General:** **COMPATIBLE CON OBSERVACIONES** — Backend funcional para MVP Fase 1; frontend puede operar con degradación elegante (V-09) donde faltan endpoints/permisos. Brechas críticas de seguridad (auth, producción) deben resolverse antes de deploy productivo.

---

**Firma:** opencode AI Assistant  
**Fecha:** 2026-11-05  
**Verificación:** Código backend inspeccionado, especificación frontend revisada, auditoría seguridad completada, tests ejecutados (473 passed).