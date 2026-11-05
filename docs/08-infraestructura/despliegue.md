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
4. (Opcional demo) `seed_initial_data`
5. Verificar `http://localhost:8000/api/v1/docs/`

## Requisitos para un despliegue real (pendientes — ver plan de mejora)

1. `settings/production.py` con: `DEBUG=False`, `ALLOWED_HOSTS` explícitos, `SECURE_SSL_REDIRECT`, `HSTS`, cookies seguras, CORS explícito, logging.
2. Servidor WSGI (gunicorn) + workers; `CMD` del Dockerfile actualizado.
3. Throttling habilitado.
4. Backups automáticos de PostgreSQL y del volumen `media_data`, con restauración probada.
5. Healthcheck de la aplicación (p. ej. endpoint de estado o `check --deploy`).
6. Colección de estáticos (`collectstatic`) en el pipeline de imagen.
7. Restricción de los endpoints de documentación (`/schema/`, `/docs/`, `/redoc/`) o de las cuentas demo.

Estos pasos **no se ejecutaron** durante la auditoría (no es una tarea de implementación); quedan como plan MEJ-P0-01.
