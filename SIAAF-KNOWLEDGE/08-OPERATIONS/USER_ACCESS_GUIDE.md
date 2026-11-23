---
system: SGT-SIAAF
type: operations
area: acceso
status: verified
source: verified-code
last_verified: 2026-11-23
---

# Guía de acceso al sistema

> Guía detallada trasladada del README. Las instrucciones de Google Authenticator para el usuario siguen en la sección 7 del `README.md`. Política técnica: `docs/autenticacion/politica-2fa.md`.

## 1. Correo institucional

En `http://localhost:8000/login`, el campo se llama **«Nombre de usuario»**, igual que en el SAC de la UNL. Debe escribirse el **correo institucional completo**: `usuario@unl.edu.ec`.

- Solo se admite `@unl.edu.ec`. Se rechazan Gmail, Hotmail, `unl.edu`, subdominios y otros dominios, con «Ingrese un correo institucional válido (@unl.edu.ec).».
- No importan las mayúsculas ni los espacios al inicio o al final.
- Campo vacío: «El nombre de usuario es un campo requerido.».

## 2. Contraseña

- Campo vacío: «La contraseña es un campo requerido.».
- Datos incorrectos: **«Usuario o contraseña incorrectos.»**, sin indicar cuál falló.
- Tras **5 intentos por minuto** desde la misma red se muestra «Demasiados intentos…».

## 3. Primer ingreso: configurar el segundo factor

Si la cuenta no tiene segundo factor, aparece **«Configurar verificación en dos pasos»** con un QR. Los pasos para el usuario están en el README, sección 7.

- El QR contiene la clave secreta y es **confidencial**.
- «¿No puede escanear el código?» muestra una clave para introducirla a mano.
- La verificación caduca a los **5 minutos** (`MFA_CHALLENGE_TTL_SECONDS`). Después se inicia sesión de nuevo y se genera otro QR.
- Al activar el 2FA se entregan **10 códigos de recuperación** que no se vuelven a mostrar.

## 4. Ingresos siguientes

Tras la contraseña aparece **«Verificación de seguridad (2FA)»**.

- Los códigos cambian cada **30 segundos** (`TOTP_INTERVAL = 30`).
- El servidor tolera un periodo de diferencia hacia cada lado (`MFA_TOTP_VALID_WINDOW = 1`).
- Cada código se acepta **una sola vez**.
- Tras **5 códigos erróneos** en el mismo intento, se vuelve a pedir la contraseña.
- Tras **10 fallos en 15 minutos**, la cuenta se bloquea temporalmente para el segundo factor.
- Con «Confiar en este dispositivo», ese navegador no pide código durante **5 días**. **Cerrar sesión revoca esa confianza**; la caducidad de la sesión no la revoca.

## 5. Acceso al panel

1. El backend emite la sesión (JWT de **30 minutos**).
2. Los permisos se obtienen de los **roles asignados en SGT-SIAAF** y de la matriz RBAC. **No** se consultan al SAC.
3. Redirección: **Estudiante** a `/estudiante`, **roles operativos** a `/bandeja` y **cuenta sin rol habilitado** a `/no-habilitado`.

## 6. Recuperación de contraseña

1. En `/login`, pulse **«Restablecer contraseña»** (`/recuperar-contrasena`).
2. Escriba el **correo registrado**.
3. El sistema responde siempre con el mismo mensaje, exista o no la cuenta.
4. Si la cuenta existe y está activa, envía un enlace a `/restablecer-contrasena?uid=…&token=…`, válido **1 hora** (`PASSWORD_RESET_TIMEOUT`) y de **un solo uso**.
5. Defina la nueva contraseña según la política de Django.
6. El cambio **revoca la confianza de todos los dispositivos**.

Límite: 10 solicitudes por hora desde la misma red.

## 7. Restablecimiento del segundo factor

Para quien no tiene el teléfono **ni** sus códigos de recuperación:

1. En `/login`, pulse **«Restablecer doble factor de autenticación (2FA)»** (`/restablecer-2fa`).
2. Complete **correo institucional**, **número de cédula** (10 dígitos) y **contraseña actual**, y pulse **«Restablecer el doble factor de autenticación (2FA)»**.
3. La respuesta es **siempre la misma**, para no revelar si los datos coinciden.
4. **Estos datos no retiran el 2FA por sí solos.** Si coinciden con una cuenta con 2FA activo, se envía al correo registrado un **enlace de un solo uso**, válido 1 hora, que deja de valer si cambia la contraseña.
5. En el enlace (`/restablecer-2fa/confirmar`), pulse **«Confirmar restablecimiento»**. Se retiran el autenticador, los códigos de recuperación y la confianza de todos los dispositivos.
6. Al iniciar sesión se muestra un **QR nuevo**. En la aplicación, borre la entrada antigua.

**Restricciones:**

- **Espera de 72 horas tras restablecer la contraseña** (`MFA_RESET_COOLDOWN_HOURS`), para que quien solo controle el buzón no anule ambos factores. Durante ese plazo no se envía el enlace, aunque la pantalla muestre el mensaje habitual.
- Límite de 10 solicitudes por hora desde la misma red.
- Todas las operaciones se auditan, sin guardar correo, cédula, contraseña ni enlace.
- Sin acceso al correo, un administrador puede usar la acción **«Restablecer doble factor (2FA) de los seleccionados»** en `/admin/`, tras verificar la identidad por un canal institucional. El procedimiento formal está pendiente de definición por la UNL.

## 8. Correos

- **Desarrollo:** no se envían. El mensaje y su enlace se escriben en el log del backend:

  ```bash
  docker compose logs backend | grep -A20 "Subject:"
  ```

- **Producción:** `docker-compose.prod.yml` entrega la configuración SMTP y usa `PUBLIC_BASE_URL` como `FRONTEND_BASE_URL`. El backend no arranca si falta `EMAIL_HOST` o `DEFAULT_FROM_EMAIL`, si el backend no es SMTP, si TLS está desactivado o si la URL no es un origen HTTPS admitido por `ALLOWED_HOSTS`. Detalle: `docs/08-infraestructura/despliegue.md`.
- **Fallos de envío:** la API responde igual para no revelar si la cuenta existe, y el error queda en el log del backend.
- **Registro de enlaces:** el Nginx de producción no registra las rutas de recuperación, porque contienen un token. El de desarrollo sí las registra.
- **Estado de la verificación:** el flujo se probó con un SMTP de ensayo con STARTTLS y autenticación. Falta probarlo con el servidor institucional.
- **Pendiente de la UNL:** la referencia del SAC envía el enlace del 2FA al «correo personal». SGT-SIAAF solo almacena el correo institucional, que es a donde lo envía hoy.

## 9. Decisiones pendientes de la UNL

Canal del enlace de restablecimiento del 2FA, aceptación formal del procedimiento, alternativa presencial y uso de la identidad visual del SAC en un servicio aún no integrado.

## Relacionado

[[PERMISSIONS_ROLES]] · [[ENVIRONMENTS]] · [[INITIAL_DATA]] · [[TROUBLESHOOTING]]
