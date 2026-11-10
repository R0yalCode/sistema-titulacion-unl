# FICHAS TÉCNICAS DE EJECUCIÓN — SEC-T001 a SEC-T021

**Fecha:** 2026-11-05  
**Versión:** 1.0  
**Uso:** Cada ficha es instrucción completa para implementar una tarea SEC-TXXX.  
**Regla:** Solo implementar tarea autorizada expresamente por responsable. Una a la vez.

---

## Índice de Fichas

1. [SEC-T001 — Configuración Producción Completa](#sec-t001--configuración-producción-completa)
2. [SEC-T002 — Throttling Login](#sec-t002--throttling-login)
3. [SEC-T003 — Rotación + Blacklist Refresh Tokens](#sec-t003--rotación--blacklist-refresh-tokens)
4. [SEC-T004 — JWT_SIGNING_KEY Separada](#sec-t004--jwt_signing_key-separada)
5. [SEC-T005 — IP Auditoría + Middleware + TRUSTED_PROXIES](#sec-t005--ip-auditoría--middleware--trusted_proxies)
6. [SEC-T006 — Access Token 30 Minutos](#sec-t006--access-token-30-minutos)
7. [SEC-T007 — Validación MIME Real](#sec-t007--validación-mime-real)
8. [SEC-T008 — Throttling Carga Documentos](#sec-t008--throttling-carga-documentos)
9. [SEC-T009 — Remover Rutas Internas Serializers](#sec-t009--remover-rutas-internas-serializers)
10. [SEC-T010 — Handler Global Excepciones](#sec-t010--handler-global-excepciones)
11. [SEC-T011 — Logging Estructurado](#sec-t011--logging-estructurado)
12. [SEC-T012 — Eliminar print() evaluar_checklist.py](#sec-t012--eliminar-print-evaluar_checklistpy)
13. [SEC-T013 — Protección Swagger/ReDoc/Schema](#sec-t013--protección-swaggerredocschema)
14. [SEC-T014 — CI/CD Security (Safety+Bandit+Gitleaks)](#sec-t014--cicd-security-safetybanditgitleaks)
15. [SEC-T015 — Dependabot Configurado](#sec-t015--dependabot-configurado)
16. [SEC-T016 — Cobertura Tests + testpaths](#sec-t016--cobertura-tests--testpaths)
17. [SEC-T017 — Tests Seguridad Faltantes](#sec-t017--tests-seguridad-faltantes)
18. [SEC-T018 — Procedimiento Rotación Secretos](#sec-t018--procedimiento-rotación-secretos)
19. [SEC-T019 — Limpieza Archivos Huérfanos](#sec-t019--limpieza-archivos-huérfanos)
20. [SEC-T020 — Verificación PermissionError Docker](#sec-t020--verificación-permissionerror-docker)
21. [SEC-T021 — Evidencias ACD 4 Reales](#sec-t021--evidencias-acd-4-reales)

---

## SEC-T001 — Configuración Producción Completa

**Objetivo:** Crear configuración completa para entorno productivo: `settings/production.py`, `Dockerfile` multi-stage, `docker-compose.prod.yml` con Nginx + PostgreSQL + Backend, certificados TLS, headers seguridad, usuario no-root.

**Contexto y evidencia:** Auditoría §7 (Hardening Producción - CRÍTICO). Backend no desplegable en producción: sin `production.py`, sin Dockerfile, sin Nginx, sin TLS, sin headers `SECURE_*`, usuario root en contenedor histórico.

**Autorización requerida:** Solo podrá implementarse cuando el responsable autorice expresamente **SEC-T001**.

**Precondiciones:**
- DEC-010 (CSP strategy) aprobada. **[APROBADA 2026-11-05: Opción D]**
- Repositorio limpio (sin cambios locales pendientes).
- Decisiones DEC-002, DEC-003 valores confirmados para config. **[AMBAS APROBADAS 2026-11-05: 5/min/IP y 10/hora/usuario respectivamente]** (Corrección 2026-11-05: esta línea incluía originalmente también a DEC-004, que no corresponde a ningún contenido real de esta ficha — pertenece exclusivamente a SEC-T016. Ver `DECISIONES_TECNICAS_PENDIENTES.md` §10bis.)

**Archivos a inspeccionar:**
- `backend/src/config/settings/base.py` (config base actual)
- `backend/src/config/settings/local.py`, `test.py` (referencia patrones)
- `backend/.env.example` (variables actuales)
- `backend/requirements.txt`, `requirements-dev.txt` (deps para Dockerfile)
- `backend/manage.py` (entrypoint Django)
- `backend/openapi.yaml` (contrato API para validar endpoints)

**Cambios autorizables:**
1. **`backend/src/config/settings/production.py` (NUEVO)** — Hereda de `base.py` con hardening completo:
   - `DEBUG = False`
   - `ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")` (sin default `[]`)
   - `SECURE_SSL_REDIRECT = True`
   - `SECURE_HSTS_SECONDS = 31536000`, `SECURE_HSTS_INCLUDE_SUBDOMAINS = True`, `SECURE_HSTS_PRELOAD = True`
   - `SESSION_COOKIE_SECURE = True`, `SESSION_COOKIE_HTTPONLY = True`, `SESSION_COOKIE_SAMESITE = "Lax"`
   - `CSRF_COOKIE_SECURE = True`, `CSRF_COOKIE_HTTPONLY = True`, `CSRF_COOKIE_SAMESITE = "Lax"`
   - `CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS")`
   - `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")`
   - `TRUSTED_PROXIES = env.list("TRUSTED_PROXIES", default=["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"])`
   - `SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"`
   - `SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"`
   - **CSP** según DEC-010: `Content-Security-Policy-Report-Only` + `frame-ancestors 'none'`, `base-uri 'self'` bloqueantes
   - `LOGGING` dict base (handlers consola, formato JSON `python-json-logger`, nivel INFO, filtros PII)
   - `SPECTACULAR_SETTINGS["SERVE_PERMISSIONS"] = ["rest_framework.permissions.IsAdminUser"]`
   - `REST_FRAMEWORK.DEFAULT_THROTTLE_RATES["auth"] = "5/minute"` (DEC-002)
   - `REST_FRAMEWORK.DEFAULT_THROTTLE_RATES["document_upload"] = "10/hour"` (DEC-003)
   - `REST_FRAMEWORK.EXCEPTION_HANDLER = "core.adapters.exceptions.custom_exception_handler"`
   - `CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS")` (requiere `django-cors-headers` en requirements)

2. **`backend/Dockerfile` (NUEVO)** — Multi-stage:
   ```dockerfile
   # Stage 1: Builder
   FROM python:3.12-slim AS builder
   WORKDIR /app
   RUN apt-get update && apt-get install -y --no-install-recommends \
       gcc libpq-dev python3-dev \
       && rm -rf /var/lib/apt/lists/*
   COPY requirements.txt requirements-dev.txt ./
   RUN pip install --no-cache-dir --user -r requirements.txt -r requirements-dev.txt

   # Stage 2: Runtime
   FROM python:3.12-slim
   WORKDIR /app
   RUN apt-get update && apt-get install -y --no-install-recommends \
       libpq5 \
       && rm -rf /var/lib/apt/lists/*
   # Si DEC-001 = python-magic: RUN apt-get update && apt-get install -y libmagic1 && rm -rf /var/lib/apt/lists/*
   COPY --from=builder /root/.local /root/.local
   ENV PATH=/root/.local/bin:$PATH
   RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
   USER appuser
   COPY --chown=appuser:appuser src/ ./src/
   COPY --chown=appuser:appuser manage.py ./
   COPY --chown=appuser:appuser .env.example ./
   EXPOSE 8000
   HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
       CMD curl -f http://localhost:8000/health/ || exit 1
   ENTRYPOINT ["./entrypoint.sh"]
   ```

3. **`backend/entrypoint.sh` (NUEVO)**:
   ```bash
   #!/bin/sh
   set -e
   python manage.py migrate --noinput
   python manage.py collectstatic --noinput
   exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 60 --access-logfile - --error-logfile -
   ```

4. **`backend/docker-compose.prod.yml` (NUEVO)**:
   ```yaml
   version: '3.8'
   services:
     backend:
       build: .
       env_file: .env.prod
       volumes:
         - media_private:/app/media/private
       depends_on:
         - postgres
       networks: [internal]
     postgres:
       image: postgres:16-alpine
       env_file: .env.prod
       volumes:
         - postgres_data:/var/lib/postgresql/data
       networks: [internal]
     nginx:
       image: nginx:alpine
       ports: ["80:80", "443:443"]
       volumes:
         - ./nginx/prod.conf:/etc/nginx/nginx.conf:ro
         - ./nginx/certs:/etc/nginx/certs:ro
         - media_private:/media/private:ro
       depends_on: [backend]
       networks: [internal, external]
   volumes:
     media_private:
     postgres_data:
   networks:
     internal:
     external:
   ```

5. **`backend/nginx/prod.conf` (NUEVO)** — TLS, rate limiting, headers seguridad, proxy headers.
6. **`backend/.env.example` (ACTUALIZAR)** — Añadir: `JWT_SIGNING_KEY`, `TRUSTED_PROXIES`, `CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS`, `AUTH_THROTTLE_RATE`, `DOCUMENT_UPLOAD_THROTTLE`, `ORPHAN_RETENTION_DAYS`.

**Cambios prohibidos:**
- Modificar `base.py` settings base (solo `production.py` sobrescribe).
- Cambiar reglas de negocio, permisos RBAC, serializers, modelos.
- Modificar `local.py` o `test.py` (excepto sincronizar imports si necesario).
- Instalar dependencias no listadas en requirements sin aprobación.

**Procedimiento recomendado:**
1. Crear `production.py` copiando `base.py` y aplicando hardening línea a línea.
2. Crear `Dockerfile` + `entrypoint.sh` + `docker-compose.prod.yml` + `nginx/prod.conf`.
3. Actualizar `.env.example` con todas las variables nuevas.
4. Build imagen: `docker build -t sgt-siaaf-backend .`
5. Levantar staging: `docker-compose -f docker-compose.prod.yml up -d`
6. Verificar salud: `curl -k https://localhost/health/` → 200
7. Ejecutar suite tests en contenedor: `docker-compose exec backend pytest`

**Pruebas obligatorias:**
1. Build imagen Docker sin errores.
2. `docker-compose -f docker-compose.prod.yml up -d` → servicios healthy.
3. `curl -k https://localhost/health/` → 200.
4. `curl -k https://localhost/api/v1/docs/` → 403 (IsAdminUser).
4. `curl -k https://localhost/api/v1/auth/token/` con credenciales válidas → 200 + JWT.
5. Headers respuesta: `Strict-Transport-Security`, `X-Frame-Options`, `Content-Security-Policy`, `X-Content-Type-Options`, `Referrer-Policy`.
6. Cookies: `Secure`, `HttpOnly`, `SameSite=Lax`.
7. Logs JSON rotativos en `docker-compose logs backend`.
8. Suite 473 tests en contenedor (PostgreSQL real) → 0 failed.

**Regresión obligatoria:**
- Flujos críticos: login → expediente → peticiones → carga docs → checklist → informe → declaratoria.
- Frontend contra backend staging (specs/003 vistas V-01 a V-09).

**Compatibilidad frontend:**
- **IMPACTO ALTO** — Ver `MATRIZ_COMPATIBILIDAD_BACKEND_FRONTEND_SEGURIDAD.md` SEC-T001.
- `API_BASE_URL` → HTTPS; Cookies seguras; CSRF token en requests mutantes; CORS origins.

**Criterios de aceptación:**
- Todos los checks de "Pruebas obligatorias" pasando.
- `DEPLOY_PRODUCTION.md` documentado.
- Imagen Docker en registry.
- Staging deploy verificado por QA.

**Evidencias de cierre:**
- `production.py`, `Dockerfile`, `docker-compose.prod.yml`, `nginx/prod.conf`, `entrypoint.sh`, `.env.example` creados/actualizados.
- Logs build y staging deploy.
- Resultados tests en contenedor.

**Rollback:**
- `docker-compose -f docker-compose.prod.yml down -v` (elimina volúmenes staging).
- Eliminar archivos creados: `production.py`, `Dockerfile`, `docker-compose.prod.yml`, `nginx/`, `entrypoint.sh`.
- Restaurar `.env.example` previo.

**Dependencias:** Desbloquea SEC-T005, SEC-T007, SEC-T010, SEC-T011, SEC-T013, SEC-T014, SEC-T019, SEC-T020. (Nota 2026-11-05: esta lista incluía originalmente a SEC-T004, lo cual contradecía la propia ficha de SEC-T004 — "Dependencias: Ninguna (independiente)" — y quedó refutado empíricamente: SEC-T004 se implementó, validó y cerró sin que SEC-T001 existiera. Corregido tras auditoría de coherencia documental.)

**Condición de bloqueo:** Si DEC-010 (CSP) no aprobada → esperar. Si build Docker falla → debug antes de continuar.

---

## SEC-T002 — Throttling Login

**Objetivo:** Implementar rate limiting 5 requests/minuto/IP (o valor DEC-002) en `POST /api/v1/auth/token/` usando `AnonRateThrottle`.

**Contexto y evidencia:** CHECKLIST SEC-AUTH-01 (PENDIENTE), MATRIZ A1 (PENDIENTE). Endpoint `TokenPairView` sin throttling; vulnerable a fuerza bruta.

**Autorización requerida:** Solo podrá implementarse cuando el responsable autorice expresamente **SEC-T002**.

**Precondiciones:**
- SEC-T005 CERRADA (TRUSTED_PROXIES + middleware funcionando → IP real confiable).
- DEC-002 aprobada (límite exacto: 5/min/IP u otro).

**Archivos a inspeccionar:**
- `backend/src/config/settings/base.py` (REST_FRAMEWORK config)
- `backend/src/config/settings/production.py` (sobrescribe rates)
- `backend/src/apps/authentication/adapters/views.py` (TokenPairView línea 8)

**Cambios autorizables:**
1. `base.py` / `production.py`: `REST_FRAMEWORK.DEFAULT_THROTTLE_RATES["auth"] = "5/minute"` (o valor DEC-002).
2. `authentication/adapters/views.py`: `TokenPairView` añadir:
   ```python
   from rest_framework.throttling import AnonRateThrottle
   class TokenPairView(BaseTokenObtainPairView):
       serializer_class = TokenObtainPairSerializer
       throttle_classes = [AnonRateThrottle]
       throttle_scope = "auth"
   ```

**Cambios prohibidos:**
- Modificar `TokenObtainPairSerializer` o lógica JWT.
- Cambiar códigos HTTP de login (200/401 existentes).
- Usar `UserRateThrottle` (requiere usuario autenticado; login es anónimo).

**Procedimiento recomendado:**
1. Añadir throttle rate en `production.py` (y `base.py` para desarrollo).
2. Modificar `TokenPairView` con `throttle_classes` y `throttle_scope`.
3. Verificar que `AnonRateThrottle` usa IP de `request.META.get("REMOTE_ADDR")` (poblada por middleware SEC-T005).
4. Tests manuales: 6 POST rápidos → 429 en el 6º.

**Pruebas obligatorias (nuevas en `authentication/tests/test_security_controls.py`):**
1. `test_login_throttle_allows_5_requests_per_minute` — 5 POST sucesivos → 200.
2. `test_login_throttle_6th_request_returns_429` — 6º POST → 429 con formato uniforme (SEC-T010).
3. `test_login_throttle_resets_after_window` — esperar 61 seg → 200.
4. `test_login_throttle_per_ip_isolation` — IP A agota, IP B tiene 5.
5. `test_login_throttle_respects_trusted_proxies` — `X-Forwarded-For` válido vs spoofed (via SEC-T005).

**Regresión obligatoria:**
- Tests auth existentes (`test_jwt.py` 6 tests) passing.
- Login normal funciona sin throttling en uso legítimo.

**Compatibilidad frontend:**
- **IMPACTO BAJO** — Frontend recibe 429 en login masivo; debe mostrar mensaje "Demasiados intentos, espera X minutos". Ver `MATRIZ_COMPATIBILIDAD_BACKEND_FRONTEND_SEGURIDAD.md` SEC-T002.

**Criterios de aceptación:**
- Tests pasando.
- Configuración en `base.py` y `production.py`.
- Documentado en `SECURITY_CONFIG.md`.

**Evidencias de cierre:**
- `views.py` modificado, `production.py` actualizado.
- Tests nuevos pasando.
- `SECURITY_CONFIG.md` actualizado.

**Rollback:**
- Revertir `TokenPairView` a versión sin `throttle_classes`.
- Eliminar `auth` de `DEFAULT_THROTTLE_RATES`.

**Dependencias:** SEC-T005 (TRUSTED_PROXIES). Desbloquea SEC-T017 (tests).

**Condición de bloqueo:** Si SEC-T005 no cerrada → IP no confiable → throttling por IP de proxy → bloqueo masivo. Esperar SEC-T005.

---

## SEC-T003 — Rotación + Blacklist Refresh Tokens

**Objetivo:** Habilitar rotación automática de refresh tokens (`ROTATE_REFRESH_TOKENS=True`), blacklist de tokens rotados (`BLACKLIST_AFTER_ROTATION=True`), instalar/migrar `rest_framework_simplejwt.token_blacklist`, implementar endpoint `POST /api/v1/auth/logout/`.

**Contexto y evidencia:** CHECKLIST SEC-AUTH-02 (FALLIDO/PENDIENTE), MATRIZ A2,A3,A6 (FALLIDO/PENDIENTE). Refresh tokens no rotan ni se revocan; robo = acceso indefinido.

**Autorización requerida:** Solo podrá implementarse cuando el responsable autorice expresamente **SEC-T003**.

**Precondiciones:**
- SEC-T004 CERRADA (JWT_SIGNING_KEY separada — rotación usa misma clave firma).
- DEC-008 decidida (refresh token storage frontend: httpOnly cookie vs localStorage).

**Archivos a inspeccionar:**
- `backend/src/config/settings/base.py` (SIMPLE_JWT config, INSTALLED_APPS)
- `backend/src/apps/authentication/adapters/views.py` (añadir LogoutView)
- `backend/src/apps/authentication/adapters/urls.py` (si existe, o `config/urls.py`)

**Cambios autorizables:**
1. `base.py`: `INSTALLED_APPS` añadir `"rest_framework_simplejwt.token_blacklist"`.
2. `base.py`: `SIMPLE_JWT.ROTATE_REFRESH_TOKENS = True`, `BLACKLIST_AFTER_ROTATION = True`.
3. Ejecutar `python manage.py migrate` (migraciones `token_blacklist`).
4. `authentication/adapters/views.py`: Nuevo `LogoutView`:
   ```python
   from rest_framework.views import APIView
   from rest_framework.response import Response
   from rest_framework.permissions import IsAuthenticated
   from rest_framework_simplejwt.tokens import RefreshToken
   from rest_framework import status

   class LogoutView(APIView):
       permission_classes = [IsAuthenticated]
       authentication_classes = [JWTAuthentication]

       def post(self, request):
           refresh_token = request.data.get("refresh")
           if not refresh_token:
               return Response({"detail": "Refresh token requerido"}, status=status.HTTP_400_BAD_REQUEST)
           try:
               token = RefreshToken(refresh_token)
               token.blacklist()
           except Exception:
               return Response({"detail": "Token inválido"}, status=status.HTTP_400_BAD_REQUEST)
           response = Response(status=status.HTTP_205_RESET_CONTENT)
           # Si DEC-008 = httpOnly cookie:
           response.delete_cookie('refresh_token', secure=True, httponly=True, samesite='Lax')
           return response
   ```
5. `config/urls.py`: Añadir `path("api/v1/auth/logout/", LogoutView.as_view(), name="auth-logout")`.

**Cambios prohibidos:**
- Modificar `TokenObtainPairSerializer` o `TokenRefreshSerializer`.
- Cambiar lifetime de refresh token (24h actual OK).
- Deshabilitar rotación en tests (tests deben validar rotación real).

**Procedimiento recomendado:**
1. Añadir app a `INSTALLED_APPS` y configurar `SIMPLE_JWT` flags.
2. Ejecutar migraciones: `python manage.py migrate`.
3. Crear `LogoutView` y registrar en URLs.
4. Verificar rotación: login → refresh → nuevo access + nuevo refresh; refresh anterior en blacklist.
5. Tests exhaustivos rotación + blacklist + logout.

**Pruebas obligatorias (nuevas en `authentication/tests/test_security_controls.py`):**
1. `test_refresh_rotates_token_returns_new_access_and_refresh` — refresh válido → nuevo access ≠ anterior, nuevo refresh ≠ anterior.
2. `test_old_refresh_rejected_after_rotation` — usar refresh anterior → 401 `Token is blacklisted`.
3. `test_blacklisted_refresh_rejected` — POST /logout/ con refresh → posterior refresh con mismo → 401.
4. `test_logout_requires_authentication` — sin token → 401.
5. `test_refresh_token_lifetime_respected` — refresh expira a 24h → 401.

**Regresión obligatoria:**
- Tests JWT existentes (`test_jwt.py` 6 tests) passing.
- Flujo: login → acceso recurso → refresh → acceso → logout → intento refresh → 401.

**Compatibilidad frontend:**
- **IMPACTO MEDIO** — Ver `MATRIZ_COMPATIBILIDAD_BACKEND_FRONTEND_SEGURIDAD.md` SEC-T003.
- Frontend: interceptor axios guarda nuevo refresh, llama `POST /auth/logout/` al cerrar sesión, maneja 401 en refresh → redirect login.
- Coordinación via issue frontend + `AUTH_FLOW_CHANGES.md`.

**Criterios de aceptación:**
- Migraciones aplicadas.
- Tests pasando.
- Endpoint logout documentado en OpenAPI.
- Frontend actualizado (issue separado cerrado).

**Evidencias de cierre:**
- `base.py` actualizado, `views.py` con `LogoutView`, `urls.py` actualizado.
- Tests nuevos pasando.
- `SECURITY_CONFIG.md` actualizado.

**Rollback:**
- `python manage.py migrate token_blacklist zero` (revierte migraciones).
- Eliminar app de `INSTALLED_APPS`.
- Revertir `SIMPLE_JWT` flags a `False`.
- Eliminar `LogoutView` y URL.

**Dependencias:** SEC-T004 (JWT_SIGNING_KEY). Desbloquea SEC-T017 (tests).

**Condición de bloqueo:** Si SEC-T004 no cerrada → rotación usa SECRET_KEY compartida → riesgo. Esperar SEC-T004.

---

## SEC-T004 — JWT_SIGNING_KEY Separada de SECRET_KEY

**Objetivo:** Separar `JWT_SIGNING_KEY` de `SECRET_KEY` mediante variable de entorno dedicada. `SECRET_KEY` para Django (sesiones, CSRF, cookies); `JWT_SIGNING_KEY` para firmar/verificar JWTs.

**Contexto y evidencia:** CHECKLIST SEC-SEC-01 (FALLIDO), MATRIZ D4 (FALLIDO). `SIGNING_KEY = SECRET_KEY` en `base.py:110` — compromiso dual.

**Autorización requerida:** Solo podrá implementarse cuando el responsable autorice expresamente **SEC-T004**.

**Precondiciones:** Ninguna (independiente, inicia Fase 0).

**Archivos a inspeccionar:**
- `backend/src/config/settings/base.py` (línea 110: `SIGNING_KEY = SECRET_KEY`)
- `backend/.env.example` (variables actuales)

**Cambios autorizables:**
1. `base.py`: `SIMPLE_JWT.SIGNING_KEY = env("JWT_SIGNING_KEY")` (nueva variable obligatoria).
2. `base.py`: `SECRET_KEY = env("SECRET_KEY")` sin cambios.
3. `production.py`: Validar que ambas existan y sean distintas (log warning si iguales).
4. `.env.example`: Documentar ambas con instrucciones generación:
   ```bash
   # Generar claves seguras (≥32 bytes para HS256):
   # openssl rand -base64 32
   SECRET_KEY=tu-secret-key-django-aqui
   JWT_SIGNING_KEY=tu-jwt-signing-key-aqui
   ```

**Cambios prohibidos:**
- Usar misma clave para ambas (debe fallar validación en production.py).
- Hardcodear claves en settings.
- Cambiar algoritmo JWT (HS256 actual OK).

**Procedimiento recomendado:**
1. Modificar `base.py` línea 110: `SIGNING_KEY = env("JWT_SIGNING_KEY")`.
2. Añadir validación en `production.py`:
   ```python
   if SIMPLE_JWT["SIGNING_KEY"] == SECRET_KEY:
       import logging
       logging.warning("JWT_SIGNING_KEY == SECRET_KEY: RIESGO CRÍTICO - Separar claves en producción")
   ```
3. Actualizar `.env.example` con ambas variables.
4. Generar claves para staging/prod: `openssl rand -base64 32`.
5. Deploy staging con nuevas claves → verificar login + tokens + sesiones admin.

**Pruebas obligatorias (nuevas en `authentication/tests/test_security_controls.py`):**
1. `test_jwt_signing_key_separate_from_secret_key` — `SIMPLE_JWT.SIGNING_KEY != SECRET_KEY`.
2. `test_jwt_token_verification_uses_jwt_signing_key` — token firmado con JWT_SIGNING_KEY válido; firmado con SECRET_KEY → 401.
3. `test_django_sessions_use_secret_key` — sesión/cookie firmada con SECRET_KEY funciona independientemente.

**Regresión obligatoria:**
- Deploy staging con nuevas claves → login funciona → tokens nuevos válidos.
- Sesiones Django admin siguen funcionando.

**Compatibilidad frontend:**
- **NINGUNO** — Cambio interno; tokens JWT existentes se invalidan (requiere re-login único tras deploy). Ver `MATRIZ_COMPATIBILIDAD_BACKEND_FRONTEND_SEGURIDAD.md` SEC-T004.

**Criterios de aceptación:**
- Variables en `.env.example`.
- Tests pasando.
- Documentado procedimiento rotación independiente en `SECURITY_CONFIG.md`.

**Evidencias de cierre:**
- `base.py` línea 110 modificada.
- `.env.example` actualizado.
- Tests pasando.
- `SECURITY_CONFIG.md` con procedimiento rotación.

**Rollback:**
- Revertir `base.py` a `SIGNING_KEY = SECRET_KEY`.
- Eliminar `JWT_SIGNING_KEY` de `.env.example` y entornos.
- Re-deploy con clave única (invalida tokens → re-login).

**Dependencias:** Ninguna (independiente). Desbloquea SEC-T003, SEC-T006, SEC-T018.

**Condición de bloqueo:** Ninguna. Puede iniciar inmediatamente (Fase 0).

---

## SEC-T005 — IP Auditoría + Middleware Thread-Local + TRUSTED_PROXIES

**Objetivo:** Implementar captura confiable de IP cliente para auditoría: middleware thread-local, `_get_current_request()` leyendo thread-local, `_get_client_ip()` validando `X-Forwarded-For` contra `TRUSTED_PROXIES`, configurar `SECURE_PROXY_SSL_HEADER` y `TRUSTED_PROXIES` en `production.py`.

**Contexto y evidencia:** CHECKLIST SEC-LOG-03 (FALLIDO), MATRIZ F9,F10 (FALLIDO/IMPLEMENTADO SIN PRUEBA). `_get_current_request()` retorna `None`; IP suplantable via `X-Forwarded-For` sin validación.

**Autorización requerida:** Solo podrá implementarse cuando el responsable autorice expresamente **SEC-T005**.

**Precondiciones:**
- SEC-T001 CERRADA (production.py + Nginx proxy real existe).

**Archivos a inspeccionar:**
- `backend/src/apps/notificaciones/adapters/signals.py` (líneas 22-36, 52-58: `_get_client_ip`, `_get_current_request`, `_crear_evento_auditoria`)
- `backend/src/apps/notificaciones/adapters/models.py` (línea 103: `EventoAuditoria.ip`)
- `backend/src/config/settings/base.py` (MIDDLEWARE list)
- `backend/src/config/settings/production.py` (nuevas settings)

**Cambios autorizables:**
1. **`core/adapters/middleware.py` (NUEVO)**:
   ```python
   import threading
   _thread_local = threading.local()

   class ThreadLocalRequestMiddleware:
       def __init__(self, get_response):
           self.get_response = get_response

       def __call__(self, request):
           _thread_local.request = request
           return self.get_response(request)

   def get_current_request():
       return getattr(_thread_local, 'request', None)
   ```
2. `base.py`: Insertar `ThreadLocalRequestMiddleware` **PRIMERO** en `MIDDLEWARE` list (antes de `SecurityMiddleware`).
3. `notificaciones/adapters/signals.py`:
   - Reemplazar `_get_current_request()` → `from core.adapters.middleware import get_current_request`
   - Actualizar `_get_client_ip(request)`:
     ```python
     import ipaddress
     from django.conf import settings

     def _get_client_ip(request):
         if request is None:
             return None
         xff = request.META.get("HTTP_X_FORWARDED_FOR")
         remote_addr = request.META.get("REMOTE_ADDR")
         trusted_proxies = getattr(settings, "TRUSTED_PROXIES", [])
         if xff and remote_addr:
             # Validar que REMOTE_ADDR está en TRUSTED_PROXIES
             client_ip = ipaddress.ip_address(remote_addr)
             for proxy_cidr in trusted_proxies:
                 if client_ip in ipaddress.ip_network(proxy_cidr):
                     # Proxy confiable: usar primer IP de X-Forwarded-For
                     return xff.split(",")[0].strip()
         # Proxy no confiable o sin XFF: usar REMOTE_ADDR
         return remote_addr
     ```
4. `production.py`:
   - `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")`
   - `TRUSTED_PROXIES = env.list("TRUSTED_PROXIES", default=["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"])`
5. Verificar `EventoAuditoria.ip` poblado en signals automáticas (crear expediente, cambiar estado, evaluar checklist, cargar doc, emitir informe, registrar declaratoria).

**Cambios prohibidos:**
- Modificar `EventoAuditoria` model o migraciones.
- Cambiar señales existentes salvo `_get_current_request` y `_get_client_ip`.
- Usar `threading.local()` en vistas directamente (centralizar en middleware).

**Procedimiento recomendado:**
1. Crear `core/adapters/middleware.py` con `ThreadLocalRequestMiddleware` y `get_current_request()`.
2. Insertar middleware **PRIMERO** en `MIDDLEWARE` en `base.py`.
3. Actualizar `signals.py` para usar nuevo `get_current_request()` y `_get_client_ip()` con validación `TRUSTED_PROXIES`.
4. Añadir `SECURE_PROXY_SSL_HEADER` y `TRUSTED_PROXIES` en `production.py`.
5. Verificar en staging con Nginx real: `X-Forwarded-For` llega, IP capturada en `EventoAuditoria`.

**Pruebas obligatorias (nuevas en `notificaciones/tests/test_audit_ip.py`):**
1. `test_audit_ip_captured_from_xff_with_trusted_proxy` — request con `X-Forwarded-For: 203.0.113.195, 198.51.100.1` + `REMOTE_ADDR=10.0.0.1` (trusted) → IP = `203.0.113.195`.
2. `test_audit_ip_spoofing_blocked_untrusted_proxy` — request con `X-Forwarded-For: 203.0.113.195` + `REMOTE_ADDR=203.0.113.195` (no trusted) → IP = `203.0.113.195` (REMOTE_ADDR).
3. `test_audit_ip_persisted_in_eventoauditoria` — crear expediente via API → `EventoAuditoria.objects.latest().ip == "203.0.113.195"`.
4. `test_audit_ip_none_when_no_request` — signal fuera de request (management command) → IP = None.

**Regresión obligatoria:**
- Tests auditoría existentes (`test_auditoria.py` 14 tests) passing.
- Flujo completo crea eventos → verificar IP en `EventoAuditoria`.

**Compatibilidad frontend:**
- **NINGUNO** — Interno de auditoría. Ver `MATRIZ_COMPATIBILIDAD_BACKEND_FRONTEND_SEGURIDAD.md` SEC-T005.

**Criterios de aceptación:**
- Middleware en `MIDDLEWARE[0]`.
- Tests pasando.
- `TRUSTED_PROXIES` documentado en `.env.example` y `DEPLOY_PRODUCTION.md`.

**Evidencias de cierre:**
- `middleware.py` creado, `base.py` MIDDLEWARE actualizado, `signals.py` modificado, `production.py` con settings.
- Tests pasando.

**Rollback:**
- Eliminar middleware de `MIDDLEWARE`.
- Revertir `signals.py` a `_get_current_request()` retorna `None` y `_get_client_ip` simple.
- Eliminar `SECURE_PROXY_SSL_HEADER` y `TRUSTED_PROXIES` de `production.py`.

**Dependencias:** SEC-T001 (production.py + Nginx). Desbloquea SEC-T002 (throttling login IP real).

**Condición de bloqueo:** Si SEC-T001 no cerrada → no hay Nginx real ni `production.py` → `TRUSTED_PROXIES` no aplicable. Esperar SEC-T001.

---

## SEC-T006 — Access Token 30 Minutos

**Objetivo:** Cambiar `SIMPLE_JWT.ACCESS_TOKEN_LIFETIME` de 60 a 30 minutos según decisión ACD.

**Contexto y evidencia:** CHECKLIST SEC-AUTH-03 (FALLIDO), MATRIZ A4 (FALLIDO). `timedelta(minutes=60)` en `base.py:106` vs 30 min ACD.

**Autorización requerida:** Solo podrá implementarse cuando el responsable autorice expresamente **SEC-T006**.

**Precondiciones:**
- SEC-T004 CERRADA (JWT_SIGNING_KEY separada — cambio lifetime invalida tokens existentes; clave separada evita impacto sesiones Django).

**Archivos a inspeccionar:**
- `backend/src/config/settings/base.py` (línea 106)

**Cambios autorizables:**
1. `base.py` / `production.py`: `SIMPLE_JWT.ACCESS_TOKEN_LIFETIME = timedelta(minutes=30)`.

**Cambios prohibidos:**
- Cambiar `REFRESH_TOKEN_LIFETIME` (24h OK).
- Cambiar algoritmo (HS256 OK).

**Procedimiento recomendado:**
1. Modificar `base.py` línea 106: `ACCESS_TOKEN_LIFETIME = timedelta(minutes=30)`.
2. `production.py` hereda (o sobrescribe mismo valor).
3. Tests: login → decodificar access → `exp - iat == 1800`.

**Pruebas obligatorias (nuevas en `authentication/tests/test_security_controls.py`):**
1. `test_access_token_lifetime_30_minutes` — decodificar access token → `exp - iat == 1800`.
2. `test_access_token_expired_after_31_minutes_rejected` — token con `exp = now + 31 min` → 401.

**Regresión obligatoria:**
- Tests JWT existentes + nuevo test lifetime.
- Verificar: login → acceso a los 29 min → OK; a los 31 min → 401 → refresh → OK.

**Compatibilidad frontend:**
- **IMPACTO BAJO** — Interceptor refresh ya maneja expiración; solo más frecuente (~25 min). Ver `MATRIZ_COMPATIBILIDAD_BACKEND_FRONTEND_SEGURIDAD.md` SEC-T006.

**Criterios de aceptación:**
- Configuración actualizada.
- Test pasando.
- Documentado en `SECURITY_CONFIG.md`.

**Evidencias de cierre:**
- `base.py` línea 106 modificada.
- Test pasando.

**Rollback:**
- Revertir a `timedelta(minutes=60)`.
- Re-deploy (invalida tokens → re-login).

**Dependencias:** SEC-T004 (JWT_SIGNING_KEY). 

**Condición de bloqueo:** Si SEC-T004 no cerrada → cambio lifetime invalida tokens Y usa SECRET_KEY compartida. Esperar SEC-T004.

---

## SEC-T007 — Validación MIME Real

**Objetivo:** Evaluar e implementar validación MIME real de contenido PDF más allá de magic bytes: `python-magic` (libmagic) o `pikepdf` (parseo PDF). Decidir según DEC-001.

**Contexto y evidencia:** CHECKLIST SEC-VAL-01 (PARCIAL), MATRIZ C3 (PARCIAL). Solo magic bytes; PDF políglota pasa.

**Autorización requerida:** Solo podrá implementarse cuando el responsable autorice expresamente **SEC-T007** y **DEC-001 aprobada**.

**Precondiciones:**
- SEC-T001 CERRADA (Dockerfile listo para deps sistema si `python-magic`).
- DEC-001 aprobada (método elegido).

**Archivos a inspeccionar:**
- `backend/src/core/adapters/pdf_validation.py` (función `validar_pdf_completo`)
- `backend/requirements.txt` (deps)
- `backend/Dockerfile` (deps sistema)

**Cambios autorizables:**
1. **Si DEC-001 = `python-magic`:**
   - `requirements.txt`: `python-magic>=0.4,<1.0`
   - `Dockerfile`: `apk add libmagic1` (o `libmagic` en Debian)
   - `pdf_validation.py`: En `validar_pdf_completo()`, antes de `validar_magic_bytes`:
     ```python
     import magic
     mime = magic.from_buffer(file.read(2048), mime=True)
     file.seek(0)
     if mime != "application/pdf":
         raise PDFValidationError("MIME type no es application/pdf", code="invalid_mime_type")
     ```
2. **Si DEC-001 = `pikepdf`:**
   - `requirements.txt`: `pikepdf>=8.0,<9.0`
   - `pdf_validation.py`: En `validar_pdf_completo()`:
     ```python
     import pikepdf
     try:
         pos = file.tell()
         file.seek(0)
         pikepdf.open(file)  # Valida estructura PDF real
         file.seek(pos)
     except pikepdf.PdfError as e:
         raise PDFValidationError(f"Estructura PDF inválida: {e}", code="invalid_pdf_structure")
     ```

**Cambios prohibidos:**
- Eliminar validaciones existentes (magic bytes, tamaño, hash SHA-256).
- Cambiar orden: validación MIME real **ANTES** de guardar archivo.
- Añadir dependencias no aprobadas en DEC-001.

**Procedimiento recomendado:**
1. Implementar según DEC-001 en `validar_pdf_completo()`.
2. Añadir dep en `requirements.txt` y Dockerfile si aplica.
3. Tests exhaustivos: PDF válido, PDF+ZIP (polyglot), PDF corrupto, PDF firmado digitalmente UNL.

**Pruebas obligatorias (nuevas en `core/adapters/tests/test_pdf_validation.py`):**
1. `test_pdf_validation_real_mime_passes_valid_pdf` — PDF real → pasa.
2. `test_pdf_validation_rejects_polyglot_pdf_zip` — PDF+ZIP → rechaza (MIME application/zip o estructura inválida).
3. `test_pdf_validation_rejects_corrupted_pdf_structure` — PDF xref corrupto → rechaza.
4. `test_pdf_validation_docker_compatibility` — build Dockerfile → éxito.

**Regresión obligatoria:**
- Tests PDF existentes (25+ tests) passing.
- Carga docs normal funciona.

**Compatibilidad frontend:**
- **NINGUNO** — Validación interna más estricta; mismo 400 si inválido. Ver `MATRIZ_COMPATIBILIDAD_BACKEND_FRONTEND_SEGURIDAD.md` SEC-T007.

**Criterios de aceptación:**
- ADR documentado (DEC-001).
- Implementación elegida funcionando.
- Tests pasando.
- Docker build exitoso.

**Evidencias de cierre:**
- `pdf_validation.py` modificado.
- `requirements.txt` / `Dockerfile` actualizados.
- Tests nuevos pasando.
- ADR en `docs/architecture/decisions/`.

**Rollback:**
- Revertir `pdf_validation.py` a solo magic bytes + tamaño + hash.
- Eliminar dep de `requirements.txt` y Dockerfile.

**Dependencias:** SEC-T001 (Dockerfile), DEC-001 (método aprobado).

**Condición de bloqueo:** Si DEC-001 no aprobada → no implementar. Esperar decisión.

---

## SEC-T008 — Throttling Carga Documentos

**Objetivo:** Implementar rate limiting en `POST /api/v1/peticiones/{id}/documento/`: 10 cargas/hora/usuario (o valor DEC-003) usando `UserRateThrottle`.

**Contexto y evidencia:** CHECKLIST SEC-VAL-02 (PENDIENTE), MATRIZ C7 (PENDIENTE). Sin límite → DoS almacenamiento.

**Autorización requerida:** Solo podrá implementarse cuando el responsable autorice expresamente **SEC-T008**.

**Precondiciones:**
- DEC-003 aprobada (límite exacto: 10/hora/user u otro).

**Archivos a inspeccionar:**
- `backend/src/config/settings/base.py` / `production.py` (REST_FRAMEWORK)
- `backend/src/apps/peticiones/adapters/views.py` (línea 151: `cargar_documento` action)

**Cambios autorizables:**
1. `base.py` / `production.py`: `REST_FRAMEWORK.DEFAULT_THROTTLE_RATES["document_upload"] = "10/hour"` (o valor DEC-003).
2. `peticiones/adapters/views.py`: En `PeticionViewSet`:
   ```python
   from rest_framework.throttling import UserRateThrottle

   @action(detail=True, methods=["post"], throttle_classes=[UserRateThrottle], throttle_scope="document_upload")
   def cargar_documento(self, request, pk=None):
       # ... código existente
   ```
   O configurar en clase:
   ```python
   def get_throttles(self):
       if self.action == "cargar_documento":
           return [UserRateThrottle()]
       return super().get_throttles()
   ```
   Y `throttle_scope = "document_upload"` en acción.

**Cambios prohibidos:**
- Usar `AnonRateThrottle` (carga requiere autenticación).
- Aplicar throttling a `descargar_documento` (GET).
- Cambiar códigos HTTP de carga exitosa (201) o error validación (400).

**Procedimiento recomendado:**
1. Añadir rate en `production.py` (y `base.py`).
2. Configurar `throttle_classes` y `throttle_scope` en `cargar_documento` action.
3. Tests: 11 POST rápidos mismo usuario → 429 en el 11º.

**Pruebas obligatorias (nuevas en `peticiones/tests/test_upload_throttle.py`):**
1. `test_document_upload_throttle_allows_10_per_hour` — 10 POST → 201.
2. `test_document_upload_throttle_11th_returns_429` — 11º POST → 429 formato uniforme.
3. `test_document_upload_throttle_per_user_isolation` — Usuario A agota, Usuario B tiene 10.
4. `test_document_upload_throttle_resets_after_hour` — esperar 61 min → 201.

**Regresión obligatoria:**
- Tests carga docs existentes passing.
- Carga normal funciona.

**Compatibilidad frontend:**
- **IMPACTO BAJO** — Frontend muestra mensaje "Límite de cargas alcanzado, espera X minutos" en 429. Ver `MATRIZ_COMPATIBILIDAD_BACKEND_FRONTEND_SEGURIDAD.md` SEC-T008.

**Criterios de aceptación:**
- Tests pasando.
- Configuración en `base.py`/`production.py`.
- Documentado.

**Evidencias de cierre:**
- `views.py` modificado, `production.py` actualizado.
- Tests nuevos pasando.

**Rollback:**
- Eliminar `throttle_classes`/`throttle_scope` de acción.
- Eliminar `document_upload` de `DEFAULT_THROTTLE_RATES`.

**Dependencias:** Ninguna (independiente, Fase 0). Desbloquea SEC-T017 (tests).

**Condición de bloqueo:** Si DEC-003 no aprobada → esperar decisión.

---

## SEC-T009 — Remover Rutas Internas Serializers

**Objetivo:** Eliminar `archivo_path` (DocumentoEntregadoSerializer) y `archivo_memorando_firmado_path` (DeclaratoriaAptitudSerializer) de respuestas API. Sustituir por `download_url` opaco apuntando a endpoint descarga autorizado.

**Contexto y evidencia:** CHECKLIST SEC-SEC-02 (FALLIDO), MATRIZ C8 (FALLIDO). Serializers exponen estructura almacenamiento privado.

**Autorización requerida:** Solo podrá implementarse cuando el responsable autorice expresamente **SEC-T009**.

**Precondiciones:**
- SEC-T001 CERRADA.
- DEC-006 implementada (endpoint `GET /api/v1/declaratorias/{id}/documento/` existe en `resoluciones/views.py`).

**Archivos a inspeccionar:**
- `backend/src/apps/peticiones/adapters/serializers.py` (líneas 81-102: `DocumentoEntregadoSerializer`)
- `backend/src/apps/resoluciones/adapters/serializers.py` (líneas 33-54: `DeclaratoriaAptitudSerializer`)
- `backend/src/apps/resoluciones/adapters/views.py` (endpoint download declaratoria)

**Cambios autorizables:**
1. `peticiones/adapters/serializers.py`: `DocumentoEntregadoSerializer`:
   - Remover `archivo_path` de `fields`.
   - Añadir `download_url = serializers.SerializerMethodField()`.
   - `get_download_url(self, obj): request = self.context.get("request"); return request.build_absolute_uri(f"/api/v1/peticiones/{obj.peticion_id}/documento/")`.
2. `resoluciones/adapters/serializers.py`: `DeclaratoriaAptitudSerializer`:
   - Remover `archivo_memorando_firmado_path` de `fields`.
   - Añadir `download_url = serializers.SerializerMethodField()`.
   - `get_download_url(self, obj): request = self.context.get("request"); return request.build_absolute_uri(f"/api/v1/declaratorias/{obj.id}/documento/")`.

**Cambios prohibidos:**
- Eliminar endpoints de descarga existentes (`descargar_documento` en peticiones, nuevo en declaratorias).
- Cambiar permisos de descarga (RBAC + ámbito vigentes).
- Exponer rutas en otros serializers.

**Procedimiento recomendado:**
1. Verificar endpoint download declaratoria existe y funciona (GET `/api/v1/declaratorias/{id}/documento/`).
2. Modificar `DocumentoEntregadoSerializer` → remover `archivo_path`, añadir `download_url`.
3. Modificar `DeclaratoriaAptitudSerializer` → remover `archivo_memorando_firmado_path`, añadir `download_url`.
3. Tests: responses no contienen paths; `download_url` presente y funcional.

**Pruebas obligatorias:**
1. `test_documento_serializer_excludes_archivo_path` — `archivo_path` not in response.data.
2. `test_documento_serializer_includes_download_url` — `download_url` presente, formato correcto.
3. `test_declaratoria_serializer_excludes_memorando_path` — idem.
4. `test_download_url_works_with_auth` — GET download_url + JWT → 200 PDF.

**Regresión obligatoria:**
- Tests serializers existentes passing (actualizar asserts).
- Descarga vía endpoint sigue funcionando.

**Compatibilidad frontend:**
- **IMPACTO MEDIO** — Ver `MATRIZ_COMPATIBILIDAD_BACKEND_FRONTEND_SEGURIDAD.md` SEC-T009.
- Frontend migra V-03, V-08 de `archivo_path` a `download_url`.
- Coordinación via issue frontend + `DOWNLOAD_URL_MIGRATION.md`.

**Criterios de aceptación:**
- Serializers actualizados.
- Tests pasando.
- Frontend notificado (issue vinculado).

**Evidencias de cierre:**
- `serializers.py` modificados (peticiones + resoluciones).
- Tests pasando.
- Issue frontend creado y vinculado.

**Rollback:**
- Revertir serializers a versión con `archivo_path`/`archivo_memorando_firmado_path`.
- Eliminar `download_url` fields.

**Dependencias:** SEC-T001, DEC-006 (endpoint download declaratoria).

**Condición de bloqueo:** Si endpoint download declaratoria no existe → no implementar. Esperar DEC-006.

---

## SEC-T010 — Handler Global Excepciones

**Objetivo:** Implementar `custom_exception_handler` en `core/adapters/exceptions.py` que estandarice respuestas: `{ "error": { "code", "message", "details" } }`. Mapear 400,401,403,404,409,429,500. Registrar en `REST_FRAMEWORK.EXCEPTION_HANDLER`.

**Contexto y evidencia:** CHECKLIST SEC-LOG-01 (PARCIAL), MATRIZ F1,F4,F5 (PARCIAL). Sin handler global; faltan 409,429,500 estandarizados.

**Autorización requerida:** Solo podrá implementarse cuando el responsable autorice expresamente **SEC-T010**.

**Precondiciones:**
- SEC-T001 CERRADA (production.py DEBUG=False para test 500 sin trace).
- DEC-009 aprobada (mensaje 500 usuario final).

**Archivos a inspeccionar:**
- `backend/src/config/settings/base.py` (REST_FRAMEWORK config)
- `backend/src/apps/peticiones/adapters/views.py` (líneas 36-61: custom APIExceptions)
- `backend/src/core/adapters/` (crear `exceptions.py`)

**Cambios autorizables:**
1. **`core/adapters/exceptions.py` (NUEVO)**:
   ```python
   from rest_framework.views import exception_handler as drf_exception_handler
   from rest_framework.exceptions import ValidationError, AuthenticationFailed, PermissionDenied, NotFound, Throttled
   from rest_framework import status
   import logging

   logger = logging.getLogger(__name__)

   def custom_exception_handler(exc, context):
       response = drf_exception_handler(exc, context)
       
       if response is not None:
           # Mapear códigos a formato uniforme
           code_map = {
               status.HTTP_400_BAD_REQUEST: "validation_error",
               status.HTTP_401_UNAUTHORIZED: "authentication_failed",
               status.HTTP_403_FORBIDDEN: "permission_denied",
               status.HTTP_404_NOT_FOUND: "not_found",
               status.HTTP_429_TOO_MANY_REQUESTS: "throttled",
           }
           code = code_map.get(response.status_code, "api_error")
           message_map = {
               "validation_error": "Datos de entrada inválidos",
               "authentication_failed": "Token de acceso expirado o inválido",
               "permission_denied": "No tienes permiso para realizar esta acción",
               "not_found": "Recurso no encontrado",
               "throttled": "Demasiadas solicitudes. Intenta de nuevo más tarde.",
           }
           message = message_map.get(code, "Error en la solicitud")
           
           details = response.data if isinstance(response.data, dict) else {"detail": str(response.data)}
           
           response.data = {
               "error": {
                   "code": code,
                   "message": message,
                   "details": details
               }
           }
       else:
           # 500 y otras excepciones no manejadas por DRF
           logger.exception("Error interno no manejado", exc_info=exc)
           response = Response({
               "error": {
                   "code": "server_error",
                   "message": "Error interno del servidor. El equipo técnico ha sido notificado.",  # DEC-009
                   "details": {}
               }
           }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       
       return response
   ```
2. `base.py` / `production.py`: `REST_FRAMEWORK.EXCEPTION_HANDLER = "core.adapters.exceptions.custom_exception_handler"`.
3. Custom exceptions existentes (`EstadoPeticionInvalidoAPI`, `UsuarioNoAutorizadoAPI`, `ValidacionPDF_API`) heredan de `APIException` → se mapean automáticamente por status_code.

**Cambios prohibidos:**
- Incluir stack trace, SQL, rutas internas en 500.
- Cambiar códigos HTTP existentes (400,401,403,404,429).
- Modificar lógica de custom exceptions existentes (solo formato respuesta).

**Procedimiento recomendado:**
1. Crear `core/adapters/exceptions.py` con `custom_exception_handler`.
2. Registrar en `REST_FRAMEWORK.EXCEPTION_HANDLER` en `base.py` y `production.py`.
3. Tests: provocar cada código HTTP → verificar formato uniforme.
4. Actualizar asserts en tests existentes si cambian formato errores.

**Pruebas obligatorias (nuevas en `core/adapters/tests/test_exceptions.py`):**
1. `test_500_no_stacktrace_leak` — provocar 500 (división by zero en vista) → response 500 sin `traceback`, `stack`, `file`, `line`.
2. `test_400_validation_error_format` — POST data inválida → 400 formato uniforme.
3. `test_401_authentication_failed_format` — token inválido → 401 formato uniforme.
4. `test_403_permission_denied_format` — sin permisos → 403 formato uniforme.
5. `test_404_not_found_format` — recurso inexistente → 404 formato uniforme.
6. `test_429_throttled_format` — throttling excedido → 429 formato uniforme.
7. `test_409_conflict_format` — si BE-11 implementado → formato uniforme.

**Regresión obligatoria:**
- Suite completa 473 tests passing (actualizar asserts si cambian formato errores).
- Endpoints críticos: login, expedientes, peticiones, checklist, resoluciones, notificaciones.

**Compatibilidad frontend:**
- **IMPACTO MEDIO** — Ver `MATRIZ_COMPATIBILIDAD_BACKEND_FRONTEND_SEGURIDAD.md` SEC-T010.
- Frontend actualiza error handling global: parsear `response.data.error.{code, message, details}`.
- Deploy coordinado backend+frontend. `API_ERROR_FORMAT.md` documentado.

**Criterios de aceptación:**
- Handler implementado.
- Tests pasando (existentes actualizados + nuevos).
- Formato documentado en `API_ERROR_FORMAT.md`.

**Evidencias de cierre:**
- `exceptions.py` creado, `base.py`/`production.py` actualizados.
- Tests nuevos + existentes passing.
- `API_ERROR_FORMAT.md` documentado.

**Rollback:**
- Eliminar `EXCEPTION_HANDLER` de `REST_FRAMEWORK`.
- Eliminar `core/adapters/exceptions.py`.
- Revertir asserts tests a formato anterior.

**Dependencias:** SEC-T001 (production.py DEBUG=False), DEC-009 (mensaje 500).

**Condición de bloqueo:** Si SEC-T001 no cerrada → no hay `production.py` con DEBUG=False → test 500 no válido. Esperar SEC-T001.

---

## SEC-T011 — Logging Estructurado

**Objetivo:** Configurar `LOGGING` dict completo en `base.py`/`production.py`: handlers `RotatingFileHandler` (10MB, 5 backups), formato JSON (`python-json-logger`), nivel INFO prod/DEBUG local, filtros PII (`password`, `token`, `authorization`, `credit_card`, `cedula`), loggers por módulo.

**Contexto y evidencia:** CHECKLIST SEC-LOG-02 (PENDIENTE/FALLIDO), MATRIZ F6,F7,F8 (PENDIENTE/FALLIDO). Sin config LOGGING; prints en código; sin rotación/filtros.

**Autorización requerida:** Solo podrá implementarse cuando el responsable autorice expresamente **SEC-T011**.

**Precondiciones:**
- SEC-T012 CERRADA (print() eliminados de código producción).
- SEC-T001 CERRADA (production.py existe).

**Archivos a inspeccionar:**
- `backend/src/config/settings/base.py` (sin LOGGING actual)
- `backend/src/config/settings/local.py`, `production.py` (sobrescriben nivel/handlers)
- `backend/src/apps/verificacion/services/evaluar_checklist.py` (líneas 164,170: prints - SEC-T012)
- `backend/requirements.txt` (añadir `python-json-logger`)

**Cambios autorizables:**
1. `requirements.txt`: `python-json-logger>=2.0,<3.0`
2. `base.py`: `LOGGING` dict completo:
   ```python
   LOGGING = {
       "version": 1,
       "disable_existing_loggers": False,
       "formatters": {
           "json": {
               "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
               "fmt": "%(timestamp)s %(level)s %(name)s %(message)s %(request_id)s %(user_id)s",
               "timestamp": True,
           },
       },
       "filters": {
           "sensitive_data": {
               "()": "core.adapters.logging_filters.SensitiveDataFilter",
           },
           "request_id": {
               "()": "core.adapters.logging_filters.RequestIdFilter",
           },
       },
       "handlers": {
           "console": {
               "class": "logging.StreamHandler",
               "formatter": "json",
               "filters": ["sensitive_data", "request_id"],
           },
           "apps_file": {
               "class": "logging.handlers.RotatingFileHandler",
               "filename": "/var/log/sgt-siaaf/apps.log",
               "maxBytes": 10485760,  # 10MB
               "backupCount": 5,
               "formatter": "json",
               "filters": ["sensitive_data", "request_id"],
           },
           "django_file": {
               "class": "logging.handlers.RotatingFileHandler",
               "filename": "/var/log/sgt-siaaf/django.log",
               "maxBytes": 10485760,
               "backupCount": 5,
               "formatter": "json",
               "filters": ["sensitive_data", "request_id"],
           },
           "security_file": {
               "class": "logging.handlers.RotatingFileHandler",
               "filename": "/var/log/sgt-siaaf/security.log",
               "maxBytes": 10485760,
               "backupCount": 5,
               "formatter": "json",
               "filters": ["sensitive_data", "request_id"],
           },
       },
       "loggers": {
           "apps": {"handlers": ["apps_file"], "level": "INFO", "propagate": False},
           "core": {"handlers": ["apps_file"], "level": "INFO", "propagate": False},
           "django": {"handlers": ["django_file"], "level": "WARNING", "propagate": False},
           "django.request": {"handlers": ["django_file"], "level": "WARNING", "propagate": False},
           "django.security": {"handlers": ["security_file"], "level": "INFO", "propagate": False},
       },
       "root": {"handlers": ["console"], "level": "WARNING"},
   }
   ```
3. `core/adapters/logging_filters.py` (NUEVO): `SensitiveDataFilter` (elimina `password`, `token`, `authorization`, `credit_card`, `cedula` de `record.__dict__` y `record.msg`), `RequestIdFilter` (inyecta `request_id` desde thread-local si disponible).
4. `production.py`: Sobrescribe `LOGGING` → nivel INFO, handlers archivo (rutas `/var/log/sgt-siaaf/`).
5. `local.py`: Sobrescribe → nivel DEBUG, handler consola.
6. `settings/__init__.py` o `wsgi.py`: `logging.config.dictConfig(LOGGING)` al inicio.

**Cambios prohibidos:**
- Logs sin filtros PII (passwords, tokens, cedulas en logs).
- Sin rotación (archivos crecen indefinido).
- Formato no JSON (difícil parsing SIEM).
- `print()` en código producción (SEC-T012 previo).

**Procedimiento recomendado:**
1. Añadir `python-json-logger` a `requirements.txt`.
2. Crear `core/adapters/logging_filters.py` con filtros.
3. Añadir `LOGGING` dict en `base.py` con configuración base.
4. Sobrescribir en `production.py` (nivel INFO, handlers archivo) y `local.py` (DEBUG, consola).
7. Ejecutar `logging.config.dictConfig(LOGGING)` en `settings/__init__.py`.
7. Deploy staging → generar logs → verificar JSON, rotación, sin secretos.

**Pruebas obligatorias:**
1. `test_logging_structured_json_format` — log generado → parseable JSON con campos esperados.
2. `test_logging_no_secrets_in_output` — log con `password="secret"` → JSON no contiene "secret".
3. `test_logging_rotation_max_bytes` — escribir >10MB → archivo rotado, backup creado.
4. `test_logging_no_print_in_production_code` — `grep "print(" src/ --include="*.py" | grep -v test | grep -v manage` → 0 resultados.

**Regresión obligatoria:**
- Deploy staging → generar logs → verificar JSON, rotación, sin secretos.
- Tests existentes no rotos por logging.

**Compatibilidad frontend:**
- **NINGUNO** — Interno de logging. Ver `MATRIZ_COMPATIBILIDAD_BACKEND_FRONTEND_SEGURIDAD.md` SEC-T011.

**Criterios de aceptación:**
- LOGGING dict en settings.
- Filtros funcionando.
- Rotación verificada.
- `print()` eliminado de código producción (SEC-T012).

**Evidencias de cierre:**
- `LOGGING` dict en `base.py`/`production.py`/`local.py`.
- `logging_filters.py` creado.
- `python-json-logger` en requirements.
- Tests pasando.

**Rollback:**
- Eliminar `LOGGING` dict de settings.
- Eliminar `logging_filters.py`.
- Eliminar `python-json-logger` de requirements.
- Revertir a logging default Django.

**Dependencias:** SEC-T012 (print cleanup), SEC-T001 (production.py).

**Condición de bloqueo:** Si SEC-T012 no cerrada → prints en stdout contaminan logs. Esperar SEC-T012.

---

## SEC-T012 — Eliminar print() en evaluar_checklist.py

**Objetivo:** Reemplazar `print(f"DEBUG: ...")` en `src/apps/verificacion/services/evaluar_checklist.py:164,170` con `logger.debug(...)` usando logger del módulo.

**Contexto y evidencia:** CHECKLIST SEC-LOG-02 (FALLIDO), MATRIZ F7 (FALLIDO), INFORME_PRUEBAS §5.2. Prints exponen username, roles, facultad_id en stdout contenedor.

**Autorización requerida:** Solo podrá implementarse cuando el responsable autorice expresamente **SEC-T012**.

**Precondiciones:** Ninguna (independiente, Fase 0).

**Archivos a inspeccionar:**
- `backend/src/apps/verificacion/services/evaluar_checklist.py` (líneas 164, 170)

**Cambios autorizables:**
1. Al inicio del módulo: `import logging; logger = logging.getLogger(__name__)`.
2. Línea 164: `logger.debug(f"user={usuario.username}, roles={list(usuario.get_roles())}, has_secretario={usuario.has_role('SECRETARIO_ABOGADO')}, has_analista={usuario.has_role('ANALISTA_APOYO')}")`
3. Línea 170: `logger.debug(f"user_facultad={user_facultad}, expediente_facultad={expediente_facultad}, match={user_facultad == expediente_facultad}")`

**Cambios prohibidos:**
- Eliminar logs de debug (cambiar a `logger.debug`).
- Añadir `print()` en otros archivos `src/`.
- Cambiar lógica de validación facultad/roles.

**Procedimiento recomendado:**
1. Añadir `logger = logging.getLogger(__name__)` al inicio.
2. Reemplazar los dos `print()` por `logger.debug()` con mismos mensajes.
3. Verificar sin `print(` en `src/apps/verificacion/services/`.

**Pruebas obligatorias:**
1. `test_no_print_in_verificacion_services` — `grep "print(" src/apps/verificacion/services/ --include="*.py"` → 0 resultados.
2. Ejecutar `test_evaluar_checklist.py` → logs DEBUG aparecen en pytest output (caplog), no en stdout.

**Regresión obligatoria:**
- Tests verificacion existentes passing.

**Compatibilidad frontend:**
- **NINGUNO**. Ver `MATRIZ_COMPATIBILIDAD_BACKEND_FRONTEND_SEGURIDAD.md` SEC-T012.

**Criterios de aceptación:**
- Código limpio (sin prints).
- Tests pasando.
- `grep -r "print(" src/ --include="*.py" | grep -v test | grep -v manage` → vacío.

**Evidencias de cierre:**
- `evaluar_checklist.py` modificado.
- Tests pasando.
- Verificación grep limpio.

**Rollback:**
- Revertir `logger.debug` a `print` (solo si absolutamente necesario debug temporal).

**Dependencias:** Ninguna (independiente, Fase 0). Desbloquea SEC-T011.

**Condición de bloqueo:** Ninguna. Puede iniciar inmediatamente.

---

## SEC-T013 — Protección Swagger/ReDoc/Schema

**Objetivo:** Cambiar `SPECTACULAR_SETTINGS.SERVE_PERMISSIONS` a `["rest_framework.permissions.IsAdminUser"]` en `production.py`. Mantener `AllowAny` en `local.py`/`test.py`.

**Contexto y evidencia:** CHECKLIST §8 (FALLIDO), MATRIZ H1-H4 (FALLIDO). Schema público expone superficie ataque.

**Autorización requerida:** Solo podrá implementarse cuando el responsable autorice expresamente **SEC-T013**.

**Precondiciones:**
- SEC-T001 CERRADA (production.py existe).

**Archivos a inspeccionar:**
- `backend/src/config/settings/base.py` (línea 120: `SERVE_PERMISSIONS = ["rest_framework.permissions.AllowAny"]`)
- `backend/src/config/settings/local.py`, `production.py`

**Cambios autorizables:**
1. `production.py`: `SPECTACULAR_SETTINGS["SERVE_PERMISSIONS"] = ["rest_framework.permissions.IsAdminUser"]`.
2. `local.py` / `test.py`: `SPECTACULAR_SETTINGS["SERVE_PERMISSIONS"] = ["rest_framework.permissions.AllowAny"]` (explícito o heredado).

**Cambios prohibidos:**
- Cambiar `SERVE_AUTHENTICATION` (actual `[]` OK).
- Requerir auth para schema en desarrollo/test (rompe DX).

**Procedimiento recomendado:**
1. Añadir override en `production.py`.
2. Tests: con `settings.production` → 403 anónimo; con `settings.local` → 200.

**Pruebas obligatorias (nuevas en `authentication/tests/test_swagger_protection.py`):**
1. `test_swagger_anonymous_denied_in_production_settings` — con `settings.production` → 403.
2. `test_swagger_admin_allowed_in_production_settings` — usuario staff → 200.
3. `test_schema_anonymous_denied_in_production_settings` — 403.
4. `test_swagger_allowany_in_local_settings` — con `settings.local` → 200.

**Regresión obligatoria:**
- Tests existentes de espectacular (si los hay) passing.
- Verificar en staging: anónimo → 403, admin → 200.

**Compatibilidad frontend:**
- **IMPACTO BAJO** — Frontend no usa Swagger/ReDoc. Ver `MATRIZ_COMPATIBILIDAD_BACKEND_FRONTEND_SEGURIDAD.md` SEC-T013.

**Criterios de aceptación:**
- Configuración por entorno.
- Tests pasando.
- Documentado en `SECURITY_CONFIG.md`.

**Evidencias de cierre:**
- `production.py` y `local.py`/`test.py` actualizados.
- Tests pasando.

**Rollback:**
- Revertir `SERVE_PERMISSIONS` a `AllowAny` en `production.py`.

**Dependencias:** SEC-T001 (production.py). Desbloquea SEC-T017 (tests).

**Condición de bloqueo:** Si SEC-T001 no cerrada → no hay `production.py`. Esperar SEC-T001.

---

## SEC-T014 — CI/CD Security (Safety + Bandit + Gitleaks)

**Objetivo:** Integrar en pipeline CI: `safety check` (vulns deps), `bandit -r src/` (SAST), `gitleaks detect` (secretos Git). Jobs obligatorios en PR/merge.

**Contexto y evidencia:** CHECKLIST §9 (PENDIENTE), MATRIZ I1-I3 (PENDIENTE). Sin escaneo automatizado vulnerabilidades.

**Autorización requerida:** Solo podrá implementarse cuando el responsable autorice expresamente **SEC-T014**.

**Precondiciones:**
- SEC-T001 CERRADA (Dockerfile para CI env consistente).

**Archivos a inspeccionar:**
- `backend/.github/workflows/` (crear `security.yml`)
- `backend/.bandit` (config existente)
- `backend/.gitleaksignore` (config existente)
- `backend/requirements.txt`, `requirements-dev.txt`

**Cambios autorizables:**
1. **`.github/workflows/security.yml` (NUEVO)**:
   ```yaml
   name: Security Checks
   on: [pull_request, push]
   jobs:
     safety:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: actions/setup-python@v5
           with: { python-version: "3.12" }
         - run: pip install safety
         - run: safety check -r requirements.txt -r requirements-dev.txt --json
     bandit:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: actions/setup-python@v5
           with: { python-version: "3.12" }
         - run: pip install bandit
         - run: bandit -r src/ -x tests,migrations -f json -o bandit-report.json || true
         - run: |
             if grep -q '"severity": "HIGH"\|"severity": "MEDIUM"' bandit-report.json; then
               echo "Bandit found HIGH/MEDIUM issues"
               cat bandit-report.json
               exit 1
             fi
     gitleaks:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
           with: { fetch-depth: 0 }
         - uses: gitleaks/gitleaks-action@v2
           with: { config: .gitleaksignore }
   ```
2. Verificar `.bandit` y `.gitleaksignore` configs existentes son correctas.

**Cambios prohibidos:**
- Deshabilitar jobs en main branch.
- Ignorar hallazgos HIGH/CRITICAL sin documentar justificación.

**Procedimiento recomendado:**
1. Crear workflow `security.yml`.
2. Ejecutar localmente: `safety check`, `bandit -r src/`, `gitleaks detect --source=.` → 0 hallazgos severos.
3. PR de prueba → pipeline pasa.
4. Merge a main → jobs obligatorios.

**Pruebas obligatorias:**
1. `safety check` local → 0 vulnerabilidades HIGH/CRITICAL (o documentadas aceptadas).
2. `bandit -r src/` local → 0 HIGH/MEDIUM (o falsos positivos documentados).
3. `gitleaks detect --source=.` local → 0 hallazgos (o falsos positivos).
4. Pipeline CI pasa en PR de prueba.

**Regresión obligatoria:**
- Ejecutar herramientas manualmente antes de cada release.

**Compatibilidad frontend:**
- **NINGUNO** — Pipeline interno. Ver `MATRIZ_COMPATIBILIDAD_BACKEND_FRONTEND_SEGURIDAD.md` SEC-T014.

**Criterios de aceptación:**
- Pipeline configurado.
- Pasando en main.
- Documentado en `CI_SECURITY.md`.

**Evidencias de cierre:**
- `security.yml` creado.
- Pipeline passing en main.
- `CI_SECURITY.md` documentado.

**Rollback:**
- Eliminar `security.yml` de workflows.
- Deshabilitar jobs en CI.

**Dependencias:** SEC-T001 (Dockerfile para CI env). Desbloquea SEC-T015.

**Condición de bloqueo:** Si SEC-T001 no cerrada → CI env inconsistente. Esperar SEC-T001.

---

## SEC-T015 — Dependabot Configurado

**Objetivo:** Crear `.github/dependabot.yml` con schedule semanal, auto-merge para patch versions, reviewers, labels.

**Contexto y evidencia:** CHECKLIST §9 (PENDIENTE), MATRIZ I4 (PENDIENTE). Sin actualizaciones automáticas deps.

**Autorización requerida:** Solo podrá implementarse cuando el responsable autorice expresamente **SEC-T015**.

**Precondiciones:**
- SEC-T014 CERRADA (CI tests para auto-merge).

**Archivos a inspeccionar:**
- `backend/.github/` (crear `dependabot.yml`)

**Cambios autorizables:**
1. **`.github/dependabot.yml` (NUEVO)**:
   ```yaml
   version: 2
   updates:
     - package-ecosystem: "pip"
       directory: "/"
       schedule:
         interval: "weekly"
         day: "monday"
         time: "09:00"
       open-pull-requests-limit: 10
       allow:
         - dependency-type: "direct"
       automerge: true
       labels: ["dependencies", "security"]
       reviewers: ["tech-lead"]
       assignees: ["tech-lead"]
   ```

**Cambios prohibidos:**
- Auto-merge para minor/major versions (solo patch).
- Sin reviewers (requiere revisión humana para cambios mayores).

**Procedimiento recomendado:**
1. Crear `dependabot.yml`.
2. Merge a main → Dependabot activa.
3. Verificar PR generado para dependencia desactualizada (simular).

**Pruebas obligatorias:**
1. Merge `.github/dependabot.yml` → Dependabot activo en repo.
2. Verificar PR generado para dependencia desactualizada (simular).

**Regresión obligatoria:**
- Verificar PRs Dependabot no rompen tests (CI pasa).

**Compatibilidad frontend:**
- **NINGUNO**. Ver `MATRIZ_COMPATIBILIDAD_BACKEND_FRONTEND_SEGURIDAD.md` SEC-T015.

**Criterios de aceptación:**
- Configuración mergeada.
- Dependabot activo.
- Primer PR automático procesado.

**Evidencias de cierre:**
- `dependabot.yml` creado.
- Dependabot activo en repo.
- Primer PR procesado.

**Rollback:**
- Eliminar `dependabot.yml`.
- Deshabilitar Dependabot en repo settings.

**Dependencias:** SEC-T014 (CI tests).

**Condición de bloqueo:** Si SEC-T014 no cerrada → auto-merge sin tests. Esperar SEC-T014.

---

## SEC-T016 — Cobertura Tests + testpaths

**Objetivo:** Cambiar `testpaths = ["src"]` en `pyproject.toml` para incluir `src/core/tests` explícitamente. Añadir `--cov=src --cov-fail-under=80 --cov-report=term-missing` (valor DEC-004).

**Contexto y evidencia:** CHECKLIST §11 (PARCIAL), MATRIZ J2,J3 (PARCIAL/PENDIENTE). `testpaths = ["src/apps"]` excluye core/tests; sin umbral cobertura.

**Autorización requerida:** Solo podrá implementarse cuando el responsable autorice expresamente **SEC-T016**.

**Precondiciones:**
- DEC-004 aprobada (umbral 80% u otro).

**Archivos a inspeccionar:**
- `backend/pyproject.toml` (líneas 17-21: pytest config)

**Cambios autorizables:**
1. `pyproject.toml`:
   ```toml
   [tool.pytest.ini_options]
   DJANGO_SETTINGS_MODULE = "config.settings.test"
   pythonpath = ["src"]
   testpaths = ["src"]  # Incluye src/apps, src/core, src/config
   addopts = "--cov=src --cov-fail-under=80 --cov-report=term-missing"  # Valor DEC-004

   [tool.coverage.run]
   omit = [
     "*/migrations/*",
     "*/settings/*",
     "*/adapters/apps.py",
     "*/__init__.py",
     "manage.py",
   ]
   ```

**Cambios prohibicidos:**
- Eliminar `omit` patterns (migrations, settings, apps.py, __init__.py, manage.py).
- Bajar umbral `< 80%` sin justificación aprobada.
- Excluir `src/core/tests` del coverage.

**Procedimiento recomendado:**
1. Modificar `pyproject.toml` con nuevos valores.
2. Ejecutar `pytest` local → coverage report ≥80% overall.
3. Verificar `pytest --collect-only` incluye `src/core/adapters/tests/`.

**Pruebas obligatorias:**
1. `pytest` → coverage report ≥80% overall.
2. `pytest --collect-only` → incluye `src/core/adapters/tests/`.
3. Módulos críticos (`authentication`, `peticiones`, `verificacion`, `core.adapters`) ≥90%.

**Regresión obligatoria:**
- Ejecutar `pytest` local y CI → coverage pasa.

**Compatibilidad frontend:**
- **NINGUNO**. Ver `MATRIZ_COMPATIBILIDAD_BACKEND_FRONTEND_SEGURIDAD.md` SEC-T016.

**Criterios de aceptación:**
- Configuración actualizada.
- Coverage ≥80% en CI.
- Documentado en `TESTING.md`.

**Evidencias de cierre:**
- `pyproject.toml` actualizado.
- Coverage ≥80% en CI.
- `TESTING.md` documentado.

**Rollback:**
- Revertir `testpaths` a `["src/apps"]`.
- Eliminar `addopts` coverage.

**Dependencias:** Ninguna (independiente, Fase 0).

**Condición de bloqueo:** Si DEC-004 no aprobada → esperar decisión.

---

## SEC-T017 — Tests Seguridad Faltantes

**Objetivo:** Crear tests para controles implementados en SEC-T002, SEC-T003, SEC-T005, SEC-T013: throttling login/carga, rotación/blacklist/logout JWT, IP auditoría con proxy real, protección Swagger prod.

**Contexto y evidencia:** INFORME_PRUEBAS §3 (Gaps), CHECKLIST controles correspondientes. Controles sin validación automática → regresión silenciosa.

**Autorización requerida:** Solo podrá implementarse cuando el responsable autorice expresamente **SEC-T017**.

**Precondiciones:**
- SEC-T002 CERRADA (throttling login).
- SEC-T003 CERRADA (rotación/blacklist).
- SEC-T005 CERRADA (IP auditoría).
- SEC-T013 CERRADA (Swagger protection).

**Archivos a inspeccionar:**
- `backend/src/apps/authentication/tests/` (crear `test_security_controls.py`, `test_swagger_protection.py`)
- `backend/src/apps/notificaciones/tests/` (crear `test_audit_ip.py`)
- `backend/src/apps/peticiones/tests/` (crear `test_upload_throttle.py`)
- `backend/src/core/adapters/tests/` (crear `test_exceptions.py`)

**Cambios autorizables:**
1. `authentication/tests/test_security_controls.py` (NUEVO): Tests throttling login, rotación/blacklist/logout, lifetime 30min, JWT key separada.
2. `notificaciones/tests/test_audit_ip.py` (NUEVO): Tests IP auditoría con proxy trusted, spoofing bloqueado, IP persistida.
3. `authentication/tests/test_swagger_protection.py` (NUEVO): Tests Swagger/schema 403 anónimo prod, 200 admin.
4. `peticiones/tests/test_upload_throttle.py` (NUEVO): Tests throttling carga docs.
5. `core/adapters/tests/test_exceptions.py` (NUEVO): Tests handler global excepciones (500, 400, 401, 403, 404, 429 formato uniforme).

**Cambios prohibidos:**
- Modificar tests existentes (salvo asserts por formato errores SEC-T010).
- Tests que no validan controles de seguridad implementados.
- Tests duplicados de funcionalidad ya testeada.

**Procedimiento recomendado:**
1. Crear archivos de test nuevos en módulos correspondientes.
2. Implementar tests según especificaciones en fichas SEC-T002, T003, T005, T010, T013, T008.
3. Ejecutar suite completa → 473+ tests passing.

**Pruebas obligatorias:**
- Los tests mismos son la verificación.
- Suite completa 473+ tests passing en CI.

**Regresión obligatoria:**
- Suite completa passing.
- No tests rotos por cambios en controles.

**Compatibilidad frontend:**
- **NINGUNO**. Ver `MATRIZ_COMPATIBILIDAD_BACKEND_FRONTEND_SEGURIDAD.md` SEC-T017.

**Criterios de aceptación:**
- Tests creados, pasando, integrados en `pytest` collection.

**Evidencias de cierre:**
- 4 archivos de test nuevos creados.
- Tests pasando en CI.

**Rollback:**
- Eliminar archivos de test creados.
- (No revertir controles implementados).

**Dependencias:** SEC-T002, SEC-T003, SEC-T005, SEC-T013 (controles deben existir).

**Condición de bloqueo:** Si alguna dependencia no cerrada → tests fallan o validan nada. Esperar dependencias.

---

## SEC-T018 — Procedimiento Rotación Secretos

**Objetivo:** Documentar en `SECURITY_CONFIG.md`: procedimiento rotación `SECRET_KEY` y `JWT_SIGNING_KEY` (generación, deploy, ventana solape, revocación antigua, verificación).

**Contexto y evidencia:** CHECKLIST SEC-SEC-01 (PENDIENTE), MATRIZ D5 (PENDIENTE). Sin procedimiento documentado.

**Autorización requerida:** Solo podrá implementarse cuando el responsable autorice expresamente **SEC-T018**.

**Precondiciones:**
- SEC-T004 CERRADA (JWT_SIGNING_KEY separada).

**Archivos a inspeccionar:**
- `backend/docs/` (crear `SECURITY_CONFIG.md` o actualizar existente)

**Cambios autorizables:**
1. `SECURITY_CONFIG.md` (NUEVO o sección):
   - Procedimiento rotación `SECRET_KEY`:
     1. Generar nueva: `openssl rand -base64 32`
     2. Añadir a `.env.prod` como `SECRET_KEY_NEW` (mantener `SECRET_KEY` actual)
     3. Deploy rolling: nuevos pods leen `SECRET_KEY_NEW`; viejos aún usan `SECRET_KEY` (ventana solape 10 min)
     4. Verificar: login funciona, sesiones admin OK, cookies firmadas válidas
     5. Renombrar `SECRET_KEY_NEW` → `SECRET_KEY`; eliminar antigua
     6. Verificar post-rotación
   - Procedimiento rotación `JWT_SIGNING_KEY`:
     1. Generar nueva: `openssl rand -base64 32`
     2. Deploy con nueva clave → tokens existentes invalidados (re-login users)
     3. Comunicar a usuarios: "Por seguridad, vuelva a iniciar sesión"
     4. Verificar: login funciona, tokens nuevos válidos
   - Checklist verificación post-rotación.
   - Responsable, frecuencia (anual o tras incidente).

**Cambios prohibidos:**
- Rotar claves sin procedimiento documentado y aprobado.
- Rotar `SECRET_KEY` y `JWT_SIGNING_KEY` simultáneamente sin ventana solape.

**Procedimiento recomendado:**
1. Redactar documento con pasos claros, comandos, checklist.
2. Simulación en staging (rotar claves → login funciona → sesiones admin OK).
3. Documentar en `SECURITY_CONFIG.md`.
4. Notificar al equipo.

**Pruebas obligatorias:**
- Simulación en staging (rotar claves → login funciona → sesiones admin OK).

**Regresión obligatoria:**
- Verificar documento actualizado tras cada rotación real.

**Compatibilidad frontend:**
- **NINGUNO**. Ver `MATRIZ_COMPATIBILIDAD_BACKEND_FRONTEND_SEGURIDAD.md` SEC-T018.

**Criterios de aceptación:**
- Documento mergeado en repo.
- Equipo notificado.

**Evidencias de cierre:**
- `SECURITY_CONFIG.md` creado/actualizado.
- Simulación staging exitosa.

**Rollback:**
- (Documentación — no requiere rollback técnico).

**Dependencias:** SEC-T004 (JWT_SIGNING_KEY separada).

**Condición de bloqueo:** Si SEC-T004 no cerrada → procedimiento incompleto. Esperar SEC-T004.

---

## SEC-T019 — Limpieza Archivos Huérfanos

**Objetivo:** Crear management command `limpiar_archivos_huerfanos`: detecta archivos sin registro DB + registros `es_vigente=False` > 90 días (DEC-005), elimina/mueve a quarantine, log JSON, cron diario 03:00.

**Contexto y evidencia:** CHECKLIST §5 (PARCIAL), MATRIZ E6 (PARCIAL). Sin job limpieza; versiones no vigentes permanecen en disco.

**Autorización requerida:** Solo podrá implementarse cuando el responsable autorice expresamente **SEC-T019**.

**Precondiciones:**
- SEC-T001 CERRADA (Dockerfile para cron).
- DEC-005 aprobada (política retención 90 días).

**Archivos a inspeccionar:**
- `backend/src/apps/peticiones/management/commands/` (crear `limpiar_archivos_huerfanos.py`)
- `backend/src/apps/peticiones/models.py` (`DocumentoEntregado`)
- `backend/src/core/adapters/local_storage.py` (`archivo_existe`, `eliminar_archivo`)

**Cambios autorizables:**
1. `peticiones/management/commands/limpiar_archivos_huerfanos.py` (NUEVO):
   ```python
   from django.core.management.base import BaseCommand
   from apps.peticiones.models import DocumentoEntregado
   from core.adapters.local_storage import archivo_existe, eliminar_archivo
   from datetime import timedelta
   from django.utils import timezone
   import json

   class Command(BaseCommand):
       help = "Limpia archivos huérfanos en almacenamiento privado"

       def add_arguments(self, parser):
           parser.add_argument("--dry-run", action="store_true", help="Solo listar, no eliminar")
           parser.add_argument("--retention-days", type=int, default=90, help="Días retención versiones no vigentes")

       def handle(self, *args, **options):
           dry_run = options["dry_run"]
           retention_days = options["retention_days"]
           cutoff = timezone.now() - timedelta(days=retention_days)
           
           # 1. Archivos en disco sin registro DB
           # (requiere escanear MEDIA_ROOT/private - implementar según estructura)
           
           # 2. Registros es_vigente=False mayores a retention_days
           huérfanos = DocumentoEntregado.objects.filter(es_vigente=False, fecha_actualizacion__lt=cutoff)
           
           resultados = {"eliminados": [], "errores": [], "bytes_liberados": 0}
           
           for doc in huérfanos:
               if archivo_existe(doc.archivo_path):
                   if not dry_run:
                       try:
                           bytes_lib = doc.tamanio_bytes
                           eliminar_archivo(doc.archivo_path)
                           resultados["eliminados"].append(str(doc.id))
                           resultados["bytes_liberados"] += bytes_lib
                       except Exception as e:
                           resultados["errores"].append({"id": str(doc.id), "error": str(e)})
                   else:
                       resultados["eliminados"].append(str(doc.id))
           
           self.stdout.write(json.dumps(resultados, indent=2))
   ```
2. Cron en `Dockerfile`/`entrypoint.sh`: `0 3 * * * python manage.py limpiar_archivos_huerfanos >> /var/log/sgt-siaaf/cleanup.log 2>&1`

**Cambios prohibidos:**
- Eliminar archivos vigentes (`es_vigente=True`).
- Eliminar registros DB (solo archivos físicos).
- Ejecutar sin `--dry-run` en producción sin verificación previa.

**Procedimiento recomendado:**
1. Crear management command con lógica above.
2. Tests: crear archivo huérfano manual → command lo detecta; `--dry-run` no elimina; sin flag elimina.
3. Añadir cron en Dockerfile/entrypoint.
4. Deploy staging → verificar ejecución diaria y logs.

**Pruebas obligatorias:**
1. Crear archivo huérfano manual → command lo detecta.
2. Crear DocumentoEntregado sin archivo físico → command lo detecta (opcional).
3. `--dry-run` no elimina; sin flag elimina.

**Regresión obligatoria:**
- Verificar command no elimina archivos vigentes.

**Compatibilidad frontend:**
- **NINGUNO**. Ver `MATRIZ_COMPATIBILIDAD_BACKEND_FRONTEND_SEGURIDAD.md` SEC-T019.

**Criterios de aceptación:**
- Command implementado, testeado.
- Documentado en `OPERATIONS.md`.

**Evidencias de cierre:**
- Command implementado en `peticiones/management/commands/`.
- Tests pasando.
- `OPERATIONS.md` documentado.

**Rollback:**
- Eliminar management command.
- Eliminar cron de Dockerfile/entrypoint.

**Dependencias:** SEC-T001 (Dockerfile cron), DEC-005 (retención 90 días).

**Condición de bloqueo:** Si SEC-T001 o DEC-005 no listas → esperar.

---

## SEC-T020 — Verificación PermissionError Docker

**Objetivo:** Reproducir y documentar errores históricos `PermissionError` en almacenamiento privado: montar volumen `media_private` con UID/GID correctos, ejecutar carga/descarga concurrente, verificar permisos rw para `appuser` (UID 1000).

**Contexto y evidencia:** CHECKLIST §5 (NO VERIFICABLE), MATRIZ E7 (NO VERIFICABLE). Requiere entorno Docker real.

**Autorización requerida:** Solo podrá implementarse cuando el responsable autorice expresamente **SEC-T020**.

**Precondiciones:**
- SEC-T001 CERRADA (Dockerfile + docker-compose.prod.yml).

**Archivos a inspeccionar:**
- `backend/docker-compose.prod.yml` (volumen `media_private`)
- `backend/Dockerfile` (usuario `appuser` UID 1000)
- `backend/src/core/adapters/local_storage.py` (operaciones archivo)

**Cambios autorizables:**
1. Verificar en `docker-compose.prod.yml`: volumen `media_private` montado con permisos correctos.
2. En `Dockerfile`: `USER appuser` (UID 1000) y `RUN chown -R appuser:appuser /app/media/private` en entrypoint si necesario.
3. Script test concurrente: 10 hilos carga/descarga simultánea → 0 PermissionError.
3. Documentar `UID/GID` requeridos, `chown` en entrypoint.

**Cambios prohibidos:**
- Cambiar usuario contenedor a root.
- Modificar permisos volumen a 777.
- Ejecutar tests en producción.

**Procedimiento recomendado:**
1. Levantar staging con `docker-compose.prod.yml`.
2. Ejecutar script test concurrente (10 hilos, 50 ops cada uno).
3. Verificar 0 PermissionError en logs.
4. Documentar configuración correcta en `DEPLOY_PRODUCTION.md`.

**Pruebas obligatorias:**
- Test de carga concurrente en staging (script separado) → 0 PermissionError.

**Regresión obligatoria:**
- Verificar en cada deploy staging.

**Compatibilidad frontend:**
- **NINGUNO**. Ver `MATRIZ_COMPATIBILIDAD_BACKEND_FRONTEND_SEGURIDAD.md` SEC-T020.

**Criterios de aceptación:**
- Documentado en `DEPLOY_PRODUCTION.md`.
- Verificado en staging.

**Evidencias de cierre:**
- `DEPLOY_PRODUCTION.md` actualizado con configuración permisos.
- Logs test concurrente sin PermissionError.

**Rollback:**
- (Documentación/validación — no requiere rollback técnico).

**Dependencias:** SEC-T001 (Dockerfile + docker-compose).

**Condición de bloqueo:** Si SEC-T001 no cerrada → no hay entorno Docker real. Esperar SEC-T001.

---

## SEC-T021 — Evidencias ACD 4 Reales

**Objetivo:** Sustituir identificadores placeholder (`a1b2c3d`, `e4f5g6h`, `i7j8k9l`, `m0n1o2p`, `q3r4s5t`) por evidencia real: SHA commits, URLs PRs, autores, archivos modificados, tests aportados. Verificar en plataforma Git.

**Contexto y evidencia:** CHECKLIST §12 (NO VERIFICADO), MATRIZ K1-K5 (NO VERIFICADO). Identificadores parecen placeholders.

**Autorización requerida:** Solo podrá implementarse cuando el responsable autorice expresamente **SEC-T021**.

**Precondiciones:**
- DEC-007 resuelta (placeholders vs datos reales).

**Archivos a inspeccionar:**
- `backend/docs/auditoria-backend/seguridad/MATRIZ_TRAZABILIDAD_SEGURIDAD.md` (sección 11)
- Plataforma Git (GitHub/GitLab) para verificar commits/PRs.

**Cambios autorizables:**
1. **Si placeholders →** Marcar tarea "NO APLICA" / "CANCELADA". Actualizar matriz trazabilidad.
2. **Si datos reales →** Actualizar `MATRIZ_TRAZABILIDAD_SEGURIDAD.md` sección 11 con:
   - SHA commits reales (ej: `a1b2c3d4e5f6...`)
   - URLs PRs reales (ej: `github.com/org/repo/pull/42`)
   - Autores (nombre/email Git)
   - Archivos modificados por commit
   - Tests aportados (nombres tests)

**Cambios prohibidos:**
- Inventar commits, PRs, autores, evidencias.
- Modificar historial Git.

**Procedimiento recomendado:**
1. Consultar con Coordinador Académico / Responsable Proyecto: ¿son placeholders o datos reales?
2. Si placeholders → cancelar tarea, actualizar matriz.
3. Si reales → buscar en Git platform, actualizar matriz con evidencia verificable.

**Pruebas obligatorias:**
- Verificación manual en plataforma Git (GitHub/GitLab).

**Regresión obligatoria:**
- N/A.

**Compatibilidad frontend:**
- **NINGUNO**. Ver `MATRIZ_COMPATIBILIDAD_BACKEND_FRONTEND_SEGURIDAD.md` SEC-T021.

**Criterios de aceptación:**
- Matriz actualizada con evidencias reales O tarea marcada NO APLICA.

**Evidencias de cierre:**
- `MATRIZ_TRAZABILIDAD_SEGURIDAD.md` sección 11 actualizada.

**Rollback:**
- (Actualización documentación — no requiere rollback técnico).

**Dependencias:** DEC-007 (resolución placeholders).

**Condición de bloqueo:** Si DEC-007 no resuelta → esperar clarificación.

---

## Protocolo Obligatorio para Futuras Implementaciones (Recordatorio)

Al recibir una tarea autorizada, Claude debe:

1. Confirmar identificador y alcance autorizado.
2. Inspeccionar estado actual repositorio y cambios locales.
3. Leer ficha técnica de la tarea.
4. Verificar dependencias (tareas previas CERRADAS).
5. Establecer línea base de pruebas (`pytest` passing actual).
6. Proponer plan de modificación antes de editar.
7. Implementar **únicamente** la tarea autorizada.
8. Evitar refactorizaciones no relacionadas.
9. Ejecutar pruebas obligatorias de la ficha.
10. Ejecutar regresión módulos afectados (suite completa 473 tests).
11. Verificar compatibilidad backend-frontend (ver matriz).
12. Revisar cambios y efectos secundarios.
13. Documentar evidencias (archivos, comandos, resultados tests).
14. Actualizar estado tarea **solo si** criterios de aceptación cumplidos.
15. Detenerse antes de siguiente tarea y esperar autorización.

**Prohibido durante implementación:**
- `git reset --hard`, `git clean`, eliminar volúmenes, borrar BD.
- Modificar archivos ajenos a la tarea.
- Instalar/actualizar dependencias sin autorización.
- Cambiar reglas de negocio, permisos, contratos API aprobados.
- Crear commits o subir a Git sin autorización expresa.

---

**Firma:** opencode AI Assistant  
**Fecha:** 2026-11-05  
**Estado:** Planificación completa — Esperando autorizaciones para iniciar Fase 0 (SEC-T004, SEC-T008, SEC-T012, SEC-T016, SEC-T021).