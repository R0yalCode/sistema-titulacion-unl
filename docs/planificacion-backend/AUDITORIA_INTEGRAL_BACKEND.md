---
title: "Auditoría integral del backend"
subtitle: "SGT-SIAAF — estado real contrastado con Documentacion-parte-2"
date: 2026-11-11
---

# Auditoría integral del backend SGT-SIAAF

> **Regla de evidencia.** La documentación define lo que *debería* existir; el código y las pruebas ejecutadas determinan lo que *existe*. Toda afirmación de estado de este documento se verificó contra el repositorio en la rama `security/inc-01-endurecimiento-backend` (derivada de `develop`, 2026-11-11). Cuando no se pudo verificar, se marca **PENDIENTE DE VALIDACIÓN**.

## 1. Resumen ejecutivo

- El backend (Django 5.2 + DRF, monolito modular hexagonal, 6 apps) implementa de forma sólida el **núcleo de la Fase 1** (expediente → peticiones documentales → checklist → informe → declaratoria), con RBAC de mundo cerrado, aislamiento IDOR por ámbito, validación estricta de PDF, plazos de 8 días hábiles con pausas y auditoría inmutable.
- **No es completo para el frontend.** Faltan, en este orden de impacto:
  1. **Transición `ENVIADA → EN_VERIFICACION`** (GAP-STATE-01). Sin ella, el flujo de verificación (evaluar checklist, observar, emitir informe) **no es alcanzable por la API**; la prueba E2E lo fuerza asignando el estado. Además, ningún servicio crea los ítems del checklist (H-17). *Actualización 2026-11-11:* el responsable aportó un criterio funcional (fuente secundaria) que define la solución técnica (PLB-E2-01). **Implementada el 2026-11-11** (E2-01, AUT-02): H-01 y H-17 corregidos.
  2. **App `indicadores` y `GET /dashboard/me/`**: no existen. Los dashboards por rol (excepto el del estudiante, que combina bandeja y notificaciones) no tienen fuente de datos.
  3. **Modalidades de titulación (TIC/EC)**: ausentes en todas las capas y **bloqueadas** por validación normativa (RRA-UNL arts. 39, 40, 212, 216, 233) y por datos: el mock SGA no expone reprobaciones ni tercera matrícula.
  4. **Sesiones**: no hay endpoint de refresh ni de logout; el refresh de 24 h no se usa.
- **Seguridad P0 (INC-01) cerrada en esta sesión**: VULN-001 (throttling de operaciones mutantes), VULN-002 (`SCOPE_ASIGNADO` en `ScopeFilterMixin`) y VULN-003 (verificación SHA-256 en la descarga), con 13 pruebas nuevas y el contrato OpenAPI actualizado.
- **Pruebas** (entorno limpio, SQLite en memoria, 2026-11-11): `src/apps` **497 aprobadas / 13 fallidas** (las 13 son deuda de entorno: `pypdf` no está en `requirements-dev.txt`); `src/core` 76/76; e2e 4/4. Las dos últimas suites **no se ejecutan por defecto** (`testpaths = ["src/apps"]`).

## 2. Documentos revisados (Obsidian MCP, `90-ORIGINAL-SOURCES/DOCUMENTATION-PART-2/`)

| Código | Documento | Propósito | Uso en esta auditoría |
|---|---|---|---|
| D01 | `PLAN_MAESTRO_IMPLEMENTACION_SGT_SIAAF.md` | Estado por área, brechas, incrementos INC-01…09 | Punto de partida del plan |
| D02 | `MATRIZ_BRECHAS_BACKEND_FRONTEND.md` | 97 brechas SEC/MOD/KPI/DB/FE/SES/API/TEST | Matriz de requerimientos |
| D03 | `ARQUITECTURA_DASHBOARDS_POR_ROL.md` | Contenido de dashboards por rol y endpoint unificado | Plan de dashboards |
| D04 | `MATRIZ_INTEGRACION_KPIS_ENDPOINTS.md` | KPI → endpoint → servicio; SQL propuesto | Plan de KPI |
| D05 | `ESPECIFICACION_SERVICIOS_DASHBOARD.md` | Servicios, viewsets, serializers y RBAC de `indicadores` | Diseño de la app `indicadores` |
| D06 | `PLAN_IMPLEMENTACION_SESIONES_USUARIOS_ACTIVOS.md` | `SesionUsuario`, rotación, logout, KPI-ADM-09 | Etapa de sesiones |
| D07 | `MATRIZ_ACCIONES_RAPIDAS_POR_ROL.md` | Acciones por rol, vista y estado | Requisitos de API por acción |
| D08 | `PLAN_INTEGRACION_FRONTEND_BACKEND.md` | Incrementos, contratos de tipos, discrepancias | Plan de integración |
| D09 | `DISENO_FUNCIONAL_MODALIDADES_TITULACION.md` | Modelo, servicios y endpoints de modalidades | Etapa de modalidades (bloqueada) |
| D10 | `MATRIZ_REGLAS_NEGOCIO_MODALIDADES.md` | RN-MOD, transiciones, permisos, errores | Reglas y contradicciones |
| D11 | `MATRIZ_KPIS_MODALIDADES_TITULACION.md` | KPI-MOD-01…08 | KPI de modalidades |
| D12 | `ESPECIFICACION_API_MODALIDADES_TITULACION.md` | Contrato de 4 endpoints de modalidad | Contrato propuesto |

Fuente complementaria de fórmulas KPI (no forma parte de los 12): `docs/indicadores/INFORME_DISENO_KPI.md` §6–§7, citado por D03/D04/D05/D11.

> **Nota sobre fechas y autoría.** Los 12 documentos están fechados el 2026-11-09 y declaran estado "análisis y planificación". Varias de sus afirmaciones de estado ya no son exactas (sección 7).

## 3. Estado de la arquitectura

| Aspecto | Estado real | Evidencia |
|---|---|---|
| Estilo | Monolito modular, hexagonal (`adapters/`, `domain/`, `services/`, `ports/`) por app | `backend/src/apps/*` |
| Apps | `authentication`, `expedientes`, `peticiones`, `verificacion`, `resoluciones`, `notificaciones` | `config/settings/base.py` `INSTALLED_APPS` |
| URLs | Rutas explícitas en `config/urls.py` (no hay `urls.py` por app); versión `/api/v1/` | `config/urls.py` |
| Endpoints de negocio | **16 rutas / 17 operaciones** (no 23 como afirma D01 §15.H) | `openapi.yaml` |
| Autenticación | JWT HS256 (`JWT_SIGNING_KEY` separada), access 30 min, refresh 24 h **sin endpoint de refresh** | `SIMPLE_JWT`, `config/urls.py` |
| Autorización | `HasRolePermission` + `RBAC_MATRIX` (denegar por defecto) | `authentication/adapters/permissions.py` |
| Aislamiento | `ScopeFilterMixin` (own/carrera/facultad/**asignado**), 404 para lo ajeno | `core/adapters/scope_filter.py` |
| Errores | Excepciones DRF; varias reglas de dominio responden **500** (INC-21) | `expedientes/adapters/views.py:observar`, `peticiones/adapters/views.py:cargar_documento` |
| Transacciones | `transaction.atomic` + `select_for_update` en servicios críticos | `cargar_documento.py`, servicios de verificación |
| Paginación | Solo bandeja (`page`, `page_size` ≤ 50); notificaciones **sin paginar** | `BandejaPagination`, `NotificacionViewSet.pagination_class = None` |
| Filtros/búsqueda | **No existen** (ni `django-filter` ni parámetros manuales) | `expedientes/adapters/views.py` |
| OpenAPI | drf-spectacular; `openapi.yaml` es su salida (ahora con `SGTAutoSchema`) | `core/adapters/openapi.py` |
| CORS | Solo en `production.py` (`django-cors-headers`); desarrollo vía proxy Vite | `config/settings/production.py` |
| Caché | Sin `CACHES`: `LocMemCache` por proceso (afecta a los throttles) | `base.py` |

## 4. Estado de los módulos

| Módulo | Funcionalidad verificada | Brechas |
|---|---|---|
| `authentication` | Login con throttle 5/min por IP real; 8 roles; RBAC | Sin refresh/logout/sesiones (VULN-005); `RESPONSABLE_DEPENDENCIA` sin celdas (VULN-006); sin API de gestión de usuarios (solo `/admin/`) |
| `expedientes` | Crear (BORRADOR), enviar (ENVIADA + plazo), detalle con IDOR, bandeja por rol | **Sin `ENVIADA→EN_VERIFICACION`** ni `CANCELADA`; sin filtros; bandeja vacía para SECRETARIA_CARRERA y DIRECTOR_CARRERA por diseño; sin modalidad |
| `peticiones` | Solicitar emisión, carga PDF versionada (magic bytes, 10 MB, SHA-256), descarga privada | Descarga ahora con SCOPE_ASIGNADO + SHA-256 (INC-01); jurista no puede descargar documentos de otras dependencias (H-07) |
| `verificacion` | Listar checklist (juristas/admin), evaluar con bloqueo, subsanar, observar | ESTUDIANTE y SECRETARIA no pueden descubrir el `checklist_verification_id` para subsanar (H-04); `ObservacionViewSet` sin ruta (código muerto) |
| `resoluciones` | Informe (Providencia 590, PDF generado), declaratoria (Memorando 162) | FirmaEC no verificada (VULN-010); sin endpoints de lectura de informe/declaratoria |
| `notificaciones` | Notificaciones internas, marcar leída, `EventoAuditoria` JSONB por signals | Sin paginación; sin API de lectura de auditoría; sin acciones de auditoría para modalidad/integridad |
| `indicadores` | **No existe** | Toda la capa KPI/dashboard |

## 5. Funcionalidades

### 5.1 Implementadas y verificadas (con pruebas en verde)

Registro de expediente con catálogo base Art. 235; envío con validación de requisitos (422); plazos con pausa/reanudación; detalle con IDOR (404); bandeja paginada por rol; solicitud de emisión; carga PDF versionada; descarga privada autenticada; evaluación de checklist con concurrencia; observación con pausa de plazo; subsanación; emisión de informe con PDF; declaratoria; notificaciones internas; auditoría por signals; throttling de login y de carga; **throttling de mutaciones, `SCOPE_ASIGNADO` y verificación SHA-256 (INC-01, esta sesión)**.

### 5.2 Implementadas parcialmente

| Funcionalidad | Qué falta |
|---|---|
| Flujo de verificación FL-03 | Transición de entrada a `EN_VERIFICACION` (solo existe desde OBSERVADA vía subsanar) |
| Subsanación por el estudiante | Descubrimiento del checklist observado (403 en `GET .../checklist/`) |
| Sesiones JWT | Refresh y logout no expuestos |
| Bandeja operativa | Filtros, búsqueda, orden y cobertura para SECRETARIA_CARRERA/DIRECTOR_CARRERA |
| Notificaciones | Paginación (discrepancia INC-19 con `specify.md`) |
| Declaratoria | Verificación criptográfica FirmaEC |

### 5.3 No implementadas

App `indicadores` y `/dashboard/me/`; endpoints analíticos; modalidades (4 endpoints, modelo e historial); refresh/logout/`SesionUsuario`; búsqueda universal; exportaciones; endpoint de reportes CSP; API de auditoría; catálogo de carreras/facultades (BE-10); cancelación de expediente.

## 6. Problemas encontrados (hallazgos)

| ID | Prioridad | Hallazgo | Evidencia |
|---|---|---|---|
| H-01 | **P0** | No existe la transición `ENVIADA→EN_VERIFICACION`; evaluar/observar/informe exigen `EN_VERIFICACION` | `evaluar_checklist.py:162`, `registrar_observacion.py:106`; solo `subsanar_requisito.py:80` asigna `EN_VERIFICACION`; `tests/e2e/test_full_workflow.py` fuerza el estado |
| H-02 | **P0** (bloqueado) | Modalidades TIC/EC ausentes; el puerto SGA (`RecordAcademicoSGA`) no tiene reprobaciones ni matrícula | `core/ports/__init__.py`, `core/adapters/fixtures/sga_mock_records.json` |
| H-03 | P1 | Reglas de dominio responden HTTP 500 (`APIException`) en observar y en la carga | `expedientes/adapters/views.py` (`ExpedienteNoEnVerificacionError`, `PeticionNoEncontradaError`) |
| H-04 | P1 | ESTUDIANTE/SECRETARIA_CARRERA no pueden obtener el `checklist_verification_id` para subsanar | `RBAC_MATRIX["checklist"]["GET"]` |
| H-05 | P1 | Sin refresh/logout; `ROTATE_REFRESH_TOKENS=False` | `config/urls.py`, `SIMPLE_JWT` |
| H-06 | P1 | `RESPONSABLE_DEPENDENCIA` sin celdas RBAC y `ROW_TO_SCOPE=DENEGADO`; además `dependencia_emisora` usa los roles como dominio, así que no distingue *qué* dependencia | `permissions.py`, `peticiones/adapters/models.py` |
| H-07 | P1 | SECRETARIO_ABOGADO/ANALISTA solo descargan documentos asignados a su rol, pero deben verificar los 5 requisitos | `RBAC_MATRIX["peticiones:documento"]["GET"]` |
| H-08 | P1 | Bandeja sin filtros/búsqueda; vacía para SECRETARIA_CARRERA y DIRECTOR_CARRERA | `MAPA_INTERVENCION_POR_ROL` |
| H-09 | P2 | Notificaciones sin paginación | `NotificacionViewSet` |
| H-10 | P2 | Sin catálogo de carreras/facultades: KPI por carrera solo con UUID | `User.carrera_id`, `ExpedienteTitulacion.carrera_id` |
| H-11 | P2 | Sin transición/endpoint a `CANCELADA` | servicios de `expedientes` |
| H-12 | P2 | FirmaEC no verificada (VULN-010) | `declarar_aptitud.py` |
| H-13 | P2 | Sin API de auditoría (D07 la cita como `/api/v1/auditoria/`) | `config/urls.py` |
| H-14 | P3 | Deuda de pruebas: `pypdf` ausente de `requirements-dev.txt` (13 fallos); `src/core` y `tests/e2e` fuera de `testpaths` | `pyproject.toml`, ejecución 2026-11-11 |
| H-15 | P3 | `ObservacionViewSet` definido sin ruta | `verificacion/adapters/views.py`, `config/urls.py` |
| H-16 | P3 | Documentación Quarto desactualizada (decía "sin throttling") — corregida en esta sesión | `docs/04-api`, `docs/06-seguridad` |
| H-17 | **P0** | Ningún servicio crea las filas de `ChecklistVerification`; `_get_or_create_checklist_verification` no se usa | `evaluar_checklist.py:51`; e2e las crea a mano |
| H-18 | P1 | Subsanar marca la observación como resuelta al cargar y notifica al estudiante con un texto dirigido al verificador | `subsanar_requisito.py` |
| H-19 | P1 | Con varias observaciones, la primera subsanación devuelve el expediente a EN_VERIFICACION y las demás ya no pueden subsanarse | `subsanar_requisito.py:127` + `_reanudar_plazo_y_cambiar_estados` |
| H-20 | P1 | Dos caminos de observación con efectos distintos: `POST /observar/` pausa el plazo; `PUT /checklist/ OBSERVADO` no | `registrar_observacion.py:141`, `evaluar_checklist.py` |
| H-21 | P1 | La carga normal acepta peticiones OBSERVADO y esquiva la subsanación (observación, checklist y plazo) | `cargar_documento.py:91` |
| H-22 | P1 | ANALISTA_APOYO evalúa de forma definitiva y observa vía `PUT`: contradice la **especificación funcional aprobada** (`sgt-siaaf/specs/001-tramite-titulacion/specify.md` §6.2, checklist PUT/PATCH = "Borrador") además de D03 §2.3 y D07; `SCOPE_BORRADOR` no se aplica en ningún sitio; la celda `informes` contradice al servicio | `permissions.py`, `evaluar_checklist.py:149`, `emitir_informe.py:67`, specify 001 §6.2 |
| H-23 | P2 | `HistorialEstado` solo se registra en informe y declaratoria | `emitir_informe.py:206`, `declarar_aptitud.py:208` |
| H-24 | P1 | Auditoría de transiciones con actor incorrecto y riesgo de duplicidad: la señal `post_save` del expediente registra `ESTADO_CAMBIADO` con `usuario=instance.estudiante` en todo cambio de estado (aunque lo ejecute el jurista o el decano), y la señal de `HistorialEstado` registra otro `ESTADO_CAMBIADO` para la misma transición | `notificaciones/adapters/signals.py` (receptores del expediente y de `historial_estado_post_save`); e2e 2026-11-11: 8 `ESTADO_CAMBIADO` para 6 transiciones |
| H-26 | P2 | `declarar_aptitud.py` admite en el servicio a DECANO **y ANALISTA_APOYO**; el RBAC HTTP (`declaratorias` POST) solo concede al DECANO, así que hoy no es explotable por API, pero contradice la competencia del Decano. No se modifica sin DP-05b | `resoluciones/services/declarar_aptitud.py` (guarda de roles) |
| H-27 | P2 | `solicitar_emision` notifica, si la facultad del expediente no tiene emisor, a un usuario con ese rol de **cualquier facultad** (fallback sin ámbito). Registrado en la auditoría de E2-01 (2026-11-11); **fuera de PLB-E1-04** (D-7) | `peticiones/services/solicitar_emision.py:111-114` |
| H-28 | P2 · **Corregido 2026-11-11** (PLB-E1-04, T4, `3cdb47d`: reserva exclusiva `O_EXCL` y borrado solo del archivo propio; probado con centinelas SHA-256) | El generador de la Providencia 590 escribe con nombre fijo y **sobrescribe** un archivo existente; si la transacción falla después, el PDF queda huérfano (reproducido en la auditoría de E2-01 con O-1) | `resoluciones/adapters/pdf_generator.py:442-446`, `resoluciones/services/emitir_informe.py`; plan: [PLAN_E1-04_O-2.md](PLAN_E1-04_O-2.md) §5 |
| H-29 | P1 · **Confirmado y corregido 2026-11-11**: reproducido en PostgreSQL 16.15 (`deadlock detected`, 40P01, HTTP 500) antes de T2; corregido con el orden expediente → petición → checklist (T2 `4d02baf`, T3 `daa8b41`); C1–C8 sin interbloqueos (T5 `7e87483`) | Orden de bloqueo inverso: `registrar_observacion` (expediente → petición → checklist) frente a `evaluar_checklist`/`subsanar_requisito` (checklist → petición → expediente); posible interbloqueo en PostgreSQL. Además, lectura obsoleta del expediente en esos dos servicios (500 reproducido con SQLite por simulación). Hipótesis original pendiente de PostgreSQL real; resuelta según la columna de severidad | `verificacion/services/*.py`; plan: [PLAN_E1-04_O-2.md](PLAN_E1-04_O-2.md) §4 |
| H-30 | P3 | En PostgreSQL fallan 8 pruebas de introspección de índices y restricciones (`notificaciones/tests/test_auditoria.py`, `test_notifications_and_audit.py`, `test_notification_service.py`, `resoluciones/tests/test_models.py`) escritas para SQLite; mismo resultado en `develop` y en `fix/e1-04-errores-dominio` (auditoría postimplementación 2026-11-11). No afecta a la suite por defecto (SQLite) | Pruebas citadas |
| H-25 | P1 | **Corregido 2026-11-11 (PLB-E2-06; = AUD-P2-01).** `emitir_informe.py` creaba `HistorialEstado` **después** de guardar el expediente y toma `estado_anterior=expediente.estado`: registra `INFORME_EMITIDO→INFORME_EMITIDO` | `resoluciones/services/emitir_informe.py:198-211`; e2e 2026-11-11 |

### 6.1 Trazabilidad de H-17…H-25

| Hallazgo | Requerimiento | Tarea | Estado | Pruebas previstas |
|---|---|---|---|---|
| H-17 Checklist no generado | RQ-FL-21 (y RQ-FL-03) | PLB-E2-01 | **Corregido 2026-11-11** (E2-01) | `expedientes/tests/test_iniciar_verificacion.py` (filas, idempotencia, rollback); e2e sin creación manual |
| H-18 Resolución automática + notificación equivocada | RQ-FL-06 / RQ-FL-23 | PLB-E2-02b3.1 / PLB-E2-02b2 | Definidas, no autorizadas | `verificacion/tests/test_subsanar_requisito.py` (no resuelve; destinatarios) |
| H-19 Subsanación múltiple bloqueada | RQ-FL-24 | PLB-E2-02b3.2 | **Bloqueada (DP-20)** | Dos o tres ítems observados, todos subsanables |
| H-20 Dos caminos de observación | RQ-FL-17 | PLB-E2-02c | **Bloqueada (DP-19)** | Paridad de efectos entre `POST /observar/` y `PUT /checklist/` |
| H-21 Carga normal sobre OBSERVADO | RQ-FL-18 | PLB-E2-02b1 | Definida, no autorizada (coordinar, R-07) | `peticiones/tests/test_cargar_documento.py` (rechazo sin efectos) |
| H-22 Analista con evaluación definitiva (desviación de la especificación aprobada §6.2) | RQ-FL-19 | PLB-E2-05 | **Bloqueada (DP-05b)** | Según la opción aprobada |
| H-23 Historial incompleto | RQ-FL-22 | PLB-E2-06 | **Corregido 2026-11-11** | Una transición = un `HistorialEstado` |
| H-24 Auditoría con actor erróneo y duplicada | RQ-FL-22 | PLB-E2-06 | **Corregido 2026-11-11** (eventos anteriores intactos) | `notificaciones/tests/test_auditoria.py`: un evento por transición, actor correcto; prueba de arquitectura |
| H-25 Estado anterior erróneo en el historial del informe | RQ-FL-25 | PLB-E2-06 | **Corregido 2026-11-11** | Prueba unitaria del informe (`EN_VERIFICACION→INFORME_EMITIDO`); e2e de estados anteriores |

## 7. Contradicciones y vacíos en la documentación

| ID | Contradicción / vacío | Documentos | Qué debe confirmarse |
|---|---|---|---|
| C-01 | Quién ejecuta `POST /modalidad/cambiar/`: D09 §7 y D12 §6 conceden POST al Secretario; D12 §3.3 dice que el Secretario recibe 403; D10 §1.3 exige "autorización dual" sin definir cómo registra un solo endpoint a dos actores | D09, D10, D12 | Flujo de autorización (¿dos pasos con estado intermedio?) |
| C-02 | ANALISTA_APOYO y elegibilidad EC: D10 §3 la deniega; su nota y D12 §6 la permiten | D10, D12 | Permiso del analista |
| C-03 | Estudiante y elegibilidad EC: D12 §3.2 → 403; D03 §2.1 y D07 §3.1 le muestran "Verificar elegibilidad" | D03, D07, D12 | Visibilidad para el estudiante |
| C-04 | Catálogo `GET /modalidades/`: D01 §4.4 solo Admin; D12 todos los autenticados | D01, D12 | Permiso del catálogo |
| C-05 | D09 §8.1 pide la elegibilidad por `expediente_id` en V-03, cuando el expediente aún no existe | D09 | Momento de la verificación |
| C-06 | RN-MOD-CAM-05 permite el cambio en `EN_VERIFICACION`, estado inalcanzable hoy (H-01) | D10 | Depende de H-01 |
| C-07 | RN-MOD-CAM-06 exige `on_delete=PROTECT`; el modelo de D09 usa `CASCADE` | D09, D10 | Política de borrado |
| C-08 | KPI-MOD-05 y KPI-DIR-07 llaman "período académico" a `year(fecha_recepcion)` | D11, INFORME_KPI | Catálogo de períodos |
| C-09 | Base del porcentaje en KPI-MOD-03: "total activos" frente a TIC+EC | D11 | Denominador |
| C-10 | KPI-EST-07 usa un denominador fijo de 5 requisitos; el catálogo es configurable (`es_obligatorio_base`, `activo`) | D04, D05 | Denominador real |
| C-11 | KPI-SEC-04 y el servicio de D05 usan `ChecklistVerification.peticion`, una FK **inexistente**; el cruce real es por `(expediente, requisito)` | D04, D05, INFORME_KPI | Corrección de la fórmula |
| C-12 | D06 añade un claim `jti` propio (simplejwt ya lo emite), exige Redis/Celery (ausentes del stack) y usa `auto_now` en un campo que pretende actualizar por lotes | D06 | Diseño de sesiones |
| C-13 | D08 §1.2 y D01 §8.1 dan por existente `POST /auth/token/refresh/`; no está enrutado | D01, D08 | — (hecho verificado) |
| C-14 | D01/D02 afirman "497 pruebas pasando"; en un entorno limpio fallan 13 | D01, D02 | — (hecho verificado) |
| C-15 | D07 concede "Cargar documento" a SECRETARIO_ABOGADO, ANALISTA, DIRECTOR y RESPONSABLE (asignado), pero el servicio solo permite al estudiante dueño y a la Secretaría | D07 | Quién carga qué documento |
| C-16 | D03 §2.2 da a SECRETARIA_CARRERA una "tabla de trabajo de la bandeja", pero su bandeja está vacía por diseño | D03 | Lista de trabajo de la Secretaría |
| C-17 | D03 §5 deriva el ámbito de "JWT → carrera_id/facultad_id"; el JWT solo lleva `cedula` y `roles` (el ámbito sale del usuario en la BD) | D03 | — (hecho verificado) |
| C-18 | `_get_rol_principal` (D05) elige un único rol, mientras `ScopeFilterMixin` une los ámbitos de todos los roles: en usuarios multirol, el dashboard y la API pueden discrepar | D05 | Regla multirrol |

## 8. Riesgos

| ID | Riesgo | Impacto | Mitigación |
|---|---|---|---|
| R-01 | Integrar el frontend de funcionarios sin resolver H-01/H-17 | Vistas V-07/V-08 sin flujo real | Autorizar e implementar PLB-E2-01 antes de INC-07 |
| R-02 | Implementar modalidades sin validación normativa | Reglas académicas inválidas | Bloqueo explícito (D09 §11) |
| R-03 | KPI con fórmulas ambiguas (C-08…C-11) | Indicadores incorrectos | Implementar solo los KPI no ambiguos; los demás quedan en "validar" |
| R-04 | Cambios de RBAC (H-04, H-07) sin aprobación | Exposición de datos entre roles | H-04 → endpoint propio de solo lectura (E2-02a) sin abrir el checklist; H-07 → AUT-01 obligatoria antes de E2-03; pruebas IDOR entre facultades |
| R-07 | Desplegar PLB-E2-02b1 antes de resolver DP-20 | El segundo y siguientes ítems observados quedan sin ninguna vía de entrega | Desplegar E2-02b1 junto con o después de E2-02b3.2 |
| R-08 | Añadir transiciones (E2-01, E2-02b3) antes de implementar `registrar_transicion()` | Más eventos de auditoría con actor incorrecto | **Mitigado 2026-11-11**: E2-06 hecha; la prueba de arquitectura impide cambios de estado fuera de la función |
| R-05 | Throttles con `LocMemCache`: el límite efectivo es por worker | Límite multiplicado por N workers | Configurar `CACHES` compartido (Redis o base de datos) en producción, DT-04 |
| R-06 | `testpaths` excluye 80 pruebas | Regresiones no detectadas | PLB-E0-02 |

## 9. Conclusiones

1. El backend es una base correcta y defendible; **no requiere reescritura**: los incrementos encajan en la arquitectura existente (nuevas apps/servicios + celdas RBAC + rutas en `config/urls.py`).
2. El **bloqueo funcional más grave** era el inicio de la verificación (H-01) junto con la generación del checklist (H-17). El criterio del responsable lo define técnicamente (PLB-E2-01); falta la **autorización de implementación**. Siguen pendientes DP-19, DP-20, DP-21, DP-01b, DP-05b, AUT-01, AUT-02 y AUT-03; DP-22 está definida técnicamente (DT-12), sin autorización de implementación.
3. La capa de **indicadores** es implementable hoy para la mayoría de los KPI de `INFORME_DISENO_KPI.md` (los que no dependen de modalidad, sesiones, períodos ni catálogos), siempre que se corrijan C-10 y C-11.
4. **Modalidades** y **RESPONSABLE_DEPENDENCIA** deben seguir bloqueadas hasta contar con validación institucional.
5. INC-01 queda cerrado con evidencia; la siguiente etapa recomendada está en `PLAN_MAESTRO_IMPLEMENTACION_BACKEND.md` §6.
