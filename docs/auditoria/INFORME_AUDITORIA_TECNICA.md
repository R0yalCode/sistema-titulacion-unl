# INFORME DE AUDITORÍA TÉCNICA INTEGRAL — SGT-SIAAF

| Campo | Valor |
|---|---|
| Proyecto | SGT-SIAAF — Sistema de Gestión del Trámite de Titulación (UNL / FEIRNNR) |
| Fecha de auditoría | 05-11-2026 |
| Alcance | Backend Django/DRF, frontend React/Vite, base de datos, APIs, seguridad, pruebas, infraestructura, documentación |
| Método | Auditoría basada en evidencia: inspección de código, ejecución real de suites de pruebas, verificación de contratos OpenAPI |
| Naturaleza | Simulación académica funcional (sin validez legal), según Constitución del proyecto |
| Versión del informe | 1.0 |

---

## 1. RESUMEN EJECUTIVO

SGT-SIAAF es un sistema de dos componentes (backend Django 5.2/DRF con arquitectura hexagonal y frontend React 19/Vite) que automatiza el trámite de **Declaratoria de Aptitud Legal (Art. 235 del RRA-UNL)**: solicitud del estudiante → envío formal → verificación documental por Secretaría-Abogacía → observaciones y subsanaciones → informe de aptitud (Providencia 590) → declaratoria (Memorando 162).

**Estado real verificado:**

- **Backend: IMPLEMENTADO Y VERIFICADO** para el flujo completo FL-01→FL-05 (crear expediente, enviar, verificar/observar, subsanar, emitir informe y declaratoria). La suite completa de pruebas ejecutada durante esta auditoría arrojó **526 pruebas: 526 aprobadas, 0 fallos, 0 errores**, con **cobertura de código del 93 %** (medida con `pytest --cov`, en contra del 95 % que declara el README raíz).
- **Contrato OpenAPI: VÁLIDO Y SINCRONIZADO.** El archivo `backend/openapi.yaml` es generado por drf-spectacular, es byte a byte idéntico a `backend/contracts/openapi.yaml`, y sus 17 operaciones coinciden exactamente con las rutas registradas en `src/config/urls.py`. Se regeneró durante la auditoría y el resultado fue idéntico (0 errores, 2 advertencias menores de spectacular).
- **Frontend: IMPLEMENTADO PARCIALMENTE (fase F0–F1).** Andamiaje, enrutamiento con las 10 rutas oficiales, autenticación JWT, cliente HTTP con manejo de errores y un design system de ~24 componentes con pruebas de accesibilidad (axe) están completos y probados (198 pruebas, 43 archivos, todas aprobadas; lint y typecheck sin errores; build exitoso). Sin embargo, **las 9 vistas de negocio (V-01…V-09) son stubs de una línea** ("Vista pendiente de implementación") y solo se consume 1 endpoint real (`POST /api/v1/auth/token/`).
- **Seguridad: RBAC sólido con brechas de endurecimiento.** La matriz RBAC de mundo cerrado + el filtrado por ámbito ORM (`ScopeFilterMixin`) mitigan IDOR (verificado con 13 pruebas específicas que exigen 404 ante objetos ajenos). Faltan: limitación de tasa (throttling), endurecimiento HTTPS/HSTS para producción, y el contenedor Docker ejecuta por defecto `DEBUG=1` con `runserver`.
- **Madurez global: MVP de backend funcional y probado; frontend en fase temprana.** El sistema **es demostrable de extremo a extremo solo vía API** (Swagger UI, pytest E2E), no vía interfaz de usuario.

### Dictamen de madurez

| Componente | Nivel de madurez | Justificación |
|---|---|---|
| Backend (API) | **MVP funcional verificado** | 17 operaciones, flujo completo probado con 526 pruebas verdes y 93 % de cobertura |
| Base de datos | **MVP funcional verificado** | 14 modelos, migraciones consistentes (`makemigrations --check` sin cambios), índices y constraints declarados |
| Seguridad de API | **Parcial** | RBAC + IDOR verificados; sin throttling ni hardening de producción |
| Infraestructura | **Solo desarrollo** | Docker Compose funcional pero con `DEBUG=1` y `runserver`; sin CI/CD |
| Frontend | **Andamiaje completo, vistas pendientes** | 0 de 9 vistas de negocio implementadas |
| Documentación | **Buena en specs, deficiente en READMEs** | Specs densas y trazables; `backend/README.md` es el README upstream de gitleaks |

**¿Está preparado para una demostración funcional?** Sí, **como demostración de API** (flujo completo con Swagger UI `/api/v1/docs/` o mediante el E2E `tests/e2e/test_full_workflow.py`). **No** como demostración de producto con interfaz de usuario: las 9 vistas son stubs. Ver §16.

---

## 2. ALCANCE DE LA AUDITORÍA

- **Incluido**: `backend/` (código, modelos, servicios, APIs, seguridad, pruebas, migraciones, OpenAPI), `frontend/` (código, rutas, auth, design system, pruebas), `docker-compose.yml`/`Dockerfile`/`nginx/`, documentación (`specs/001`, `specs/003`, `auditoria/`, `docs/`, READMEs).
- **Excluido**: prototipos HTML/CSS/JS (`SGT_SIAAF_Prototipo_*`, referencia no normativa), `diseno-ui/` (referencia visual), scripts auxiliares de verificación en la raíz (`audit_*.py`, `verify_*.py`).
- **Restricción metodológica**: auditoría de solo lectura. No se modificó código, modelos, migraciones ni contratos. Las dependencias del backend se instalaron en un entorno temporal fuera del repositorio (`/tmp/opencode/be-deps`) exclusivamente para poder ejecutar las pruebas; no se instaló nada dentro del proyecto.

---

## 3. METODOLOGÍA

1. **Inspección estática** del árbol completo del repositorio (backend, frontend, specs, docs, auditorías previas).
2. **Trazabilidad de código**: verificación directa de modelos, servicios, vistas, URLs, permisos y settings, con referencia `archivo:línea`.
3. **Ejecución real de verificaciones** (evidencia reproducible; comandos documentados en §9):

| Verificación | Comando | Resultado |
|---|---|---|
| Suite backend (configurada) | `pytest -q` (settings `config.settings.test`, SQLite en memoria) | **473 passed**, 15 warnings |
| Suite backend extendida (excluida por `testpaths`) | `pytest -q src/core src/core/adapters/tests tests/e2e` | **53 passed** |
| Cobertura | `pytest --cov=src --cov-report=term` | **93 %** total |
| Migraciones | `manage.py makemigrations --check --dry-run` | "No changes detected" |
| OpenAPI regenerado | `manage.py spectacular --file …` + `diff` | Idéntico a `openapi.yaml` y `contracts/openapi.yaml` |
| Lint backend | `flake8 src --count` | 854 hallazgos (estilo; ver §8) |
| Lint frontend | `npm run lint` | Sin errores |
| Typecheck frontend | `npm run typecheck` | Sin errores |
| Tests frontend | `npm run test` | **198 passed** (43 archivos) |
| Build frontend | `npm run build` | Exitoso (~296 ms) |

4. **Contraste documentación ↔ código**: los resultados de auditorías previas (`auditoria/01…08`, sprint S1) se revalidaron contra el código actual (los hallazgos SEC-01/SEC-02/SEC-03 del sprint S1 se verificaron punto por punto; ver §8).

---

## 4. ARQUITECTURA ENCONTRADA

### 4.1 Arquitectura general

Monolito modular con **arquitectura hexagonal** (puertos y adaptadores), conforme a ADR-0001 (`backend/docs/adr/0001-arquitectura-hexagonal-monolito-modular.md`):

```
backend/src/
├── apps/<dominio>/
│   ├── domain/        # dominio puro (p. ej. plazo_calculator.py)
│   ├── services/      # casos de uso (lógica de negocio transaccional)
│   └── adapters/      # Django: models, serializers, views, admin, migrations
├── core/              # infraestructura compartida (ports/adapters)
│   ├── ports/         # ISGALegacyPort (contrato abstracto SGA)
│   └── adapters/      # mock_sga, local_storage, pdf_validation, scope_filter
└── config/            # settings (base/local/test), urls, wsgi/asgi
```

- **Separación de responsabilidades**: correcta y verificable. La lógica de negocio está centralizada en `services/*.py` (no en las vistas); las vistas son delgadas y delegan. Excepción parcial: los serializers de entrada de `resoluciones` están definidos inline en las vistas (`resoluciones/adapters/views.py:75-104,157-187`).
- **Patrones**: estado explícito con máquina de estados del expediente (7 estados, probada en `test_expediente_state_machine.py`), bloqueo pesimista `select_for_update()` en todas las transacciones de negocio, repositorio de almacenamiento privado (`PrivateMediaStorage`), adaptador mock sobre puerto (`ISGALegacyPort` → `MockSGAAdapter` con dataclasses frozen, RN-005).
- **Comunicación**: SPA React ↔ API REST `/api/v1/` con JWT Bearer (SimpleJWT); sin WebSocket ni tareas asíncronas — las notificaciones se despachan **sincrónicamente in-process** (`notificaciones/services/notification_service.py:1-5`).
- **Integraciones externas**: ninguna real. El SGA/SIAAF institucional se simula con `mock_sga.py` + fixture `sga_mock_records.json` (5 récords, solo lectura, promedio inmutable). FirmaEC se simula como "PDF firmado ya cargado" (DEC-04).
- **Gestión de configuración**: `django-environ` lee `.env`; `SECRET_KEY` sin valor por defecto (falla si falta, correcto); `DEBUG` por defecto `False`. Settings separados: `base.py`, `local.py` (solo `DEBUG=True`), `test.py` (SQLite en memoria + MD5 hasher). **No existe `production.py`**.
- **Manejo de excepciones**: excepciones de dominio mapeadas a códigos HTTP explícitos (400/403/422) con `code` DRF (p. ej. `requisitos_incompletos` → 422 en `expedientes/adapters/views.py:43-48`); `ErrorBoundary` en frontend.
- **Logs**: **no hay configuración de `LOGGING`** en `settings/base.py`. Además existen `print()` de depuración en código de producción (`verificacion/services/evaluar_checklist.py:164,170`).

### 4.2 Frontend

SPA React 19 + TypeScript 5.9 (modo estricto) + Vite 8 + TanStack Query 5 + react-router-dom 7. Estructura `src/{app,api,auth,components,features,lib,styles,types,mocks,test}` con alias `@/`. Regla arquitectónica ESLint que impide imports entre features. Design system con tokens CSS (`styles/tokens.css`) y componentes con CSS Modules.

### 4.3 Coherencia documentación ↔ código

- ADR-0001/0002/0003/0009 (backend) coinciden con la implementación.
- Los ADRs 0004–0008 declarados como "Aceptados" en `specs/001/plan.md` **no tienen archivo físico** (solo existen 0001, 0002, 0003, 0009).
- Los ADRs a nivel spec (`specs/001/adr/ADR-001-arquitectura.md`, `ADR-002-limites-modulares.md`) están **vacíos (0 bytes)**.
- Existen **dos copias divergentes de la Constitución**: `.specify/memory/constitution.md` (v2.0) vs `specs/001-tramite-titulacion/constitucion.md` (v2.1, con P-18); 85 líneas de diferencia.
- `docs/frontend/FRONTEND_IMPLEMENTATION_PLAN.md` está **vacío (0 bytes)**.
- `backend/README.md` es el README upstream de **gitleaks**, no documenta el proyecto.
- README raíz declara "19 endpoints" (reales: 17) y "cobertura 95 %" (medida: 93 %).

---

## 5. AUDITORÍA DEL BACKEND

### 5.1 Aplicaciones y módulos

| App | Responsabilidad | Modelos | Servicios (casos de uso) | Endpoints | Pruebas |
|---|---|---|---|---|---|
| `authentication` | Usuario institucional (UUID, cédula), roles, JWT con claims, matriz RBAC | User, Role, UserRole | — (login directo en vista) | 1 | 28 |
| `expedientes` | Ciclo de vida del expediente, envío formal, bandeja por rol, plazos laborables | ExpedienteTitulacion, HistorialEstado | crear_expediente, enviar_expediente, plazo_calculator (dominio puro) | 5 | 73 |
| `peticiones` | Catálogo documental (Art. 235), peticiones por expediente, documentos PDF versionados | CatalogoDocumental, PeticionDocumental, DocumentoEntregado | solicitar_emision, cargar_documento | 4 | 85 |
| `verificacion` | Checklist del jurista, observaciones accionables, subsanación, completitud (RN-003) | ChecklistVerification, ObservacionAccionable | evaluar_checklist, registrar_observacion, subsanar_requisito, validar_checklist_completo | 3 | 72 |
| `resoluciones` | Informe de aptitud (Providencia 590) y declaratoria (Memorando 162) con PDF ReportLab | InformeAptitud, DeclaratoriaAptitud | emitir_informe, declarar_aptitud, pdf_generator | 2 | 113 |
| `notificaciones` | Notificaciones in-app y bitácora de auditoría JSONB con signals | NotificacionInterna, EventoAuditoria | notification_service (despacho sincrónico) | 2 | 71 |
| `core` (infra) | Almacenamiento privado, validación PDF, filtrado por ámbito, mock SGA | — | — | — | 49 (+22) |

**Total: 14 modelos, 13 servicios/casos de uso, 17 operaciones API, 526 pruebas.**

Elementos sin uso (código muerto): `PeticionDocumentalViewSet` (`peticiones/adapters/views.py:285`) y `ObservacionViewSet` (`verificacion/adapters/views.py:169`) **no están ruteados**; este último además usa el recurso RBAC `observaciones`, que no existe en la matriz (denegaría todo). Los eventos de auditoría `SUBSANACION_REALIZADA`, `EXPEDIENTE_ENVIADO` y `EXPEDIENTE_CANCELADO` del enum (`notificaciones/adapters/models.py:71-79`) no se generan desde ningún servicio o signal. `_get_current_request()` (`notificaciones/adapters/signals.py:32-36`) siempre devuelve `None`, por lo que la IP de `EventoAuditoria` queda siempre vacía.

### 5.2 Modelos y base de datos

Entidades y relaciones clave (evidencia: `apps/*/adapters/models.py`):

- `User` (UUID, `cedula` único, `carrera_id`/`facultad_id` UUID indexados) — `authentication/adapters/models.py:86-110`.
- `UserRole` con UniqueConstraint `(user, role)` (models.py:57-59); `Role.name` con choices cerrados de 8 roles (models.py:7-25).
- `ExpedienteTitulacion`: `numero_expediente` único (`EXP-YYYY-NNNN`), `numero_providencia` único indexado, FK PROTECT a `estudiante`, `estado` con 7 choices e índice, `fecha_limite_atencion`, `dias_laborables_acumulados`, `activa`; índice `idx_exped_carrera` (models.py:32-68).
- `HistorialEstado` (bitácora de transiciones, FK CASCADE, índice propio) (models.py:71-99).
- `CatalogoDocumental` (código único, fase FASE_1/2/3, `rol_emisor_sugerido` con choices de roles) — sembrado por migración `0002_catalogo_base_art235.py` con los 5 requisitos del Art. 235 RRA.
- `PeticionDocumental`: UniqueConstraint `(expediente, requisito)` (models.py:90-95); estados `PENDIENTE→SOLICITADO→CARGADO→VERIFICADO/OBSERVADO` (+`LEGALIZADO`, `CANCELADA`).
- `DocumentoEntregado`: versionado N+1 con UniqueConstraint `(peticion, version)` (models.py:135-140), `hash_sha256`, `es_vigente` indexado.
- `ChecklistVerification`: UniqueConstraint `(expediente, requisito)`; `ObservacionAccionable` con `resuelta` indexada.
- `InformeAptitud` y `DeclaratoriaAptitud`: **OneToOne** con `ExpedienteTitulacion` (PROTECT), números únicos (`PROV-590-YYYY-NNNN`, `MEM-162-YYYY-NNNN`).
- `NotificacionInterna` (4 índices compuestos) y `EventoAuditoria` (JSONB `detalles`, 4 índices temporales).

**Evaluación**: la normalización es adecuada; la integridad referencial usa PROTECT donde corresponde (no se borran usuarios con expedientes); los índices cubren los filtros de bandeja y auditoría. Riesgo N+1: bajo — los serializers usan campos planos y las bandejas pagan; no se detectaron loops de consulta en servicios. Campos sensibles: `DocumentoEntregado.archivo_path` y hashes — almacenamiento privado sin URL pública (`PrivateMediaStorage.url()` lanza `NotImplementedError`, `core/adapters/local_storage.py:30-35`).

**Migraciones**: 13 archivos en 6 apps; `makemigrations --check --dry-run` → sin cambios pendientes. Los modelos representan correctamente el trámite definido en la Constitución y `specs/001/specify.md` (§7, 11 entidades conceptuales; 14 físicas por desdoblamiento de catálogo/checklist/auditoría).

### 5.3 Lógica de negocio

Reglas verificadas (centralizadas en servicios, con pruebas):

| Regla | Implementación | Evidencia |
|---|---|---|
| Un expediente activo por estudiante | `select_for_update()` + validación | `expedientes/services/crear_expediente.py:50-60` |
| Exactamente 5 requisitos base Art. 235 FASE_1 | validación al crear | `crear_expediente.py:61-73` |
| Numeración correlativa anual (EXP/PROV/PROV-590/MEM-162) | generadores por servicio | `crear_expediente.py:32-45`, `enviar_expediente.py:45-61`, `emitir_informe.py:29-46` |
| Transición BORRADOR→ENVIADA solo con requisitos en firme | estados bloqueados `PENDIENTE/SOLICITADO/OBSERVADO/CANCELADA` | `enviar_expediente.py:29-34,83-114` |
| Plazo de 8 días hábiles (COA Art. 160 / AP-01), con pausa al observar y reanudación al subsanar | `PlazoLaboralCalculator` (dominio puro) | `expedientes/domain/plazo_calculator.py:23-113` |
| Checklist 100 % VERIFICADO antes del informe (RN-003) | `validar_checklist_completo.execute` | `verificacion/services/validar_checklist_completo.py` |
| Motivo obligatorio si OBSERVADO | validación serializer + servicio | `verificacion/adapters/serializers.py:56-65` |
| Subsanación con versionado N+1 y cierre de observación | servicio transaccional | `verificacion/services/subsanar_requisito.py:84-223` |
| Rechazo de dictamen NO APTO en informe | validación | `resoluciones/services/emitir_informe.py:159-164` |
| Restricciones por rol en cada caso de uso | verificación explícita por servicio | p. ej. `evaluar_checklist.py:137-139`, `declarar_aptitud.py:125-128` |

**Defecto detectado (N-1, confirmado)**: en `emitir_informe.py:203-211`, `HistorialEstado.estado_anterior` se asigna **después** de mutar y guardar `expediente.estado`, por lo que el historial registra `estado_anterior == estado_nuevo` en la transición a `INFORME_EMITIDO`. Impacto: trazabilidad incompleta de ese paso. Severidad P2.

**Discrepancia de permisos**: `declarar_aptitud.py:125-128` admite roles `DECANO | ANALISTA_APOYO`, mientras la matriz RBAC (`permissions.py:106-110`) solo concede `declaratorias` a DECANO. En la práctica el RBAC gana (la vista deniega a ANALISTA_APOYO antes del servicio), pero es una inconsistencia latente. P3.

### 5.4 Inventario completo de APIs REST

Fuente: `src/config/urls.py:26-121` (rutas reales) contrastado con `backend/openapi.yaml` (contrato generado). **17 operaciones API + 3 endpoints de documentación + Django Admin.** Sin router DRF: todas las rutas son `path()` explícitos.

| # | Método | Ruta | Operación | App | Permisos (RBAC) | Autenticación | Respuestas |
|---|---|---|---|---|---|---|---|
| 1 | POST | `/api/v1/auth/token/` | Obtener par JWT | authentication | Público (credenciales) | — | 200, 401 |
| 2 | POST | `/api/v1/expedientes/` | Crear solicitud (BORRADOR + 5 peticiones) | expedientes | ESTUDIANTE, ADMINISTRADOR (allow) | JWT | 201, 400, 401, 403 |
| 3 | GET | `/api/v1/expedientes/bandeja/` | Bandeja operativa paginada por rol | expedientes | según `MAPA_INTERVENCION_POR_ROL` | JWT | 200, 401, 403 |
| 4 | GET | `/api/v1/expedientes/{id}/` | Detalle de expediente (aislamiento IDOR → 404) | expedientes | scopes own/carrera/facultad/all | JWT | 200, 401, 403, 404 |
| 5 | POST | `/api/v1/expedientes/{id}/enviar/` | Envío formal (providencia + plazo 8 días) | expedientes | ESTUDIANTE propietario | JWT | 200, 400, 401, 403, 404, **422** |
| 6 | GET | `/api/v1/expedientes/{expediente_id}/checklist/` | Checklist del expediente | verificacion | SECRETARIO_ABOGADO, ANALISTA_APOYO, ADMINISTRADOR | JWT | 200, 401, 403, 404 |
| 7 | PUT | `/api/v1/checklist/{id}/` | Evaluar requisito (VERIFICADO/OBSERVADO) | verificacion | SECRETARIO_ABOGADO (allow), ANALISTA_APOYO (borrador), ADMIN | JWT | 200, 400, 401, 403, 404 |
| 8 | POST | `/api/v1/checklist/{id}/subsanar/` | Subsanar con PDF (versión N+1) | verificacion | ESTUDIANTE own, SECRETARIA_CARRERA carrera, ADMIN | JWT | 200, 400, 401, 403, 404 |
| 9 | POST | `/api/v1/expedientes/{id}/observar/` | Observación accionable + pausa de plazo | expedientes/verificacion | SECRETARIO_ABOGADO | JWT | 200, 400, 401, 403, 404 |
| 10 | POST | `/api/v1/informes/` | Emitir informe (Providencia 590, PDF) | resoluciones | SECRETARIO_ABOGADO | JWT | 201, 400, 401, 403 |
| 11 | POST | `/api/v1/declaratorias/` | Declaratoria (Memorando 162, PDF firmado) | resoluciones | DECANO | JWT | 201, 400, 401, 403 |
| 12 | GET | `/api/v1/notificaciones/` | Listado propio (filtro `?leida=`) | notificaciones | todos (scope own) | JWT | 200, 401 |
| 13 | PATCH | `/api/v1/notificaciones/{id}/marcar-leida/` | Marcar leída (doble check de propiedad) | notificaciones | dueño | JWT | 200, 401, 403, 404 |
| 14 | POST | `/api/v1/peticiones/{id}/solicitar-emision/` | PENDIENTE→SOLICITADO + notificación | peticiones | ESTUDIANTE own, SECRETARIA_CARRERA | JWT | 200, 400, 401, 403, 404 |
| 15 | POST | `/api/v1/peticiones/{id}/documento/` | Cargar PDF (≤10 MB, magic bytes, hash) | peticiones | ESTUDIANTE own, SECRETARIA_CARRERA, emisores asignados, ADMIN | JWT (multipart) | 200, 400, 401, 403, 404 |
| 16 | GET | `/api/v1/peticiones/{id}/documento/` | Descargar documento vigente | peticiones | ídem + SCOPE_ASIGNADO | JWT | 200, 401, 403, 404 |
| 17 | GET | `/api/v1/peticiones/{id}/documento/{version}/` | Descargar versión específica | peticiones | ídem | JWT | 200, 401, 403, 404 |
| — | GET | `/api/v1/schema/`, `/api/v1/docs/`, `/api/v1/redoc/` | Documentación OpenAPI | config | **AllowAny** | — | 200 |

**Paginación**: solo la bandeja pagina (`PageNumberPagination`, `page_size=10`, `page_size` hasta 50 — `expedientes/adapters/views.py:179-184`); notificaciones la deshabilita explícitamente. **Filtros**: `?leida=` en notificaciones; el resto del filtrado es por ámbito RBAC, no por parámetros de consulta. No hay búsqueda ni ordenamiento por parámetros (orden fijo por `fecha_limite_atencion, fecha_creacion`).

**Coherencia de verbos**: correcta — POST solo crea/acciona, GET solo lee, PUT evalúa el checklist (reemplazo de estado de la verificación), PATCH solo marca-leída. No existen DELETE en la API (coherente con la política de no borrado).

### 5.5 Seguridad

**Implementado y verificado:**

- **Autenticación**: SimpleJWT stateless, access 60 min / refresh 24 h, claims `cedula` y `roles` (`authentication/adapters/serializers.py:6-12`; ADR-0003).
- **RBAC de mundo cerrado**: `RBAC_MATRIX` (`authentication/adapters/permissions.py:24-115`) — celda vacía = DENY; `HasRolePermission` deniega si la vista no declara recurso (permissions.py:151-165). Verificado con 17 pruebas dedicadas, incluida la comparación de la matriz codificada contra el literal 6.2 de la spec.
- **Anti-IDOR a nivel ORM**: `ScopeFilterMixin.scope_queryset` (`core/adapters/scope_filter.py`) mapea rol→ámbito (`own/carrera/facultad/all`, RESPONSABLE_DEPENDENCIA→denegado) y compone `Q()` sobre `estudiante_id/carrera_id/facultad_id`; los detalles usan `get_object_or_404(self.get_queryset())` → **404** (no 403) ante objetos ajenos. 13 pruebas específicas de aislamiento IDOR + 4 E2E.
- **Validación de archivos**: límite 10 MB, magic bytes `%PDF-` reales (no confía en extensión/MIME), hash SHA-256 en streaming (`core/adapters/pdf_validation.py`), aplicada en carga, subsanación y memorando.
- **Almacenamiento privado**: archivos bajo `MEDIA_ROOT/private` (o `PRIVATE_MEDIA_ROOT`), sin URL pública; descarga solo por `FileResponse` con `Content-Disposition: attachment`.
- **Integridad transaccional**: `select_for_update()` + `atomic` en todos los casos de uso de escritura.
- **Secretos**: sin secretos en el código (gitleaks: 0 hallazgos, `docs/security_report.md`); `SECRET_KEY` obligatoria por entorno; cuentas demo (`seed_initial_data`, contraseña `SgtDemo2026!`) marcadas explícitamente como no productivas (`seed_initial_data.py:6-9,54`).

**Brechas (ver §8 para detalle y prioridad):**

1. **Sin throttling/rate limiting** en ningún endpoint, incluido el login (no hay `DEFAULT_THROTTLE_CLASSES` en `settings/base.py:98-103`).
2. **Sin endurecimiento de producción**: no hay `SECURE_SSL_REDIRECT`, `HSTS`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `X_FRAME_OPTIONS`, ni `CORS` configurado; no existe `settings/production.py`.
3. **Docker en modo desarrollo**: `docker-compose.yml` fija `DJANGO_SETTINGS_MODULE: config.settings.local` y `DEBUG: ${DEBUG:-1}`; el `Dockerfile` arranca con `runserver` (CMD), no con gunicorn.
4. **Endpoints de documentación con `AllowAny`** (`settings/base.py:120-121`): `/api/v1/schema/`, `/docs/`, `/redoc/` exponen el contrato sin autenticación.
5. **JWT sin rotación ni blacklist** (`ROTATE_REFRESH_TOKENS=False`, `SIGNING_KEY = SECRET_KEY`).
6. `print()` de depuración en código de producción (`evaluar_checklist.py:164,170`).
7. `PRIVATE_MEDIA_ROOT` no está declarado en settings (el código usa `getattr` con fallback a `MEDIA_ROOT/private`; funciona, pero la ruta canónica no es configurable por entorno).
8. IP de auditoría siempre vacía (`_get_current_request()` devuelve `None`).

---

## 6. AUDITORÍA DE BASE DE DATOS

- **Motor**: PostgreSQL 16 en Docker (healthcheck incluido); SQLite en memoria para pruebas (`settings/test.py:5-10`).
- **Modelos**: 14 (ver §5.2). `db_table` explícitos en todas las apps; `AUTH_USER_MODEL="authentication.User"`.
- **Restricciones**: 4 UniqueConstraints nombradas + unique=True en números correlativos y cédula; FK PROTECT hacia usuarios y catálogo (evita borrados con historial).
- **Índices**: ~25 índices declarados, incluidos compuestos de consulta frecuente (`idx_notif_usuario_leida`, `idx_audit_expediente_fecha`, `idx_doc_peticion_vigente`).
- **Integridad y consistencia de migraciones**: verificada (`makemigrations --check` sin cambios). Las semillas (catálogo Art. 235, usuarios demo) están en migraciones/management commands idempotentes.
- **Riesgos**: (a) las pruebas corren en SQLite mientras producción es PostgreSQL — la portabilidad está verificada por la suite extendida (53 pruebas adicionales en SQLite; el sprint S1 documentó que 8 pruebas fallaban solo en Postgres por SQL hardcodeado y fue corregido); (b) `CONN_HEALTH_CHECKS=True` y `CONN_MAX_AGE` configurados, correcto; (c) no hay backups ni estrategia de restauración documentada; (d) no hay revisión de planes de consulta sobre volúmenes reales (el mock SGA no ejercita la BD).

---

## 7. AUDITORÍA DE PRUEBAS

### 7.1 Resultados ejecutados (reproducibles)

| Suite | Comando | Resultado |
|---|---|---|
| Backend configurada (`src/apps`) | `pytest -q` | 473 passed / 0 failed / 0 errors (10,8 s) |
| Backend extendida (`core` + `e2e`) | `pytest -q src/core src/core/adapters/tests tests/e2e` | 53 passed (1,0 s) |
| **Total backend** | | **526 passed / 0 failed** |
| Cobertura backend | `pytest --cov=src` | **93 %** (7693 stmts, 534 omitidas) |
| Frontend unit/integración | `npm run test` | 198 passed (43 archivos, 16,5 s) |
| Lint frontend / typecheck | `npm run lint` / `npm run typecheck` | 0 errores / 0 errores |
| Build frontend | `npm run build` | Exitoso |
| Migraciones | `makemigrations --check` | Sin cambios |
| OpenAPI | `manage.py spectacular` + `diff` | Idéntico al contrato versionado |

### 7.2 Qué verifica realmente la suite (no solo "pasa")

- **Máquina de estados del expediente**: 25 pruebas de transiciones válidas (7 caminos legales), inválidas, inmutabilidad de campos críticos y plazos (`test_expediente_state_machine.py`).
- **Cálculo de plazos laborables**: 11 pruebas — 8 días hábiles, feriados, fines de semana, pausa/reanudación y acumulación (`test_plazo_calculator.py`).
- **Aislamiento por rol (IDOR)**: 13 pruebas que exigen 404/200/403 correctos por cada uno de los 8 roles (`test_idor_isolation_expediente.py`) + 17 pruebas de la matriz RBAC, incluida su igualdad con el literal 6.2 de la spec (`test_rbac_permissions.py`).
- **Ingesta y seguridad de PDF**: 39 pruebas — magic bytes (rechaza ejecutable/PNG/JPEG renombrado), tamaño, hash, versionado, descarga segura y almacenamiento privado (`test_pdf_ingestion_and_security.py`).
- **Reglas de negocio**: unicidad de expediente activo, 5 requisitos Art. 235, checklist completo antes de informe (RN-003), rechazo de NO APTO, pausa/reanudación del plazo al observar/subsanar.
- **Auditoría**: 14 pruebas sobre `EventoAuditoria` (señales por entidad, inmutabilidad JSONB, índices).
- **E2E**: flujo completo FL-01→FL-05 con mock SGA e IDOR (`tests/e2e/test_full_workflow.py`) — **fuera de `testpaths`** (hallazgo P2).
- **Frontend**: router y guards por rol, expiración de sesión 401, cliente HTTP (400/401/403/404/red/timeout), cada componente UI con aserciones axe (`toHaveNoViolations`).

### 7.3 Vacíos de prueba

- Sin pruebas de carga/rendimiento ni de concurrencia real (el bloqueo pesimista se prueba lógicamente, no bajo contención paralela).
- Sin pruebas sobre PostgreSQL real en esta auditoría (no había servicio de BD disponible; la suite corre en SQLite).
- Sin tests E2E de navegador en frontend (no hay Playwright/Cypress).
- Sin pruebas de los ViewSets no ruteados (código muerto, ver §5.1).
- Cobertura con huecos notables: `verificacion/adapters/views.py` 65 %, `registrar_observacion.py` 76 %, `mock_sga.py` 84 %.

### 7.4 Hallazgos de calidad estática

- `flake8 src`: **854 hallazgos** — 530 E501 (línea larga), 44 W292, 41 W293, ~39 F811 (redefiniciones, p. ej. imports no usados de constantes de estado en `peticiones/adapters/models.py` y `verificacion/adapters/models.py`). Sin errores funcionales (no hay F821/F401 críticos reportados como error). Prioridad P3.
- Bandit (informe previo T044, 22-oct-2026): 0 high / 17 medium / 1303 low (todos en tests). Gitleaks: 0 hallazgos.

---

## 8. HALLAZGOS CLASIFICADOS POR PRIORIDAD

Formato: ID | Descripción | Evidencia | Impacto | Recomendación | Estado.

### P0 — Críticos

| ID | Hallazgo | Evidencia | Impacto | Recomendación | Estado |
|---|---|---|---|---|---|
| AUD-P0-01 | El despliegue Docker ejecuta en modo desarrollo: `DEBUG=1` por defecto, settings `local` y servidor `runserver` | `docker-compose.yml` (env backend), `Dockerfile` (CMD) | Exposición de detalles internos, sin servidor de producción, riesgo de integridad | Crear `settings/production.py` con hardening, usar gunicorn+nginx y overrides por entorno | Abierto (plan MEJ-P0-01) |
| AUD-P0-02 | Sin limitación de tasa en toda la API, incluido el login | `settings/base.py:98-103` (sin throttling), `auth/token/` sin throttle | Fuerza bruta de credenciales y abuso de endpoints | Habilitar throttling DRF (p. ej. `AnonRateThrottle` en login, `ScopedRateThrottle` global) | Abierto (MEJ-P0-02) |

### P1 — Altos

| ID | Hallazgo | Evidencia | Impacto | Recomendación | Estado |
|---|---|---|---|---|---|
| AUD-P1-01 | Sin endurecimiento HTTPS/HSTS/cookies ni CORS configurado; sin `production.py` | `settings/base.py` (sin SECURE_*/CORS_*) | Despliegue seguro imposible con la configuración actual | Añadir settings de producción tras decisión de topología (proxy TLS) | Abierto |
| AUD-P1-02 | Endpoints de documentación (`/schema/`, `/docs/`, `/redoc/`) con `AllowAny` | `settings/base.py:120-121` | Exposición pública del contrato y superficie de reconocimiento | Restringir por autenticación o red interna en producción | Abierto |
| AUD-P1-03 | Las 9 vistas del frontend son stubs; el producto no es usable por usuario final | `frontend/src/features/*/*.tsx` (todas "Vista pendiente de implementación") | El sistema no puede demostrarse con UI | Ejecutar el plan FE (specs/003, tareas FE-T pendientes) | Abierto |
| AUD-P1-04 | `testpaths` de pytest excluye `core/tests`, `core/adapters/tests` y `tests/e2e` | `backend/pyproject.toml` (`testpaths=["src/apps"]`) | La suite "verde" por defecto no ejecuta 53 pruebas reales, incluido el E2E del flujo completo | Incluir las rutas en `testpaths` o un profile CI | Abierto |
| AUD-P1-05 | Sin estrategia de respaldo/restauración de PostgreSQL ni de `media/private` | ausencia en `docker-compose.yml`, `docs/`, scripts | Pérdida de expedientes/documentos ante incidente | Definir backup programado + prueba de restauración documentada | Abierto |

### P2 — Medios

| ID | Hallazgo | Evidencia | Impacto | Recomendación | Estado |
|---|---|---|---|---|---|
| AUD-P2-01 | `HistorialEstado.estado_anterior` incorrecto en la transición a INFORME_EMITIDO (N-1 confirmado) | `emitir_informe.py:203-211` | Trazabilidad incompleta del paso clave | Capturar el estado previo antes de mutar | Abierto |
| AUD-P2-02 | `print()` de depuración en producción | `evaluar_checklist.py:164,170` | Fugas de información por stdout; ruido | Eliminar y configurar `LOGGING` | Abierto |
| AUD-P2-03 | Sin configuración de `LOGGING` en settings | `settings/base.py` (ausente) | Sin observabilidad de errores | Definir logging estructurado por entorno | Abierto |
| AUD-P2-04 | JWT sin rotación ni blacklist; `SIGNING_KEY = SECRET_KEY` | `settings/base.py:105-111` | Tokens de refresh reutilizables indefinidamente | Habilitar rotación + blacklist (o ciclo de vida corto documentado) | Abierto |
| AUD-P2-05 | `PRIVATE_MEDIA_ROOT` no declarado en settings (fallback implícito) | `local_storage.py:21`, `pdf_generator.py:25` (getattr) | Ruta de almacenamiento no controlada por entorno | Declarar la variable en `base.py`/`.env.example` | Abierto |
| AUD-P2-06 | IP de auditoría siempre vacía | `signals.py:32-36` | Bitácora sin origen de la operación | Resolver request real (thread-local/ASGI) o eliminar el campo del flujo | Abierto |
| AUD-P2-07 | Discrepancia de roles: servicio de declaratoria admite ANALISTA_APOYO, la matriz RBAC no | `declarar_aptitud.py:125-128` vs `permissions.py:106-110` | Inconsistencia latente de autorización | Alinear servicio con la matriz | Abierto |
| AUD-P2-08 | Discrepancia menor del contrato: securityScheme del yaml (`jwtAuth`) vs `SPECTACULAR_SETTINGS` (`BearerAuth`); POST de login marcado con security | `openapi.yaml:1220-1224`, `settings/base.py:138-147`, `openapi.yaml:32-33` | Confusión en clientes generados | Ajustar configuración y regenerar | Abierto |
| AUD-P2-09 | README raíz declara "19 endpoints" y "cobertura 95 %" (reales: 17 y 93 %) | `README.md:204` vs medición de esta auditoría | Comunicación inexacta del estado | Corregir README | Abierto |
| AUD-P2-10 | Cobertura desigual: `verificacion/adapters/views.py` 65 %, `registrar_observacion.py` 76 % | salida `--cov` | Riesgo en ramas de error de vistas | Añadir pruebas de ramas de error | Abierto |

### P3 — Bajos

| ID | Hallazgo | Evidencia | Impacto | Recomendación | Estado |
|---|---|---|---|---|---|
| AUD-P3-01 | Código muerto: `PeticionDocumentalViewSet` y `ObservacionViewSet` sin rutar; recurso RBAC `observaciones` inexistente | `peticiones/adapters/views.py:285`, `verificacion/adapters/views.py:169,177` | Superficie confusa; riesgo de uso futuro sin permisos | Eliminar o rutear con celda de matriz | Abierto |
| AUD-P3-02 | Eventos de auditoría definidos y nunca generados (`SUBSANACION_REALIZADA`, `EXPEDIENTE_ENVIADO`, `EXPEDIENTE_CANCELADO`) | `notificaciones/adapters/models.py:71-79` | Catálogo de auditoría incompleto | Emitirlos desde signals/servicios | Abierto |
| AUD-P3-03 | 854 hallazgos de flake8 (estilo + F811) | `flake8 src --count` | Mantenibilidad | Pasar black/isort y limpiar imports | Abierto |
| AUD-P3-04 | Duplicación byte a byte de `openapi.yaml` en `contracts/` | `diff` idéntico | Riesgo de desincronización manual | Generar `contracts/` desde CI | Abierto |
| AUD-P3-05 | ADRs declarados sin archivo (0004-0008) y ADRs spec vacíos; 2 copias divergentes de la Constitución | `specs/001/plan.md`, `specs/001/adr/*` (0 bytes), diff constituciones | Confusión normativa | Consolidar o eliminar duplicados | Abierto |
| AUD-P3-06 | `backend/README.md` es el README upstream de gitleaks; `docs/frontend/FRONTEND_IMPLEMENTATION_PLAN.md` vacío | ambos archivos | Documentación de onboarding rota | Reescribir README del backend | Abierto |
| AUD-P3-07 | Guard `RedirectIfAuthenticated` y barrels (`ui/index.ts`, `features/index.ts`, etc.) sin uso | `guards.tsx:34-41`, barrels vacíos | Scaffolding sin uso | Usarlos o eliminarlos | Abierto |
| AUD-P3-08 | README del frontend desactualizado (dice "no hay cliente HTTP") | `frontend/README.md:9` vs `src/api/client.ts` | Orientación incorrecta a nuevos devs | Actualizar | Abierto |
| AUD-P3-09 | `Content-Length` estática en descarga streaming | `peticiones/adapters/views.py:220-228` | Progreso de descarga impreciso | Usar FileResponse con tamaño real | Abierto |

### Revalidación de hallazgos previos (sprint S1)

| Hallazgo previo | Estado actual verificado |
|---|---|
| SEC-01 memorando 162 no persistido | **CORREGIDO** — `declarar_aptitud.py:183` llama `guardar_archivo_privado` |
| SEC-02 rutas `/media/private` hardcodeadas | **PARCIALMENTE CORREGIDO** — el código usa `PRIVATE_MEDIA_ROOT` con fallback, pero la variable no está declarada en settings (AUD-P2-05) |
| SEC-03 GET checklist inoperable (403) | **CORREGIDO** — celda GET en `RBAC_MATRIX["checklist"]` (`permissions.py:77-98`) y pruebas asociadas |
| D-04 suite regresada (50F/24E) | **CORREGIDO** — 526/526 verdes en esta auditoría |
| R1–R5 (recomendaciones S1) | R1, R2, R3, R4 ejecutadas; **R5 (producción real) sigue abierta** → AUD-P0-01 |

---

## 9. AUDITORÍA DE INFRAESTRUCTURA

| Aspecto | Estado | Evidencia |
|---|---|---|
| Docker Compose (db+backend+nginx) | Funcional para desarrollo; healthcheck de PG incluido | `docker-compose.yml` |
| Servidor de aplicación | `runserver` (desarrollo) — no apto producción | `Dockerfile` CMD |
| Configuración por entorno | base/local/test; **falta production** | `src/config/settings/` |
| Variables de entorno | Documentadas en `backend/.env.example`; SECRET_KEY y DB_PASSWORD obligatorias | `.env.example`, `base.py:11-13` |
| Almacenamiento | Volúmenes Docker `media_data`/`static_data`; almacenamiento privado bajo `/app/backend/media` | `docker-compose.yml`, `local_storage.py` |
| Nginx | Proxy a backend:8000; estáticos desde volumen | `nginx/nginx.conf` |
| Health checks | Solo PostgreSQL; **sin healthcheck de Django** | `docker-compose.yml` |
| Backups / restauración | **Ausentes** | — |
| CI/CD | **Ausente** (solo `.github/` mínimo; sin workflows de test/build verificados) | `.github/` |
| Reproducibilidad en entorno limpio | **Alta para desarrollo**: `docker compose up` + `migrate` + `seed_initial_data`; las pruebas requieren solo `requirements*.txt` | README raíz |

---

## 10. MATRIZ DE FUNCIONALIDADES Y ESTADO REAL

Categorías: **IV** = Implementado y Verificado (evidencia de ejecución); **IP** = Implementado Parcialmente; **ISV** = Implementado Sin Verificación; **DSI** = Documentado Sin Implementación; **NI** = No Implementado.

| # | Funcionalidad | Capa | Estado | Evidencia |
|---|---|---|---|---|
| F-01 | Login JWT con claims de rol/cédula | API | IV | 473 pruebas incl. `test_jwt.py`; E2E |
| F-02 | Crear solicitud (BORRADOR + 5 peticiones Art. 235) | API→BD | IV | `test_crear_expediente.py` (8), E2E |
| F-03 | Envío formal con providencia y plazo 8 días hábiles | API→BD | IV | `test_enviar_expediente.py` (7), `test_plazo_calculator.py` (11) |
| F-04 | Bandeja operativa paginada por rol | API | IV | `test_bandeja_expedientes.py` (9) |
| F-05 | Solicitar emisión de documento a dependencia | API→BD | IV | `test_solicitar_emision.py` (15) |
| F-06 | Carga de PDF con validación y versionado N+1 | API→BD→disco | IV | `test_pdf_ingestion_and_security.py` (39) |
| F-07 | Descarga segura de documento (vigente/versión) | API→disco | IV | `test_descargar_documento.py` (12) |
| F-08 | Checklist: evaluación VERIFICADO/OBSERVADO con bloqueo pesimista | API→BD | IV | `test_evaluar_checklist.py` (22) |
| F-09 | Observación accionable con pausa del plazo | API→BD | IV | `test_checklist_and_observations.py` (28) |
| F-10 | Subsanación con nueva versión y reanudación del plazo | API→BD | IV | `test_subsanar_requisito.py` (15) |
| F-11 | Informe de aptitud (Providencia 590, PDF ReportLab) | API→BD→disco | IV | `test_emitir_informe.py` (24), `test_pdf_generator.py` (30) |
| F-12 | Declaratoria (Memorando 162, PDF firmado persistido) | API→BD→disco | IV | `test_declarar_aptitud.py` (29) |
| F-13 | Notificaciones in-app + marcar leída | API→BD | IV | `test_notification_service.py` (17), `test_endpoints.py` (12) |
| F-14 | Bitácora de auditoría (signals, JSONB) | BD | IP | `test_auditoria.py` (14); IP: 3 eventos sin emitir, IP siempre vacía (AUD-P3-02, AUD-P2-06) |
| F-15 | RBAC de mundo cerrado + aislamiento IDOR | API | IV | `test_rbac_permissions.py` (17), `test_idor_isolation_expediente.py` (13) |
| F-16 | Mock SGA (récord académico inmutable) | core | IV | `test_mock_sga.py` (25) |
| F-17 | Django Admin como consola interna (ADR-0009) | backend | IV | `test_django_admin.py` (4) |
| F-18 | Contrato OpenAPI sincronizado y servido | API | IV | regeneración idéntica; Swagger/Redoc en `/api/v1/docs/` |
| F-19 | Login UI (V-01) | frontend | IP | LoginPage es stub; auth + cliente HTTP listos y probados |
| F-20 | Dashboard estudiante (V-02) | frontend | NI | stub |
| F-21 | Nueva solicitud (V-03) | frontend | NI | stub |
| F-22 | Detalle expediente (V-04) | frontend | NI | stub |
| F-23 | Peticiones y seguimiento (V-05/V-06) | frontend | NI | stub |
| F-24 | Bandeja y detalle funcionario (V-07/V-08) | frontend | NI | stub |
| F-25 | No habilitado (V-09) | frontend | IP | stub (ruta y guard operativos) |
| F-26 | 404 global | frontend | IV | `NotFoundPage` + pruebas |
| F-27 | Refresh token / logout server-side | frontend | NI | refresh no persistido ni usado (BE-03) |
| F-28 | Integración real SGA / FirmaEC | sistema | NI (por diseño) | mock según DEC-04/RN-005; integración futura |
| F-29 | Legalización de documentos (estado LEGALIZADO) | backend | NI | estado definido sin flujo que lo produzca |
| F-30 | Cancelación de expediente (estado CANCELADA) | backend | NI | estado definido sin endpoint/servicio |
| F-31 | Catálogo de requisitos (CRUD admin) | backend | NI | celda RBAC `catalogos:requisitos` definida sin endpoint |
| F-32 | Dashboards/indicadores por rol | sistema | NI | no existe endpoint ni vista; diseñado en Fase II de esta auditoría |

**Resumen**: de 32 funcionalidades evaluadas — 18 IV (56 %), 3 IP (9 %), 9 NI (28 %), 2 por diseño/NI (6 %). *Método de cálculo: cada fila se clasificó según evidencia de ejecución (pruebas corridas en esta auditoría) o ausencia de código; IP = existe código parcial o infraestructura lista sin el flujo completo.*

---

## 11. RIESGOS IDENTIFICADOS

| ID | Riesgo | Prob. | Impacto | Mitigación propuesta |
|---|---|---|---|---|
| R-A01 | Despliegue en producción con DEBUG/runserver | Alta si se despliega hoy | Alto | MEJ-P0-01 (settings producción + gunicorn) |
| R-A02 | Fuerza bruta sobre `/auth/token/` | Media | Alto | MEJ-P0-02 (throttling) |
| R-A03 | Pérdida de datos sin backups | Media | Alto | MEJ-P1-05 |
| R-A04 | Desincronización manual de `contracts/openapi.yaml` | Media | Medio | MEJ-P3-04 (generación en CI) |
| R-A05 | Deriva de expectativas: README sobredeclara estado (95 % cobertura, 19 endpoints, "sistema funcional") | Alta | Medio (reputacional en demo) | Corregir READMEs (AUD-P2-09, AUD-P3-06) |
| R-A06 | Dependencia de SQLite en pruebas vs PostgreSQL en producción | Baja-media | Medio | Ejecutar CI contra PostgreSQL (servicio en contenedor) |
| R-A07 | Trazabilidad de historial incompleta (N-1) | Alta (ya ocurre) | Medio | MEJ-P2-01 |
| R-A08 | Cuentas demo con contraseña pública si se despliega sin cambio | Alta | Alto en contexto real | Bloquear seed en producción / forzar cambio de contraseña |

---

## 12. RECOMENDACIONES

1. **P0**: crear `settings/production.py` con hardening (SSL redirect, HSTS, cookies seguras, ALLOWED_HOSTS, CORS explícito), servir con gunicorn y eliminar `DEBUG=1` del compose por defecto (MEJ-P0-01).
2. **P0**: habilitar throttling DRF, con umbral estricto en el login (MEJ-P0-02).
3. **P1**: incluir `core`, `core/adapters/tests` y `tests/e2e` en `testpaths` (MEJ-P1-04).
4. **P1**: definir backups automáticos de PostgreSQL y del volumen `media_data`, con procedimiento de restauración probado (MEJ-P1-05).
5. **P1**: continuar el plan FE (specs/003): V-01 login real contra el backend, luego V-02/V-07 (los dashboards de estudiante y bandeja son los de mayor valor de demostración).
6. **P2**: corregir N-1 (capturar estado previo antes de mutar), eliminar prints, configurar LOGGING, declarar `PRIVATE_MEDIA_ROOT`.
7. **P2**: corregir READMEs para reflejar cifras reales (17 endpoints, 93 % cobertura, 526 pruebas).
8. **P3**: limpieza de código muerto, flake8/black, generación del contrato en CI, consolidación de constituciones y ADRs.

El detalle con criterios de aceptación y estimaciones está en `docs/auditoria/PLAN_MEJORA_TECNICA.md`.

---

## 13. CONCLUSIONES

1. El **backend está genuinamente implementado y verificado**: no es documentación sin código; el flujo completo del trámite funciona y está blindado por 526 pruebas con 93 % de cobertura, incluido un E2E de extremo a extremo.
2. La **arquitectura hexagonal se cumple en el código**, no solo en los documentos: dominio puro, casos de uso transaccionales, adaptadores delgados y puertos para integraciones futuras (SGA).
3. La **seguridad de autorización es un punto fuerte** (RBAC de mundo cerrado + aislamiento ORM con semántica 404), mientras que la **seguridad operacional** (throttling, TLS, endurecimiento, backups) es el principal gap.
4. El **frontend tiene cimientos de alta calidad** (router, auth, design system, 198 pruebas con axe) pero **cero vistas de negocio**: la brecha principal hacia una demo de producto.
5. La **documentación de specs es excelente**; la documentación de onboarding (READMEs) es deficiente e incluso incorrecta en cifras.

---

## 14. DICTAMEN SOBRE EL NIVEL DE MADUREZ

**Dictamen: MVP de backend funcional y verificado (TRL académico alto); sistema integral en fase de integración frontend.**

- **Demostrable hoy vía API**: sí — flujo FL-01→FL-05 completo con datos de prueba (`seed_initial_data`), Swagger UI incluido.
- **Demostrable hoy vía UI**: no — las 9 vistas son stubs.
- **Aptitud para producción institucional**: no — faltan P0 de infraestructura/seguridad y la integración real con SGA/FirmaEC (hoy simuladas por diseño del proyecto).

## 15. TABLA RESUMEN DE EVALUACIÓN

| Área | Estado | Evidencia | Riesgo | Prioridad |
|---|---|---|---|---|
| Arquitectura | Hexagonal implementada y coherente con ADRs | `backend/src/apps/*`, ADR-0001 | Bajo | P3 |
| Backend | MVP completo, 526 pruebas verdes, servicios centralizados | §5, §7 | Bajo-medio | P2 |
| Base de datos | 14 modelos, migraciones consistentes, índices/constraints correctos | §6 | Medio (sin backups) | P1 |
| APIs REST | 17 operaciones, contrato OpenAPI válido y sincronizado | §5.4 | Bajo | P3 |
| Seguridad | RBAC+IDOR sólidos; sin throttling ni hardening; Docker en modo dev | §5.5, §8 | Alto | P0 |
| Pruebas | 526 backend + 198 frontend verdes; cobertura 93 %; huecos en vistas y E2E de navegador | §7 | Bajo-medio | P2 |
| Infraestructura | Docker dev funcional; sin CI/CD, backups ni healthcheck de app | §9 | Alto | P0/P1 |
| Documentación | Specs densas y trazables; READMEs incorrectos/desactualizados | §4.3 | Medio | P2/P3 |
