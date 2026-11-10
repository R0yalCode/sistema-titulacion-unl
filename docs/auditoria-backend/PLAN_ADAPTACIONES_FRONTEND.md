# PLAN DE ADAPTACIONES FRONTEND — SGT-SIAAF

**Versión:** 1.0  
**Fecha:** 2026-11-05  
**Basado en:** `MATRIZ_COMPATIBILIDAD_BACKEND_FRONTEND.md`, `AUDITORIA_SEGURIDAD.md`, `BACKLOG_BRECHAS_SEGURIDAD.md`, `specs/003-frontend-titulacion/specify.md`  
**Objetivo:** Definir adaptaciones necesarias en frontend para garantizar compatibilidad con backend actual y futuro (tras hardening seguridad)  
**Naturaleza:** Plan — **NO autoriza modificaciones en frontend**; solo documenta adaptaciones necesarias

---

## 1. Resumen de Adaptaciones Requeridas

| Prioridad | Adaptación | Dependencia Backend | Vistas Afectadas | Esfuerzo Estimado |
|-----------|------------|---------------------|------------------|-------------------|
| 🔴 **CRÍTICA** | HTTPS + Cookies seguras + CSRF | SEC-T001 (Producción) | Todas (Layout, Auth, API Client) | Alto |
| 🔴 **CRÍTICA** | Manejo rotación refresh + logout | SEC-T003 (Rotación/Blacklist) | Auth, Layout, API Client | Medio |
| 🟡 **MEDIA** | Migración `archivo_path` → `download_url` | SEC-T009 (Serializers) | V-03, V-07, V-08 | Medio |
| 🟡 **MEDIA** | Formato errores uniforme | SEC-T010 (Exception Handler) | Todas (Error Boundary, Forms, API Client) | Medio |
| 🟡 **MEDIA** | Endpoint `GET /peticiones/{id}/` | BE-02 | V-06, V-08 | Bajo (si BE-02 implementado) |
| 🟡 **MEDIA** | Checklist estudiante (BE-04) | BE-04 | V-04 | Bajo (si BE-04 autorizado) |
| 🟡 **MEDIA** | Catálogo carreras (BE-10) | BE-10 | V-03 | Bajo (si BE-10 autorizado) |
| 🟢 **BAJA** | Perfil `/me` (BE-01) | BE-01 | V-02, V-03, V-04, V-05, V-06 | Bajo |
| 🟢 **BAJA** | Campo `opcion_titulacion` (BE-06) | BE-06 | V-03, V-04 | Bajo |
| 🟢 **BAJA** | Motivo observación en respuestas (BE-07) | BE-07 | V-04, V-08 | Muy Bajo |

---

## 2. Fichas de Adaptación Detalladas

### ADAPT-001 — HTTPS, Cookies Seguras, CSRF, CORS (Producción)

| Campo | Detalle |
|-------|---------|
| **Problema** | Backend producción (SEC-T001) requerirá HTTPS obligatorio, cookies `Secure`+`HttpOnly`+`SameSite=Lax`, `CSRF_COOKIE_SECURE=True`, `CORS_ALLOWED_ORIGINS` configurado |
| **Dependencia** | SEC-T001 (Configuración producción completa) |
| **Vistas Afectadas** | Layout (Header, Sidebar), Auth (Login, Logout), API Client (todos requests) |
| **Cambios Requeridos** | 1. `VITE_API_BASE_URL` → `https://api.sgt-siaaf.unl.edu.ec` (variable entorno)<br>2. `API Client`: Detectar HTTPS y enviar `X-CSRFToken` header en requests mutantes (POST/PUT/PATCH/DELETE)<br>3. `AuthContext`: Leer `csrftoken` cookie + `access` token `sessionStorage`<br>4. `LoginPage`: Manejar cookies seguras (no accesibles via JS)<br>5. `Logout`: Limpiar cookies + `sessionStorage` + `queryClient.clear()`<br>6. `vite.config.ts`: Proxy desarrollo → `server.proxy` para evitar CORS local<br>7. `vite.config.ts`: Build producción → assets con hash, `index.html` sin cache |
| **Archivos Candidatos** | `frontend/src/lib/env.ts`, `frontend/src/api/client.ts`, `frontend/src/auth/AuthContext.tsx`, `frontend/src/auth/storage.ts`, `frontend/src/auth/jwt.ts`, `frontend/src/features/auth/LoginPage.tsx`, `frontend/src/components/layout/Header.tsx`, `frontend/vite.config.ts`, `frontend/.env.example` |
| **Validaciones Necesarias** | 1. Login HTTPS → 200 + access/refresh en body + `csrftoken` cookie Secure/HttpOnly<br>2. Request mutante sin `X-CSRFToken` → 403 CSRF<br>3. Request mutante con `X-CSRFToken` válido → 200/201<br>4. CORS preflight OPTIONS → 200 con headers correctos<br>5. Logout → cookies limpiadas + redirect login |
| **Dependencias Backend** | SEC-T001 completado (production.py, Dockerfile, docker-compose.prod.yml, Nginx TLS, headers SECURE_*, CSRF_TRUSTED_ORIGINS, CORS_ALLOWED_ORIGINS) |
| **Criterios de Aceptación** | Frontend funciona end-to-end contra backend staging HTTPS con cookies seguras, CSRF, CORS |
| **Riesgos** | Cambio breaking si frontend no actualiza `API_BASE_URL` y manejo CSRF antes de deploy producción |

---

### ADAPT-002 — Rotación Refresh Token + Logout Servidor

| Campo | Detalle |
|-------|---------|
| **Problema** | SEC-T003 habilita `ROTATE_REFRESH_TOKENS=True` + `BLACKLIST_AFTER_ROTATION=True` + endpoint `POST /api/v1/auth/logout/` |
| **Dependencia** | SEC-T003 (Rotación + Blacklist + Logout) + SEC-T004 (JWT_SIGNING_KEY separada) |
| **Vistas Afectadas** | Auth (Login, Logout), Layout (Header logout), API Client (Interceptor), Todas las vistas autenticadas |
| **Cambios Requeridos** | 1. **Interceptor Axios (API Client):**<br>   - Tras recibir 401 en request autenticado → llamar `POST /api/v1/auth/token/` con `refresh` actual<br>   - **Guardar nuevo `refresh` token** devuelto (reemplazar el anterior)<br>   - Reintentar request original con nuevo `access`<br>   - Si refresh falla (401/403) → limpiar sesión + redirect `/login`<br>2. **Logout (Header + LoginPage):**<br>   - Llamar `POST /api/v1/auth/logout/` con `{"refresh": <current_refresh>}`<br>   - Esperar 205 → limpiar `sessionStorage` + `queryClient.clear()` + redirect `/login`<br>3. **AuthContext:**<br>   - Eliminar lógica "sin refresh automático" (ahora sí hay refresh)<br>   - Manejar nuevo flujo: login → access + refresh → interceptor renueva automáticamente<br>4. **Storage:**<br>   - `access` en `sessionStorage` (clave `sgt.access`)<br>   - `refresh` en `sessionStorage` (clave `sgt.refresh`) — **NUEVO** (antes se descartaba) |
| **Archivos Candidatos** | `frontend/src/api/client.ts`, `frontend/src/api/endpoints/auth.ts`, `frontend/src/auth/AuthContext.tsx`, `frontend/src/auth/storage.ts`, `frontend/src/auth/jwt.ts`, `frontend/src/features/auth/LoginPage.tsx`, `frontend/src/components/layout/Header.tsx`, `frontend/src/auth/guards.tsx` |
| **Validaciones Necesarias** | 1. Login → access + refresh guardados<br>2. Access expira → interceptor usa refresh → nuevo access + **nuevo refresh** guardado<br>3. Refresh anterior usado → 401 blacklisted<br>4. Logout → POST /auth/logout/ → 205 → sesión limpia → login page<br>5. Refresh token expirado (24h) → 401 → redirect login |
| **Dependencias Backend** | SEC-T003 completado (rotación, blacklist, logout endpoint, migraciones token_blacklist) + SEC-T004 (JWT_SIGNING_KEY separada) |
| **Criterios de Aceptación** | Flujo completo: login → acceso recurso → expiración access → refresh automático → nuevo access+refresh guardado → acceso OK → logout → sesión limpia |
| **Riesgos** | Cambio breaking en interceptor axios; coordinar deploy backend+frontend simultáneo |

---

### ADAPT-003 — Migración `archivo_path` → `download_url` (Serializers)

| Campo | Detalle |
|-------|---------|
| **Problema** | SEC-T009: Serializers `DocumentoEntregadoSerializer` y `DeclaratoriaAptitudSerializer` remueven `archivo_path`/`archivo_memorando_firmado_path` y exponen `download_url` opaco |
| **Dependencia** | SEC-T009 (Serializers) + DEC-006 (Endpoint download declaratoria implementado) |
| **Vistas Afectadas** | V-03 (Cargar documento), V-07 (Bandeja → Detalle → Descarga), V-08 (Detalle funcionario → Descarga documento/declaratoria) |
| **Cambios Requeridos** | 1. **Types/Interfaces:**<br>   - `DocumentoEntregado`: Remover `archivo_path`, añadir `download_url: string`<br>   - `DeclaratoriaAptitud`: Remover `archivo_memorando_firmado_path`, añadir `download_url: string`<br>2. **Componentes Descarga:**<br>   - `FileDownloadButton` / `DocumentoDescarga`: Usar `download_url` directamente en `<a href>` o `fetch` + `blob()`<br>   - Eliminar lógica que construía URL desde `archivo_path`<br>3. **Endpoints Descarga:**<br>   - `GET /api/v1/peticiones/{id}/documento/` → funciona sin cambios<br>   - `GET /api/v1/declaratorias/{id}/documento/` → **NUEVO** (DEC-006) |
| **Archivos Candidatos** | `frontend/src/api/types/models.ts`, `frontend/src/api/types/payloads.ts`, `frontend/src/features/expediente/DocumentoDescarga.tsx`, `frontend/src/features/bandeja/DetalleFuncionarioPage.tsx`, `frontend/src/features/solicitud/NuevaSolicitudPage.tsx`, `frontend/src/features/peticiones/SeguimientoPeticionPage.tsx` |
| **Validaciones Necesarias** | 1. GET `/api/v1/peticiones/{id}/documento/` → response incluye `download_url` (no `archivo_path`)<br>2. GET `download_url` + JWT → 200 PDF descarga<br>3. GET `/api/v1/declaratorias/{id}/` → response incluye `download_url` (no `archivo_memorando_firmado_path`)<br>4. GET `download_url` declaratoria + JWT → 200 PDF |
| **Dependencias Backend** | SEC-T009 completado + DEC-006 (endpoint `GET /api/v1/declaratorias/{id}/documento/` en `resoluciones/views.py`) |
| **Criterios de Aceptación** | Frontend usa `download_url` en todas las descargas; no hay referencias a `archivo_path` en código frontend |

---

### ADAPT-004 — Formato Errores Uniforme (Exception Handler Global)

| Campo | Detalle |
|-------|---------|
| **Problema** | SEC-T010: Nuevo `custom_exception_handler` → formato uniforme `{error: {code, message, details}}` para todos los códigos HTTP |
| **Dependencia** | SEC-T010 (Exception Handler) + DEC-009 (Mensaje 500 usuario final) |
| **Vistas Afectadas** | Todas (API Client, Error Boundary, Forms, Toast/Alerts) |
| **Cambios Requeridos** | 1. **API Client (`client.ts`):**<br>   - Actualizar `ApiError` type: `code`, `message`, `details`, `fieldErrors`<br>   - Parsear nuevo formato `response.data.error.{code, message, details}`<br>   - Mapear códigos: `validation_error` (400), `authentication_failed` (401), `permission_denied` (403), `not_found` (404), `throttled` (429), `server_error` (500)<br>2. **Error Boundary / ErrorState / Toast:**<br>   - Mostrar `error.message` al usuario (español institucional)<br>   - Usar `error.code` para lógica condicional (ej: redirect login si `authentication_failed`)<br>   - `details` para errores de campo en formularios (RFF-005)<br>3. **Formularios (React Hook Form + Zod):**<br>   - Parsear `details` → `fieldErrors` para `setError()` por campo<br>4. **Throttling (SEC-T002, SEC-T008):**<br>   - `code: "throttled"` + `message: "Demasiadas solicitudes. Intenta de nuevo en X minutos."` + `details: {retry_after: 45}` |
| **Archivos Candidatos** | `frontend/src/api/errors.ts`, `frontend/src/api/client.ts`, `frontend/src/components/feedback/ErrorState.tsx`, `frontend/src/components/feedback/ToastProvider.tsx`, `frontend/src/components/ui/Alert.tsx`, `frontend/src/lib/validation.ts`, `frontend/src/features/*/components/*.tsx` (formularios) |
| **Validaciones Necesarias** | 1. Cada código HTTP (400,401,403,404,429,500) retorna formato uniforme<br>2. `message` en español institucional, sin tecnicismos<br>3. `details` presente solo cuando aplica (validación campos, `retry_after`)<br>4. 500 sin stack trace, SQL, rutas internas |
| **Dependencias Backend** | SEC-T010 completado (custom_exception_handler + EXCEPTION_HANDLER registrado) |
| **Criterios de Aceptación** | Frontend parsea y muestra correctamente todos los formatos de error nuevos; deploy coordinado backend+frontend |

---

### ADAPT-005 — Endpoint `GET /api/v1/peticiones/{id}/` (BE-02)

| Campo | Detalle |
|-------|---------|
| **Problema** | Frontend V-06 y V-08 buscan petición en `expediente.peticiones[]` porque no existe `GET /api/v1/peticiones/{id}/` (BE-02) |
| **Dependencia** | BE-02 (Endpoint autorizado e implementado) |
| **Vistas Afectadas** | V-06 (Seguimiento Petición), V-08 (Detalle Funcionario → Petición) |
| **Cambios Requeridos** | 1. **API Client:** Añadir `getPeticion(id: string): Promise<PeticionDetalle>` en `endpoints/peticiones.ts`<br>2. **V-06 SeguimientoPeticionPage:** Reemplazar búsqueda en `expediente.peticiones[]` por llamada directa `getPeticion(peticionId)`<br>3. **V-08 DetalleFuncionarioPage:** Igual para acciones sobre petición específica<br>4. **Types:** Añadir `PeticionDetalle` type con campos completos (`requisito_codigo`, `requisito_nombre`, `estado_peticion`, `dependencia_emisora`, `documentos[]`, etc.) |
| **Archivos Candidatos** | `frontend/src/api/endpoints/peticiones.ts`, `frontend/src/features/peticiones/SeguimientoPeticionPage.tsx`, `frontend/src/features/bandeja/DetalleFuncionarioPage.tsx`, `frontend/src/api/types/models.ts` |
| **Validaciones Necesarias** | 1. GET `/api/v1/peticiones/{id}/` → 200 con detalle completo petición<br>2. V-06 y V-08 cargan datos vía endpoint directo (no búsqueda en expediente)<br>3. Fallback graceful si endpoint no disponible (mostrar "No disponible" + link a expediente) |
| **Dependencias Backend** | BE-02 autorizado e implementado (`GET /api/v1/peticiones/{id}/` en `peticiones/views.py`) |
| **Criterios de Aceptación** | V-06 y V-08 usan endpoint dedicado; fallback graceful si no disponible |

---

### ADAPT-006 — Checklist Estudiante (BE-04)

| Campo | Detalle |
|-------|---------|
| **Problema** | `GET /api/v1/expedientes/{id}/checklist/` retorna 403 para rol `ESTUDIANTE` (BE-04 no autorizado) |
| **Dependencia** | BE-04 (Permiso autorizado e implementado) |
| **Vistas Afectadas** | V-04 (Expediente y Requisitos — panel checklist) |
| **Cambios Requeridos** | 1. **Guarda/Componente:** Si BE-04 implementado, remover panel "No disponible para su rol" y renderizar `ChecklistPanel` normal para `ESTUDIANTE`<br>2. **API Client:** `getChecklist(expedienteId)` ya existe; solo cambiar manejo 403 → ya no debería ocurrir para estudiante propio<br>3. **UX:** Estudiante ve checklist de solo lectura (sin botones evaluar) |
| **Archivos Candidatos** | `frontend/src/features/expediente/ExpedientePage.tsx`, `frontend/src/features/expediente/ChecklistPanel.tsx`, `frontend/src/auth/guards.tsx` |
| **Validaciones Necesarias** | 1. `ESTUDIANTE` accede `GET /expedientes/{id}/checklist/` → 200 con checklist propio<br>2. `ESTUDIANTE` NO ve botones evaluar/observar (RBAC server-side) |
| **Dependencias Backend** | BE-04 autorizado e implementado (permiso `ESTUDIANTE` en `checklist` GET scope `own`) |

---

### ADAPT-007 — Catálogo Carreras (BE-10)

| Campo | Detalle |
|-------|---------|
| **Problema** | V-03 requiere `carrera_id` UUID manual; no hay catálogo carreras (BE-10) |
| **Dependencia** | BE-10 (Endpoint `GET /api/v1/carreras/` autorizado) |
| **Vistas Afectadas** | V-03 (Crear Solicitud) |
| **Cambios Requeridos** | 1. **API Client:** Añadir `getCarreras(): Promise<Carrera[]>` en `endpoints/carreras.ts` (nuevo)<br>2. **V-03 NuevaSolicitudPage:** Reemplazar input UUID manual por `Select` con opciones de `getCarreras()`<br>3. **Types:** Añadir `Carrera` type `{id: string, nombre: string, facultad_id: string}`<br>4. **Fallback:** Si BE-10 no disponible, mantener input UUID manual + V-09 |
| **Archivos Candidatos** | `frontend/src/api/endpoints/carreras.ts` (nuevo), `frontend/src/features/solicitud/NuevaSolicitudPage.tsx`, `frontend/src/features/solicitud/NuevaSolicitudForm.tsx`, `frontend/src/api/types/models.ts` |
| **Validaciones Necesarias** | 1. `GET /api/v1/carreras/` → 200 array carreras<br>2. V-03 muestra selector con nombres carreras (no UUID manual)<br>3. Selección → envía `carrera_id` UUID correcto |
| **Dependencias Backend** | BE-10 autorizado e implementado (`GET /api/v1/carreras/` en nuevo `carreras/views.py`) |

---

### ADAPT-008 — Perfil Usuario /me (BE-01)

| Campo | Detalle |
|-------|---------|
| **Problema** | Frontend decodifica `cedula` y `roles` del JWT; no tiene nombre, carrera, facultad (BE-01) |
| **Dependencia** | BE-01 (Endpoint `GET /api/v1/me/` o claims extendidos en JWT) |
| **Vistas Afectadas** | V-02 (Dashboard saludo), V-03 (Crear solicitud), V-04, V-05, V-06 |
| **Cambios Requeridos** | 1. **API Client:** `getMe(): Promise<UsuarioPerfil>` en `endpoints/auth.ts`<br>2. **AuthContext:** Al login, llamar `getMe()` y almacenar perfil completo (`nombre`, `carrera`, `facultad`, `cedula`, `roles`)<br>2. **Layout/Header:** Mostrar nombre completo en lugar de solo cédula<br>3. **V-03:** Pre-llenar carrera si perfil la trae (opcional) |
| **Archivos Candidatos** | `frontend/src/api/endpoints/auth.ts`, `frontend/src/auth/AuthContext.tsx`, `frontend/src/auth/useAuth.ts`, `frontend/src/components/layout/Header.tsx`, `frontend/src/features/dashboard/StudentDashboardPage.tsx` |
| **Validaciones Necesarias** | 1. `GET /api/v1/me/` → 200 con perfil completo<br>2. Header muestra nombre completo<br>3. Dashboard saludo personalizado |
| **Dependencias Backend** | BE-01 autorizado e implementado |

---

### ADAPT-009 — Campo `opcion_titulacion` (BE-06)

| Campo | Detalle |
|-------|---------|
| **Problema** | `opcion_titulacion` no existe en backend (BE-06 no autorizado); V-03 lo tiene condicionado (DEC-14) |
| **Dependencia** | BE-06 (Campo `opcion_titulacion` en expediente/petición autorizado) |
| **Vistas Afectadas** | V-03 (Crear Solicitud), V-04 (Expediente) |
| **Cambios Requeridos** | 1. **Types:** Añadir `opcion_titulacion` en `CrearExpedienteRequest`, `ExpedienteDetalle`<br>2. **V-03:** Añadir selector modalidad (condicionado a BE-06 + decisión humana DEC-14)<br>3. **V-04:** Mostrar `opcion_titulacion` en detalle expediente |
| **Archivos Candidatos** | `frontend/src/api/types/payloads.ts`, `frontend/src/api/types/models.ts`, `frontend/src/features/solicitud/NuevaSolicitudForm.tsx`, `frontend/src/features/expediente/ExpedientePage.tsx` |
| **Validaciones Necesarias** | 1. `POST /expedientes/` acepta `opcion_titulacion` opcional<br>2. `GET /expedientes/{id}/` retorna `opcion_titulacion` |
| **Dependencias Backend** | BE-06 autorizado + DEC-14 aprobada (modalidades validadas contra RRA-UNL) |

---

### ADAPT-010 — Motivo Observación en Respuestas (BE-07)

| Campo | Detalle |
|-------|---------|
| **Problema** | `motivo_observacion` no expuesto en respuestas `ExpedienteDetalle` / `PeticionInicializada` (BE-07) |
| **Dependencia** | BE-07 (Exponer `motivo`/`motivo_observacion` en respuestas) |
| **Vistas Afectadas** | V-04 (Expediente), V-08 (Detalle Funcionario) |
| **Cambios Requeridos** | 1. **Types:** Añadir `motivo_observacion` en `PeticionInicializada`, `ExpedienteDetalle` (nullable)<br>2. **V-04/V-08:** Mostrar motivo en UI cuando `estado_peticion = OBSERVADO` o `estado = OBSERVADA` |
| **Archivos Candidatos** | `frontend/src/api/types/models.ts`, `frontend/src/features/expediente/ExpedientePage.tsx`, `frontend/src/features/bandeja/DetalleFuncionarioPage.tsx` |
| **Validaciones Necesarias** | 1. `GET /expedientes/{id}/` incluye `motivo_observacion` en peticiones observadas<br>2. UI muestra motivo correctamente |
| **Dependencias Backend** | BE-07 autorizado e implementado |

---

## 3. Plan de Ejecución por Prioridad

| Sprint | Adaptaciones | Dependencias Backend | Entregable |
|--------|--------------|---------------------|------------|
| **Sprint 0** (Pre-producción) | ADAPT-001 (HTTPS/CSRF/Cookies) | SEC-T001 completado | Frontend listo para staging HTTPS |
| **Sprint 1** | ADAPT-002 (Rotación refresh + logout) | SEC-T003 completado | Auth flow actualizado |
| **Sprint 2** | ADAPT-003 (download_url) + ADAPT-004 (Errores uniformes) | SEC-T009, SEC-T010 completados | Descargas + Error handling actualizados |
| **Sprint 3** | ADAPT-005 (BE-02) + ADAPT-006 (BE-04) | BE-02, BE-04 autorizados | V-06, V-08, V-04 actualizados |
| **Sprint 4** | ADAPT-007 (BE-10) + ADAPT-008 (BE-01) | BE-10, BE-01 autorizados | V-03, V-02 mejorados |
| **Sprint 5** | ADAPT-009 (BE-06) + ADAPT-010 (BE-07) | BE-06, BE-07 autorizados | V-03, V-04, V-08 completados |

---

## 4. Criterios de Validación de Integración (Por Sprint)

| Sprint | Pruebas de Integración Backend-Frontend |
|--------|----------------------------------------|
| **Sprint 0** | 1. Login HTTPS → 200 + cookies Secure/HttpOnly + CSRF token<br>2. Request mutante sin CSRF → 403<br>3. Request mutante con CSRF → 200<br>4. Logout limpia cookies + sessionStorage |
| **Sprint 1** | 1. Login → access + refresh guardados<br>2. Access expira → interceptor refresh → nuevo access + **nuevo refresh** guardado<br>2. Refresh anterior → 401 blacklisted<br>3. Logout → POST /auth/logout/ → 205 → sesión limpia |
| **Sprint 2** | 1. Descarga documento usa `download_url` → 200 PDF<br>2. Descarga declaratoria usa `download_url` → 200 PDF<br>3. Errores 400/401/403/404/429/500 → formato uniforme `{error: {code, message, details}}`<br>4. Formularios muestran `details` por campo |
| **Sprint 3** | 1. V-06 usa `GET /peticiones/{id}/` directo → 200<br>2. V-04 checklist estudiante → 200 (no 403) |
| **Sprint 4** | 1. V-03 selector carreras → 200 + opciones<br>2. Header muestra nombre completo (perfil `/me`) |
| **Sprint 5** | 1. V-03 selector modalidad titulación funcional<br>2. V-04/V-08 muestran motivo observación |

---

## 5. Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Deploy backend+frontend desincronizado (ej. SEC-T003 rotación) | Media | Alto | Deploy coordinado obligatorio; feature flags si necesario |
| BE-02/BE-04/BE-10 no autorizados a tiempo | Media | Medio | Frontend con fallback graceful (V-09, input manual, datos decodificados JWT) |
| Cambio breaking en formato errores (SEC-T010) | Alta | Alto | Deploy coordinado backend+frontend; tests de contrato MSW actualizados |
| Frontend no actualiza `download_url` a tiempo (SEC-T009) | Baja | Medio | Backend mantiene `archivo_path` temporalmente (deprecation window) |
| Cookies seguras + CSRF en staging no funcionan | Media | Alto | Verificar Nginx `proxy_cookie_flags`, `proxy_set_header X-Forwarded-For`, `CSRF_TRUSTED_ORIGINS` |

---

## 5. Checklist de Validación Final (Pre-Producción)

| Check | Descripción | Responsable | Estado |
|-------|-------------|-------------|--------|
| ☐ | Frontend build HTTPS + cookies seguras + CSRF funciona contra backend staging | FE Team | ⏳ |
| ☐ | Rotación refresh + logout + interceptor axios funcionan end-to-end | FE/BE Team | ⏳ |
| ☐ | `download_url` en todas las descargas (documentos + declaratorias) | FE Team | ⏳ |
| ☐ | Formato errores uniforme en todos los códigos HTTP | FE/BE Team | ⏳ |
| ☐ | `GET /peticiones/{id}/` implementado y usado en V-06/V-08 | BE/FE Team | ⏳ |
| ☐ | Checklist estudiante accesible (BE-04) | BE Team | ⏳ |
| ☐ | Catálogo carreras funcional en V-03 (BE-10) | BE Team | ⏳ |
| ☐ | Perfil `/me` funcional en Header/Dashboard (BE-01) | BE Team | ⏳ |
| ☐ | `opcion_titulacion` en expediente (BE-06 + DEC-14) | BE/FE Team | ⏳ |
| ☐ | `motivo_observacion` expuesto en respuestas (BE-07) | BE Team | ⏳ |
| ☐ | Tests de contrato MSW actualizados para todos los cambios | FE Team | ⏳ |
| ☐ | Suite E2E Playwright: Login → Expediente → Peticiones → Checklist → Informe → Declaratoria | FE Team | ⏳ |
| ☐ | Deploy staging backend+frontend coordinado verificado por QA | BE/FE/QA Team | ⏳ |

---

**Firma:** opencode AI Assistant  
**Fecha:** 2026-11-05  
**Estado:** Planificación completa — Pendiente autorización backend para BE-xx y autorización hardening para SEC-Txxx