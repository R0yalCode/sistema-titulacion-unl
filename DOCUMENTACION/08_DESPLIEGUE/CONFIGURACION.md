---
title: "Configuración"
---

# Configuración — SGT-SIAAF

**Fuente:** `backend/src/config/settings/{base,local,production,test}.py`, `backend/.env.example`, `docker-compose.yml`, `docker-compose.prod.yml` (todos verificados directamente). Complementa `DOCUMENTACION/06_SEGURIDAD/PROTECCION_DATOS.md` §1 (variables de entorno) sin repetir la tabla completa.

## 1. Módulos de configuración por entorno

| Módulo | Uso | Particularidad verificada |
|---|---|---|
| `base.py` | Compartido por todos los entornos | `DEBUG=False` y `ALLOWED_HOSTS=[]` por defecto; `SECRET_KEY`/`JWT_SIGNING_KEY` obligatorias sin default |
| `local.py` | `docker-compose.yml` (target `development`) | Hereda `base.py`; activa `DEBUG` vía variable de entorno (`${DEBUG:-1}`, default **activado** en ese compose) |
| `production.py` | `docker-compose.prod.yml` (target `production`) | Añade CORS (`corsheaders`), `CSRF_TRUSTED_ORIGINS`, `TRUSTED_PROXIES`, hardening HTTPS (ver §3) |
| `test.py` | `pytest` (vía `pyproject.toml`) | SQLite en memoria, `PASSWORD_HASHERS` reducido a MD5 (acelera las pruebas; **nunca usar en producción**, es una práctica estándar y segura solo porque es exclusiva del entorno de test) |

## 2. Variables obligatorias por entorno (verificado en código, no solo en `.env.example`)

| Variable | `local` (dev) | `production` |
|---|---|---|
| `SECRET_KEY` | Obligatoria | Obligatoria |
| `JWT_SIGNING_KEY` | Obligatoria | Obligatoria |
| `DB_PASSWORD` | Obligatoria | Obligatoria |
| `ALLOWED_HOSTS` | Fijo en `docker-compose.yml` (`localhost,127.0.0.1`) | Obligatoria, sin default (`${ALLOWED_HOSTS:?...}`) |
| `CSRF_TRUSTED_ORIGINS` | No aplica | Obligatoria |
| `CORS_ALLOWED_ORIGINS` | No aplica (CORS no activo en dev) | Obligatoria |
| `TRUSTED_PROXIES` | No aplica | Opcional, default redes privadas RFC1918 |
| `AUTH_THROTTLE_RATE` / `DOCUMENT_UPLOAD_THROTTLE` | Opcional, defaults `5/minute` / `10/hour` | Igual |

## 3. Hardening específico de `production.py` (verificado, no asumido)

`production.py` añade, sobre `base.py`: activación de `corsheaders` (app + middleware), `CORS_ALLOWED_ORIGINS`/`CORS_ALLOW_CREDENTIALS=True`, y `TRUSTED_PROXIES` para el throttling consciente de proxy (`DOCUMENTACION/06_SEGURIDAD/AUTENTICACION.md` §5). No se verificó en esta pasada si `production.py` también fija `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE` o cabeceras HSTS a nivel de Django (serían las variables típicas de un checklist de "Django deployment checklist"); el propio comentario del archivo (citado en Fase 0) menciona "HTTPS obligatorio, cookies seguras, CSRF, CORS, cabeceras de seguridad" como su propósito declarado, pero no se confirmó línea por línea cada ajuste — pendiente de verificación exhaustiva si se requiere certeza total.

## 4. Separación de secretos (resumen, detalle completo en Fase 6)

Confirmado: `SECRET_KEY` (sesiones/CSRF Django) y `JWT_SIGNING_KEY` (firma JWT) son variables independientes desde SEC-T004; ninguna tiene valor de reserva hardcodeado. `backend/.env.example` documenta ambas con placeholders (`change-me-in-dev`), nunca con valores reales.

## 5. Configuración de base de datos

PostgreSQL 16 en todos los entornos salvo `test` (SQLite en memoria). Nombre de base, usuario y host se parametrizan vía `DB_NAME`/`DB_USER`/`DB_HOST`/`DB_PORT`, con valores por defecto razonables para desarrollo (`sgt_siaaf`/`sgt_user`/`localhost`/`5432`) pero `DB_PASSWORD` siempre obligatoria.
