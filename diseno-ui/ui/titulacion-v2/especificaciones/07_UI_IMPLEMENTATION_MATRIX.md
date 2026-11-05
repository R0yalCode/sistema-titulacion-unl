# 07 · Matriz de trazabilidad visual ↔ backend (SGT-SIAAF)

**Versión:** 1.2.0 · **Fecha:** 2026-11-04 · **Estado:** Referencia no normativa de dependencias entre lo visual y el backend real (backend **no modificable**: openapi.yaml, permisos, modelos y migraciones fuera de alcance; la spec de backend existente es `specs/001-tramite-titulacion/` — una futura `specs/004-*` es referencia reservada y **aún no existe** en el repo). Los IDs y pares oficiales de las tareas están en `specs/003-frontend-titulacion/tasks.md`; los requisitos en `specify.md`.
Esta matriz cruza cada elemento visual de las 9 vistas con el estado real del backend (auditoría 003 + BE-01…BE-11 de `tasks.md` §2). Es la herramienta para decidir qué se implementa ahora (API-backed), qué se degrada (V-09/estado vacío) y qué queda **conceptual / bloqueado**.

Clave de clasificación (estandarizada en MOMENTO 2):
- **API-backed** — el endpoint existe y declara la operación en `openapi.yaml`: implementar con datos reales.
- **Frontend-only con datos reales** — computa la UI a partir de respuestas reales del backend (sin datos nuevos inventados).
- **Requiere ampliación del backend** — falta un dato/acción; implementable solo tras aprobar la dependencia (BE-x sin autorizar).
- **Conceptual** — existe solo en el prototipo; maqueta no funcional o **no** mostrar.
- **Solo visual** — decoración/estructura, sin comportamiento demandante de datos.
- **Bloqueado** — sin endpoint, sin autorización o sin contrato (**no se simula**).

## 7.1. Matriz por vista

> Revisión MOMENTO 2 (2026-11-04): toda fila fue contrastada contra `backend/openapi.yaml` y, cuando correspondía, contra el código de permisos de solo lectura (`backend/src/apps/authentication/adapters/permissions.py`, `backend/src/apps/verificacion/adapters/views.py`). El 403 del checklist de pregunta al estudiante queda **RBAC por diseño** (opciones de roles: `SECRETARIO_ABOGADO`, `ANALISTA_APOYO`, `ADMINISTRADOR` — verificado).

| Vista | Elemento visual | Clasificación | Backend / API | Notas |
|---|---|---|---|---|
| V-01 Login | Formulario (usuario/contraseña) | **API-backed** | `POST /auth/token/` | JWT local vigente (doc 06 §6.1); sin SAC. El OpenAPI declara solo `200` con "No response body"; SimpleJWT devuelve `{access, refresh}` (INC-13) — en V-01 se guarda **solo `access`** (Corrección MOMENTO 2, ver doc 06 §6.3) |
| V-01 | Botón "Ingresar con SAC" | Conceptual | N/A | Futuro OAuth2/OIDC; no mostrar hoy |
| V-01 | Área con sesión activa | **API-backed** | `GET /auth/token/derivación del JWT` | Derivación de roles del access. La renovación no existe: re-login al expirar (BE-03 inexistente) |
| V-09 No habilitado | Tarjetas ciclo/créditos | Conceptual | N/A | Sin API de récord académico/SGA; solo maqueta no funcional o se ocultan |
| V-09 | Banner "no habilitado" + requisitos | **Frontend-only con datos reales** | Documentos/menú institucional | El contenido normativo real lo provee el backend o docs; sin datos ficticios |
| V-02 Dashboard | Datos del expediente | **API-backed** | `GET /expedientes/bandeja/` (scope own) | Ver expediente activo del estudiante; si no hay, estado vacío oficial (FE-T201) |
| V-02 | Barra de progreso (N/M) | **Frontend-only con datos reales** | Estados devueltos por el backend | Conteo calculado de estados; sin listas inventadas. Checklist GET es **operable** (denegado por RBAC = por diseño; ver 7.2) |
| V-02 | Contadores "Mis solicitudes"/"Peticiones" | **Frontend-only con datos reales** | `GET /expedientes/bandeja/` | Contar de la respuesta real del expediente/lista |
| V-03 Crear solicitud | Stepper | **Solo visual** | N/A | Estructura de UI simple |
| V-03 | Tarjetas de opciones (TIC/Complexivo/Emprendimiento) | **Conceptual (DEC-14 corregida)** | `POST /expedientes/` (`carrera_id`) | Creador real con `carrera_id` (sin catálogo, BE-10). Opciones TIC/Complexivo: **hipótesis del análisis secundario, pendientes de validación del RRA-UNL**; "Emprendimiento": **no confirmado** — no se muestra. Selector **no implementable hoy** (pendencia de decisión humana + BE-06 + contrato aprobado; BE-06 NO es autorización de modificar backend) — ver `specify.md` §9.2 |
| V-03 | Enviar `carrera_id` | **API-backed** | `POST /expedientes/` | UUID obligatorio validado cliente |
| V-04 Expediente | Tabla de requisitos (checklist) | **API-backed** (roles autorizados) | `GET /expedientes/{id}/checklist/` | El 403 al estudiante es **RBAC por diseño** (verificado en `permissions.py`: GET solo para SECRETARIO/ANALISTA/ADMIN) — UI degradada con `ForbiddenState` (FE-T407; ver 7.2) |
| V-04 | Datos del expediente + timeline | **API-backed** | `GET /expedientes/{id}/` | Timeline inferido del estado actual (sin historial por endpoint) |
| V-04 | Botón "Enviar" / "Subsanar" | **API-backed** | `POST /expedientes/{id}/enviar/`, `POST /checklist/{id}/subsanar/` | 400 estado inválido; 422 requisitos incompletos |
| V-04 | Botón "Solicitar emisión" | **API-backed** | `POST /peticiones/{id}/solicitar-emision/` | Solo si estado = PENDIENTE y rol lo permite |
| V-04 | Badges de estado | **Frontend-only con datos reales** | enum `estado` del backend | Mapear enum real (PENDIENTE, SOLICITADO, CARGADO…); docs 01/03 |
| V-05 Modal petición | Dropzone de archivo | **API-backed** | `POST /peticiones/{id}/documento/` | Validar tipo/tamaño (PDF, 10 MB) antes de enviar (RFF-005) |
| V-05 | Textarea "Motivo" | Conceptual | N/A | No existe campo `motivo` en DB; no renderizar como campo real |
| V-05 | Continuar y registrar "crear petición" | **Bloqueado** | — | No hay endpoint de creación manual: la petición se genera al crear el expediente; UI lo explica (CA-V05-05) |
| V-06 Seguimiento | Timeline de estados | **Frontend-only** (inferido) | estado actual de la petición (desde `GET expedientes/{id}/`) | Sin `GET /peticiones/{id}/` ni historial: inferir del estado; nunca inventar hitos futuros. Depende de BE-02 para detalle |
| V-06 | Estado "En revisión" | Conceptual | N/A | No existe en el enum del backend: solo estados reales devueltos |
| V-06 | Descarga de documentos | **API-backed** | `GET /peticiones/{id}/documento/` y `/{version}/` | Con `Authorization` + blob; vigente o versión conocida |
| V-07 Bandeja | Tabla de datos | **API-backed** | `GET /expedientes/bandeja/` | Scope por rol (token); roles sin expedientes → lista vacía |
| V-07 | Filtros/búsqueda | **Frontend-only con datos reales** | misma respuesta | Etiquetar "filtra la página actual" si no hay soporte server-side; sin páginas inventadas |
| V-08 Detalle | Evaluar checklist / observar / informe / declaratoria | **API-backed** | `PUT /checklist/{id}/`, `POST /expedientes/{id}/observar/`, `POST /informes/`, `POST /declaratorias/` | Por rol/estado (RBAC por diseño); sin acciones no permitidas |
| V-08 | Datos del estudiante (email/ciclo) | **Requiere ampliación del backend** | N/A | La API no anida el perfil completo: mostrar solo campos reales recibidos |
| V-08 | Dropzone de archivos | **Solo visual / Solo lectura** | — | Panel de lectura; cargar documentos solo en V-05 (roles de carga) |
| V-08 | Historial de acciones | Conceptual | N/A | Sin endpoint de historial: ocultar o estado vacío con texto real |
| Transversal | Estados 404/403/401/500/503 | **API-backed** (códigos DRF estándar de facto) | errores del cliente API | Doc 08; 401 aviso+`/login`, 403 `ForbiddenState`+V-09, 404 página + estados, 5xx `ErrorState`. La ausencia en OpenAPI no impide recibirlos (CL-22) |
| Transversal | InlineAlert 409/412/428 | **Bloqueado** | **BE-11 (NO AUTORIZADA)** | Sin declaración de esos códigos ni mecanismo de versión; escenario propuesto; no implementar |
| Transversal | SAC / OAuth2 / OIDC / TOTP | **Conceptual** | N/A | No existe; no inventar (doc 06 §6.4) |
| Transversal | Renovación automática de sesión | **Bloqueado** | BE-03 (NO AUTORIZADA) | No hay endpoint de refresh: re-login (doc 06 §6.3) |

## 7.2. Correcciones respecto a versiones anteriores

- **INC-18 corregido (con verificación de código, MOMENTO 2):** `GET /expedientes/{expediente_id}/checklist/` **funciona** y está protegido por `HasRolePermission` + `ScopeFilterMixin`; la tabla de roles (`permissions.py`, recurso `checklist`) concede `GET` solo a `SECRETARIO_ABOGADO`/`ANALISTA_APOYO`/`ADMINISTRADOR`, por lo que el 403 al `ESTUDIANTE` es **RBAC por diseño**, no defecto. Consecuencia de UI correcta: RFF-404, `ForbiddenState`/vista degradada en V-04 (FE-T407).
- **INC-17 corregido:** el "endpoint demo" de versiones anteriores no existe; las referencias demo eran del prototipo A (V-01 con perfiles demo, solo visual). No hay semillas ni endpoints demo en el backend vigente.
- **DEC-14 reformulada (MOMENTO 2):** las opciones de titulación (TIC ordinaria; Examen Complexivo excepcional) pasan de "solo visual" a **hipótesis pendientes de validación del RRA-UNL** con el selector **condicionado** (decisión humana + BE-06 + contrato aprobado); "Proyecto de Emprendimiento" **no confirmado** (no se muestra). Ver `specify.md` §9.2.
- **Almacenamiento de tokens (MOMENTO 2):** en V-01 se persiste **solo `access`**; el `refresh` se recibe y descarta (BE-03 inexistente) — corrige la redacción anterior "access y refresh".
- Los colores rojo/azul del kit B (errores) están documentados como **observados** (doc 01 §1.1) y no como institucionales.

## 7.3. Referencias

- Backend (no tocar): `backend/openapi.yaml` (declara solo `200`; los errores estándar DRF ocurren de facto — CL-22), permisos en `backend/src/apps/authentication/adapters/permissions.py` (solo lectura), migraciones.
- SDD: `specs/003-frontend-titulacion/specify.md` §9.2, §9.3; `clarify.md` DEC-13, DEC-14, B-03, B-06, B-11, PQ-13.
- Tareas y dependencias BE: `specs/003-frontend-titulacion/tasks.md` §2 (BE-01…BE-11) y matriz §17.
