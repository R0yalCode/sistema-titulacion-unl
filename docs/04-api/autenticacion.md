---
title: "API — Autenticación"
---

# Autenticación de la API

## Esquema

JWT Bearer (SimpleJWT, HS256). El esquema se declara en el contrato OpenAPI (`securitySchemes`) y todas las operaciones de negocio lo requieren salvo el login.

## Obtener tokens

El ingreso tiene dos pasos. El endpoint anterior, `POST /api/v1/auth/token/`, se retiró (AUTH-B) porque emitía el JWT solo con la contraseña.

### 1. Credenciales

`POST /api/v1/auth/login/`

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `email` | string | Sí | Correo institucional `@unl.edu.ec` |
| `password` | string | Sí | Contraseña |

| Respuesta | Significado |
|---|---|
| 200 `status=mfa_required` + `challenge` | Debe verificar el código TOTP |
| 200 `status=mfa_setup_required` + `challenge` | Debe registrar el autenticador |
| 200 `status=authenticated` + `access`, `refresh` | Cookie de confianza vigente |
| 400 | Campo vacío o dominio no institucional |
| 401 | Credenciales inválidas, sin indicar cuál falló |

### 2. Segundo factor

| Operación | Cuerpo |
|---|---|
| `POST /api/v1/auth/mfa/setup/` | `{challenge}`. Devuelve el QR y la clave manual |
| `POST /api/v1/auth/mfa/setup/confirm/` | `{challenge, code, trust_device}`. Devuelve JWT y 10 códigos de recuperación |
| `POST /api/v1/auth/mfa/verify/` | `{challenge, code, trust_device}`. Devuelve JWT |
| `POST /api/v1/auth/mfa/recovery/` | `{challenge, recovery_code}`. Obliga a registrar un autenticador nuevo |

Detalle del flujo: [`flujo-autenticacion.md`](../autenticacion/flujo-autenticacion.md).

## Uso del token

```
Authorization: Bearer <access>
```

## Vigencia y renovación

| Token | Vigencia | Rotación |
|---|---|---|
| access | 30 min | No |
| refresh | 24 h | No (`ROTATE_REFRESH_TOKENS=False`) |

No existe endpoint de refresh expuesto en las rutas actuales (el frontend aún no lo consume — dependencia BE-03). No hay blacklist (ver AUD-P2-04 en el informe de auditoría): `POST /api/v1/auth/logout/` revoca la confianza del dispositivo, pero no invalida un JWT ya emitido.

## Errores de autenticación

| Situación | HTTP |
|---|---|
| Sin token / token expirado / firma inválida | 401 |
| Token válido pero rol sin celda en la matriz RBAC | 403 |
