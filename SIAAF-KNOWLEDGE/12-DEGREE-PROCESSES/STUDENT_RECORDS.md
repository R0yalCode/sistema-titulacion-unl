---
system: SGT-SIAAF
type: process
area: expedientes
status: verified
source: verified-code
last_verified: 2026-11-11
---

# Expediente de titulación

**Código:** `backend/src/apps/expedientes/` · **Frontend:** V-02 (bandeja del estudiante), V-03 (crear), V-04 (detalle).

## Qué es

`ExpedienteTitulacion` es el **expediente global** del estudiante para la declaratoria de aptitud legal. Lleva el número de expediente (único), número de providencia, carrera y facultad (UUID sin catálogo), estado, fechas de recepción y límite, contador de días laborables y bandera `activa`. Cada cambio de estado queda en `HistorialEstado` y `EventoAuditoria`.

## Reglas verificadas

- Solo ESTUDIANTE (propio) o ADMINISTRADOR pueden crearlo; el frontend envía `carrera_id` como UUID manual (no hay catálogo, BE-10).
- **Un solo expediente activo** por estudiante: un segundo intento devuelve **400** (no 409), según `CLAUDE.md` (V-03).
- Al crearse genera 5 peticiones base ([[REQUESTS_AND_APPLICATIONS]]).
- Se envía solo con los 5 documentos vigentes; desde ese momento, plazo de 8 días laborables.
- Campos críticos inmutables (control listado en el commit ECLIPSE).
- Estados y transiciones: [[BACKEND_ARCHITECTURE#Máquina de estados]]; incluye GAP-STATE-01 y `CANCELADA` sin operación.

## Limitaciones conocidas

- BE-05: no hay historial completo del estudiante (la bandeja solo muestra BORRADOR/OBSERVADA para ESTUDIANTE).
- BE-06: no hay modalidad de titulación.
- BE-07: el motivo de observación no se expone en las respuestas del expediente.

## Relacionado

[[DEGREE_PROCESS_OVERVIEW]] · [[DATABASE]] · [[ROUTES]]
