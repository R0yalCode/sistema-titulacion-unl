"""Configuración de pruebas con PostgreSQL real (PLB-E1-04 + O-2, T3).

Hereda de `config.settings.test` y solo sustituye la base de datos. Se usa
para las pruebas marcadas `postgres` (bloqueos, concurrencia, interbloqueos),
que SQLite no puede evidenciar: SQLite ignora `select_for_update` y
serializa las escrituras.

Variables de entorno (sin valores secretos por defecto):

- `PG_TEST_HOST` (por defecto `localhost`), `PG_TEST_PORT` (`5432`)
- `PG_TEST_USER` (`postgres`), `PG_TEST_PASSWORD` (**obligatoria**)
- `PG_TEST_DB` (`sgt_siaaf`): base de conexión; pytest-django crea y
  destruye `test_<PG_TEST_DB>`.
- `PG_TEST_LOCK_TIMEOUT_MS` (`10000`): una espera de bloqueo más larga
  falla con SQLSTATE 55P03 en lugar de colgar la prueba.

Instrucciones de ejecución: `backend/tests/integration/README.md`.
"""

import os

from .test import *  # noqa: F401,F403

_password = os.environ.get("PG_TEST_PASSWORD")
if not _password:
    raise RuntimeError(
        "PG_TEST_PASSWORD es obligatoria para config.settings.test_postgres "
        "(ver backend/tests/integration/README.md)."
    )

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("PG_TEST_DB", "sgt_siaaf"),
        "USER": os.environ.get("PG_TEST_USER", "postgres"),
        "PASSWORD": _password,
        "HOST": os.environ.get("PG_TEST_HOST", "localhost"),
        "PORT": os.environ.get("PG_TEST_PORT", "5432"),
        "CONN_MAX_AGE": 0,
        "OPTIONS": {
            "options": "-c lock_timeout={}".format(
                int(os.environ.get("PG_TEST_LOCK_TIMEOUT_MS", "10000"))
            ),
        },
    }
}
