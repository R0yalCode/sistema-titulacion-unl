---
title: "Ejecución"
---

# Ejecución — SGT-SIAAF

**Fuente:** `README.md`, `docker-compose.yml`, `docker-compose.prod.yml`, verificado en Fases 0, 3 y 8. No se ejecutó `docker compose up` en esta sesión de auditoría (no se levantó el stack completo en contenedores); la Fase 7 ejecutó el backend y el frontend directamente con Python/Node en el entorno de esta sesión, sin Docker — ver `DOCUMENTACION/07_PRUEBAS/RESULTADOS_VALIDACION.md` §1 para esa decisión metodológica.

## 1. Arranque — desarrollo

```bash
docker compose up --build -d
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py seed_initial_data
```

Resultado esperado (según `README.md` y `docker-compose.yml`, no verificado con ejecución real en esta fase): tres contenedores (`db`, `backend`, `nginx`), backend sirviendo con `runserver` (ver `ARQUITECTURA_DOCKER.md` §1), Nginx expuesto en `localhost:8000`.

## 2. Arranque — producción

```bash
docker compose -f docker-compose.prod.yml -p sgt-siaaf-prod up -d
```

Requiere, a diferencia del compose de desarrollo: `.env.prod` con `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS` reales (sin valores por defecto), y certificados TLS montados en `./nginx/certs/fullchain.pem` y `privkey.pem` — sin ellos, Nginx no arranca (advertencia explícita en el comentario del propio `prod.conf`).

## 3. Acceso a la API en ejecución

| Interfaz | URL (desarrollo) |
|---|---|
| API REST | `http://localhost:8000/api/v1/` |
| Swagger UI | `http://localhost:8000/api/v1/docs/` |
| ReDoc | `http://localhost:8000/api/v1/redoc/` |
| Healthcheck | `http://localhost:8000/health/` |
| Django Admin | `http://localhost:8000/admin/` |

## 4. Comandos de administración frecuentes (documentados en `README.md`)

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py seed_initial_data
docker compose exec backend python manage.py spectacular --file openapi.yaml
```

## 5. Apagar el entorno

No documentado explícitamente en `README.md` más allá del uso estándar de Docker Compose (`docker compose down`); no se añade aquí un procedimiento no verificado contra el proyecto.

## 6. Nota de alcance de esta auditoría

Esta página documenta el procedimiento **tal como está declarado** en los archivos del proyecto. Si se requiere una verificación empírica completa (levantar el stack, confirmar que los tres contenedores quedan `healthy`, probar el flujo FL-01→FL-05 vía HTTP real), es una actividad que implica ejecutar infraestructura con efectos más amplios que correr una suite de pruebas local (red de contenedores, Postgres persistente, puertos del host) — se solicitaría autorización explícita adicional al usuario antes de realizarla, siguiendo el mismo criterio aplicado en la Fase 7 para la ejecución de pruebas.
