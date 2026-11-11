---
system: SGT-SIAAF
type: traceability
status: verified
source: verified-code + specs + Documentacion-parte-2
last_verified: 2026-11-11
aliases: [REQUIREMENTS_IMPLEMENTATION, REQUIREMENTS_TESTS]
---

# Matriz general de trazabilidad

Leyenda: **IV** implementado y verificado en código · **IP** parcial · **DNI** documentado, no implementado · **PR** propuesta · **NV** no verificado · **BL** bloqueado.
"Prueba" indica que existe un archivo de prueba; su ejecución backend **no** se repitió en esta sesión.

| Capacidad | Requisito / fuente | Backend | Frontend | Prueba | Estado |
|---|---|---|---|---|---|
| Login JWT | specify 001 §6; FE-T011…017, FE-T101…104 | `POST /auth/token/` | V-01 | `test_jwt.py`; pruebas de V-01 | **IV** |
| Refresh / logout de servidor | BE-03; INC-02 | — | Logout local | — | **DNI** (BL) |
| Crear expediente + 5 peticiones | RN-001, HU-001 | `crear_expediente.py` | V-03 | `test_crear_expediente.py` | **IV** |
| Enviar (plazo de 8 días) | RN-002, RN-010 | `enviar_expediente.py`, `plazo_calculator.py` | V-04 | `test_enviar_expediente.py`, `test_plazo_calculator.py` | **IV** |
| Iniciar verificación (`ENVIADA→EN_VERIFICACION`) | FL-03 | **Sin operación** | — | Los tests fuerzan el estado | **IP** (GAP-STATE-01) |
| Solicitar emisión | FL-02, HU-002 | `solicitar_emision.py` | V-05 (stub) | `test_solicitar_emision.py` | Backend IV / frontend DNI |
| Cargar o descargar PDF versionado | RN-009, RN-011 | `cargar_documento.py`, `descargar_documento` | V-04 (descarga); V-05 stub | `test_cargar_documento.py`, `test_descargar_documento.py` | **IV** (sin hash al descargar) |
| Evaluar checklist | FL-03 | `evaluar_checklist.py` | V-04 (por rol); V-08 stub | `test_evaluar_checklist.py` | **IV** (inalcanzable por API sin GAP-STATE-01) |
| Observar | FL-04 | `registrar_observacion.py` | `ObservarDialog` | `test_checklist_and_observations.py` | **IV** (500 en errores de dominio) |
| Subsanar | FL-04 | `subsanar_requisito.py` | V-04 | `test_subsanar_requisito.py` | **IP** (ESTUDIANTE no puede obtener el ID: FE-T407) |
| Emitir informe #590 | RN-003, RN-004 | `emitir_informe.py`, `pdf_generator.py` | V-08 stub | `test_emitir_informe.py` | Backend IV / frontend DNI |
| Declarar aptitud #162 | FL-05 | `declarar_aptitud.py` | V-08 stub | `test_declarar_aptitud.py` | Backend IP (FirmaEC) / frontend DNI |
| Notificaciones internas | DEC-01 (spec 001) | `notificaciones` | V-02 | `test_endpoints.py` (notificaciones) | **IV** |
| Auditoría inmutable | — | `EventoAuditoria` | — | `test_auditoria.py`, `test_audit_ip.py` | **IV** |
| Bandeja de funcionario | BE-09 | `BandejaExpedienteViewSet` | V-07 stub | `test_bandeja_expedientes.py` | Backend IP / frontend DNI |
| Cancelar expediente | — | Estado sin operación | — | — | **DNI** |
| RBAC de RESPONSABLE_DEPENDENCIA | VULN-006 | Sin celdas | Fuera de `OPERATIONAL_ROLES` | — | **IP** |
| Throttling de mutantes | VULN-001 / INC-01 | — | — | — | **PR** |
| Modalidades TIC/EC | BE-06 / INC-03 / INC-08 | — | — | — | **PR** (sin validación normativa) |
| KPIs y `/dashboard/me/` | INC-04 | — | Solo V-02 con datos reales | — | **PR** |
| Búsqueda / exportación | INC-05/06 | — | — | — | **PR** |
| Sesiones / usuarios activos | INC-02 | — | — | — | **PR** |
| FirmaEC real | VULN-010 | — | — | — | **PR** |
| Fase 2 (tribunal, notas) | RN-006…008 | — | — | — | **DNI** |
| Fase 3 (acta, SENESCYT) | Arts. 243–244 | — | — | — | **DNI** |

Detalle normativo: [[REGULATORY_TRACEABILITY]] · Fuentes documentales: [[DOCUMENT_TRACEABILITY]] · Evidencias: [[EVIDENCE_INDEX]]
