---
system: SGT-SIAAF
type: operations
status: verified
source: repository-config
last_verified: 2026-11-23
aliases: [DEPLOYMENT, INSTALLATION]
---

# Docker, despliegue y CI

> Los valores de secretos **no** se registran aquí. Las variables se definen en `.env` (raíz, **no versionado**; no se leyó) a partir de `backend/.env.example`.

## Desarrollo (`docker-compose.yml`)

| Servicio | Imagen / build | Notas |
|---|---|---|
| `db` | `postgres:16` | `TZ=UTC`, healthcheck `pg_isready`, volumen `postgres_data` |
| `backend` | `Dockerfile` target `development` | `DJANGO_SETTINGS_MODULE=config.settings.local`; depende de `db` sano; volúmenes `media_data`, `static_data` |
| `nginx` | build de `frontend/Dockerfile` (etapa `node:24-alpine` + `nginx:1.24-alpine`, target `web`) | Publica **`8000:80`**: sirve el frontend React compilado en la imagen y reenvía `/api/`, `/admin/`, `/health/`, `/static/` y `/media/` a `backend:8000` (`nginx/nginx.conf`, montado) |

Red `backend_net`. Desde el 2026-11-12 (rama `fix/docker-nginx-frontend`), el frontend se sirve en compose desde el **mismo origen** `http://localhost:8000`:
- **Compilación:** `docker compose up --build` ejecuta `npm ci` y `npm run build` (con `tsc -b`) dentro de la imagen y nunca usa `frontend/dist` del host. El build arg `VITE_API_BASE_URL` vale por defecto `http://localhost:8000`.
- **React Router:** la ruta `/` y el resto de rutas usan `try_files $uri $uri/ /index.html`. Los recursos de `/assets/` con hash llevan `Cache-Control: public, max-age=31536000, immutable` y responden 404 si no existen; `index.html` se sirve con `no-cache`.
- **Redirecciones:** `absolute_redirect off`, para que `/admin` redirija a `/admin/` conservando el puerto 8000.
- **`/media/`:** no se sirve desde el volumen `media_data`, porque los PDF del trámite son privados y solo salen por la API.
- **Persistencia de documentos en desarrollo:** `MEDIA_ROOT` es `backend/src/media`, mientras el volumen `media_data` se monta en `/app/backend/media`. Recrear el contenedor `backend` **borra los PDF cargados** ([[INITIAL_DATA]] §8).
- **Configuración montada:** `nginx/nginx.conf` es un archivo montado suelto. Tras editarlo, `docker compose restart nginx`; ni `nginx -s reload` ni `up --build` ven el archivo nuevo, porque el contenedor conserva el inodo antiguo. Esa fue la causa del 404 de Django en `/`.

El servidor de desarrollo de Vite (`npm --prefix frontend run dev`, puerto 5173) sigue disponible para trabajar con recarga en caliente.

## Producción (`docker-compose.prod.yml`)

Proyecto `sgt-siaaf-prod`, declarado con `name:`. Usar siempre `-p sgt-siaaf-prod`: `-p` y `COMPOSE_PROJECT_NAME` tienen precedencia sobre `name:`, y el proyecto `sgt-siaaf` es el entorno de desarrollo de `:8000`.

`db` (postgres:16), `backend` (target `production`), `nginx` con puertos `80` y `443` (`nginx/prod.conf`); volúmenes `postgres_data_prod`, `media_private_prod`, `static_data_prod`; red `backend_net_prod`. Variables obligatorias en producción: `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS`, `PUBLIC_BASE_URL`, `EMAIL_HOST` y `DEFAULT_FROM_EMAIL`, y opcionales `CSP_CONNECT_SRC_EXTRA`, `TRUSTED_PROXIES`, `LOG_DIR`. La imagen `production` incluye la marca `.entorno-produccion` y, al arrancar, registra la base como `produccion` ([[INITIAL_DATA]]).

## Variables (solo nombres)

Backend: `SECRET_KEY`, `JWT_SIGNING_KEY` (distintas, SEC-T004), `DEBUG`, `ALLOWED_HOSTS`, `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DOCUMENT_UPLOAD_THROTTLE`, `AUTH_THROTTLE_RATE`, más las de producción citadas arriba.
Frontend (`frontend/.env.example`): `VITE_API_BASE_URL`, `VITE_DEMO_MODE`, `VITE_USE_MOCKS`, `VITE_APP_NAME`. Existe `frontend/.env.local` (local; no se leyó).

## CI/CD

Verificado en `develop` (`f666ef5`) el 2026-11-23:

| Archivo | Disparadores | Contenido |
|---|---|---|
| `.github/workflows/ci.yml` | `pull_request`, `push` a `main` y `develop` | Frontend, backend con SQLite, backend con PostgreSQL 16 y contrato OpenAPI |
| `.github/workflows/security.yml` | `pull_request`, `push` a `main` y `develop` | Safety, Bandit y Gitleaks |
| `.github/workflows/publish-quarto.yml` | `push` a `main` con cambios en `docs/` | `quarto render` → GitHub Pages |
| `.github/safety-policy.yml` | — | Política de Safety |
| `.github/PULL_REQUEST_TEMPLATE.md` | — | Plantilla de PR |

`.github/dependabot.yml` no está versionado en `develop`.

## Documentación operativa previa

`docs/08-infraestructura/{docker,despliegue,configuracion,entorno-desarrollo,mantenimiento}.md`, `DOCUMENTACION/08_DESPLIEGUE/*` (instalación, ejecución, problemas frecuentes, GitHub Actions; sin seguimiento Git), `DOCUMENTACION/11_PUBLICACION_GITHUB_PAGES.md`, `backend/README.md`, `frontend/README.md`.
