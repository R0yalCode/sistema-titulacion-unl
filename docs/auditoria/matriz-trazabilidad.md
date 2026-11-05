---
title: "Matriz de trazabilidad"
---

# Matriz de trazabilidad

Relaciona requisitos → módulo → modelo → API → pruebas → KPI → documentación. **Fuente de requisitos**: `specs/001-tramite-titulacion/specify.md` (RF-001…RF-016) y `specs/003-frontend-titulacion/specify.md` (RFF). No se inventaron identificadores.

Leyenda de estado: **IV** implementado y verificado · **IP** parcial · **NI** no implementado · **BLQ** bloqueado.

## Backend (RF de specs/001)

| Requisito | Módulo | Modelo | API | Prueba | KPI relacionado | Estado |
|---|---|---|---|---|---|---|
| RF-001 Crear solicitud con requisitos Art. 235 | expedientes | ExpedienteTitulacion, PeticionDocumental | POST /expedientes/ | test_crear_expediente (8) | KPI-EST-01, KPI-SEC-05 | IV |
| RF-002 Numeración correlativa | expedientes, resoluciones | numero_expediente/providencia/memorando | todas las de creación | test_crear/enviar, test_emitir/declarar | — | IV |
| RF-003 Envío formal con requisitos en firme | expedientes | estado, fecha_recepcion | POST /expedientes/{id}/enviar/ | test_enviar_expediente (7) | KPI-SEC-01 | IV |
| RF-004 Plazo de 8 días hábiles con pausa/reanudación | expedientes | fecha_limite_atencion, dias_laborables_acumulados | (derivado de enviar/observar/subsanar) | test_plazo_calculator (11), state_machine | KPI-SEC-02, KPI-EST-06 | IV |
| RF-005 Solicitar emisión a dependencia | peticiones | PeticionDocumental, NotificacionInterna | POST /peticiones/{id}/solicitar-emision/ | test_solicitar_emision (15) | KPI-DEP-01 | IV |
| RF-006 Carga de PDF validado y versionado | peticiones, core | DocumentoEntregado | POST /peticiones/{id}/documento/ | test_cargar (19), test_pdf_ingestion (39) | KPI-EST-04 | IV |
| RF-007 Descarga segura de documentos | peticiones, core | DocumentoEntregado | GET /peticiones/{id}/documento[/{version}]/ | test_descargar (12) | — | IV |
| RF-008 Checklist digital del jurista | verificacion | ChecklistVerification | GET /expedientes/{id}/checklist/, PUT /checklist/{id}/ | test_evaluar (22) | KPI-JUR-02, KPI-EST-07 | IV |
| RF-009 Observación accionable con pausa de plazo | verificacion | ObservacionAccionable | POST /expedientes/{id}/observar/ | test_checklist_and_observations (28) | KPI-JUR-03, KPI-EST-03 | IV |
| RF-010 Subsanación con nueva versión | verificacion, peticiones | DocumentoEntregado vN+1 | POST /checklist/{id}/subsanar/ | test_subsanar (15) | KPI-EST-03 | IV |
| RF-011 Informe de aptitud (Providencia 590) | resoluciones | InformeAptitud | POST /informes/ | test_emitir_informe (24) | KPI-JUR-05, KPI-DEC-01 | IV |
| RF-012 Declaratoria (Memorando 162) | resoluciones | DeclaratoriaAptitud | POST /declaratorias/ | test_declarar_aptitud (29) | KPI-DEC-02 | IV |
| RF-013 Notificaciones in-app | notificaciones | NotificacionInterna | GET /notificaciones/, PATCH marcar-leida | test_notification_service (17), endpoints (12) | KPI-EST-05 | IV |
| RF-014 Bitácora de auditoría | notificaciones | EventoAuditoria | (signals, sin endpoint) | test_auditoria (14) | KPI-ADM-08 | IP (3 eventos sin emitir, IP vacía) |
| RF-015 RBAC por rol y recurso | authentication | Role, UserRole | transversal | test_rbac_permissions (17) | (base de todos) | IV |
| RF-016 Récord académico del SGA (solo lectura) | core | — (puerto) | — | test_mock_sga (25) | — | IV (mock; integración real NI) |

## Requisitos sin implementación declarada en specs/001

| Requisito | Estado | Nota |
|---|---|---|
| Legalización de documentos (estado LEGALIZADO) | NI | Estado definido en el enum, sin flujo |
| Cancelación de expediente (CANCELADA) | NI | Estado definido, sin endpoint |
| CRUD de catálogo de requisitos | NI | Celda RBAC definida, sin endpoint |
| Modalidades de titulación | NI | Fuera de Fase 1 (BE-06) |

## Frontend (RFF de specs/003 — resumen)

| Requisito/Vista | Módulo FE | API que consume | Prueba FE | Estado |
|---|---|---|---|---|
| RFF-101…105 / V-01 Login | features/auth | POST /auth/token/ | auth.test, client.test | IP (auth lista, vista stub) |
| V-02 Dashboard estudiante | features/dashboard | (futura: dashboard/me) | — | NI |
| V-03 Nueva solicitud | features/solicitud | POST /expedientes/ | — | NI |
| V-04 Detalle expediente | features/expediente | GET /expedientes/{id}/ | — | NI |
| V-05/V-06 Peticiones y seguimiento | features/peticiones | /peticiones/… | — | NI |
| V-07/V-08 Bandeja | features/bandeja | GET /expedientes/bandeja/ | — | NI |
| V-09 No habilitado | features/no-habilitado | — | guards.test | IP (guard listo, vista stub) |
| 404 global | app | — | NotFoundPage.test | IV |
| RFF-001…020 transversales (router, auth, errores, a11y) | app/api/auth/components | — | 198 pruebas | IP (base lista; vistas pendientes) |
| FE-T1213 inline-alerts 409/412/428 | — | BE-11 | — | **BLQ** (backend no declara esos códigos) |

## Correspondencia con documentación

| Requisito | Documentado en |
|---|---|
| RF-001…RF-016 | [Módulos](../03-modulos/inventario-modulos.md), [API](../04-api/introduccion.md), [C4 componentes](../02-arquitectura/c4/componentes.md) |
| RFF/RNFF | [Arquitectura frontend](../02-arquitectura/arquitectura-frontend.md) |
| KPI | [Informe KPI](../07-indicadores/informe-kpi.md) |
