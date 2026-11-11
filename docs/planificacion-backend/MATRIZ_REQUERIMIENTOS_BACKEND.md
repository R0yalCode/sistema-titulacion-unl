---
title: "Matriz de requerimientos backend"
subtitle: "Trazabilidad documento → código → acción (2026-11-11)"
date: 2026-11-11
---

# Matriz de requerimientos backend

**Estados:** `IV` implementado y verificado · `IP` implementado parcialmente · `NI` no implementado · `IM` implementado, pero requiere mejora · `PV` pendiente de validación · `BL` bloqueado por dependencias o información faltante.

**Documentos:** D01 Plan maestro · D02 Matriz de brechas · D03 Arquitectura de dashboards · D04 Matriz de integración KPI · D05 Especificación de servicios de dashboard · D06 Plan de sesiones · D07 Matriz de acciones rápidas · D08 Plan de integración · D09 Diseño funcional de modalidades · D10 Reglas de negocio de modalidades · D11 KPI de modalidades · D12 API de modalidades · IK = `docs/indicadores/INFORME_DISENO_KPI.md`.

Las rutas de evidencia son relativas a `backend/src/` salvo indicación contraria. Las tareas `PLB-*` están en `PLAN_MAESTRO_IMPLEMENTACION_BACKEND.md`.

## 1. Seguridad

| ID | Documento | Requerimiento | Módulo | Estado real | Evidencia en código | Acción requerida | Prioridad |
|---|---|---|---|---|---|---|---|
| RQ-SEC-01 | D01 §3.2, D02 SEC-01 | Throttling de endpoints mutantes (VULN-001) | core / todas | **IV** (2026-11-11) | `core/adapters/throttling.py`; vistas con `throttle_classes`; `test_inc01_seguridad.py` (4 pruebas) | Aprobar la tasa por defecto (DT-03) | P0 → cerrado |
| RQ-SEC-02 | D01 §3.2, D02 SEC-02 | `SCOPE_ASIGNADO` en `ScopeFilterMixin` (VULN-002) | core / peticiones | **IV** (2026-11-11) | `core/adapters/scope_filter.py` (`_predicado_asignado`); `peticiones/adapters/views.py` (`get_scope_grants`); `cargar_documento.py` (dependencia); 6 pruebas | Decidir H-07 (alcance de lectura del jurista) | P0 → cerrado |
| RQ-SEC-03 | D02 SEC-03 | Verificar SHA-256 al descargar (VULN-003) | peticiones | **IV** (2026-11-11) | `core/adapters/local_storage.py:calcular_sha256`; `DocumentoIntegridadAPI`; 2 pruebas | Registrar el fallo en `EventoAuditoria` (PLB-E1-05) | P1 → cerrado |
| RQ-SEC-04 | D02 SEC-04, D06 | Rotación de refresh, blacklist y logout (VULN-005) | authentication | **NI** | `SIMPLE_JWT["ROTATE_REFRESH_TOKENS"]=False`; sin rutas | PLB-E3-01/02 | P1 |
| RQ-SEC-05 | D02 SEC-05 | FirmaEC real en la declaratoria (VULN-010) | resoluciones | **BL** | `services/declarar_aptitud.py` valida solo el PDF | Decisión PKI/proveedor (DP-09) | P1 |
| RQ-SEC-06 | D02 SEC-06 | Permisos de `RESPONSABLE_DEPENDENCIA` (VULN-006) | authentication | **BL** | Sin celdas en `RBAC_MATRIX`; `ROW_TO_SCOPE=DENEGADO` | Definir dependencias institucionales (DP-07) | P1 |
| RQ-SEC-07 | D02 SEC-07 | Endpoint de reportes CSP (VULN-004) | core | **NI** | `production.py` define `CSP_REPORT_ONLY_POLICY` sin `report-uri` | PLB-E6-03 | P2 |
| RQ-SEC-08 | D02 SEC-08 | Migración a RS256 (VULN-011) | authentication | **NI** | `ALGORITHM="HS256"` | Futuro (requiere gestión de claves) | P3 |
| RQ-SEC-09 | D02 SEC-10 | Pruebas negativas de mass assignment/BOLA (VULN-013) | todas | **IP** | IDOR: `test_idor_isolation_expediente.py`; sin pruebas de mass assignment | PLB-E0-03 | P3 |
| RQ-SEC-10 | D02 SEC-11 | Historial de modelos maestros (VULN-014) | authentication / peticiones | **NI** | Signals solo en modelos de negocio | Futuro | P3 |
| RQ-SEC-11 | D01 §15.B | `JWT_SIGNING_KEY` ≠ `SECRET_KEY` (SEC-T004) | config | **IV** | `config/settings/base.py`; `test_security_controls.py` | — | — |
| RQ-SEC-12 | — (CLAUDE.md, SEC-T002) | Throttle de login por IP real | authentication | **IV** | `TokenPairView`, `TrustedProxyScopedRateThrottle` | — | — |

## 2. Flujo del trámite (Fase 1)

| ID | Documento | Requerimiento | Módulo | Estado real | Evidencia en código | Acción requerida | Prioridad |
|---|---|---|---|---|---|---|---|
| RQ-FL-01 | D08 §2.2, D07 §2 | Crear expediente en BORRADOR | expedientes | **IV** | `services/crear_expediente.py`; `test_crear_expediente.py` | — | — |
| RQ-FL-02 | D07 §2 | Enviar expediente (BORRADOR→ENVIADA, plazo de 8 días hábiles) | expedientes | **IV** | `services/enviar_expediente.py:103`; `test_enviar_expediente.py` | — | — |
| RQ-FL-03 | D07 §3.5; criterio DP-01 (2026-11-11, fuente secundaria) | Entrada a verificación por acción explícita del SECRETARIO_ABOGADO (H-01) | expedientes / verificacion | **I** (2026-11-11, E2-01) | `expedientes/services/iniciar_verificacion.py` + `POST /expedientes/{id}/iniciar-verificacion/`; la e2e ya no fuerza el estado | PLB-E2-01 (requiere AUT-02 y E2-06) · pruebas `test_iniciar_verificacion.py` + e2e (analista: DP-01b) | **P0** |
| RQ-FL-04 | D07 §3.5 | Evaluar checklist (VERIFICADO/OBSERVADO) | verificacion | **IV** (condicionado a RQ-FL-03) | `services/evaluar_checklist.py`; `test_evaluar_checklist.py` | — | — |
| RQ-FL-05 | D07 §3.5 | Observar expediente | verificacion | **IM** | `expedientes/adapters/views.py:observar` mapea reglas de dominio a 500 | PLB-E1-04 | P1 |
| RQ-FL-06 | D07 §3.1–3.3; criterio DP-04 | Subsanar presentando una nueva versión que queda en revisión hasta que el jurista verifique (H-18, resolución automática) | verificacion | **IM** | `subsanar_requisito.py` marca `resuelta=True` al cargar | PLB-E2-02b3.1 · migración aditiva + pruebas de ciclo observar/subsanar/verificar | P1 |
| RQ-FL-16 | Criterio DP-04 | El estudiante consulta los requisitos observados, el motivo, la fecha y el estado de subsanación (H-04) | verificacion | **NI** (definida, no autorizada) | Detalle sin motivo/fecha/id; `GET /checklist/` 403 | PLB-E2-02a · pruebas de serializer + IDOR (Secretaría: DP-21) | P1 |
| RQ-FL-17 | Criterio DP-04; `ARTICLES_AND_PROVISIONS` pendiente #2 | Un único comportamiento para observar un requisito, incluido su efecto sobre el plazo (H-20) | verificacion / expedientes | **IM** / **BL** | `POST /observar/` pausa (`registrar_observacion.py:141`); `PUT /checklist/ OBSERVADO` no pausa | PLB-E2-02c (BL: DP-19) · pruebas de paridad entre rutas | P1 |
| RQ-FL-18 | Criterio DP-04 (sin camino paralelo) | La carga normal no debe aceptar peticiones OBSERVADO (H-21) | peticiones | **IM** | `cargar_documento.py:91` las admite | PLB-E2-02b1 (coordinar con E2-02b3.2, R-07) · pruebas de servicio + endpoint | P1 |
| RQ-FL-19 | **Especificación aprobada** `specs/001` §6.2 (checklist PUT/PATCH: ANALISTA_APOYO = "Borrador"); criterio DP-05; D03 §2.3; Providencia 590 (citada) | Competencias del ANALISTA_APOYO acotadas (H-22) | verificacion / resoluciones | **IM** (desviación de la especificación aprobada) / **PV** (alcance definitivo) | Evalúa de forma definitiva y observa vía `PUT`; `SCOPE_BORRADOR` sin efecto; la celda `informes` contradice al servicio; además `declarar_aptitud` admite ANALISTA_APOYO en el servicio, aunque el RBAC HTTP solo permite al DECANO (H-26) | PLB-E2-05 (BL: DP-05b) | P1 |
| RQ-FL-20 | Criterio DP-01 (precondición de envío) | ¿Envío con los 5 requisitos o envío incompleto gestionado por observación? | expedientes | **PV** | `enviar_expediente` exige los 5 (422) | DP-18 | P2 |
| RQ-FL-21 | Criterio DP-01; D07 §3.5 (evaluar requiere ítems) | Generación automática y atómica del checklist (un ítem PENDIENTE por requisito base activo) al iniciar la verificación (H-17) | verificacion / expedientes | **I** (2026-11-11, E2-01) | `iniciar_verificacion` crea las 5 filas PENDIENTE de forma idempotente con `_get_or_create_checklist_verification`; la e2e ya no las crea a mano | PLB-E2-01 · pruebas de filas creadas, idempotencia y rollback | **P0** |
| RQ-FL-22 | Trazabilidad (D01 §2.1 "auditoría inmutable"); DT-12 | Un único evento por transición con el actor autenticado, mediante `registrar_transicion()` (H-23, H-24) | expedientes / notificaciones | **IV** (2026-11-11) | `expedientes/services/transiciones.py`; señales sin auditoría de transiciones; e2e: 5 transiciones = 5 eventos con el actor real | PLB-E2-06 hecha · `test_transiciones.py` (10) + e2e | P1 → cerrado |
| RQ-FL-23 | Criterio DP-04 | La notificación de subsanación llega al jurista de la facultad y el estudiante recibe una confirmación coherente (H-18, notificación) | verificacion / notificaciones | **IM** | `subsanar_requisito.py` envía al estudiante un texto dirigido al verificador | PLB-E2-02b2 · pruebas de destinatarios | P1 |
| RQ-FL-24 | Criterio DP-04 | Con varias observaciones, todas pueden subsanarse (H-19) | verificacion | **IM** / **BL** | La primera subsanación pasa el expediente a EN_VERIFICACION y bloquea el resto | PLB-E2-02b3.2 (BL: DP-20) | P1 |
| RQ-FL-25 | DT-12; AUD-P2-01 (Bug N-1 de `docs/03-modulos/modulo-resoluciones.md`) | El historial registra el estado anterior real de cada transición (H-25) | resoluciones / expedientes | **IV** (2026-11-11) | `emitir_informe.py` usa `registrar_transicion()`; `test_emitir_informe_historial_estado_anterior_real_h25` | PLB-E2-06 hecha | P1 → cerrado |
| RQ-FL-07 | D07 §3.5 | Emitir informe (Providencia 590) | resoluciones | **IV** (condicionado a RQ-FL-03) | `services/emitir_informe.py`; `test_emitir_informe.py` | — | — |
| RQ-FL-08 | D07 §3.6 | Declarar aptitud (Memorando 162) | resoluciones | **IP** | `services/declarar_aptitud.py` sin FirmaEC | RQ-SEC-05 | P1 |
| RQ-FL-09 | D10 §2 (estado CANCELADA) | Cancelar expediente | expedientes | **NI** | Estado definido en el modelo; sin servicio ni ruta | DP-08 → PLB-E2-04 | P2 |
| RQ-FL-10 | D07 §3.3 | Solicitar emisión (PENDIENTE→SOLICITADO) | peticiones | **IV** | `services/solicitar_emision.py`; `test_solicitar_emision.py` | — | — |
| RQ-FL-11 | D07 §3.3/§3.7 | Cargar documento (versionado N+1) | peticiones | **IV** | `services/cargar_documento.py`; `test_cargar_documento.py` | Resolver C-15 (quién carga) | P2 |
| RQ-FL-12 | D07 §3.3; criterio DP-05 | Descargar documento vigente o por versión; el jurista, los 5 requisitos de su facultad (H-07) | peticiones | **IP** | `descargar_documento` (SHA-256 + ámbito); el jurista solo ve lo asignado a su rol | PLB-E2-03 (una celda de la matriz: requiere AUT-01) · pruebas IDOR entre facultades | P1 |
| RQ-FL-13 | D08 §6 | Plazos con pausa y reanudación | expedientes | **IV** | `domain/plazo_calculator.py`; `test_plazo_calculator.py` | — | — |
| RQ-FL-14 | D01 §2.1 | Notificaciones internas por evento | notificaciones | **IV** | `adapters/signals.py`, `services/notification_service.py` | — | — |
| RQ-FL-15 | D02 FE-07 | Notificaciones en tiempo real | notificaciones | **NI** (polling vigente) | — | Opcional; no prioritario | P3 |

## 3. API para el frontend

| ID | Documento | Requerimiento | Módulo | Estado real | Evidencia en código | Acción requerida | Prioridad |
|---|---|---|---|---|---|---|---|
| RQ-API-01 | D08 §3 INC-07 | Bandeja paginada por rol | expedientes | **IP** | `BandejaExpedienteViewSet`; sin filtros; vacía para SECRETARIA/DIRECTOR | PLB-E4-05 | P1 |
| RQ-API-02 | D02 FE-09 | Filtros (estado, fechas, carrera, modalidad) | expedientes | **NI** | — | PLB-E4-05 (sin modalidad hasta E5) | P1 |
| RQ-API-03 | D01 §7.2, D02 FE-05 | Búsqueda universal `GET /buscar/` | core | **NI** | — | PLB-E6-01 | P2 |
| RQ-API-04 | D01 §7.2, D02 FE-06 | Exportación PDF/Excel/CSV | core | **NI** | — | PLB-E6-02 (CSV/PDF con `reportlab`); Excel → DP-17 | P2 |
| RQ-API-05 | D08 §6 (INC-19) | Paginación de notificaciones | notificaciones | **IM** | `pagination_class = None` | PLB-E4-06 (compatible) | P2 |
| RQ-API-06 | D08 §6 (INC-21) | Errores de dominio como 4xx | expedientes / peticiones | **IM** | `APIException` (500) en observar y carga | PLB-E1-04 | P1 |
| RQ-API-07 | D07 §2 | API de auditoría (Admin) | notificaciones | **NI** | — | PLB-E7-04 | P2 |
| RQ-API-08 | D07 §2 | Gestión de usuarios/roles por API | authentication | **NI** (solo `/admin/`) | `config/urls.py` | Fuera de alcance mientras baste `/admin/` (DT-09) | P3 |
| RQ-API-09 | D02 API-07 | OpenAPI sincronizado con el código | config | **IV** | `openapi.yaml` regenerado 2026-11-11; `test_openapi_declara_429_y_500_de_integridad` | Regenerar en cada cambio de contrato | — |
| RQ-API-10 | D01 §8.2 | Lectura de informe/declaratoria emitidos | resoluciones | **NI** | Solo `POST` | PLB-E4-07 | P2 |

## 4. Sesiones (D06)

| ID | Documento | Requerimiento | Módulo | Estado real | Evidencia en código | Acción requerida | Prioridad |
|---|---|---|---|---|---|---|---|
| RQ-SES-01 | D06 §3.6 | `POST /auth/token/refresh/` con rotación | authentication | **NI** | Sin ruta | PLB-E3-01 | P1 |
| RQ-SES-02 | D06 §3.5 | `POST /auth/logout/` con blacklist | authentication | **NI** | Sin ruta | PLB-E3-02 | P1 |
| RQ-SES-03 | D06 §3.1 | Registro `SesionUsuario` | authentication | **NI** | — | PLB-E3-03 (variante sin Redis, DT-05) | P2 |
| RQ-SES-04 | D06 §4 | Métricas de usuarios activos (KPI-ADM-09) | indicadores | **BL** | Depende de RQ-SES-03 | PLB-E3-03 | P2 |

## 5. Modalidades de titulación (D09–D12)

| ID | Documento | Requerimiento | Módulo | Estado real | Evidencia en código | Acción requerida | Prioridad |
|---|---|---|---|---|---|---|---|
| RQ-MOD-01 | D09 §4.1, D10 RN-MOD-CRE-01 | Campo `opcion_titulacion` (TIC por defecto) | expedientes | **BL** | Ausente en `ExpedienteTitulacion` | Validación normativa (DP-02) | P0 (bloqueado) |
| RQ-MOD-02 | D10 RN-MOD-CRE-02 | Rechazar EC en la creación | expedientes | **BL** | — | DP-02 | P0 (bloqueado) |
| RQ-MOD-03 | D10 §1.2 | Elegibilidad EC (2 reprobaciones + 3.ª matrícula) | core (SGA) | **BL** | `RecordAcademicoSGA` sin esos datos | DP-02 + DP-03 (fuente de datos) | P0 (bloqueado) |
| RQ-MOD-04 | D10 §1.3 | Cambio TIC→EC autorizado, único e irreversible | expedientes | **BL** | — | DP-02 + C-01 | P0 (bloqueado) |
| RQ-MOD-05 | D09 §4.2 | `HistorialModalidad` inmutable con evidencia | expedientes | **BL** | — | DP-02 + C-07 | P0 (bloqueado) |
| RQ-MOD-06 | D10 §5 | Eventos de auditoría de modalidad | notificaciones | **BL** | `EventoAuditoria.Accion` sin esas acciones | Con RQ-MOD-04 | P1 |
| RQ-MOD-07 | D12 §3.4 | `GET /modalidades/` | expedientes | **BL** | — | C-04 | P1 |
| RQ-MOD-08 | D11 | KPI-MOD-01…08 | indicadores | **BL** | — | Tras E5 | P1 |

## 6. Indicadores y dashboards (D03, D04, D05, IK)

| ID | Documento | Requerimiento | Módulo | Estado real | Evidencia en código | Acción requerida | Prioridad |
|---|---|---|---|---|---|---|---|
| RQ-KPI-01 | D04 §1, D05 §1 | App `indicadores` con fórmulas centralizadas | indicadores | **NI** | No existe | PLB-E4-01 | P1 |
| RQ-KPI-02 | D03 §1.1, D05 §4 | `GET /dashboard/me/` compuesto por rol | indicadores | **NI** | — | PLB-E4-02 | P1 |
| RQ-KPI-03 | D04 §2.2 | `GET /indicadores/culminacion/` | indicadores | **NI** | — | PLB-E4-03 (cohorte: DP-10) | P2 |
| RQ-KPI-04 | D04 §2.2 | `GET /indicadores/evolucion/` (serie con ceros) | indicadores | **NI** | — | PLB-E4-03 | P2 |
| RQ-KPI-05 | D05 §6 | Celdas RBAC `dashboard` e `indicadores:*` | authentication | **NI** | — | PLB-E4-04 | P1 |
| RQ-KPI-06 | IK §6.1–6.7 | KPI EST/SEC/JUR/DEC/DIR/ADM implementables | indicadores | **NI** | Fuentes de datos presentes (modelos verificados) | PLB-E4-02 (corrigiendo C-10/C-11) | P1 |
| RQ-KPI-07 | IK §6.6 | KPI-DEP-01…03 | indicadores | **BL** | Depende de RQ-SEC-06 | DP-07 | P2 |
| RQ-KPI-08 | IK §6.8 | Tutoría, sustentación, período académico, abandonados | — | **BL** | Sin modelos | Decisión institucional | P3 |
| RQ-KPI-09 | IK §6.7 KPI-ADM-07 | Nombres de carrera en KPI | — | **BL** | Solo UUID | BE-10 (DP-11) | P2 |

## 7. Calidad y pruebas

| ID | Documento | Requerimiento | Módulo | Estado real | Evidencia en código | Acción requerida | Prioridad |
|---|---|---|---|---|---|---|---|
| RQ-TST-01 | D02 TEST-01 | Suite backend en verde | todas | **IM** | 497/510 en `src/apps` (13 por `pypdf`) | PLB-E0-01 (requiere autorizar la dependencia) | P2 |
| RQ-TST-02 | — | Ejecutar `src/core` y e2e por defecto | config | **IM** | 76 + 4 pruebas fuera de `testpaths` | PLB-E0-02 | P2 |
| RQ-TST-03 | D02 TEST-05/06 | E2E y pruebas de carga (Locust) | — | **NI** (E2E backend mínimo existe) | `tests/e2e/test_full_workflow.py` | INC-09 | P2 |
| RQ-TST-04 | D04 §8.5 | Cobertura de `indicadores` ≥ 90 % | indicadores | **NI** | — | Con E4 | P1 |
