---
system: SGT-SIAAF
type: operations
status: verified
source: repository-config
last_verified: 2026-11-23
---

# Entornos

| Entorno | Settings Django | Cómo se levanta | Particularidades |
|---|---|---|---|
| Desarrollo | `config.settings.local` | `docker compose up` (backend en `:8000` vía Nginx) + `npm --prefix frontend run dev` (`:5173`) | `DEBUG=1` por defecto; CORS de desarrollo pendiente (BE-08) |
| Pruebas | `config.settings.test` | `pytest` (backend), `npm run test` (frontend, jsdom + MSW) | jsdom fija `innerWidth=1024` y no implementa `matchMedia` (D-FE-01) |
| Producción | `config.settings.production` | `docker compose -f docker-compose.prod.yml -p sgt-siaaf-prod up` | HTTPS, HSTS, CSP report-only, cookies seguras; Swagger restringido; logs JSON en `LOG_DIR` |

Todos los datos son ficticios (simulación académica); en desarrollo, el perfil académico usa `MockSGAAdapter`. MockSGA está prohibido en producción y no existe un adaptador real del SGA. **Nunca** apuntar a BD productivas del SGA/SIAAF (RN-012).

## Desarrollo frente a producción

| | Desarrollo (`docker-compose.yml`) | Producción (`docker-compose.prod.yml`) |
|---|---|---|
| Settings | `config.settings.local` (`DEBUG`) | `config.settings.production` |
| Servidor | `runserver`, migraciones manuales | Gunicorn, `migrate` automático en el arranque |
| HTTPS y cookies | HTTP local; cookie de confianza sin `Secure` | HTTPS obligatorio, HSTS, cookies `Secure` |
| Clave del 2FA | Derivada de `SECRET_KEY` si falta | `MFA_ENCRYPTION_KEYS` obligatoria |
| Correo | Consola (log del backend) | SMTP con TLS, validado al arrancar |
| Documentos | `backend/src/media`, **fuera** del volumen `media_data` | `backend/media`, en el volumen `media_private_prod` |
| Swagger y ReDoc | Abiertos | Solo `IsAdminUser` |
| Identidad de la base | `registrar_entorno_bd desarrollo`, manual y una vez | `produccion`, registrada al arrancar |

## Variables de configuración

La mayoría de las variables del backend están documentadas, sin valores secretos, en `backend/.env.example`. No figuran allí `POSTGRES_*` ni `PUBLIC_BASE_URL`, que usa Compose, ni `ACADEMIC_PROFILE_*` y `MFA_RESET_COOLDOWN_HOURS`, que tienen valor por defecto en settings. Nunca versione archivos `.env` ni copie en ellos valores reales de otros entornos.

> **Definir una variable no basta para que llegue al contenedor.** Cada Compose entrega solo las que enumera en `environment`. En `docker-compose.prod.yml` **no** están `AUTH_THROTTLE_RATE`, `PASSWORD_RESET_*`, `MFA_` de política, `LOG_DIR` ni `ACADEMIC_PROFILE_PROVIDER`, por lo que usan su valor por defecto.

| Variable | Uso |
|---|---|
| `SECRET_KEY` | Firma de Django (sesiones, CSRF, enlaces de recuperación). Obligatoria |
| `JWT_SIGNING_KEY` | Firma de los JWT. Obligatoria y **distinta** de `SECRET_KEY` |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Base de datos en Compose (el backend las recibe como `DB_NAME`, `DB_USER` y `DB_PASSWORD`) |
| `ALLOWED_HOSTS` | Hosts admitidos por Django (obligatoria en producción) |
| `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS` | Orígenes permitidos. Solo en producción; en desarrollo todo es mismo origen |
| `PUBLIC_BASE_URL` | URL HTTPS pública que se compila en el frontend de producción |
| `TRUSTED_PROXIES` | Proxies de confianza para obtener la IP real |
| `MFA_ENCRYPTION_KEYS` | Claves Fernet de los secretos TOTP. Admite varias separadas por comas: la primera cifra y todas descifran |
| `MFA_TRUSTED_DEVICE_DAYS`, `MFA_CHALLENGE_*`, `MFA_USER_*`, `MFA_THROTTLE_RATE`, `MFA_RESET_COOLDOWN_HOURS` | Política del 2FA |
| `AUTH_THROTTLE_RATE`, `PASSWORD_RESET_THROTTLE_RATE`, `PASSWORD_RESET_TIMEOUT` | Límites de intentos y vigencia de los enlaces |
| `EMAIL_*`, `DEFAULT_FROM_EMAIL`, `FRONTEND_BASE_URL` | Envío de correos y enlaces ([[USER_ACCESS_GUIDE]] §8). En producción, Compose toma `FRONTEND_BASE_URL` de `PUBLIC_BASE_URL` |
| `ACADEMIC_PROFILE_PROVIDER`, `ACADEMIC_PROFILE_MOCK_ALLOWED` | Fuente académica. En producción el mock está prohibido |
| `SEED_DEMO_PASSWORD` | Contraseña de `seed_initial_data`. El comando solo escribe en una base registrada como desarrollo o en la temporal de pytest ([[INITIAL_DATA]]) |

## Sesión

JWT `access` de 30 minutos. No existe renovación automática: al expirar, se vuelve a ingresar. El cierre de sesión no invalida en el servidor un JWT ya emitido, que caduca por tiempo.

El frontend y la API comparten origen (`http://localhost:8000` en desarrollo). El frontend envía el JWT en `Authorization: Bearer`. La cookie de dispositivo de confianza es `HttpOnly` y solo viaja a `/api/v1/auth/`. La autenticación ocurre en dos pasos y nunca se emite un JWT sin el segundo factor. Los roles se leen de `UserRole` y se evalúan en el servidor en cada operación.

## Clave de cifrado del 2FA

Genere una clave **independiente** de `SECRET_KEY`:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Para rotarla:

1. Anteponga la clave nueva: `MFA_ENCRYPTION_KEYS=<nueva>,<anterior>`.
2. Reinicie el servicio.
3. Ejecute `python manage.py rotate_mfa_keys`.
4. Retire la clave anterior y reinicie.

Si se pierde una clave en uso, los autenticadores que cifraba deben registrarse de nuevo. Detalle: `docs/autenticacion/politica-2fa.md`.

## Controles de seguridad implementados

- Contraseñas con los hashers de Django.
- Límites de intentos por IP y bloqueo del 2FA por cuenta.
- Secretos TOTP cifrados.
- Retos, tokens de confianza y códigos de recuperación guardados solo como hash.
- Filtro que enmascara datos sensibles en los logs.
- RBAC con filtrado por ámbito.
- PDF validados (cabecera `%PDF-`, SHA-256, ≤ 10 MB) y almacenados de forma privada.
- Auditoría de eventos del trámite y de autenticación.
- Safety, Bandit y Gitleaks en CI.

Detalle: [[DOCKER]] · [[INITIAL_DATA]] · [[USER_ACCESS_GUIDE]] · [[TROUBLESHOOTING]].
