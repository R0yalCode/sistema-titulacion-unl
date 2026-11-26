---
title: "Instalación"
---

# Instalación — SGT-SIAAF

**Fuente:** `README.md` (raíz, 302 líneas, leído íntegramente), contrastado contra `docker-compose.yml`, `docker-compose.prod.yml` y `backend/src/config/settings/base.py`. Se reproduce el procedimiento documentado por el propio proyecto, **señalando las inexactitudes encontradas al contrastarlo con el código**, en vez de asumir que el README es perfecto o de reescribirlo desde cero.

## 1. Prerrequisitos (según `README.md`)

- Docker ≥ 24.0, Docker Compose ≥ 2.20
- Git (para clonar)
- Puertos libres: 8000 (Nginx expuesto al host)

## 2. Procedimiento documentado (Docker Compose, recomendado)

1. Clonar el repositorio.
2. Crear `.env` en la raíz con `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `SECRET_KEY`, `DEBUG`.
3. `docker compose up --build -d`.
4. `docker compose exec backend python manage.py migrate` + `seed_initial_data`.
5. Verificar en `http://localhost:8000/api/v1/docs/`.

## 3. Hallazgo verificado: el `.env` de ejemplo del README está incompleto

El ejemplo de `.env` en `README.md` §2 **no incluye `JWT_SIGNING_KEY`**. Se verificó en `docker-compose.yml` que esa variable es **obligatoria sin valor por defecto**: `JWT_SIGNING_KEY: ${JWT_SIGNING_KEY:?JWT_SIGNING_KEY is required}`. Siguiendo el procedimiento del README exactamente como está escrito, **`docker compose up` fallaría** al arrancar el servicio `backend` por falta de esa variable. Esto es consistente con la separación de claves documentada en `DOCUMENTACION/06_SEGURIDAD/AUTENTICACION.md` §4 (SEC-T004): el README parece no haberse actualizado tras introducir esa separación. Corrección necesaria (no aplicada aquí, el README no se edita en este trabajo): el `.env` de ejemplo debe incluir también `JWT_SIGNING_KEY=<valor generado, distinto de SECRET_KEY>`.

## 4. Hallazgo menor: alcance real de `pytest` sin argumentos

El README (§"Desarrollo Local") documenta `pytest  # Todos los tests`. Verificado en Fase 7: `pytest` sin argumentos usa `testpaths = ["src/apps"]` (configurado en `pyproject.toml`) y **excluye `src/core`** (76 pruebas). El comentario "Todos los tests" es impreciso; el comando real para todas las pruebas es `pytest src/apps src/core` (o `pytest src`).

## 5. Procedimiento alternativo sin Docker (según `README.md`)

Documentado para Python 3.12 + PostgreSQL 16 local: crear venv, `pip install -r requirements.txt -r requirements-dev.txt`, copiar `backend/.env.example` a `.env`, migrar, poblar con `seed_initial_data`. Es el mismo patrón que se usó (adaptado, sin PostgreSQL) para la ejecución real de pruebas en la Fase 7 de esta auditoría.

## 6. Instalación del frontend (no cubierta en el README raíz; ver `frontend/README.md`)

No se auditó el contenido de `frontend/README.md` en esta fase (fuera del alcance del incremento backend); se confirma únicamente que `frontend/node_modules/` ya existe en el repositorio de trabajo, lo cual permitió ejecutar `npm run test`/`lint`/`typecheck` directamente en la Fase 7 sin reinstalar dependencias.

## 7. Cuentas demo

`README.md` documenta 8 cuentas demo creadas por `seed_initial_data` (una por rol), con una contraseña compartida ya publicada abiertamente en el propio `README.md` del repositorio — no se reproduce aquí para no normalizar su cita fuera de contexto, pero se confirma que es información que el proyecto mismo ya hace pública para fines de evaluación académica, coherente con el hallazgo de `DOCUMENTACION/06_SEGURIDAD/PROTECCION_DATOS.md` §5 (cuentas demo marcadas como no productivas).
