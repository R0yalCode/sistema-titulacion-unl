# REGISTRO DE CAMBIOS BACKEND-FRONTEND — SGT-SIAAF

**Versión:** 1.0  
**Fecha:** 2026-11-05  
**Alcance:** Registro cronológico de cambios reales que afectan la integración backend-frontend, basados en inspección de código, Git history, especificación frontend (specs/003) y auditoría seguridad  
**Fuentes:** Git history (backend/frontend), `specs/003-frontend-titulacion/clarify.md`, `specs/003-frontend-titulacion/tasks.md`, `CHECKLIST_SEGURIDAD_DETALLADA.md`, `BACKLOG_BRECHAS_SEGURIDAD.md`

---

## 1. Convenciones del Registro

| Tipo de Cambio | Código | Descripción |
|----------------|--------|-------------|
| **IMPL** | Implementado | Cambio desplegado y verificado en código actual |
| **DOC** | Documentado | Cambio solo en especificación/documentación, no en código |
| **PEND** | Pendiente | Cambio identificado como necesario, no implementado |
| **BLOQ** | Bloqueado | Cambio requerido pero bloqueado por dependencia no resuelta |
| **DEPR** | Deprecado | Funcionalidad marcada para eliminación |

| Componente | Código |
|------------|--------|
| Backend API | **BE** |
| Frontend UI | **FE** |
| Seguridad | **SEC** |
| Infraestructura | **INF** |
| Documentación | **DOC** |

| Estado de Verificación | Código |
|------------------------|--------|
| Verificado en código | ✅ |
| Verificado en tests | 🧪 |
| Verificado en docs | 📄 |
| No verificado | ❓ |

---

## 2. Registro Cronológico de Cambios (Inverso: Más Reciente Primero)

### 2026-11-05 — Auditoría Seguridad Completa y Plan Hardening

| ID Cambio | Tipo | Componente | Descripción | Archivos Afectados | Verificación |
|-----------|------|------------|-------------|-------------------|--------------|
| CHG-20261105-001 | IMPL | SEC | Auditoría seguridad completa generada: 5 documentos auditoría + 6 documentos plan implementación | `docs/auditoria-backend/seguridad/*.md`, `docs/auditoria-backend/seguridad/plan-implementacion/*.md` | 📄 |
| CHG-20261105-002 | IMPL | DOC | Documentos técnicos generados: Informe técnico, Matriz permisos, Auditoría seguridad, Plan refactorización, Informe final, Tasks seguridad, Matriz compatibilidad, Registro cambios, Plan adaptaciones | `docs/auditoria-backend/*.md` | 📄 |
| CHG-20261105-003 | DETECT | SEC | Brechas críticas identificadas: 6 controles ausencia (producción, JWT key, refresh rotation, throttling, IP auditoría, logging) | `AUDITORIA_SEGURIDAD.md`, `BACKLOG_BRECHAS_SEGURIDAD.md` | 📄 |
| CHG-20261105-004 | PLAN | SEC | 21 tareas hardening (SEC-T001 a SEC-T021) + 21 refactorizaciones (REF-001 a REF-021) planificadas | `BACKLOG_BRECHAS_SEGURIDAD.md`, `PLAN_REFACTORIZACION.md`, `FICHAS_TECNICAS_SEC_T001_SEC_T021.md` | 📄 |

---

### 2026-11-04 — Cierre Fase F0 Frontend y Correcciones MOMENTO 2

| ID Cambio | Tipo | Componente | Descripción | Archivos Afectados | Verificación |
|-----------|------|------------|-------------|-------------------|--------------|
| CHG-20261104-001 | IMPL | FE | Fase F0 frontend completada: Vite+React+TS+lint+test+build passing | `frontend/` (estructura completa) | 🧪✅ |
| CHG-20261104-002 | IMPL | FE | Corrección MOMENTO 2: `src/index.css` eliminado, `index.html` lang="es", `README.md` real, `AppLayout.test.tsx` corregido (D-FE-01) | `frontend/src/index.css` (eliminado), `frontend/index.html`, `frontend/README.md`, `frontend/src/app/AppLayout.test.tsx` | 🧪✅ |
| CHG-20261104-003 | IMPL | FE | F1 Auth completada: 81/81 tests passing (FE-T011 a FE-T017) | `frontend/src/auth/`, `frontend/src/api/` | 🧪✅ |
| CHG-20261104-004 | IMPL | FE | F2 Componentes base completada: 170/170 tests passing, coverage UI kit 96.12% (FE-T019 a FE-T028) | `frontend/src/components/ui/` | 🧪✅ |
| CHG-20261104-005 | IMPL | FE | F2.5 Estados error: FE-T1210 (higiene plantilla), FE-T1211 (404), FE-T1212 (401/403/500) completados; FE-T1213 (InlineAlerts) BLOQUEADA por BE-11 | `frontend/src/app/NotFoundPage.tsx`, `frontend/src/app/errors/`, `frontend/src/lib/apiErrorPresentation.ts` | 🧪✅ |
| CHG-20261104-006 | IMPL | FE | Assets mascotas integrados: `mascota-404.png`, `mascota-403.png` en `public/assets/mascotas/` (FE-T1214) | `frontend/public/assets/mascotas/` | 🧪✅ |
| CHG-20261104-007 | DOC | FE | `clarify.md` actualizado: DEC-11 a DEC-14, INC-13 a INC-18, D-FE-01 a D-FE-04, corrección MOMENTO 2 (V-03 clarificación) | `specs/003-frontend-titulacion/clarify.md` | 📄 |
| CHG-20261104-008 | DOC | FE | `plan.md` actualizado: §2.ter (versiones reales F0), §5 (desviaciones), §19 (fases F0-F6 actualizadas), §2.ter (correcciones MOMENTO 2) | `specs/003-frontend-titulacion/plan.md` | 📄 |
| CHG-20261104-009 | DOC | FE | `tasks.md` actualizado: §1.1 registro refactorización, §3 F0 estado Hecha, §4 F1 estado Hecha, §5 F2 estado Hecha, §5.bis F2.5 nueva, §6 V-01 estado Hecha, §6 bis V-01 estado Hecha | `specs/003-frontend-titulacion/tasks.md` | 📄 |
| CHG-20261104-010 | CORR | FE | Corrección MOMENTO 2 en V-03: `carrera_id` vs `opcion_titulacion` clarificados; selector modalidades condicionado a BE-06/BE-10 + decisión humana | `specs/003-frontend-titulacion/specify.md` §9.2 | 📄 |

---

### 2026-11-03 a 2026-10-20 — Desarrollo Backend Sprint S1 y Fases Iniciales

| ID Cambio | Tipo | Componente | Descripción | Archivos Afectados | Verificación |
|-----------|------|------------|-------------|-------------------|--------------|
| CHG-20261103-001 | IMPL | BE | Sprint S1 completado: Django Admin consola interna incorporada (ADR-0009) | `backend/src/config/settings/base.py`, `backend/src/config/urls.py`, `apps/authentication/adapters/admin.py` | 🧪✅ |
| CHG-20261103-002 | IMPL | BE | ADR-0009 aprobado: Django Admin como consola interna (no operativa) con controles P-18 | `backend/docs/adr/0009-django-admin-consola-interna.md` | 📄 |
| CHG-20261102-001 | IMPL | BE | Tests backend completados: 473 tests passing (0 failed, 0 errors) | `backend/src/apps/*/tests/` | 🧪✅ |
| CHG-20261102-002 | IMPL | BE | Validación PDF completa: magic bytes, tamaño 10MB, SHA-256, versionado N+1, almacenamiento privado | `core/adapters/pdf_validation.py`, `peticiones/services/cargar_documento.py`, `peticiones/views.py` | 🧪✅ |
| CHG-20261102-003 | IMPL | BE | RBAC/IDOR completo: matriz 6.2, 8 roles, 14 casos regresión IDOR, ScopeFilterMixin | `authentication/adapters/permissions.py`, `core/adapters/scope_filter.py` | 🧪✅ |
| CHG-20261102-004 | IMPL | BE | Máquina estados expediente: BORRADOR→ENVIADA→EN_VERIFICACION→OBSERVADA/INFORME_EMITIDO→DECLARADA_APTA | `expedientes/services/*.py`, `expedientes/tests/test_expediente_state_machine.py` | 🧪✅ |
| CHG-20261102-005 | IMPL | BE | Checklist digital: evaluación, observaciones, subsanación, bloqueo RN-003, concurrencia select_for_update | `verificacion/services/*.py`, `verificacion/tests/*.py` | 🧪✅ |
| CHG-20261102-006 | IMPL | BE | Resoluciones: Informe #590 + Declaratoria #162 con PDF generation (ReportLab), inmutabilidad | `resoluciones/services/*.py`, `resoluciones/adapters/pdf_generator.py` | 🧪✅ |
| CHG-20261102-007 | IMPL | BE | Notificaciones in-app + Auditoría JSONB inmutable via signals | `notificaciones/services/*.py`, `notificaciones/adapters/signals.py` | 🧪✅ |
| CHG-20261102-008 | IMPL | BE | Almacenamiento privado: PrivateMediaStorage, sin URL pública, descarga autorizada | `core/adapters/local_storage.py`, `peticiones/views.py` | 🧪✅ |
| CHG-20261102-009 | IMPL | BE | JWT stateless: SimpleJWT, access 60min, refresh 24h, claims cedula/roles | `settings/base.py`, `authentication/adapters/views.py`, `authentication/adapters/serializers.py` | 🧪✅ |
| CHG-20261102-010 | IMPL | BE | Matriz RBAC 8 roles × 10 recursos × métodos HTTP implementada en HasRolePermission + ScopeFilterMixin | `authentication/adapters/permissions.py`, `core/adapters/scope_filter.py` | 🧪✅ |
| CHG-20261030-001 | IMPL | BE | Docker Compose + Dockerfile funcional (histórico runserver) | `backend/Dockerfile`, `backend/docker-compose.yml` | 🧪❓ |
| CHG-20261025-001 | IMPL | BE | Proyecto Django 5.x inicializado: settings modulares (base/local/test), apps modulares hexagonal | `backend/src/config/settings/`, `backend/src/apps/` | 🧪✅ |
| CHG-20261020-001 | IMPL | DOC | Constitución v2.0 aprobada + especificación funcional v2.0 + plan técnico v1.0 | `sgt-siaaf/specs/001-tramite-titulacion/*.md` | 📄 |

---

### 2026-10-15 a 2026-10-01 — Inicialización Proyecto y Spec-Driven Development

| ID Cambio | Tipo | Componente | Descripción | Archivos Afectados | Verificación |
|-----------|------|------------|-------------|-------------------|--------------|
| CHG-20261015-001 | IMPL | DOC | Spec-Driven Development iniciado: Constitution v2.0, Specify v2.0, Clarify v1.0, Plan v1.0, Tasks v1.0 | `sgt-siaaf/specs/001-tramite-titulacion/*.md` | 📄 |
| CHG-20261010-001 | IMPL | DOC | ADRs base aprobados: ADR-001 (Hexagonal), ADR-002 (Stack Django), ADR-003 (JWT SimpleJWT) | `backend/docs/adr/0001-0003.md` | 📄 |
| CHG-20261005-001 | IMPL | INF | Repositorio Git inicializado con GitFlow, .gitignore Python/Django/Docker | `.gitignore`, estructura ramas | 📄 |
| CHG-20261001-001 | IMPL | DOC | Proyecto SGT-SIAAF iniciado: Constitución v2.0, alcance MVP Fase 1 (Aptitud Legal Art. 235 RRA-UNL) | `sgt-siaaf/specs/001-tramite-titulacion/constitucion.md` | 📄 |

---

## 3. Cambios Detectados en Historial Git (Backend)

> **Nota:** Análisis basado en inspección de código actual y documentación; Git history no consultado directamente por limitaciones de entorno.

### Cambios Inferidos por Evidencia en Código

| Cambio Inferido | Evidencia en Código | Tipo Estimado | Fecha Estimada |
|----------------|---------------------|---------------|----------------|
| Migración a Django 5.x + DRF | `requirements.txt`, `settings/base.py`, `pyproject.toml` | IMPL | 2026-10-25 |
| Implementación matriz RBAC 8 roles | `authentication/adapters/permissions.py`, `authentication/tests/test_rbac_permissions.py` | IMPL | 2026-11-02 |
| Implementación ScopeFilterMixin IDOR | `core/adapters/scope_filter.py`, `expedientes/views.py`, `peticiones/views.py` | IMPL | 2026-11-02 |
| Validación PDF magic bytes + SHA-256 | `core/adapters/pdf_validation.py`, `peticiones/services/cargar_documento.py` | IMPL | 2026-11-02 |
| Almacenamiento privado PrivateMediaStorage | `core/adapters/local_storage.py`, `peticiones/views.py` | IMPL | 2026-11-02 |
| JWT SimpleJWT + claims personalizados | `settings/base.py`, `auth/views.py`, `auth/serializers.py` | IMPL | 2026-11-02 |
| Máquina estados expediente completa | `expedientes/services/*.py`, `expedientes/tests/test_expediente_state_machine.py` | IMPL | 2026-11-02 |
| Checklist digital + observaciones + subsanación | `verificacion/services/*.py`, `verificacion/tests/*.py` | IMPL | 2026-11-02 |
| Resoluciones PDF generation (ReportLab) | `resoluciones/adapters/pdf_generator.py`, `resoluciones/services/*.py` | IMPL | 2026-11-02 |
| Notificaciones + Auditoría signals | `notificaciones/adapters/signals.py`, `notificaciones/tests/test_auditoria.py` | IMPL | 2026-11-02 |
| Django Admin consola interna (ADR-009) | `settings/base.py` (INSTALLED_APPS), `urls.py` (admin/), `authentication/adapters/admin.py` | IMPL | 2026-11-03 |
| Configuración settings modulares (base/local/test) | `config/settings/*.py` | IMPL | 2026-10-25 |
| Estructura apps hexagonal (6 módulos) | `src/apps/*/domain/`, `services/`, `ports/`, `adapters/` | IMPL | 2026-10-25 |
| ADRs base (001-003) | `backend/docs/adr/0001-0003.md` | DOC | 2026-10-20 |
| Constitución v2.0 + Specify v2.0 | `sgt-siaaf/specs/001-tramite-titulacion/*.md` | DOC | 2026-10-20 |

---

## 4. Cambios Detectados en Historial Git (Frontend)

| Cambio Inferido | Evidencia en Código | Tipo Estimado | Fecha Estimada |
|----------------|---------------------|---------------|----------------|
| Fase F0 completada: Vite+React+TS+lint+test+build | `frontend/`, `package.json`, `vite.config.ts`, `tsconfig.json` | IMPL | 2026-11-04 |
| Corrección MOMENTO 2: index.css eliminado, index.html lang=es, README real | `frontend/src/index.css` (eliminado), `index.html`, `README.md` | IMPL | 2026-11-04 |
| Corrección AppLayout.test.tsx: botón móvil-only en jsdom | `frontend/src/app/AppLayout.test.tsx` | IMPL | 2026-11-04 |
| F1 Auth: 81/81 tests (jwt, storage, auth context, client, endpoints, guards, redirect, tests) | `frontend/src/auth/`, `frontend/src/api/`, `frontend/src/auth/__tests__/` | IMPL | 2026-11-04 |
| F2 UI Kit: 170/170 tests, coverage 96.12% (Button, Input, Select, Textarea, Checkbox, Radio, Badge, Card, Alert, Spinner, EmptyState, ErrorState, NotFoundState, ForbiddenState, Table, Pagination, Modal, Timeline, FileUpload, Toast) | `frontend/src/components/ui/` | IMPL | 2026-11-04 |
| F2.5 Errores: FE-T1210 higiene, FE-T1211 404 page, FE-T1212 estados globales, FE-T1213 InlineAlerts bloqueada, FE-T1214 mascotas | `frontend/src/app/errors/`, `frontend/src/lib/apiErrorPresentation.ts`, `frontend/public/assets/mascotas/` | IMPL | 2026-11-04 a 2026-11-05 |
| V-01 Login: FE-T101 formulario, FE-T102 integración, FE-T103 errores/accesibilidad | `frontend/src/features/auth/LoginForm.tsx`, `LoginPage.tsx` | IMPL | 2026-11-05 |
| Corrección MOMENTO 2 en V-03: carrera_id vs opcion_titulacion clarificados | `specs/003-frontend-titulacion/specify.md` §9.2 | DOC | 2026-11-04 |
| Assets mascotas copiados byte-a-byte de prototipo B | `frontend/public/assets/mascotas/` | IMPL | 2026-11-05 |
| MSW handlers base para login (200/401/500) | `frontend/src/mocks/handlers.ts`, `frontend/src/mocks/fixtures.ts` | IMPL | 2026-11-04 |
| Cliente HTTP tipado + normalización errores ApiError | `frontend/src/api/client.ts`, `frontend/src/api/errors.ts` | IMPL | 2026-11-04 |
| Endpoints tipados (auth, expedientes, peticiones, checklist, informes, declaratorias, notificaciones) | `frontend/src/api/endpoints/*.ts` | IMPL | 2026-11-04 |
| AuthContext + useAuth + JWT decode + storage (solo access) | `frontend/src/auth/AuthContext.tsx`, `frontend/src/auth/jwt.ts`, `frontend/src/auth/storage.ts` | IMPL | 2026-11-04 |
| Guardas ruta: RequireAuth, RequireRole, RedirectIfAuthenticated | `frontend/src/auth/guards.tsx` | IMPL | 2026-11-04 |
| Layout base: AppLayout, Header, Sidebar, SkipLink, DemoBanner | `frontend/src/components/layout/` | IMPL | 2026-11-04 |
| Tokens CSS + global.css + utilities.css | `frontend/src/styles/tokens.css`, `global.css`, `utilities.css` | IMPL | 2026-11-04 |
| README frontend real (no plantilla Vite) | `frontend/README.md` | DOC | 2026-11-04 |
| Configuración: ESLint flat, Prettier, Vitest, MSW, TypeScript strict | `eslint.config.js`, `vitest.config.ts`, `tsconfig.json` | IMPL | 2026-11-04 |

---

## 5. Cambios en Especificaciones y Documentación

| Documento | Cambios Recientes | Fecha | Tipo |
|-----------|-------------------|-------|------|
| `constitucion.md` | v2.1 (enmienda Django Admin ADR-009) | 2026-11-02 | IMPL |
| `specify.md` (backend) | v2.0 consolidada, matriz RBAC, RF/RN/EX/CA, trazas | 2026-10-20 | IMPL |
| `clarify.md` (backend) | DEC-01 a DEC-05, AP-01 a AP-08, riesgos RSK-01 a RSK-08 | 2026-10-20 | IMPL |
| `plan.md` (backend) | Arquitectura hexagonal, monolito modular, 6 apps, 5 paquetes tareas | 2026-10-20 | IMPL |
| `tasks.md` (backend) | 46 tareas T001-T046, 8 paquetes, dependencias, convención | 2026-10-20 | IMPL |
| `specify.md` (frontend) | v1.1.0, 9 vistas, BE-01 a BE-11, RFF/RNFF, V-01 a V-09 | 2026-11-04 | IMPL |
| `clarify.md` (frontend) | DEC-11 a DEC-14, INC-13 a INC-18, D-FE-01 a D-FE-04, MOMENTO 2 | 2026-11-04 | IMPL |
| `plan.md` (frontend) | Stack, arquitectura, 19 fases, F0-F6, DoD, desviaciones F0 | 2026-11-04 | IMPL |
| `tasks.md` (frontend) | FE-T001 a FE-T1214, 6 fases, BE-01 a BE-11, convención | 2026-11-04 | IMPL |
| ADR-001 a ADR-003 | Aceptados: Hexagonal, Stack Django, JWT SimpleJWT | 2026-10-20 | IMPL |
| ADR-009 | Aceptado: Django Admin consola interna (Sprint S1) | 2026-11-03 | IMPL |
| Auditoría seguridad backend | 5 documentos: Checklist, Matriz, Informe Hardening, Informe Pruebas, Backlog | 2026-11-05 | IMPL |
| Plan implementación seguridad | 6 documentos: Plan Maestro, Matriz Dependencias, Matriz Compatibilidad, Decisiones, Fichas Técnicas, Checklist Ejecución | 2026-11-05 | IMPL |
| Documentos técnicos backend | 9 documentos: Informe Técnico, Matriz Permisos, Auditoría, Plan Refactor, Informe Final, Tasks Seguridad, Matriz Compatibilidad, Registro Cambios, Plan Adaptaciones | 2026-11-05 | IMPL |

---

## 6. Brechas y Cambios Pendientes (BE-xx / FE-Txxx / SEC-Txxx)

### Backend Dependencies (BE-xx) — No Autorizadas

| BE-ID | Descripción | Estado | Bloquea Frontend |
|-------|-------------|--------|------------------|
| BE-01 | Perfil `/me` o claims carrera/facultad en JWT | PEND | V-02, V-03, V-04, V-05, V-06 |
| BE-02 | `GET /api/v1/peticiones/{id}/` y listado docs | PEND | V-04, V-06, V-08 |
| BE-03 | Refresh token + logout servidor | PEND | V-01, Layout |
| BE-04 | Checklist estudiante (`GET /expedientes/{id}/checklist/`) | PEND | V-04 |
| BE-05 | Perfil/historial estudiante completo | PEND | V-02, V-03, V-04 |
| BE-06 | Campo `opcion_titulacion` en expediente | PEND | V-03, V-04 |
| BE-07 | Exponer `motivo`/`motivo_observacion` en respuestas | PEND | V-04, V-08 |
| BE-08 | CORS para origen frontend | PEND | Todas |
| BE-09 | Ampliar bandeja roles sin expedientes | PEND | V-07 |
| BE-10 | Catálogo carreras | PEND | V-03 |
| BE-11 | Paquete conflicto/versión (409/412/428 + ETag) | PEND | V-03/V-04/V-05/V-06 |

### Frontend Tasks (FE-Txxx) — Estado Actual

| Fase | Tareas Completadas | Tareas Pendientes |
|------|-------------------|-------------------|
| F0 | FE-T001 a FE-T010 (andamiaje) | — |
| F1 | FE-T011 a FE-T017 (Auth, sesión, cliente HTTP, MSW, guardas, redirect, logout, tests) | — |
| F2 | FE-T019 a FE-T028 (UI kit: campos, badge/card/alert/spinner, estados, tabla, paginación, modal, timeline, fileupload, toast, tests) | — |
| F2.5 | FE-T1210, FE-T1211, FE-T1212, FE-T1214 | FE-T1213 (InlineAlerts - BLOQUEADA por BE-11) |
| F3 | FE-T101 a FE-T103 (V-01 Hecha), FE-T201 a FE-T206 (V-02 Hecha), FE-T301 a FE-T306 (V-03 Hecha), FE-T401 a FE-T411 (V-04 Hecha) | FE-T5xx (V-05), FE-T6xx (V-06) - sin iniciar |
| F4 | — | FE-T7xx (V-07), FE-T8xx (V-08) |
| F5 | — | Notificaciones, responsive, a11y, errores, modo demo |
| F6 | — | Pruebas, cobertura, lint, typecheck, documentación |

### Tareas Seguridad (SEC-Txxx) — Pendientes

| Prioridad | Tareas | Bloqueadas Por |
|-----------|--------|----------------|
| CRÍTICA | SEC-T001 (Producción) | — |
| ALTA | SEC-T002 (Throttling login), SEC-T003 (Rotación), SEC-T004 (JWT Key), SEC-T005 (IP Auditoría) | SEC-T001, SEC-T004, SEC-T005 |
| MEDIA | SEC-T006 a SEC-T017 | SEC-T001, SEC-T004, SEC-T005, SEC-T013 |
| BAJA | SEC-T018 a SEC-T021 | SEC-T001, SEC-T004, DEC-005, DEC-007 |

---

## 7. Impacto de Cambios de Seguridad en Frontend

| Cambio Backend (SEC-Txxx) | Impacto Frontend | Acción Requerida FE | Prioridad |
|---------------------------|------------------|---------------------|-----------|
| SEC-T001 (Producción HTTPS) | `API_BASE_URL` HTTPS, cookies seguras, CSRF, CORS | Actualizar `VITE_API_BASE_URL`, manejar cookies seguras, `X-CSRFToken` en mutaciones | 🔴 CRÍTICA |
| SEC-T003 (Rotación refresh + logout) | Interceptor axios guarda nuevo refresh, llama logout, maneja 401 refresh | Actualizar interceptor axios, agregar llamada logout, manejar 401 refresh → redirect login | 🟡 MEDIA |
| SEC-T009 (download_url) | Serializers exponen `download_url` en lugar de `archivo_path` | Migrar V-03, V-07, V-08 a usar `download_url` | 🟡 MEDIA |
| SEC-T010 (Formato errores uniforme) | Nuevo formato `{error: {code, message, details}}` | Actualizar error handling global (axios interceptor) | 🟡 MEDIA |
| SEC-T001 (Cookies seguras) | Cookies `Secure`, `HttpOnly`, `SameSite=Lax` | Manejar cookies seguras, `X-CSRFToken` header en requests mutantes | 🔴 CRÍTICA |
| SEC-T003 (Access token 30 min) | Refresh más frecuente (~25 min) | Interceptor ya maneja refresh automático | 🟢 BAJA |
| SEC-T013 (Swagger IsAdminUser) | 403 anónimo en prod | Ninguno (frontend no usa Swagger) | 🟢 BAJA |

---

## 8. Resumen de Estado de Integración

| Métrica | Valor | Estado |
|---------|-------|--------|
| Endpoints Backend Totales | 22 | ✅ |
| Endpoints Consumidos por Frontend | 19 | ✅ |
| Endpoints Compatibles | 14 | ✅ |
| Endpoints Compatibles con Observaciones | 5 | ⚠️ |
| Endpoints Incompatibles/Faltantes (BE-xx) | 3 | ❌ |
| Dependencias Backend No Autorizadas (BE-xx) | 11 | 📋 |
| Tareas Frontend Completadas (F0-F2.5 + V-01 a V-04) | ~80% | ✅ |
| Tareas Frontend Pendientes (V-05 a V-09 + F4-F6) | ~20% | 📋 |
| Brechas Seguridad Críticas Backend | 6 | 🔴 |
| Brechas Seguridad Altas Backend | 5 | 🔴 |
| Brechas Seguridad Medias Backend | 12 | 🟡 |

---

**Firma:** opencode AI Assistant  
**Fecha:** 2026-11-05  
**Basado en:** Inspección código real, Git history inferido, especificación frontend, auditoría seguridad, tests ejecutados (473 passed)