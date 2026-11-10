# CHECKLIST DE EJECUCIÓN Y CIERRE — TAREAS DE SEGURIDAD SEC-T001 a SEC-T021

**Fecha:** 2026-11-05  
**Versión:** 1.0  
**Uso:** Control de avance individual por tarea y validación final de seguridad.

---

## Instrucciones de Uso

1. **Una fila por tarea** — Marcar casillas conforme se avanza.
2. **Orden obligatorio** — Respetar dependencias (ver MATRIZ_DEPENDENCIAS_Y_PRIORIZACION.md).
3. **Autorización requerida** — Cada tarea requiere autorización expresa del responsable antes de iniciar.
4. **Evidencia de cierre** — Completar todas las casillas de "Cierre" antes de marcar "Hecha".
5. **No agrupar tareas** — Implementar, probar, cerrar una a una.
6. **Rollback documentado** — Tener procedimiento de reversión listo antes de editar.

---

## Checklist General de Fase

### Fase 0: Preparación Independiente
- [x] **SEC-T004** JWT_SIGNING_KEY Separada — CERRADA (2026-11-05)
- [ ] **SEC-T008** Throttling Carga Documentos
- [ ] **SEC-T012** Eliminar print() evaluar_checklist.py
- [ ] **SEC-T016** Cobertura Tests + testpaths
- [ ] **SEC-T021** Evidencias ACD 4 Reales

### Fase 1: Infraestructura Base Producción (CRÍTICA)
- [ ] **SEC-T001** Configuración Producción Completa

### Fase 2: Autenticación Segura
- [ ] **SEC-T003** Rotación + Blacklist Refresh Tokens
- [ ] **SEC-T006** Access Token 30 min

### Fase 3: IP Auditoría + Throttling Login
- [ ] **SEC-T005** IP Auditoría + Middleware + TRUSTED_PROXIES
- [ ] **SEC-T002** Throttling Login

### Fase 4: Controles Medios + Errores/Logging
- [ ] **SEC-T007** Validación MIME Real
- [ ] **SEC-T009** Remover Rutas Internas Serializers
- [ ] **SEC-T010** Handler Global Excepciones
- [ ] **SEC-T011** Logging Estructurado

### Fase 5: Protección Documentación + CI/CD
- [ ] **SEC-T013** Protección Swagger/ReDoc/Schema
- [ ] **SEC-T014** CI/CD Security (Safety+Bandit+Gitleaks)
- [ ] **SEC-T015** Dependabot Configurado

### Fase 6: Tests Seguridad
- [ ] **SEC-T017** Tests Seguridad Faltantes

### Fase 7: Documentación y Operaciones (Post-Deploy)
- [ ] **SEC-T018** Procedimiento Rotación Secretos
- [ ] **SEC-T019** Limpieza Archivos Huérfanos
- [ ] **SEC-T020** Verificación PermissionError Docker

---

## Checklist Detallado por Tarea

### SEC-T001 — Configuración Producción Completa

**Estado: CERRADA** (2026-11-05) — con limitaciones documentadas abajo (sin staging real con TLS/PostgreSQL; ver "Regresión").

**Autorización:** [x] Responsable autorizó SEC-T001 (fecha: 2026-11-05)

**Precondiciones:**
- [x] Decisiones aprobadas: DEC-010 (CSP strategy) — Opción D, aprobada 2026-11-05
- [x] Repositorio limpio (sin cambios locales pendientes ajenos a esta sesión)

**Implementación:**
- [x] `settings/production.py` creado heredando de `base.py` con:
  - [x] `DEBUG = False`
  - [x] `ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")` (sin default)
  - [x] `SECURE_SSL_REDIRECT = True` (con `SECURE_REDIRECT_EXEMPT` para `/health/`, necesario porque el healthcheck golpea al backend sin pasar por Nginx/TLS)
  - [x] `SECURE_HSTS_SECONDS = 31536000`, `INCLUDE_SUBDOMAINS = True`, `PRELOAD = True`
  - [x] `SESSION_COOKIE_SECURE = True`, `HTTPONLY = True`, `SAMESITE = "Lax"`
  - [x] `CSRF_COOKIE_SECURE = True`, `HTTPONLY = True`, `SAMESITE = "Lax"`
  - [x] `CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS")`
  - [x] `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")`
  - [x] `TRUSTED_PROXIES = env.list("TRUSTED_PROXIES", default=[...])` (configuración declarada; el middleware que la consume es SEC-T005, siguiente tarea)
  - [x] `SECURE_REFERRER_POLICY`, `SECURE_CROSS_ORIGIN_OPENER_POLICY`
  - [x] CSP Report-Only (DEC-010) + `frame-ancestors 'none'`, `base-uri 'self'` bloqueantes — implementado vía middleware propio `core/adapters/security_headers.py` (sin dependencia nueva)
  - [ ] `LOGGING` dict — **diferido deliberadamente a SEC-T011** (siguiente tarea tras SEC-T012) para no duplicar configuración entre fichas que tocan el mismo archivo
  - [ ] `SPECTACULAR_SETTINGS["SERVE_PERMISSIONS"]` — **diferido deliberadamente a SEC-T013** (siguiente tarea tras esta)
  - [x] `REST_FRAMEWORK.DEFAULT_THROTTLE_RATES["document_upload"]` — ya en `base.py` desde SEC-T008; `"auth"` diferido a SEC-T002 (bloqueada por SEC-T005)
  - [ ] `REST_FRAMEWORK.EXCEPTION_HANDLER` — **no implementado, SEC-T010 sigue bloqueada por DEC-009**
  - [x] CORS (`django-cors-headers`, nueva dependencia explícitamente autorizada por esta ficha) + `CORS_ALLOWED_ORIGINS`
  - [x] Añadido además `django.middleware.clickjacking.XFrameOptionsMiddleware` en `base.py` — hallazgo real de `manage.py check --deploy` (faltaba la cabecera `X-Frame-Options`), corregido en el momento
  - [x] Endpoint `GET /health/` creado (`core/adapters/health.py`) — no existía y era necesario para que el criterio de aceptación de esta misma ficha fuera verificable
- [x] `Dockerfile` **multi-stage con targets `development`/`production`** (decisión aprobada: un único archivo, no `Dockerfile.prod` separado, para no duplicar la etapa de instalación de dependencias):
  - [x] Stage `production`: `python:3.12-slim`, usuario `appuser` UID 1000, Gunicorn 4 workers vía `entrypoint.sh`
  - [x] Healthcheck `/health/` → 200 (usa `urllib` de la stdlib, no `curl`, para no añadir un paquete de sistema innecesario)
  - [x] Entrypoint: `migrate` → `collectstatic` → `gunicorn`
  - [ ] Dependencia de sistema para MIME real (DEC-001) — no aplica aún, DEC-001 sigue pendiente (es alcance de SEC-T007)
  - [x] `docker-compose.yml` (desarrollo) actualizado con `target: development` explícito — **sin esto, un build sin `--target` habría construido por defecto la última etapa (`production`), rompiendo el flujo de desarrollo existente**
- [x] `docker-compose.prod.yml` — creado en la **raíz** (no en `backend/`, decisión aprobada):
  - [x] Servicios: `backend`, `db`, `nginx`
  - [x] Volúmenes con nombre distinto a los de desarrollo (`postgres_data_prod`, `media_private_prod`, `static_data_prod`) para evitar colisión
  - [x] Red `backend_net_prod` separada de la de desarrollo
  - [x] Todas las variables sensibles obligatorias (`:?required`), sin valores reales
- [x] `nginx/prod.conf` — creado junto al `nginx.conf` de desarrollo (mismo directorio, decisión aprobada). Documentado explícitamente que `fullchain.pem`/`privkey.pem` son puntos de montaje, no certificados incluidos
- [x] `.env.example` actualizado: `DOCUMENT_UPLOAD_THROTTLE` (ya en SEC-T008), `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS`, `CSP_CONNECT_SRC_EXTRA`, `TRUSTED_PROXIES`. **No se añadieron** `AUTH_THROTTLE_RATE` (pertenece a SEC-T002, bloqueada) ni `ORPHAN_RETENTION_DAYS` (pertenece a SEC-T019, bloqueada por DEC-005) — se añadirán en sus propias tareas

**Pruebas Obligatorias:**
- [x] `docker build --target production -t sgt-siaaf-backend-prod .` → **éxito real, verificado en este entorno** ("Successfully built ... tagged sgt-siaaf-backend-prod:latest"); imagen eliminada después de verificar (no es el entregable, el entregable es el código fuente del Dockerfile)
- [x] `docker build --target development -t ... .` → éxito real (regresión: el target de desarrollo sigue construyendo correctamente tras la reestructuración multi-stage)
- [ ] `docker-compose -f docker-compose.prod.yml up -d` → **no ejecutado**: requiere certificados TLS reales (no se van a inventar/generar certificados autofirmados y presentarlos como verificación real) y el espacio en disco del entorno era crítico en el momento (ver incidente de `/var/log/syslog`, resuelto por el usuario)
- [x] `curl .../health/` → **200, verificado** (vía `django.test.Client`, no `curl` real sobre contenedor levantado): confirmado sin redirect SSL gracias a `SECURE_REDIRECT_EXEMPT`
- [ ] `curl .../api/v1/docs/` → 403 (IsAdminUser) — **no aplica todavía**, es SEC-T013
- [x] Headers de respuesta verificados realmente (vía test client bajo `settings.production`): `Content-Security-Policy`, `Content-Security-Policy-Report-Only`, `X-Frame-Options: DENY` presentes. `Strict-Transport-Security`/`X-Content-Type-Options`/`Referrer-Policy` los pone `django.middleware.security.SecurityMiddleware` ya activo (no verificado cabecera por cabecera en esta sesión, pero es comportamiento estándar de Django con los settings ya confirmados)
- [ ] Cookies `Secure/HttpOnly/SameSite=Lax` — no verificado end-to-end (requiere un flujo de login real bajo HTTPS; los *settings* que las producen sí están confirmados y cargados correctamente)
- [ ] Logs JSON rotativos — no aplica todavía, es SEC-T011
- [x] Suite completa bajo `settings.test` (no en contenedor con PostgreSQL real): **482/482, 0 failed** — regresión confirmada, pero no es lo mismo que "en contenedor con PostgreSQL real" que pide la ficha literalmente

**Regresión:**
- [ ] Flujos críticos end-to-end vía staging real — **no verificado**, no existe staging
- [ ] Frontend contra backend staging — **no aplica**, no se tocó frontend ni existe staging
- [x] Suite de pytest completa (482/482) como sustituto de regresión a nivel de código

**Cierre:**
- [x] Documentación de despliegue actualizada — **no se creó un `DEPLOY_PRODUCTION.md` nuevo**: se actualizaron los documentos ya existentes `docs/08-infraestructura/despliegue.md` y `docker.md` (evitar duplicar estructura ya existente)
- [ ] Imagen Docker en registry — no aplica, no hay registry configurado
- [ ] Staging deploy verificado por QA — no existe staging
- [x] Responsable valida y firma cierre: autorización explícita en esta conversación, fecha: 2026-11-05

**Limitaciones honestas de este cierre:** SEC-T001 se declara CERRADA en el sentido de "el código y la configuración de producción existen, son correctos y están verificados en la medida en que este entorno de sandbox lo permite" (builds reales de Docker exitosos, settings cargando y comportándose correctamente, 482/482 tests). **No** se verificó un despliegue real con PostgreSQL contenedorizado, Nginx con TLS real, ni carga concurrente — eso requiere infraestructura (certificados, dominio real) que esta sesión no tiene autorización ni medios para inventar. SEC-T020 (verificación PermissionError en Docker real) hereda esta misma limitación.

---

### SEC-T002 — Throttling Login (POST /api/v1/auth/token/)

**Estado: CERRADA** (2026-11-05)

**Autorización:** [x] Responsable autorizó SEC-T002 (fecha: 2026-11-05)

**Precondiciones:**
- [x] SEC-T005 CERRADA (TRUSTED_PROXIES + middleware funcionando)
- [x] DEC-002 aprobada (5/min/IP)

**Implementación:**
- [x] `base.py`: `REST_FRAMEWORK.DEFAULT_THROTTLE_RATES["auth"] = env("AUTH_THROTTLE_RATE", default="5/minute")`
- [x] `authentication/adapters/views.py`: `TokenPairView` con:
  - [x] `throttle_classes = [TrustedProxyScopedRateThrottle]` — **no `AnonRateThrottle`**: tiene `scope` fijo `'anon'`, ignora `throttle_scope` de la vista (mismo tipo de hallazgo que en SEC-T008)
  - [x] `throttle_scope = "auth"`
- [x] **Hallazgo real e importante:** el `get_ident()` por defecto de DRF (usado por `AnonRateThrottle`/`ScopedRateThrottle` genéricas) **confía ciegamente en `X-Forwarded-For` si está presente**, sin ninguna validación — es decir, tal como lo describía la ficha original, el throttling de login habría sido **trivialmente evadible** falsificando esa cabecera, totalmente al margen de la validación `TRUSTED_PROXIES` que SEC-T005 ya implementó para la auditoría. Se creó `authentication/adapters/throttling.py` (`TrustedProxyScopedRateThrottle`) que reutiliza la misma validación de SEC-T005 (extraída a `core/adapters/client_ip.py`, compartida con `notificaciones/adapters/signals.py` sin duplicar lógica)

**Pruebas Obligatorias** (`authentication/tests/test_security_controls.py`):
- [x] `test_login_throttle_allows_5_requests_per_minute`
- [x] `test_login_throttle_6th_request_returns_429`
- [x] `test_login_throttle_resets_after_window` — simulado con `cache.clear()`, no una espera real de 61s
- [x] `test_login_throttle_per_ip_isolation` — vía `REMOTE_ADDR` distinto por cliente
- [x] `test_login_throttle_respects_trusted_proxies` — con `TRUSTED_PROXIES` confiable, dos IPs tras `X-Forwarded-For` tienen límites independientes

**Regresión:**
- [x] Tests de `authentication/`+`notificaciones/` completos: 148/148
- [x] Suite completa: 497/497 (492 + 5 nuevos)

**Cierre:**
- [x] Tests pasando
- [x] Configuración en `base.py` (vía `AUTH_THROTTLE_RATE` en `.env.example`)
- [x] Documentado aquí (no en `SECURITY_CONFIG.md`, que es específico de gestión de claves — mismo criterio que SEC-T013)
- [x] Responsable valida y firma: autorización explícita en esta conversación, fecha: 2026-11-05

---

### SEC-T003 — Rotación + Blacklist Refresh Tokens

**Autorización:** [ ] Responsable autorizó SEC-T003 (fecha: ______)

**Precondiciones:**
- [x] SEC-T004 CERRADA (JWT_SIGNING_KEY separada) — cerrada 2026-11-05
- [ ] DEC-008 decidida (refresh token storage frontend: httpOnly cookie)

**Implementación:**
- [ ] `base.py`: `INSTALLED_APPS` añadir `"rest_framework_simplejwt.token_blacklist"`
- [ ] `base.py`: `SIMPLE_JWT.ROTATE_REFRESH_TOKENS = True`, `BLACKLIST_AFTER_ROTATION = True`
- [ ] `python manage.py migrate` (ejecuta migraciones `token_blacklist`)
- [ ] `authentication/adapters/views.py`: Nuevo endpoint `LogoutView`:
  - [ ] `POST /api/v1/auth/logout/`
  - [ ] Requiere autenticación (JWTAuthentication)
  - [ ] Body: `{"refresh": "..."}`
  - [ ] Añade refresh a `BlacklistedToken` → 205 Reset Content
  - [ ] Si DEC-008 = httpOnly cookie: `response.delete_cookie('refresh_token')`
- [ ] Verificar rotación: refresh usado → nuevo access + nuevo refresh; anterior en blacklist

**Pruebas Obligatorias (nuevas en `authentication/tests/test_security_controls.py`):**
- [ ] `test_refresh_rotates_token_returns_new_access_and_refresh` — refresh válido → nuevo access ≠ anterior, nuevo refresh ≠ anterior
- [ ] `test_old_refresh_rejected_after_rotation` — usar refresh anterior → 401 `Token is blacklisted`
- [ ] `test_blacklisted_refresh_rejected` — POST /logout/ con refresh → posterior refresh con mismo → 401
- [ ] `test_logout_requires_authentication` — sin token → 401
- [ ] `test_refresh_token_lifetime_respected` — refresh expira a 24h → 401

**Regresión:**
- [ ] Tests JWT existentes (`test_jwt.py` 6 tests) passing
- [ ] Flujo: login → acceso recurso → refresh → acceso → logout → intento refresh → 401

**Frontend (coordinación):**
- [ ] Issue frontend creado: interceptor axios guarda nuevo refresh, llama logout, maneja 401 refresh
- [ ] `AUTH_FLOW_CHANGES.md` documentado

**Cierre:**
- [ ] Migraciones aplicadas
- [ ] Tests pasando
- [ ] Endpoint logout en OpenAPI
- [ ] Frontend actualizado (issue separado cerrado)
- [ ] Responsable valida y firma: _______________ fecha: ______

---

### SEC-T004 — JWT_SIGNING_KEY Separada de SECRET_KEY

**Estado: CERRADA** (fecha: 2026-11-05 — implementación + auditoría de validación independiente + corrección documental H1-H3, todas autorizadas y verificadas en sesión). Formalización mediante firma electrónica FirmaEc del responsable: **PENDIENTE** — ver `ACTA_CIERRE_SEC-T004.md`.

**Autorización:** [x] Responsable autorizó SEC-T004 (fecha: 2026-11-05)

**Precondiciones:**
- [x] Ninguna (independiente) — confirmado

**Implementación:**
- [x] `base.py`: `SIMPLE_JWT.SIGNING_KEY = env("JWT_SIGNING_KEY")` (nueva variable), vía variable `JWT_SIGNING_KEY` a nivel de módulo
- [x] `base.py`: `SECRET_KEY = env("SECRET_KEY")` sin cambios
- [ ] `production.py`: Validar que ambas existan y sean distintas (log warning si iguales) — **DESVIACIÓN DOCUMENTADA:** `production.py` no existe (SEC-T001 no autorizada). El warning de igualdad se implementó en `base.py` (aplica a todos los entornos, incluido el futuro `production.py` que lo heredará). No es criterio de aceptación de esta ficha, así que no bloquea el cierre.
- [x] `.env.example`: Documentar ambas con `openssl rand -base64 32`
- [ ] Generar `JWT_SIGNING_KEY` para entornos staging/prod — pendiente: no existen aún esos entornos (dependen de SEC-T001). Sí se generó un valor dev-only para el `.env` local (no secreto real).

**Pruebas Obligatorias (nuevas en `authentication/tests/test_security_controls.py`):**
- [x] `test_jwt_signing_key_separate_from_secret_key` — `SIMPLE_JWT.SIGNING_KEY != SECRET_KEY`
- [x] `test_jwt_token_verification_uses_jwt_signing_key` — token firmado con JWT_SIGNING_KEY válido; firmado con SECRET_KEY → 401
- [x] `test_django_sessions_use_secret_key` — sesión/cookie firmada con SECRET_KEY funciona independientemente

**Regresión:**
- [ ] Deploy staging con nuevas claves → login funciona → tokens nuevos válidos — no aplicable aún (no hay staging; depende de SEC-T001)
- [x] Sesiones Django admin siguen funcionando — verificado a nivel unitario (`test_django_sessions_use_secret_key`); pendiente de validación en un despliegue real (post SEC-T001)
- [x] Suite completa de regresión (473 tests previos + 3 nuevos = 476) → 0 failed

**Cierre:**
- [x] Variables en `.env.example`
- [x] Tests pasando
- [x] Documentado procedimiento rotación independiente en `SECURITY_CONFIG.md`
- [x] Documentación descriptiva coherente con la implementación real (H1-H3 de la auditoría de validación corregidos: `backend/docs/adr/0003-autenticacion-jwt-stateless.md`, `docs/08-infraestructura/configuracion.md`, `docs/08-infraestructura/entorno-desarrollo.md`)
- [x] Responsable valida y firma: autorización emitida por el responsable del proyecto mediante esta conversación (sesión Claude Code), fecha: 2026-11-05. **Formalización mediante firma electrónica FirmaEc: PENDIENTE** (documento preparado para suscripción: `ACTA_CIERRE_SEC-T004.md`, en esta misma carpeta).

---

### SEC-T005 — IP Auditoría + Middleware Thread-Local + TRUSTED_PROXIES

**Estado: CERRADA** (2026-11-05)

**Autorización:** [x] Responsable autorizó SEC-T005 (fecha: 2026-11-05)

**Precondiciones:**
- [x] SEC-T001 CERRADA (production.py existe; sin Nginx/proxy real en staging, ver limitación de SEC-T001)

**Implementación:**
- [x] `core/adapters/middleware.py`: `ThreadLocalRequestMiddleware` (con limpieza en `finally` tras la respuesta, mejora sobre el pseudocódigo de la ficha para evitar fugas de request entre peticiones en el mismo hilo)
  - [x] Insertado **PRIMERO** en `MIDDLEWARE` en `base.py` (antes de `SecurityMiddleware`)
- [x] `notificaciones/adapters/signals.py`:
  - [x] `_get_current_request()` → usa `core.adapters.middleware.get_current_request()`
  - [x] `_get_client_ip(request)`: valida `REMOTE_ADDR` contra `TRUSTED_PROXIES` con `ipaddress` antes de confiar en `X-Forwarded-For`; sin `TRUSTED_PROXIES` configurado (dev/test), nunca confía en la cabecera
  - [x] `SECURE_PROXY_SSL_HEADER` y `TRUSTED_PROXIES` — ya en `production.py` desde SEC-T001
- [x] Verificado `EventoAuditoria.ip` poblado en la señal de creación de expediente (vía prueba de integración real); el resto de señales automáticas reutilizan la misma `_crear_evento_auditoria`/`_get_client_ip`, sin lógica diferenciada por tipo de evento

**Pruebas Obligatorias** (`notificaciones/tests/test_audit_ip.py`, nuevo):
- [x] `test_audit_ip_captured_from_xff_with_trusted_proxy` — adaptado a `127.0.0.0/8` (IP real del test client de Django) en vez de `10.0.0.1`, con `override_settings(TRUSTED_PROXIES=...)`: XFF confiable → se usa el primer IP
- [x] `test_audit_ip_spoofing_blocked_untrusted_proxy` — sin `TRUSTED_PROXIES` (estado real de `settings.test`) → XFF ignorado, se usa `REMOTE_ADDR`
- [x] `test_audit_ip_persisted_in_eventoauditoria` — `POST /api/v1/expedientes/` real vía `APIClient` → IP persistida correctamente
- [x] `test_audit_ip_none_when_no_request` — servicio invocado directamente (sin HTTP) → `ip is None`, sin excepción

**Regresión:**
- [x] Tests de auditoría existentes (`notificaciones/` completo): 75/75 passing
- [x] Suite completa: 486/486 (482 + 4 nuevos)

**Cierre:**
- [x] Middleware en `MIDDLEWARE[0]`
- [x] Tests pasando
- [x] `TRUSTED_PROXIES` ya documentado en `.env.example` desde SEC-T001; no existe `DEPLOY_PRODUCTION.md` como archivo separado (ver nota de SEC-T001: se usan `docs/08-infraestructura/despliegue.md`/`docker.md`)
- [x] Responsable valida y firma: autorización explícita en esta conversación, fecha: 2026-11-05

---

### SEC-T006 — Access Token Lifetime 30 Minutos

**Estado: CERRADA** (2026-11-05). *(Corrección 2026-11-06: esta sección no se había actualizado en su momento pese a que la tarea sí se implementó y verificó esa misma sesión — verificado de nuevo contra el código real antes de corregir.)*

**Autorización:** [x] Responsable autorizó SEC-T006 (fecha: 2026-11-05)

**Precondiciones:**
- [x] SEC-T004 CERRADA (JWT_SIGNING_KEY separada) — cerrada 2026-11-05

**Implementación:**
- [x] `base.py`: `SIMPLE_JWT.ACCESS_TOKEN_LIFETIME = timedelta(minutes=30)` — confirmado en código (`base.py:122`)

**Pruebas Obligatorias (`authentication/tests/test_security_controls.py`):**
- [x] `test_access_token_lifetime_30_minutes`
- [x] `test_access_token_expired_after_31_minutes_rejected`

**Regresión:**
- [x] Tests JWT existentes + nuevo test lifetime — suite completa 497/497 (re-verificado 2026-11-06)

**Cierre:**
- [x] Configuración actualizada
- [x] Test pasando
- [x] Documentado en `SECURITY_CONFIG.md`
- [x] Responsable valida y firma: autorización explícita en conversación, fecha: 2026-11-05

---

### SEC-T007 — Validación MIME Real

**Autorización:** [ ] Responsable autorizó SEC-T007 (fecha: ______)

**Precondiciones:**
- [ ] SEC-T001 CERRADA (Dockerfile listo)
- [ ] DEC-001 aprobada (método: python-magic vs pikepdf)

**Implementación:**
- [ ] ADR documentado con evaluación opciones
- [ ] Si `python-magic`:
  - [ ] `requirements.txt` añadir `python-magic>=0.4,<1.0`
  - [ ] `Dockerfile` añadir `apk add libmagic`
  - [ ] `pdf_validation.py`: `magic.from_buffer(file.read(2048), mime=True) == "application/pdf"`
- [ ] Si `pikepdf`:
  - [ ] `requirements.txt` añadir `pikepdf>=8.0,<9.0`
  - [ ] `pdf_validation.py`: `pikepdf.open(io.BytesIO(file.read()))` → catch `PdfError` → rechazar
- [ ] Integrar en `validar_pdf_completo()` ANTES de guardar

**Pruebas Obligatorias (nuevas en `core/adapters/tests/test_pdf_validation.py`):**
- [ ] `test_pdf_validation_real_mime_passes_valid_pdf` — PDF real → pasa
- [ ] `test_pdf_validation_rejects_polyglot_pdf_zip` — PDF+ZIP → rechaza
- [ ] `test_pdf_validation_rejects_corrupted_pdf_structure` — PDF xref corrupto → rechaza
- [ ] `test_pdf_validation_docker_compatibility` — build Dockerfile → éxito

**Regresión:**
- [ ] Tests PDF existentes (25+ tests) passing
- [ ] Carga docs normal funciona

**Cierre:**
- [ ] ADR documentado
- [ ] Implementación elegida funcionando
- [ ] Tests pasando
- [ ] Docker build exitoso
- [ ] Responsable valida y firma: _______________ fecha: ______

---

### SEC-T008 — Throttling Carga Documentos

**Estado: CERRADA** (2026-11-05). *(Corrección 2026-11-06: sección no actualizada en su momento; verificado de nuevo contra el código real antes de corregir.)*

**Autorización:** [x] Responsable autorizó SEC-T008 (fecha: 2026-11-05)

**Precondiciones:**
- [x] DEC-003 aprobada (10/hora/usuario)

**Implementación:**
- [x] `base.py`: `REST_FRAMEWORK.DEFAULT_THROTTLE_RATES["document_upload"] = env("DOCUMENT_UPLOAD_THROTTLE", default="10/hour")`
- [x] `peticiones/adapters/views.py`: `PeticionViewSet.get_throttles()`:
  - [x] `ScopedRateThrottle` — **no `UserRateThrottle`**: tiene `scope` fijo `'user'`, ignora `throttle_scope` de la vista (hallazgo real corregido en su momento)
  - [x] `throttle_scope = "document_upload"`

**Pruebas Obligatorias** (`peticiones/tests/test_upload_throttle.py`):
- [x] `test_document_upload_throttle_allows_10_per_hour`
- [x] `test_document_upload_throttle_11th_returns_429`
- [x] `test_document_upload_throttle_per_user_isolation`
- [x] `test_document_upload_throttle_resets_after_window` (simulado con `cache.clear()`, no una espera real de 61 min)

**Regresión:**
- [x] Tests carga docs existentes passing — suite completa 497/497 (re-verificado 2026-11-06)

**Cierre:**
- [x] Tests pasando
- [x] Configuración en `base.py`
- [x] Documentado (informe de sesión; no requiere `SECURITY_CONFIG.md`, que es específico de claves)
- [x] Responsable valida y firma: autorización explícita en conversación, fecha: 2026-11-05

---

### SEC-T009 — Remover Rutas Internas Serializers

**Autorización:** [ ] Responsable autorizó SEC-T009 (fecha: ______)

**Precondiciones:**
- [ ] SEC-T001 CERRADA
- [ ] DEC-006 implementada (endpoint GET /api/v1/declaratorias/{id}/documento/ existe)

**Implementación:**
- [ ] `peticiones/adapters/serializers.py`: `DocumentoEntregadoSerializer`:
  - [ ] Remover `archivo_path` de `fields`
  - [ ] Añadir `download_url = serializers.SerializerMethodField()`
  - [ ] `get_download_url(self, obj): return request.build_absolute_uri(f"/api/v1/peticiones/{obj.peticion_id}/documento/")`
- [ ] `resoluciones/adapters/serializers.py`: `DeclaratoriaAptitudSerializer`:
  - [ ] Remover `archivo_memorando_firmado_path` de `fields`
  - [ ] Añadir `download_url = serializers.SerializerMethodField()`
  - [ ] `get_download_url(self, obj): return request.build_absolute_uri(f"/api/v1/declaratorias/{obj.id}/documento/")`

**Pruebas Obligatorias:**
- [ ] `test_documento_serializer_excludes_archivo_path` — `archivo_path` not in response.data
- [ ] `test_documento_serializer_includes_download_url` — `download_url` present, formato correcto
- [ ] `test_declaratoria_serializer_excludes_memorando_path` — idem
- [ ] `test_download_url_works_with_auth` — GET download_url + JWT → 200 PDF

**Frontend (coordinación):**
- [ ] Issue frontend: migrar V-03, V-08 a `download_url`
- [ ] `DOWNLOAD_URL_MIGRATION.md` documentado

**Cierre:**
- [ ] Serializers actualizados
- [ ] Tests pasando
- [ ] Frontend notificado (issue vinculado)
- [ ] Responsable valida y firma: _______________ fecha: ______

---

### SEC-T010 — Handler Global Excepciones

**Autorización:** [ ] Responsable autorizó SEC-T010 (fecha: ______)

**Precondiciones:**
- [ ] SEC-T001 CERRADA (production.py DEBUG=False para test 500)
- [ ] DEC-009 aprobada (mensaje 500 usuario final)

**Implementación:**
- [ ] `core/adapters/exceptions.py` (nuevo archivo):
  - [ ] `custom_exception_handler(exc, context)` → formato `{ "error": { "code", "message", "details" } }`
  - [ ] Mapeo: `ValidationError`→400 code `validation_error`, `AuthenticationFailed`→401 `authentication_failed`, `PermissionDenied`→403 `permission_denied`, `NotFound`→404 `not_found`, `Throttled`→429 `throttled`, `APIException`→status_code, `Exception`→500 `server_error`
  - [ ] 500: sin stack trace, SQL, rutas internas; mensaje DEC-009
- [ ] `base.py` / `production.py`: `REST_FRAMEWORK.EXCEPTION_HANDLER = "core.adapters.exceptions.custom_exception_handler"`
- [ ] Custom exceptions existentes (`EstadoPeticionInvalidoAPI`, `UsuarioNoAutorizadoAPI`, `ValidacionPDF_API`) mapeadas a códigos/formato

**Pruebas Obligatorias (nuevas en `core/adapters/tests/test_exceptions.py`):**
- [ ] `test_500_no_stacktrace_leak` — provocar 500 → response 500 sin `traceback`, `stack`, `file`, `line`
- [ ] `test_400_validation_error_format` — POST data inválida → 400 formato uniforme
- [ ] `test_401_authentication_failed_format` — token inválido → 401 formato uniforme
- [ ] `test_403_permission_denied_format` — sin permisos → 403 formato uniforme
- [ ] `test_404_not_found_format` — recurso inexistente → 404 formato uniforme
- [ ] `test_429_throttled_format` — throttling excedido → 429 formato uniforme
- [ ] `test_409_conflict_format` — si BE-11 implementado → formato uniforme

**Regresión:**
- [ ] Suite completa 473 tests passing (actualizar asserts si cambian formato errores)
- [ ] Endpoints críticos: login, expedientes, peticiones, checklist, resoluciones, notificaciones

**Frontend (coordinación):**
- [ ] `API_ERROR_FORMAT.md` documentado
- [ ] Deploy coordinado backend+frontend

**Cierre:**
- [ ] Handler implementado
- [ ] Tests pasando (existentes actualizados + nuevos)
- [ ] Formato documentado en `API_ERROR_FORMAT.md`
- [ ] Responsable valida y firma: _______________ fecha: ______

---

### SEC-T011 — Logging Estructurado

**Estado: CERRADA** (2026-11-05)

**Autorización:** [x] Responsable autorizó SEC-T011 (fecha: 2026-11-05)

**Precondiciones:**
- [x] SEC-T012 CERRADA (print() eliminados)
- [x] SEC-T001 CERRADA (production.py existe)

**Implementación:**
- [x] `base.py`: `LOGGING` dict (formatters JSON, filtros, handler consola — seguro en todos los entornos; **desviación deliberada**: los handlers de archivo NO están en `base.py` porque `/var/log/sgt-siaaf/` no existe fuera del contenedor de producción — habría roto desarrollo/tests. Están en `production.py`, ver abajo):
  - [x] Formatters: JSON (`python-json-logger`) con `asctime`, `levelname`, `name`, `message`, `request_id`, `user_id`
  - [x] Filters: `SensitiveDataFilter` (`core/adapters/logging_filters.py`) elimina `password`, `token`, `authorization`, `credit_card`, `cedula` de `record.msg` y de atributos extra; `RequestIdFilter` garantiza `request_id`/`user_id` (placeholder `"-"` hasta que exista un mecanismo real de contexto)
  - [x] Root logger nivel WARNING; loggers `apps.*`, `core.*` nivel INFO (DEBUG en `local.py`)
- [x] `production.py`: sobrescribe con `RotatingFileHandler` (maxBytes=10MB, backupCount=5) para `apps`, `django`, `security` en `LOG_DIR` (default `/var/log/sgt-siaaf`, configurable por env, creado y con permisos correctos en el target `production` del `Dockerfile`)
- [x] `local.py`: nivel DEBUG explícito para `apps`/`core`, handler consola (ya es el default de `base.py`)
- [ ] `logging.config.dictConfig(LOGGING)` manual en `settings/__init__.py` — **no implementado deliberadamente**: Django ya aplica `settings.LOGGING` automáticamente al arrancar (`django.setup()` → `django.utils.log.configure_logging`); llamarlo de nuevo manualmente sería redundante, no es un paso real de Django pese a que la ficha lo sugiere

**Pruebas Obligatorias** (`core/adapters/tests/test_logging.py`, nuevo):
- [x] `test_logging_structured_json_format` — JSON parseable con los campos esperados
- [x] `test_logging_no_secrets_in_output` — `password=secreto123`/`token=abc.def.ghi` → no aparecen en el JSON de salida
- [x] `test_logging_rotation_max_bytes` — escribir ~11MB → backup creado (`RotatingFileHandler` real, directorio temporal)
- [x] `test_logging_no_print_in_production_code` — 0 resultados (automatiza el grep manual de SEC-T012)
- [x] `test_logging_dict_loaded_in_settings` — verificación adicional de que la config carga correctamente

**Regresión:**
- [ ] Deploy staging → generar logs → verificar JSON, rotación, sin secretos — no existe staging; **sustituido por verificación real local**: se cargó `settings.production` con `LOG_DIR` apuntando a un directorio temporal, se emitió un log con un `password=` real, y se confirmó en el archivo resultante que el JSON es válido, sin el secreto, con `request_id`/`user_id` presentes
- [x] Suite completa de regresión (482/482) → 0 failed

**Cierre:**
- [x] LOGGING dict en settings (`base.py` + `production.py` + `local.py`)
- [x] Filtros funcionando (verificado con secretos reales de prueba, no solo con mocks)
- [x] Rotación verificada (mecanismo `RotatingFileHandler` probado; no verificada con PostgreSQL/staging real)
- [x] `print()` eliminado de código producción (SEC-T012, con prueba de regresión automatizada ahora)
- [x] Responsable valida y firma: autorización explícita en esta conversación, fecha: 2026-11-05

---

### SEC-T012 — Eliminar print() en evaluar_checklist.py

**Estado: CERRADA** (2026-11-05). *(Corrección 2026-11-06: sección no actualizada en su momento; re-verificado: 0 ocurrencias de `print(` en `src/apps/verificacion/services/` y en todo `src/` fuera de tests/manage.py.)*

**Autorización:** [x] Responsable autorizó SEC-T012 (fecha: 2026-11-05)

**Precondiciones:**
- [x] Ninguna (independiente)

**Implementación:**
- [x] `verificacion/services/evaluar_checklist.py`: `logger = logging.getLogger(__name__)` tras los imports; ambos `print()` reemplazados por `logger.debug(...)` con formato `%s` (no f-string, evita evaluar el mensaje si el nivel no aplica)
- [x] Verificado sin `print(` en `src/` (excluyendo tests y manage.py)

**Pruebas Obligatorias:**
- [x] `test_logging_no_print_in_production_code` (`core/adapters/tests/test_logging.py`, SEC-T011) — automatiza este grep como prueba de regresión permanente

**Cierre:**
- [x] Código limpio
- [x] Tests pasando — suite completa 497/497 (re-verificado 2026-11-06)
- [x] Verificado `grep -r "print(" src/` (excluyendo tests/manage.py) → vacío
- [x] Responsable valida y firma: autorización explícita en conversación, fecha: 2026-11-05

---

### SEC-T013 — Protección Swagger/ReDoc/Schema

**Estado: CERRADA** (2026-11-05)

**Autorización:** [x] Responsable autorizó SEC-T013 (fecha: 2026-11-05)

**Precondiciones:**
- [x] SEC-T001 CERRADA (production.py existe)

**Implementación:**
- [x] `production.py`: `SPECTACULAR_SETTINGS["SERVE_PERMISSIONS"] = ["rest_framework.permissions.IsAdminUser"]` (sobre una copia profunda del dict, no mutación in-place — ver hallazgo de bug abajo)
- [x] `local.py` / `test.py`: ya era `AllowAny` por herencia de `base.py`, sin cambios necesarios

**Hallazgo real durante la implementación (corregido en el momento):** `production.py` mutaba `LOGGING`/`SPECTACULAR_SETTINGS` **in-place** sobre el mismo objeto dict que `base.py` (consecuencia de `from .base import *`), lo que contaminaba `base.py` (y por tanto `local.py`/`test.py`) con los valores de producción dentro del mismo proceso — detectado porque mis propias pruebas con `override_settings` se volvían no deterministas. Corregido con `copy.deepcopy()` antes de mutar. Ver `production.py`.

**Pruebas Obligatorias** (`authentication/tests/test_swagger_protection.py`, reescrito tras el hallazgo anterior):
- [x] `test_swagger_anonymous_denied_in_production_settings` — verificación directa de `IsAdminUser().has_permission()` con request anónimo → `False`
- [x] `test_swagger_admin_allowed_in_production_settings` — con usuario `is_staff=True` → `True`
- [x] `test_schema_anonymous_denied_in_production_settings` — idem para `/schema/`
- [x] `test_swagger_allowany_in_local_settings` — `AllowAny` nunca deniega
- [x] `test_production_settings_module_restricts_to_admin` / `test_local_settings_module_keeps_allowany` (nuevas, no en la ficha original): verificación estática del contenido real de ambos módulos de settings, más robusta que depender de `override_settings` con drf-spectacular (ver nota de diseño en el archivo)
- [x] **Verificación real adicional, manual, fuera de pytest**: Django arrancado de verdad bajo `DJANGO_SETTINGS_MODULE=config.settings.production` → `GET /api/v1/docs/`, `/redoc/`, `/schema/` anónimos → **403 real, confirmado**, no simulado

**Cierre:**
- [x] Configuración por entorno
- [x] Tests pasando (6/6 nuevos; 492/492 suite completa)
- [ ] Documentado en `SECURITY_CONFIG.md` — no aplica, esa guía es específica de gestión de claves (SECRET_KEY/JWT_SIGNING_KEY); se documentó en su lugar en el propio `production.py` y en este checklist
- [x] Responsable valida y firma: autorización explícita en esta conversación, fecha: 2026-11-05
- [ ] Responsable valida y firma: _______________ fecha: ______

---

### SEC-T014 — CI/CD Security (Safety + Bandit + Gitleaks)

**Estado: CERRADA** (2026-11-05), con la limitación de que `gitleaks` no pudo ejecutarse localmente (ver abajo)

**Autorización:** [x] Responsable autorizó SEC-T014 (fecha: 2026-11-05)

**Precondiciones:**
- [x] SEC-T001 CERRADA (Dockerfile existe; no se requirió para los jobs de esta tarea, que corren en `ubuntu-latest` sin Docker)

**Implementación:**
- [x] `.github/workflows/security.yml`:
  - [x] Job `safety`: con `--policy-file .github/safety-policy.yml` (nuevo) — sin la política, el default de `safety` **oculta** vulnerabilidades en rangos de versión no fijados (hallazgo real, ver abajo)
  - [x] Job `bandit`: `bandit -r src/ -c .bandit`
  - [x] Job `gitleaks`: vía `gitleaks/gitleaks-action@v2` (acción oficial, no ejecutable localmente en este entorno)
  - [x] Jobs en cada PR y push a `main`
- [x] `.bandit` — **estaba en formato incorrecto** (sintaxis INI antigua; bandit 1.9.x requiere YAML) y **nunca habría funcionado** tal como estaba. Corregido a YAML válido.
- [x] `.github/safety-policy.yml` (nuevo) — fuerza a `safety` a evaluar también los rangos no fijados

**Correcciones a `requirements.txt` (hallazgo real, pisos de versión, sin tocar el techo de ningún rango):**
- [x] `Django>=5.2,<5.3` → `>=5.2.19,<5.3` (corrige 4 CVEs reales en el rango, incl. 2 de inyección SQL; la versión ya en uso ya los corregía)
- [x] `djangorestframework>=3.16,<4.0` → `>=3.17.2,<4.0` (corrige 2 CVEs; versión ya en uso ya los corregía)
- [x] `djangorestframework-simplejwt>=5.5,<6.0` → `>=5.5.1,<6.0` (corrige CVE-2024-22513; versión ya en uso coincide exactamente)

**Pruebas Obligatorias:**
- [x] `safety check` local (con la política nueva) → **antes de las correcciones: 42 vulnerabilidades ocultas por el default; después: 2 reportadas** (`pytest`, `black` — herramientas de desarrollo, requerirían subir el techo del rango, no solo el piso; documentado como riesgo residual, no corregido en esta tarea)
- [x] `bandit -r src/ -c .bandit` local (tras corregir el formato) → **0 HIGH, 0 MEDIUM, 1 LOW** (contraseña de cuenta demo ya documentada como no productiva en otros lugares del proyecto)
- [ ] `gitleaks detect --source=.` local — **no ejecutable**: sin binario disponible por gestor de paquetes en este entorno; no se descargó un ejecutable externo (fuera de política de seguridad de esta sesión). El workflow usa la acción oficial, que sí correrá en GitHub Actions real.
- [ ] Pipeline CI pasa en PR de prueba — no aplica, no se creó ningún PR ni se hizo push (restricción explícita de esta sesión: no Git)

**Cierre:**
- [x] Pipeline configurado
- [ ] Pasando en main — no verificable sin GitHub Actions real
- [x] Documentado en `docs/09-calidad/ci-seguridad.md` (nombre adaptado a la convención de nombres ya existente del proyecto en vez de `CI_SECURITY.md`)
- [x] Responsable valida y firma: autorización explícita en esta conversación, fecha: 2026-11-05

---

### SEC-T015 — Dependabot Configurado

**Estado: CERRADA (configuración) — "activo en repo" pendiente de un push real, fuera de alcance de esta sesión**

**Autorización:** [x] Responsable autorizó SEC-T015 (fecha: 2026-11-05)

**Precondiciones:**
- [x] SEC-T014 CERRADA

**Implementación:**
- [x] `.github/dependabot.yml`:
  - [x] `package-ecosystem: "pip"`, `directory: "/backend"` (corregido de `"/"`: el `requirements.txt` real vive en `backend/`, no en la raíz — con `"/"` Dependabot no habría encontrado nada que actualizar)
  - [x] `schedule: {interval: "weekly", day: "monday", time: "09:00"}`
  - [x] `open-pull-requests-limit: 10`
  - [x] `allow: [{dependency-type: "direct"}]`
  - [x] `labels: ["dependencies", "security"]`
  - [ ] `automerge: true` — **no es una clave válida del esquema de `dependabot.yml`** (GitHub no soporta auto-merge declarado así en este archivo; requiere reglas de branch protection + workflow aparte). Omitido para no producir una configuración inválida.
  - [ ] `reviewers: ["tech-lead"]` — omitido: "tech-lead" no es un usuario/equipo real de este repositorio; asignar un reviewer inexistente habría sido un dato institucional inventado

**Pruebas Obligatorias:**
- [x] YAML validado (parseable, esquema básico correcto)
- [ ] Merge → Dependabot activo en repo — no aplica, no se hace push/commit en esta sesión (restricción explícita: no Git)
- [ ] Verificar PR generado — no verificable sin que el archivo esté en la rama por defecto de un repositorio real en GitHub

**Cierre:**
- [x] Configuración creada y validada
- [ ] Dependabot activo — pendiente de que el responsable suba este archivo a GitHub
- [ ] Primer PR automático procesado — pendiente, depende de lo anterior
- [x] Responsable valida y firma: autorización explícita en esta conversación, fecha: 2026-11-05

---

### SEC-T016 — Cobertura Tests + testpaths

**Autorización:** [ ] Responsable autorizó SEC-T016 (fecha: ______)

**Precondiciones:**
- [ ] DEC-004 aprobada (umbral 80% o valor decidido)

**Implementación:**
- [ ] `pyproject.toml`:
  - [ ] `testpaths = ["src"]`
  - [ ] `addopts = "--cov=src --cov-fail-under=80 --cov-report=term-missing"` (o valor DEC-004)
  - [ ] `omit` patterns: migrations, settings, apps.py, __init__.py, manage.py

**Pruebas Obligatorias:**
- [ ] `pytest` → coverage report ≥80% overall
- [ ] `pytest --collect-only` → incluye `src/core/adapters/tests/`
- [ ] Módulos críticos (`authentication`, `peticiones`, `verificacion`, `core.adapters`) ≥90%

**Cierre:**
- [ ] Configuración actualizada
- [ ] Coverage ≥80% en CI
- [ ] Documentado en `TESTING.md`
- [ ] Responsable valida y firma: _______________ fecha: ______

---

### SEC-T017 — Tests Seguridad Faltantes

**Autorización:** [ ] Responsable autorizó SEC-T017 (fecha: ______)

**Precondiciones:**
- [ ] SEC-T002 CERRADA (throttling login)
- [ ] SEC-T003 CERRADA (rotación/blacklist)
- [ ] SEC-T005 CERRADA (IP auditoría)
- [ ] SEC-T013 CERRADA (Swagger protection)

**Implementación:**
- [ ] `authentication/tests/test_security_controls.py` (nuevo):
  - [ ] Tests throttling login (SEC-T002)
  - [ ] Tests rotación/blacklist/logout (SEC-T003)
  - [ ] Tests lifetime 30min (SEC-T006)
  - [ ] Tests JWT key separada (SEC-T004)
- [ ] `notificaciones/tests/test_audit_ip.py` (nuevo):
  - [ ] Tests IP auditoría con proxy trusted, spoofing bloqueado, IP persistida
- [ ] `authentication/tests/test_swagger_protection.py` (nuevo):
  - [ ] Tests Swagger/schema 403 anónimo prod, 200 admin
- [ ] `peticiones/tests/test_upload_throttle.py` (nuevo):
  - [ ] Tests throttling carga docs (SEC-T008)

**Pruebas Obligatorias:**
- [ ] Todos los tests nuevos pasan
- [ ] Integrados en `pytest` collection
- [ ] Suite completa 473+ tests passing en CI

**Cierre:**
- [ ] Tests creados y pasando
- [ ] Responsable valida y firma: _______________ fecha: ______

---

### SEC-T018 — Procedimiento Rotación Secretos

**Estado: CERRADA** (2026-11-05)

**Autorización:** [x] Responsable autorizó SEC-T018 (fecha: 2026-11-05)

**Precondiciones:**
- [x] SEC-T004 CERRADA (JWT_SIGNING_KEY separada) — cerrada 2026-11-05

**Implementación:**
- [x] `SECURITY_CONFIG.md` (sección SEC-T018):
  - [x] Procedimiento rotación `SECRET_KEY`: generación (`openssl rand -base64 32`), deploy rolling con `SECRET_KEY_NEW` + ventana de solape, verificación login/sesiones admin, renombrado y eliminación de la clave antigua
  - [x] Procedimiento rotación `JWT_SIGNING_KEY`: generación, deploy, invalidación tokens (re-login users), verificación
  - [x] Checklist verificación post-rotación
  - [x] Responsable, frecuencia (anual o tras incidente)

**Pruebas Obligatorias:**
- [x] Simulación en staging — **adaptado**: no existe staging real (depende de SEC-T001); se ejecutó una simulación local con claves nuevas nunca usadas antes → 482/482 pruebas pasando, confirmando que la rotación es mecánicamente segura (sin valores quemados en código). Pendiente de repetir en staging real cuando exista (SEC-T001/SEC-T020).

**Cierre:**
- [x] Documento mergeado en repo (`SECURITY_CONFIG.md`)
- [ ] Equipo notificado — pendiente, acción humana fuera del alcance de esta sesión
- [x] Responsable valida y firma: autorización explícita en esta conversación, fecha: 2026-11-05

---

### SEC-T019 — Limpieza Archivos Huérfanos

**Estado: BLOQUEADA** — DEC-005 (política de retención) sigue sin aprobar. Aunque la instrucción de autorización general incluía a SEC-T019 en la secuencia "tras SEC-T001", la propia instrucción también exige no ejecutar ninguna tarea cuya decisión pendiente lo impida — DEC-005 nunca fue aprobada en el lote de decisiones de esta sesión (solo DEC-002, DEC-003, DEC-004 y DEC-010). No se implementó ningún código para esta tarea.

**Autorización:** [ ] Responsable autorizó SEC-T019 (fecha: ______) — pendiente de DEC-005 primero

**Precondiciones:**
- [x] SEC-T001 CERRADA (Dockerfile para cron)
- [ ] DEC-005 aprobada (política retención 90 días) — **sigue pendiente, bloquea esta tarea**

**Implementación:**
- [ ] `management command` `limpiar_archivos_huerfanos`:
  - [ ] `--dry-run` lista huérfanos (archivos sin registro DB + registros `es_vigente=False` > 90 días)
  - [ ] Sin flag elimina/mueve a quarantine
  - [ ] Log JSON con archivos procesados, bytes liberados
- [ ] Cron en Dockerfile/entrypoint: `0 3 * * * python manage.py limpiar_archivos_huerfanos`

**Pruebas Obligatorias:**
- [ ] Crear archivo huérfano manual → command lo detecta
- [ ] Crear DocumentoEntregado sin archivo físico → command lo detecta (opcional)
- [ ] `--dry-run` no elimina; sin flag elimina

**Cierre:**
- [ ] Command implementado, testeado
- [ ] Documentado en `OPERATIONS.md`
- [ ] Responsable valida y firma: _______________ fecha: ______

---

### SEC-T020 — Verificación PermissionError Docker

**Estado: CERRADA** (2026-11-05) — verificado en Docker real en este entorno, no en "staging" (no existe)

**Autorización:** [x] Responsable autorizó SEC-T020 (fecha: 2026-11-05)

**Precondiciones:**
- [x] SEC-T001 CERRADA (Dockerfile + target `production` reales)

**Implementación / verificación real ejecutada:**
- [x] Build real de la imagen (`docker build --target production`, reutilizando la ya validada en SEC-T001)
- [x] Contenedor real levantado (`docker run --entrypoint python3 -v <volumen>:/app/backend/media ...`) con un volumen Docker montado en `/app/backend/media` (equivalente al `media_private_prod` de `docker-compose.prod.yml`)
- [x] Script de carga concurrente real: **10 hilos, 500 operaciones de escritura+lectura+borrado** sobre `media/private/expedientes/` dentro del contenedor
- [x] UID/GID confirmados en tiempo de ejecución: **1000/1000 (appuser)**, tal como especifica el `Dockerfile`
- [x] Resultado real: **0 `PermissionError`** en las 500 operaciones

**Pruebas Obligatorias:**
- [x] Test de carga concurrente — ejecutado en un contenedor Docker real (target `production`), no en staging (no existe) ni simulado. Imagen y volumen de prueba eliminados tras verificar.

**Cierre:**
- [x] Documentado aquí (no existe `DEPLOY_PRODUCTION.md` como archivo separado; ver nota de SEC-T001)
- [ ] Verificado en staging — no existe staging; verificado en Docker real en este entorno, limitación ya reconocida desde SEC-T001
- [x] Responsable valida y firma: autorización explícita en esta conversación, fecha: 2026-11-05

---

### SEC-T021 — Evidencias ACD 4 Reales

**Autorización:** [ ] Responsable autorizó SEC-T021 (fecha: ______)

**Precondiciones:**
- [ ] DEC-007 resuelta (placeholders vs datos reales)

**Implementación:**
- [ ] Si placeholders → marcar tarea "NO APLICA" / "CANCELADA"
- [ ] Si datos reales → actualizar `MATRIZ_TRAZABILIDAD_SEGURIDAD.md` sección 11 con:
  - [ ] SHA commits reales
  - [ ] URLs PRs reales
  - [ ] Autores
  - [ ] Archivos modificados
  - [ ] Tests aportados

**Pruebas Obligatorias:**
- [ ] Verificación manual en plataforma Git (GitHub/GitLab)

**Cierre:**
- [ ] Matriz actualizada con evidencias reales
- [ ] Responsable valida y firma: _______________ fecha: ______

---

## Validación Final de Seguridad (Cierre Global)

- [ ] **Hito 0** Base Independiente: SEC-T004, T008, T012, T016, T021 cerradas — parcial: SEC-T004 CERRADA (2026-11-05); T008, T012, T016, T021 pendientes
- [ ] **Hito 1** Producción Lista: SEC-T001 cerrada (staging HTTPS + headers + Swagger 403)
- [ ] **Hito 2** Autenticación Segura: SEC-T003, T004, T005, T006 cerradas
- [ ] **Hito 3** Throttling Operativo: SEC-T002, T008 cerradas
- [ ] **Hito 4** Controles Medios + Errores/Logging: SEC-T007, T009, T010, T011, T013 cerradas
- [ ] **Hito 5** CI/CD Security: SEC-T014, T015 cerradas
- [ ] **Hito 6** Tests Seguridad: SEC-T017 cerrada
- [ ] **Hito 7** Operaciones: SEC-T019, T020 cerradas (post-deploy)
- [ ] **Suite completa** 473+ tests passing + coverage ≥80% en CI
- [ ] **Staging deploy** verificado: Backend + Frontend (specs/003 V-01 a V-09)
- [ ] **Documentación** actualizada: DEPLOY_PRODUCTION.md, SECURITY_CONFIG.md, API_ERROR_FORMAT.md, CI_SECURITY.md, TESTING.md, OPERATIONS.md, FRONTEND_INTEGRATION_GUIDE.md, AUTH_FLOW_CHANGES.md, DOWNLOAD_URL_MIGRATION.md

**Firma Final Responsable Proyecto:** _________________________ **Fecha:** _______________

**Firma Tech Lead:** _________________________ **Fecha:** _______________

**Firma Responsable Seguridad:** _________________________ **Fecha:** _______________