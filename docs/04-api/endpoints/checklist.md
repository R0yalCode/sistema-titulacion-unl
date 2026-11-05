---
title: "Endpoints: Checklist"
---

# Checklist

## PUT /api/v1/checklist/{id}/

Evalúa un requisito del checklist (T027): VERIFICADO u OBSERVADO, con bloqueo pesimista.

- **Parámetro de ruta**: `id` UUID de la verificación.
- **Cuerpo** (`ChecklistEvaluationRequest`):

| Campo | Tipo | Obligatorio | Validación |
|---|---|---|---|
| `estado_verificacion` | enum `VERIFICADO \| OBSERVADO` | Sí | Solo esos valores |
| `motivo_observacion` | string | Condicional | **Obligatorio si** `estado_verificacion = OBSERVADO` |

- **Roles**: SECRETARIO_ABOGADO (allow), ANALISTA_APOYO (solo borrador), ADMINISTRADOR.
- **Efectos**: verificación→nuevo estado; petición asociada→VERIFICADO/OBSERVADO; si OBSERVADO además expediente→OBSERVADA, observación accionable creada y notificación al estudiante.
- **Respuestas**:

| Código | Cuerpo (`ChecklistVerification`) |
|---|---|
| 200 | verificación actualizada con `evaluado_por`, `fecha_evaluacion` |
| 400 | `{ "code": "invalid_checklist_state" \| "expediente_not_in_verification" \| "verification_already_done" \| "observacion_required" }` |
| 404 | ajena; 401/403 |

## POST /api/v1/checklist/{id}/subsanar/

Subsana un requisito observado (T030): nueva versión del documento, cierra la observación y reanuda el plazo.

- **Cuerpo** (`SubsanacionRequest`, multipart): `archivo` (binary PDF ≤ 10 MB, obligatorio); `nombre_original` opcional.
- **Roles**: ESTUDIANTE dueño, SECRETARIA_CARRERA de la misma carrera, ADMINISTRADOR (DEC-02).
- **Precondiciones**: expediente OBSERVADA, verificación OBSERVADO, petición OBSERVADO con observación pendiente.
- **Efectos**: observación→resuelta; `DocumentoEntregado` vN+1; verificación→PENDIENTE; petición→CARGADO; expediente→EN_VERIFICACION con `fecha_limite_atencion` extendida; notificaciones.
- **Respuestas**:

| Código | Cuerpo (`SubsanacionResponse`) |
|---|---|
| 200 | resumen de la subsanación (documento nuevo + estados resultantes) |
| 400 | estado inválido / PDF inválido |
| 404 | ajena; 401/403 |
