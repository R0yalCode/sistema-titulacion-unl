---
title: "Endpoints: Autenticación"
---

# Autenticación

Todas las rutas son públicas, usan `POST` y pertenecen al módulo `authentication`. `POST /api/v1/auth/token/` se retiró (AUTH-B).

| Ruta (`/api/v1/auth/…`) | Cuerpo | Resultado | Límite por IP |
|---|---|---|---|
| `login/` | `{email, password}` | `status` y, según el caso, `challenge` o JWT | `auth`, 5/min |
| `mfa/setup/` | `{challenge}` | QR y clave manual | `mfa`, 10/min |
| `mfa/setup/confirm/` | `{challenge, code, trust_device}` | JWT y códigos de recuperación | `mfa`, 10/min |
| `mfa/verify/` | `{challenge, code, trust_device}` | JWT | `mfa`, 10/min |
| `mfa/recovery/` | `{challenge, recovery_code}` | Nuevo reto de registro | `mfa`, 10/min |
| `mfa/reset/` | `{email, cedula, password}` | Respuesta genérica; envía un enlace si los datos coinciden | `password_reset`, 10/h |
| `mfa/reset/confirm/` | `{uid, token}` | Retira el autenticador | `password_reset`, 10/h |
| `password-reset/` | `{email}` | Respuesta genérica | `password_reset`, 10/h |
| `password-reset/validate/` | `{uid, token}` | Valida el enlace | `password_reset`, 10/h |
| `password-reset/confirm/` | `{uid, token, new_password}` | Cambia la contraseña | `password_reset`, 10/h |
| `logout/` | — | Revoca la confianza del dispositivo | `mfa`, 10/min |

## POST /api/v1/auth/login/

| Código | Cuerpo |
|---|---|
| 200 | `{ "status": "mfa_required" \| "mfa_setup_required", "challenge": string, "expires_in": number }` |
| 200 | `{ "status": "authenticated", "access": string, "refresh": string }`, solo con confianza vigente |
| 400 | Campo vacío o correo no institucional |
| 401 | `credenciales_invalidas` |
| 429 | Límite de intentos excedido |

El `access` incluye los claims `cedula` y `roles[]` y dura 30 minutos. Contrato completo: `backend/openapi.yaml`.
