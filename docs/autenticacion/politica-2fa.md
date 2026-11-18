# Política de segundo factor (2FA) — SGT-SIAAF

> Vigente desde 2026-11-18 (prototipo, autenticación propia). Valores configurables en `backend/.env.example`.

## 1. Conceptos que no deben confundirse

| Concepto | Duración | Dónde se controla |
|---|---|---|
| **Sesión** | JWT access de 30 min (`SIMPLE_JWT`) | Al caducar, se vuelve a iniciar sesión (no hay renovación automática) |
| **Reto MFA** | 5 min, 5 intentos | `MfaChallenge` (servidor) |
| **Confianza del dispositivo** | 5 días (`MFA_TRUSTED_DEVICE_DAYS`) | `TrustedDevice` (servidor) + cookie HttpOnly |
| **Vigencia del segundo factor** | Hasta revocar o restablecer el autenticador | `MfaDevice` |

## 2. TOTP (Google Authenticator)

- RFC 6238: 6 dígitos y periodo de 30 s. Tolerancia de ±1 periodo (`MFA_TOTP_VALID_WINDOW`); los códigos fuera de la ventana se rechazan.
- Secreto aleatorio de 160 bits (`pyotp.random_base32`), único por usuario.
- **Anti-reutilización:** se guarda el último periodo aceptado y se acepta solo uno posterior, con una actualización condicional para evitar carreras entre peticiones.
- El QR (`otpauth://`) se genera en el backend como SVG y se muestra solo durante el registro, con `Cache-Control: no-store`. No se persiste ni se registra en logs.
- MFA se activa solo después de verificar el primer código. Si el registro queda incompleto, se reanuda llamando de nuevo a `/mfa/setup/`, que genera un secreto nuevo.

## 3. Protección del secreto

- Se cifra con **MultiFernet** (AES-128-CBC + HMAC-SHA256) usando las claves de `MFA_ENCRYPTION_KEYS`, separadas por comas: la primera cifra y todas descifran.
- En producción la variable es obligatoria (`production.py`, `docker-compose.prod.yml`). En desarrollo, `local.py` deriva una clave de `SECRET_KEY`. En pruebas se genera una clave efímera.
- Sin clave válida, el sistema falla (`ImproperlyConfigured`): nunca guarda el secreto en texto plano.
- Nunca se devuelve el secreto después del registro ni se escribe en logs. El filtro `SensitiveDataFilter` enmascara `secret`, `totp`, `otp_code`, `recovery_code` y `challenge`.

### Rotación de claves

1. Generar una clave: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`.
2. Anteponerla: `MFA_ENCRYPTION_KEYS=<nueva>,<anterior>` y reiniciar el servicio.
3. Ejecutar `python manage.py rotate_mfa_keys` para recifrar todos los secretos.
4. Retirar la clave anterior y reiniciar.

Si se pierde una clave en uso, los secretos que cifraba no se pueden recuperar. Los usuarios afectados deben restablecer su 2FA (§6).

## 4. Fuerza bruta

- 5 intentos por reto; al agotarse, hay que volver a introducir la contraseña.
- Bloqueo por cuenta: 10 fallos de segundo factor en 15 minutos devuelven 429 `mfa_bloqueado`, con auditoría.
- Throttle por IP, consciente de `TRUSTED_PROXIES`: `auth` 5/min y `mfa` 10/min.

## 5. Confianza del dispositivo (5 días)

- Se concede solo si el usuario marca «Confiar en este dispositivo durante 5 días» al completar el TOTP.
- La cookie `sgt_trusted_device` lleva un token aleatorio de 256 bits y es `HttpOnly`, `SameSite=Strict`, `Secure` en producción, con `Path=/api/v1/auth/`.
- El servidor guarda **solo el hash**, la fecha de expiración y la revocación. React no puede leer la cookie ni cambiar su caducidad.
- Con la confianza vigente, el login no pide TOTP. **Al cumplirse los 5 días** se vuelve a pedir.

| Evento | Efecto |
|---|---|
| Cierre de sesión pedido por el usuario | **Siempre** revoca la confianza de ese dispositivo (decisión del responsable, 2026-11-18) |
| Expiración del JWT | No revoca la confianza (la sesión caduca; el dispositivo sigue reconocido) |
| Cambio de User-Agent con la misma cookie | Evento de riesgo: revoca y exige TOTP |
| Restablecimiento de contraseña | Revoca todas las confianzas del usuario |
| Restablecimiento del 2FA o uso de un código de recuperación | Revoca todas las confianzas |

## 6. Recuperación

- **Códigos de recuperación:** 10 códigos de un solo uso (`XXXXX-XXXXX`, alfabeto sin caracteres ambiguos), guardados con el hasher de contraseñas de Django y mostrados una sola vez. Usar uno **anula el autenticador anterior** y obliga a registrar uno nuevo en el mismo paso.
- **Sin códigos, por autoservicio (MFA-RST):** sigue la referencia `restablecer_doble_factor.png`.
  - **Solicitud:** correo institucional, cédula y contraseña actual. Solo sirven para **solicitar** un enlace de un solo uso que se envía al correo registrado. Nunca retiran el 2FA por sí mismos.
  - **Confirmación:** el 2FA se retira al confirmar ese enlace con un botón (POST), lo que requiere acceso al buzón.
  - **Validez del enlace:** está ligado a la contraseña y al autenticador vigentes; caduca en `PASSWORD_RESET_TIMEOUT` (1 h) y queda invalidado tras usarse o si cambia la contraseña.
  - **Antienumeración:** la respuesta es idéntica en todos los casos.
  - **Límite:** 10 solicitudes por hora e IP.
  - **Espera tras cambiar la contraseña:** después de restablecer la contraseña por correo, durante `MFA_RESET_COOLDOWN_HOURS` (72 h) se rechaza el restablecimiento del 2FA. Así, quien solo controle el buzón no puede anular ambos factores por el mismo canal.
  - **Auditoría:** `MFA_RESTABLECIMIENTO_SOLICITADO`, `MFA_RESTABLECIMIENTO_RECHAZADO` (con motivo) y `MFA_RESTABLECIDO`, sin correo, cédula, contraseña ni token.
- **Por soporte:** acción «Restablecer doble factor (2FA)» del admin de Django, o `restablecer_mfa` desde la consola. Hoy ninguna cuenta demo es `is_staff`, así que el admin no es utilizable.

**Pendiente de decisión de la UNL:**

1. **Canal del enlace:** la referencia del SAC lo envía al «correo personal». SGT-SIAAF solo almacena el correo institucional, que es a donde se envía hoy. Hace falta decidir si se incorpora un correo personal verificado y de dónde se obtiene (SGA o SAC).
2. **Aceptación formal** del procedimiento: correo, cédula y contraseña más el enlace, y la espera de 72 h.
3. **Verificación presencial** para quien no tenga acceso a su correo.
4. **Envío real:** SMTP institucional (hoy `EMAIL_BACKEND` de consola en desarrollo: el enlace aparece en `docker compose logs backend`).
- Ninguna petición no autenticada puede desactivar MFA.
- Todas las operaciones quedan en `EventoAutenticacion` (consulta de solo lectura en el admin).

## 7. Cuentas existentes y semillas

Las cuentas creadas por `seed_initial_data` también deben registrar Google Authenticator en su primer ingreso. No hay excepciones ni usuarios sin MFA.

## 8. Pendientes conocidos

- El JWT no se revoca en el servidor al cerrar sesión (no hay lista negra). Caduca a los 30 minutos.
- El access token sigue en `sessionStorage` (decisión previa a este trabajo). Lo que no está en el navegador son el secreto TOTP, el reto y la autoridad de confianza.
- La política de confianza bajo CAS se describe en `arquitectura-cas.md` §5.
