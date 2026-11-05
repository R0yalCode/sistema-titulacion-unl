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

- Base `python:3.12-slim`; usuario no privilegiado `django`; instala requirements y requirements-dev; `CMD python manage.py runserver 0.0.0.0:8000`.

## Advertencia operativa (hallazgo AUD-P0-01)

El compose actual fija `DJANGO_SETTINGS_MODULE: config.settings.local` y `DEBUG: ${DEBUG:-1}`: **por defecto el contenedor corre en modo desarrollo con DEBUG activo y runserver**. Es funcional para demostración local, pero no debe exponerse más allá del entorno de desarrollo. El plan de mejora incluye `settings/production.py` + gunicorn.

## Uso

```bash
export POSTGRES_PASSWORD=… SECRET_KEY=…
docker compose up -d --build
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py seed_initial_data   # opcional, demo
# API: http://localhost:8000/api/v1/docs/
```

## Volúmenes

| Volumen | Contenido |
|---|---|
| `postgres_data` | Base de datos |
| `media_data` | PDFs privados (`/app/backend/media`) |
| `static_data` | Estáticos de Django Admin |
