---
title: "Endpoints: Peticiones y documentos"
---

# Peticiones y documentos

## POST /api/v1/peticiones/{id}/solicitar-emision/

Solicita a la dependencia emisora la emisión del documento (T021): PENDIENTE→SOLICITADO + notificación.

- **Parámetro de ruta**: `id` UUID de la petición.
- **Cuerpo**: vacío (`SolicitarEmisionRequest` sin campos).
- **Roles**: estudiante dueño, SECRETARIA_CARRERA (su carrera), ADMINISTRADOR.
- **Respuestas**:

| Código | Cuerpo (`SolicitarEmisionResponse`) |
|---|---|
| 200 | petición con `estado_peticion="SOLICITADO"`, `fecha_solicitud`, datos del requisito y de la dependencia |
| 400 | expediente en estado inválido / petición no PENDIENTE |
| 403 | usuario sin rol de emisión válido |
| 404 | ajena/inexistente |

## POST /api/v1/peticiones/{id}/documento/

Carga un PDF para la petición (T023). **Solo `multipart/form-data`** (JSON no admitido en esta acción).

- **Cuerpo** (`CargarDocumentoRequest`): `archivo` (binary, obligatorio, PDF ≤ 10 MB). Sin otros campos.
- **Roles**: estudiante dueño, SECRETARIA_CARRERA de la misma carrera **solo en peticiones con `dependencia_emisora = SECRETARIA_CARRERA`** (SCOPE_ASIGNADO, VULN-002, desde 2026-11-11; antes podía cargar en cualquier petición de su carrera), ADMINISTRADOR. Estados de petición admitidos: PENDIENTE, SOLICITADO, OBSERVADO, CARGADO.
- **Efectos**: validación (tamaño + magic bytes + hash SHA-256), guardado en almacenamiento privado, versionado N+1 (anterior `es_vigente=False`), petición→CARGADO.
- **Respuestas**:

| Código | Cuerpo (`CargarDocumentoResponse`) |
|---|---|
| 200 | `{ documento: { id, version, nombre_original, tamanio_bytes, hash_sha256, fecha_carga }, peticion: { … } }` |
| 400 | `{ "code": "pdf_validation_error" \| "file_too_large" }` o estado inválido |
| 404 | ajena; 401/403 |

## GET /api/v1/peticiones/{id}/documento/

Descarga el documento **vigente** (T024).

- **Roles** (matriz RBAC `peticiones:documento` GET): estudiante dueño (`SCOPE_OWN`); SECRETARIA_CARRERA, SECRETARIO_ABOGADO, ANALISTA_APOYO y DIRECTOR_CARRERA con `SCOPE_ASIGNADO`; ADMINISTRADOR. DECANO no tiene celda (403).
- **SCOPE_ASIGNADO** (VULN-002, `ScopeFilterMixin`, 2026-11-11): la petición es visible si `dependencia_emisora` es uno de los roles del usuario **y** el expediente pertenece a su carrera (o, si el usuario no tiene carrera, a su facultad). Un jurista solo descarga documentos asignados a su rol; no descarga los emitidos por otras dependencias (hallazgo H-07, pendiente de decisión).
- **Integridad** (VULN-003): antes de servir el archivo se recalcula su SHA-256 por bloques y se compara con el registrado en la carga. Si no coincide: **500** `documento_integridad_comprometida`, el archivo no se entrega y se registra un `logger.error`.
- **200**: binario PDF (`Content-Disposition: attachment; filename=…`, `Content-Length`). **404** si no hay documento vigente o el objeto es ajeno. 401/403.

## GET /api/v1/peticiones/{id}/documento/{version}/

Descarga una versión específica del documento.

- **Parámetros de ruta**: `id` UUID, `version` entero ≥ 1.
- **200/404** con la misma semántica que la descarga vigente; la versión inexistente devuelve 404.
