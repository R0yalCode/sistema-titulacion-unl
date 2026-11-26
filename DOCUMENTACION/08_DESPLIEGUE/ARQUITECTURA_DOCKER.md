---
title: "Arquitectura Docker"
---

# Arquitectura de ejecución — Docker — SGT-SIAAF

**Fuente:** `Dockerfile` (raíz del repositorio), `docker-compose.yml`, `docker-compose.prod.yml`, `backend/entrypoint.sh`, `nginx/nginx.conf`, `nginx/prod.conf` — todos leídos íntegramente en esta Fase 8 (2026-11-06).

## 1. El `Dockerfile` es multi-stage con dos targets independientes

Esto es la corrección central de esta fase (ver nota en `DOCUMENTACION/03_ARQUITECTURA/C2_CONTENEDORES.md`, que contenía un error de la Fase 3 ya corregido):

```
FROM python:3.12-slim AS base        # dependencias comunes (requirements.txt)
FROM base AS development             # + requirements-dev.txt, CMD runserver
FROM base AS production              # + entrypoint.sh, ENTRYPOINT gunicorn
```

| Target | Usado por | Usuario del contenedor | Comando final | Dependencias instaladas |
|---|---|---|---|---|
| `development` | `docker-compose.yml` (`target: development`) | `django` (no root) | `CMD ["python","manage.py","runserver","0.0.0.0:8000"]` | `requirements.txt` + `requirements-dev.txt` |
| `production` | `docker-compose.prod.yml` (`target: production`) | `appuser` (UID/GID 1000, no root) | `ENTRYPOINT ["./entrypoint.sh"]` → `migrate` + `collectstatic` + `exec gunicorn config.wsgi:application --workers 4` | solo `requirements.txt` |

**Conclusión correcta (reemplaza la de la Fase 3):** el entorno de **desarrollo por defecto (`docker-compose.yml`) sí ejecuta el servidor de desarrollo de Django (`runserver`)**, con `DEBUG=1` por defecto. Solo el despliegue explícito de producción (`docker-compose.prod.yml`) usa Gunicorn. La afirmación original de `auditoria/01_AUDITORIA_GENERAL.md` sobre "servidor de desarrollo en contenedor" era correcta para el compose por defecto; lo que esa auditoría no decía es que **ya existe una alternativa de producción real y separada** (`docker-compose.prod.yml`), lista para usar.

## 2. Servicios por compose

### `docker-compose.yml` (desarrollo)

| Servicio | Imagen/build | Notas |
|---|---|---|
| `db` | `postgres:16` | Healthcheck `pg_isready`, volumen `postgres_data` |
| `backend` | build local, `target: development` | `DEBUG=${DEBUG:-1}` (por defecto **activado**), `DJANGO_SETTINGS_MODULE=config.settings.local`, `ALLOWED_HOSTS=localhost,127.0.0.1` fijo |
| `nginx` | `nginx:1.24-alpine` | Expone `8000:80`, proxy simple sin TLS (`nginx/nginx.conf`) |

### `docker-compose.prod.yml` (producción)

| Servicio | Imagen/build | Notas |
|---|---|---|
| `db` | `postgres:16` | Mismo patrón, volumen separado `postgres_data_prod` |
| `backend` | build local, `target: production` | **Todas** las variables sensibles son obligatorias sin default (`ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS`), `TRUSTED_PROXIES` con default de redes privadas RFC1918 |
| `nginx` | `nginx:1.24-alpine` | Expone `80:443`, redirección HTTP→HTTPS, TLS 1.2/1.3 (`nginx/prod.conf`), requiere certificados montados en `./nginx/certs/` (no incluidos en el repo, confirmado por el propio comentario del archivo) |

Ambos compose usan redes Docker bridge aisladas (`backend_net` / `backend_net_prod`) y volúmenes nombrados independientes — no comparten datos entre entornos.

## 3. Seguridad del contenedor

- Ambos targets corren como **usuario no root** (`django` en dev, `appuser` UID 1000 en prod) — buena práctica, verificado por lectura directa del `Dockerfile`.
- `HEALTHCHECK` solo está definido en el target `production` (`/health/` cada 30s); el target `development` no tiene healthcheck propio en el `Dockerfile` (`docker-compose.yml` tampoco lo define aparte para el servicio `backend`, solo para `db`).
- El volumen de medios en producción se llama `media_private_prod` (nombre explícito), reforzando la intención de almacenamiento privado ya verificada en `core/adapters/local_storage.py`.

## 4. Nginx

| Aspecto | Dev (`nginx.conf`) | Prod (`prod.conf`) |
|---|---|---|
| Puertos | 80 (mapeado a 8000 del host) | 80 (redirect) + 443 |
| TLS | No | Sí, TLSv1.2/TLSv1.3, certificados montados externamente |
| `client_max_body_size` | 15M | 15M (coherente con el límite de 10 MB de PDF + margen) |
| Proxy headers | `X-Real-IP`, `X-Forwarded-For`, `X-Forwarded-Proto` | Igual |

Ninguno de los dos archivos de Nginx configura cabeceras de seguridad HTTP (HSTS, CSP, X-Frame-Options, etc.) a nivel de proxy — eso lo hace, según `docs/06-seguridad/`, el middleware `core/adapters/security_headers.py` del lado de Django (el mismo módulo que la Fase 7 encontró con **0 % de cobertura de pruebas** — ver `DOCUMENTACION/07_PRUEBAS/RESULTADOS_VALIDACION.md` §3).
