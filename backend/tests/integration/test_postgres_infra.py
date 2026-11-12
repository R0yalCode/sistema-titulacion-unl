"""Prueba de humo de la infraestructura PostgreSQL (PLB-E1-04 + O-2, T3).

Confirma que las pruebas `postgres` se ejecutan de verdad contra PostgreSQL
(no SQLite), que `select_for_update` produce un bloqueo real entre dos
conexiones independientes y que `lock_timeout` está activo.
"""

import threading

import pytest
from django.db import OperationalError, connection, connections, transaction

from apps.authentication.adapters.models import Role

pytestmark = [pytest.mark.postgres, pytest.mark.django_db(transaction=True)]


def test_motor_es_postgresql_y_lock_timeout_activo():
    assert connection.vendor == "postgresql"
    with connection.cursor() as cursor:
        cursor.execute("SHOW lock_timeout")
        assert cursor.fetchone()[0] not in ("0", "0ms")


def test_select_for_update_bloquea_entre_conexiones_independientes():
    role = Role.objects.create(name="ROL_PRUEBA_INFRA")
    bloqueado = threading.Event()
    liberar = threading.Event()
    resultado = {}

    def retener():
        try:
            with transaction.atomic():
                Role.objects.select_for_update().get(pk=role.pk)
                bloqueado.set()
                liberar.wait(timeout=10)
        finally:
            connections.close_all()

    def intentar_sin_esperar():
        try:
            with transaction.atomic():
                Role.objects.select_for_update(nowait=True).get(pk=role.pk)
            resultado["obtuvo"] = True
        except OperationalError as error:
            resultado["sqlstate"] = getattr(error.__cause__, "sqlstate", None)
        finally:
            connections.close_all()

    hilo_a = threading.Thread(target=retener)
    hilo_a.start()
    assert bloqueado.wait(timeout=10)
    hilo_b = threading.Thread(target=intentar_sin_esperar)
    hilo_b.start()
    hilo_b.join(timeout=10)
    liberar.set()
    hilo_a.join(timeout=10)

    # 55P03 = lock_not_available: la fila estaba bloqueada por la otra conexión.
    assert resultado == {"sqlstate": "55P03"}
