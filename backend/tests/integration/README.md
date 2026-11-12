# Pruebas de integración con PostgreSQL real

Las pruebas marcadas `postgres` (bloqueos, concurrencia, interbloqueos) solo
tienen valor contra PostgreSQL: SQLite ignora `select_for_update` y serializa
las escrituras. Con la configuración por defecto (`config.settings.test`,
SQLite en memoria) se **omiten** automáticamente (`backend/conftest.py`).

## 1. Levantar un PostgreSQL desechable

No uses el volumen de desarrollo (`docker-compose.yml`, servicio `db`): las
pruebas crean y destruyen su propia base `test_<PG_TEST_DB>`. Un contenedor
temporal, sin volumen, en un puerto libre:

```bash
docker run -d --rm --name sgt-pg-pruebas \
  -e POSTGRES_PASSWORD=<clave-local-de-pruebas> \
  -p 55432:5432 postgres:16
```

## 2. Ejecutar

Desde `backend/`:

```bash
export SECRET_KEY=<clave-de-pruebas> JWT_SIGNING_KEY=<otra-clave> DB_PASSWORD=x
export DJANGO_SETTINGS_MODULE=config.settings.test_postgres
export PG_TEST_HOST=localhost PG_TEST_PORT=55432 PG_TEST_USER=postgres
export PG_TEST_PASSWORD=<clave-local-de-pruebas>
python -m pytest -m postgres tests/integration -p no:cacheprovider
```

Variables opcionales: `PG_TEST_DB` (base de conexión, por defecto
`sgt_siaaf`) y `PG_TEST_LOCK_TIMEOUT_MS` (por defecto 10000: una espera de
bloqueo mayor falla con SQLSTATE `55P03` en lugar de colgar la prueba).

## 3. Detener

```bash
docker stop sgt-pg-pruebas
```

## Evidencia

Al cerrar una tarea que dependa de estas pruebas, registra en la bitácora el
comando, la versión de PostgreSQL (`SELECT version()`) y el resultado real.
