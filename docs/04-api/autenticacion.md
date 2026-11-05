---
title: "API — Autenticación"
---

# Autenticación de la API

## Esquema

JWT Bearer (SimpleJWT, HS256). El esquema se declara en el contrato OpenAPI (`securitySchemes`) y todas las operaciones de negocio lo requieren salvo el login.

## Obtener tokens

`POST /api/v1/auth/token/`

**Cuerpo** (`application/json`):

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `username` | string | Sí | Nombre de usuario institucional |
| `password` | string | Sí | Contraseña |

**Ejemplo de solicitud**:

```json
{ "username": "estudiante.demo", "password": "…" }
```

**200 OK**:

```json
{
  "access": "eyJhbGciOi…",   // 60 minutos; claims: cedula, roles[]
  "refresh": "eyJhbGciOi…"    // 24 horas
}
```

**401 Unauthorized**: credenciales inválidas → `{"detail": "No active account found with the given credentials"}`.

## Uso del token

```
Authorization: Bearer <access>
```

## Vigencia y renovación

| Token | Vigencia | Rotación |
|---|---|---|
| access | 60 min | No |
| refresh | 24 h | No (`ROTATE_REFRESH_TOKENS=False`) |

No existe endpoint de refresh expuesto en las rutas actuales (el frontend aún no lo consume — dependencia BE-03). No hay blacklist (ver AUD-P2-04 en el informe de auditoría).

## Errores de autenticación

| Situación | HTTP |
|---|---|
| Sin token / token expirado / firma inválida | 401 |
| Token válido pero rol sin celda en la matriz RBAC | 403 |
