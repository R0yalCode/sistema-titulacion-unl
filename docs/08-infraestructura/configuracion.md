---
title: "Configuración"
---

# Configuración

## Variables de entorno (backend)

Fuente: `backend/.env.example` y `src/config/settings/base.py`.

| Variable | Obligatoria | Default | Uso |
|---|---|---|---|
| `SECRET_KEY` | Sí (sin default) | — | Firma Django y JWT |
| `DEBUG` | No | `False` | Modo desarrollo |
| `ALLOWED_HOSTS` | No | `[]` | Hosts permitidos |
| `DB_ENGINE` | No | `postgresql` | Motor |
| `DB_NAME` / `DB_USER` | No | `sgt_siaaf` / `sgt_user` | Credenciales |
| `DB_PASSWORD` | Sí (sin default) | — | Contraseña |
| `DB_HOST` / `DB_PORT` | No | `localhost` / `5432` | Conexión |

## Settings por entorno

| Archivo | Uso | Diferencias |
|---|---|---|
| `base.py` | Común | Seguro por defecto; DRF+SimpleJWT+spectacular; sin CORS ni throttling |
| `local.py` | Desarrollo | Solo `DEBUG=True` |
| `test.py` | Pruebas | SQLite en memoria, hasher MD5 |
| `production.py` | **No existe** | Pendiente (AUD-P0-01) |

## Frontend

| Variable | Obligatoria | Uso |
|---|---|---|
| `VITE_API_BASE_URL` | Sí | URL absoluta de la API, sin barra final |
| `VITE_DEMO_MODE` | No | Muestra banner de demostración |
| `VITE_USE_MOCKS` | No | Activa MSW (solo pruebas) |
| `VITE_APP_NAME` | No | Nombre en la UI |

## Pendientes de configuración

- `PRIVATE_MEDIA_ROOT` (el código lo soporta vía `getattr`, pero no está declarado) — AUD-P2-05.
- `LOGGING` estructurado — AUD-P2-03.
- CORS y endurecimiento HTTPS — AUD-P1-01.
