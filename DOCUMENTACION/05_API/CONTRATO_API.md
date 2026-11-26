---
title: "Contrato de respuestas"
---

# Contrato de respuestas de la API — SGT-SIAAF

## 1. Verificación del "contrato universal" {success, message, data, errors, meta}

El encargo de esta auditoría pide verificar el uso de un contrato universal de respuesta con la forma:

```json
{ "success": true, "message": "Operación realizada correctamente.", "data": {}, "errors": null, "meta": {} }
```

**Resultado de la verificación (búsqueda directa en el código y en el contrato OpenAPI):** este envelope **no existe en ningún lugar del backend SGT-SIAAF**. Se buscó literalmente `"success"`, `'data'`/`"data"` como clave de nivel superior, `errors:` y `meta:` en `backend/openapi.yaml` (1224 líneas) y en los adaptadores (`views.py`) de las 6 apps — sin resultados. Tampoco se declara un `EXCEPTION_HANDLER` personalizado en `backend/src/config/settings/base.py` que pudiera estar envolviendo las respuestas de error en ese formato.

**Conclusión:** SGT-SIAAF **no implementa** el contrato `{success, message, data, errors, meta}`. Esto se declara explícitamente como **NO APLICA**, no como una brecha a corregir: ese envelope nunca fue un requisito de este proyecto (no aparece en `specify.md`, `plan.md` ni `clarify.md` del backend) — es una convención genérica de otros proyectos que no corresponde imponer aquí sin autorización, y que de hecho el equipo del backend documentó explícitamente de otra forma (ver §2).

## 2. Contrato real implementado (verificado, documentado previamente en `docs/04-api/convenciones.md` y confirmado contra `openapi.yaml`)

### Respuestas exitosas

El cuerpo de la respuesta **es el recurso serializado directamente** (sin envoltorio), siguiendo la convención estándar de Django REST Framework. Ejemplo (`POST /api/v1/expedientes/`, 201): el cuerpo es el objeto `ExpedienteTitulacion` serializado, no `{"data": {...}}`.

### Respuestas de error

Cuerpo DRF estándar, de dos formas posibles:

```json
{ "detail": "Mensaje", "code": "requisitos_incompletos" }
```

```json
{ "fieldErrors": { "carrera_id": ["Invalid value."] } }
```

### Códigos semánticos de error observados (`docs/04-api/convenciones.md`, consistentes con las excepciones de dominio documentadas en `COMPONENTES_NEGOCIO.md`)

| Código | HTTP | Origen (excepción de dominio) |
|---|---|---|
| `requisitos_incompletos` | 422 | `RequisitosIncompletosError` (enviar_expediente) |
| `pdf_validation_error` | 400 | Validación de magic bytes |
| `file_too_large` | 400 | Límite de 10 MB |
| `invalid_checklist_state` | 400 | `InvalidVerificationStateError` |
| `expediente_not_in_verification` | 400 | `ExpedienteNoEnVerificacionError` |
| `informe_ya_emitido` / `declaratoria_ya_emitida` | 400 | `InformeYaExisteError` / `DeclaratoriaYaExisteError` |
| `expediente_invalido_para_informe` | 400 | `ExpedienteNoValidoParaInformeError` |

### Códigos HTTP en uso

`200, 201, 400, 401, 403, 404, 422`. **No se declaran** `409`, `412`, `428` ni `429`: los tres primeros corresponden a la dependencia bloqueada BE-11 (ETag/If-Match, concurrencia optimista — ver `AGENTS.md` §3.6 y `CLAUDE.md`, FE-T1213 Bloqueada); `429` (rate limiting) no está implementado, lo cual es coherente con el hallazgo P0 de `docs/RESUMEN_EJECUTIVO.md` ("sin throttling/rate limiting").

## 3. Inconsistencia detectada y ya documentada por el propio equipo: excepciones de dominio que responden 500

Ya registrado en `DOCUMENTACION/01_ESPECIFICACION/HISTORIAS_Y_CASOS_DE_USO.md` §4 (hallazgo heredado de **INC-21**, `specs/003-frontend-titulacion/clarify.md`): varias excepciones de dominio reales en observar/evaluar/subsanar responden **HTTP 500** en vez de 400/404, aunque describen reglas de negocio conocidas (no errores de programación). Esto significa que el contrato de errores documentado en §2 de esta página **no se cumple de forma completa**: existen casos donde una regla de negocio esperada produce un error genérico no mapeado, en vez de un `code` semántico. Se reafirma aquí el mismo hallazgo (no se investiga más a fondo en esta fase; corresponde a Fase 6/7 confirmar el listado exacto de endpoints afectados).

## 4. Paginación y filtros (verificado en `docs/04-api/convenciones.md`, consistente con el inventario de endpoints)

- Solo `GET /expedientes/bandeja/` pagina (`?page`, `?page_size`, respuesta `{count, next, previous, results}`).
- `GET /notificaciones/` **no pagina**, devuelve `{"results": [...]}` — discrepancia ya señalada en `CLAUDE.md` (V-02 cerrada): "`GET /notificaciones/` no está paginado en el backend real, a diferencia de lo que indican `specify.md` y `openapi.yaml`". Esta auditoría no reverificó si `openapi.yaml` sigue declarando paginación para ese endpoint (pendiente, no crítico para el alcance de esta fase).
