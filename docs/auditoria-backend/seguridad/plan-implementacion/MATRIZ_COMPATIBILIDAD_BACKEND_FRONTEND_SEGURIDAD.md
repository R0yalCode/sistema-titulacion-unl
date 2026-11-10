# MATRIZ DE COMPATIBILIDAD BACKEND-FRONTEND — TAREAS DE SEGURIDAD

**Fecha:** 2026-11-05  
**Versión:** 1.0  
**Frontend de referencia:** specs/003-frontend-titulacion/ (Vistas V-01 a V-09, rutas, CA)

---

## Resumen de Impacto por Tarea

| ID | Tarea | Impacto Frontend | Contratos API Afectados | Cambios HTTP | Cambios Auth | Cambios Permisos | Coordinación Requerida |
|----|-------|------------------|------------------------|--------------|--------------|------------------|------------------------|
| SEC-T001 | Configuración Producción | **ALTO** | Todos (HTTPS, CORS, CSRF) | Ninguno (mismos códigos) | Cookies seguras, CSRF token | Ninguno | **SÍ** — API_BASE_URL HTTPS, cookies, CSRF |
| SEC-T002 | Throttling Login | **BAJO** | POST /api/v1/auth/token/ | 429 nuevo | Ninguno | Ninguno | Menor — mensaje "demasiados intentos" |
| SEC-T003 | Rotación + Blacklist Refresh | **MEDIO** | POST /api/v1/auth/token/ (refresh), POST /api/v1/auth/logout/ (nuevo) | 401 en refresh con token viejo | Refresh token rota cada uso; logout invalida | Ninguno | **SÍ** — Interceptor axios: guardar nuevo refresh, llamar logout, manejar 401 refresh |
| SEC-T004 | JWT_SIGNING_KEY Separada | **NINGUNO** | Ninguno (interno) | Ninguno | Tokens JWT existentes invalidados (re-login único) | Ninguno | No — solo re-login tras deploy |
| SEC-T005 | IP Auditoría | **NINGUNO** | Ninguno (interno auditoría) | Ninguno | Ninguno | Ninguno | No — transparente |
| SEC-T006 | Access Token 30 min | **BAJO** | POST /api/v1/auth/token/ | Ninguno | Refresh más frecuente (~25 min) | Ninguno | Menor — Interceptor ya debe manejar refresh automático |
| SEC-T007 | Validación MIME Real | **NINGUNO** | POST /api/v1/peticiones/{id}/documento/ | 400 si PDF inválido (igual) | Ninguno | Ninguno | No — mismo contrato, validación más estricta interna |
| SEC-T008 | Throttling Carga Docs | **BAJO** | POST /api/v1/peticiones/{id}/documento/ | 429 nuevo | Ninguno | Ninguno | Menor — mensaje "límite cargas alcanzado" |
| SEC-T009 | Remover Rutas Internas Serializers | **MEDIO** | GET /api/v1/peticiones/{id}/documento/ (response), GET /api/v1/declaratorias/{id}/ (response) | Ninguno | Ninguno | Ninguno | **SÍ** — Frontend migra `archivo_path` → `download_url` en V-03, V-07, V-08 |
| SEC-T010 | Handler Global Excepciones | **MEDIO** | **Todos los endpoints** | Formato uniforme errores | Ninguno | Ninguno | **SÍ** — Frontend actualiza error handling: `{error: {code, message, details}}` |
| SEC-T011 | Logging Estructurado | **NINGUNO** | Ninguno | Ninguno | Ninguno | Ninguno | No — interno |
| SEC-T012 | Eliminar print() | **NINGUNO** | Ninguno | Ninguno | Ninguno | Ninguno | No — interno |
| SEC-T013 | Protección Swagger/ReDoc | **BAJO** | /api/v1/docs/, /api/v1/redoc/, /api/v1/schema/ | 403 anónimo prod | Admin required | Ninguno | No — frontend no usa Swagger |
| SEC-T014 | CI/CD Security | **NINGUNO** | Ninguno | Ninguno | Ninguno | Ninguno | No — pipeline interno |
| SEC-T015 | Dependabot | **NINGUNO** | Ninguno | Ninguno | Ninguno | Ninguno | No — pipeline interno |
| SEC-T016 | Cobertura Tests | **NINGUNO** | Ninguno | Ninguno | Ninguno | Ninguno | No — configuración tests |
| SEC-T017 | Tests Seguridad | **NINGUNO** | Ninguno | Ninguno | Ninguno | Ninguno | No — tests backend |
| SEC-T018 | Procedimiento Rotación | **NINGUNO** | Ninguno | Ninguno | Ninguno | Ninguno | No — documentación |
| SEC-T019 | Limpieza Huérfanos | **NINGUNO** | Ninguno | Ninguno | Ninguno | Ninguno | No — management command |
| SEC-T020 | Verificación PermissionError | **NINGUNO** | Ninguno | Ninguno | Ninguno | Ninguno | No — validación ops |
| SEC-T021 | Evidencias ACD 4 | **NINGUNO** | Ninguno | Ninguno | Ninguno | Ninguno | No — trazabilidad |

---

## Detalle de Impacto por Tareas con Cambios Frontend

### SEC-T001 — Configuración Producción Completa (IMPACTO ALTO)

**Cambios Backend:**
- HTTPS obligatorio (SECURE_SSL_REDIRECT=True, HSTS)
- Cookies: `Secure`, `HttpOnly`, `SameSite=Lax`
- CSRF: `CSRF_COOKIE_SECURE=True`, `CSRF_TRUSTED_ORIGINS` configurado
- CORS: `django-cors-headers` + `CORS_ALLOWED_ORIGINS`
- Headers seguridad: HSTS, CSP, X-Frame-Options, Referrer-Policy, COOP

**Impacto Frontend (specs/003):**
| Aspecto | Cambio Requerido | Vistas Afectadas |
|---------|------------------|------------------|
| `API_BASE_URL` | Cambiar `http://localhost:8000` → `https://dominio.unl.edu.ec` | Todas (V-01 a V-09) |
| Cookies | Navegador envía cookies seguras automáticamente en HTTPS; `SameSite=Lax` permite navegación normal | Login (V-01), estado sesión |
| CSRF Token | Frontend debe leer `csrftoken` cookie y enviar en header `X-CSRFToken` en requests mutantes (POST/PUT/PATCH/DELETE) | Crear expediente (V-02), Cargar docs (V-03), Checklist (V-05), Informe (V-07), Declaratoria (V-08) |
| CORS | `CORS_ALLOWED_ORIGINS` debe incluir origen frontend (ej. `https://frontend.unl.edu.ec`) | Todas |
| Credentials | `withCredentials: true` en axios/fetch para enviar cookies | Login, requests autenticados |

**Pruebas de Contrato Requeridas:**
1. Login HTTPS → 200 + access/refresh en body + `csrftoken` cookie Secure/HttpOnly.
2. Request mutante sin `X-CSRFToken` → 403 CSRF.
3. Request mutante con `X-CSRFToken` válido → 200/201.
4. CORS preflight OPTIONS → 200 con headers correctos.
5. Logout → cookies limpiadas.

**Coordinación:** Reunión técnica con equipo frontend antes de deploy staging. Documentar cambios en `FRONTEND_INTEGRATION_GUIDE.md`.

---

### SEC-T003 — Rotación + Blacklist Refresh Tokens (IMPACTO MEDIO)

**Cambios Backend:**
- `ROTATE_REFRESH_TOKENS=True`: cada refresh genera nuevo access + nuevo refresh; refresh anterior → blacklist.
- `BLACKLIST_AFTER_ROTATION=True`.
- Nuevo endpoint: `POST /api/v1/auth/logout/` (body: `{"refresh": "..."}`) → 205.
- Refresh token viejo usado → 401 `{"detail": "Token is blacklisted", "code": "token_not_valid"}`.

**Impacto Frontend:**
| Componente | Cambio Requerido |
|------------|------------------|
| **Interceptor axios (refresh automático)** | Tras recibir nuevo access+refresh en respuesta 401→refresh, **guardar nuevo refresh token** (reemplazar el viejo). |
| **Logout (V-01, barra usuario, expiración sesión)** | Llamar `POST /api/v1/auth/logout/` con refresh token actual **antes** de limpiar estado local. |
| **Manejo 401 en refresh** | Si refresh retorna 401 (token blacklisted/expirado) → redirigir a login (V-01) limpiando estado. |
| **Almacenamiento tokens** | Access en memoria (variable JS); Refresh en `httpOnly` cookie **O** localStorage (según arquitectura actual). Si en localStorage, actualizar en cada refresh. |

**Contrato API Nuevo:**
```json
// POST /api/v1/auth/logout/
Request: { "refresh": "eyJ..." }
Response: 205 Reset Content (sin body)

// POST /api/v1/auth/token/ (refresh)
Request: { "refresh": "eyJ..." }
Response 200: { "access": "eyJ...", "refresh": "eyJ...nuevo" }
Response 401: { "detail": "Token is blacklisted", "code": "token_not_valid" }
```

**Pruebas de Contrato:**
1. Login → access + refresh guardados.
2. Access expira → interceptor usa refresh → nuevo access + **nuevo refresh** guardado.
3. Refresh anterior usado → 401 blacklisted.
4. Logout → POST /auth/logout/ → 205 → estado limpio → login page.
5. Refresh token expirado (24h) → 401 → redirect login.

**Coordinación:** Issue frontend para actualizar interceptor axios y logout. Documentar en `AUTH_FLOW_CHANGES.md`.

---

### SEC-T009 — Remover Rutas Internas Serializers (IMPACTO MEDIO)

**Cambios Backend:**
- `DocumentoEntregadoSerializer`: remover `archivo_path`; añadir `download_url = SerializerMethodField()` → `request.build_absolute_uri(f"/api/v1/peticiones/{obj.peticion_id}/documento/")`.
- `DeclaratoriaAptitudSerializer`: remover `archivo_memorando_firmado_path`; añadir `download_url` → endpoint download declaratoria (por crear/confirmar en resoluciones/views.py).

**Impacto Frontend (specs/003):**
| Vista | Componente Actual | Cambio Requerido |
|-------|-------------------|------------------|
| **V-03** (Carga/Descarga docs) | `documento.archivo_path` para construir URL descarga | Usar `documento.download_url` directo en `<a href>` o `axios.get()` |
| **V-07** (Informe aptitud) | `informe.archivo_informe_path` (si expuesto) | Verificar serializer InformeAptitudSerializer — actualmente NO expone path (solo `archivo_informe_path` en modelo, serializer fields no lo incluye). **Sin impacto si no expuesto.** |
| **V-08** (Declaratoria) | `declaratoria.archivo_memorando_firmado_path` | Usar `declaratoria.download_url` |

**Verificación Serializers Actuales:**
- `InformeAptitudSerializer` (resoluciones/serializers.py): fields NO incluye `archivo_informe_path` ✅
- `DeclaratoriaAptitudSerializer` (resoluciones/serializers.py): fields **INCLUYE** `archivo_memorando_firmado_path` ❌ → SEC-T009 lo remueve.

**Contrato API Cambiado:**
```json
// ANTES (DocumentoEntregadoSerializer)
{
  "id": "...",
  "archivo_path": "expedientes/2026/uuid/timestamp_doc.pdf",  // REMOVER
  "download_url": "https://api.unl.edu.ec/api/v1/peticiones/{id}/documento/"  // NUEVO
}

// ANTES (DeclaratoriaAptitudSerializer)
{
  "id": "...",
  "archivo_memorando_firmado_path": "expedientes/2026/uuid/timestamp_mem.pdf",  // REMOVER
  "download_url": "https://api.unl.edu.ec/api/v1/declaratorias/{id}/documento/"  // NUEVO (endpoint por confirmar)
}
```

**Pruebas de Contrato:**
1. GET /api/v1/peticiones/{id}/documento/ → response incluye `download_url` (no `archivo_path`).
2. GET `download_url` + JWT → 200 PDF (descarga autorizada).
3. GET /api/v1/declaratorias/{id}/ → response incluye `download_url` (no `archivo_memorando_firmado_path`).
4. Frontend: botón "Descargar" usa `download_url` → funciona.

**Coordinación:** **Requerida**. Frontend debe migrar V-03 y V-08. Endpoint download declaratoria debe confirmarse/implementarse en resoluciones/views.py (GET /api/v1/declaratorias/{id}/documento/).

---

### SEC-T010 — Handler Global Excepciones (IMPACTO MEDIO)

**Cambios Backend:**
- Formato uniforme **todos** los errores HTTP:
```json
{
  "error": {
    "code": "string",        // ej: "validation_error", "authentication_failed", "permission_denied", "not_found", "throttled", "server_error"
    "message": "string",     // mensaje legible usuario final (español institucional)
    "details": {}            // opcional: campos, parámetros, metadatos
  }
}
```
- Códigos mapeados: 400, 401, 403, 404, 409, 429, 500.
- 500 **NUNCA** incluye stack trace, SQL, rutas internas.

**Impacto Frontend:**
| Componente | Cambio Requerido |
|------------|------------------|
| **Error handling global (axios interceptor / try-catch)** | Parsear nuevo formato `response.data.error.{code, message, details}`. Mostrar `message` al usuario. Usar `code` para lógica condicional (ej: redirect login si `authentication_failed`). |
| **Validación formularios (V-02, V-03, V-05, V-07, V-08)** | `details` puede contener errores por campo → mostrar inline. |
| **Throttling (SEC-T002, SEC-T008)** | `code: "throttled"` + `message: "Demasiados intentos, espera X minutos"` → mostrar toast/banner. |
| **Permisos/IDOR** | `code: "permission_denied"` o `not_found` (404 IDOR) → mensaje genérico "No tienes acceso" o "Recurso no encontrado". |

**Ejemplos Nuevo Formato:**
```json
// 400 Validation Error
{ "error": { "code": "validation_error", "message": "Datos de entrada inválidos", "details": { "archivo": ["El archivo excede el límite de 10 MB"] } } }

// 401 Authentication Failed
{ "error": { "code": "authentication_failed", "message": "Token de acceso expirado o inválido", "details": {} } }

// 403 Permission Denied
{ "error": { "code": "permission_denied", "message": "No tienes permiso para realizar esta acción", "details": {} } }

// 404 Not Found (IDOR)
{ "error": { "code": "not_found", "message": "Recurso no encontrado", "details": {} } }

// 429 Throttled
{ "error": { "code": "throttled", "message": "Demasiadas solicitudes. Intenta de nuevo en 45 segundos.", "details": { "retry_after": 45 } } }

// 500 Server Error
{ "error": { "code": "server_error", "message": "Error interno del servidor. El equipo técnico ha sido notificado.", "details": {} } }
```

**Pruebas de Contrato:**
1. Cada código HTTP (400,401,403,404,429,500) retorna formato uniforme.
2. `message` en español institucional, sin tecnicismos.
3. `details` presente solo cuando aplica (validación campos, retry_after).
4. 500 sin stack trace, SQL, rutas.

**Coordinación:** **Requerida**. Frontend debe actualizar manejo de errores global. Documentar formato en `API_ERROR_FORMAT.md`. Coordinar deploy simultáneo backend+frontend para evitar mismatch temporal.

---

## Tareas SIN Impacto Frontend (17 tareas)

| ID | Tarea | Justificación Sin Impacto |
|----|-------|---------------------------|
| SEC-T004 | JWT_SIGNING_KEY Separada | Cambio interno clave; tokens invalidados → re-login único. |
| SEC-T005 | IP Auditoría | Interno señales Django; no expuesto en API. |
| SEC-T006 | Access Token 30 min | Interceptor refresh ya maneja expiración; solo más frecuente. |
| SEC-T007 | Validación MIME Real | Validación interna más estricta; mismo 400 si inválido. |
| SEC-T008 | Throttling Carga Docs | Solo añade 429; frontend muestra mensaje genérico. |
| SEC-T011 | Logging Estructurado | Interno contenedor; no API. |
| SEC-T012 | Eliminar print() | Limpieza stdout; no API. |
| SEC-T013 | Protección Swagger | Frontend no usa /docs, /redoc, /schema. |
| SEC-T014 | CI/CD Security | Pipeline interno; no runtime. |
| SEC-T015 | Dependabot | Pipeline interno. |
| SEC-T016 | Cobertura Tests | Configuración pytest; no runtime. |
| SEC-T017 | Tests Seguridad | Tests backend; no API. |
| SEC-T018 | Procedimiento Rotación | Documentación; no código. |
| SEC-T019 | Limpieza Huérfanos | Management command; no API. |
| SEC-T020 | Verificación PermissionError | Validación ops Docker; no API. |
| SEC-T021 | Evidencias ACD 4 | Trazabilidad Git; no código. |

---

## Plan de Coordinación Frontend

| Fase | Tareas con Impacto | Actividades Coordinación | Entregables |
|------|-------------------|-------------------------|-------------|
| **Pre-SEC-T001** | SEC-T001 | Reunión técnica: HTTPS, CORS, CSRF, cookies | `FRONTEND_INTEGRATION_GUIDE.md` |
| **Pre-SEC-T003** | SEC-T003 | Issue frontend: interceptor refresh, logout, 401 handling | `AUTH_FLOW_CHANGES.md` |
| **Pre-SEC-T009** | SEC-T009 | Confirmar endpoint download declaratoria; migrar V-03, V-08 | `DOWNLOAD_URL_MIGRATION.md` |
| **Pre-SEC-T010** | SEC-T010 | Definir formato errores; actualizar error handling global | `API_ERROR_FORMAT.md` |
| **Deploy Staging** | SEC-T001, T003, T009, T010 | Pruebas integradas backend+frontend en staging | Checklist validación V-01 a V-09 |

---

## Riesgos de Integración

| Riesgo | Tareas | Mitigación |
|--------|--------|------------|
| **Mismatch temporal formato errores** | SEC-T010 | Deploy coordinado backend+frontend; feature flag temporal si necesario. |
| **CSRF token no enviado en requests mutantes** | SEC-T001 | Verificar interceptor axios lee `csrftoken` cookie y envía `X-CSRFToken`. |
| **Refresh token storage incompatibilidad** | SEC-T003 | Confirmar dónde guarda frontend refresh (localStorage vs httpOnly cookie). |
| **Download URL declaratoria no existe** | SEC-T009 | Implementar GET /api/v1/declaratorias/{id}/documento/ en resoluciones/views.py ANTES de SEC-T009. |
| **CORS bloquea frontend en HTTPS** | SEC-T001 | `CORS_ALLOWED_ORIGINS` incluye origen frontend exacto. |

---

**Firma:** opencode AI Assistant  
**Fecha:** 2026-11-05