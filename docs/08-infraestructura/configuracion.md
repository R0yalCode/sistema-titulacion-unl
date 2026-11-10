---
title: "Configuración"
---

# Configuración

## Variables de entorno (backend)

Fuente: `backend/.env.example` y `src/config/settings/base.py`.

| Variable | Obligatoria | Default | Uso |
|---|---|---|---|
| `SECRET_KEY` | Sí (sin default) | — | Firma sesiones/cookies/CSRF de Django |
| `JWT_SIGNING_KEY` | Sí (sin default) | — | Firma y verifica JWT (access/refresh), independiente de `SECRET_KEY` (SEC-T004) |
| `DEBUG` | No | `False` | Modo desarrollo |
| `ALLOWED_HOSTS` | No | `[]` | Hosts permitidos |
| `DB_ENGINE` | No | `postgresql` | Motor |
| `DB_NAME` / `DB_USER` | No | `sgt_siaaf` / `sgt_user` | Credenciales |
| `DB_PASSWORD` | Sí (sin default) | — | Contraseña |
| `DB_HOST` / `DB_PORT` | No | `localhost` / `5432` | Conexión |
| `DOCUMENT_UPLOAD_THROTTLE` | No | `10/hour` | Límite de carga de documentos (SEC-T008/DEC-003) |
| `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS` | Sí, solo en `production.py` | — | Dominios reales del despliegue; sin valor por defecto (SEC-T001) |
| `CSP_CONNECT_SRC_EXTRA` | No, solo en `production.py` | `'self'` | Orígenes extra para la CSP Report-Only (DEC-010) |
| `TRUSTED_PROXIES` | No, solo en `production.py` | Rangos RFC1918 | Proxies confiables para IP real (SEC-T005) |

## Settings por entorno

| Archivo | Uso | Diferencias |
|---|---|---|
| `base.py` | Común | Seguro por defecto; DRF+SimpleJWT+spectacular; sin CORS ni throttling de login (sí de carga de documentos, SEC-T008) |
| `local.py` | Desarrollo | Solo `DEBUG=True` |
| `test.py` | Pruebas | SQLite en memoria, hasher MD5 |
| `production.py` | Producción | **Implementado (SEC-T001, 2026-11-05).** `DEBUG=False`, `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS`/`CORS_ALLOWED_ORIGINS` obligatorios, HSTS, cookies seguras, CORS (`django-cors-headers`), CSP Report-Only + `frame-ancestors`/`base-uri` bloqueantes (DEC-010). No incluye el handler global de excepciones (SEC-T010, bloqueada), la protección de Swagger (SEC-T013) ni el logging estructurado completo (SEC-T011) — se añaden en sus propias tareas sobre este mismo archivo. |

## Frontend

| Variable | Obligatoria | Uso |
|---|---|---|
| `VITE_API_BASE_URL` | Sí | URL absoluta de la API, sin barra final |
| `VITE_DEMO_MODE` | No | Muestra banner de demostración |
| `VITE_USE_MOCKS` | No | Activa MSW (solo pruebas) |
| `VITE_APP_NAME` | No | Nombre en la UI |

## Pendientes de configuración

- `PRIVATE_MEDIA_ROOT` (el código lo soporta vía `getattr`, pero no está declarado) — AUD-P2-05.
- ~~`LOGGING` estructurado — AUD-P2-03.~~ **Resuelto (SEC-T011, 2026-11-05):** JSON (`python-json-logger`), filtros de datos sensibles y `request_id`/`user_id`, consola en todos los entornos, archivos rotativos (`RotatingFileHandler`, 10MB/5 backups) solo en `production.py` vía `LOG_DIR`.
- ~~CORS y endurecimiento HTTPS — AUD-P1-01.~~ **Resuelto (SEC-T001, 2026-11-05).**
