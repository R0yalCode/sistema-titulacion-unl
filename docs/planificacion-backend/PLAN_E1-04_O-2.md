---
title: "Plan técnico PLB-E1-04 + O-2"
subtitle: "Errores de dominio sin HTTP 500 genéricos, bloqueo uniforme y concurrencia real (2026-11-11)"
date: 2026-11-11
---

# Plan técnico PLB-E1-04 + O-2

> **Estado: IMPLEMENTADO (2026-11-11)** en la rama `fix/e1-04-errores-dominio` (cinco commits, §10), con ejecución autorizada expresamente por el responsable el 2026-11-11 e integración local en `develop` autorizada (sin publicar). Anexo de [PLB-E1-04](PLAN_MAESTRO_IMPLEMENTACION_BACKEND.md). Origen: auditoría de E2-01 (2026-11-11), observaciones O-1/O-2/O-3 de E2-06 y hallazgos H-27…H-29 ([auditoría](AUDITORIA_INTEGRAL_BACKEND.md)). Reparto T1–T5 aprobado por el responsable (2026-11-11); **modalidad de implementación centralizada** (DK-010, enmienda 2026-11-11): ver §6.1 y §7.

**Invariantes que el plan no toca:** `authentication/adapters/permissions.py` (RBAC), `TRANSICIONES_PERMITIDAS`, la decisión funcional de O-1, DP-18 (envío), la política SHA-256 de INC-01 (`documento_integridad_comprometida`, 500), y la regla de no reescribir historial.

## 1. Decisiones D-1…D-7 (instrucción del responsable, 2026-11-11)

| ID | Decisión | Consecuencia técnica |
|---|---|---|
| **D-1** | O-1 sigue **pendiente de decisión funcional**. **Aprobado por el responsable (2026-11-11): 409 Conflict `regla_pendiente_o1`** para la emisión del informe desde OBSERVADA, sin relación con BE-11 y sin ETag/If-Match | Prevalidación de la transición **antes** de cualquier efecto (PDF incluido); si aun así falla tras crear el PDF: rollback y borrado **solo** del PDF creado por esa operación. Ver §2.1 (riesgo con BE-11) |
| **D-2** | `CatalogoIncompletoError` (crear expediente e iniciar verificación) → **500 explícito**, `code` visible, log técnico y OpenAPI | Corrige el 400 actual de `POST /expedientes/` que oculta un fallo de configuración |
| **D-3** | Inconsistencia de observación (`ObservacionNoEncontradaError` con ítem y petición OBSERVADO) → **500 explícito**, `code`, log | No se maquilla como 400 |
| **D-4** | `UsuarioEmisorNoEncontradoError` → **500 explícito**, `code`, log | Hoy es una excepción sin capturar |
| **D-5** | **Sin manejador global**. Respuesta estructurada común `{"detail","code"}` solo para los errores nuevos/modificados | Las pruebas comprueban el JSON externo (`response.json()`), no `ErrorDetail.code` |
| **D-6** | Limpieza de archivos **solo** de los creados por la operación que falla | Pruebas con archivos preexistentes y ajenos (hash antes/después) |
| **D-7** | El emisor de otra facultad (`solicitar_emision.py:111-114`) queda **fuera de E1-04** | Registrado como **H-27** |

### 2.1 Estudio del 409 para O-1

- **A favor:** la petición es válida, pero el recurso está en un estado sobre el que la regla aún no está definida: es un conflicto con el estado actual, no un error del cliente (400) ni del servidor (500).
- **Riesgo:** en el frontend los códigos 409/412/428 están asociados a **BE-11** (FE-T1213 **Bloqueada**, `CLAUDE.md` máxima 5). Este 409 **no** es BE-11 (no hay ETag/If-Match ni concurrencia optimista) y el frontend actual lo mostraría con el tratamiento genérico de error (`detail`). Debe documentarse así en OpenAPI y en la bóveda para que nadie lo tome como desbloqueo de FE-T1213.
- **Decisión (2026-11-11):** el responsable aprueba el 409; la alternativa de 500 explícito queda descartada. No se usará 400.
- **Condición de salida:** cuando se decida O-1, el 409 desaparece (se añade la transición o se retira OBSERVADA de `validar_checklist_completo`).

## 2. Inventario de excepciones y respuestas HTTP

Leyenda: **SVC** = el servicio cambia (excepción específica o bloqueo); "Hoy" medido por inspección de código y, donde se indica, por ejecución (auditoría E2-01).

| Endpoint | Excepción | Hoy | Objetivo (`code`) | SVC | Tarea |
|---|---|---|---|---|---|
| `POST /expedientes/` | `ExpedienteActivoExistenteError` | 400 (lista) | 400 `expediente_activo_existente` | — | T1 |
| ″ | `CatalogoIncompletoError` | **400** | **500** `configuracion_catalogo_incompleta` (D-2) | — | T1 |
| `POST /expedientes/{id}/enviar/` | `EstadoInvalidoError` | 400 (lista) | 400 `estado_invalido` | — | T1 |
| ″ | `RequisitosIncompletosError` | 422 | 422 `requisitos_incompletos` (sin cambio de regla, DP-18) | — | T1 |
| ″ | `TransicionNoPermitidaError` | 500 | 400 `transicion_invalida` (defensa; inalcanzable con §4) | — | T1 |
| `POST /expedientes/{id}/iniciar-verificacion/` | `EstadoInvalidoError` / `TransicionNoPermitidaError` | 400 `{"detail"}` | 400 `transicion_invalida` **con `code` en JSON** | — | T1 |
| ″ | `CatalogoIncompletoError` | 500 genérico | **500** `configuracion_catalogo_incompleta` (D-2) | — | T1 |
| `POST /expedientes/{id}/observar/` | `ExpedienteNoEnVerificacionError` | **500** | 400 `expediente_no_en_verificacion` | — | T1 |
| ″ | `PeticionNoEncontradaError` | **500** | 404 `peticion_no_encontrada` | — | T1 |
| ″ | `ValueError("ya está en OBSERVADO")` | **500 sin capturar** | 400 `peticion_ya_observada` | SVC | T1 |
| ″ | `ObservacionYaExisteError` | 400 (lista) | 400 `observacion_ya_existe` | — | T1 |
| ″ | `TransicionNoPermitidaError` | 500 | 400 `transicion_invalida` | — | T1 |
| `PUT /checklist/{id}/` | `ChecklistVerificationNotFoundError` | **500** | 404 `checklist_no_encontrado` | — | T2 |
| ″ | `ExpedienteNotInVerificationError` / `VerificationAlreadyCompletedError` / `InvalidVerificationStateError` | 400 | mismo status, `code` en JSON | — | T2 |
| ″ | `TransicionNoPermitidaError` | **500 (reproducido)** | 400 `transicion_invalida`; inalcanzable con §4 | SVC (bloqueo) | T2 |
| `POST /checklist/{id}/subsanar/` | `SubsanacionNoPermitidaError("no existe")` | **500** | 404 `checklist_no_encontrado` | SVC | T2 |
| ″ | `SubsanacionNoPermitidaError` (3 estados) | **500** | 400 `subsanacion_no_permitida` | — | T2 |
| ″ | `PeticionNoEncontradaError` | **500** | 404 `peticion_no_encontrada` | — | T2 |
| ″ | `ObservacionNoEncontradaError` | **500** | **500** `inconsistencia_observacion` + log (D-3) | — | T2 |
| ″ | `TransicionNoPermitidaError` | 500 | 400 `transicion_invalida` | SVC (bloqueo) | T2 |
| `POST /peticiones/{id}/solicitar-emision/` | `PeticionNoEncontradaError` | **500** | 404 `peticion_no_encontrada` | SVC (bloqueo) | T3 |
| ″ | `UsuarioEmisorNoEncontradoError` | **500 sin capturar** | **500** `emisor_no_configurado` + log (D-4) | — | T3 |
| `POST /peticiones/{id}/documento/` | `PeticionNoEncontradaError` | **500** | 404 `peticion_no_encontrada` | SVC (bloqueo) | T3 |
| `GET /peticiones/{id}/documento/…` | integridad SHA-256 | 500 `documento_integridad_comprometida` | **sin cambios** (INC-01) | — | — |
| `POST /informes/` | `ValueError("expediente no existe")` | 400 | 404 `expediente_no_encontrado` | SVC | T4 |
| ″ | Emisión desde OBSERVADA (O-1) | **500 + PDF huérfano (reproducido)** | **409** `regla_pendiente_o1` antes del PDF (D-1) | SVC | T4 |
| ″ | `TransicionNoPermitidaError` (otra causa) | 500 | 400 `transicion_invalida` + borrado del PDF propio | SVC | T4 |
| `POST /declaratorias/` | `ValueError("expediente no existe")` | 400 | 404 `expediente_no_encontrado` | SVC | T4 |
| ″ | `TransicionNoPermitidaError` | 500 | 400 `transicion_invalida` + borrado del memorando propio | SVC | T4 |

`ActorRequeridoError` sigue siendo 500: indica un error de programación (vista sin autenticación), no una regla de negocio. Los 403 (RBAC/ámbito) no cambian.

## 3. Diseño de errores JSON y contrato OpenAPI (D-5)

**Respuesta externa común** (verificado en el entorno de pruebas: `APIException` con `detail` dict se renderiza tal cual, sin manejador global):

```json
{"detail": "Mensaje legible en español.", "code": "transicion_invalida"}
```

- `core/adapters/api_errors.py` (nuevo, sin importar `apps`): clase base `ErrorDominioAPI(APIException)` que construye `{"detail", "code"}`; subclases `TransicionInvalidaAPI` (400), `RecursoNoEncontradoAPI` (404), `ReglaPendienteAPI` (409), `ConfiguracionInconsistenteAPI` e `InconsistenciaDatosAPI` (500 explícito: además registran `logger.error` con `code`, vista y `expediente_id`, **sin** datos personales).
- La `TransicionInvalidaAPI` de E2-01 se migra a la base común: el 400 de `iniciar-verificacion` **gana** el campo `code` (cambio aditivo).
- Las excepciones existentes que hoy devuelven `["…"]` (lista de `ValidationError`) **solo** se migran en los endpoints de §2; el resto del API no cambia (sin manejador global).
- **OpenAPI:** componente `ErrorDominio` (`detail`, `code` requeridos; `code` con `enum` por operación en la descripción) vía `openapi_respuestas_extra` de `SGTAutoSchema`; cada operación de §2 declara sus 400/404/409/500 con los `code` posibles. `openapi.yaml` solo lo regenera T5.
- **Pruebas:** `response.json() == {"detail": ANY, "code": "<code>"}` + status; prueba de contrato que recorre el esquema y exige que cada respuesta de error declarada referencie `ErrorDominio`.

## 4. Estrategia de bloqueos y concurrencia (O-2)

### 4.1 Diagnóstico (por inspección de código)

| Servicio | Orden actual de bloqueo | Problema |
|---|---|---|
| `registrar_observacion` | expediente → petición → checklist (UPDATE) | Correcto |
| `evaluar_checklist` | **checklist** → petición (UPDATE) → expediente (en `registrar_transicion`) | Orden inverso; valida el estado con `checklist.expediente` **sin bloquear** (lectura obsoleta → 500 reproducido) |
| `subsanar_requisito` | **checklist** → petición → expediente | Orden inverso; lectura obsoleta del expediente |
| `cargar_documento` | petición **+ expediente en una sola sentencia** (`select_related(...).select_for_update()` sin `of`) | En PostgreSQL bloquea ambas filas en un orden no controlado |
| `solicitar_emision` | **ninguno** (`get` sin bloqueo y `save`) | Actualización perdida posible frente a `cargar_documento` |
| `enviar_expediente`, `iniciar_verificacion`, `emitir_informe`, `declarar_aptitud` | expediente primero | Correcto |

**Hipótesis H-29 (pendiente de PostgreSQL real):** `observar` (exp→pet→chk) concurrente con `evaluar`/`subsanar` (chk→pet→exp) puede producir `deadlock_detected` (SQLSTATE 40P01), hoy un 500.

### 4.2 Diseño: el expediente como bloqueo del agregado

Toda operación que **modifique** el expediente o sus peticiones, checklist, observaciones o documentos:

1. Resuelve `expediente_id` sin bloquear (p. ej. `values_list` desde el checklist o la petición).
2. **Bloquea el expediente primero** (`select_for_update()` por `pk`) y valida su estado **sobre esa fila bloqueada**.
3. **Vuelve a consultar con bloqueo** las filas dependientes (no reutiliza instancias leídas antes del bloqueo): petición(es) con `select_for_update(of=("self",))` ordenadas por `pk`, después checklist con `select_for_update(of=("self",))` ordenado por `pk`; revalida sus estados.
4. Escribe observaciones/documentos y llama a `registrar_transicion()` (que vuelve a bloquear el expediente: no-op en la misma transacción) dentro de la **misma** `transaction.atomic()`.

**Por qué evita la carrera:** todas las mutaciones de un mismo expediente se serializan en el bloqueo de su fila; la segunda operación espera, relee el estado ya confirmado y lo rechaza con la regla de dominio correspondiente (400 específico), no con `TransicionNoPermitidaError`. Con un único orden global (expediente → petición → checklist) no puede formarse un ciclo de espera, así que no hay interbloqueo. `TransicionNoPermitidaError` queda como **defensa en profundidad** (400 `transicion_invalida`, con rollback completo por la transacción) y como señal de O-1 (409).

**Integridad:** cualquier excepción dentro del bloque revierte estado, historial, auditoría, checklist, observaciones y notificaciones; los archivos se tratan en §5. La restricción única `unique_verificacion_por_requisito` sigue protegiendo el checklist.

| Servicio | Cambio | Tarea |
|---|---|---|
| `evaluar_checklist` | Pasos 1–4; revalidar `estado_verificacion` tras el bloqueo | T2 |
| `subsanar_requisito` | Pasos 1–4 | T2 |
| `registrar_observacion` | Ya cumple; añadir `of=("self",)` y revalidación explícita | T1 |
| `cargar_documento` | Bloquear expediente primero; petición con `of=("self",)` | T3 |
| `solicitar_emision` | Añadir bloqueo expediente → petición | T3 |
| `enviar_expediente`, `iniciar_verificacion`, `emitir_informe`, `declarar_aptitud` | Ya cumplen; solo verificación por prueba | T5 |

### 4.3 Pruebas de concurrencia (solo PostgreSQL)

SQLite **no** sirve como evidencia de bloqueo (ignora `select_for_update` y serializa escrituras): ahí solo se admiten pruebas funcionales y simulaciones con monkeypatch, presentadas como tales.

- **Infraestructura (T3):** `config/settings/test_postgres.py` (hereda de `test.py`; motor PostgreSQL por variables de entorno; `OPTIONS: {"options": "-c lock_timeout=5000 -c deadlock_timeout=200"}`); servicio `db` de `docker-compose.yml` (PostgreSQL 16); marcador `postgres` que se omite si el motor no es PostgreSQL. `psycopg` ya está en `requirements.txt`: **sin dependencias nuevas**.
- **Técnica (T5):** `pytest.mark.django_db(transaction=True)`; dos hilos, cada uno con **su propia conexión** (Django abre una por hilo; `connection.close()` al terminar) y transacciones reales; `threading.Barrier` para arrancar a la vez y `threading.Event` inyectado tras adquirir el primer bloqueo para forzar el entrelazado **determinista** (A retiene el expediente mientras B intenta entrar); límite de espera por hilo para detectar bloqueos colgados.
- **Comprobaciones en cada escenario:** status HTTP y `code` de ambas respuestas; ninguna `OperationalError` con SQLSTATE 40P01 (interbloqueo) ni 55P03 (timeout de bloqueo); estado final del expediente; número exacto de `HistorialEstado` y de `EventoAuditoria ESTADO_CAMBIADO`; filas de checklist, observaciones, documentos y notificaciones; ausencia de efectos parciales del perdedor.

| Escenario | Resultado esperado |
|---|---|
| C1 `observar` vs `PUT /checklist` OBSERVADO (mismo expediente) | Sin interbloqueo; uno 2xx y otro 400 `expediente_no_en_verificacion`; 1 transición EN_VERIFICACION→OBSERVADA |
| C2 dos `PUT /checklist` OBSERVADO sobre ítems distintos | 200 + 400; 1 transición; 1 observación |
| C3 `PUT /checklist` vs `subsanar` | Sin interbloqueo; resultado coherente con el orden de llegada |
| C4 doble `iniciar-verificacion` | 200 + 400 `transicion_invalida`; exactamente 5 filas de checklist; 1 transición |
| C5 doble `POST /informes/` | 201 + 400 (`informe_ya_existe`); 1 `InformeAptitud`; 1 transición; **1 solo PDF** creado, válido (`%PDF`), cuyo nombre coincide con el registrado; ningún PDF del perdedor; archivo centinela preexistente intacto (SHA-256 igual) |
| C6 `cargar_documento` vs `observar` (misma petición) | Sin interbloqueo; versiones de documento coherentes |
| C7 doble `POST /declaratorias/` | 1 declaratoria; 1 memorando almacenado; ningún archivo del perdedor |
| C8 `solicitar_emision` vs `cargar_documento` | Sin actualización perdida del estado de la petición |

**Escribir C1 antes de T2** documenta la hipótesis H-29: si falla en PostgreSQL con 40P01, queda confirmada; si no, se registra como no reproducida.

## 5. Estrategia de rollback y archivos (D-6)

- **Invariante comprobada:** no hay `ATOMIC_REQUESTS` (`config/settings/base.py`): la `transaction.atomic()` de cada servicio es la más externa en el camino HTTP. T4 añade una prueba que lo fija (si alguien activa `ATOMIC_REQUESTS`, el diseño debe revisarse).
- **Providencia 590 (`emitir_informe`):** hoy el generador escribe con nombre fijo (`providencia_590_<número>.pdf`) y **sobrescribe** un archivo existente (**H-28**, observado en la auditoría). Cambio: crear el archivo con **creación exclusiva** (`open(..., "xb")`: falla si existe) y nombre único si hay colisión; el servicio guarda la ruta **creada por esta operación** y, si cualquier paso posterior falla, la borra en un `except` alrededor del bloque atómico y relanza. Además, la prevalidación de la transición (D-1) va **antes** de generar el PDF, de modo que O-1 no crea archivo alguno.
- **Memorando 162 (`declarar_aptitud`):** `storage.save()` ya devuelve un nombre disponible (no sobrescribe); si fallan `registrar_transicion` o las notificaciones, se borra **exactamente** esa ruta con `storage.delete()`.
- **Nunca** se borra por patrón, por directorio ni por nombre calculado: solo la ruta devuelta por la creación de esta operación.
- **Pruebas (SQLite, con `MEDIA_ROOT`/`PRIVATE_MEDIA_ROOT` en `tmp_path`):** fallo inyectado tras crear el archivo → archivo propio eliminado, BD intacta; archivo preexistente con el **mismo nombre base** → no se sobrescribe ni se borra (SHA-256 antes/después); archivos ajenos del directorio intactos; éxito → el archivo existe y coincide con la ruta registrada. Esto corrige también F-04 (pruebas escribiendo en el `media/` real) para las pruebas nuevas; T3 propone un `conftest` que lo aplique a toda la suite.

## 6. Tareas T1–T5 (reparto aprobado el 2026-11-11; ejecutadas, ver §10)

| ID | Contenido técnico | Archivos | Depende de | Pruebas | Commit previsto (uno por bloque, §6.1) |
|---|---|---|---|---|---|
| **T1a** Núcleo | Base `ErrorDominioAPI` y subclases; migrar `TransicionInvalidaAPI` de E2-01; atributos `estado_anterior`/`estado_nuevo` en `TransicionNoPermitidaError` y función de **prevalidación** `transicion_permitida(estado_actual, nuevo)` que **lee** `TRANSICIONES_PERMITIDAS` sin modificarla | `core/adapters/api_errors.py` (nuevo), `expedientes/services/transiciones.py`, `expedientes/adapters/views.py` | — | Renderizado JSON de cada clase; log de los 500 explícitos; E2-01 34/34 con `code` en JSON | Commit del bloque T1 (T1a + T1b), ver T1b |
| **T1b** Expedientes | Mapeos de §2 (`create`, `enviar`, `observar`, `iniciar-verificacion`); `registrar_observacion`: excepción propia para "ya OBSERVADO", `of=("self",)` y revalidación | `expedientes/adapters/views.py`, `verificacion/services/registrar_observacion.py`, `expedientes/tests/` | T1a | JSON + status por excepción; D-2 (500 explícito + log); rollback ante transición inválida simulada | `fix(expedientes): respuesta común de errores de dominio sin 500 genéricos (E1-04)` · `--author="Dan1el17 <steeven.pardo@unl.edu.ec>"` |
| **T2** Verificación | Mapeos de §2; separar "no existe"; D-3; **bloqueo del agregado** (§4.2) en `evaluar_checklist` y `subsanar_requisito` | `verificacion/adapters/views.py`, `verificacion/services/evaluar_checklist.py`, `verificacion/services/subsanar_requisito.py`, `verificacion/tests/` | T1a | JSON + status; carrera simulada (monkeypatch, SQLite) → 400 sin efectos; regresión `test_evaluar_checklist`/`test_subsanar_requisito`/e2e | `fix(verificacion): errores con code y bloqueo del expediente primero (E1-04, O-2)` · `--author="JJOC3S <jimmy.ontaneda@unl.edu.ec>"` |
| **T3** Peticiones + infraestructura | Mapeos y D-4; bloqueo expediente → petición en `cargar_documento` y `solicitar_emision`; `test_postgres.py`, marcador `postgres`, `conftest` con `MEDIA_ROOT` temporal, instrucciones de ejecución | `peticiones/adapters/views.py`, `peticiones/services/cargar_documento.py`, `peticiones/services/solicitar_emision.py`, `peticiones/tests/`, `config/settings/test_postgres.py` (nuevo), `pyproject.toml` (marcador), `conftest.py` | — (los mapeos, T1a) | JSON + status; `test_inc01_seguridad` 13/13 (SHA-256 intacto); prueba de humo `postgres` | `fix(peticiones): errores con code, bloqueo uniforme e infraestructura PostgreSQL (E1-04)` · `--author="7777-C <markgonzalez20062@gmail.com>"` |
| **T4** Resoluciones | Mapeos; separar "expediente no existe"; **D-1** (prevalidación → 409 antes del PDF); **D-6** (creación exclusiva y borrado del archivo propio); prueba de la invariante `ATOMIC_REQUESTS` | `resoluciones/adapters/views.py`, `resoluciones/services/emitir_informe.py`, `resoluciones/services/declarar_aptitud.py`, `resoluciones/adapters/pdf_generator.py`, `resoluciones/tests/` | T1a | O-1 → 409 sin PDF y sin cambios; fallo inyectado → sin archivo propio y BD intacta; preexistentes/ajenos intactos (hash) | `fix(resoluciones): O-1 como 409 explícito y rollback de archivos (E1-04, D-1, D-6)` · `--author="R0yalCode <royel.jima@unl.edu.ec>"` |
| **T5** Contrato + concurrencia | **Trabajo técnico propio:** componente `ErrorDominio` y respuestas por operación; prueba de contrato; **escenarios C1–C8** en PostgreSQL (§4.3), incluida la confirmación/refutación de H-29; regeneración y validación de `openapi.yaml`; e2e; documentación de cierre | `*/adapters/views.py` (solo `openapi_respuestas_extra`, tras integrar T1–T4), `backend/openapi.yaml`, `tests/integration/test_concurrencia_postgres.py` (nuevo), prueba de contrato, `docs/planificacion-backend`, bóveda | T3 (infraestructura); T1a…T4 para el contrato | `spectacular --validate`; contrato; C1–C8; suite completa | `test(concurrencia): escenarios PostgreSQL y contrato de errores de dominio (E1-04, O-2)` · `--author="JuanCalopinoo <Juan.calopino@unl.edu.ec>"` |

### 6.1 Modalidad de ejecución: implementación centralizada (DK-010, enmienda 2026-11-11)

- **Autorización de la modalidad:** el responsable del proyecto autorizó expresamente (2026-11-11) que **Claude Code implemente los cinco bloques** y prepare **un commit independiente por bloque** con `git commit --author` del integrante responsable. La **ejecución** del código fue autorizada expresamente el 2026-11-11 y finalizó ese mismo día (resultado en §10).
- **Significado de la atribución:** el autor Git de cada commit identifica al **integrante responsable de la tarea** según el reparto aprobado (contribución delegada), **no** a quien escribió materialmente el código: la implementación la ejecuta Claude Code de forma centralizada. El committer es la identidad Git configurada en el equipo que ejecuta (R0yalCode). Claude Code no figura como autor, committer ni coautor.
- **Correspondencia commit ↔ tarea ↔ integrante:**

| Orden | Bloque | Responsable | `--author` | Contenido del commit |
|---|---|---|---|---|
| 1 | T1 (T1a + T1b) | Dan1el17 | `Dan1el17 <steeven.pardo@unl.edu.ec>` | Solo archivos de T1a/T1b |
| 2 | T3 | 7777-C | `7777-C <markgonzalez20062@gmail.com>` | Solo archivos de T3 (incluida la infraestructura PostgreSQL) |
| 3 | T2 | JJOC3S | `JJOC3S <jimmy.ontaneda@unl.edu.ec>` | Solo archivos de T2 |
| 4 | T4 | R0yalCode | `R0yalCode <royel.jima@unl.edu.ec>` | Solo archivos de T4 |
| 5 | T5 | JuanCalopinoo | `JuanCalopinoo <Juan.calopino@unl.edu.ec>` | Solo archivos de T5 (después de T1–T4 y de la infraestructura de T3) |

- **Orden y dependencias:** T1 primero (núcleo del que dependen T2 y T4); T3 antes de T2 para disponer de PostgreSQL; el escenario C1 se **ejecuta** contra el código anterior a T2 para confirmar o refutar H-29 (resultado registrado en la bitácora), pero se **versiona** en el commit de T5; T5 al final (contrato, C1–C8, `openapi.yaml`, regresión).
- **Cuerpo de cada commit:** Conventional Commits con descripción técnica y validaciones reales, más la línea `Modalidad: implementación centralizada (DK-010, enmienda 2026-11-11) · Tarea <ID> · responsable <Identificador>`; sin menciones a IA (regla 2 de `CLAUDE.md`).
- **Separación de bloques:** antes de cada commit se verifica que los archivos preparados pertenecen solo a su bloque (tabla de §6). Si un cambio no es separable, se detiene y se consulta.
- **Rama:** propuesta `fix/e1-04-errores-dominio` desde `develop` actualizada, con los cinco commits y una única integración `--no-ff`. Crear la rama, hacer push o merge requiere autorización expresa.
- **Restricciones que no cambian:** sin `--force` ni variantes, sin reescribir historial publicado, sin rebase de ramas publicadas, sin modificar commits históricos (incluido `c0d75b6`).

Conflictos evitados: cada archivo tiene un único propietario; `openapi.yaml` solo lo regenera T5; `registrar_observacion.py` pertenece a T1 (lo usa `observar`), no a T2.

## 7. Reparto y conocimiento del equipo (DK-010)

| Tarea | Responsable (aprobado por el responsable del proyecto, 2026-11-11) | Identidad de autor | Conocimiento del integrante |
|---|---|---|---|
| T1a + T1b | Dan1el17 | steeven.pardo@unl.edu.ec | **Pendiente**: sin evidencia de notificación |
| T2 | JJOC3S | jimmy.ontaneda@unl.edu.ec | **Pendiente**: sin evidencia de notificación |
| T3 | 7777-C | markgonzalez20062@gmail.com | **Pendiente**: sin evidencia de notificación |
| T4 | R0yalCode | royel.jima@unl.edu.ec | **Conocido**: es el responsable que autorizó la modalidad, el reparto y la ejecución (2026-11-11) |
| T5 | JuanCalopinoo | Juan.calopino@unl.edu.ec | **Pendiente**: sin evidencia de notificación |

- En la modalidad centralizada no se exige que cada integrante ejecute personalmente su bloque; sí que sea **informado** de la tarea asignada y de que su identidad figurará como autor Git de ese bloque (DK-010). La comunicación de tareas fue autorizada el 2026-11-11 y los mensajes se prepararon, pero **no consta su envío ni ninguna respuesta**: el estado queda pendiente y no se presume.
- *(Nota 2026-11-12: requisito suprimido por la enmienda de DK-010 del 2026-11-12. La asignación del responsable es autorización suficiente; no se exige notificación. Ver `SIAAF-KNOWLEDGE/15-GIT-AND-WORKFLOWS/DK010_REGISTRO_NOTIFICACIONES.md`.)*
- **Registro de notificación (I-1).** Para cerrarlo, el responsable registra por cada integrante: fecha, medio con constancia escrita (issue o comentario en GitHub, chat del equipo) y respuesta. Texto mínimo de la notificación: *"En PLB-E1-04 + O-2 (rama `fix/e1-04-errores-dominio`) figuras como autor Git del commit de la tarea <ID> (`<hash>`). La implementación fue ejecutada de forma centralizada por Claude Code, autorizada por el responsable (DK-010, enmienda 2026-11-11); el autor Git representa tu responsabilidad delegada sobre la tarea, no que escribieras el código. Detalle: `docs/planificacion-backend/PLAN_E1-04_O-2.md` §10."*
- La atribución se limita al bloque asignado: no se atribuyen a un integrante cambios de otro bloque.
- La documentación de cierre (este plan y la bitácora de sesión) dejará constancia de la ejecución centralizada por Claude Code y de la tabla commit ↔ tarea ↔ integrante de §6.1.
- `c0d75b6` (E2-01) se conserva **sin reescribir**; la enmienda de DK-010 no tiene efectos retroactivos.

## 8. Riesgos

| Riesgo | Mitigación |
|---|---|
| 409 confundido con BE-11/FE-T1213 | §2.1; descripción explícita en OpenAPI y en la bóveda |
| Cambio de contrato (500/lista → JSON con `code`) | Aditivo para `detail`; el frontend ya muestra `detail` |
| El cambio de orden de bloqueo introduce regresiones o nuevas esperas | C1–C8 en PostgreSQL + regresión completa; `lock_timeout` para detectar esperas |
| H-29 no reproducible | Se documenta como no reproducida; el orden uniforme se mantiene por diseño |
| Borrar archivos ajenos | Solo la ruta devuelta por la creación propia; pruebas con centinelas |
| Pruebas PostgreSQL no ejecutables en algún equipo | Marcador `postgres` (omitidas con SQLite) + instrucciones Docker; el cierre exige su ejecución al menos una vez con evidencia |
| Atribución incorrecta o ambigua | Un commit por bloque con solo sus archivos (§6.1); constancia documental de la modalidad centralizada; la atribución representa responsabilidad de tarea, no autoría material |
| Lectura externa del historial (GitHub) | El historial muestra a cada integrante como autor de su bloque; la aclaración de la modalidad está en este plan, en `GIT_POLICY.md` y en la bitácora, no en GitHub |

## 9. Criterios de aceptación

1. Todo error nuevo o modificado devuelve JSON `{"detail","code"}`, comprobado con `response.json()` y declarado en OpenAPI (`ErrorDominio`).
2. Ningún error de dominio, recurso inexistente o transición inválida responde 500 genérico.
3. Los únicos 500 son explícitos, con `code`, log técnico y documentación: `configuracion_catalogo_incompleta`, `inconsistencia_observacion`, `emisor_no_configurado` y `documento_integridad_comprometida` (sin cambios).
4. O-1 responde 409 `regla_pendiente_o1` (o la alternativa que decida el responsable) sin generar PDF y sin decidir la regla.
5. C1–C8 pasan en **PostgreSQL real** con evidencia (comando, versión, resultado): sin 40P01/55P03, sin efectos parciales y con historial, auditoría, checklist, documentos y archivos coherentes.
6. Limpieza de archivos limitada a los propios, con centinelas preexistentes y ajenos intactos.
7. Sin cambios en `permissions.py`, `TRANSICIONES_PERMITIDAS`, DP-18 ni SHA-256.
8. Regresión: suite completa (554 + N; solo las 13 de `pypdf` fallan), `src/core` 76/76, e2e 4/4, `spectacular --validate` con 0 errores.
9. Cinco commits independientes conforme a DK-010 (modalidad centralizada): uno por bloque, con el `--author` de §6.1, solo archivos de su bloque, la línea de modalidad en el cuerpo y sin menciones a IA; constancia documental de la ejecución centralizada.

## 10. Resultado de la ejecución (2026-11-11)

**Modalidad:** implementación centralizada por Claude Code (DK-010, enmienda 2026-11-11), autorizada por el responsable. Committer de los cinco commits: R0yalCode. El autor Git identifica al integrante responsable de la tarea (responsabilidad delegada), no a quien escribió el código.

| Orden | Tarea | Autor Git | Commit | Archivos |
|---|---|---|---|---|
| 1 | T1 (T1a + T1b) | Dan1el17 | `2623685` | 6 |
| 2 | T3 | 7777-C | `daa8b41` | 9 |
| 3 | T2 | JJOC3S | `4d02baf` | 4 |
| 4 | T4 | R0yalCode | `3cdb47d` | 6 |
| 5 | T5 | JuanCalopinoo | `7e87483` | 10 |

Rama `fix/e1-04-errores-dominio` desde `develop` (`d1fa86e`), ejecutada en un worktree separado. Auditoría postimplementación: implementación **aprobada técnicamente**; integración condicionada a la integración documental (B-1), hecha con los commits documentales de esta rama.

**Pruebas (resultados reales):**

| Ámbito | Resultado |
|---|---|
| `pytest` (SQLite) | 606 aprobadas, 13 fallidas (`test_pdf_generator.py`, `pypdf` ausente). Línea base 554/13; listas de fallos idénticas en `develop` y en la rama |
| `src/core` | 88/88 |
| `tests/` (SQLite) | 24 aprobadas (4 e2e + 20 de contrato), 10 omitidas (`postgres`) |
| PostgreSQL 16.15, `-m postgres tests/integration` | 10/10 (C1–C8 + 2 de infraestructura), varias ejecuciones, sin errores en el log |
| PostgreSQL, `tests/` completo | 34/34 |
| PostgreSQL, `src/apps` (auditoría) | 21 fallos **idénticos en `develop` y en la rama**: 13 de `pypdf` y 8 de introspección de índices escritas para SQLite (H-30); la rama añade 52 aprobadas |
| `pypdf` | Con `pdftotext` como lector sustituto, `test_pdf_generator.py` pasa 30/30 en `develop` y en la rama: la causa es solo la dependencia ausente (PLB-E0-01) |
| OpenAPI | `spectacular --validate` sin errores; `openapi.yaml` sincronizado; componentes `ErrorDominio`, `ErrorSimple`, `ErrorValidacion` |

**H-29 reproducido y corregido:** C1 ejecutado contra el código anterior a T2 produjo en PostgreSQL `deadlock detected` (40P01) y HTTP 500 (`observar` esperaba la petición; `evaluar`, dentro de `registrar_transicion`, esperaba el expediente). Con T2, C1–C8 pasan sin interbloqueos.

**Desviaciones respecto del plan (menores, documentadas):** `observar` con `peticion_id` mal formado responde 404 `peticion_no_encontrada` (antes 500); el contrato usa `anyOf` con `ErrorSimple`/`ErrorValidacion` para 400/404, porque los 404 de `get_object_or_404` y los errores de validación no llevan `code`.

**Riesgos residuales y observaciones:**

- **I-3:** `subsanar_requisito` y `cargar_documento` guardan el PDF antes de terminar la transacción; si fallan después, el archivo queda huérfano (fuera de D-6).
- **I-4:** `backend/contracts/openapi.yaml` difiere de `backend/openapi.yaml` **desde `0a24109` (INC-01)**; no lo introdujo PLB-E1-04 y no se sincroniza en esta tarea.
- O-1 sigue pendiente de decisión funcional (hoy 409 `regla_pendiente_o1`).
- Solo C1 se ejecutó contra el código previo a la corrección; C2–C8, contra el código final.
- La protección contra sobrescritura cubre los nombres autogenerados del generador (`archivo_salida` explícito no se reserva); los archivos reservados se crean con permisos 0640.
- I-1: notificación de cuatro integrantes pendiente (§7). *(Nota 2026-11-12: requisito suprimido por la enmienda de DK-010 del 2026-11-12. La asignación del responsable es autorización suficiente; no se exige notificación. Ver `SIAAF-KNOWLEDGE/15-GIT-AND-WORKFLOWS/DK010_REGISTRO_NOTIFICACIONES.md`.)*
- Bitácora: `SIAAF-KNOWLEDGE/09-SESSION-LOGS/2026/2026-11-11-e1-04-o2-implementacion.md`.
