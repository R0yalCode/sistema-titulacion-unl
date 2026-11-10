---
title: "Docker"
---

# Docker y Docker Compose

## Servicios (`docker-compose.yml`)

| Servicio | Imagen | Notas |
|---|---|---|
| `db` | postgres:16 | Healthcheck `pg_isready`; volumen `postgres_data`; contraseña obligatoria por entorno |
| `backend` | build local (Dockerfile) | Depende de `db` healthy; volúmenes `media_data` y `static_data` |
| `nginx` | nginx:1.24-alpine | Puerto 8000→80; configura `./nginx/nginx.conf` |

## Dockerfile

Multi-stage (SEC-T001, 2026-11-05) con dos targets, en el mismo archivo
para no duplicar las etapas comunes de instalación de dependencias:

| Target | Uso | Usuario | Servidor |
|---|---|---|---|
| `development` | `docker-compose.yml` (este, por defecto) | `django` | `runserver` |
| `production` | `docker-compose.prod.yml` | `appuser` (UID 1000) | `gunicorn` vía `entrypoint.sh` |

`docker-compose.yml` fija explícitamente `target: development` — sin esa
línea, un build multi-stage construye por defecto la **última** etapa
(`production`), lo que habría roto silenciosamente el flujo de desarrollo.

## Advertencia operativa (hallazgo AUD-P0-01) — resuelta para producción

El compose de **desarrollo** sigue fijando `DJANGO_SETTINGS_MODULE: config.settings.local` y `DEBUG: ${DEBUG:-1}` intencionalmente (es su propósito). Para producción real, usar `docker-compose.prod.yml` (`DJANGO_SETTINGS_MODULE: config.settings.production`, `DEBUG=False` fijo, gunicorn) — ver `despliegue.md`.

## Uso

```bash
export POSTGRES_PASSWORD=… SECRET_KEY=…
docker compose up -d --build
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py seed_initial_data   # opcional, demo
# API: http://localhost:8000/api/v1/docs/
```

## Volúmenes

| Volumen | Contenido | Compose |
|---|---|---|
| `postgres_data` | Base de datos | `docker-compose.yml` (dev) |
| `media_data` | PDFs privados (`/app/backend/media`) | `docker-compose.yml` (dev) |
| `static_data` | Estáticos de Django Admin | `docker-compose.yml` (dev) |
| `postgres_data_prod`, `media_private_prod`, `static_data_prod` | Equivalentes de producción, nombrados aparte para no colisionar con los de desarrollo | `docker-compose.prod.yml` |
