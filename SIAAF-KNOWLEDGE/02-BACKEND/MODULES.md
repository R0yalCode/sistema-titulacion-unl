---
system: SGT-SIAAF
type: module-catalog
area: backend
status: verified
source: verified-code
last_verified: 2026-11-11
---

# Módulos backend

Ruta base: `backend/src/apps/`. Estado según código real; los tests existen pero **no se reejecutaron en esta sesión** (requieren PostgreSQL/entorno Docker). La última cifra documentada es 497 tests con 93 % de cobertura y 13 fallos de entorno `pypdf` ([[DP2-MATRIZ_BRECHAS]] TEST-01, no verificada aquí).

| Módulo | Responsabilidad | Servicios (`services/`) | Endpoints | Tests | Estado |
|---|---|---|---|---|---|
| `authentication` | Usuario, roles, JWT, RBAC, throttling de login, admin, comando `seed_initial_data` | — (lógica en `adapters/permissions.py`, `throttling.py`) | `POST /auth/token/` | `test_jwt`, `test_rbac_permissions`, `test_security_controls`, `test_swagger_protection`, `test_django_admin` | Implementado; sin refresh/logout (BE-03) |
| `expedientes` | Expediente de titulación, estados, plazos, bandeja | `crear_expediente`, `enviar_expediente`; `domain/plazo_calculator` | `POST /expedientes/`, `GET bandeja`, `GET {id}`, `POST enviar`, `POST observar` | `test_crear_expediente`, `test_enviar_expediente`, `test_expediente_state_machine`, `test_bandeja_expedientes`, `test_idor_isolation_expediente`, `test_plazo_calculator` | Implementado; **falta transición `ENVIADA→EN_VERIFICACION`** (GAP-STATE-01) y `CANCELADA` |
| `peticiones` | Catálogo de requisitos, peticiones documentales, carga/descarga PDF versionada | `solicitar_emision`, `cargar_documento` | `POST solicitar-emision`, `POST/GET documento`, `GET documento/{version}` | `test_solicitar_emision`, `test_cargar_documento`, `test_descargar_documento`, `test_pdf_ingestion_and_security`, `test_upload_throttle` | Implementado; `SCOPE_ASIGNADO` manual solo en descarga; sin verificación SHA-256 al descargar (VULN-003, según DP2) |
| `verificacion` | Checklist digital, observaciones, subsanación | `evaluar_checklist`, `registrar_observacion`, `subsanar_requisito`, `validar_checklist_completo` | `GET checklist`, `PUT checklist/{id}`, `POST subsanar` | `test_evaluar_checklist`, `test_subsanar_requisito`, `test_validar_checklist_completo`, `test_checklist_and_observations` | Implementado; excepciones de dominio → HTTP 500 (INC-21) |
| `resoluciones` | Informe de aptitud (Providencia #590) y declaratoria (Memorando #162) | `emitir_informe`, `declarar_aptitud`; `adapters/pdf_generator.py` | `POST /informes/`, `POST /declaratorias/` | `test_emitir_informe`, `test_declarar_aptitud`, `test_models`, `test_pdf_generator`, `test_resoluciones_and_pdf_generation` | Parcial: memorando "firmado externamente (FirmaEC)" validado solo como PDF genérico (VULN-010) |
| `notificaciones` | Notificaciones internas, auditoría inmutable, señales | `notification_service`; `adapters/signals.py` | `GET /notificaciones/`, `PATCH marcar-leida` | `test_endpoints`, `test_auditoria`, `test_audit_ip`, `test_notification_service`, `test_notifications_and_audit` | Implementado; listado sin paginación (INC-19) |
| `core` | Transversales: scope, PDF, almacenamiento, mock SGA, IP, cabeceras, health | — | `GET /health/` | `core/tests/`, `core/adapters/tests/` | Implementado |

E2E backend: `backend/tests/e2e/test_full_workflow.py` (fuerza `ENVIADA→EN_VERIFICACION` asignando el estado).

## Módulos inexistentes (solo propuestos)

| Módulo | Fuente | Estado |
|---|---|---|
| App `indicadores` (KPIs, `/dashboard/me/`) | [[DP2-ESPECIFICACION_SERVICIOS_DASHBOARD]] | Propuesta (INC-04) |
| Modalidades de titulación | [[DP2-DISENO_FUNCIONAL_MODALIDADES]] | Propuesta (BE-06, INC-03); sin validación normativa |
| Sesiones / logout | [[DP2-PLAN_SESIONES]] | Propuesta (INC-02) |
| Integración FirmaEC real | [[FIRMA_EC]] | Propuesta |

## Relacionado

[[BACKEND_ARCHITECTURE]] · [[DATABASE]] · [[API_CONTRACTS]] · [[PERMISSIONS_ROLES]] · [[06-AUDITS/BACKEND/BACKEND_AUDITS|Auditorías backend]]
