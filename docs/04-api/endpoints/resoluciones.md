---
title: "Endpoints: Resoluciones"
---

# Resoluciones

## POST /api/v1/informes/

Emite el Informe de Aptitud Legal (Providencia N.º 590) con PDF generado por ReportLab (T034).

- **Cuerpo** (`InformeCreateRequest`, JSON):

| Campo | Tipo | Obligatorio | Validación |
|---|---|---|---|
| `expediente_id` | UUID | Sí | Debe existir y estar EN_VERIFICACION con checklist 100 % VERIFICADO |
| `dictamen` | enum `APTO \| NO APTO` | Sí | **NO APTO es rechazado** por regla de negocio |
| `fundamentacion` | string | No | Texto libre |

- **Roles**: SECRETARIO_ABOGADO (ámbito facultad).
- **Efectos**: numeración `PROV-590-AAAA-NNNN`; PDF persistido en almacenamiento privado; expediente→INFORME_EMITIDO; historial; notificación a Decanos de la facultad.
- **Respuestas**:

| Código | Cuerpo (`InformeAptitud`) |
|---|---|
| 201 | `{ id, expediente, expediente_numero, numero_providencia, dictamen, emisor, emisor_nombre, archivo_informe_path, fecha_emision }` |
| 400 | `{ "code": "informe_ya_emitido" \| "expediente_invalido_para_informe" }` |
| 404 | expediente ajeno; 401/403 |

## POST /api/v1/declaratorias/

Registra la Declaratoria de Aptitud (Memorando N.º 162) con el PDF firmado (T035). **Solo `multipart/form-data`.**

- **Cuerpo** (`DeclaratoriaCreateRequest`):

| Campo | Tipo | Obligatorio | Validación |
|---|---|---|---|
| `expediente_id` | UUID | Sí | Debe estar INFORME_EMITIDO con informe existente |
| `archivo_memorando` | binary PDF | Sí | Validación PDF (≤10 MB, magic bytes) |
| `numero_memorando` | string | No | Si falta, se autogenera `MEM-162-AAAA-NNNN` |

- **Roles**: DECANO (ámbito facultad).
- **Efectos**: persistencia del memorando firmado (con rollback si falla el disco); expediente→DECLARADA_APTA; historial; notificación al estudiante y copias a autoridades de la facultad (excluye al emisor).
- **Respuestas**:

| Código | Cuerpo (`DeclaratoriaAptitud`) |
|---|---|
| 201 | `{ id, expediente, expediente_numero, numero_memorando, decano, decano_nombre, archivo_memorando_firmado_path, fecha_declaratoria }` |
| 400 | `{ "code": "declaratoria_ya_emitida" \| "expediente_invalido_para_declaratoria" \| "pdf_invalido" }` |
| 404 | expediente ajeno; 401/403 |
