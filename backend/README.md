# SGT-SIAAF — Backend

API REST del Sistema de Gestión del Trámite de Titulación (UNL), construida con
Django 5.2, Django REST Framework, SimpleJWT y PostgreSQL 16, siguiendo una
arquitectura hexagonal sobre un monolito modular
([ADR-0001](docs/adr/0001-arquitectura-hexagonal-monolito-modular.md)).

La instalación completa (Docker Compose, cuentas de demostración, endpoints y
solución de problemas) está en el [README de la raíz](../README.md). Este
archivo resume lo propio del directorio `backend/`.

## Estructura

| Ruta | Contenido |
|---|---|
| `src/config/` | `urls.py`, WSGI/ASGI y `settings/` (`base`, `local`, `production`, `test`, `test_postgres`) |
| `src/core/` | Dominio, puertos y adaptadores compartidos |
| `src/apps/` | Módulos: `authentication`, `expedientes`, `peticiones`, `verificacion`, `resoluciones`, `notificaciones` |
| `tests/integration/` | Pruebas con PostgreSQL real (marcador `postgres`; ver su [README](tests/integration/README.md)) |
| `tests/e2e/` | Flujo completo de extremo a extremo |
| `docs/adr/` | Decisiones de arquitectura (ADR-0001, 0002, 0003 y 0009) |
| `openapi.yaml` | Contrato OpenAPI canónico (único en el repositorio) |
| `entrypoint.sh` | Arranque del contenedor: migraciones, `collectstatic` y Gunicorn |

## Desarrollo local (sin Docker)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env      # completar SECRET_KEY, JWT_SIGNING_KEY y DB_* (distintas entre sí)
python manage.py migrate
python manage.py seed_initial_data    # cuentas de demostración (idempotente)
python manage.py runserver 0.0.0.0:8000
```

Variables obligatorias: `SECRET_KEY`, `JWT_SIGNING_KEY` y `DB_PASSWORD`. El
resto y sus valores por defecto están documentados en `.env.example`. Nunca
versiones `.env`.

Comandos de gestión propios: `seed_initial_data` y `reconciliar_archivos`.

## Pruebas y calidad

```bash
pytest                       # config.settings.test (SQLite en memoria); omite las pruebas `postgres`
pytest --cov=src             # con cobertura
flake8 src                   # lint
bandit -r src/ -c .bandit    # análisis estático de seguridad (también en CI)
```

## Contrato OpenAPI

`openapi.yaml` se genera desde el código con drf-spectacular. Tras cambiar la
API, regenéralo y revisa el diff:

```bash
python manage.py spectacular --validate --file openapi.yaml
git diff openapi.yaml
```

El job `openapi` de `.github/workflows/ci.yml` falla si el archivo versionado
no coincide con el esquema generado. En ejecución se sirve en
`/api/v1/schema/`, `/api/v1/docs/` (Swagger UI) y `/api/v1/redoc/`.

## Detección de secretos

El repositorio se analiza con [gitleaks](https://github.com/gitleaks/gitleaks)
mediante su Action oficial (`.github/workflows/security.yml`). La
configuración está en `.gitleaks.toml`, en la raíz del repositorio: conserva
las reglas oficiales y solo exime falsos positivos verificados. No se versiona
el binario. Para analizar en local con gitleaks instalado:

```bash
gitleaks git --config .gitleaks.toml .   # desde la raíz del repositorio
```

## Licencia

MIT; ver [`LICENSE`](../LICENSE) en la raíz.
