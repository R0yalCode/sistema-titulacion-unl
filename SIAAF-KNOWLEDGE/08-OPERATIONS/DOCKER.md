---
system: SGT-SIAAF
type: operations
status: verified
source: repository-config
last_verified: 2026-11-11
aliases: [DEPLOYMENT, INSTALLATION]
---

# Docker, despliegue y CI

> Los valores de secretos **no** se registran aquí. Las variables se definen en `.env` (raíz, **no versionado**; no se leyó) a partir de `backend/.env.example`.

## Desarrollo (`docker-compose.yml`)

| Servicio | Imagen / build | Notas |
|---|---|---|
| `db` | `postgres:16` | `TZ=UTC`, healthcheck `pg_isready`, volumen `postgres_data` |
| `backend` | `Dockerfile` target `development` | `DJANGO_SETTINGS_MODULE=config.settings.local`; depende de `db` sano; volúmenes `media_data`, `static_data` |
| `nginx` | `nginx:1.24-alpine` | Publica **`8000:80`**; `nginx/nginx.conf` (proxy al backend) |

Red `backend_net`. El frontend **no** está en compose: se ejecuta con `npm --prefix frontend run dev` (puerto 5173; `.claude/launch.json`).

## Producción (`docker-compose.prod.yml`)

`db` (postgres:16), `backend` (target `production`), `nginx` con puertos `80` y `443` (`nginx/prod.conf`); volúmenes `postgres_data_prod`, `media_private_prod`, `static_data_prod`; red `backend_net_prod`. Variables obligatorias en producción (`backend/.env.example`): `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS`, y opcionales `CSP_CONNECT_SRC_EXTRA`, `TRUSTED_PROXIES`, `LOG_DIR`.

## Variables (solo nombres)

Backend: `SECRET_KEY`, `JWT_SIGNING_KEY` (distintas, SEC-T004), `DEBUG`, `ALLOWED_HOSTS`, `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DOCUMENT_UPLOAD_THROTTLE`, `AUTH_THROTTLE_RATE`, más las de producción citadas arriba.
Frontend (`frontend/.env.example`): `VITE_API_BASE_URL`, `VITE_DEMO_MODE`, `VITE_USE_MOCKS`, `VITE_APP_NAME`. Existe `frontend/.env.local` (local; no se leyó).

## CI/CD

| Workflow | Disparadores | Contenido | Seguimiento Git |
|---|---|---|---|
| `.github/workflows/security.yml` | `pull_request`, `push` a `main` | Safety, Bandit (`bandit -r src/ -c .bandit`), Gitleaks | **Sin seguimiento** (local) |
| `.github/workflows/publish-quarto.yml` | `push` a `main` | `quarto render` → GitHub Pages | **Sin seguimiento** (local) |
| `.github/dependabot.yml`, `.github/safety-policy.yml` | — | — | **Sin seguimiento** |
| `.github/PULL_REQUEST_TEMPLATE.md` | — | Plantilla de PR | Versionado |

Como los workflows no están en el remoto, **hoy no se ejecutan en GitHub**. Esta construcción no los incorporó: no son de su alcance y son cambios locales ajenos.

## Documentación operativa previa

`docs/08-infraestructura/{docker,despliegue,configuracion,entorno-desarrollo,mantenimiento}.md`, `DOCUMENTACION/08_DESPLIEGUE/*` (instalación, ejecución, problemas frecuentes, GitHub Actions; sin seguimiento Git), `DOCUMENTACION/11_PUBLICACION_GITHUB_PAGES.md`, `backend/README.md`, `frontend/README.md`.
