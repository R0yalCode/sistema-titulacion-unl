---
title: "Entorno de desarrollo"
---

# Entorno de desarrollo

## Requisitos

| Componente | Versión |
|---|---|
| Python | 3.12 (contenedor); ≥ 3.10 en local |
| Node.js | ≥ 20 |
| PostgreSQL | 16 |
| Quarto (solo para esta documentación) | ≥ 1.4 |

## Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env            # definir SECRET_KEY, JWT_SIGNING_KEY y DB_PASSWORD
python manage.py migrate
python manage.py seed_initial_data   # 8 cuentas demo (solo desarrollo)
python manage.py runserver
```

## Frontend

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```

Variables (`frontend/.env`): `VITE_API_BASE_URL` (obligatoria, p. ej. `http://localhost:8000`), `VITE_DEMO_MODE`, `VITE_USE_MOCKS`, `VITE_APP_NAME`.

## Cuentas demo (solo desarrollo)

`seed_initial_data` crea 8 usuarios (uno por rol) con contraseña `SgtDemo2026!`. Están marcados explícitamente como no productivos. **No usar en un despliegue real.**

## Verificaciones locales

```bash
# backend
pytest -q                                            # suite configurada (473)
pytest -q src/core src/core/adapters/tests tests/e2e # suite extendida (53)
pytest --cov=src                                     # cobertura
flake8 src

# frontend
npm run lint && npm run typecheck && npm run test && npm run build
```
