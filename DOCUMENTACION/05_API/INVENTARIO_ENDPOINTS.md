---
title: "Inventario de endpoints"
---

# Inventario de endpoints — API SGT-SIAAF

**Fuente:** `backend/src/config/urls.py` (leído íntegramente — 21 declaraciones `path()`, sin `DefaultRouter`), cruzado con `backend/openapi.yaml` y con `backend/src/apps/authentication/adapters/permissions.py` (`RBAC_MATRIX`) para la columna de permisos. Prefijo base: `/api/v1/`.

## 1. Endpoints de negocio (17 operaciones, igual cifra que reporta `docs/RESUMEN_EJECUTIVO.md`)

| # | Método | Ruta | Recurso | Objetivo | Auth | RF asociado |
|---|---|---|---|---|---|---|
| 1 | POST | `/api/v1/auth/token/` | Autenticación | Obtener par de tokens JWT (access+refresh) | No (es el login) | RNF-001 |
| 2 | POST | `/api/v1/expedientes/` | Expedientes | Crear expediente de aptitud legal | JWT | RF-001 |
| 3 | GET | `/api/v1/expedientes/bandeja/` | Expedientes | Bandeja operativa filtrada por rol/ámbito | JWT | HU-005 |
| 4 | GET | `/api/v1/expedientes/{id}/` | Expedientes | Detalle de expediente (filtrado por ámbito, 404 anti-IDOR) | JWT | — |
| 5 | POST | `/api/v1/expedientes/{id}/enviar/` | Expedientes | Envío formal, arranca plazo de 8 días | JWT | RF-002, RF-003 |
| 6 | GET | `/api/v1/expedientes/{expediente_id}/checklist/` | Verificación | Listar checklist de un expediente | JWT | RF-006 |
| 7 | PUT | `/api/v1/checklist/{id}/` | Verificación | Evaluar un requisito (VERIFICADO/OBSERVADO) | JWT | RF-006 |
| 8 | POST | `/api/v1/checklist/{id}/subsanar/` | Verificación | Subsanar documento observado | JWT | RF-008 |
| 9 | POST | `/api/v1/expedientes/{id}/observar/` | Verificación | Registrar observación accionable | JWT | RF-007 |
| 10 | POST | `/api/v1/informes/` | Resoluciones | Emitir informe legal de aptitud (#590) | JWT | RF-009, RF-010 |
| 11 | POST | `/api/v1/declaratorias/` | Resoluciones | Registrar declaratoria de aptitud (#162) | JWT | RF-011 |
| 12 | GET | `/api/v1/notificaciones/` | Notificaciones | Listar notificaciones del usuario (sin paginar, confirmado en `docs/04-api/convenciones.md`) | JWT | RF-012 |
| 13 | PATCH | `/api/v1/notificaciones/{id}/marcar-leida/` | Notificaciones | Marcar notificación como leída | JWT | RF-012 |
| 14 | POST | `/api/v1/peticiones/{id}/solicitar-emision/` | Peticiones | Solicitar emisión de certificado a dependencia | JWT | RF-004 |
| 15 | GET | `/api/v1/peticiones/{id}/documento/` | Peticiones | Descargar documento vigente | JWT | RF-007 (descarga) |
| 16 | POST | `/api/v1/peticiones/{id}/documento/` | Peticiones | Cargar/versionar documento PDF | JWT, `multipart/form-data` | RF-005 |
| 17 | GET | `/api/v1/peticiones/{id}/documento/{version}/` | Peticiones | Descargar una versión específica del documento | JWT | RF-005 (historial) |

## 2. Endpoints de infraestructura/documentación (4, fuera del conteo de negocio)

| Método | Ruta | Objetivo | Auth |
|---|---|---|---|
| GET | `/health/` | Healthcheck del contenedor (usado por `Dockerfile HEALTHCHECK`) | No |
| * | `/admin/` | Consola Django Admin (ADR-0009, solo staff/superuser) | Sesión Django, staff |
| GET | `/api/v1/schema/` | Esquema OpenAPI 3 crudo (JSON/YAML) | No (`AllowAny`, señalado como hallazgo P1 por `docs/RESUMEN_EJECUTIVO.md`) |
| GET | `/api/v1/docs/` | Swagger UI | No |
| GET | `/api/v1/redoc/` | ReDoc | No |

**Total: 21 declaraciones `path()` + el `admin.site.urls` (que internamente expande a muchas rutas adicionales no enumeradas aquí, por ser generadas por Django, no por el equipo).**

## 3. Validaciones y permisos por endpoint (resumen; matriz completa en `docs/auditoria-backend/MATRIZ_PERMISOS_ROLES.md` y en `DOCUMENTACION/01_ESPECIFICACION/ACTORES_Y_NECESIDADES.md` §4)

- Todos los endpoints de negocio exigen JWT válido (`Authorization: Bearer <token>`), excepto el propio login.
- Autorización evaluada contra `RBAC_MATRIX` (mundo cerrado: recurso/método no declarado ⇒ 403).
- Carga de documentos (#16): validación de magic bytes `%PDF-`, tamaño ≤10 MB, hash SHA-256 (`core/adapters/pdf_validation.py`).
- Descargas (#15, #17): semántica anti-IDOR — un objeto fuera de ámbito responde **404**, no 403 (decisión deliberada, documentada en `docs/04-api/convenciones.md`).

## 4. Hallazgo H-03 (resuelto en esta fase): duplicado confirmado de `openapi.yaml`

Se verificó con `diff` y `md5sum`: **`backend/openapi.yaml` y `backend/contracts/openapi.yaml` son archivos idénticos byte a byte** (mismo hash MD5, `diff` sin salida). Esto confirma, con evidencia directa (no solo por referencia a `auditoria/01`), que existe un duplicado real en el repositorio. No se elimina ningún archivo en este trabajo de documentación (regla 2.3); se reporta como hallazgo de higiene de repositorio para que el equipo del backend decida cuál ubicación es la canónica y retire la otra.
