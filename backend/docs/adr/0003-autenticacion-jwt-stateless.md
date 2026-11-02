# ADR-0003: Autenticación JWT Stateless (SimpleJWT)

- **Estado:** Aceptado
- **Fecha:** 21 de octubre de 2026
- **Tarea de origen:** `T008` en `tasks.md` v1.0.0
- **Sistema:** SGT-SIAAF — Backend de la Fase de entrega 1 (Unidad 1)

## Contexto

Las operaciones protegidas del backend requieren autenticación sin estado
server-side por petición (Constitución P-06) y el frontend web y la app móvil
deben consumir la misma API (P-13). El plan (`plan.md` § 6.2) ya evaluó y
seleccionó `djangorestframework-simplejwt` como mecanismo de emisión y
verificación de tokens para la API REST versionada `/api/v1/`.

## Decisión

1. Endpoint `POST /api/v1/auth/token/` (adaptador de
   `rest_framework_simplejwt.views.TokenObtainPairView`) que devuelve el par
   `access` (60 minutos) y `refresh` (24 horas).
2. Algoritmo `HS256` y clave de firma = `SECRET_KEY` del backend (vale
   igualmente el `SIGNING_KEY` por defecto); sin tokens en base de datos
   (stateless).
3. `REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES =
   "rest_framework_simplejwt.authentication.JWTAuthentication"` como
   autenticación por defecto de la API.
4. El payload del token incluye los claims estándar de SimpleJWT (`user_id`,
   `exp`, `jti`) más los claims propios del dominio: `cedula` y `roles`
   (obtenidos del modelo de `T007`).

## Justificación (plan.md § 6.2)

Estándar IETF RFC 7519; tokens stateless firmados con clave secreta HS256;
sin consulta de base de datos en cada petición; biblioteca compatible con el
ecosistema DRF.

## Consecuencias

- Positivas: autenticación verificable en el servidor sin sesiones; cliente
  web y móvil comparten el mismo mecanismo; los claims de rol quedan
  disponibles para el evaluador RBAC que se implementará en `T009`.
- Negativas: un `SECRET_KEY` comprometido permite falsificar tokens → gestión
  estricta de secretos por variable de entorno (C-012); la revocación
  individual de tokens no está contemplada por ADR dentro del MVP.
- La autorización (matriz rol × recurso × acción) sigue siendo
  responsabilidad del backend en cada operación; el presencia de un token
  válido no es autorización (`T009`/`T010`).

## Referencias

- `constitucion.md` — P-06, P-13, sección 7 (seguridad).
- `plan.md` — § 6.2 (Autenticación), § 15 y § 18.
- `specify.md` — `RNF-001` (autenticación JWT stateless).
- `tasks.md` — `T007` (modelo de usuario y roles), `T008`, `T009`, `T012`.
