---
title: "Plan maestro de implementación backend"
subtitle: "Etapas, tareas, dependencias y criterios de aceptación (2026-11-11)"
date: 2026-11-11
---

# Plan maestro de implementación backend

## 1. Objetivo general

Completar el backend de SGT-SIAAF para que el frontend consuma información **real, consistente, segura y suficiente** para todas sus vistas, dashboards, reportes y KPI, ampliando la arquitectura existente sin reescribirla y sin inventar reglas institucionales.

Este plan **reemplaza el orden de ejecución** de los incrementos INC-01…INC-09 de `PLAN_MAESTRO_IMPLEMENTACION_SGT_SIAAF.md` (D01) y de `PLAN_INTEGRACION_FRONTEND_BACKEND.md` (D08) para la parte backend. **Conserva su contenido**: cada tarea cita el incremento de origen. Los cambios de orden se justifican en `REGISTRO_DECISIONES_TECNICAS.md` (DT-01).

## 2. Arquitectura actual

Monolito modular hexagonal, Django 5.2 + DRF + PostgreSQL (SQLite en memoria para las pruebas). Seis apps con `adapters/` (models, serializers, views), `services/` (casos de uso transaccionales) y `domain/`. RBAC por matriz (`RBAC_MATRIX`) y aislamiento por ámbito (`ScopeFilterMixin`). Rutas centralizadas en `config/urls.py`. OpenAPI generado por drf-spectacular. Detalle en `AUDITORIA_INTEGRAL_BACKEND.md` §3.

## 3. Arquitectura objetivo

```
apps/
  authentication  + refresh/logout (simplejwt.token_blacklist) + SesionUsuario (E3)
  expedientes     + iniciar verificación (E2) + cancelar (E2) + filtros de bandeja (E4)
                  + opcion_titulacion / HistorialModalidad / endpoints de modalidad (E5, bloqueado)
  peticiones      (sin cambios estructurales; SCOPE_ASIGNADO ya integrado)
  verificacion    + descubrimiento del checklist para quien subsana (E2)
  resoluciones    + lectura de informe/declaratoria (E4) + FirmaEC (E7, bloqueado)
  notificaciones  + paginación compatible (E4) + API de auditoría de solo lectura (E7)
  indicadores     NUEVA: services/ (una función por KPI, ámbito derivado del usuario)
                  adapters/ (DashboardMe, Indicadores) — sin modelos propios (E4)
core/
  adapters/throttling.py (E1, hecho) · openapi.py (E1, hecho) · scope_filter.py (+asignado, hecho)
  adapters/busqueda.py, exportacion.py (E6)
```

Principios: fórmulas solo en `indicadores/services`; las vistas aplican RBAC y serializan; el ámbito **nunca** viene de parámetros del cliente; las agregaciones se hacen en la base de datos (`Count`, `Avg`, `TruncMonth`, `Exists`), sin N+1.

## 4. Etapas y orden de ejecución

| Etapa | Nombre | Origen | Estado | Depende de |
|---|---|---|---|---|
| **E0** | Higiene de pruebas y línea base | — | Pendiente (E0-01 requiere autorización) | — |
| **E1** | Seguridad P0 | INC-01 | **E1-01…03 Hechas** · E1-04/05 pendientes | — |
| **E2** | Flujo de verificación operable | GAP-STATE-01, INC-21, FE-T407 | E2-01, E2-02a, E2-02b1, E2-02b2, E2-02b3.1 definidas (**no autorizadas**); E2-03 definida + AUT-01; E2-06 definida (DT-12); todas **no autorizadas**; E2-01, E2-02a y E2-03 requieren además AUT-02, AUT-03 y AUT-01; bloqueadas E2-02b3.2 (DP-20), E2-02c (DP-19), E2-04 (DP-08), E2-05 (DP-05b) | E1 |
| **E3** | Sesiones JWT | INC-02 | Lista para implementar (decidir DP-06) | E1 |
| **E4** | Indicadores, dashboards y bandeja | INC-04 | Lista (E4-01…04 sin bloqueos) | E1; E2 para que los KPI de verificación tengan datos reales |
| **E5** | Modalidades de titulación | INC-03 | **Bloqueada** (DP-02, DP-03) | E2, validación normativa |
| **E6** | Búsqueda, exportación, CSP | INC-05 | Lista (CSV) / bloqueada (PDF/Excel, DT-08) | E4 |
| **E7** | Dependencias, FirmaEC, catálogos, auditoría | VULN-006/010, BE-10 | Bloqueada salvo E7-04 | Decisiones institucionales |

**Ruta crítica (actualizada 2026-11-11):**

```
E1 (hecha)
 └─[autorización]→ E2-06 registrar_transicion() (DT-12, corrige H-24/H-25)
       (HECHA 2026-11-11)
       └─[autorización + AUT-02]→ E2-01 ─→ [autorización + AUT-03] E2-02a ─→ E2-02b2 ─→ E2-02b3.1
                                    └─[autorización + AUT-01]→ E2-03
 [DP-20]→ E2-02b3.2 ─→ E2-02b1 (su despliegue no puede preceder a E2-02b3.2: R-07)
 [DP-19]→ E2-02c
 E2 operable ─→ E4 (KPI de verificación con datos reales) ─→ INC-07/INC-08 del frontend
```

En paralelo y sin dependencia de E2: PLB-E1-04 y E4-01…04 (si se autorizan). E3 solo si el responsable autoriza la renovación de sesión.

## 5. Tareas por etapa

Formato por tarea: descripción · problema · requerimiento · estado · prioridad · dependencias · archivos · implementación · pruebas · aceptación · impacto API · impacto frontend · riesgos.

### E0 — Higiene de pruebas

#### PLB-E0-01 — Dependencia `pypdf` para las pruebas de PDF
| Campo | Valor |
|---|---|
| Descripción / problema | 13 pruebas de `test_pdf_generator.py` fallan en un entorno limpio porque `pypdf` no está declarada (extraen texto vacío) |
| Requerimiento | RQ-TST-01 |
| Estado / prioridad | Pendiente · P2 · **requiere autorización humana** (dependencia nueva, CLAUDE.md máxima 4) |
| Dependencias / archivos | — · `backend/requirements-dev.txt` |
| Implementación | Añadir `pypdf>=4,<6` solo a dev, o reescribir esas pruebas para no extraer texto |
| Pruebas / aceptación | `pytest src/apps` → 0 fallos |
| Impacto API / frontend / riesgos | Ninguno · ninguno · bajo |

#### PLB-E0-02 — Recolectar todas las suites
| Campo | Valor |
|---|---|
| Problema | `testpaths=["src/apps"]` excluye `src/core` (76 pruebas) y `tests/e2e` (4) |
| Requerimiento / estado / prioridad | RQ-TST-02 · Pendiente · P2 |
| Archivos / implementación | `backend/pyproject.toml`: `testpaths = ["src/apps", "src/core", "tests"]` |
| Aceptación | `pytest` ejecuta 510 + 76 + 4 pruebas; CI en verde |
| Riesgos | Fallos latentes en las suites hoy no ejecutadas (las 80 pasaron el 2026-11-11) |

#### PLB-E0-03 — Pruebas negativas de mass assignment/BOLA (VULN-013)
P3 · `tests` por app: enviar campos de solo lectura (`estado`, `estudiante_id`, `numero_providencia`) en los POST y verificar que se ignoran o rechazan. Sin impacto en la API.

### E1 — Seguridad P0 (INC-01)

#### PLB-E1-01 — `MutantOperationThrottle` (VULN-001) — **HECHA 2026-11-11**
| Campo | Valor |
|---|---|
| Problema | Las mutaciones (enviar, observar, checklist, subsanar, informe, declaratoria, solicitar emisión, crear) no tenían límite de frecuencia |
| Requerimiento | RQ-SEC-01 (D01 INC-01-T01) |
| Archivos | `core/adapters/throttling.py` (nuevo); `throttle_classes` en `ExpedienteViewSet`, `ChecklistViewSet`, `InformeViewSet`, `DeclaratoriaViewSet`, `PeticionViewSet`; `config/settings/base.py` (`"mutante"`); `.env.example` (`MUTANT_THROTTLE_RATE`) |
| Implementación | `SimpleRateThrottle` con ámbito fijo `mutante`, clave por `user.pk`, contador compartido; los métodos seguros no se limitan. La carga mantiene su throttle propio (`document_upload`) |
| Pruebas | `test_throttle_mutante_429_tras_exceder_tasa`, `…_no_limita_lecturas`, `…_contador_por_usuario`, `…_aplicado_a_vistas_criticas` |
| Aceptación | 429 al superar la tasa; las lecturas nunca devuelven 429 ✔ |
| Impacto API | Nueva respuesta 429 en 9 operaciones (OpenAPI regenerado) |
| Impacto frontend | Tratar 429 como error recuperable (mensaje + `Retry-After`); no hay reintento automático |
| Riesgos | Tasa provisional (DT-03); `LocMemCache` por proceso (DT-04) |

#### PLB-E1-02 — `SCOPE_ASIGNADO` en `ScopeFilterMixin` (VULN-002) — **HECHA 2026-11-11**
| Campo | Valor |
|---|---|
| Problema | El mixin no soportaba "asignado": la descarga replicaba el filtro a mano, sin unión de roles, y la Secretaría podía cargar en peticiones de otra dependencia de su carrera |
| Requerimiento | RQ-SEC-02 (D01 INC-01-T02) |
| Archivos | `core/adapters/scope_filter.py` (`scope_asignado_field`, `get_scope_grants`, `_predicado_asignado`); `peticiones/adapters/views.py` (concesiones desde RBAC solo en GET de documento; se elimina `_validar_ambito_descarga`); `peticiones/services/cargar_documento.py` (exige `dependencia_emisora == SECRETARIA_CARRERA`) |
| Implementación | Asignado = `dependencia_emisora ∈ roles` ∧ (carrera del usuario, o su facultad si no tiene carrera). En POST se conserva el contrato 403 vía servicio (DT-02) |
| Pruebas | 6 en `test_inc01_seguridad.py` (otra dependencia 404, otra carrera 404, jurista de facultad 200, carga de otra dependencia 403, sin ámbito, filtro del queryset) |
| Aceptación | Ningún registro ajeno visible; la suite previa sin regresiones ✔ |
| Impacto API | Descarga: un rol de facultad sin carrera ahora **puede** descargar lo asignado a su rol en su facultad (antes 404). Carga: la Secretaría recibe 403 en peticiones no asignadas a la Secretaría (antes 201) |
| Impacto frontend | V-05/V-08: mostrar 403/404 con el mensaje del backend |
| Riesgos | H-07: el jurista sigue sin ver documentos de otras dependencias (decisión DP-05) |

#### PLB-E1-03 — Verificación SHA-256 en la descarga (VULN-003) — **HECHA 2026-11-11**
| Campo | Valor |
|---|---|
| Problema | La descarga solo comprobaba la existencia del archivo |
| Archivos | `core/adapters/local_storage.py:calcular_sha256` (lectura por bloques de 64 KiB); `peticiones/adapters/views.py` (`DocumentoIntegridadAPI`, `openapi_respuestas_extra`) |
| Pruebas | `test_descarga_archivo_alterado_500_sin_servirlo`, `test_descarga_archivo_integro_200`, `test_openapi_declara_429_y_500_de_integridad` |
| Aceptación | Un archivo alterado no se sirve y responde 500 `documento_integridad_comprometida` ✔ |
| Impacto API / frontend | Nueva respuesta 500 documentada · `ErrorState` sin reintento útil (mensaje real) |
| Riesgos | Coste de E/S doble en cada descarga (≤ 10 MB por archivo: aceptable) |

#### PLB-E1-04 — Errores de dominio como 4xx (INC-21)
| Campo | Valor |
|---|---|
| Problema | `observar` y la carga envuelven reglas de negocio en `APIException` (500) |
| Requerimiento / prioridad | RQ-API-06 · P1 · sin dependencias |
| Archivos | `expedientes/adapters/views.py` (`ExpedienteNoEnVerificacionError`→400 `expediente_not_in_verification`; `PeticionNoEncontradaError`→404); `peticiones/adapters/views.py` (`PeticionNoEncontradaError`→404); también evaluar/subsanar si aplica |
| Pruebas | Una por excepción: código HTTP + `code` |
| Aceptación | Ninguna regla de negocio responde 5xx |
| Impacto API / frontend | Cambio de contrato justificado (500→400/404); el frontend ya muestra `detail`, así que no se rompe |
| Riesgos | Pruebas existentes que esperen 500 (actualizarlas) |

#### PLB-E1-05 — Auditar los fallos de integridad
P2 · añadir `EventoAuditoria.Accion.DOCUMENTO_INTEGRIDAD_FALLIDA` (migración de `choices`) y registrarla desde la descarga. Hoy solo se emite `logger.error`.

### E2 — Flujo de verificación operable (revisión documental 2026-11-11)

> **Fundamento y alcance.** DP-01, DP-04 y DP-05 se basan en el **criterio del responsable** obtenido en una consulta secundaria (NotebookLM), que no es fuente normativa (`REGISTRO_DECISIONES_TECNICAS.md` §4.1). "Definida" significa técnicamente especificada; **ninguna tarea de E2 está autorizada para implementarse** hasta que el responsable lo indique expresamente (§4.2 del registro, columna de autorización).
>
> **Leyenda de estado:** `DEF` definida, implementación **no autorizada** · `BL` bloqueada por una decisión pendiente · `AUT` requiere además una autorización específica.

| Tarea | Hallazgo | Requerimiento | Estado | Bloqueo / autorización |
|---|---|---|---|---|
| E2-01 Iniciar verificación + generar checklist | H-01, H-17 | RQ-FL-03, RQ-FL-21 | DEF + **AUT** | AUT-02 (celda nueva); requiere E2-06 (DT-12) antes o a la vez; DP-01b solo afecta al analista |
| E2-02a Consulta de observaciones | H-04 | RQ-FL-16 | DEF + **AUT** | AUT-03 (celda nueva); DP-21 solo afecta a la Secretaría de Carrera |
| E2-02b1 Rechazar la carga normal sobre OBSERVADO | H-21 | RQ-FL-18 | DEF | Coordinar con E2-02b3.2 (riesgo R-07) |
| E2-02b2 Notificación de subsanación al actor correcto | H-18 | RQ-FL-23 | DEF | DP-05b para incluir o no al analista (excluido por defecto) |
| E2-02b3.1 Observación en revisión (sin resolución automática) | H-18 | RQ-FL-06 | DEF | Si cambia el estado del expediente, lo hace mediante `registrar_transicion()` (DT-12) |
| E2-02b3.2 Múltiples observaciones: retorno del expediente a verificación | H-19 | RQ-FL-24 | **BL** | DP-20 |
| E2-02c Comportamiento único de observación y plazo | H-20 | RQ-FL-17 | **BL** | DP-19 |
| E2-03 Descarga de los 5 requisitos por el jurista | H-07 | RQ-FL-12 | DEF + **AUT** | AUT-01 (visto bueno para modificar la matriz 6.2) |
| E2-04 Cancelación | H-11 | RQ-FL-09 | **BL** | DP-08 |
| E2-05 Atribuciones del analista | H-22 | RQ-FL-19 | **BL** | DP-05b |
| E2-06 Historial y auditoría de transiciones (`registrar_transicion()`) | H-23, H-24, H-25 | RQ-FL-22, RQ-FL-25 | **HECHA 2026-11-11** (autorizada; pendiente de aprobación de fase) | — |

#### PLB-E2-01 — Iniciar verificación (`ENVIADA → EN_VERIFICACION`) y generar el checklist
| Campo | Valor |
|---|---|
| Objetivo funcional | Que el SECRETARIO_ABOGADO de la facultad inicie de forma explícita la verificación de un expediente ENVIADA y que, en la misma operación, queden creados los ítems del checklist que luego se evalúan |
| Problema | H-01 (no existe la transición) y H-17 (ningún servicio crea `ChecklistVerification`; la e2e fuerza ambos) |
| Requerimiento / prioridad | RQ-FL-03, RQ-FL-21 · **P0** |
| Estado | DEF (no autorizada) + **AUT-02** pendiente. El ANALISTA_APOYO queda excluido hasta DP-01b |
| Archivos / componentes | `expedientes/services/iniciar_verificacion.py` (nuevo); `expedientes/adapters/views.py` (acción `iniciar_verificacion` en `ExpedienteViewSet`, que ya hereda `MutantOperationThrottle`); `config/urls.py`; `authentication/adapters/permissions.py` (**nueva** celda `expedientes:iniciar_verificacion`: requiere **AUT-02**, independiente de la autorización de la tarea); reutiliza `verificacion/services/evaluar_checklist._get_or_create_checklist_verification`; `tests/e2e/test_full_workflow.py` |
| Endpoint | `POST /api/v1/expedientes/{id}/iniciar-verificacion/` (sin cuerpo) → 200 con `ExpedienteDetalleSerializer` |
| Autorización | RBAC `expedientes:iniciar_verificacion` POST = `{SECRETARIO_ABOGADO: SCOPE_FACULTAD}`; el queryset se filtra con `ScopeFilterMixin` (lo ajeno → 404); el servicio revalida la facultad (defensa en profundidad, igual que `evaluar_checklist`) |
| Atomicidad | Una sola `transaction.atomic()` con `select_for_update()` del expediente: validar ENVIADA → crear las filas PENDIENTE (idempotente) → `registrar_transicion(expediente, EN_VERIFICACION, actor, origen)` (DT-12). Si algo falla, no queda ni el estado cambiado ni filas huérfanas. Dos llamadas concurrentes: la segunda espera el bloqueo y recibe 400 |
| Plazo | Sin cambios: el plazo corre desde `fecha_recepcion`, como hoy (RN-002 de specify 001, que cita el Art. 235). **El cómputo exacto según el Art. 235 requiere verificación directa de la fuente normativa primaria**, que no está en el repositorio (`ARTICLES_AND_PROVISIONS.md`: estado "Citado (spec)") |
| Notificaciones | Al estudiante: "verificación iniciada" (solo informativa) |
| Historial | Mediante `registrar_transicion()` (DT-12): un `HistorialEstado` y un `ESTADO_CAMBIADO` con el actor autenticado. Por eso E2-01 **requiere E2-06** implementada antes o en el mismo incremento; si no, no debe implementarse (evita agravar H-24) |
| Pruebas unitarias | `expedientes/tests/test_iniciar_verificacion.py`: ENVIADA→EN_VERIFICACION; otro estado → error; filas = requisitos base activos de FASE_1; idempotencia de filas (segunda creación no duplica); rollback si falla la creación de filas (mock); plazo sin cambios; otra facultad → error |
| Pruebas de integración | 200 SECRETARIO_ABOGADO misma facultad; 404 otra facultad; 403 ESTUDIANTE/ANALISTA_APOYO/DECANO/SECRETARIA_CARRERA; 400 si ya está en verificación; 401 anónimo; 429 heredado; `GET /checklist/` devuelve los ítems tras iniciar; e2e sin forzar estados ni crear filas a mano |
| Criterios de aceptación | (1) Un expediente ENVIADA puede evaluarse por API extremo a extremo; (2) operación atómica verificada por prueba de rollback; (3) ningún rol distinto del SECRETARIO_ABOGADO de la facultad puede ejecutarla; (4) contrato OpenAPI regenerado |
| Dependencias | E1 (hecha); **E2-06** (DT-12); **AUT-02**. No depende de DP-18 (la precondición de envío no cambia) |
| Impacto frontend | Acción "Iniciar verificación" en V-08 para ENVIADA |
| Riesgos | DP-01b podría ampliar el actor (una celda); la notificación al estudiante se apoya en el criterio funcional, no en la norma |

#### PLB-E2-02a — Consulta de observaciones por el estudiante
| Campo | Valor |
|---|---|
| Objetivo funcional | Que el estudiante vea qué requisitos están observados, el motivo, la fecha y el estado de subsanación, y obtenga el identificador necesario para subsanar |
| Problema | H-04: hoy recibe 403 en el checklist y el detalle no muestra el motivo, la fecha ni el id |
| Requerimiento / prioridad | RQ-FL-16 · P1 |
| Estado | DEF (no autorizada) + **AUT-03** pendiente |
| Archivos / componentes | `verificacion/adapters/views.py` (vista de lista con `ScopeFilterMixin`), `verificacion/adapters/serializers.py`, `config/urls.py`, `authentication/adapters/permissions.py` (**nueva** celda `expedientes:observaciones`: requiere **AUT-03**) |
| Endpoint | `GET /api/v1/expedientes/{id}/observaciones/` → `[{id, requisito_codigo, requisito_nombre, motivo, fecha_observacion, estado_subsanacion, checklist_verification_id, puede_subsanar}]` |
| Autorización | GET: `ESTUDIANTE: SCOPE_OWN`, `SECRETARIO_ABOGADO: SCOPE_FACULTAD`, `ADMINISTRADOR: ALLOW`. ANALISTA_APOYO según DP-05b (excluido por defecto). SECRETARIA_CARRERA según **DP-21** (excluida por defecto). No expone `registrada_por` ni datos de otros expedientes |
| Pruebas unitarias | Serializer: campos exactos (sin datos internos); `puede_subsanar` verdadero solo con expediente OBSERVADA y checklist OBSERVADO; `estado_subsanacion` derivado de `resuelta` mientras no exista E2-02b3.1 |
| Pruebas de integración | Dueño 200; otro estudiante 404; jurista de otra facultad 404; jurista de la facultad 200; SECRETARIA_CARRERA y ANALISTA 403; expediente sin observaciones → `[]`; número constante de consultas (`django_assert_num_queries`) |
| Criterios de aceptación | (1) El estudiante identifica qué subsanar sin acceso al checklist completo; (2) aislamiento por estudiante y facultad verificado; (3) OpenAPI regenerado |
| Dependencias | **AUT-03**. Útil antes de E2-02b1 (ver R-07) |
| Impacto frontend | V-04: lista de observaciones y botón "Subsanar" con el id real (resuelve el hallazgo crítico de FE-T407) |
| Riesgos | Exponer más datos de los necesarios (mitigado con el serializer cerrado) |

#### PLB-E2-02b1 — Rechazar la carga normal sobre peticiones OBSERVADO
| Campo | Valor |
|---|---|
| Objetivo funcional | Que la única vía para presentar una nueva versión de un requisito observado sea la subsanación |
| Problema | H-21: `cargar_documento` admite OBSERVADO y pasa la petición a CARGADO sin tocar la observación, el checklist ni el plazo |
| Requerimiento / prioridad | RQ-FL-18 · P1 |
| Estado | DEF (no autorizada) |
| Archivos | `peticiones/services/cargar_documento.py` (quitar `"OBSERVADO"` de `estados_permitidos`); `docs/04-api/endpoints/peticiones.md`; `openapi.yaml` si cambia la descripción |
| Endpoint | `POST /api/v1/peticiones/{id}/documento/`: con petición OBSERVADO responde el error de estado ya existente (`EstadoPeticionInvalidoError` → `ExpedienteEstadoInvalidoAPI`), con un mensaje que remite a `POST /checklist/{id}/subsanar/` |
| Autorización | Sin cambios de RBAC |
| Pruebas unitarias | El servicio rechaza OBSERVADO; mantiene PENDIENTE, SOLICITADO y CARGADO |
| Pruebas de integración | Estudiante dueño con petición OBSERVADO → error sin documento creado, petición, observación y checklist intactos; la subsanación sigue funcionando |
| Criterios de aceptación | No existe ninguna ruta que cambie una petición OBSERVADO sin pasar por la subsanación |
| Dependencias | E2-02a (el estudiante necesita el id para subsanar). **Coordinar con E2-02b3.2**: hoy la carga normal es la única salida para el segundo ítem observado bloqueado por H-19 (R-07) |
| Impacto API / frontend | Cambio de contrato justificado (H-21) · V-05 debe ofrecer "Subsanar" en lugar de "Cargar" para OBSERVADO |
| Riesgos | R-07: desplegarla antes de resolver DP-20 deja sin vía de entrega el segundo y siguientes ítems observados |

#### PLB-E2-02b2 — Notificación de subsanación al actor correcto
| Campo | Valor |
|---|---|
| Objetivo funcional | Que la subsanación avise a quien debe revisarla y que el estudiante reciba un mensaje coherente con su acción |
| Problema | H-18 (parte de notificación): hoy el aviso "proceda a la verificación" llega al estudiante |
| Requerimiento / prioridad | RQ-FL-23 · P1 |
| Estado | DEF (no autorizada) |
| Archivos | `verificacion/services/subsanar_requisito.py`; consulta de destinatarios análoga a `resoluciones/services/emitir_informe._obtener_decanos_facultad` |
| Endpoint | Sin cambios (`POST /api/v1/checklist/{id}/subsanar/`) |
| Autorización / destinatarios | Usuarios activos con rol SECRETARIO_ABOGADO y `facultad_id` del expediente. ANALISTA_APOYO solo si DP-05b lo determina. El estudiante recibe una confirmación de recepción "pendiente de revisión" |
| Pruebas unitarias | Destinatarios = juristas de la facultad (no los de otra facultad, no el analista); sin juristas → no falla y se registra un log |
| Pruebas de integración | Tras subsanar: N notificaciones a juristas, 1 confirmación al estudiante, textos correctos |
| Criterios de aceptación | Ninguna notificación dirigida al verificador llega al estudiante |
| Dependencias | Ninguna (independiente de DP-20) |
| Riesgos | Bajo |

#### PLB-E2-02b3 — Resolución de observaciones (H-18, H-19)

**E2-02b3.1 — Observación "en revisión" sin resolución automática (DEF, no autorizada)**

| Campo | Valor |
|---|---|
| Objetivo funcional | Que subsanar no resuelva la observación: queda en revisión hasta que el SECRETARIO_ABOGADO verifique el requisito |
| Problema | H-18 (parte de resolución automática) |
| Requerimiento / prioridad | RQ-FL-06 · P1 |
| Archivos | `verificacion/adapters/models.py` + migración **aditiva** (`estado_subsanacion`: PENDIENTE, EN_REVISION, ACEPTADA, REITERADA; `fecha_subsanacion`); `services/subsanar_requisito.py` (EN_REVISION, sin `resuelta=True`); `services/evaluar_checklist.py` (VERIFICADO → ACEPTADA + `resuelta=True`; OBSERVADO sobre EN_REVISION → REITERADA + nueva observación); `services/registrar_observacion.py` (guarda de duplicados que tenga en cuenta EN_REVISION/REITERADA) |
| Endpoints | Sin rutas nuevas; cambia el efecto de `subsanar` y de `PUT /checklist/{id}/`; E2-02a expone `estado_subsanacion` |
| Autorización | Sin cambios de RBAC |
| Atomicidad | Subsanar (versión N+1 + observación EN_REVISION + ítem PENDIENTE) en una transacción, como hoy |
| Pruebas unitarias | Subsanar no marca `resuelta`; evaluar VERIFICADO acepta; evaluar OBSERVADO reitera y crea una observación nueva; migración: `resuelta=True` existente → ACEPTADA, `False` → PENDIENTE |
| Pruebas de integración | Ciclo completo observar → subsanar → verificar y observar → subsanar → reobservar; actualizar las pruebas actuales que esperan `resuelta=True` tras subsanar, con trazabilidad a DP-04 |
| Criterios de aceptación | Ninguna observación queda resuelta sin verificación del jurista; el historial documental N+1 se conserva |
| Dependencias | E2-01 (sin checklist no hay ciclo real). No depende de DP-20 |
| Riesgos | Pruebas existentes a reescribir; la migración debe ser reversible |

**E2-02b3.2 — Múltiples observaciones: retorno del expediente a verificación (BL: DP-20)**

| Campo | Valor |
|---|---|
| Objetivo funcional | Que todos los ítems observados puedan subsanarse, y que el expediente vuelva a EN_VERIFICACION según la regla institucional |
| Problema | H-19: tras la primera subsanación el expediente pasa a EN_VERIFICACION y el resto de ítems OBSERVADO ya no puede subsanarse |
| Requerimiento / prioridad | RQ-FL-24 · P1 |
| Bloqueo | **DP-20** (¿retorno por ítem o cuando todos estén en revisión?). No se implementa ninguna de las dos opciones hasta decidir |
| Archivos (previstos) | `services/subsanar_requisito.py` (`_reanudar_plazo_y_cambiar_estados`), y su efecto sobre el plazo según DP-19 |
| Pruebas previstas | Dos y tres ítems observados: todos subsanables; transición del expediente según la regla aprobada; plazo coherente con DP-19 |
| Criterio de aceptación | Ningún ítem observado queda sin vía de subsanación |

#### PLB-E2-02c — Comportamiento único de observación (H-20) — **BL: DP-19**
| Campo | Valor |
|---|---|
| Objetivo funcional | Que observar un requisito produzca el mismo efecto por `POST /expedientes/{id}/observar/` y por `PUT /checklist/{id}/` (estado, checklist, observación, notificación, plazo y registro) |
| Problema | H-20: el primero pausa el plazo y actualiza el checklist con un `update()` que no hace nada si no hay filas; el segundo no pausa; las guardas de duplicados difieren |
| Requerimiento | RQ-FL-17 · P1 |
| Implementación prevista | Un único servicio de dominio que invocan ambas rutas (sin eliminar endpoints del contrato) |
| Bloqueo | DP-19 (pausa, reinicio o continuidad del plazo). La unificación no se despliega con un efecto sobre el plazo supuesto |
| Pruebas previstas | Paridad de efectos entre ambas rutas (misma secuencia de estados y registros) |

#### PLB-E2-03 — Descarga de los 5 requisitos por el jurista
| Campo | Valor |
|---|---|
| Objetivo funcional | Que el SECRETARIO_ABOGADO pueda leer y descargar los documentos de todos los requisitos de los expedientes de su facultad para verificarlos |
| Problema | H-07: hoy solo descarga lo asignado a su rol (`SCOPE_ASIGNADO`) |
| Requerimiento / prioridad | RQ-FL-12 · P1 |
| Estado | DEF (no autorizada) + **AUT-01** pendiente: modifica la celda **implementada** `peticiones:documento` GET (vigente desde `795d6a7`), que la matriz 6.2 de la especificación aprobada no define (solo define el POST). Requiere la autorización expresa del responsable además de la autorización de la tarea |
| Archivos | `authentication/adapters/permissions.py` (`peticiones:documento` GET, `SECRETARIO_ABOGADO`: `SCOPE_ASIGNADO` → `SCOPE_FACULTAD`); `peticiones/tests/`; `docs/04-api/endpoints/peticiones.md`; `docs/06-seguridad/roles-permisos.md` |
| Endpoints | `GET /api/v1/peticiones/{id}/documento/` y `GET /api/v1/peticiones/{id}/documento/{version}/` |
| Autorización | Solo el SECRETARIO_ABOGADO; ANALISTA_APOYO sin cambios (DP-05b); `PeticionViewSet.get_scope_grants` ya traduce `facultad` → filtro `expediente__facultad_id` |
| Pruebas unitarias | Concesiones: el jurista obtiene `facultad` en GET y sigue sin concesión de carga |
| Pruebas de integración | Misma facultad, cualquier dependencia → 200 (con SHA-256); otra facultad → 404; analista sin cambios; estudiante, Secretaría y admin sin regresión |
| Criterios de aceptación | El jurista descarga los 5 requisitos de su facultad y nada fuera de ella |
| Dependencias | AUT-01 |
| Impacto frontend | V-08: descarga de los documentos a verificar |
| Riesgos | Ampliación de lectura: mitigada con pruebas IDOR entre facultades |

#### PLB-E2-04 — Cancelación de expediente — **BL: DP-08**
Servicio `cancelar_expediente`; actor, estados de origen y efectos por definir. Requerimiento RQ-FL-09; hallazgo H-11.

#### PLB-E2-05 — Atribuciones del ANALISTA_APOYO — **BL: DP-05b**
Requerimiento RQ-FL-19; hallazgo H-22. Hoy evalúa de forma definitiva y observa vía `PUT` sin que `SCOPE_BORRADOR` tenga efecto, y la celda `informes` POST contradice al servicio. Opciones en DP-05b. **No se amplía ni se reduce** ningún permiso del analista hasta decidir.

#### PLB-E2-06 — Historial y auditoría de transiciones: `registrar_transicion()` — **HECHA 2026-11-11 (autorizada por el responsable; pendiente de su aprobación de fase)**

**Resultado de la implementación**

| Aspecto | Evidencia |
|---|---|
| Función | `backend/src/apps/expedientes/services/transiciones.py`: `registrar_transicion(expediente, nuevo_estado, actor, *, origen, campos_adicionales=())`, `TRANSICIONES_PERMITIDAS` (5 transiciones existentes; ENVIADA→EN_VERIFICACION **no** incluida: llegará con E2-01), `TransicionNoPermitidaError`, `ActorRequeridoError` |
| Estado anterior | Leído con `select_for_update()` desde la BD dentro de la transacción (no de la instancia) |
| Actor | Obligatorio y autenticado; `enviar_expediente.execute(..., *, actor)` recibe `request.user` desde la vista; el resto de servicios ya recibían `usuario`. El rol registrado es el de la transición (multirrol cubierto); los roles de la tabla solo atribuyen, **no autorizan** |
| Servicios migrados | `enviar_expediente`, `registrar_observacion`, `evaluar_checklist`, `subsanar_requisito`, `emitir_informe` (corrige H-25) y `declarar_aptitud` |
| Señales | `notificaciones/adapters/signals.py`: se eliminó el `pre_save` y la auditoría de transiciones del `post_save` del expediente, así como el receptor de `HistorialEstado`. Se conserva `EXPEDIENTE_CREADO` y los eventos de negocio |
| Eventos históricos | No se modifican (prueba `test_eventos_historicos_no_se_modifican`). Fecha de corte: 2026-11-11; los `ESTADO_CAMBIADO` anteriores pueden tener actor estudiante y duplicados |
| Contrato API | Sin cambios (`openapi.yaml` regenerado idéntico) |
| Pruebas nuevas | `expedientes/tests/test_transiciones.py` (10: actor y estado anterior correctos, estado anterior desde la BD, transición no permitida sin efectos, actor obligatorio ×2, rollback si falla la auditoría, campos adicionales, rol en usuario multirrol, eventos históricos intactos, arquitectura); `test_save_directo_no_audita_transicion`; `test_emitir_informe_historial_estado_anterior_real_h25`; aserciones nuevas en la e2e (5 transiciones = 5 eventos, actores reales) |
| Pruebas adaptadas (con trazabilidad a DT-12) | 2 pruebas que exigían auditoría por `save()` directo; 7 llamadas a `enviar_expediente.execute` con `actor=` explícito |
| Ejecución | `pytest` (src/apps): **509 aprobadas / 13 fallidas** (las 13 de `pypdf`, previas); `src/core` 76/76; e2e 4/4; INC-01 + E2-06: 23/23; `spectacular --validate`: 0 errores |
| Verificación empírica | e2e instrumentada: antes 8 `ESTADO_CAMBIADO` para 6 transiciones (6 con actor estudiante); ahora 1 por transición de servicio, con actor estudiante/jurista/decano según quien actúa |
| Limitación conocida | La e2e aún fuerza ENVIADA→EN_VERIFICACION con `save()` (no auditado, como corresponde) hasta E2-01. La prueba de arquitectura cubre asignaciones a `expediente|cadena|exp|instance.estado` y creaciones de `HistorialEstado`, no `QuerySet.update(estado=…)` (no hay ninguna hoy) |

**Especificación original**
| Campo | Valor |
|---|---|
| Objetivo funcional | Que cada transición del expediente quede registrada **una sola vez**, con el estado anterior correcto y el usuario autenticado que la ejecuta, en el historial y en la auditoría |
| Problema | H-23 (historial solo en informe y declaratoria), **H-24** (la señal del expediente atribuye todo `ESTADO_CAMBIADO` al estudiante; con la señal de `HistorialEstado` hay duplicados: 8 eventos para 6 transiciones en la e2e) y **H-25** (`emitir_informe.py` crea el historial tras guardar y registra `INFORME_EMITIDO→INFORME_EMITIDO`) |
| Requerimiento / prioridad | RQ-FL-22, RQ-FL-25 · P1 (requisito previo de E2-01) |
| Decisión | DP-22 resuelta técnicamente por **DT-12** (`REGISTRO_DECISIONES_TECNICAS.md`) |
| Archivos / componentes | `expedientes/services/transiciones.py` (nuevo: `registrar_transicion()` y tabla de transiciones permitidas); servicios que cambian el estado: `enviar_expediente`, `registrar_observacion`, `evaluar_checklist`, `subsanar_requisito`, `emitir_informe` (corrige H-25), `declarar_aptitud`; vistas (paso del actor autenticado); `notificaciones/adapters/signals.py` (se retira la auditoría de transiciones de las señales del expediente y del historial; `EXPEDIENTE_CREADO` se conserva) |
| Endpoints | Ninguno nuevo; sin cambios de contrato. Alimenta `GET /expedientes/{id}/historial/` (E4-08) |
| Autorización | No modifica la matriz RBAC. El actor es el `request.user` de la vista que ejecuta la acción |
| Atomicidad | Estado, historial y evento en la transacción del servicio llamador; si falla cualquiera, nada persiste |
| Pruebas unitarias | Transición válida → 1 `HistorialEstado` + 1 `ESTADO_CAMBIADO` con actor y estado anterior correctos; transición no permitida → error sin efectos; rollback; caso H-25 (informe: `EN_VERIFICACION→INFORME_EMITIDO`) |
| Pruebas de integración | e2e completa: número de `ESTADO_CAMBIADO` = número de transiciones (6 en el flujo actual); actor por transición = estudiante, jurista o decano según quien actúa; ninguna transición sin registro; prueba de arquitectura: ninguna asignación directa de `expediente.estado` fuera de `registrar_transicion()` |
| Criterios de aceptación | Cero duplicados; atribución correcta; estado anterior correcto en todos los registros nuevos; eventos existentes intactos (fecha de corte documentada) |
| Dependencias | Autorización de implementación. Debe preceder o acompañar a E2-01 y E2-02b3.1 |
| Riesgos | Pruebas actuales que cuentan eventos o esperan el actor estudiante (actualizarlas con trazabilidad a DT-12); revisar que ningún flujo cambie el estado con `QuerySet.update()` (hoy no se detectó ninguno) |

### E3 — Sesiones JWT (INC-02)

#### PLB-E3-01 — Refresh con rotación y blacklist
| Campo | Valor |
|---|---|
| Problema | H-05: el refresh de 24 h se emite pero no puede usarse; no hay revocación |
| Requerimiento / prioridad | RQ-SES-01 · P1 · decidir DP-06 (rotación+blacklist frente a sliding) |
| Archivos | `config/settings/base.py` (`ROTATE_REFRESH_TOKENS`, `BLACKLIST_AFTER_ROTATION`, `rest_framework_simplejwt.token_blacklist` en `INSTALLED_APPS`, que ya forma parte de simplejwt: **sin dependencia nueva**); `config/urls.py` (`TokenRefreshView` con throttle `auth`); migración de `token_blacklist` |
| Pruebas | Refresh válido → nuevo par; refresh rotado reutilizado → 401; throttle |
| Aceptación | El frontend puede renovar la sesión sin re-login, si el responsable lo autoriza (`plan.md` §6 del frontend hoy lo prohíbe) |
| Impacto frontend | Requiere modificar la política de sesión del frontend (decisión aparte) |
| Riesgos | Crecimiento de la tabla de blacklist (`flushexpiredtokens` periódico) |

#### PLB-E3-02 — `POST /auth/logout/`
P1 · blacklist del refresh recibido; 205/200; 400 con token inválido. Depende de E3-01.

#### PLB-E3-03 — `SesionUsuario` y KPI-ADM-09
P2 · variante **sin Redis/Celery** (D06 §11, DT-05): actualización de actividad como máximo cada 5 min por sesión. Expone `GET /indicadores/usuarios-activos/` (ADMINISTRADOR). Se corrige C-12 (usar el `jti` nativo de simplejwt; sin `auto_now`).

### E4 — Indicadores, dashboards y bandeja (INC-04)

#### PLB-E4-01 — App `indicadores` y servicios base
| Campo | Valor |
|---|---|
| Problema | No hay fuente de datos para los dashboards de funcionarios |
| Requerimiento / prioridad | RQ-KPI-01 · P1 · sin bloqueos |
| Archivos | `apps/indicadores/{services,adapters,tests}`; registro en `INSTALLED_APPS` |
| Implementación | `services/ambito.py`: deriva el ámbito del usuario autenticado (reutiliza la semántica de `ScopeFilterMixin`, sin duplicarla); `services/kpi_*.py`: una función pura por KPI, que recibe el queryset ya acotado. Corregir C-10 (denominador = requisitos base activos) y C-11 (cruce checklist↔petición por `(expediente, requisito)`) |
| Pruebas | Por KPI: casos 0, 1 y N; ámbitos; doble cálculo frente al ORM directo |
| Aceptación | Cobertura ≥ 90 %; ninguna consulta por fila (assertNumQueries) |
| Riesgos | Usuarios multirrol (C-18): unión de ámbitos (DT-07) |

#### PLB-E4-02 — `GET /api/v1/dashboard/me/`
P1 · compone tarjetas, gráfico y alertas por rol con los KPI implementables (ver `PLAN_APIS_DASHBOARDS_KPI.md` §4). **No** incluye `modalidad_titulacion` hasta E5 (la clave se omite, nunca se rellena con valores ficticios). `Cache-Control: no-store`.

#### PLB-E4-03 — `GET /indicadores/culminacion/` y `/evolucion/`
P2 · cohorte según IK §7; `CANCELADA` excluida del numerador y, por defecto, también del denominador, informada aparte (pendiente de ratificar en DP-10). La serie mensual rellena los ceros en Python a partir de `TruncMonth` (portable a SQLite para las pruebas; DT-06). `meses ≤ 24`.

#### PLB-E4-04 — Celdas RBAC `dashboard` e `indicadores:*`
P1 · según D05 §6, **excepto** RESPONSABLE_DEPENDENCIA (bloqueado, DP-07). Pruebas de 403 por rol.

#### PLB-E4-05 — Filtros de bandeja
P1 · parámetros en lista blanca: `estado` (enum, dentro del mapa del rol), `desde`/`hasta` (`fecha_recepcion`), `numero` (prefijo), `vencidos=true`, `ordering ∈ {fecha_limite_atencion, fecha_creacion, -…}`. Sin dependencia nueva (parseo manual). La lista para SECRETARIA_CARRERA/DIRECTOR_CARRERA depende de DP-12.

#### PLB-E4-06 — Paginación opt-in de notificaciones
P2 · si llega `?page=`, se pagina; sin él, se mantiene `{results: [...]}` (contrato actual, INC-19). Así no se rompe V-02.

#### PLB-E4-07 — Lectura de informe y declaratoria
P2 · `GET /expedientes/{id}/informe/` y `/declaratoria/` (metadatos + descarga del PDF con SHA-256), con ámbito por facultad. Lo necesita V-08.

#### PLB-E4-08 — Historial de estados del expediente
P2 · `GET /expedientes/{id}/historial/` sobre `HistorialEstado` (ya poblado por los servicios), con el mismo ámbito que el detalle. Alimenta el timeline de V-04 y KPI-EST-08.

#### PLB-E4-09 — Listado de versiones de documentos
P2 · `GET /peticiones/{id}/documentos/` con los metadatos de `DocumentoEntregado` (versión, fecha, tamaño, hash, vigente), con el mismo ámbito que la descarga. Lo necesita V-06.

### E5 — Modalidades de titulación (INC-03) — **BLOQUEADA**

Tareas INC-03-T01…T07 de D01, **sin cambios de alcance**, con estas condiciones previas: DP-02 (validación firmada de los arts. 39, 40, 212, 216 y 233 RRA-UNL), DP-03 (fuente real de reprobaciones y tercera matrícula: ampliar `ISGALegacyPort`), y la resolución de C-01…C-07. **No se implementa ni se simula** (CA-G-01).

### E6 — Búsqueda, exportación y CSP (INC-05)

- **PLB-E6-01** `GET /api/v1/buscar/?q=&tipo=expediente` (P2): `numero_expediente`/`numero_providencia` por `istartswith` y cédula del estudiante, siempre dentro del ámbito; mínimo 3 caracteres; máximo 20 resultados. `pg_trgm` queda como mejora (DT-08).
- **PLB-E6-02** `GET /api/v1/exportar/?recurso=bandeja&formato=csv|pdf` (P2): CSV con la librería estándar y PDF con `reportlab` (ya es dependencia), con los mismos filtros y el mismo ámbito que la bandeja, y un máximo de filas. Excel requiere `openpyxl` (DP-17).
- **PLB-E6-03** `POST /api/v1/csp-report/` (P2): anónimo, throttle por IP, payload ≤ 8 KB, se registra en el log estructurado (sin modelo nuevo inicialmente).

### E7 — Bloqueadas por decisiones institucionales

- **PLB-E7-01** RBAC de RESPONSABLE_DEPENDENCIA (DP-07; requiere modelar "dependencia" como algo distinto del rol).
- **PLB-E7-02** FirmaEC (DP-09).
- **PLB-E7-03** Catálogo de carreras/facultades (BE-10, DP-11).
- **PLB-E7-04** `GET /api/v1/auditoria/` de solo lectura para ADMINISTRADOR (P2, **no bloqueada**): filtros `accion`, `desde`, `hasta`, `expediente_id`; paginada; datos sensibles filtrados.

## 6. Siguiente etapa recomendada

1. **Autorizar** la implementación de E2-06 (DT-12) y, después, E2-01, E2-02a, E2-02b2 y E2-02b3.1; conceder o denegar **AUT-01** (E2-03), **AUT-02** (E2-01) y **AUT-03** (E2-02a); para cerrar E2, decidir DP-20, DP-19, DP-21, DP-01b y DP-05b.
2. Mientras tanto, ejecutar **PLB-E1-04** (bajo riesgo, sin decisiones) y **PLB-E4-01 → E4-04** (indicadores con los KPI no ambiguos).
3. Después, **E3** si el responsable autoriza la renovación de sesión en el frontend.

## 7. Estrategia de pruebas

- **Unitarias de servicio** por regla y por KPI (casos 0/1/N, límites de fechas, ámbitos).
- **Integración HTTP** por endpoint: 200/201, 400/422, 401, 403 (RBAC), 404 (IDOR), 429 (throttle).
- **Contrato**: `manage.py spectacular --validate` sin errores; pruebas que comprueban las respuestas declaradas (como `test_openapi_declara_429_y_500_de_integridad`).
- **Rendimiento**: `django_assert_num_queries` en dashboards y bandeja (número constante de consultas).
- **Regresión**: suite completa (`src/apps`, `src/core`, `tests/e2e`) antes de cada cierre de tarea.

## 8. Puntos de control

| Hito | Condición de salida |
|---|---|
| PC-1 (cerrado 2026-11-11) | E1-01…03 hechas; 497 pruebas aprobadas (13 fallos previos de `pypdf`); OpenAPI válido |
| PC-2 | E2-01, E2-02a, E2-02b1/2/3, E2-03 y E2-06 implementadas con sus decisiones aprobadas (DP-19, DP-20, AUT-01, AUT-02, AUT-03; DT-12 autorizada); e2e sin forzar estados ni crear el checklist a mano; un evento de auditoría por transición con el actor correcto |
| PC-3 | E4-01…05 hechas; `/dashboard/me/` cubre los 7 roles operativos con KPI implementables |
| PC-4 | E3 hecha (si se autoriza); frontend con logout real |
| PC-5 | Validación normativa firmada → E5 |
