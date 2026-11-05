---
title: "Endpoints: Expedientes"
---

# Expedientes

## POST /api/v1/expedientes/

Crea la solicitud en BORRADOR con sus 5 peticiones documentales del Art. 235 (HU-001). Atómico.

- **Cuerpo** (`CrearExpedienteRequest`): `{ "carrera_id": uuid (obligatorio) }` — validado contra el catálogo institucional; carrera inválida → 400.
- **Roles**: ESTUDIANTE, ADMINISTRADOR.
- **Respuestas**:

| Código | Cuerpo (`ExpedienteBorrador`) |
|---|---|
| 201 | expediente con `id`, `numero_expediente` (`EXP-AAAA-NNNN`), `estado="BORRADOR"`, `peticiones_inicializadas[]` (5 × `{id, requisito_codigo, requisito_nombre, estado_peticion, dependencia_emisora}`) |
| 400 | expediente activo existente / carrera inválida |
| 401 / 403 | sin token / rol sin permiso |

## GET /api/v1/expedientes/bandeja/

Bandeja operativa paginada, filtrada por los estados de intervención del rol (HU-005).

- **Parámetros de consulta**: `page` (entero, opcional), `page_size` (entero, opcional, máx 50; por defecto 10).
- **Roles**: según `MAPA_INTERVENCION_POR_ROL`; rol sin estados → lista vacía; SECRETARIA/DIRECTOR/RESPONSABLE → vacía por diseño.
- **200**: `PaginatedBandejaExpedienteList` `{count, next, previous, results: [BandejaExpediente]}` con `id, numero_expediente, numero_providencia, estado, fecha_creacion, fecha_recepcion, fecha_limite_atencion, dias_laborables_acumulados, estudiante_*`. Orden: `fecha_limite_atencion, fecha_creacion`.
- **401 / 403**.

## GET /api/v1/expedientes/{id}/

Detalle completo del expediente (aislamiento por ámbito).

- **Parámetro de ruta**: `id` (UUID, obligatorio).
- **200**: `ExpedienteDetalle` (datos del expediente + `facultad_id`).
- **404**: inexistente **o** fuera del ámbito del rol (anti-IDOR). **401/403**.

## POST /api/v1/expedientes/{id}/enviar/

Envío formal: BORRADOR→ENVIADA, genera providencia `PROV-AAAA-NNNN`, fija `fecha_recepcion` (UTC) y `fecha_limite_atencion` (+8 días hábiles).

- **Cuerpo**: vacío (`ExpedienteEnviadoRequest` sin campos). Sin parámetros de consulta.
- **Roles**: estudiante propietario (forzado server-side).
- **Respuestas**:

| Código | Cuerpo (`ExpedienteEnviado`) |
|---|---|
| 200 | expediente con `estado="ENVIADA"`, `numero_providencia`, `fecha_recepcion`, `fecha_limite_atencion` |
| 400 | estado inválido (p. ej. reenvío) |
| 422 | `{ "code": "requisitos_incompletos" }` — requisitos sin documento en firme |
| 404 | ajeno/inexistente; 401/403 |

## POST /api/v1/expedientes/{id}/observar/

Registra una observación accionable sobre una petición (T028): pausa el plazo, petición→OBSERVADO, expediente→OBSERVADA, notifica al estudiante.

- **Cuerpo** (`ObservacionRegistroRequest`): `{ "motivo_observacion": string (obligatorio) }` sobre la petición indicada en la ruta de la acción.
- **Roles**: SECRETARIO_ABOGADO.
- **200** con `ObservacionResponse`; **400** (estado inválido / sin motivo); **404** ajeno; 401/403.

## GET /api/v1/expedientes/{expediente_id}/checklist/

Listado del checklist del expediente.

- **Roles**: SECRETARIO_ABOGADO, ANALISTA_APOYO, ADMINISTRADOR.
- **200**: `[ChecklistVerification]` con `id, requisito_codigo, requisito_nombre, estado_verificacion, evaluado_por, evaluado_por_username, fecha_evaluacion`.
- **404** si el expediente es ajeno; 401/403.
