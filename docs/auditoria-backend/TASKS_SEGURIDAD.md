# TAREAS DE SEGURIDAD — SGT-SIAAF Backend

**Versión:** 1.0  
**Fecha:** 2026-11-05  
**Fuente:** Auditoría seguridad (`AUDITORIA_SEGURIDAD.md`, `BACKLOG_BRECHAS_SEGURIDAD.md`, `CHECKLIST_SEGURIDAD_DETALLADA.md`)  
**Formato:** IDs `SEC-T001` a `SEC-T021` — Conservados del backlog original

---

## Resumen de Tareas

| ID | Título | Prioridad | Riesgo | Estado | Fase |
|----|--------|-----------|--------|--------|------|
| SEC-T001 | Configuración Producción Completa | CRÍTICA | CRÍTICO | Pendiente | 1 |
| SEC-T002 | Throttling Login (5/min/IP) | ALTA | ALTO | Pendiente | 2 |
| SEC-T003 | Rotación + Blacklist Refresh Tokens | ALTA | ALTO | Pendiente | 2 |
| SEC-T004 | JWT_SIGNING_KEY Separada de SECRET_KEY | ALTA | ALTO | Pendiente | 0 |
| SEC-T005 | IP Auditoría + Middleware Thread-Local + TRUSTED_PROXIES | ALTA | ALTO | Pendiente | 1 |
| SEC-T006 | Access Token 30 min (ACD) | MEDIA | MEDIO | Pendiente | 2 |
| SEC-T007 | Validación MIME Real (python-magic/pikepdf) | MEDIA | MEDIO | Pendiente | 3 |
| SEC-T008 | Throttling Carga Documentos (10/hora/user) | MEDIA | MEDIO | Pendiente | 0 |
| SEC-T009 | Reemplazar Rutas Internas por download_url en Serializers | MEDIA | MEDIO | Pendiente | 3 |
| SEC-T010 | Handler Global Excepciones + Formato Uniforme | MEDIA | MEDIO | Pendiente | 3 |
| SEC-T011 | Logging Estructurado (JSON, Rotación, Filtros PII) | MEDIA | MEDIO | Pendiente | 3 |
| SEC-T012 | Eliminar print() en evaluar_checklist.py | MEDIA | MEDIO | Pendiente | 0 |
| SEC-T013 | Protección Swagger/ReDoc/Schema en Producción | MEDIA | MEDIO | Pendiente | 4 |
| SEC-T014 | CI/CD Security (Safety + Bandit + Gitleaks) | MEDIA | MEDIO | Pendiente | 4 |
| SEC-T015 | Dependabot Configurado | MEDIA | MEDIO | Pendiente | 4 |
| SEC-T016 | Cobertura Tests + testpaths Correcto + fail_under | MEDIA | MEDIO | Pendiente | 0 |
| SEC-T017 | Tests Seguridad Faltantes (Throttling, Rotación, Swagger, IP) | MEDIA | MEDIO | Pendiente | 5 |
| SEC-T018 | Procedimiento Rotación Secretos Documentado | BAJA | BAJO | Pendiente | 6 |
| SEC-T019 | Limpieza Archivos Huérfanos (Management Command) | BAJA | BAJO | Pendiente | 6 |
| SEC-T020 | Verificación PermissionError Docker | BAJA | BAJO | Pendiente | 6 |
| SEC-T021 | Evidencias ACD 4 Reales (Commits/PRs) | BAJA | BAJO | Pendiente | 0 |

---

## Fichas Detalladas por Tarea

### SEC-T001 — Configuración Producción Completa

| Campo | Detalle |
|-------|---------|
| **Descripción** | Crear configuración completa para entorno productivo: `settings/production.py`, `Dockerfile` multi-stage, `docker-compose.prod.yml` con Nginx + PostgreSQL + Backend, certificados TLS, headers seguridad, usuario no-root |
| **Evidencia Origen** | `AUDITORIA_SEGURIDAD.md` §7 (Hardening Producción - CRÍTICO); `CHECKLIST_SEGURIDAD_DETALLADA.md` §7 (todas filas PENDIENTE/FALLIDO) |
| **Prioridad** | **CRÍTICA** |
| **Riesgo** | **CRÍTICO** — Backend no desplegable en producción sin esto |
| **Criterios de Aceptación** | 1. `settings/production.py` hereda de `base.py` con todo hardening (DEBUG=False, SECURE_*, ALLOWED_HOSTS, CSRF/CORS, cookies seguras, LOGGING, TRUSTED_PROXIES)<br>2. `Dockerfile` multi-stage (builder → python:3.12-slim), usuario `appuser` UID 1000, Gunicorn 4 workers, healthcheck `/health/`, entrypoint migra + collectstatic<br>3. `docker-compose.prod.yml`: servicios `backend`, `postgres`, `nginx` (SSL Let's Encrypt/Certbot), volúmenes persistentes `media_private`, `postgres_data`, `nginx_certs`<br>4. Nginx config: `limit_req_zone`, `proxy_set_header X-Forwarded-For`, TLS 1.2+, HSTS, CSP headers, serve static/media solo via backend endpoints<br>5. `.env.example` documentado con todas las variables requeridas |
| **Pruebas Obligatorias** | 1. Build imagen Docker sin errores<br>2. `docker-compose -f docker-compose.prod.yml up -d` levanta servicios healthy<br>3. `curl -k https://localhost/health/` → 200<br>4. `curl -k https://localhost/api/v1/docs/` → 403 (IsAdminUser)<br>5. `curl -k https://localhost/api/v1/auth/token/` con credenciales válidas → 200 + JWT<br>6. Headers seguridad: `Strict-Transport-Security`, `X-Frame-Options`, `Content-Security-Policy`, `X-Content-Type-Options`, `Referrer-Policy`<br>7. Cookies: `Secure`, `HttpOnly`, `SameSite=Lax`<br>8. Logs JSON rotativos en `docker-compose logs backend`<br>9. Suite 473 tests en contenedor (PostgreSQL real) → 0 failed |
| **Dependencias** | SEC-T004 (JWT_SIGNING_KEY), SEC-T005 (IP auditoría + TRUSTED_PROXIES), SEC-T010 (Exception handler), SEC-T011 (Logging), SEC-T013 (Swagger protection) |
| **Impacto Backend-Frontend** | **ALTO** — Cambia URLs base (HTTPS), headers CORS/CSRF, cookies, endpoints Swagger (requieren auth admin). Frontend debe actualizar `API_BASE_URL` a HTTPS, manejar cookies seguras, CSRF token en requests mutantes |
| **Plan de Regresión** | 1. Ejecutar suite completa 473 tests en contenedor staging (PostgreSQL real)<br>2. Verificar flujos críticos: login → expediente → peticiones → carga docs → checklist → informe → declaratoria<br>3. Probar frontend contra backend staging (specs/003 vistas V-01 a V-09) |
| **Criterio de Cierre** | Documento `DEPLOY_PRODUCTION.md` con pasos, variables, checklist verificación; imagen Docker publicada en registry; staging deploy verificado por QA |

---

### SEC-T002 — Throttling en Login (POST /api/v1/auth/token/)

| Campo | Detalle |
|-------|---------|
| **Descripción** | Implementar rate limiting 5 requests/minuto/IP en endpoint de obtención de token JWT. Usar `AnonRateThrottle` con scope `auth` |
| **Evidencia Origen** | `CHECKLIST_SEC-AUTH-01` (PENDIENTE); `MATRIZ_TRAZABILIDAD A1` (PENDIENTE); `AUDITORIA_SEGURIDAD.md` §1 |
| **Prioridad** | **ALTA** |
| **Riesgo** | **ALTO** — Fuerza bruta / credential stuffing sin límite |
| **Criterios de Aceptación** | 1. `REST_FRAMEWORK.DEFAULT_THROTTLE_RATES["auth"] = "5/minute"` en `base.py` y `production.py`<br>2. `TokenPairView` usa `throttle_classes = [AnonRateThrottle]` con `throttle_scope = "auth"`<br>3. Request 6 en <1 min → HTTP 429 `{"detail": "Request was throttled. Expected available in X seconds."}`<br>4. Throttle por IP real (respetando `X-Forwarded-For` validado por `TRUSTED_PROXIES` — ver SEC-T005) |
| **Pruebas Obligatorias** | 1. `test_login_throttle_allows_5_requests_per_minute` — 5 POST sucesivos → 200<br>2. `test_login_throttle_6th_request_returns_429` — 6º POST → 429<br>3. `test_login_throttle_resets_after_window` — esperar 61 seg → 200<br>4. `test_login_throttle_per_ip_isolation` — IP A agota, IP B sigue teniendo 5<br>5. `test_login_throttle_respects_trusted_proxies` — `X-Forwarded-For` válido vs spoofed |
| **Dependencias** | SEC-T005 (TRUSTED_PROXIES + middleware thread-local para IP real) |
| **Impacto Backend-Frontend** | **BAJO** — Frontend solo recibe 429 en login masivo; debe mostrar mensaje "Demasiados intentos, espera X minutos" |
| **Plan de Regresión** | Ejecutar tests auth existentes (`test_jwt.py` 6 tests) + nuevos tests throttling. Verificar login normal funciona |
| **Criterio de Cierre** | Tests pasando; configuración en `base.py` y `production.py`; documentado en `SECURITY_CONFIG.md` |

---

### SEC-T003 — Rotación y Blacklist de Refresh Tokens

| Campo | Detalle |
|-------|---------|
| **Descripción** | Habilitar rotación automática de refresh tokens (`ROTATE_REFRESH_TOKENS=True`) y blacklist de tokens rotados (`BLACKLIST_AFTER_ROTATION=True`). Instalar y migrar `rest_framework_simplejwt.token_blacklist`. Implementar endpoint `POST /api/v1/auth/logout/` que añade refresh token a blacklist |
| **Evidencia Origen** | `CHECKLIST SEC-AUTH-02` (FALLIDO/PENDIENTE); `MATRIZ_TRAZABILIDAD A2,A3,A6` (FALLIDO/PENDIENTE); `AUDITORIA_SEGURIDAD.md` §1 |
| **Prioridad** | **ALTA** |
| **Riesgo** | **ALTO** — Refresh token robado = acceso indefinido sin rotación ni revocación |
| **Criterios de Aceptación** | 1. `INSTALLED_APPS` incluye `"rest_framework_simplejwt.token_blacklist"`<br>2. `SIMPLE_JWT.ROTATE_REFRESH_TOKENS = True`, `BLACKLIST_AFTER_ROTATION = True`<br>3. Migraciones `token_blacklist` ejecutadas (`python manage.py migrate`)<br>4. Refresh token usado → nuevo access + nuevo refresh; refresh anterior añadido a `OutstandingToken` + `BlacklistedToken`<br>5. Reutilizar refresh anterior → 401 `Token is blacklisted`<br>6. Endpoint `POST /api/v1/auth/logout/` (requiere auth) recibe `{"refresh": "..."}` → añade a blacklist → 205 Reset Content<br>7. Logout invalida refresh → posterior refresh con mismo token → 401 |
| **Pruebas Obligatorias** | 1. `test_refresh_rotates_token_returns_new_access_and_refresh` — refresh válido → nuevo access ≠ anterior, nuevo refresh ≠ anterior<br>2. `test_old_refresh_rejected_after_rotation` — usar refresh anterior → 401 blacklisted<br>3. `test_blacklisted_refresh_rejected` — POST /logout/ con refresh → posterior refresh con mismo → 401<br>4. `test_logout_requires_authentication` — sin token → 401<br>5. `test_refresh_token_lifetime_respected` — refresh expira a 24h → 401 |
| **Dependencias** | SEC-T004 (JWT_SIGNING_KEY separada — rotación usa misma clave firma) |
| **Impacto Backend-Frontend** | **MEDIO** — Frontend debe: 1) Guardar nuevo refresh token tras cada refresh (interceptor axios), 2) Llamar `POST /auth/logout/` al cerrar sesión, 3) Manejar 401 en refresh → redirigir a login |
| **Plan de Regresión** | 1. Tests JWT existentes (`test_jwt.py` 6 tests) + nuevos tests rotación/blacklist/logout<br>2. Flujo login → acceso recurso → refresh → acceso → logout → intento refresh → 401 |
| **Criterio de Cierre** | Migraciones aplicadas; tests pasando; endpoint logout documentado en OpenAPI; frontend actualizado (issue separado) |

---

### SEC-T004 — Clave de Firma JWT Separada de SECRET_KEY

| Campo | Detalle |
|-------|---------|
| **Descripción** | Separar `JWT_SIGNING_KEY` de `SECRET_KEY` mediante variable de entorno dedicada. `SECRET_KEY` para Django (sesiones, CSRF, cookies); `JWT_SIGNING_KEY` para firmar/verificar JWTs |
| **Evidencia Origen** | `CHECKLIST SEC-SEC-01` (FALLIDO); `MATRIZ_TRAZABILIDAD D4` (FALLIDO); `AUDITORIA_SEGURIDAD.md` §4 |
| **Prioridad** | **ALTA** |
| **Riesgo** | **ALTO** — Compromiso SECRET_KEY permite forjar JWTs Y firmar cookies/sesiones Django |
| **Criterios de Aceptación** | 1. `JWT_SIGNING_KEY = env("JWT_SIGNING_KEY")` en `base.py` (SIMPLE_JWT.SIGNING_KEY)<br>2. `SECRET_KEY = env("SECRET_KEY")` sin cambios<br>3. `production.py` valida que ambas existan y sean distintas (warning/log si iguales)<br>4. `.env.example` documenta ambas variables con instrucciones generación (`openssl rand -base64 32`)<br>5. Rotación de `JWT_SIGNING_KEY` no invalida sesiones Django (cookies) |
| **Pruebas Obligatorias** | 1. `test_jwt_signing_key_separate_from_secret_key` — `SIMPLE_JWT.SIGNING_KEY != SECRET_KEY`<br>2. `test_jwt_token_verification_uses_jwt_signing_key` — token firmado con JWT_SIGNING_KEY válido; firmado con SECRET_KEY → 401<br>3. `test_django_sessions_use_secret_key` — sesión/cookie firmada con SECRET_KEY funciona independientemente |
| **Dependencias** | Ninguna (independiente) |
| **Impacto Backend-Frontend** | **NINGUNO** — Cambio interno de clave; tokens JWT existentes se invalidan (requiere re-login único tras deploy) |
| **Plan de Regresión** | 1. Deploy staging con nuevas claves → login funciona → tokens nuevos válidos<br>2. Verificar sesiones Django admin siguen funcionando |
| **Criterio de Cierre** | Variables en `.env.example`; tests pasando; documentado procedimiento rotación independiente en `SECURITY_CONFIG.md` |

---

### SEC-T005 — IP de Auditoría con Middleware Thread-Local y TRUSTED_PROXIES

| Campo | Detalle |
|-------|---------|
| **Descripción** | Implementar captura confiable de IP cliente para auditoría: 1) Middleware que guarda `request` en `thread_local` (`_thread_locals.request = request`), 2) `_get_current_request()` lee de `thread_local`, 3) `_get_client_ip()` valida `X-Forwarded-For` contra `TRUSTED_PROXIES` (lista CIDR en settings), 4) Configurar `SECURE_PROXY_SSL_HEADER` y `TRUSTED_PROXIES` en `production.py` |
| **Evidencia Origen** | `CHECKLIST SEC-LOG-03` (FALLIDO); `MATRIZ_TRAZABILIDAD F9,F10` (FALLIDO/IMPLEMENTADO SIN PRUEBA); `AUDITORIA_SEGURIDAD.md` §6 |
| **Prioridad** | **ALTA** |
| **Riesgo** | **ALTO** — IP suplantable via `X-Forwarded-For` → auditoría poco fiable; trazabilidad comprometida |
| **Criterios de Aceptación** | 1. `core/adapters/middleware.py`: `ThreadLocalRequestMiddleware` (ejecuta primero en MIDDLEWARE)<br>2. `signals.py`: `_get_current_request()` retorna `_thread_locals.request` si existe<br>3. `_get_client_ip(request)`: si `HTTP_X_FORWARDED_FOR` y IP cliente en `TRUSTED_PROXIES` → usa primer IP de `X-Forwarded-For`; sino `REMOTE_ADDR`<br>4. `production.py`: `TRUSTED_PROXIES = env.list("TRUSTED_PROXIES", default=["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"])`<br>5. `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")`<br>6. `EventoAuditoria.ip` poblado correctamente en signals automáticas (crear expediente, cambiar estado, evaluar checklist, cargar doc, emitir informe, registrar declaratoria) |
| **Pruebas Obligatorias** | 1. `test_audit_ip_captured_from_xff_with_trusted_proxy` — request con `X-Forwarded-For: 203.0.113.195, 198.51.100.1` + `REMOTE_ADDR=10.0.0.1` (trusted) → IP = `203.0.113.195`<br>2. `test_audit_ip_spoofing_blocked_untrusted_proxy` — request con `X-Forwarded-For: 203.0.113.195` + `REMOTE_ADDR=203.0.113.195` (no trusted) → IP = `203.0.113.195` (REMOTE_ADDR)<br>3. `test_audit_ip_persisted_in_eventoauditoria` — crear expediente via API → `EventoAuditoria.objects.latest().ip == "203.0.113.195"`<br>4. `test_audit_ip_none_when_no_request` — signal fuera de request (management command) → IP = None |
| **Dependencias** | SEC-T001 (production.py + Nginx config con proxy real) |
| **Impacto Backend-Frontend** | **NINGUNO** — Interno de auditoría |
| **Plan de Regresión** | 1. Tests auditoría existentes (`test_auditoria.py` 14 tests) + nuevos tests IP<br>2. Flujo completo crea eventos → verificar IP en `EventoAuditoria` |
| **Criterio de Cierre** | Middleware en MIDDLEWARE[0]; tests pasando; `TRUSTED_PROXIES` documentado en `.env.example` y `DEPLOY_PRODUCTION.md` |

---

### SEC-T006 — Access Token Lifetime 30 Minutos (ACD)

| Campo | Detalle |
|-------|---------|
| **Descripción** | Cambiar `SIMPLE_JWT.ACCESS_TOKEN_LIFETIME` de 60 a 30 minutos según decisión ACD registrada |
| **Evidencia Origen** | `CHECKLIST SEC-AUTH-03` (FALLIDO); `MATRIZ_TRAZABILIDAD A4` (FALLIDO) |
| **Prioridad** | **MEDIA** (clasificada ALTA en checklist por decisión ACD) |
| **Riesgo** | **MEDIO** — Ventana exposición access token robado 2x mayor a lo aprobado |
| **Criterios de Aceptación** | 1. `ACCESS_TOKEN_LIFETIME = timedelta(minutes=30)` en `base.py` (y `production.py`)<br>2. Token generado tiene claim `exp = iat + 1800 segundos` |
| **Pruebas Obligatorias** | 1. `test_access_token_lifetime_30_minutes` — decodificar access token → `exp - iat == 1800`<br>2. `test_access_token_expired_after_31_minutes_rejected` — token con `exp = now + 31 min` → 401 |
| **Dependencias** | SEC-T004 (JWT_SIGNING_KEY separada — cambiar lifetime invalida tokens existentes) |
| **Impacto Backend-Frontend** | **BAJO** — Frontend debe manejar refresh más frecuente (cada ~25 min); interceptor axios ya debe hacerlo |
| **Plan de Regresión** | Tests JWT existentes + nuevo test lifetime. Verificar login → acceso a los 29 min → OK; a los 31 min → 401 → refresh → OK |
| **Criterio de Cierre** | Configuración actualizada; test pasando; documentado en `SECURITY_CONFIG.md` |

---

### SEC-T007 — Validación MIME Real con python-magic / pikepdf

| Campo | Detalle |
|-------|---------|
| **Descripción** | Evaluar e implementar validación MIME real de contenido PDF más allá de magic bytes: opción A) `python-magic` (libmagic sistema) para detectar MIME real; opción B) `pikepdf` / `PyPDF2` para parsing estructura PDF básica y rechazar malformados/poliglotas. Decidir según compatibilidad Docker (libmagic en alpine/slim) |
| **Evidencia Origen** | `CHECKLIST SEC-VAL-01` (PARCIAL); `MATRIZ_TRAZABILIDAD C3` (PARCIAL); `AUDITORIA_SEGURIDAD.md` §3 |
| **Prioridad** | **MEDIA** |
| **Riesgo** | **MEDIO** — PDF con magic bytes válidos pero estructura maliciosa/poliglota pasa validación actual |
| **Criterios de Aceptación** | 1. Decisión documentada (ADR) con evaluación opciones<br>2. Si `python-magic`: añadido a `requirements.txt`, `libmagic` en Dockerfile, validación `magic.from_buffer(file.read(2048), mime=True) == "application/pdf"`<br>3. Si `pikepdf`: `pikepdf.open(io.BytesIO(file.read()))` → catch `PdfError` → rechazar<br>4. Validación integrada en `validar_pdf_completo()` ANTES de guardar<br>5. Tests: PDF válido pasa; PDF poliglota (PDF+ZIP) rechazado; PDF corrupto rechazado |
| **Pruebas Obligatorias** | 1. `test_pdf_validation_real_mime_passes_valid_pdf` — PDF real → pasa<br>2. `test_pdf_validation_rejects_polyglot_pdf_zip` — PDF+ZIP → rechaza (MIME application/zip o estructura inválida)<br>3. `test_pdf_validation_rejects_corrupted_pdf_structure` — PDF con xref corrupto → rechaza<br>4. `test_pdf_validation_docker_compatibility` — build Dockerfile con libmagic/pikepdf → éxito |
| **Dependencias** | SEC-T001 (Dockerfile para libmagic) |
| **Impacto Backend-Frontend** | **NINGUNO** — Validación interna; mismo contrato API (400 si inválido) |
| **Plan de Regresión** | Tests PDF existentes (25+ tests) + nuevos tests MIME real. Verificar carga docs normal sigue funcionando |
| **Criterio de Cierre** | ADR documentado; implementación elegida; tests pasando; Docker build exitoso |

---

### SEC-T008 — Throttling Carga Documentos (10/hora/usuario)

| Campo | Detalle |
|-------|---------|
| **Descripción** | Implementar rate limiting en `POST /api/v1/peticiones/{id}/documento/`: 10 cargas por hora por usuario autenticado. Usar `UserRateThrottle` con scope `document_upload` |
| **Evidencia Origen** | `CHECKLIST SEC-VAL-02` (PENDIENTE); `MATRIZ_TRAZABILIDAD C7` (PENDIENTE) |
| **Prioridad** | **MEDIA** |
| **Riesgo** | **MEDIO** — DoS agotamiento almacenamiento; abuso carga masiva |
| **Criterios de Aceptación** | 1. `REST_FRAMEWORK.DEFAULT_THROTTLE_RATES["document_upload"] = "10/hour"` en `base.py`/`production.py`<br>2. `PeticionViewSet.cargar_documento` usa `throttle_classes = [UserRateThrottle]`, `throttle_scope = "document_upload"`<br>3. Request 11 en <1 hora → HTTP 429<br>4. Throttle por usuario autenticado (no IP) |
| **Pruebas Obligatorias** | 1. `test_document_upload_throttle_allows_10_per_hour` — 10 POST → 201<br>2. `test_document_upload_throttle_11th_returns_429` — 11º POST → 429<br>3. `test_document_upload_throttle_per_user_isolation` — Usuario A agota, Usuario B tiene 10<br>4. `test_document_upload_throttle_resets_after_hour` — esperar 61 min → 201 |
| **Dependencias** | Ninguna (independiente) |
| **Impacto Backend-Frontend** | **BAJO** — Frontend muestra mensaje "Límite de cargas alcanzado, espera X minutos" en 429 |
| **Plan de Regresión** | Tests carga docs existentes + nuevos tests throttling. Verificar carga normal funciona |
| **Criterio de Cierre** | Tests pasando; configuración en `base.py`/`production.py`; documentado |

---

### SEC-T009 — Remover Rutas Internas de Serializers (archivo_path, archivo_memorando_firmado_path)

| Campo | Detalle |
|-------|---------|
| **Descripción** | Eliminar campos `archivo_path` (DocumentoEntregadoSerializer) y `archivo_memorando_firmado_path` (DeclaratoriaAptitudSerializer) de respuestas API. Sustituir por `download_url` opaco que apunte al endpoint de descarga autorizada (`/api/v1/peticiones/{id}/documento/` o `/api/v1/declaratorias/{id}/documento/`) |
| **Evidencia Origen** | `CHECKLIST SEC-SEC-02` (FALLIDO); `MATRIZ_TRAZABILIDAD C8` (FALLIDO); `AUDITORIA_SEGURIDAD.md` §4 |
| **Prioridad** | **MEDIA** |
| **Riesgo** | **MEDIO** — Fuga estructura almacenamiento privado; facilita path traversal si hay vuln en servidor web |
| **Criterios de Aceptación** | 1. `DocumentoEntregadoSerializer`: remover `archivo_path`; añadir `download_url = SerializerMethodField()` → `request.build_absolute_uri(f"/api/v1/peticiones/{obj.peticion_id}/documento/")`<br>2. `DeclaratoriaAptitudSerializer`: remover `archivo_memorando_firmado_path`; añadir `download_url` → endpoint declaratoria download (por crear)<br>3. Endpoints de descarga existentes funcionan sin cambios<br>4. Frontend actualizado para usar `download_url` (issue separado) |
| **Pruebas Obligatorias** | 1. `test_documento_serializer_excludes_archivo_path` — `archivo_path` not in response.data<br>2. `test_documento_serializer_includes_download_url` — `download_url` present, correct format<br>3. `test_declaratoria_serializer_excludes_memorando_path` — idem<br>4. `test_download_url_works_with_auth` — GET download_url + JWT → 200 PDF |
| **Dependencias** | SEC-T001 (endpoints download declaratoria — ver resoluciones/views.py) |
| **Impacto Backend-Frontend** | **MEDIO** — Frontend debe migrar de `archivo_path` a `download_url` en componentes de descarga (V-03, V-07, V-08). Coordinar con equipo frontend (specs/003) |
| **Plan de Regresión** | Tests serializers existentes + nuevos tests campos. Verificar descarga vía endpoint sigue funcionando |
| **Criterio de Cierre** | Serializers actualizados; tests pasando; frontend notificado (issue vinculado) |

---

### SEC-T010 — Handler Global de Excepciones (Formato Uniforme)

| Campo | Detalle |
|-------|---------|
| **Descripción** | Implementar `custom_exception_handler` en `core/adapters/exceptions.py` que estandarice respuestas de error: `{ "error": { "code": "string", "message": "string", "details": {} } }`. Mapear: `ValidationError`→400, `AuthenticationFailed`→401, `PermissionDenied`→403, `NotFound`→404, `Throttled`→429, `APIException`→status_code, `Exception`→500 (sin stack trace). Registrar en `REST_FRAMEWORK.EXCEPTION_HANDLER` |
| **Evidencia Origen** | `CHECKLIST SEC-LOG-01` (PARCIAL); `MATRIZ_TRAZABILIDAD F1,F4,F5` (PARCIAL); `AUDITORIA_SEGURIDAD.md` §6 |
| **Prioridad** | **MEDIA** |
| **Riesgo** | **MEDIO** — Respuestas error inconsistentes; posible fuga en 500 si DEBUG mal configurado |
| **Criterios de Aceptación** | 1. `core/adapters/exceptions.py` con `custom_exception_handler(exc, context)`<br>2. Formato uniforme para todos los códigos (400,401,403,404,409,429,500)<br>3. 500 NUNCA incluye stack trace, SQL, rutas internas<br>4. `REST_FRAMEWORK.EXCEPTION_HANDLER = "core.adapters.exceptions.custom_exception_handler"` en `base.py`<br>5. Custom APIExceptions existentes (`EstadoPeticionInvalidoAPI`, `UsuarioNoAutorizadoAPI`, `ValidacionPDF_API`) mapeadas correctamente |
| **Pruebas Obligatorias** | 1. `test_500_no_stacktrace_leak` — provocar 500 (ej. division by zero en vista) → response 500 sin `traceback`, `stack`, `file`, `line`<br>2. `test_400_validation_error_format` — POST data inválida → 400 con formato uniforme<br>3. `test_401_authentication_failed_format` — token inválido → 401 formato uniforme<br>4. `test_403_permission_denied_format` — sin permisos → 403 formato uniforme<br>5. `test_404_not_found_format` — recurso inexistente → 404 formato uniforme<br>6. `test_429_throttled_format` — throttling excedido → 429 formato uniforme<br>7. `test_409_conflict_format` — si se implementa 409 (BE-11) → formato uniforme |
| **Dependencias** | SEC-T001 (production.py con DEBUG=False para probar 500 sin trace) |
| **Impacto Backend-Frontend** | **MEDIO** — Frontend debe actualizar manejo de errores para nuevo formato uniforme (code, message, details). Coordinar con equipo frontend |
| **Plan de Regresión** | 1. Ejecutar suite completa 473 tests — todos deben pasar con nuevo formato (o actualizar asserts)<br>2. Verificar endpoints críticos: login, expedientes, peticiones, checklist, resoluciones, notificaciones |
| **Criterio de Cierre** | Handler implementado; tests pasando (existentes actualizados + nuevos); formato documentado en `API_ERROR_FORMAT.md` |

---

### SEC-T011 — Logging Estructurado (LOGGING dict, Rotación, Filtros PII)

| Campo | Detalle |
|-------|---------|
| **Descripción** | Configurar `LOGGING` dict completo en `base.py`/`production.py`: handlers `RotatingFileHandler` (maxBytes=10MB, backupCount=5), formato JSON (`python-json-logger`), nivel INFO en producción/DEBUG en local, filtros que eliminen `password`, `token`, `authorization`, `credit_card`, `cedula` de logs. Loggers por módulo (`apps.*`, `core.*`, `django.request`, `django.security`) |
| **Evidencia Origen** | `CHECKLIST SEC-LOG-02` (PENDIENTE/FALLIDO); `MATRIZ_TRAZABILIDAD F6,F7,F8` (PENDIENTE/FALLIDO); `AUDITORIA_SEGURIDAD.md` §6 |
| **Prioridad** | **MEDIA** |
| **Riesgo** | **MEDIO** — Sin rotación logs llenan disco; sin filtros PII fugan datos sensibles; sin estructura difícil análisis SIEM |
| **Criterios de Aceptación** | 1. `LOGGING` dict en `base.py` con configuración base; `production.py` sobrescribe nivel=INFO, handlers archivo<br>2. Formato JSON: `{"timestamp": "...", "level": "INFO", "logger": "apps.peticiones", "message": "...", "request_id": "...", "user_id": "..."}`<br>3. Filtro `SensitiveDataFilter` elimina campos sensibles de `record.__dict__` y `record.msg`<br>4. `RotatingFileHandler` para `apps`, `core`, `django`, `security` logs separados<br>5. `logging.config.dictConfig(LOGGING)` ejecutado al inicio |
| **Pruebas Obligatorias** | 1. `test_logging_structured_json_format` — log generado → parseable JSON con campos esperados<br>2. `test_logging_no_secrets_in_output` — log con `password="secret"` → JSON no contiene "secret"<br>3. `test_logging_rotation_max_bytes` — escribir >10MB → archivo rotado, backup creado<br>4. `test_logging_no_print_in_production_code` — `grep "print(" src/ --include="*.py" | grep -v test | grep -v manage` → 0 resultados |
| **Dependencias** | SEC-T012 (eliminar print en evaluar_checklist.py) |
| **Impacto Backend-Frontend** | **NINGUNO** — Interno de logging |
| **Plan de Regresión** | 1. Deploy staging → generar logs → verificar JSON, rotación, sin secretos<br>2. Tests existentes no rotos por logging |
| **Criterio de Cierre** | LOGGING dict en settings; filtros funcionando; rotación verificada; `print()` eliminado de código producción |

---

### SEC-T012 — Eliminar print() en evaluar_checklist.py

| Campo | Detalle |
|-------|---------|
| **Descripción** | Reemplazar `print(f"DEBUG: ...")` en `src/apps/verificacion/services/evaluar_checklist.py:164,170` con `logger.debug(...)` usando logger del módulo |
| **Evidencia Origen** | `CHECKLIST SEC-LOG-02` (FALLIDO); `MATRIZ_TRAZABILIDAD F7` (FALLIDO); `INFORME_PRUEBAS_SEGURIDAD.md` §5.2 |
| **Prioridad** | **MEDIA** (fácil, rápido) |
| **Riesgo** | **MEDIO** — Fuga username, roles, facultad_id en stdout contenedor |
| **Criterios de Aceptación** | 1. `logger = logging.getLogger(__name__)` al inicio del módulo<br>2. `logger.debug(f"user={usuario.username}, roles={list(usuario.get_roles())}, ...")` en línea 164<br>3. `logger.debug(f"user_facultad={user_facultad}, expediente_facultad={expediente_facultad}, match={...}")` en línea 170<br>4. Sin `print(` en ningún archivo `src/` (excluyendo tests y manage.py) |
| **Pruebas Obligatorias** | 1. `test_no_print_in_verificacion_services` — `grep "print(" src/apps/verificacion/services/` → 0<br>2. Ejecutar tests `test_evaluar_checklist.py` → logs DEBUG aparecen en pytest output (caplog), no en stdout |
| **Dependencias** | Ninguna |
| **Impacto Backend-Frontend** | **NINGUNO** |
| **Plan de Regresión** | Tests verificacion existentes pasando |
| **Criterio de Cierre** | Código limpio; tests pasando; verificado con `grep -r "print(" src/ --include="*.py" | grep -v test | grep -v manage` → vacío |

---

### SEC-T013 — Protección Swagger/ReDoc/Schema en Producción (IsAdminUser)

| Campo | Detalle |
|-------|---------|
| **Descripción** | Cambiar `SPECTACULAR_SETTINGS.SERVE_PERMISSIONS` a `["rest_framework.permissions.IsAdminUser"]` en `production.py`. Mantener `AllowAny` en `local.py` y `test.py` |
| **Evidencia Origen** | `CHECKLIST §8` (FALLIDO); `MATRIZ_TRAZABILIDAD H1-H4` (FALLIDO); `AUDITORIA_SEGURIDAD.md` §8 |
| **Prioridad** | **MEDIA** |
| **Riesgo** | **MEDIO** — Superficie de ataque expuesta (endpoints, modelos, parámetros) |
| **Criterios de Aceptación** | 1. `production.py`: `SPECTACULAR_SETTINGS["SERVE_PERMISSIONS"] = ["rest_framework.permissions.IsAdminUser"]`<br>2. `local.py`/`test.py`: `SERVE_PERMISSIONS = ["rest_framework.permissions.AllowAny"]`<br>3. Anónimo en producción → 403 en `/api/v1/docs/`, `/api/v1/redoc/`, `/api/v1/schema/`<br>4. Admin (staff/superuser) → 200 |
| **Pruebas Obligatorias** | 1. `test_swagger_anonymous_denied_in_production_settings` — con `settings.production` → 403<br>2. `test_swagger_admin_allowed_in_production_settings` — usuario staff → 200<br>3. `test_schema_anonymous_denied_in_production_settings` — 403<br>4. `test_swagger_allowany_in_local_settings` — con `settings.local` → 200 |
| **Dependencias** | SEC-T001 (production.py existe) |
| **Impacto Backend-Frontend** | **BAJO** — Frontend no usa Swagger/ReDoc; solo equipo desarrollo/admin |
| **Plan de Regresión** | Tests existentes de espectacular (si los hay) + nuevos tests. Verificar en staging |
| **Criterio de Cierre** | Configuración por entorno; tests pasando; documentado en `SECURITY_CONFIG.md` |

---

### SEC-T014 — Escaneo Vulnerabilidades en CI/CD (Safety + Bandit + Gitleaks)

| Campo | Detalle |
|-------|---------|
| **Descripción** | Integrar en pipeline CI (GitHub Actions / GitLab CI): 1) `safety check` — falla si vulnerabilidades HIGH/CRITICAL en deps. 2) `bandit -r src/` — falla si issues HIGH/MEDIUM. 3) `gitleaks detect --source=. --verbose` — falla si secretos en historial. Configurar como jobs obligatorios en PR/merge |
| **Evidencia Origen** | `CHECKLIST §9` (PENDIENTE); `MATRIZ_TRAZABILIDAD I1-I3` (PENDIENTE); `AUDITORIA_SEGURIDAD.md` §9 |
| **Prioridad** | **MEDIA** |
| **Riesgo** | **MEDIO** — Deps vulnerables / código inseguro / secretos en Git sin detección automática |
| **Criterios de Aceptación** | 1. `.github/workflows/security.yml` (o `.gitlab-ci.yml`) con jobs `safety`, `bandit`, `gitleaks`<br>2. Jobs corren en cada PR y push a main<br>3. Falla build si hallazgos severos<br>4. `safety` usa `requirements.txt` + `requirements-dev.txt`<br>5. `bandit` excluye `tests/`, `migrations/`<br>6. `gitleaks` escanea historial completo (`--source=.`) |
| **Pruebas Obligatorias** | 1. Ejecutar `safety check` local → 0 vulnerabilidades HIGH/CRITICAL (o documentadas como aceptadas)<br>2. Ejecutar `bandit -r src/` local → 0 HIGH/MEDIUM (o falsos positivos documentados)<br>3. Ejecutar `gitleaks detect --source=.` local → 0 hallazgos (o falsos positivos)<br>4. Pipeline CI pasa en PR de prueba |
| **Dependencias** | SEC-T001 (Dockerfile para CI environment consistente) |
| **Impacto Backend-Frontend** | **NINGUNO** — Pipeline interno |
| **Plan de Regresión** | Ejecutar herramientas manualmente antes de cada release |
| **Criterio de Cierre** | Pipeline configurado; pasando en main; documentado en `CI_SECURITY.md` |

---

### SEC-T015 — Dependabot Configurado

| Campo | Detalle |
|-------|---------|
| **Descripción** | Crear `.github/dependabot.yml` con schedule semanal, auto-merge para patch versions, reviewers asignados, labels `dependencies`, `security` |
| **Evidencia Origen** | `CHECKLIST §9` (PENDIENTE); `MATRIZ_TRAZABILIDAD I4` (PENDIENTE) |
| **Prioridad** | **MEDIA** |
| **Riesgo** | **MEDIO** — Actualizaciones manuales propensas a olvido; ventana exposición CVEs |
| **Criterios de Aceptación** | 1. `.github/dependabot.yml` con `package-ecosystem: "pip"`, `directory: "/"`, `schedule: {interval: "weekly"}`, `open-pull-requests-limit: 10`, `allow: [{dependency-type: "direct"}]`, `automerge: true` para `update-type: "version-update:semver-patch"`<br>2. PRs generados semanalmente; patch auto-merge si tests pasan |
| **Pruebas Obligatorias** | 1. Merge `.github/dependabot.yml` → Dependabot activa en repo<br>2. Verificar PR generado para dependencia desactualizada (simular) |
| **Dependencias** | SEC-T014 (CI tests para auto-merge) |
| **Impacto Backend-Frontend** | **NINGUNO** |
| **Plan de Regresión** | Verificar PRs Dependabot no rompen tests |
| **Criterio de Cierre** | Configuración mergeada; Dependabot activo; primer PR automático procesado |

---

### SEC-T016 — Cobertura Tests + fail_under + testpaths Correcto

| Campo | Detalle |
|-------|---------|
| **Descripción** | 1) Cambiar `testpaths = ["src"]` en `pyproject.toml` para incluir `src/core/tests` explícitamente. 2) Añadir `--cov=src --cov-fail-under=80 --cov-report=term-missing` a pytest config o CI. 3) Configurar `coverage.py` omit patterns (migrations, settings, apps.py, __init__.py) |
| **Evidencia Origen** | `CHECKLIST §11` (PARCIAL); `MATRIZ_TRAZABILIDAD J2,J3` (PARCIAL/PENDIENTE); `INFORME_PRUEBAS_SEGURIDAD.md` §4 |
| **Prioridad** | **MEDIA** |
| **Riesgo** | **MEDIO** — Cobertura no medida; gaps sin detectar; testpaths engañoso |
| **Criterios de Aceptación** | 1. `pyproject.toml`: `testpaths = ["src"]`, `addopts = "--cov=src --cov-fail-under=80 --cov-report=term-missing"`<br>2. `pytest` ejecuta 473+ tests (incluye core/tests) y reporta cobertura ≥80%<br>3. Módulos críticos (`authentication`, `peticiones`, `verificacion`, `core.adapters`) ≥90% |
| **Pruebas Obligatorias** | 1. `pytest` → coverage report ≥80% overall<br>2. `pytest --collect-only` → incluye `src/core/adapters/tests/` |
| **Dependencias** | Ninguna |
| **Impacto Backend-Frontend** | **NINGUNO** |
| **Plan de Regresión** | Ejecutar `pytest` local y CI → coverage pasa |
| **Criterio de Cierre** | Configuración actualizada; coverage ≥80% en CI; documentado en `TESTING.md` |

---

### SEC-T017 — Tests de Seguridad Faltantes (Throttling, Rotación, Swagger, IP Auditoría)

| Campo | Detalle |
|-------|---------|
| **Descripción** | Crear tests para controles implementados en SEC-T002, SEC-T003, SEC-T005, SEC-T013: throttling login/carga, rotación/blacklist/logout JWT, IP auditoría con proxy real, protección Swagger prod |
| **Evidencia Origen** | `INFORME_PRUEBAS_SEGURIDAD.md` §3 (Gaps); `CHECKLIST` controles correspondientes |
| **Prioridad** | **MEDIA** |
| **Riesgo** | **MEDIO** — Controles implementados sin validación automática → regresión silenciosa |
| **Criterios de Aceptación** | 1. Tests en `src/apps/authentication/tests/test_security_controls.py` (nuevo archivo): throttling login, rotación/blacklist, logout, lifetime 30min<br>2. Tests en `src/apps/notificaciones/tests/test_audit_ip.py` (nuevo): IP con proxy trusted, spoofing bloqueado, IP persistida<br>3. Tests en `src/apps/authentication/tests/test_swagger_protection.py` (nuevo): Swagger/schema 403 anónimo prod, 200 admin<br>4. Tests en `src/apps/peticiones/tests/test_upload_throttle.py` (nuevo): throttling carga docs<br>5. Todos los tests nuevos pasan y están en suite CI |
| **Pruebas Obligatorias** | Los tests mismos son la verificación |
| **Dependencias** | SEC-T002, SEC-T003, SEC-T005, SEC-T013 (controles deben existir para testearlos) |
| **Impacto Backend-Frontend** | **NINGUNO** |
| **Plan de Regresión** | Suite completa 473+ tests passing en CI |
| **Criterio de Cierre** | Tests creados, pasando, integrados en `pytest` collection |

---

### SEC-T018 — Procedimiento Documentado Rotación Secretos

| Campo | Detalle |
|-------|---------|
| **Descripción** | Documentar en `SECURITY_CONFIG.md`: procedimiento rotación `SECRET_KEY` y `JWT_SIGNING_KEY` (generación, deploy, ventana solape, revocación antigua, verificación) |
| **Evidencia Origen** | `CHECKLIST SEC-SEC-01` (PENDIENTE); `MATRIZ_TRAZABILIDAD D5` (PENDIENTE) |
| **Prioridad** | **BAJA** |
| **Riesgo** | **BAJO** — Sin procedimiento, rotación reactiva y propensa a errores |
| **Criterios de Aceptación** | Documento con pasos claros, comandos, checklist verificación, responsable, frecuencia (ej. anual o tras incidente) |
| **Pruebas Obligatorias** | Simulación en staging (rotar claves → login funciona → sesiones admin OK) |
| **Dependencias** | SEC-T004 (JWT_SIGNING_KEY separada) |
| **Impacto Backend-Frontend** | **NINGUNO** |
| **Plan de Regresión** | Verificar documento actualizado tras cada rotación real |
| **Criterio de Cierre** | Documento mergeado en repo; equipo notificado |

---

### SEC-T019 — Limpieza Archivos Huérfanos (Management Command)

| Campo | Detalle |
|-------|---------|
| **Descripción** | Crear `management command` `limpiar_archivos_huerfanos`: 1) Archivos en `MEDIA_ROOT/private/` sin registro `DocumentoEntregado` correspondiente → eliminar (o mover a quarantine). 2) Registros `DocumentoEntregado` con `es_vigente=False` mayores a 90 días → opcional eliminar archivo físico (política retención). 3) Programar via cron en contenedor backend (diario 03:00) |
| **Evidencia Origen** | `CHECKLIST §5` (PARCIAL); `MATRIZ_TRAZABILIDAD E6` (PARCIAL); `AUDITORIA_SEGURIDAD.md` §5 |
| **Prioridad** | **BAJA** |
| **Riesgo** | **BAJO** — Fuga almacenamiento a largo plazo; inconsistencia DB-disco |
| **Criterios de Aceptación** | 1. `python manage.py limpiar_archivos_huerfanos --dry-run` lista huérfanos<br>2. `python manage.py limpiar_archivos_huerfanos` elimina/mueve<br>3. Log JSON con archivos procesados, bytes liberados<br>4. Cron configurado en Dockerfile/entrypoint |
| **Pruebas Obligatorias** | 1. Crear archivo huérfano manual → command lo detecta<br>2. Crear DocumentoEntregado sin archivo físico → command lo detecta (opcional)<br>3. `--dry-run` no elimina; sin flag elimina |
| **Dependencias** | SEC-T001 (Dockerfile para cron) |
| **Impacto Backend-Frontend** | **NINGUNO** |
| **Plan de Regresión** | Verificar command no elimina archivos vigentes |
| **Criterio de Cierre** | Command implementado, testeado, documentado en `OPERATIONS.md` |

---

### SEC-T020 — Verificación PermissionError Histórico en Docker

| Campo | Detalle |
|-------|---------|
| **Descripción** | Reproducir y documentar errores históricos `PermissionError` en almacenamiento privado: montar volumen `media_private` con usuario/grupo específicos, ejecutar carga/descarga concurrente, verificar permisos rw para `appuser` (UID 1000). Documentar configuración correcta en `DEPLOY_PRODUCTION.md` |
| **Evidencia Origen** | `CHECKLIST §5` (NO VERIFICABLE); `MATRIZ_TRAZABILIDAD E7` (NO VERIFICABLE); `AUDITORIA_SEGURIDAD.md` §5 |
| **Prioridad** | **BAJA** |
| **Riesgo** | **BAJO** — Solo afecta si permisos volumen mal configurados |
| **Criterios de Aceptación** | 1. Entorno Docker staging con volumen `media_private` montado<br>2. Carga/descarga docs concurrentes (10 hilos) → 0 PermissionError<br>3. Documentar `UID/GID` requeridos, `chown` en entrypoint si necesario |
| **Pruebas Obligatorias** | Test de carga concurrente en staging (script separado) |
| **Dependencias** | SEC-T001 (Dockerfile + docker-compose.prod.yml) |
| **Impacto Backend-Frontend** | **NINGUNO** |
| **Plan de Regresión** | Verificar en cada deploy staging |
| **Criterio de Cierre** | Documentado en `DEPLOY_PRODUCTION.md`; verificado en staging |

---

### SEC-T021 — Evidencias ACD 4 Reales (Commits/PRs)

| Campo | Detalle |
|-------|---------|
| **Descripción** | Sustituir identificadores placeholder (`a1b2c3d`, `e4f5g6h`, `i7j8k9l`, `m0n1o2p`, `q3r4s5t`) por evidencia real: SHA commits, URLs PRs, autores, archivos modificados, tests aportados. Verificar en plataforma Git (GitHub/GitLab) |
| **Evidencia Origen** | `CHECKLIST §12` (NO VERIFICADO); `MATRIZ_TRAZABILIDAD K1-K5` (NO VERIFICADO) |
| **Prioridad** | **BAJA** |
| **Riesgo** | **BAJO** — Trazabilidad individual incompleta; no bloquea producción |
| **Criterios de Aceptación** | Matriz actualizada con datos reales verificables para cada integrante |
| **Pruebas Obligatorias** | Verificación manual en plataforma Git (GitHub/GitLab) |
| **Dependencias** | Ninguna |
| **Impacto Backend-Frontend** | **NINGUNO** |
| **Plan de Regresión** | N/A |
| **Criterio de Cierre** | Matriz `MATRIZ_TRAZABILIDAD_SEGURIDAD.md` actualizada con evidencias reales |

---

## Resumen de Dependencias Críticas

```
SEC-T001 (Producción) ──┬──→ SEC-T004 (JWT Key)
    │                   ├──→ SEC-T005 (IP Auditoría + TRUSTED_PROXIES)
    │                   ├──→ SEC-T007 (python-magic Docker)
    │                   ├──→ SEC-T010 (Exception Handler prod)
    │                   ├──→ SEC-T011 (Logging prod)
    │                   ├──→ SEC-T013 (Swagger prod)
    │                   └──→ SEC-T019, SEC-T020 (Docker ops)
    │
SEC-T004 (JWT Key) ────→ SEC-T003 (Rotación/Blacklist)
    │                   └──→ SEC-T006 (Lifetime 30min)
    │                   └──→ SEC-T018 (Proc. Rotación)
    │
SEC-T005 (IP Auditoría) → SEC-T002 (Throttling login por IP real)
    │
SEC-T002, T003, T005, T013 → SEC-T017 (Tests seguridad)
    │
SEC-T014 (CI Security) → SEC-T015 (Dependabot auto-merge)
    │
SEC-T012 (Print cleanup) → SEC-T011 (Logging sin prints)
```

---

## Criterios Generales de Cierre de Fase

La fase de hardening se considera **cerrada** cuando:

1. ✅ **Tareas CRÍTICAS completadas:** SEC-T001 (producción deployable)
2. ✅ **Tareas ALTAS completadas:** SEC-T002, SEC-T003, SEC-T004, SEC-T005, SEC-T006
3. ✅ **Tareas MEDIAS completadas:** SEC-T007 a SEC-T017 (controles + tests + CI)
4. ⏳ **Tareas BAJAS:** SEC-T018 a SEC-T021 (documentación, ops, trazabilidad) — pueden completarse post-deploy inicial
5. ✅ **Suite de pruebas completa:** 473+ tests passing + nuevos tests seguridad + coverage ≥80% en CI
6. ✅ **Staging deploy verificado:** Backend + Frontend (specs/003) funcionando en entorno idéntico a producción
7. ✅ **Documentación actualizada:** `DEPLOY_PRODUCTION.md`, `SECURITY_CONFIG.md`, `API_ERROR_FORMAT.md`, `CI_SECURITY.md`, `TESTING.md`, `OPERATIONS.md`

---

**Firma:** opencode AI Assistant  
**Fecha:** 2026-11-05  
**Próxima revisión:** Tras implementación SEC-T001 a SEC-T006 (hito "Producción Lista")