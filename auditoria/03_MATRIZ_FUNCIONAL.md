# 03 — MATRIZ FUNCIONAL

Estados: **Implementado** / **Parcialmente implementado** / **Simulado** / **No implementado** / **No verificable**.
Evidencia por archivo:línea. Los RF provienen de `sgt-siaaf/specs/001-tramite-titulacion/specify.md §10`.

## A. Requisitos Funcionales (RF)

| ID | Funcionalidad | Evidencia en código | Estado | Observaciones |
|---|---|---|---|---|
| RF-001 | Registro/inicialización de solicitud (expediente BORRADOR + 5 peticiones base Art. 235) | `expedientes/services/crear_expediente.py:48-94` (correlativo EXP-YYYY-NNNN:32-45, bulk_create 5 peticiones :80-94); endpoint `POST /api/v1/expedientes/` (`config/urls.py:29-32`) | **Implementado** | Regla 1-expediente-activo vía `select_for_update` |
| RF-002 | Recepción inmutable + timestamp + providencia + estado ENVIADA | `expedientes/services/enviar_expediente.py:83-114` (fecha_recepcion UTC :102-105, `PROV-YYYY-NNNN` :106-112) | **Implementado** | Providencia autogenerada (DEC-03) con posible sobreescritura manual vía serializer |
| RF-003 | Cómputo de plazo 8 días laborables | `expedientes/domain/plazo_calculator.py` (cálculo 95% cov., pausar :61-65, reanudar :67-113); llamado en `enviar_expediente.py:112` y `registrar_observacion.py:141`/`subsanar_requisito.py` | **Implementado** | Pausa/reanudación activa (DEC-01 AP-01). Feriados configurables como parámetro |
| RF-004 | Petición interna de certificados (sin correo) | `peticiones/services/solicitar_emision.py:38-121`; endpoint POST `/peticiones/{id}/solicitar-emision/` | **Implementado** | Notifica al RESPONSABLE_DEPENDENCIA buscado por rol+carrera/facultad |
| RF-005 | Carga y validación PDF (≤10 MB, magic bytes `%PDF-`) | `core/adapters/pdf_validation.py` (100% cov.); `peticiones/services/cargar_documento.py:56-154`; endpoint `/peticiones/{id}/documento/` GET+POST | **Implementado** | SHA-256 streaming; versionado N+1 con `es_vigente` (RN-011) |
| RF-006 | Checklist digital de verificación | `verificacion/models.py` (ChecklistVerification); `verificacion/services/evaluar_checklist.py:103-220` | **Parcialmente implementado** | Evaluación PUT funciona; **el GET de checklist (`GET /expedientes/{id}/checklist/`) no tiene celda GET en RBAC_MATRIX** (`authentication/adapters/permissions.py:77-93`) ⇒ **403 siempre → endpoint inoperable** |
| RF-007 | Observaciones accionables + bloqueo de informe | `verificacion/services/registrar_observacion.py:69-185` (`ObservacionAccionable`, pausa de reloj :141); bloqueo vía `validar_checklist_completo.py:46-79` | **Implementado** | Duplicación del helper `_create_observacion_and_notify` con `evaluar_checklist.py:75-100` |
| RF-008 | Subsanación y reemplazo versionado N+1 | `verificacion/services/subsanar_requisito.py:84-236` (valida versiones, reanuda plazo); endpoint `POST /checklist/{id}/subsanar/` | **Implementado** | Reabre PENDIENTE la verificación; reanuda reloj y EN_VERIFICACION |
| RF-009 | Emisión e inmutabilidad del informe legal #590 | `resoluciones/services/emitir_informe.py:106-218` (+ OneToOne InformeAptitud, endpoints `POST /informes/`) | **Parcialmente implementado** | Funcional, PERO: (a) `HistorialEstado.estado_anterior` guarda el estado YA cambiado (`:199-211`), (b) caracas "Computación"/"FEIRNNR" hardcodeadas (`:69-70` TODO), (c) rechaza dictamen NO APTO (no hay flujo de rechazo) |
| RF-010 | Autogeneración de PDF #590 desde plantilla | `resoluciones/adapters/pdf_generator.py` (796 líneas ReportLab, 99% cov. unitaria) | **Parcialmente implementado** | Genera PDF, PERO `output_dir` default absoluto `/media/private/resoluciones` (`pdf_generator.py:48`) choca con `os.makedirs` en raíz del FS → **74 fallos/errores de test** (PermissionError); no usa `PrivateMediaStorage` |
| RF-011 | Registro de declaratoria y memorando #162 (DECANO) | `resoluciones/services/declarar_aptitud.py:103-199`; endpoint `POST /declaratorias/` | **Parcialmente implementado** | Transición a DECLARADA_APTA + HistorialEstado correcto, **PERO el archivo del memorando firmado NUNCA se guarda** (sólo path nominal, `:180` sin `guardar_archivo_privado`) ⇒ **pérdida de evidencia legal** |
| RF-012 | Notificaciones internas por rol | `notificaciones/models.py` (NotificacionInterna), `services/notification_service.py`, endpoints GET/PATCH | **Implementado** | In-app (DEC-01). Deuda: los servicios de negocio crean notificaciones directamente y no usan el servicio centralizado |
| RF-013 | Bitácora inmutable de auditoría | `notificaciones/adapters/signals.py` (9 señales → EventoAuditoria JSONB fail-safe) | **Parcialmente implementado** | 8 tipos de evento activos; **IP siempre NULL** (`signals.py:32-37`, `_get_current_request` devuelve None); acciones `SUBSANACION_REALIZADA`/`EXPEDIENTE_CANCELADO` definidas en choices pero sin emisión |
| RF-014 | Programación de defensa y tribunal (Fase 2) | — | **No implementado** | Perteneciente a Fase 2 por diseño (specify §10) |
| RF-015 | Calificaciones y acta con firma autógrafa (Fase 2) | — | **No implementado** | Fase 2 |
| RF-016 | Consolidación/registro SENESCYT (Fase 3) | — | **No implementado** | Fase 3 |

## B. Endpoints declarados en OpenAPI (`backend/openapi.yaml` — 17 paths/18 ops)

| ID | Endpoint | Método | Evidencia | Estado | Observaciones |
|---|---|---|---|---|---|
| EP-01 | `/api/v1/auth/token/` | POST | `urls.py:25-26`; serializers claims cedula+roles | Implementado | Sin refresh endpoint ni logout explícito (sólo par) |
| EP-02 | `/api/v1/expedientes/` | POST | `urls.py:29-32` | Implementado | |
| EP-03 | `/api/v1/expedientes/bandeja/` | GET | `views.py:213-242` (MAPA_INTERVENCION_POR_ROL, paginación) | Implementado | RESPONSABLE_DEPENDENCIA no mapeado con alcance propio en scope_filter (denegado) |
| EP-04 | `/api/v1/expedientes/{id}/` | GET | `views.py:111-118` | Implementado | IDOR→404 anti-enumeración |
| EP-05 | `/api/v1/expedientes/{id}/enviar/` | POST | `views.py:120-137`; `enviar_expediente.py` | Implementado | |
| EP-06 | `/api/v1/expedientes/{id}/checklist/` | GET | `urls.py:63-67`; `ChecklistListViewSet` | **Simulado (inoperable)** | Sin celda GET en RBAC ⇒ 403 siempre; existe código+schema+tests pero no usable |
| EP-07 | `/api/v1/checklist/{id}/` | PUT | `ChecklistViewSet.update`→`evaluar_checklist` | Implementado | |
| EP-08 | `/api/v1/checklist/{id}/subsanar/` | POST | `ChecklistViewSet.subsanar`→`subsanar_requisito` | Implementado | |
| EP-09 | `/api/v1/expedientes/{id}/observar/` | POST | `views.py`→`registrar_observacion` | Implementado | |
| EP-10 | `/api/v1/informes/` | POST | `InformeViewSet.create` | Implementado | Con BUG historial (ver RF-009) |
| EP-11 | `/api/v1/declaratorias/` | POST | `DeclaratoriaViewSet.create` | Parcialmente implementado | No persiste archivo (ver RF-011) |
| EP-12 | `/api/v1/notificaciones/` | GET | NotificacionViewSet (doble filtro usuario, `?leida=`) | Implementado | `pagination_class=None` (deuda explícita) |
| EP-13 | `/api/v1/notificaciones/{id}/marcar-leida/` | PATCH | `views.py:69-85` | Implementado | |
| EP-14 | `/api/v1/peticiones/{id}/solicitar-emision/` | POST | `PeticionViewSet` | Implementado | |
| EP-15 | `/api/v1/peticiones/{id}/documento/` | GET/POST | `views.py:187-228` (FileResponse privado) | Implementado | IDOR manual con 404; dependencia de `carrera_id` no-null |
| EP-16 | `/api/v1/peticiones/{id}/documento/{v}/` | GET | mismo | Implementado | Versión específica |
| EP-17 | `/api/v1/schema/`, `/docs/`, `/redoc/` | GET | drf-spectacular | Implementado | |

**No declarados ni implementados:** `/api/v1/health/` (RNF-006), gestión de catálogos (recurso `catalogos:requisitos` en matriz sin vista/endpoint), cancelación de expedientes (estado `CANCELADA` huérfano), legalización de documentos (estado `LEGALIZADO` huérfano), bandeja de `RESPONSABLE_DEPENDENCIA`.

## C. Módulos del proceso de titulación (lista del enunciado, contrastada contra RF oficiales)

| Módulo | Estado | Respaldo |
|---|---|---|
| Gestión de estudiantes | Simulado | Users creados por `seed_initial_data`; no hay registro/self-service (fuera de alcance MVP) |
| Modalidades de titulación | No implementado | Fuera del MVP Art.235 (Fase 2/3) |
| Solicitudes (Aptitud Legal) | Implementado | RF-001 |
| Asignación de tutores | No implementado | Fase 2 |
| Seguimiento | Parcialmente implementado | Bandeja por rol + plazos; sin timeline UI (no hay frontend) |
| Documentación (PDF versionado) | Implementado | RF-005/008 |
| Sustentaciones / Tribunales / Calificaciones / Actas | No implementado | RF-014/RF-015 (Fase 2) |
| Aprobaciones (informe + declaratoria) | Parcialmente implementado | RF-009/RF-011 con defectos |
| Notificaciones | Implementado | RF-012 in-app |
| Reportes | No implementado | No hay requisito RF que lo exija en MVP |
| Integración SIAAF/SGA | **Simulado (honesto)** | `SGAMockAdapter` + fixtures JSON (`core/adapters/mock_sga.py`, `fixtures/sga_mock_records.json`); cero código HTTP (coherente con P-01/RNF-008/DEC-05) |
| Frontend (web/móvil) | No implementado | Fases 2-3 por diseño |

## D. Pruebas por funcionalidad (resultados REALES de ejecución, no porcentajes propagados)

| Suite (src/apps) | Resultado real |
|---|---|
| authentication (JWT + RBAC) | ✅ pasa (100% pass) |
| expedientes (6 suites) | ✅ pasa (100% pass) |
| peticiones (4 suites) | ✅ pasa (100% pass) |
| verificacion (4 suites) | ✅ pasa |
| notificaciones (4 suites) | ⚠️ 5 FAILED + 1 FAILED (por PermissionError de PDF y desincronización) |
| resoluciones (5 suites) | ❌ 39 FAILED + 24 ERROR (raíz: `/media/private` hardcodeado) |
| **Total src/apps** | **464: 390 OK / 50 FAILED / 24 ERROR** |
| `src/core/tests` (26) excluidos de testpaths | ✅ 26/26 pasan |
| `tests/e2e` (4) excluidos de testpaths | ⚠️ 3/4 pasan; **el flujo completo E2E FALLA** por PermissionError `/app/backend/src/media` (PRIVATE_MEDIA_ROOT no definido) en subsanación |

## E. Contraste con el README (`README.md`)

| Afirmación README | Realidad medida |
|---|---|
| "464+ tests, TOTAL 468, cobertura 95%" | 464 en src/apps (494 con core+e2e); **88%** cobertura medida; **74 fallos reales** |
| Suite "resoluciones 122 tests, 95% cob." | Dedo falla mayoritario (39F+24E); servicio `declarar_aptitud` cubierta sólo 35% |
| Despliegue docker compose | ✅ verificado funcionando (con migraciones/seed) |
| Swagger 200 | ✅ verificado |
| JWT login demo | ✅ verificado con `estudiante_1/SgtDemo2026!` |
