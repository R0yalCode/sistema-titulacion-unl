# PLAN MAESTRO DE IMPLEMENTACIÓN — HARDENING DE SEGURIDAD BACKEND SGT-SIAAF

**Fecha:** 2026-11-05  
**Versión:** 1.0  
**Estado:** Planificación — No implementado

---

## Resumen Ejecutivo

Este plan describe la implementación incremental, controlada y verificable de las **21 tareas de seguridad (SEC-T001 a SEC-T021)** identificadas en la auditoría del backend SGT-SIAAF.

**Objetivo:** Cerrar las brechas críticas y medias que impiden considerar el backend listo para producción, manteniendo compatibilidad total con el frontend en desarrollo (specs/003).

**Alcance:** Solo backend (Django REST Framework). No se modifican reglas de negocio, permisos RBAC, contratos de API aprobados ni código del frontend.

**Estrategia:** Implementar por fases según dependencias técnicas y riesgo de seguridad, priorizando infraestructura base (SEC-T001) y controles de autenticación (SEC-T002 a SEC-T005).

---

## Estado de las 21 Tareas

| ID | Tarea | Prioridad | Riesgo | Estado | Dependencias Clave |
|----|-------|-----------|--------|--------|-------------------|
| SEC-T001 | Configuración Producción Completa | CRÍTICA | CRÍTICO | **Cerrada (2026-11-05)** | Bloquea: SEC-T005, SEC-T007, SEC-T010, SEC-T011, SEC-T013, SEC-T019, SEC-T020 |
| SEC-T002 | Throttling Login | ALTA | ALTO | **Cerrada (2026-11-05)** | Requiere: SEC-T005 (IP real) |
| SEC-T003 | Rotación + Blacklist Refresh Tokens | ALTA | ALTO | Pendiente — bloqueada por DEC-008 | Requiere: SEC-T004 (JWT Key separada) |
| SEC-T004 | JWT_SIGNING_KEY Separada | ALTA | ALTO | **Cerrada (2026-11-05)** | Independiente — cerrada sin depender de SEC-T001 |
| SEC-T005 | IP Auditoría + Middleware Thread-Local + TRUSTED_PROXIES | ALTA | ALTO | **Cerrada (2026-11-05)** | Requiere: SEC-T001 (production.py + Nginx) |
| SEC-T006 | Access Token 30 min | MEDIA | MEDIO | **Cerrada (2026-11-05)** | Requiere: SEC-T004 |
| SEC-T007 | Validación MIME Real (python-magic/pikepdf) | MEDIA | MEDIO | Pendiente — bloqueada por DEC-001 | Requiere: SEC-T001 (Dockerfile libmagic) |
| SEC-T008 | Throttling Carga Documentos | MEDIA | MEDIO | **Cerrada (2026-11-05)** | Independiente |
| SEC-T009 | Remover Rutas Internas Serializers | MEDIA | MEDIO | Pendiente — bloqueada por DEC-006 | Requiere: SEC-T001 (endpoint download declaratoria) |
| SEC-T010 | Handler Global Excepciones | MEDIA | MEDIO | Pendiente — bloqueada por DEC-009 | Requiere: SEC-T001 (production.py DEBUG=False) |
| SEC-T011 | Logging Estructurado | MEDIA | MEDIO | **Cerrada (2026-11-05)** | Requiere: SEC-T012 (eliminar print) |
| SEC-T012 | Eliminar print() evaluar_checklist.py | MEDIA | MEDIO | **Cerrada (2026-11-05)** | Independiente |
| SEC-T013 | Protección Swagger/ReDoc/Schema (IsAdminUser) | MEDIA | MEDIO | **Cerrada (2026-11-05)** | Requiere: SEC-T001 (production.py) |
| SEC-T014 | CI/CD Security (Safety + Bandit + Gitleaks) | MEDIA | MEDIO | **Cerrada (2026-11-05)** | Requiere: SEC-T001 (Dockerfile) |
| SEC-T015 | Dependabot Configurado | MEDIA | MEDIO | **Cerrada (2026-11-05)** (config; activación pendiente de push real) | Requiere: SEC-T014 (CI tests) |
| SEC-T016 | Cobertura Tests + testpaths | MEDIA | MEDIO | Pendiente — bloqueada por DEC-004 (valor umbral) | Independiente |
| SEC-T017 | Tests Seguridad Faltantes | MEDIA | MEDIO | Pendiente — requiere SEC-T003 (aún bloqueada) | Requiere: SEC-T002, SEC-T003, SEC-T005, SEC-T013 |
| SEC-T018 | Procedimiento Rotación Secretos | BAJA | BAJO | **Cerrada (2026-11-05)** | Requiere: SEC-T004 |
| SEC-T019 | Limpieza Archivos Huérfanos | BAJA | BAJO | Bloqueada — DEC-005 pendiente | Requiere: SEC-T001 (Dockerfile cron) |
| SEC-T020 | Verificación PermissionError Docker | BAJA | BAJO | **Cerrada (2026-11-05)** | Requiere: SEC-T001 (Dockerfile + docker-compose) |
| SEC-T021 | Evidencias ACD 4 Reales | BAJA | BAJO | Pendiente — bloqueada por DEC-007 | Independiente |

---

## Estrategia General

### Principios de Implementación

1. **Una tarea a la vez** — Implementar, probar, verificar, documentar, cerrar.
2. **Dependencias respetadas** — No iniciar tarea si sus dependencias no están cerradas.
3. **Tests first** — Para tareas que añaden funcionalidad, escribir tests antes o en paralelo.
4. **Regresión obligatoria** — Ejecutar suite completa (473 tests) tras cada tarea.
5. **Frontend compatible** — Cualquier cambio en API/contrato requiere coordinación y tests de contrato.
6. **Rollback documentado** — Cada tarea debe tener procedimiento de reversión.
7. **Evidencia de cierre** — Criterios de aceptación medibles y verificables.

### Orden Recomendado (por fases)

#### Fase 0: Preparación e Independencia (Semana 1)
- **SEC-T004** — JWT_SIGNING_KEY separada (independiente, base para SEC-T003, SEC-T006)
- **SEC-T012** — Eliminar print() evaluar_checklist.py (independiente, rápido, requisito para SEC-T011)
- **SEC-T016** — Cobertura tests + testpaths (independiente, mejora calidad suite)
- **SEC-T008** — Throttling carga documentos (independiente, bajo riesgo)

#### Fase 1: Infraestructura Base Producción (Semana 1-2) — **BLOQUE CRÍTICO**
- **SEC-T001** — Configuración producción completa (production.py, Dockerfile, docker-compose.prod.yml, Nginx, TLS, headers, usuario no-root)
  - *Desbloquea: SEC-T005, SEC-T007, SEC-T010, SEC-T011, SEC-T013, SEC-T014, SEC-T019, SEC-T020*

#### Fase 2: Controles Autenticación y Auditoría (Semana 2-3)
- **SEC-T005** — IP Auditoría + Middleware Thread-Local + TRUSTED_PROXIES (requiere SEC-T001)
- **SEC-T002** — Throttling login 5/min/IP (requiere SEC-T005 para IP real)
- **SEC-T003** — Rotación + Blacklist refresh tokens + logout endpoint (requiere SEC-T004)
- **SEC-T006** — Access token 30 min (requiere SEC-T004)

#### Fase 3: Validación, Serializers y Errores (Semana 3-4)
- **SEC-T007** — Validación MIME real (requiere SEC-T001 Dockerfile)
- **SEC-T009** — Remover rutas internas serializers (requiere SEC-T001 endpoint declaratoria download)
- **SEC-T010** — Handler global excepciones (requiere SEC-T001 production.py)
- **SEC-T011** — Logging estructurado (requiere SEC-T012)

#### Fase 4: Protección Documentación y CI/CD (Semana 4)
- **SEC-T013** — Protección Swagger/ReDoc/Schema (requiere SEC-T001)
- **SEC-T014** — CI/CD Security Safety+Bandit+Gitleaks (requiere SEC-T001 Dockerfile)
- **SEC-T015** — Dependabot (requiere SEC-T014)

#### Fase 5: Tests de Seguridad (Semana 4-5)
- **SEC-T017** — Tests seguridad faltantes (requiere SEC-T002, SEC-T003, SEC-T005, SEC-T013 implementados)

#### Fase 6: Documentación y Operaciones (Post-deploy inicial)
- **SEC-T018** — Procedimiento rotación secretos (requiere SEC-T004)
- **SEC-T019** — Limpieza archivos huérfanos (requiere SEC-T001)
- **SEC-T020** — Verificación PermissionError Docker (requiere SEC-T001)
- **SEC-T021** — Evidencias ACD 4 reales (independiente)

---

## Matriz de Dependencias y Bloqueos

```
SEC-T001 ──────────────────────────────────┐
  │                                        │
  ├── SEC-T005 (IP Auditoría) ◄───────────┤
  │     │                                  │
  │     └── SEC-T002 (Throttling Login)    │
  │                                        │
  ├── SEC-T007 (MIME Real)                 │
  │                                        │
  ├── SEC-T010 (Exception Handler)         │
  │                                        │
  ├── SEC-T011 (Logging)                   │
  │     │                                  │
  │     └── SEC-T012 (print cleanup) ◄─────┤ (independiente)
  │                                        │
  ├── SEC-T013 (Swagger Protection)        │
  │                                        │
  ├── SEC-T014 (CI/CD Security)            │
  │     │                                  │
  │     └── SEC-T015 (Dependabot)          │
  │                                        │
  ├── SEC-T019 (Archivos Huérfanos)        │
  │                                        │
  └── SEC-T020 (PermissionError Docker)    │
                                           │
SEC-T004 (JWT Key) ◄───────────────────────┘ (independiente)
  │
  ├── SEC-T003 (Rotación/Blacklist)
  │
  ├── SEC-T006 (Access Token 30min)
  │
  └── SEC-T018 (Proc. Rotación)

SEC-T008 (Throttling Carga) ── Independiente
SEC-T009 (Serializers) ───────► Requiere SEC-T001 (endpoint declaratoria)
SEC-T016 (Cobertura) ─────────► Independiente
SEC-T017 (Tests Seguridad) ───► Requiere SEC-T002, T003, T005, T013
SEC-T021 (Evidencias ACD 4) ──► Independiente
```

---

## Riesgos Principales

| Riesgo | Tareas Afectadas | Mitigación |
|--------|------------------|------------|
| SEC-T001 complejidad alta (infra completa) | Todas las que dependen de production.py/Dockerfile | Dividir en sub-tareas: 1) production.py, 2) Dockerfile, 3) docker-compose, 4) Nginx. Validar cada paso. |
| Cambio JWT_SIGNING_KEY invalida tokens existentes | SEC-T003, SEC-T006 | Planear deploy coordinado; comunicar re-login único a usuarios. |
| Middleware thread-local en Django async | SEC-T005 | Usar `contextvars` (Python 3.7+) compatible con ASGI/async. Validar en tests concurrencia. |
| Impacto frontend en SEC-T009 (download_url) | SEC-T009 | Coordinar con equipo frontend; mantener backward compatibility temporal si es posible. |
| Tests de seguridad (SEC-T017) requieren controles implementados | SEC-T017 | No iniciar SEC-T017 hasta que SEC-T002, T003, T005, T013 estén cerrados y pasando tests. |
| Rotación secretos (SEC-T018) sin procedimiento aprobado | SEC-T018 | Documentar y aprobar ANTES de primera rotación real. |

---

## Decisiones Pendientes (Requieren Aprobación Humana)

1. **Validación MIME:** `python-magic` (libmagic sistema) vs `pikepdf` (parseo PDF) — requiere evaluación compatibilidad Docker alpine/slim.
2. **Límite throttling login:** 5/min/IP es referencia; confirmar valor aprobado.
3. **Límite throttling carga docs:** 10/hora/usuario es referencia; confirmar valor aprobado.
4. **Umbral cobertura:** 80% propuesto; confirmar valor acordado.
4. **Retención archivos huérfanos:** 90 días propuesto; confirmar política.
5. **Evidencias ACD 4:** Confirmar si placeholders son datos de prueba o requieren evidencia real.
6. **Scope SEC-T009:** Crear endpoint download declaratoria vs reutilizar existente — requiere análisis resoluciones/views.py.

---

## Condiciones de Cierre Global

La implementación se considera completa cuando:

1. ✅ **SEC-T001 a SEC-T006** cerradas (Producción lista + Autenticación segura).
2. ✅ **SEC-T007 a SEC-T017** cerradas (Controles medios + Tests + CI/CD).
3. ✅ **Suite 473+ tests passing** + coverage ≥80% en CI.
4. ✅ **Staging deploy verificado** con PostgreSQL real, Nginx TLS, backend + frontend (specs/003 V-01 a V-09).
5. ✅ **Documentación actualizada:** DEPLOY_PRODUCTION.md, SECURITY_CONFIG.md, API_ERROR_FORMAT.md, CI_SECURITY.md, TESTING.md, OPERATIONS.md.
6. ⏳ **SEC-T018 a SEC-T021** documentadas (pueden completarse post-deploy inicial).

---

## Entregables del Plan (esta carpeta)

1. `PLAN_MAESTRO_IMPLEMENTACION.md` — Este documento.
2. `FICHAS_TECNICAS_SEC_T001_SEC_T021.md` — 21 fichas de ejecución para Claude.
3. `MATRIZ_DEPENDENCIAS_Y_PRIORIZACION.md` — Dependencias, orden, bloqueos, paralelizables.
4. `MATRIZ_COMPATIBILIDAD_BACKEND_FRONTEND_SEGURIDAD.md` — Impacto frontend por tarea.
5. `DECISIONES_TECNICAS_PENDIENTES.md` — Decisiones que requieren aprobación (estado de cada una).
6. `CHECKLIST_EJECUCION_Y_CIERRE.md` — Lista de verificación control avance (estado real por tarea).
7. `DECISION_LOG.md` — Registro cronológico de decisiones efectivamente aprobadas (DEC-002, DEC-003, DEC-004 corrección documental, DEC-010).
8. `PAQUETE_APROBACION_SEC-T001_DEC_002_003_010.md` — Análisis y recomendación para DEC-002, DEC-003, DEC-010 y la ubicación de archivos de producción (ya resuelto).
9. `PAQUETE_APROBACION_DECISIONES_PENDIENTES.md` — Análisis y recomendación para DEC-001, DEC-004 (valor), DEC-005, DEC-006, DEC-007, DEC-008, DEC-009 (pendientes).
10. `ACTA_CIERRE_SEC-T004.md` — Acta de cierre de SEC-T004, pendiente de firma electrónica FirmaEc.

---

**Firma:** opencode AI Assistant  
**Fecha:** 2026-11-05  
**Próxima acción (actualizado 2026-11-05):** SEC-T004 (JWT_SIGNING_KEY separada) fue autorizada, implementada, validada de forma independiente y cerrada — ver `CHECKLIST_EJECUCION_Y_CIERRE.md` y `ACTA_CIERRE_SEC-T004.md`. Próxima acción pendiente: autorización del responsable para continuar con el resto de Fase 0 (SEC-T008, SEC-T012, SEC-T016, SEC-T021) y/o resolución de DEC-010 para desbloquear SEC-T001.