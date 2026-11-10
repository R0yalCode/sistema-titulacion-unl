# INFORME DE HARDENING Y SEGURIDAD — SGT-SIAAF Backend

**Fecha:** 2026-11-05  
**Versión:** 1.0  
**Clasificación:** Interno - Equipo de Desarrollo UNL

---

## Resumen Ejecutivo

Esta auditoría evalúa la postura de seguridad del backend SGT-SIAAF (Django REST Framework) frente a los requisitos del ACD 4, la Constitución del proyecto (specs/001), la especificación frontend (specs/003) y las mejores prácticas OWASP/STRIDE.

**Conclusión principal:** El backend tiene una **base funcional sólida** (RBAC completo, JWT, almacenamiento privado, validación PDF, 473 tests passing) pero **no está listo para producción** debido a brechas críticas en hardening de infraestructura, gestión de secretos JWT, throttling, logging y configuración de producción.

---

## 1. Estado de Autenticación (JWT)

### Fortalezas
- JWT implementado con `djangorestframework-simplejwt` (v5.5+)
- Claims personalizados: `cedula`, `roles` (TokenObtainPairSerializer)
- Access token expiración configurable (actualmente 60 min)
- Refresh token expiración 24 horas
- Algoritmo HS256

### Brechas Críticas
| Brecha | Severidad | Detalle |
|--------|-----------|---------|
| **Throttling login ausente** | **ALTA** | Sin límite de intentos en `POST /api/v1/auth/token/`; vulnerable a fuerza bruta y credential stuffing. |
| **Rotación refresh tokens deshabilitada** | **ALTA** | `ROTATE_REFRESH_TOKENS = False`; `BLACKLIST_AFTER_ROTATION` no configurado; app `token_blacklist` no instalada. |
| **Clave firma JWT = SECRET_KEY** | **ALTA** | `SIGNING_KEY = SECRET_KEY` (base.py:110); compromiso de SECRET_KEY permite forjar JWTs Y firmar cookies/sesiones Django. |
| **Access token 60 min vs 30 min ACD** | **MEDIA** | Configurado 60 min (base.py:106); decisión ACD requiere 30 min. |
| **Sin endpoint logout** | **MEDIA** | No hay revocación explícita de refresh token. |

### Recomendaciones Prioritarias
1. **Inmediato:** Configurar `AnonRateThrottle` (5/min) en `TokenPairView` y `REST_FRAMEWORK.DEFAULT_THROTTLE_RATES`.
2. **Inmediato:** Habilitar `ROTATE_REFRESH_TOKENS=True`, `BLACKLIST_AFTER_ROTATION=True`, instalar `rest_framework_simplejwt.token_blacklist`, ejecutar migraciones.
3. **Inmediato:** Separar `JWT_SIGNING_KEY` via env var distinta de `SECRET_KEY`.
4. **Corto plazo:** Ajustar `ACCESS_TOKEN_LIFETIME = timedelta(minutes=30)`.
5. **Corto plazo:** Implementar `POST /api/v1/auth/logout/` que añada refresh token a blacklist.

---

## 2. Estado de Autorización (RBAC, Ámbitos, IDOR)

### Fortalezas ✅ **VERIFICADO COMPLETO**
- **Matriz RBAC server-side** completa y coincidente con literal 6.2 de specify.md (validado en test_rbac_permissions.py:167-169).
- **Denegación por defecto (closed world)**: roles no en matriz → acceso denegado.
- **ScopeFilterMixin** filtra ORM por ámbito institucional (`own`, `carrera`, `facultad`, `asignado`, `borrador`).
- **Protección IDOR robusta**: acceso a recurso ajeno retorna **404** (no 403) para no filtrar existencia.
- **14 casos de regresión IDOR históricos** cubiertos por tests automatizados (todos passing).
- **Separación clara**: `HasRolePermission` (permisos) + `ScopeFilterMixin` (filtrado datos).

### Cobertura de Matriz (Recursos × Métodos × Roles)
| Recurso | GET | POST | PUT | PATCH | DELETE |
|---------|-----|------|-----|-------|--------|
| expedientes | ✅ | ✅ | - | - | - |
| expedientes:enviar | - | ✅ | - | - | - |
| peticiones | - | ✅ | - | - | - |
| peticiones:documento | ✅ | ✅ | - | - | - |
| checklist | ✅ | ✅ | ✅ | ✅ | - |
| expedientes:observar | - | ✅ | - | - | - |
| informes | - | ✅ | - | - | - |
| declaratorias | - | ✅ | ✅ | ✅ | - |
| catalogos:requisitos | - | ✅ | ✅ | - | - |
| notificaciones | ✅ | - | - | ✅ | - |

### Ámbitos por Rol
| Rol | expedientes | peticiones:documento | checklist | informes | declaratorias |
|-----|-------------|----------------------|-----------|----------|---------------|
| ESTUDIANTE | own | own | DENY | DENY | DENY |
| SECRETARIA_CARRERA | carrera | asignado | DENY | DENY | DENY |
| SECRETARIO_ABOGADO | facultad | asignado | facultad/allow | allow | DENY |
| ANALISTA_APOYO | facultad | asignado | facultad/borrador | borrador | DENY |
| DECANO | facultad | DENY | DENY | DENY | allow |
| DIRECTOR_CARRERA | carrera | asignado | DENY | DENY | DENY |
| RESPONSABLE_DEPENDENCIA | DENY | DENY | DENY | DENY | DENY |
| ADMINISTRADOR | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW |

**Estado:** **VERIFICADO** — Sin brechas detectadas en autorización.

---

## 3. Validación de Entradas y Documentos PDF

### Fortalezas
- **Validación estricta server-side** (Principio C-006, CA-G-01): magic bytes, tamaño, hash SHA-256 ANTES de guardar.
- **Límite 10 MB** enforceado en `validar_tamano_archivo` y serializer.
- **Magic bytes `%PDF-`** validados en offset 0 (rechaza espacios, headers manipulados).
- **Hash SHA-256 streaming** para integridad (calculado en chunks, no carga todo en memoria).
- **Versionado N+1** con marca `es_vigente` (solo última versión vigente).
- **Tests exhaustivos**: 40+ tests cubren PDF válido, ejecutables renombrados (PE, PNG, JPEG), texto plano, vacío, >10MB, header manipulado, múltiples versiones.

### Brechas
| Brecha | Severidad | Detalle |
|--------|-----------|---------|
| **Validación MIME real incompleta** | **MEDIA** | Solo magic bytes; **no usa `python-magic`** (libmagic) ni parsing PDF (pikepdf/PyPDF2). PDF políglota o con estructura maliciosa pasaría. |
| **Throttling carga documentos ausente** | **MEDIA** | Sin límite de cargas/hora/usuario en `POST /api/v1/peticiones/{id}/documento/`. |
| **Rutas internas expuestas en serializers** | **MEDIA** | `DocumentoEntregadoSerializer.archivo_path` y `DeclaratoriaAptitudSerializer.archivo_memorando_firmado_path` exponen estructura almacenamiento privado. |

### Recomendaciones
1. **Evaluar `python-magic`** (requiere libmagic en Docker) o `pikepdf` para validación estructura PDF real.
2. **Implementar `UserRateThrottle` (10/hour)** en `cargar_documento` action.
3. **Remover `archivo_path`/`archivo_memorando_firmado_path` de serializers de respuesta**; usar `download_url` opaco apuntando a endpoint autorizado.

---

## 4. Protección de Secretos y Datos Sensibles

### Fortalezas
- `SECRET_KEY`, `DB_PASSWORD`, etc. via `environ.Env()` obligatorias (base.py:11,65).
- `DEBUG = env.bool("DEBUG", default=False)` — default seguro.
- Configuraciones separadas: `local.py` (DEBUG=True), `test.py` (DEBUG=False, SQLite memory).
- No cuentas demo ni passwords hardcoded en código producción (solo en fixtures de test).

### Brechas Críticas
| Brecha | Severidad | Detalle |
|--------|-----------|---------|
| **JWT_SIGNING_KEY = SECRET_KEY** | **ALTA** | Clave única para firmar JWTs Y sesiones Django/cookies. Compromiso = control total. |
| **Sin procedimiento rotación claves** | **MEDIA** | No hay documento ni automatización para rotar SECRET_KEY ni JWT_SIGNING_KEY. |
| **Gitleaks no ejecutado historial completo** | **MEDIA** | Requiere verificación independiente (fuera de alcance esta auditoría). |

### Recomendaciones
1. **Inmediato:** Crear `JWT_SIGNING_KEY` env var separada; configurar `SIMPLE_JWT.SIGNING_KEY = env("JWT_SIGNING_KEY")`.
2. **Corto plazo:** Documentar procedimiento rotación (generar nueva, deploy, revocar antigua, ventana de solape).
3. **Continuo:** Integrar Gitleaks en pipeline CI (pre-commit + scheduled).

---

## 5. Almacenamiento Privado y Ciclo de Vida

### Fortalezas
- **PrivateMediaStorage** heredado de `FileSystemStorage` con `base_url = None` y `url()` → `NotImplementedError`.
- Archivos en `MEDIA_ROOT/private/expedientes/{year}/{expediente_id}/` — fuera de web root.
- **Descarga solo vía endpoint autorizado** (`descargar_documento` con validación RBAC + ámbito).
- **Validación ANTES de persistir** (orden correcto en `cargar_documento.execute`).
- **Transacción atómica** cubre consistencia DB.
- **Tests de almacenamiento** verifican: ruta privada, archivo existe, sin base_url, descarga autorizada, versionado.

### Brechas
| Brecha | Severidad | Detalle |
|--------|-----------|---------|
| **Rollback archivo en disco ausente** | **BAJA-MEDIA** | `transaction.atomic` hace rollback DB pero archivo parcial puede quedar en disco si falla tras `storage.save()`. |
| **Sin limpieza archivos huérfanos** | **BAJA-MEDIA** | Versiones `es_vigente=False` permanecen en disco sin job de limpieza. |
| **PermissionError histórico no verificado** | **BAJA** | Requiere entorno Docker real con volúmenes montados para reproducir. |

### Recomendaciones
1. **Patrón "guardar archivo → crear registro DB"** (orden inverso) o compensación manual en `except` borrando archivo si falla commit.
2. **Management command `limpiar_archivos_huerfanos`** programado (diario/semanal).
3. **Documentar y testear `PermissionError`** en entorno Docker staging.

---

## 6. Manejo de Errores y Logging Seguro

### Fortalezas
- `DEBUG=False` por defecto en base.py.
- Custom APIExceptions para códigos 400 específicos (`EstadoPeticionInvalidoAPI`, `UsuarioNoAutorizadoAPI`, `ValidacionPDF_API`).
- Logger usado en signals.py (auditoría) con `exc_info=True` para errores.
- No `print()` en código crítico (salvo evaluar_checklist.py).

### Brechas Críticas
| Brecha | Severidad | Detalle |
|--------|-----------|---------|
| **Sin EXCEPTION_HANDLER global** | **MEDIA** | Formato errores inconsistente; faltan handlers 409, 429, 500 estandarizados. |
| **`print()` en evaluar_checklist.py:164,170** | **MEDIA** | Exponen `username`, `roles`, `facultad_id` en stdout contenedor. |
| **Sin configuración LOGGING** | **MEDIA** | Sin handlers rotativos, niveles producción, formato JSON, filtros PII. |
| **IP auditoría suplantable** | **ALTA** | `_get_current_request()` retorna `None`; `_get_client_ip` acepta `X-Forwarded-For` sin validar `TRUSTED_PROXIES`. |
| **IP no capturada en signals automáticas** | **ALTA** | Signals usan `_get_current_request()` → `None` → IP = `None` en EventoAuditoria. |

### Recomendaciones
1. **Inmediato:** Eliminar `print()` en `evaluar_checklist.py`; usar `logger.debug()`.
2. **Inmediato:** Implementar middleware `ThreadLocalRequestMiddleware` que guarde `request` en `_thread_locals`.
3. **Inmediato:** Configurar `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")` y `TRUSTED_PROXIES` lista IPs/CIDR en `production.py`.
4. **Corto plazo:** Crear `core/adapters/exceptions.py` con `custom_exception_handler` formato uniforme `{ "error": { "code", "message", "details" } }`; registrar en `REST_FRAMEWORK.EXCEPTION_HANDLER`.
5. **Corto plazo:** Configuración `LOGGING` completa en `base.py`/`production.py`: handlers `RotatingFileHandler`, formato JSON, nivel INFO prod, filtro que elimine `password`, `token`, `authorization` headers.

---

## 7. Hardening de Producción e Infraestructura

### Estado Actual: **CRÍTICO - CONFIGURACIÓN PRODUCCIÓN INEXISTENTE**

| Componente | Estado | Detalle |
|------------|--------|---------|
| `settings/production.py` | **AUSENTE** | Solo `base.py`, `local.py`, `test.py`. |
| Dockerfile | **AUSENTE** | Sin contenedorización; histórico usa `runserver`. |
| docker-compose.prod.yml | **AUSENTE** | Sin orquestación producción. |
| Nginx config | **AUSENTE** | Sin reverse proxy, TLS, rate limiting. |
| Gunicorn/WSGI | **AUSENTE** | Sin servidor producción. |
| Usuario no-root contenedor | **AUSENTE** | Sin Dockerfile. |
| Variables entorno producción | **PARCIAL** | `.env` no versionado (OK) pero sin plantilla `.env.example`. |

### Configuraciones de Seguridad Faltantes (settings/production.py)
```python
# Requeridas en production.py
DEBUG = False
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")  # Sin default []
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 año
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS")
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
# Content Security Policy (via django-csp o middleware custom)
# CORS: django-cors-headers + CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS")
```

### Recomendaciones Prioritarias
1. **CRÍTICO - Semana 1:** Crear `settings/production.py` heredando de `base.py` con todo hardening arriba.
2. **CRÍTICO - Semana 1:** Crear `Dockerfile` multi-stage: builder → runtime (python:3.12-slim), usuario `appuser` no-root, Gunicorn 4 workers, healthcheck.
3. **CRÍTICO - Semana 1:** Crear `docker-compose.prod.yml`: backend + PostgreSQL + Nginx (SSL Let's Encrypt/Certbot) + volúmenes persistentes.
4. **CRÍTICO - Semana 1:** Configurar Nginx: `limit_req_zone`, `proxy_set_header X-Forwarded-For`, TLS 1.2+, HSTS, headers seguridad.
5. **Corto plazo:** Documentar `.env.example` con todas las variables requeridas para producción.

---

## 8. Protección de Documentación API (Swagger/ReDoc/OpenAPI)

### Estado: **FALLIDO - PÚBLICO POR DEFECTO**

| Endpoint | Configuración Actual | Requerido Producción |
|----------|---------------------|---------------------|
| `/api/v1/docs/` (Swagger UI) | `AllowAny` (base.py:120) | `IsAdminUser` |
| `/api/v1/redoc/` (ReDoc) | `AllowAny` | `IsAdminUser` |
| `/api/v1/schema/` (OpenAPI JSON) | `AllowAny` | `IsAdminUser` |

### Recomendación
- En `production.py`: `SPECTACULAR_SETTINGS["SERVE_PERMISSIONS"] = ["rest_framework.permissions.IsAdminUser"]`
- En `local.py`/`test.py`: mantener `AllowAny` para desarrollo.
- Verificar en tests de integración que anónimo recibe 403/401 en producción.

---

## 9. Dependencias y Vulnerabilidades

### Estado Actual
| Herramienta | Estado | Hallazgos |
|-------------|--------|-----------|
| `safety check` | **NO EJECUTADO** | Requiere ejecución en entorno con deps instaladas. |
| `bandit -r src/` | **NO EJECUTADO** | SAST no ejecutado. |
| `gitleaks detect --source=.` | **NO EJECUTADO** | Historial completo no escaneado. |
| Dependabot/Renovate | **AUSENTE** | Sin `.github/dependabot.yml`. |
| Versiones fijadas | **PARCIAL** | Rangos `>=x.y,<z.0` (no `==x.y.z`). |

### Dependencias Principales (requirements.txt)
| Paquete | Rango | Última Conocida | Notas |
|---------|-------|-----------------|-------|
| Django | >=5.2,<5.3 | 5.2.x | LTS actual; verificar CVE recientes. |
| djangorestframework | >=3.16,<4.0 | 3.16.x | Rango amplio; fijar versión exacta. |
| djangorestframework-simplejwt | >=5.5,<6.0 | 5.5.x | Verificar CVE en 5.5.x. |
| psycopg[binary] | >=3.2,<4.0 | 3.2.x | OK. |
| django-environ | >=0.12,<1.0 | 0.12.x | OK. |
| drf-spectacular | >=0.27,<1.0 | 0.27.x | OK. |
| reportlab | >=4.3,<5.0 | 4.3.x | Solo para PDF generation. |

### Recomendaciones
1. Ejecutar `safety check` y `bandit -r src/` en pipeline CI (fallar build si hallazgos HIGH/CRITICAL).
2. Configurar Dependabot (`.github/dependabot.yml`) con schedule semanal, auto-merge para patch.
3. Considerar fijar versiones exactas (`==x.y.z`) en `requirements.txt` para builds reproducibles.
4. Programar revisión mensual de dependencias y actualización controlada.

---

## 10. Suite de Pruebas, Cobertura y Reproducibilidad

### Estado Ejecución Local
```
473 passed, 15 warnings in 20.24s
```
- **Suites incluidas:** `src/apps/*/tests/`, `src/core/adapters/tests/`
- **Cobertura módulos críticos:** Auth, RBAC, PDF validation, Peticiones, Verificación, Resoluciones, Notificaciones, Auditoría.
- **Gaps de pruebas seguridad:** Throttling, rotación tokens, protección Swagger, IP auditoría real, e2e.

### Configuración pytest (pyproject.toml)
```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.test"
pythonpath = ["src"]
testpaths = ["src/apps"]  # <-- EXCLUYE src/core/tests y tests/e2e
```

### Brechas
| Brecha | Severidad | Detalle |
|--------|-----------|---------|
| **testpaths excluye `src/core/tests`** | **BAJA** | Se descubren por convención `test_*.py` pero no por config explícita. |
| **Sin `tests/e2e/`** | **MEDIA** | No existe suite de pruebas end-to-end en backend. |
| **Sin `--cov-fail-under`** | **MEDIA** | No hay umbral de cobertura obligatorio. |
| **Tests faltantes controles seguridad** | **ALTA** | Sin tests para: throttling login/carga, rotación/blacklist tokens, protección Swagger prod, IP auditoría con proxy real. |

### Recomendaciones
1. Cambiar `testpaths = ["src"]` para incluir todo explícitamente.
2. Agregar `--cov=src --cov-fail-under=80` (o valor acordado) a pytest config o CI.
3. Crear tests de seguridad faltantes (ver BACKLOG_BRECHAS_SEGURIDAD.md).
4. Evaluar necesidad de suite `tests/e2e/` con base de datos real (PostgreSQL testcontainers).

---

## 11. Verificación Evidencias ACD 4 (Integrantes)

| Identificador | PR | Commit | Estado |
|---------------|----|--------|--------|
| `a1b2c3d` | #42 | No encontrado | **NO VERIFICADO** |
| `e4f5g6h` | #43 | No encontrado | **NO VERIFICADO** |
| `i7j8k9l` | #44 | No encontrado | **NO VERIFICADO** |
| `m0n1o2p` | #45 | No encontrado | **NO VERIFICADO** |
| `q3r4s5t` | #46 | No encontrado | **NO VERIFICADO** |

**Nota:** Identificadores parecen placeholders (formato hash corto genérico `a1b2c3d`). No existen en historial Git del repositorio auditado. Solicitar evidencia real (SHA commits, URLs PRs, autores) o marcar como no aplicables.

---

## 12. Priorización Final de Brechas (Backlog)

| Prioridad | ID | Brecha | Control Afectado | Esfuerzo | Riesgo |
|-----------|----|--------|------------------|----------|--------|
| **CRÍTICA** | SEC-T001 | Configuración producción completa (settings/production.py, Dockerfile, docker-compose, Nginx) | Hardening infra | Alto | **CRÍTICO** |
| **ALTA** | SEC-T002 | Throttling login (5/min/IP) | SEC-AUTH-01 | Bajo | **ALTO** |
| **ALTA** | SEC-T003 | Rotación + blacklist refresh tokens | SEC-AUTH-02 | Medio | **ALTO** |
| **ALTA** | SEC-T004 | JWT_SIGNING_KEY separada de SECRET_KEY | SEC-SEC-01 | Bajo | **ALTO** |
| **ALTA** | SEC-T005 | IP auditoría con middleware thread-local + TRUSTED_PROXIES | SEC-LOG-03 | Medio | **ALTO** |
| **MEDIA** | SEC-T006 | Access token 30 min (ACD) | SEC-AUTH-03 | Bajo | **MEDIO** |
| **MEDIA** | SEC-T007 | Validación MIME real (python-magic/pikepdf) | SEC-VAL-01 | Medio | **MEDIO** |
| **MEDIA** | SEC-T008 | Throttling carga documentos (10/hora/usuario) | SEC-VAL-02 | Bajo | **MEDIO** |
| **MEDIA** | SEC-T009 | Remover rutas internas de serializers (archivo_path) | SEC-SEC-02 | Bajo | **MEDIO** |
| **MEDIA** | SEC-T010 | Handler global excepciones + formato uniforme | SEC-LOG-01 | Medio | **MEDIO** |
| **MEDIA** | SEC-T011 | Logging estructurado (LOGGING dict, rotación, filtros PII) | SEC-LOG-02 | Medio | **MEDIO** |
| **MEDIA** | SEC-T012 | Eliminar print() en evaluar_checklist.py | SEC-LOG-02 | Bajo | **MEDIO** |
| **MEDIA** | SEC-T013 | Protección Swagger/ReDoc/schema en producción (IsAdminUser) | Swagger protection | Bajo | **MEDIO** |
| **MEDIA** | SEC-T014 | Safety + Bandit + Gitleaks en CI/CD | Dependencias | Medio | **MEDIO** |
| **MEDIA** | SEC-T015 | Dependabot configurado | Dependencias | Bajo | **MEDIO** |
| **MEDIA** | SEC-T016 | Cobertura tests + fail_under + testpaths correcto | Suite pruebas | Medio | **MEDIO** |
| **MEDIA** | SEC-T017 | Tests seguridad faltantes (throttling, rotación, Swagger, IP auditoría) | Suite pruebas | Medio | **MEDIO** |
| **BAJA** | SEC-T018 | Procedimiento documentado rotación secretos | SEC-SEC-01 | Bajo | **BAJO** |
| **BAJA** | SEC-T019 | Limpieza archivos huérfanos (management command) | Almacenamiento | Medio | **BAJO** |
| **BAJA** | SEC-T020 | Verificación PermissionError histórico en Docker | Almacenamiento | Medio | **BAJO** |
| **BAJA** | SEC-T021 | Evidencias ACD 4 reales (commits/PRs) | ACD 4 | Bajo | **BAJO** |

---

## 13. Conclusiones y Cierre de Auditoría

### Base Funcional Implementada ✅
- Autenticación JWT funcional
- Autorización RBAC completa y probada (matriz 6.2, 14 casos IDOR)
- Validación PDF estricta (magic bytes, tamaño, hash SHA-256)
- Almacenamiento privado con descarga autorizada
- Auditoría automática via signals (EventoAuditoria JSONB)
- Suite de pruebas extensa (473 tests passing)

### Controles Realmente Verificados ✅
- RBAC/IDOR (100% casos regresión)
- Validación PDF básica (magic bytes + size + hash)
- Almacenamiento privado (ruta, sin URL pública, descarga autorizada)
- Hash integridad documentos
- Configuración base secrets/DB/DEBUG via env vars

### Controles Implementados Sin Pruebas Suficientes ⚠️
- Captura IP auditoría (código existe pero `_get_current_request()` retorna `None`)
- Almacenamiento privado (funciona pero sin tests de fallos IO/rollback)

### Brechas Pendientes Hardening 🔴
**Críticas (bloquean producción):**
1. Sin configuración producción (settings/production.py, Dockerfile, Nginx, Gunicorn)
2. Refresh tokens sin rotación/blacklist
3. JWT signing key = SECRET_KEY
4. IP auditoría suplantable (sin TRUSTED_PROXIES, sin middleware thread-local)
5. Throttling ausente en login y carga documentos

**Altas/Medias:**
6. Access token 60 min vs 30 min ACD
7. Validación MIME real incompleta
8. Rutas internas expuestas en serializers
9. Sin handler global excepciones / logging estructurado
10. Swagger/ReDoc público
11. Sin escaneo vulnerabilidades (Safety, Bandit, Gitleaks) en CI
12. Sin umbral cobertura / testpaths incompleto

### Veredicto Final

> **El backend NO está listo para producción.**  
> Posee una base funcional robusta y bien probada en lógica de negocio y autorización, pero **carece completamente de hardening de infraestructura, gestión segura de claves JWT, throttling, logging seguro y configuración de producción**.  
> Las brechas críticas (SEC-T001 a SEC-T005) deben resolverse **antes de cualquier despliegue en entorno productivo**.  
> El backlog priorizado (SEC-T001 a SEC-T021) proporciona hoja de ruta para cerrar brechas manteniendo compatibilidad con frontend en desarrollo (specs/003).

---

**Firma del auditor:** opencode AI Assistant  
**Fecha:** 2026-11-05  
**Documentos generados:**
- `CHECKLIST_SEGURIDAD_DETALLADA.md`
- `MATRIZ_TRAZABILIDAD_SEGURIDAD.md`
- `INFORME_HARDING_SEGURIDAD.md` (este)
- `INFORME_PRUEBAS_SEGURIDAD.md` (pendiente)
- `BACKLOG_BRECHAS_SEGURIDAD.md` (pendiente)