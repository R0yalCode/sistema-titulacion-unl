---
system: SGT-SIAAF
type: session-log
date: 2026-11-11
branch: security/inc-01-endurecimiento-backend
commits: ninguno (el usuario pidió no hacer commits)
---
# Sesión 2026-11-11 — Auditoría integral del backend + INC-01

## Investigado
- Los 12 documentos de [[90-ORIGINAL-SOURCES/DOCUMENTATION-PART-2/README|Documentacion-parte-2]] (lectura completa vía MCP).
- Código: `config/urls.py`, `authentication/adapters/permissions.py`, `core/adapters/scope_filter.py`, modelos de las 6 apps, vistas de expedientes/peticiones, servicios de estado, `core/ports` (SGA), settings.

## Modificado
- `backend/src/core/adapters/throttling.py` (nuevo), `openapi.py` (nuevo), `scope_filter.py`, `local_storage.py`
- Vistas: expedientes, verificacion, resoluciones, peticiones; `peticiones/services/cargar_documento.py`
- `config/settings/base.py`, `backend/.env.example`, `backend/openapi.yaml` (regenerado)
- Pruebas: `apps/peticiones/tests/test_inc01_seguridad.py` (13)
- Docs Quarto: `docs/planificacion-backend/*` (5 documentos), `docs/04-api/convenciones.md`, `04-api/endpoints/{peticiones,auth}.md`, `06-seguridad/{consideraciones-seguridad,autenticacion}.md`, `_quarto.yml`

## Pruebas (venv temporal con requirements del proyecto, SQLite en memoria)
- Línea base: `pytest` → 484 aprobadas, 13 fallidas (`pypdf` ausente).
- Final: `pytest` → **497 aprobadas, 13 fallidas** (mismas, `test_pdf_generator.py`); `pytest src/core` 76/76; `pytest tests` 4/4.
- `manage.py spectacular --validate` → 0 errores (2 warnings preexistentes).
- flake8 limpio en los archivos nuevos.

## Hallazgos clave
- GAP-STATE-01 confirmado (H-01, P0): sin `ENVIADA→EN_VERIFICACION`; decisión DP-01.
- 18 contradicciones documentales (C-01…C-18), incl. C-11: KPI-SEC-04 usa una FK checklist→petición inexistente.
- gh-pages: `.github/workflows/publish-quarto.yml` está **sin versionar** y publica solo en push a `main`.

## Pendientes
Ver `docs/planificacion-backend/REGISTRO_DECISIONES_TECNICAS.md` §3 y [[BLOCKED_TASKS]].


## Revisión de DP-01, DP-04 y DP-05 (sin cambios de código)

- Insumo: conclusiones del responsable obtenidas en NotebookLM (**fuente secundaria**; no normativa según [[INSTITUTIONAL_FRAMEWORK]]).
- Revisado: `enviar_expediente`, `evaluar_checklist`, `registrar_observacion`, `subsanar_requisito`, `cargar_documento`, `emitir_informe`, `plazo_calculator`, RBAC, `tests/e2e/test_full_workflow.py`.
- Nuevos hallazgos H-17…H-23 (destaca H-17: nadie crea las filas del checklist; H-19: la subsanación parcial bloquea el resto de observaciones).
- Decisiones nuevas: DP-01b, DP-05b, DP-18, DP-19, DP-20. Contradicciones N-01…N-07.
- Actualizados: `docs/planificacion-backend/{REGISTRO_DECISIONES_TECNICAS §4, PLAN_MAESTRO E2, MATRIZ_REQUERIMIENTOS, PLAN_APIS, AUDITORIA §6}`.
- Definidas para implementar (pendientes de autorización): E2-01 (solo SECRETARIO_ABOGADO), E2-02a, E2-02b (salvo DP-20), E2-03, E2-06. Bloqueadas: E2-02c (DP-19), E2-04, E2-05.


## Corrección documental de E2 (autorizada; sin código)

- Plan maestro: E2 completa por tarea; E2-02b dividida en b1 (H-21), b2 (H-18 notificación), b3.1 (sin resolución automática) y b3.2 (H-19, bloqueada por DP-20); E2-06 bloqueada por DP-22 (H-24); ruta crítica actualizada.
- Registro: estados de aprobación ("definida" ≠ "autorizada"), DP-21 (N-07), DP-22 (H-24), AUT-01 (celda de la matriz 6.2), nota sobre el Art. 235, §4.4 decisión→tareas.
- Matriz: RQ-FL-21 (H-17), RQ-FL-22…24; vínculos H-xx en las filas E2. Auditoría: H-24, §6.1 trazabilidad H-17…H-24, R-07, R-08.
- Verificado: `permissions.py` sin cambios; diff del backend idéntico al de INC-01; nada en el área de preparación de git.


## H-24 verificado y DP-22 resuelta técnicamente (sin código)

- e2e instrumentada desde el scratchpad: 8 `ESTADO_CAMBIADO` para 6 transiciones; la señal del expediente atribuye todo al estudiante; H-25: el historial del informe registra `INFORME_EMITIDO→INFORME_EMITIDO`.
- DP-22 → DT-12 `registrar_transicion()` (decisión técnica del responsable; **implementación no autorizada**). E2-06 definida y requisito previo de E2-01.
- AUT-01 redefinida: la celda GET de descarga es una derivación de implementación (la especificación 6.2 solo define el POST). AUT-02/AUT-03 para las celdas nuevas de E2-01/E2-02a. Las tres, pendientes.
- H-22 reforzado: contradice la especificación aprobada §6.2 (analista = "Borrador"). DP-20 sin preferencia ni redacción ambigua.


## Fase 1 — PLB-E2-06 implementada (autorizada; sin commit)

- Nuevo `expedientes/services/transiciones.py` (`registrar_transicion()`); 6 servicios migrados; señales sin auditoría de transiciones (se conserva `EXPEDIENTE_CREADO`); H-24 y H-25 (= AUD-P2-01) corregidos. Hallazgo nuevo H-26 (`declarar_aptitud` admite al analista en el servicio).
- Pruebas: `src/apps` 509 aprobadas / 13 fallidas (`pypdf`, previas); `src/core` 76/76; e2e 4/4; INC-01 + E2-06 23/23; OpenAPI sin cambios. e2e instrumentada: 1 `ESTADO_CAMBIADO` por transición, con el actor real.
- AUT-02 concedida por el responsable para la Fase 2 (E2-01), aún no aplicada. `permissions.py` intacto.
