---
title: "API — Convenciones"
---

# Convenciones de la API

## Formato de datos

- `application/json; charset=utf-8` en todas las operaciones, excepto:
  - Carga de documentos: `multipart/form-data` (campo `archivo`).
  - Descarga de documentos: `application/pdf` (streaming, `Content-Disposition: attachment`).
- Fechas: ISO 8601 UTC (`2026-11-05T14:30:00Z`).
- Identificadores: UUID v4.

## Errores

Cuerpo DRF estándar:

```json
{ "detail": "Mensaje", "code": "requisitos_incompletos" }
```

```json
{ "fieldErrors": { "carrera_id": ["Invalid value."] } }
```

| code semántico | HTTP | Significado |
|---|---|---|
| `requisitos_incompletos` | 422 | Envío con requisitos sin documento en firme |
| `pdf_validation_error` | 400 | PDF inválido (magic bytes) |
| `file_too_large` | 400 | Archivo > 10 MB |
| `invalid_checklist_state` | 400 | Evaluación con estado previo no válido |
| `expediente_not_in_verification` | 400 | Operación requiere expediente EN_VERIFICACION |
| `informe_ya_emitido` / `declaratoria_ya_emitida` | 400 | Resolución duplicada |
| `expediente_invalido_para_informe` | 400 | Estado del expediente no permite el informe |

Códigos HTTP usados: 200, 201, 400, 401, 403, 404, 422. **No se declaran** 409/412/428/429 porque no están implementados (los 409/412/428 son dependencia BE-11, bloqueada).

## Aislamiento por rol (importante)

Los detalles de objeto devuelven **404** (no 403) cuando el objeto existe pero está fuera del ámbito del rol — semántica anti-IDOR deliberada y probada.

## Paginación

Solo la bandeja pagina: `?page` (por defecto 1), `?page_size` (10 por defecto, máx 50). Respuesta DRF estándar `{count, next, previous, results}`. El listado de notificaciones **no pagina** y devuelve `{"results": [...]}`.

## Filtros

| Endpoint | Filtro |
|---|---|
| `GET /notificaciones/` | `?leida=true|false` |
| `GET /expedientes/bandeja/` | Sin parámetros; el filtro es por rol (estados de intervención) |

No hay búsqueda textual ni ordenamiento por parámetros (orden fijo de la bandeja: `fecha_limite_atencion, fecha_creacion`).

## Idempotencia y concurrencia

- Operaciones de escritura con bloqueo pesimista (`select_for_update`): dos evaluaciones concurrentes del mismo checklist no pueden ambas prosperar.
- Sin cabeceras ETag/If-Match (optimistic locking pendiente, BE-11).
