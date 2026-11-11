---
system: SGT-SIAAF
type: session-log
date: 2026-11-11
agent: claude-code
branch: security/inc-01-endurecimiento-backend
commits: []
---

# Sesión 2026-11-11 — E2-01: iniciar verificación (AUT-02)

## Objetivo

Implementar PLB-E2-01, autorizada expresamente por el responsable con AUT-02: `POST /api/v1/expedientes/{id}/iniciar-verificacion/`, exclusivo del SECRETARIO_ABOGADO de la facultad, transición `ENVIADA → EN_VERIFICACION` con `registrar_transicion()` y generación atómica e idempotente de los cinco ítems del checklist. Revisar O-1/O-2/O-3 de E2-06 sin salir del alcance.

## Investigado (archivos y secciones)

- `docs/planificacion-backend/PLAN_MAESTRO_IMPLEMENTACION_BACKEND.md` § PLB-E2-01; `REGISTRO_DECISIONES_TECNICAS.md` (AUT-02, DP-01).
- `expedientes/services/transiciones.py`, `enviar_expediente.py`, `crear_expediente.py`; `verificacion/services/evaluar_checklist.py`; `expedientes/adapters/views.py`; `config/urls.py`; `authentication/adapters/permissions.py`; `core/adapters/scope_filter.py`, `throttling.py`, `openapi.py`; `tests/e2e/test_full_workflow.py`.

## Cambios (rutas)

- `backend/src/apps/expedientes/services/iniciar_verificacion.py` (nuevo): una transacción con `select_for_update()`; revalida rol y facultad; exige ENVIADA; crea las 5 filas PENDIENTE con `_get_or_create_checklist_verification`; `registrar_transicion(..., origen="iniciar_verificacion")`; notificación informativa al estudiante. Plazo sin cambios.
- `expedientes/services/transiciones.py`: `(ENVIADA, EN_VERIFICACION): ("SECRETARIO_ABOGADO",)`.
- `authentication/adapters/permissions.py`: **única** celda nueva `expedientes:iniciar_verificacion` POST `{SECRETARIO_ABOGADO: SCOPE_FACULTAD}` (AUT-02).
- `expedientes/adapters/views.py`: acción `iniciar_verificacion` (queryset por ámbito → 404; `TransicionInvalidaAPI` 400 `transicion_invalida` con cuerpo `{"detail"}`; 403; 429 heredado), `extend_schema(request=None)` y respuestas extra del contrato.
- `config/urls.py`: ruta `expedientes-iniciar-verificacion`. `backend/openapi.yaml` regenerado.
- Pruebas: `expedientes/tests/test_iniciar_verificacion.py` (34); `test_transiciones.py` (O-3, +11); e2e sin estado forzado ni checklist creado a mano.

## Pruebas ejecutadas (comando → resultado real)

- `pytest` (backend) → **554 aprobadas, 13 fallidas** (solo `test_pdf_generator.py`, `pypdf` ausente: deuda previa). Línea base: 509/13.
- `pytest src/core` → 76/76 · `pytest tests` (e2e) → 4/4.
- `manage.py spectacular --validate` → 0 errores (2 warnings preexistentes).
- `flake8` / `black --check` sobre los archivos nuevos y las líneas añadidas → limpios (los avisos restantes de `views.py`/`urls.py` son preexistentes).

## Decisiones (→ DECISIONS_LOG / ADR)

- AUT-02 aplicada tal cual fue concedida (sin ANALISTA_APOYO ni ADMINISTRADOR; DP-01b pendiente).
- El conjunto de filas se toma del catálogo base vigente (FASE_1, obligatorio, activo) y exige exactamente 5; si no, error sin efectos.
- O-2 tratada **solo en este endpoint** (errores de estado/transición → 400). El mapeo global en los demás endpoints queda pendiente.
- O-3 tratada: la prueba de arquitectura detecta también `.update(estado=…)` y `.bulk_update(…, ["estado"…])`.
- O-1 **no** tratada: requiere decisión funcional sobre `OBSERVADA → INFORME_EMITIDO`.

## Notas de la bóveda actualizadas

[[CURRENT_STATE]] · [[API_CONTRACTS]] · [[PERMISSIONS_ROLES]] · [[BLOCKED_TASKS]] (GAP-STATE-01 resuelta).

## Pendientes y bloqueos

- O-1; O-2 en los demás endpoints; H-26 / DP-05b; DP-01b; DP-18 sin cambios.
- Concurrencia real no probada (SQLite en pruebas): cubierta por `select_for_update` y la prueba secuencial de segunda llamada.
- Frontend: acción "Iniciar verificación" en V-08 (sin autorizar).

## Fuentes originales relacionadas

`docs/planificacion-backend/` (PLB-E2-01, AUT-02, DP-01).
