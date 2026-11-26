# Matriz de trazabilidad — SGT-SIAAF (consolidada)

**Objetivo:** relacionar Requisito → Historia de usuario → Criterio de aceptación → Componente implementado → Endpoint → Prueba, usando únicamente relaciones verificables declaradas en las fuentes. Consolida `sgt-siaaf/specs/001-tramite-titulacion/specify.md` §15 (requisito↔HU↔CA↔principio) con `docs/auditoria/matriz-trazabilidad.md` (módulo↔modelo↔API↔prueba↔estado), y corrige el estado del frontend con la fuente más reciente (`CLAUDE.md`, 2026-11-05/06) donde ambas fuentes discrepan (hallazgo H-02 de la Fase 0).

## 1. Backend — Fase 1 (MVP)

| Requisito | Historia de usuario | Criterio de aceptación | Módulo / Componente | Endpoint | Prueba (fuente: `docs/auditoria/matriz-trazabilidad.md`) | Estado |
|---|---|---|---|---|---|---|
| RF-001 | HU-001 | CA-001 | `expedientes` (`ExpedienteTitulacion`, `PeticionDocumental`) | `POST /expedientes/` | `test_crear_expediente` (8 casos) | IV |
| RF-002, RF-003 | HU-004 | CA-001 | `expedientes` | `POST /expedientes/{id}/enviar/` | `test_enviar_expediente` (7), `test_plazo_calculator` (11) | IV |
| RF-004 | HU-002 | CA-002 | `peticiones` | `POST /peticiones/{id}/solicitar-emision/` | `test_solicitar_emision` (15) | IV |
| RF-005 | HU-003 | CA-001, CA-004 | `peticiones`, `core` (validación PDF) | `POST /peticiones/{id}/documento/` | `test_cargar` (19), `test_pdf_ingestion` (39) | IV |
| RF-006 | HU-006 | CA-003 | `verificacion` | `GET /expedientes/{id}/checklist/`, `PUT /checklist/{id}/` | `test_evaluar` (22) | IV |
| RF-007 | HU-007 | CA-003 | `verificacion` | `POST /expedientes/{id}/observar/` | `test_checklist_and_observations` (28) | IV |
| RF-008 | HU-008 | CA-004 | `verificacion`, `peticiones` | `POST /checklist/{id}/subsanar/` | `test_subsanar` (15) | IV |
| RF-009, RF-010 | HU-009 | CA-005 | `resoluciones` | `POST /informes/` | `test_emitir_informe` (24) | IV |
| RF-011 | HU-010 | CA-006 | `resoluciones` | `POST /declaratorias/` | `test_declarar_aptitud` (29) | IV |
| RF-012 | HU-005 | CA-002 | `notificaciones` | `GET /notificaciones/`, `PATCH .../marcar-leida/` | `test_notification_service` (17), endpoints (12) | IV |
| RF-013 | — | CA-008 (relacionado, IDOR) | `notificaciones` (signals) | — (sin endpoint directo) | `test_auditoria` (14) | **IP** — posiblemente 3 eventos sin emitir (no reverificado); **la IP de origen YA NO está vacía** (corregido en Fase 9, `resolver_ip_cliente` confirmado wired a `EventoAuditoria.ip`) |
| RF-014 | — | CA-007 (parcial) | — | — | — | NI (Fase 2, fuera de alcance) |
| RF-015 | — | CA-007 | — | — | — | NI (Fase 2, fuera de alcance) |
| RF-016 | — | — | — | — | — | NI (Fase 3, fuera de alcance) |
| RNF-002/003 (transversal) | — | CA-008 | `authentication` | transversal | `test_rbac_permissions` (17) | IV |
| — (soporte) | — | — | `core` (mock SGA) | — | `test_mock_sga` (25) | IV (mock; integración real NI por diseño) |

**Pendientes sin HU/RF propio** (ver `docs/auditoria/matriz-trazabilidad.md`, sección "Requisitos sin implementación declarada"): legalización de documentos (estado `LEGALIZADO`), cancelación de expediente (`CANCELADA`), CRUD de catálogo de requisitos, modalidades de titulación — todos **NI**, por diseño o por ausencia de endpoint, sin corresponder a un RF numerado en `specify.md`.

## 2. Frontend — vistas (estado actualizado respecto a la fuente original)

| Vista / Requisito | Módulo FE | API que consume | Estado en `docs/auditoria/matriz-trazabilidad.md` (05-nov, snapshot temprano) | **Estado corregido** (fuente: `CLAUDE.md`, checkpoint más reciente del mismo periodo) |
|---|---|---|---|---|
| V-01 Login | `features/auth` | `POST /auth/token/` | IP (vista stub) | **Hecha** — FE-T101…T104, 22 pruebas nuevas |
| V-02 Dashboard estudiante | `features/dashboard` | `GET /expedientes/bandeja/`, `GET`/`PATCH /notificaciones/` | NI | **Hecha** — FE-T201…T206, 29 pruebas nuevas |
| V-03 Nueva solicitud | `features/solicitud` | `POST /expedientes/` | NI | **Hecha** — FE-T301…T306, 24 pruebas nuevas |
| V-04 Detalle expediente / requisitos | `features/expediente`, `features/peticiones` | `GET /expedientes/{id}/`, checklist, descarga | NI | **Hecha** — FE-T401…T411, 51 pruebas nuevas |
| V-05/V-06 Peticiones y seguimiento adicional | `features/peticiones` | — | NI | **Sin iniciar** (requiere autorización explícita, `CLAUDE.md`) |
| V-07/V-08 Bandeja (roles no-estudiante) | `features/bandeja` | `GET /expedientes/bandeja/` | NI | **Sin iniciar** |
| V-09 No habilitado | `features/no-habilitado` | — | IP (guard listo) | Sin cambio reportado; guard confirmado |
| 404 global | `app` | — | IV | Sin cambio |
| FE-T1213 (409/412/428) | — | BE-11 | BLQ | **BLQ** — sigue bloqueada por BE-11, no autorizada |

**Nota metodológica:** esta corrección no reemplaza el archivo `docs/auditoria/matriz-trazabilidad.md` (no se modifica, conforme a la regla de no duplicar/sobrescribir documentación existente sin análisis); se presenta como una vista actualizada en este expediente nuevo, citando ambas fuentes y la fecha de cada una.

## 3. Correspondencia con documentación del portal

| Conjunto | Documentado en |
|---|---|
| RF-001…RF-013 (implementados) | [Módulos](../../docs/03-modulos/inventario-modulos.md), [API](../../docs/04-api/introduccion.md), [C4 componentes](../../docs/02-arquitectura/c4/componentes.md) |
| RNF | `DOCUMENTACION/01_ESPECIFICACION/REQUISITOS_NO_FUNCIONALES.md` (este expediente) |
| Vistas frontend | [Arquitectura frontend](../../docs/02-arquitectura/arquitectura-frontend.md), `CLAUDE.md` (estado más reciente) |
| KPI | [Informe KPI](../../docs/07-indicadores/informe-kpi.md) |

## 4. Brechas de trazabilidad detectadas

1. RF-013 (auditoría) está marcado IP, no IV — **actualizado en Fase 9**: la IP de origen ya se captura correctamente (hallazgo heredado corregido); queda sin reverificar si los "3 eventos sin emitir" originales siguen pendientes.
2. No existe una matriz tarea↔prueba completa y verificada para el backend en este expediente (la de `tasks.md` §8 no se leyó íntegramente en esta pasada); se recomienda incorporarla en la Fase 4 si aporta trazabilidad adicional no cubierta aquí.
3. El snapshot de vistas frontend en `docs/auditoria/matriz-trazabilidad.md` quedó desactualizado dentro del mismo periodo de trabajo (H-02); esta matriz lo corrige citando ambas fuentes, pero el archivo original no se edita.
