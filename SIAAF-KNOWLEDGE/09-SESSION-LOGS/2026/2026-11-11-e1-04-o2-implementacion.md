---
system: SGT-SIAAF
type: session-log
date: 2026-11-11
agent: claude-code
branch: fix/e1-04-errores-dominio
commits: [2623685, daa8b41, 4d02baf, 3cdb47d]
---

# Sesión 2026-11-11 — PLB-E1-04 + O-2: errores de dominio, bloqueo uniforme y concurrencia real

## Modalidad de ejecución (DK-010, enmienda 2026-11-11)

- **Implementación centralizada:** los cinco bloques los ejecutó materialmente **Claude Code**, en una sola sesión, por autorización expresa del responsable del proyecto (R0yalCode, 2026-11-11).
- **Atribución:** cada commit lleva como autor Git (`--author`) al **integrante responsable de la tarea** según el reparto aprobado (contribución delegada). El autor Git **no** indica que el integrante escribiera personalmente el código. Committer de todos: R0yalCode (identidad configurada en el equipo que ejecutó).
- **Rama:** `fix/e1-04-errores-dominio`, creada desde `develop` (`d1fa86e`) en un `git worktree` separado, para no tocar los cambios locales ni la rama documental `docs/politica-autoria-equipo`. Sin push ni merge.

| Orden | Tarea | Responsable (autor Git) | Commit |
|---|---|---|---|
| 1 | T1 (T1a + T1b) | Dan1el17 `<steeven.pardo@unl.edu.ec>` | `2623685` |
| 2 | T3 | 7777-C `<markgonzalez20062@gmail.com>` | `daa8b41` |
| 3 | T2 | JJOC3S `<jimmy.ontaneda@unl.edu.ec>` | `4d02baf` |
| 4 | T4 | R0yalCode `<royel.jima@unl.edu.ec>` | `3cdb47d` |
| 5 | T5 | JuanCalopinoo `<Juan.calopino@unl.edu.ec>` | el commit que incorpora esta bitácora |

## Objetivo

Que ninguna regla de negocio, recurso inexistente o transición inválida responda HTTP 500 genérico; código de error visible en JSON y en OpenAPI; orden de bloqueo uniforme (expediente → petición → checklist) sin interbloqueos; limpieza segura de archivos; evidencia de concurrencia con PostgreSQL real.

## Cambios por bloque

- **T1:** `core/adapters/api_errors.py` (respuesta común `{"detail","code"}`; 400/404/409/422 y 500 explícitos con registro técnico); `TransicionNoPermitidaError` con `estado_anterior`/`estado_nuevo` y `transicion_permitida()` (solo lectura de la tabla); mapeos de crear, enviar, iniciar-verificacion y observar; excepciones específicas en `registrar_observacion`.
- **T3:** 404/500 explícito (`emisor_no_configurado`, D-4) en peticiones; bloqueo expediente → petición en `cargar_documento` y `solicitar_emision`; `config/settings/test_postgres.py`, marcador `postgres`, `conftest.py` (MEDIA_ROOT temporal; la suite ya no escribe en `src/media`), `tests/integration/README.md`.
- **T2:** bloqueo canónico y validación sobre la fila bloqueada en `evaluar_checklist` y `subsanar_requisito`; 404/400/500 explícito (`inconsistencia_observacion`, D-3).
- **T4:** O-1 → **409 `regla_pendiente_o1`** con prevalidación antes del PDF (D-1; regla no decidida, tabla intacta); reserva exclusiva del archivo (H-28); limpieza solo del archivo propio (D-6) en informe y declaratoria.
- **T5:** escenarios C1–C8 en PostgreSQL; componentes OpenAPI `ErrorDominio`, `ErrorSimple`, `ErrorValidacion` (`anyOf` por código); `openapi_respuestas_extra` de las operaciones afectadas; `backend/openapi.yaml` regenerado; prueba de contrato con validación `jsonschema` de respuestas reales.

## Pruebas ejecutadas (resultados reales)

| Ámbito | Comando | Resultado |
|---|---|---|
| Suite backend (SQLite) | `pytest` | **606 aprobadas, 13 fallidas** (solo `test_pdf_generator.py`: texto extraído vacío por `pypdf` ausente; deuda previa, causa verificada sin cambios). Línea base: 554/13 |
| Core | `pytest src/core` | 88/88 (76 + 12 nuevas) |
| e2e + contrato + integración (SQLite) | `pytest tests` | 24 aprobadas, 10 omitidas (marcador `postgres`) |
| PostgreSQL real | `DJANGO_SETTINGS_MODULE=config.settings.test_postgres pytest -m postgres tests/integration` | **10/10**, tres ejecuciones consecutivas, sin errores en el log del servidor |
| OpenAPI | `manage.py spectacular --validate` | 0 errores (2 advertencias preexistentes) |

PostgreSQL usado: `PostgreSQL 16.15 (Debian 16.15-1.pgdg13+2)`, contenedor desechable `postgres:16` sin volumen (no se tocó el volumen de desarrollo).

## Evidencia H-29 (interbloqueo)

C1 ejecutado **antes de T2** (código en `daa8b41`): el servidor registró

```
ERROR:  deadlock detected
DETAIL:  Process 104 waits for ShareLock on transaction 947; blocked by process 103.
         Process 103 waits for ShareLock on transaction 948; blocked by process 104.
         Process 104: SELECT ... FROM "peticiones_peticiondocumental" ... FOR UPDATE   (observar)
         Process 103: SELECT "estado" FROM "expedientes_expedientetitulacion" ... FOR UPDATE   (evaluar -> registrar_transicion)
```

y una de las dos peticiones respondió HTTP 500. Con T2, C1 pasa: evaluar 200, observar 400 `expediente_no_en_verificacion`, una transición, un evento y una observación.

## Escenarios C1–C8 (PostgreSQL, conexiones independientes)

Cada escenario retiene al hilo A con sus bloqueos y **verifica en `pg_stat_activity`** que B espera un bloqueo antes de liberar A; comprueba códigos HTTP y `code`, estado, historial, auditoría, checklist, observaciones, documentos y archivos, y que no haya 500 (40P01/55P03).

| Escenario | Resultado |
|---|---|
| C1 observar vs evaluar OBSERVADO (mismo ítem) | 200 + 400; sin interbloqueo |
| C2 dos evaluaciones OBSERVADO (ítems distintos) | 200 + 400; 1 transición, 1 observación |
| C3 subsanar vs evaluar | 201 + 200 sobre el estado ya confirmado |
| C4 doble iniciar-verificacion | 200 + 400; 5 filas; 1 transición; 1 notificación |
| C5 doble POST /informes | 201 + 400; 1 informe; 1 PDF íntegro; centinelas intactos (SHA-256) |
| C6 carga vs observar (misma petición) | 201 + 201; versiones coherentes (aceptar la carga sobre OBSERVADO es H-21, pendiente) |
| C7 doble declaratoria | 201 + 400; 1 memorando; ningún archivo del perdedor |
| C8 solicitar-emisión vs carga | 200 + 201; sin actualización perdida |

## Decisiones aplicadas

D-1 (409 `regla_pendiente_o1`, aprobado), D-2…D-7 según el plan; `permissions.py`, `TRANSICIONES_PERMITIDAS`, DP-18 y la política SHA-256 sin cambios; H-27 fuera de alcance.

## Pendientes y limitaciones

- **O-1** sigue pendiente de decisión funcional (hoy 409).
- Solo C1 se ejecutó contra el código anterior a la corrección; C2–C8 se ejecutaron contra el código final.
- `subsanar_requisito` y `cargar_documento` guardan el PDF antes de terminar la transacción: si fallan después, el archivo queda huérfano (fuera de D-6, que cubre informe y declaratoria).
- `backend/contracts/openapi.yaml` **ya no es idéntico** a `backend/openapi.yaml` desde `0a24109` (INC-01); no se modificó (fuera de alcance). Contradicción a registrar en la trazabilidad documental.
- Integración documental pendiente: la enmienda de DK-010 y el plan `PLAN_E1-04_O-2.md` están en la rama documental (`c53671e` + cambios sin commitear), no en esta rama; su integración requiere autorización.
- `jsonschema` se usa en la prueba de contrato como dependencia transitiva de `drf-spectacular` (no se declaró ninguna dependencia nueva).
- 13 fallos de `test_pdf_generator.py` (PLB-E0-01, `pypdf`).
