# PLAN DE REFACTORIZACIÓN — SGT-SIAAF Backend

**Versión:** 1.0  
**Fecha:** 2026-11-05  
**Basado en:** Auditoría seguridad, revisión código, deuda técnica identificada  
**Principio:** No reescrituras generales; correcciones localizadas y verificables

---

## Resumen de Refactorizaciones Propuestas

| ID | Título | Tipo | Prioridad | Módulos Afectados | Impacto API | Impacto Frontend |
|----|--------|------|-----------|-------------------|-------------|------------------|
| REF-001 | Separar JWT_SIGNING_KEY de SECRET_KEY | Seguridad | 🔴 Crítica | `settings/base.py`, `.env.example` | Bajo (re-login único) | Ninguno |
| REF-002 | Habilitar rotación + blacklist refresh tokens | Seguridad | 🔴 Crítica | `settings/base.py`, `auth/views.py`, `urls.py`, migraciones | Medio (nuevo endpoint logout, refresh rota) | Medio (interceptor axios, logout) |
| REF-003 | Implementar throttling login | Seguridad | 🔴 Crítica | `settings/base.py`, `auth/views.py` | Bajo (429 en login masivo) | Bajo (mensaje "demasiados intentos") |
| REF-004 | Middleware thread-local + TRUSTED_PROXIES para IP auditoría | Seguridad | 🔴 Crítica | `core/adapters/middleware.py` (nuevo), `notificaciones/signals.py`, `settings/production.py` | Ninguno | Ninguno |
| REF-005 | Configuración producción completa | Infra | 🔴 Crítica | `settings/production.py` (nuevo), `Dockerfile`, `docker-compose.prod.yml`, `nginx/prod.conf` | Alto (HTTPS, CORS, CSRF, cookies) | Alto (API_BASE_URL HTTPS, cookies seguras, CSRF) |
| REF-006 | Access token 30 min (ACD) | Seguridad | 🟡 Media | `settings/base.py`, `settings/production.py` | Bajo (re-login más frecuente) | Bajo (interceptor ya maneja refresh) |
| REF-007 | Validación MIME real PDF (pikepdf/python-magic) | Seguridad | 🟡 Media | `core/adapters/pdf_validation.py`, `requirements.txt`, `Dockerfile` | Ninguno (mismo 400 si inválido) | Ninguno |
| REF-008 | Throttling carga documentos (10/hora/user) | Seguridad | 🟡 Media | `settings/base.py`, `peticiones/views.py` | Bajo (429 en carga masiva) | Bajo (mensaje límite) |
| REF-009 | Reemplazar rutas internas por download_url en serializers | Seguridad | 🟡 Media | `peticiones/serializers.py`, `resoluciones/serializers.py`, `resoluciones/views.py` (nuevo endpoint) | Medio (estructura response cambia) | **Alto** (migración V-03, V-07, V-08 a download_url) |
| REF-010 | Handler global excepciones + formato uniforme | Seguridad | 🟡 Media | `core/adapters/exceptions.py` (nuevo), `settings/base.py` | **Medio** (formato error cambia) | **Medio** (error handling global) |
| REF-011 | Logging estructurado (JSON, rotación, filtros PII) | Seguridad | 🟡 Media | `settings/base.py`, `settings/production.py`, `core/adapters/logging_filters.py` (nuevo) | Ninguno | Ninguno |
| REF-012 | Eliminar print() en evaluar_checklist.py | Seguridad | 🟡 Media | `verificacion/services/evaluar_checklist.py:164,170` | Ninguno | Ninguno |
| REF-013 | Protección Swagger/ReDoc/schema en producción | Seguridad | 🟡 Media | `settings/production.py`, `settings/local.py`, `settings/test.py` | Bajo (403 anónimo prod) | Bajo (frontend no usa Swagger) |
| REF-014 | CI/CD Security (Safety + Bandit + Gitleaks) | Calidad | 🟡 Media | `.github/workflows/security.yml` (nuevo), `.bandit`, `.gitleaksignore` | Ninguno | Ninguno |
| REF-015 | Dependabot configurado | Calidad | 🟡 Media | `.github/dependabot.yml` (nuevo) | Ninguno | Ninguno |
| REF-016 | Cobertura tests + testpaths correcto + fail_under | Calidad | 🟡 Media | `pyproject.toml` | Ninguno | Ninguno |
| REF-017 | Tests seguridad faltantes (throttling, rotación, Swagger, IP auditoría) | Calidad | 🟡 Media | `auth/tests/test_security_controls.py`, `notificaciones/tests/test_audit_ip.py`, `auth/tests/test_swagger_protection.py`, `peticiones/tests/test_upload_throttle.py` | Ninguno | Ninguno |
| REF-018 | Procedimiento rotación secretos documentado | Documentación | 🟢 Baja | `SECURITY_CONFIG.md` (nuevo) | Ninguno | Ninguno |
| REF-019 | Limpieza archivos huérfanos (management command) | Operaciones | 🟢 Baja | `peticiones/management/commands/limpiar_archivos_huérfanos.py` (nuevo), `Dockerfile` cron | Ninguno | Ninguno |
| REF-020 | Verificación PermissionError Docker | Operaciones | 🟢 Baja | `DEPLOY_PRODUCTION.md`, Docker staging | Ninguno | Ninguno |
| REF-021 | Evidencias ACD 4 reales | Trazabilidad | 🟢 Baja | `MATRIZ_TRAZABILIDAD_SEGURIDAD.md` | Ninguno | Ninguno |

---

## Fichas Detalladas por Refactorización

### REF-001 — Separar JWT_SIGNING_KEY de SECRET_KEY

| Campo | Detalle |
|-------|---------|
| **Problema** | `SIMPLE_JWT.SIGNING_KEY = SECRET_KEY` en `base.py:110` — compromiso dual (JWT + sesiones Django/cookies) |
| **Justificación** | ADR-003 advierte: "un SECRET_KEY comprometido permite falsificar tokens Y firmar cookies" |
| **Archivos Afectados** | `backend/src/config/settings/base.py` (línea 110), `backend/.env.example` |
| **Cambio Propuesto** | 1. `SIMPLE_JWT.SIGNING_KEY = env("JWT_SIGNING_KEY")`<br>2. `SECRET_KEY = env("SECRET_KEY")` sin cambios<br>3. `production.py` valida que ambas existan y sean distintas (warning si iguales)<br>4. `.env.example` documenta ambas con `openssl rand -base64 32` |
| **Dependencias** | Ninguna (independiente, inicia Fase 0) |
| **Impacto Backend** | Bajo — tokens JWT existentes se invalidan (re-login único tras deploy) |
| **Impacto Frontend** | Ninguno — solo re-login único |
| **Pruebas Requeridas** | 1. `test_jwt_signing_key_separate_from_secret_key`<br>2. `test_jwt_token_verification_uses_jwt_signing_key`<br>3. `test_django_sessions_use_secret_key` |
| **Riesgos** | Deploy coordinado requerido; comunicar re-login único a usuarios |
| **Criterios Aceptación** | Tests passing; variables en `.env.example`; documentado en `SECURITY_CONFIG.md` |
| **Rollback** | Revertir `base.py` a `SIGNING_KEY = SECRET_KEY`; eliminar `JWT_SIGNING_KEY` de env; re-deploy |

---

### REF-002 — Habilitar Rotación + Blacklist Refresh Tokens

| Campo | Detalle |
|-------|---------|
| **Problema** | `ROTATE_REFRESH_TOKENS=False`, `BLACKLIST_AFTER_ROTATION` no configurado, `token_blacklist` no instalado |
| **Justificación** | Refresh token robado = acceso indefinido sin rotación ni revocación |
| **Archivos Afectados** | `settings/base.py` (INSTALLED_APPS, SIMPLE_JWT), `auth/views.py` (nuevo LogoutView), `config/urls.py`, migraciones |
| **Cambio Propuesto** | 1. `INSTALLED_APPS` += `"rest_framework_simplejwt.token_blacklist"`<br>2. `SIMPLE_JWT.ROTATE_REFRESH_TOKENS = True`, `BLACKLIST_AFTER_ROTATION = True`<br>3. `python manage.py migrate` (token_blacklist)<br>4. Nuevo `LogoutView` en `auth/views.py`: `POST /api/v1/auth/logout/` body `{"refresh": "..."}` → blacklist → 205<br>5. Registrar en `config/urls.py` |
| **Dependencias** | REF-001 (JWT_SIGNING_KEY separada — rotación usa misma clave firma) |
| **Impacto Backend** | Medio — migraciones, nuevo endpoint, lógica rotación |
| **Impacto Frontend** | **Medio** — Interceptor axios debe guardar nuevo refresh tras cada refresh, llamar `POST /auth/logout/` al cerrar sesión, manejar 401 en refresh → redirect login |
| **Pruebas Requeridas** | 1. `test_refresh_rotates_token_returns_new_access_and_refresh`<br>2. `test_old_refresh_rejected_after_rotation`<br>3. `test_blacklisted_refresh_rejected`<br>4. `test_logout_requires_authentication`<br>5. `test_refresh_token_lifetime_respected` |
| **Riesgos** | Migraciones en producción; coordinación frontend para interceptor/logout |
| **Criterios Aceptación** | Migraciones aplicadas; tests passing; endpoint logout en OpenAPI; frontend actualizado |
| **Rollback** | `migrate token_blacklist zero`; eliminar app de INSTALLED_APPS; revertir flags SIMPLE_JWT; eliminar LogoutView y URL |

---

### REF-003 — Throttling Login (5 req/min/IP)

| Campo | Detalle |
|-------|---------|
| **Problema** | Sin límite intentos en `POST /api/v1/auth/token/` — vulnerable a fuerza bruta |
| **Justificación** | OWASP: throttling login esencial; auditoría SEC-AUTH-01 PENDIENTE |
| **Archivos Afectados** | `settings/base.py`, `settings/production.py`, `auth/views.py` |
| **Cambio Propuesto** | 1. `DEFAULT_THROTTLE_RATES["auth"] = "5/minute"` en `base.py`/`production.py`<br>2. `TokenPairView` añadir `throttle_classes = [AnonRateThrottle]`, `throttle_scope = "auth"`<br>3. Requiere REF-004 (TRUSTED_PROXIES) para IP real confiable |
| **Dependencias** | REF-004 (TRUSTED_PROXIES + middleware thread-local) |
| **Impacto Backend** | Bajo — config + 2 líneas en View |
| **Impacto Frontend** | Bajo — solo recibe 429 en login masivo; mensaje "Demasiados intentos, espera X minutos" |
| **Pruebas Requeridas** | 1. `test_login_throttle_allows_5_requests_per_minute`<br>2. `test_login_throttle_6th_request_returns_429`<br>3. `test_login_throttle_resets_after_window`<br>4. `test_login_throttle_per_ip_isolation`<br>5. `test_login_throttle_respects_trusted_proxies` |
| **Riesgos** | Sin REF-004, throttling por IP de proxy → bloqueo masivo |
| **Criterios Aceptación** | Tests passing; config en base/production; documentado en `SECURITY_CONFIG.md` |
| **Rollback** | Eliminar `auth` de `DEFAULT_THROTTLE_RATES`; revertir `TokenPairView` sin `throttle_classes` |

---

### REF-004 — Middleware Thread-Local + TRUSTED_PROXIES para IP Auditoría

| Campo | Detalle |
|-------|---------|
| **Problema** | `_get_current_request()` retorna `None` hardcoded; `_get_client_ip()` acepta `X-Forwarded-For` sin validar proxies → IP suplantable |
| **Justificación** | Auditoría con IP falsificada compromete trazabilidad (SEC-LOG-03 FALLIDO) |
| **Archivos Afectados** | `core/adapters/middleware.py` (nuevo), `notificaciones/signals.py`, `settings/base.py` (MIDDLEWARE), `settings/production.py` |
| **Cambio Propuesto** | 1. `core/adapters/middleware.py`: `ThreadLocalRequestMiddleware` (guarda `request` en `thread_local`, expone `get_current_request()`)<br>2. `settings/base.py`: Insertar middleware **PRIMERO** en `MIDDLEWARE`<br>3. `signals.py`: `_get_current_request()` lee de thread-local; `_get_client_ip()` valida `X-Forwarded-For` contra `TRUSTED_PROXIES` (CIDR con `ipaddress`)<br>4. `production.py`: `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")`, `TRUSTED_PROXIES = env.list("TRUSTED_PROXIES", default=["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"])` |
| **Dependencias** | REF-005 (production.py + Nginx proxy real) |
| **Impacto Backend** | Medio — nuevo middleware, cambios signals, config producción |
| **Impacto Frontend** | Ninguno — interno auditoría |
| **Pruebas Requeridas** | 1. `test_audit_ip_captured_from_xff_with_trusted_proxy`<br>2. `test_audit_ip_spoofing_blocked_untrusted_proxy`<br>3. `test_audit_ip_persisted_in_eventoauditoria`<br>4. `test_audit_ip_none_when_no_request` |
| **Riesgos** | Middleware debe ser PRIMERO en MIDDLEWARE; validar compatibilidad ASGI (`contextvars` para async) |
| **Criterios Aceptación** | Middleware en MIDDLEWARE[0]; tests passing; TRUSTED_PROXIES documentado |
| **Rollback** | Eliminar middleware de MIDDLEWARE; revertir signals.py; eliminar settings TRUSTED_PROXIES |

---

### REF-005 — Configuración Producción Completa

| Campo | Detalle |
|-------|---------|
| **Problema** | **CRÍTICO:** Sin `production.py`, `Dockerfile`, `docker-compose.prod.yml`, Nginx, TLS, headers seguridad, usuario no-root |
| **Justificación** | Backend NO desplegable en producción; hardening ausente (SEC-T001 CRÍTICO) |
| **Archivos Afectados** | `settings/production.py` (nuevo), `Dockerfile` (nuevo), `docker-compose.prod.yml` (nuevo), `nginx/prod.conf` (nuevo), `entrypoint.sh` (nuevo), `.env.example` (actualizar) |
| **Cambio Propuesto** | Ver `SEC-T001` en `BACKLOG_BRECHAS_SEGURIDAD.md` — detalle completo:<br>1. `production.py` heredando `base.py` con hardening completo (SECURE_*, cookies, CSRF, CORS, CSP, TRUSTED_PROXIES, LOGGING, SERVE_PERMISSIONS=IsAdminUser)<br>2. `Dockerfile` multi-stage (builder → python:3.12-slim), usuario `appuser` UID 1000, Gunicorn 4 workers, healthcheck `/health/`, entrypoint `migrate` + `collectstatic` + `gunicorn`<br>3. `docker-compose.prod.yml`: `backend`, `postgres`, `nginx` (SSL Let's Encrypt), volúmenes `media_private`, `postgres_data`, `nginx_certs`<br>4. `nginx/prod.conf`: `limit_req_zone`, `proxy_set_header X-Forwarded-For`, TLS 1.2+, HSTS, CSP, headers seguridad<br>5. `.env.example`: todas variables requeridas (incl. `JWT_SIGNING_KEY`, `TRUSTED_PROXIES`, `CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS`, `AUTH_THROTTLE_RATE`, `DOCUMENT_UPLOAD_THROTTLE`, `ORPHAN_RETENTION_DAYS`) |
| **Dependencias** | REF-001, REF-004 (TRUSTED_PROXIES), REF-010 (Exception Handler), REF-011 (Logging), REF-013 (Swagger) |
| **Impacto Backend** | **Alto** — Infraestructura completa nueva |
| **Impacto Frontend** | **ALTO** — `API_BASE_URL` HTTPS, cookies seguras (`Secure`, `HttpOnly`, `SameSite=Lax`), CSRF token en requests mutantes (`X-CSRFToken`), CORS origins |
| **Pruebas Requeridas** | 1. Build Docker sin errores<br>2. `docker-compose -f docker-compose.prod.yml up -d` → healthy<br>3. `curl -k https://localhost/health/` → 200<br>4. `curl -k https://localhost/api/v1/docs/` → 403 (IsAdminUser)<br>5. `curl -k https://localhost/api/v1/auth/token/` → 200 + JWT<br>6. Headers: HSTS, X-Frame-Options, CSP, X-Content-Type-Options, Referrer-Policy<br>7. Cookies: Secure, HttpOnly, SameSite=Lax<br>8. Logs JSON rotativos<br>9. Suite 473 tests en contenedor (PostgreSQL real) |
| **Riesgos** | Complejidad alta; dividir en sub-tareas: 1) production.py, 2) Dockerfile, 3) docker-compose, 4) Nginx |
| **Criterios Aceptación** | Ver `SEC-T001` en `BACKLOG_BRECHAS_SEGURIDAD.md` |
| **Rollback** | `docker-compose down -v`; eliminar archivos creados; restaurar `.env.example` |

---

### REF-006 — Access Token 30 min (ACD)

| Campo | Detalle |
|-------|---------|
| **Problema** | `ACCESS_TOKEN_LIFETIME = timedelta(minutes=60)` vs 30 min ACD |
| **Justificación** | Decisión ACD registrada; ventana exposición 2x mayor |
| **Archivos Afectados** | `settings/base.py:106`, `settings/production.py` |
| **Cambio Propuesto** | `SIMPLE_JWT.ACCESS_TOKEN_LIFETIME = timedelta(minutes=30)` |
| **Dependencias** | REF-001 (JWT_SIGNING_KEY separada — cambio invalida tokens existentes) |
| **Impacto Backend** | Muy bajo — 1 línea |
| **Impacto Frontend** | Bajo — interceptor ya maneja refresh automático (~25 min) |
| **Pruebas Requeridas** | 1. `test_access_token_lifetime_30_minutes` (claim `exp - iat == 1800`)<br>2. `test_access_token_expired_after_31_minutes_rejected` |
| **Riesgos** | Deploy coordinado (invalida tokens existentes → re-login) |
| **Criterios Aceptación** | Config actualizada; test passing; documentado en `SECURITY_CONFIG.md` |
| **Rollback** | Revertir a `timedelta(minutes=60)`; re-deploy |

---

### REF-007 — Validación MIME Real PDF (pikepdf/python-magic)

| Campo | Detalle |
|-------|---------|
| **Problema** | Solo magic bytes `%PDF-`; PDF políglota/malicioso con header válido pasa |
| **Justificación** | SEC-VAL-01 PARCIAL; OWASP: validar estructura archivo real |
| **Archivos Afectados** | `core/adapters/pdf_validation.py`, `requirements.txt`, `Dockerfile` |
| **Cambio Propuesto** | **DEC-001 requerida** (evaluar opciones):<br>**Opción A `python-magic`**: `magic.from_buffer(file.read(2048), mime=True) == "application/pdf"` + `apk add libmagic` en Dockerfile<br>**Opción B `pikepdf`**: `pikepdf.open(io.BytesIO(file.read()))` catch `PdfError` → rechazar (pure Python, ideal Alpine)<br>Integrar en `validar_pdf_completo()` ANTES de guardar |
| **Dependencias** | REF-005 (Dockerfile para libmagic si Opción A); DEC-001 (decisión aprobada) |
| **Impacto Backend** | Medio — nueva dep, lógica validación |
| **Impacto Frontend** | Ninguno — mismo 400 si inválido |
| **Pruebas Requeridas** | 1. `test_pdf_validation_real_mime_passes_valid_pdf`<br>2. `test_pdf_validation_rejects_polyglot_pdf_zip`<br>3. `test_pdf_validation_rejects_corrupted_pdf_structure`<br>4. `test_pdf_validation_docker_compatibility` |
| **Riesgos** | Falsos positivos (PDFs válidos UNL rechazados) — mitigar con corpus prueba real |
| **Criterios Aceptación** | ADR documentado; implementación elegida; tests passing; Docker build OK |
| **Rollback** | Revertir `pdf_validation.py` a solo magic bytes; eliminar dep requirements/Dockerfile |

---

### REF-008 — Throttling Carga Documentos (10/hora/user)

| Campo | Detalle |
|-------|---------|
| **Problema** | Sin límite cargas/hora/user en `POST /api/v1/peticiones/{id}/documento/` |
| **Justificación** | DoS agotamiento almacenamiento; abuso carga masiva (SEC-VAL-02 PENDIENTE) |
| **Archivos Afectados** | `settings/base.py`, `settings/production.py`, `peticiones/views.py` |
| **Cambio Propuesto** | 1. `DEFAULT_THROTTLE_RATES["document_upload"] = "10/hour"` (DEC-003 valor aprobado)<br>2. `PeticionViewSet.cargar_documento`: `throttle_classes = [UserRateThrottle]`, `throttle_scope = "document_upload"` |
| **Dependencias** | Ninguna (independiente, Fase 0) |
| **Impacto Backend** | Bajo — config + 2 líneas en action |
| **Impacto Frontend** | Bajo — mensaje "Límite de cargas alcanzado, espera X minutos" en 429 |
| **Pruebas Requeridas** | 1. `test_document_upload_throttle_allows_10_per_hour`<br>2. `test_document_upload_throttle_11th_returns_429`<br>3. `test_document_upload_throttle_per_user_isolation`<br>4. `test_document_upload_throttle_resets_after_hour` |
| **Criterios Aceptación** | Tests passing; config en base/production; documentado |
| **Rollback** | Eliminar `throttle_classes`/`throttle_scope`; eliminar `document_upload` de `DEFAULT_THROTTLE_RATES` |

---

### REF-009 — Reemplazar Rutas Internas por download_url en Serializers

| Campo | Detalle |
|-------|---------|
| **Problema** | `DocumentoEntregadoSerializer.archivo_path`, `DeclaratoriaAptitudSerializer.archivo_memorando_firmado_path` exponen estructura almacenamiento privado |
| **Justificación** | Fuga info estructura almacenamiento; facilita path traversal si vuln servidor web (SEC-SEC-02 FALLIDO) |
| **Archivos Afectados** | `peticiones/serializers.py`, `resoluciones/serializers.py`, `resoluciones/views.py` (nuevo endpoint download declaratoria) |
| **Cambio Propuesto** | 1. `DocumentoEntregadoSerializer`: remover `archivo_path`, añadir `download_url = SerializerMethodField()` → `request.build_absolute_uri(f"/api/v1/peticiones/{obj.peticion_id}/documento/")`<br>2. `DeclaratoriaAptitudSerializer`: remover `archivo_memorando_firmado_path`, añadir `download_url` → endpoint download declaratoria (DEC-006)<br>3. Endpoints descarga existentes funcionan sin cambios |
| **Dependencias** | REF-005 (endpoint download declaratoria); DEC-006 (endpoint download declaratoria implementado) |
| **Impacto Backend** | Bajo — serializers + nuevo endpoint download declaratoria |
| **Impacto Frontend** | **ALTO** — Migración V-03, V-07, V-08 de `archivo_path` a `download_url` (coordinar con equipo frontend specs/003) |
| **Pruebas Requeridas** | 1. `test_documento_serializer_excludes_archivo_path`<br>2. `test_documento_serializer_includes_download_url`<br>3. `test_declaratoria_serializer_excludes_memorando_path`<br>4. `test_download_url_works_with_auth` |
| **Riesgos** | Coordinación frontend requerida; endpoint download declaratoria debe existir ANTES |
| **Criterios Aceptación** | Serializers actualizados; tests passing; frontend notificado (issue vinculado) |
| **Rollback** | Revertir serializers a versión con `archivo_path`/`archivo_memorando_firmado_path`; eliminar `download_url` |

---

### REF-010 — Handler Global Excepciones + Formato Uniforme

| Campo | Detalle |
|-------|---------|
| **Problema** | Sin `EXCEPTION_HANDLER` global; faltan handlers 409,429,500; formato inconsistente |
| **Justificación** | SEC-LOG-01 PARCIAL; respuestas error inconsistentes; posible fuga 500 |
| **Archivos Afectados** | `core/adapters/exceptions.py` (nuevo), `settings/base.py`, `settings/production.py` |
| **Cambio Propuesto** | 1. `core/adapters/exceptions.py`: `custom_exception_handler(exc, context)` → formato `{error: {code, message, details}}`<br>2. Mapear: `ValidationError`→400 `validation_error`, `AuthenticationFailed`→401 `authentication_failed`, `PermissionDenied`→403 `permission_denied`, `NotFound`→404 `not_found`, `Throttled`→429 `throttled`, `APIException`→status_code, `Exception`→500 `server_error` (sin stack trace)<br>3. `settings/base.py`: `REST_FRAMEWORK.EXCEPTION_HANDLER = "core.adapters.exceptions.custom_exception_handler"`<br>4. Custom exceptions existentes (`EstadoPeticionInvalidoAPI`, etc.) mapeadas automáticamente por status_code |
| **Dependencias** | REF-005 (production.py DEBUG=False para test 500); DEC-009 (mensaje 500 usuario final) |
| **Impacto Backend** | Medio — nuevo archivo, config, actualizar asserts tests |
| **Impacto Frontend** | **MEDIO** — Error handling global debe parsear `response.data.error.{code, message, details}`; deploy coordinado |
| **Pruebas Requeridas** | 1. `test_500_no_stacktrace_leak`<br>2. `test_400_validation_error_format`<br>3. `test_401_authentication_failed_format`<br>4. `test_403_permission_denied_format`<br>5. `test_404_not_found_format`<br>6. `test_429_throttled_format`<br>7. `test_409_conflict_format` (si BE-11) |
| **Riesgos** | Suite 473 tests puede requerir actualizar asserts; deploy coordinado frontend |
| **Criterios Aceptación** | Handler implementado; tests pasando (existentes actualizados + nuevos); formato documentado en `API_ERROR_FORMAT.md` |
| **Rollback** | Eliminar `EXCEPTION_HANDLER` de `REST_FRAMEWORK`; eliminar `exceptions.py`; revertir asserts tests |

---

### REF-011 — Logging Estructurado (JSON, Rotación, Filtros PII)

| Campo | Detalle |
|-------|---------|
| **Problema** | Sin `LOGGING` dict; `print()` en código; sin rotación, filtros PII, formato JSON |
| **Justificación** | SEC-LOG-02 FALLIDO; logs inmanejables, posible fuga PII/tokens |
| **Archivos Afectados** | `settings/base.py`, `settings/production.py`, `settings/local.py`, `core/adapters/logging_filters.py` (nuevo), `requirements.txt` (`python-json-logger`) |
| **Cambio Propuesto** | 1. `requirements.txt`: `python-json-logger>=2.0,<3.0`<br>2. `core/adapters/logging_filters.py`: `SensitiveDataFilter` (elimina `password`, `token`, `authorization`, `credit_card`, `cedula`), `RequestIdFilter` (inyecta `request_id` desde thread-local)<br>3. `base.py`: `LOGGING` dict completo (formatters JSON, handlers `RotatingFileHandler` 10MB/5 backups, loggers `apps.*`, `core.*`, `django.request`, `django.security`, root WARNING)<br>4. `production.py`: Sobrescribe nivel INFO, handlers archivo `/var/log/sgt-siaaf/`<br>5. `local.py`: Nivel DEBUG, handler consola<br>6. `settings/__init__.py`: `logging.config.dictConfig(LOGGING)` al inicio<br>7. Requiere REF-012 (eliminar prints) |
| **Dependencias** | REF-012 (eliminar print en evaluar_checklist.py) |
| **Impacto Backend** | Medio — config extensa, nuevos filtros |
| **Impacto Frontend** | Ninguno — interno logging |
| **Pruebas Requeridas** | 1. `test_logging_structured_json_format`<br>2. `test_logging_no_secrets_in_output` (password no en JSON)<br>3. `test_logging_rotation_max_bytes`<br>4. `test_logging_no_print_in_production_code` (grep print → 0) |
| **Riesgos** | Rutas logs `/var/log/sgt-siaaf/` requieren permisos en Docker; `python-json-logger` dep nueva |
| **Criterios Aceptación** | LOGGING dict en settings; filtros funcionando; rotación verificada; prints eliminados |
| **Rollback** | Eliminar `LOGGING` dict; eliminar `logging_filters.py`; eliminar `python-json-logger` |

---

### REF-012 — Eliminar print() en evaluar_checklist.py

| Campo | Detalle |
|-------|---------|
| **Problema** | `print(f"DEBUG: ...")` en `verificacion/services/evaluar_checklist.py:164,170` expone username, roles, facultad_id en stdout |
| **Justificación** | SEC-LOG-02 FALLIDO; fuga info sensible en contenedor; ejecutado durante tests (visible en output pytest) |
| **Archivos Afectados** | `verificacion/services/evaluar_checklist.py` (líneas 164, 170) |
| **Cambio Propuesto** | 1. `logger = logging.getLogger(__name__)` al inicio<br>2. Línea 164: `logger.debug(f"user={usuario.username}, roles={list(usuario.get_roles())}, ...")`<br>3. Línea 170: `logger.debug(f"user_facultad={user_facultad}, expediente_facultad={expediente_facultad}, match={...}")` |
| **Dependencias** | Ninguna (independiente, Fase 0) |
| **Impacto Backend** | Muy bajo — 3 líneas |
| **Impacto Frontend** | Ninguno |
| **Pruebas Requeridas** | 1. `test_no_print_in_verificacion_services` (grep print → 0)<br>2. Tests `test_evaluar_checklist.py` → logs DEBUG en caplog, no stdout |
| **Criterios Aceptación** | Código limpio; tests passing; `grep -r "print(" src/ --include="*.py" \| grep -v test \| grep -v manage` → vacío |
| **Rollback** | Revertir `logger.debug` a `print` (solo debug temporal) |

---

### REF-013 — Protección Swagger/ReDoc/Schema en Producción

| Campo | Detalle |
|-------|---------|
| **Problema** | `SERVE_PERMISSIONS = ["AllowAny"]` en `base.py:120` — schema público expone superficie ataque |
| **Justificación** | SEC-SWAGGER FALLIDO; OWASP: documentación API no pública en prod |
| **Archivos Afectados** | `settings/production.py`, `settings/local.py`, `settings/test.py` |
| **Cambio Propuesto** | 1. `production.py`: `SPECTACULAR_SETTINGS["SERVE_PERMISSIONS"] = ["rest_framework.permissions.IsAdminUser"]`<br>2. `local.py`/`test.py`: `SERVE_PERMISSIONS = ["rest_framework.permissions.AllowAny"]` (explícito) |
| **Dependencias** | REF-005 (production.py existe) |
| **Impacto Backend** | Muy bajo — 1 línea por entorno |
| **Impacto Frontend** | Bajo — frontend no usa Swagger/ReDoc |
| **Pruebas Requeridas** | 1. `test_swagger_anonymous_denied_in_production_settings` (403)<br>2. `test_swagger_admin_allowed_in_production_settings` (200 staff)<br>3. `test_schema_anonymous_denied_in_production_settings` (403)<br>4. `test_swagger_allowany_in_local_settings` (200) |
| **Criterios Aceptación** | Config por entorno; tests passing; documentado en `SECURITY_CONFIG.md` |
| **Rollback** | Revertir `SERVE_PERMISSIONS` a `AllowAny` en `production.py` |

---

### REF-014 — CI/CD Security (Safety + Bandit + Gitleaks)

| Campo | Detalle |
|-------|---------|
| **Problema** | Sin escaneo automatizado vulnerabilidades en CI/CD |
| **Justificación** | SEC-DEPS PENDIENTE; detección automática CVEs, SAST, secretos Git |
| **Archivos Afectados** | `.github/workflows/security.yml` (nuevo), `.bandit`, `.gitleaksignore` |
| **Cambio Propuesto** | `.github/workflows/security.yml`:<br>```yaml<br>jobs:<br>  safety:<br>    runs-on: ubuntu-latest<br>    steps:<br>      - uses: actions/checkout@v4<br>      - uses: actions/setup-python@v5 (python 3.12)<br>      - run: pip install safety<br>      - run: safety check -r requirements.txt -r requirements-dev.txt --json<br>  bandit:<br>    runs-on: ubuntu-latest<br>    steps:<br>      - uses: actions/checkout@v4<br>      - uses: actions/setup-python@v5<br>      - run: pip install bandit<br>      - run: bandit -r src/ -x tests,migrations -f json -o bandit-report.json \|\| true<br>      - run: grep -q '"severity": "HIGH"\|"MEDIUM"' bandit-report.json && exit 1<br>  gitleaks:<br>    runs-on: ubuntu-latest<br>    steps:<br>      - uses: actions/checkout@v4 (fetch-depth: 0)<br>      - uses: gitleaks/gitleaks-action@v2 (config: .gitleaksignore)<br>```<br>Jobs en PR y push a main; fallan si hallazgos severos |
| **Dependencias** | REF-005 (Dockerfile para CI env consistente) |
| **Impacto Backend** | Pipeline interno |
| **Impacto Frontend** | Ninguno |
| **Pruebas Requeridas** | 1. `safety check` local → 0 HIGH/CRITICAL<br>2. `bandit -r src/` local → 0 HIGH/MEDIUM<br>3. `gitleaks detect --source=.` local → 0 hallazgos<br>4. Pipeline CI pasa en PR prueba |
| **Criterios Aceptación** | Pipeline configurado; passing en main; documentado en `CI_SECURITY.md` |
| **Rollback** | Eliminar `security.yml`; deshabilitar jobs |

---

### REF-015 — Dependabot Configurado

| Campo | Detalle |
|-------|---------|
| **Problema** | Sin actualizaciones automáticas dependencias |
| **Justificación** | SEC-DEPS PENDIENTE; ventana exposición CVEs por olvido manual |
| **Archivos Afectados** | `.github/dependabot.yml` (nuevo) |
| **Cambio Propuesto** | `.github/dependabot.yml`:<br>```yaml<br>version: 2<br>updates:<br>  - package-ecosystem: "pip"<br>    directory: "/"<br>    schedule: {interval: "weekly", day: "monday", time: "09:00"}<br>    open-pull-requests-limit: 10<br>    allow: [{dependency-type: "direct"}]<br>    automerge: true (para version-update:semver-patch)<br>    labels: ["dependencies", "security"]<br>    reviewers: ["tech-lead"]<br>    assignees: ["tech-lead"]<br>``` |
| **Dependencias** | REF-014 (CI tests para auto-merge) |
| **Impacto Backend** | Pipeline interno |
| **Impacto Frontend** | Ninguno |
| **Pruebas Requeridas** | 1. Merge `dependabot.yml` → Dependabot activo<br>2. Verificar PR generado para dep desactualizada (simular) |
| **Criterios Aceptación** | Config mergeada; Dependabot activo; primer PR auto-procesado |
| **Rollback** | Eliminar `dependabot.yml`; deshabilitar Dependabot en repo settings |

---

### REF-016 — Cobertura Tests + testpaths Correcto + fail_under

| Campo | Detalle |
|-------|---------|
| **Problema** | `testpaths = ["src/apps"]` excluye `src/core/tests`; sin `--cov-fail-under` |
| **Justificación** | Cobertura no medida; gaps sin detectar; testpaths engañoso |
| **Archivos Afectados** | `backend/pyproject.toml` |
| **Cambio Propuesto** | ```toml<br>[tool.pytest.ini_options]<br>testpaths = ["src"]  # Incluye src/apps, src/core, src/config<br>addopts = "--cov=src --cov-fail-under=80 --cov-report=term-missing"<br>```<br>`[tool.coverage.run]` omit patterns mantenidos |
| **Dependencias** | Ninguna (independiente, Fase 0) |
| **Impacto Backend** | Configuración pytest |
| **Impacto Frontend** | Ninguno |
| **Pruebas Requeridas** | 1. `pytest` → coverage report ≥80% overall<br>2. `pytest --collect-only` → incluye `src/core/adapters/tests/`<br>3. Módulos críticos (`authentication`, `peticiones`, `verificacion`, `core.adapters`) ≥90% |
| **Criterios Aceptación** | Config actualizada; coverage ≥80% en CI; documentado en `TESTING.md` |
| **Rollback** | Revertir `testpaths` a `["src/apps"]`; eliminar `addopts` coverage |

---

### REF-017 — Tests Seguridad Faltantes

| Campo | Detalle |
|-------|---------|
| **Problema** | Controles implementados sin tests: throttling, rotación/blacklist, IP auditoría real, Swagger prod |
| **Justificación** | Controles sin validación automática → regresión silenciosa |
| **Archivos Afectados** | `auth/tests/test_security_controls.py` (nuevo), `notificaciones/tests/test_audit_ip.py` (nuevo), `auth/tests/test_swagger_protection.py` (nuevo), `peticiones/tests/test_upload_throttle.py` (nuevo), `core/adapters/tests/test_exceptions.py` (nuevo) |
| **Cambio Propuesto** | 1. `auth/tests/test_security_controls.py`: tests throttling login, rotación/blacklist/logout, lifetime 30min, JWT key separada<br>2. `notificaciones/tests/test_audit_ip.py`: tests IP con proxy trusted, spoofing bloqueado, IP persistida<br>3. `auth/tests/test_swagger_protection.py`: tests Swagger/schema 403 anónimo prod, 200 admin<br>4. `peticiones/tests/test_upload_throttle.py`: tests throttling carga docs<br>5. `core/adapters/tests/test_exceptions.py`: tests handler global (500, 400, 401, 403, 404, 429 formato uniforme) |
| **Dependencias** | REF-002, REF-003, REF-004, REF-010, REF-013 (controles deben existir) |
| **Impacto Backend** | Tests nuevos |
| **Impacto Frontend** | Ninguno |
| **Pruebas Requeridas** | Los tests mismos son la verificación; suite completa 473+ passing en CI |
| **Criterios Aceptación** | Tests creados, passing, integrados en `pytest` collection |
| **Rollback** | Eliminar archivos test creados (no revertir controles) |

---

### REF-018 — Procedimiento Rotación Secretos Documentado

| Campo | Detalle |
|-------|---------|
| **Problema** | Sin procedimiento documentado rotación `SECRET_KEY` y `JWT_SIGNING_KEY` |
| **Justificación** | Sin procedimiento → rotación reactiva y propensa a errores |
| **Archivos Afectados** | `SECURITY_CONFIG.md` (nuevo o sección) |
| **Cambio Propuesto** | Documentar:<br>1. Procedimiento rotación `SECRET_KEY`: generar (`openssl rand -base64 32`), deploy rolling (ventana solape 10 min), verificar login/sesiones admin, renombrar, revocar antigua<br>2. Procedimiento rotación `JWT_SIGNING_KEY`: generar, deploy, invalidación tokens (re-login users), verificar<br>3. Checklist verificación post-rotación<br>4. Responsable, frecuencia (anual o tras incidente) |
| **Dependencias** | REF-001 (JWT_SIGNING_KEY separada) |
| **Impacto Backend** | Documentación |
| **Impacto Frontend** | Ninguno |
| **Pruebas Requeridas** | Simulación staging (rotar claves → login funciona → sesiones admin OK) |
| **Criterios Aceptación** | Documento mergeado; equipo notificado |
| **Rollback** | (Documentación — no requiere rollback técnico) |

---

### REF-019 — Limpieza Archivos Huérfanos (Management Command)

| Campo | Detalle |
|-------|---------|
| **Problema** | Versiones `es_vigente=False` permanecen en disco sin job limpieza; archivos sin registro DB |
| **Justificación** | Fuga almacenamiento largo plazo; inconsistencia DB-disco |
| **Archivos Afectados** | `peticiones/management/commands/limpiar_archivos_huerfanos.py` (nuevo), `Dockerfile` (cron) |
| **Cambio Propuesto** | 1. Command `--dry-run` lista huérfanos (archivos sin registro DB + `es_vigente=False` > 90 días DEC-005)<br>2. Sin flag elimina/mueve a quarantine<br>3. Log JSON con archivos procesados, bytes liberados<br>4. Cron en Dockerfile/entrypoint: `0 3 * * * python manage.py limpiar_archivos_huerfanos` |
| **Dependencias** | REF-005 (Dockerfile cron); DEC-005 (retención 90 días aprobada) |
| **Impacto Backend** | Operaciones |
| **Impacto Frontend** | Ninguno |
| **Pruebas Requeridas** | 1. Crear archivo huérfano manual → command detecta<br>2. `--dry-run` no elimina; sin flag elimina<br>3. Verificar no elimina archivos vigentes |
| **Criterios Aceptación** | Command implementado, testeado, documentado en `OPERATIONS.md` |
| **Rollback** | Eliminar command; eliminar cron Dockerfile |

---

### REF-020 — Verificación PermissionError Docker

| Campo | Detalle |
|-------|---------|
| **Problema** | `PermissionError` histórico en almacenamiento privado no reproducido/verificado |
| **Justificación** | Solo afecta si permisos volumen mal configurados; requiere Docker real |
| **Archivos Afectados** | `DEPLOY_PRODUCTION.md`, `docker-compose.prod.yml`, `Dockerfile` |
| **Cambio Propuesto** | 1. Staging con volumen `media_private` montado<br>2. Script test concurrente (10 hilos, 50 ops c/u) → 0 PermissionError<br>3. Documentar UID/GID requeridos, `chown` en entrypoint si necesario |
| **Dependencias** | REF-005 (Dockerfile + docker-compose.prod.yml) |
| **Impacto Backend** | Operaciones/Validación |
| **Impacto Frontend** | Ninguno |
| **Pruebas Requeridas** | Test carga concurrente en staging → 0 PermissionError |
| **Criterios Aceptación** | Documentado en `DEPLOY_PRODUCTION.md`; verificado en staging |
| **Rollback** | (Documentación/validación — no requiere rollback técnico) |

---

### REF-021 — Evidencias ACD 4 Reales

| Campo | Detalle |
|-------|---------|
| **Problema** | Identificadores `a1b2c3d`, `e4f5g6h`, `i7j8k9l`, `m0n1o2p`, `q3r4s5t` parecen placeholders; no existen en Git |
| **Justificación** | Trazabilidad individual incompleta; no bloquea producción |
| **Archivos Afectados** | `MATRIZ_TRAZABILIDAD_SEGURIDAD.md` (sección 11) |
| **Cambio Propuesto** | Consultar Coordinador Académico/Responsable: ¿placeholders o datos reales?<br>Si placeholders → marcar "NO APLICA"/"CANCELADA"<br>Si reales → actualizar matriz con SHA commits, URLs PRs, autores, archivos, tests |
| **Dependencias** | Ninguna |
| **Impacto Backend** | Ninguno |
| **Impacto Frontend** | Ninguno |
| **Pruebas Requeridas** | Verificación manual en Git platform (GitHub/GitLab) |
| **Criterios Aceptación** | Matriz actualizada con evidencias reales O tarea marcada NO APLICA |
| **Rollback** | (Documentación — no rollback técnico) |

---

## Priorización y Secuencia de Ejecución

| Orden | Refactorización | Fase | Bloqueada Por |
|-------|-----------------|------|---------------|
| 1 | REF-001 (JWT Key) | 0 | — |
| 2 | REF-008 (Throttling upload) | 0 | — |
| 3 | REF-012 (Print cleanup) | 0 | — |
| 4 | REF-016 (Cobertura tests) | 0 | — |
| 5 | REF-021 (Evidencias ACD 4) | 0 | — |
| 6 | **REF-005 (Producción completa)** | **1** | **REF-001, REF-004, REF-007, REF-010, REF-011, REF-013** |
| 7 | REF-002 (Rotación tokens) | 1 | REF-001 |
| 8 | REF-006 (Token 30min) | 1 | REF-001 |
| 9 | REF-004 (IP Auditoría) | 1 | REF-005 |
| 10 | REF-003 (Throttling login) | 2 | REF-004 |
| 11 | REF-007 (MIME real) | 3 | REF-005, DEC-001 |
| 12 | REF-009 (download_url) | 3 | REF-005, DEC-006 |
| 13 | REF-010 (Exception handler) | 3 | REF-005, DEC-009 |
| 14 | REF-011 (Logging) | 3 | REF-005, REF-012 |
| 14 | REF-013 (Swagger protection) | 4 | REF-005 |
| 15 | REF-014 (CI/CD Security) | 4 | REF-005 |
| 16 | REF-015 (Dependabot) | 4 | REF-014 |
| 17 | REF-017 (Tests seguridad) | 5 | REF-002, REF-003, REF-004, REF-013 |
| 18 | REF-018 (Proc rotación) | 6 | REF-001 |
| 19 | REF-019 (Limpieza huérfanos) | 6 | REF-005, DEC-005 |
| 20 | REF-020 (PermissionError Docker) | 6 | REF-005 |

---

## Criterios Generales de Validación

Para cada refactorización, antes de marcar "Completada":

1. ✅ **Tests obligatorios passing** (incluyendo nuevos)
2. ✅ **Regresión suite completa** (473 tests passing)
3. ✅ **Verificación compatibilidad frontend** (ver `MATRIZ_COMPATIBILIDAD_BACKEND_FRONTEND_SEGURIDAD.md`)
4. ✅ **Evidencias documentadas** (archivos, comandos, resultados tests)
5. ✅ **Rollback documentado y probado** (en entorno staging)
6. ✅ **Autorización expresa del responsable** para iniciar siguiente

---

**Firma:** opencode AI Assistant  
**Fecha:** 2026-11-05  
**Estado:** Planificación completa — Esperando autorizaciones para iniciar Fase 0 (REF-001, REF-008, REF-012, REF-016, REF-021).