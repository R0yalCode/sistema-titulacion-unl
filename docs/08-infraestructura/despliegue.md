---
title: "Despliegue"
---

# Despliegue

## Estado actual

| Aspecto | Realidad verificada |
|---|---|
| Modo | Desarrollo/demostración. **No existe un despliegue de producción** |
| Servidor en desarrollo | `runserver` (target `development`) |
| Servidor en producción | Gunicorn (target `production`), probado solo en ensayos aislados |
| DEBUG | `1` por defecto en `docker-compose.yml`; `False` en producción |
| Proxy | Nginx 1.24: puerto 8000 en desarrollo, 80 y 443 en producción |
| CI/CD | CI y controles de seguridad en GitHub Actions. **No hay despliegue automático** |
| Healthcheck de la app | Solo en `docker-compose.prod.yml` y en la imagen `production` |

**Pendiente antes de producción:** adaptador SGA real, certificados y dominio, SMTP institucional, backups y pruebas completas a través de Nginx en un navegador.

## Procedimiento actual (demostración local)

1. `export POSTGRES_PASSWORD=… SECRET_KEY=…`
2. `docker compose up -d --build`
3. `docker compose exec backend python manage.py migrate`
4. (Opcional demo) `seed_initial_data`, con la variable obligatoria `SEED_DEMO_PASSWORD` (ver `backend/README.md`)
5. Verificar `http://localhost:8000/api/v1/docs/`

## Despliegue de producción (SEC-T001, implementado 2026-11-05)

| Requisito (lista anterior) | Estado |
|---|---|
| 1. `settings/production.py` (`DEBUG=False`, `ALLOWED_HOSTS`, `SECURE_SSL_REDIRECT`, HSTS, cookies seguras, CORS, CSP) | ✅ Implementado (`backend/src/config/settings/production.py`) |
| 2. Servidor WSGI (gunicorn) + workers | ✅ Implementado (target `production` del `Dockerfile`, `entrypoint.sh`) |
| 3. Throttling habilitado | ✅ Implementado: carga de documentos (SEC-T008), login y flujo MFA (SEC-T002/SEC-T005) |
| 4. Backups automáticos PostgreSQL/`media` | ❌ Sigue pendiente, fuera del alcance de SEC-T001 |
| 5. Healthcheck de la aplicación | ✅ Implementado (`GET /health/`, `HEALTHCHECK` en el Dockerfile) |
| 6. `collectstatic` en el pipeline | ✅ Implementado (`entrypoint.sh`) |
| 7. Restricción de `/docs/`, `/redoc/`, `/schema/` | ✅ Implementado (SEC-T013): solo `IsAdminUser` en producción |

### Archivos de producción

Viven en la raíz del repositorio, junto a los de desarrollo (decisión
registrada en `DECISION_LOG.md`, no en `backend/`):

- `Dockerfile` — multi-stage, target `production` (gunicorn, usuario `appuser` UID 1000, sin acceso de root).
- `docker-compose.prod.yml` — servicios `db`, `backend`, `nginx`; variables de entorno obligatorias sin valores reales.
- `nginx/prod.conf` y `nginx/snippets/` — TLS, SPA, estáticos y proxy de la API; requiere montar certificados reales en `nginx/certs/` (no incluidos en el repositorio).
- `backend/entrypoint.sh` — `migrate` → registro de la base como `produccion` → `collectstatic` → `gunicorn`. Se detiene si la base está registrada como desarrollo.
- `backend/gunicorn.conf.py` — ruta de importación de `config` y parámetros del servidor.
- `backend/healthcheck.py` — healthcheck con un `Host` admitido por `ALLOWED_HOSTS`.

### Rutas y persistencia

| Dato | Ruta en el backend | Volumen | Quién lo sirve |
|---|---|---|---|
| Documentos | `/app/backend/media` | `media_private_prod` | Solo la API autenticada; Nginx responde 404 en `/media/` |
| Estáticos | `/app/backend/staticfiles` | `static_data_prod` | Nginx, en solo lectura desde `/var/www/static` |

Estas rutas se aplican solo a `config.settings.production`. En desarrollo,
`MEDIA_ROOT` sigue siendo `backend/src/media`, fuera del volumen `media_data`:
recrear el contenedor de desarrollo elimina los documentos subidos.

### Procedimiento

```bash
# 1. Definir variables reales (dominio, orígenes, contraseñas, claves) en
#    un .env.prod — nunca los valores de ejemplo de backend/.env.example.
#    Incluye PUBLIC_BASE_URL (URL HTTPS pública, sin barra final), que se
#    compila en el frontend y genera los enlaces de recuperación, y la
#    configuración SMTP. Use comillas simples en valores con caracteres
#    especiales.
set -a; . ./.env.prod; set +a

# 2. Certificados TLS reales montados en ./nginx/certs/
#    (fullchain.pem, privkey.pem) — no provistos por este repositorio.

# 3. Comprobar el proyecto y desplegar. Si el entorno o un .env seleccionan
#    otro nombre, la comprobación falla y `up` no se ejecuta:
[ "$(docker compose -f docker-compose.prod.yml config --no-interpolate | sed -n 's/^name: //p')" = "sgt-siaaf-prod" ] &&
  docker compose -f docker-compose.prod.yml -p sgt-siaaf-prod up -d --build

# 4. Verificación
curl -k https://<dominio>/health/              # 200
# La ruta de ingreso solo admite POST. Un cuerpo vacío confirma que responde,
# sin enviar credenciales:
curl -k -o /dev/null -w '%{http_code}\n' -X POST -H 'Content-Type: application/json' \
  -d '{}' https://<dominio>/api/v1/auth/login/  # 400
```

### Nombre del proyecto Compose

`docker-compose.prod.yml` declara `name: sgt-siaaf-prod`. El entorno de
desarrollo del puerto 8000 usa el proyecto `sgt-siaaf` y los mismos nombres de
servicio (`db`, `backend`, `nginx`): ejecutar el Compose de producción con ese
proyecto **reemplazaría sus contenedores**.

El nombre se resuelve en este orden, de mayor a menor prioridad:

1. Parámetro `-p`.
2. `COMPOSE_PROJECT_NAME`, del entorno o de un archivo `.env`.
3. `name:` del archivo Compose.
4. Nombre del directorio, que ya no se usa en producción.

`name:` evita el error de omitir `-p`, pero no es una protección absoluta. Por
eso toda operación (`up`, `down`, `build`, `restart`, `exec`) debe incluir
`-f docker-compose.prod.yml -p sgt-siaaf-prod`. El repositorio no tiene un
script de despliegue, así que esta regla y la comprobación del paso 3 son
manuales.

### Correo y enlaces de recuperación

La recuperación de contraseña y del 2FA necesita estas variables en `.env.prod`:

| Variable | Obligatoria | Valor o regla |
|---|---|---|
| `PUBLIC_BASE_URL` | Sí | Origen HTTPS público, sin ruta ni barra final. Su host debe figurar en `ALLOWED_HOSTS`. Compose lo entrega como `FRONTEND_BASE_URL` |
| `EMAIL_HOST` | Sí | Servidor SMTP. No admite `localhost` ni direcciones de loopback |
| `DEFAULT_FROM_EMAIL` | Sí | Dirección de correo válida |
| `EMAIL_PORT` | No | `587` |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | Juntas o ninguna | Credenciales SMTP. No las versione |
| `EMAIL_USE_TLS` | No | `1`. Producción no arranca si se desactiva |
| `EMAIL_TIMEOUT` | No | `10` segundos |
| `EMAIL_BACKEND` | No | Solo se admite `django.core.mail.backends.smtp.EmailBackend` |

Si falta un valor obligatorio o uno no cumple su regla, Compose o Django detienen
el arranque sin mostrar credenciales. Solo se admite STARTTLS: un servidor que
exija TLS implícito (puerto 465) no está soportado.

Si el servidor SMTP falla durante una solicitud, la API responde igual, para no
revelar si la cuenta existe, y el error queda en el log del backend. Nginx no
registra las rutas de los enlaces de recuperación, que contienen un token.

### Limitación conocida

El modo `Report-Only` de la Content-Security-Policy (DEC-010) no tiene,
en esta fase, un endpoint de recepción de reportes — las violaciones solo
son visibles manualmente (herramientas de desarrollador del navegador).
Los backups automáticos quedan como trabajo posterior, ya identificado arriba.
