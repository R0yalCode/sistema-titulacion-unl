# Flujo de autenticación — SGT-SIAAF

> Estado: **implementado y probado** en la rama `build/reorganizacion-estructural` (2026-11-18). Tareas AUTH-A…AUTH-E.
> Autenticación **propia** con segundo factor TOTP (Google Authenticator). No existe integración con el SAC/CAS de la UNL (ver `arquitectura-cas.md`).

## 1. Responsabilidades separadas

| Responsabilidad | Dónde vive | Notas |
|---|---|---|
| Identidad (correo institucional + contraseña) | `apps/authentication/services/identity_providers.py` (`LocalIdentityProvider`) | Busca la cuenta por `email` (sin distinguir mayúsculas) y autentica su `username` con `ModelBackend`; puerto `ports/identity_provider.py`; futuro `CasIdentityProvider` |
| Segundo factor TOTP | `apps/authentication/services/mfa.py` | `pyotp`, secreto cifrado con MultiFernet |
| Confianza del dispositivo (5 días) | `TrustedDevice` + cookie HttpOnly | Ver `politica-2fa.md` |
| Sesión | JWT de SimpleJWT (access 30 min) | Solo se emite tras el segundo factor |
| Autorización | `RBAC_MATRIX` + `HasRolePermission` en cada endpoint | Roles leídos de la BD al emitir el JWT; nunca de React |

## 2. Secuencia

```text
Usuario ──► /            Landing pública ──► «Ingresar al sistema» ──► /login
/login   ──► POST /api/v1/auth/login/ {email, password}   (solo @unl.edu.ec)
              │
              ├─ 400 email/password: campo requerido o dominio no institucional
              ├─ 401 credenciales_invalidas (genérico, auditado; también correo no registrado)
              ├─ status=authenticated     (solo con cookie de confianza vigente)
              ├─ status=mfa_setup_required + challenge (sin autenticador activo)
              └─ status=mfa_required      + challenge (autenticador activo)

mfa_setup_required:
  POST /auth/mfa/setup/ {challenge}            → QR SVG + clave manual (no-store)
  (Google Authenticator escanea el QR y genera códigos de 6 dígitos)
  POST /auth/mfa/setup/confirm/ {challenge, code, trust_device}
              → status=authenticated + JWT + 10 códigos de recuperación (una sola vez)

mfa_required:
  POST /auth/mfa/verify/   {challenge, code, trust_device} → status=authenticated + JWT
  POST /auth/mfa/recovery/ {challenge, recovery_code}      → status=mfa_setup_required (reinscripción)

Cierre de sesión pedido por el usuario:
  POST /auth/logout/ → revoca la confianza del dispositivo y borra la cookie
```

Después de `authenticated`, React guarda el access token (como antes de AUTH-B) y redirige según el claim `roles`: roles operativos → `/bandeja`, `ESTUDIANTE` → `/estudiante`, sin rol reconocido → `/no-habilitado`. El backend vuelve a comprobar el rol en cada petición.

`POST /api/v1/auth/token/` **se retiró**: emitía el JWT solo con la contraseña.

## 3. Reto MFA

- Token aleatorio de 256 bits; el servidor guarda solo su SHA-256.
- 5 minutos de vigencia, de un solo uso, ligado al propósito (`SETUP` o `VERIFY`) y con un máximo de 5 intentos.
- En el frontend vive solo en el estado de React: nunca en `localStorage` ni en `sessionStorage`.
- Un reto caducado o agotado (`reto_mfa_invalido`) devuelve al formulario de credenciales.

## 4. Errores (sin información sensible)

| Código | HTTP | Significado |
|---|---|---|
| `credenciales_invalidas` | 401 | Usuario inexistente, contraseña errónea o cuenta inactiva (no se distinguen) |
| `codigo_mfa_invalido` | 400 | Código TOTP o de recuperación incorrecto |
| `reto_mfa_invalido` | 400 | Reto inexistente, caducado, consumido o agotado |
| `estado_mfa_invalido` | 400 | Operación incompatible con el estado del autenticador |
| `mfa_bloqueado` | 429 | 10 fallos de segundo factor en 15 minutos para la cuenta |
| (throttle DRF) | 429 | 5 inicios de sesión por minuto e IP; 10 por minuto e IP en `/mfa/*` |

## 5. Evidencias

- Backend: `test_mfa_totp.py` (32 casos) y `test_mfa_dispositivo_confianza.py` (12 casos); suite completa con 850 aprobadas y 13 omitidas.
- Frontend: `MfaFlow.test.tsx`, `signOut.test.tsx` y `LandingPage.test.tsx`; 458/458.
- E2E real por HTTP: `scripts/e2e/e2e_mfa.py` (17 comprobaciones superadas el 2026-11-18).

## 6. Inconsistencias registradas

- El rediseño previo del login (AUTH-RC) dejó 13 pruebas desalineadas. Se corrigieron en el commit de AUTH-RC.
- El `.venv` del repositorio está roto (no tiene pip ni Django). Las pruebas del backend se ejecutaron en la imagen Docker `sgt-siaaf-backend`.
- No se ejecutó la variante de pruebas con PostgreSQL (`config.settings.test_postgres`).

## 7. Acceso por correo institucional (2026-11-18)

- El formulario muestra «Nombre de usuario», pero el dato es el **correo institucional**. Solo se admite `@unl.edu.ec` (`INSTITUTIONAL_EMAIL_DOMAIN`).
- El correo se **normaliza** (quitar espacios y pasar a minúsculas) y se valida **en el frontend** (`features/auth/validation.ts`) **y en el backend** (`CorreoInstitucionalField` en `serializers.py`, que usa `domain/correo_institucional.py`). El backend es la autoridad.
- Se rechazan otros dominios, dominios parecidos (`unl.edu`, `mail.unl.edu.ec`, `unl.edu.ec.com`) y valores sin dominio.
- Mensajes exactos:
  - «El nombre de usuario es un campo requerido.»
  - «La contraseña es un campo requerido.»
  - «Ingrese un correo institucional válido (@unl.edu.ec).»
- No se migró `USERNAME_FIELD`. La migración `0003_acceso_correo_institucional` añade una restricción única de `email` que no distingue mayúsculas y excluye los correos vacíos.
- Para no revelar qué correos existen, un correo no registrado consume el mismo coste de hash y recibe el mismo 401.
- Cuentas demo: `sgtdemo.<usuario>@unl.edu.ec` (`seed_initial_data` completa el correo de las cuentas existentes sin cambiar contraseñas ni roles).
- Los roles salen de `UserRole` y `RBAC_MATRIX` de SGT-SIAAF, **no del SAC**. Destino por rol:
  - Roles operativos → `/bandeja`.
  - `ESTUDIANTE` → `/estudiante`.
  - `RESPONSABLE_DEPENDENCIA` → `/no-habilitado`: ese rol aún no tiene celdas en la matriz RBAC; es una brecha conocida.

## 8. Restablecimiento del doble factor (MFA-RST)

```text
/restablecer-2fa  ──► POST /auth/mfa/reset/ {email, cedula, password}
                       → 200 siempre con el mismo mensaje (throttle password_reset, 10/h por IP)
                       → si correo + cédula + contraseña coinciden, la cuenta tiene 2FA y no
                         está en espera tras un cambio de contraseña: enlace por correo
/restablecer-2fa/confirmar?uid&token ──► (botón) POST /auth/mfa/reset/confirm/
                       → retira autenticador, códigos y confianzas; el siguiente ingreso
                         pide registrar Google Authenticator
```

Detalle de seguridad y pendientes de la UNL en `politica-2fa.md` §6.
