---
title: "Despliegue"
---

# Despliegue

## Estado actual

| Aspecto | Realidad verificada |
|---|---|
| Modo | Desarrollo/demostración |
| Servidor | `runserver` (Dockerfile CMD) |
| DEBUG | `1` por defecto en el compose |
| Proxy | Nginx 1.24 en el puerto 8000 |
| CI/CD | No existe |
| Healthcheck de la app | No existe (solo el de PostgreSQL) |

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
| 3. Throttling habilitado | ⚠️ Parcial: carga de documentos sí (SEC-T008); login pendiente de SEC-T005/SEC-T002 |
| 4. Backups automáticos PostgreSQL/`media` | ❌ Sigue pendiente, fuera del alcance de SEC-T001 |
| 5. Healthcheck de la aplicación | ✅ Implementado (`GET /health/`, `HEALTHCHECK` en el Dockerfile) |
| 6. `collectstatic` en el pipeline | ✅ Implementado (`entrypoint.sh`) |
| 7. Restricción de `/docs/`, `/redoc/`, `/schema/` | ❌ Pendiente — es SEC-T013, siguiente tarea tras SEC-T001 |

### Archivos de producción

Viven en la raíz del repositorio, junto a los de desarrollo (decisión
registrada en `DECISION_LOG.md`, no en `backend/`):

- `Dockerfile` — multi-stage, target `production` (gunicorn, usuario `appuser` UID 1000, sin acceso de root).
- `docker-compose.prod.yml` — servicios `db`, `backend`, `nginx`; variables de entorno obligatorias sin valores reales.
- `nginx/prod.conf` — TLS + proxy; requiere montar certificados reales en `nginx/certs/` (no incluidos en el repositorio).
- `backend/entrypoint.sh` — `migrate` → `collectstatic` → `gunicorn`.

### Procedimiento

```bash
# 1. Definir variables reales (dominio, orígenes, contraseñas, claves) en
#    un .env.prod — nunca los valores de ejemplo de backend/.env.example.
export $(grep -v '^#' .env.prod | xargs)

# 2. Certificados TLS reales montados en ./nginx/certs/
#    (fullchain.pem, privkey.pem) — no provistos por este repositorio.

# 3. Nombre de proyecto propio para no colisionar con una instancia de
#    desarrollo en el mismo host:
docker compose -f docker-compose.prod.yml -p sgt-siaaf-prod up -d --build

# 4. Verificación
curl -k https://<dominio>/health/              # 200
curl -k https://<dominio>/api/v1/auth/token/   # 200/401 según credenciales
```

### Limitación conocida

El modo `Report-Only` de la Content-Security-Policy (DEC-010) no tiene,
en esta fase, un endpoint de recepción de reportes — las violaciones solo
son visibles manualmente (herramientas de desarrollador del navegador).
Backups automáticos y la restricción de Swagger/ReDoc (SEC-T013) quedan
como trabajo posterior, ya identificado arriba.
