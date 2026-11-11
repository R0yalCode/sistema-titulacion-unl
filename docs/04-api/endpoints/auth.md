---
title: "Endpoints: Autenticación"
---

# Autenticación

## POST /api/v1/auth/token/

Obtiene el par de tokens JWT con credenciales. **Sin parámetros de ruta ni de consulta.**

- **Cuerpo**: `{ "username": string (obligatorio), "password": string (obligatorio) }`
- **Respuestas**:

| Código | Cuerpo |
|---|---|
| 200 | `{ "access": string, "refresh": string }` — `access` incluye claims `cedula` y `roles[]` |
| 401 | `{ "detail": "No active account found with the given credentials" }` |

- **Seguridad**: endpoint público (login). Throttling 5/min por IP real (`TrustedProxyScopedRateThrottle`, ámbito `auth`, SEC-T002); excederlo responde 429.
- **Módulo**: authentication (`TokenPairView`).

Ejemplo:

```json
// 200 OK
{
  "access": "eyJhbGciOiJIUzI1NiIs…",
  "refresh": "eyJhbGciOiJIUzI1NiIs…"
}
```
