"""V-03: dos creaciones simultáneas del mismo estudiante (PostgreSQL real).

Mismo método que `test_concurrencia_postgres.py`: el hilo A se retiene dentro
de su transacción, ya con el bloqueo de la fila del estudiante tomado; se
confirma en `pg_stat_activity` que el hilo B espera realmente ese bloqueo y
se libera A. Resultado esperado: un 201 y un 400 `expediente_activo_existente`,
un solo expediente activo y ningún 500.
"""

import threading
import time

import pytest
from django.db import connection, connections
from rest_framework.test import APIClient

from apps.academico.tests.factories import crear_carrera, crear_perfil_mock
from apps.authentication.adapters.models import Role, User, UserRole
from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.expedientes.services import crear_expediente

pytestmark = [
    pytest.mark.postgres,
    pytest.mark.django_db(transaction=True, serialized_rollback=True),
]

ESPERA_MAX = 20


def _esperando_bloqueo(timeout=ESPERA_MAX):
    limite = time.monotonic() + timeout
    while time.monotonic() < limite:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT count(*) FROM pg_stat_activity "
                "WHERE datname = current_database() AND wait_event_type = 'Lock' "
                "AND pid <> pg_backend_pid()"
            )
            if cursor.fetchone()[0] > 0:
                return True
        time.sleep(0.05)
    return False


def test_creaciones_simultaneas_del_mismo_estudiante(monkeypatch):
    estudiante = User.objects.create_user(username="conc_v03", password="x")
    UserRole.objects.create(
        user=estudiante, role=Role.objects.get_or_create(name="ESTUDIANTE")[0]
    )
    crear_perfil_mock(estudiante, crear_carrera("CONC-V03"))

    retenido = threading.Event()
    continuar = threading.Event()
    primera = threading.Lock()
    real = crear_expediente.generar_numero_expediente

    def retener(*args, **kwargs):
        # Se ejecuta con el bloqueo del estudiante ya tomado y RN-001 ya
        # comprobado: solo la primera llamada (hilo A) queda retenida.
        if primera.acquire(blocking=False):
            retenido.set()
            assert continuar.wait(ESPERA_MAX)
        return real(*args, **kwargs)

    monkeypatch.setattr(crear_expediente, "generar_numero_expediente", retener)
    respuestas = {}

    def crear(nombre):
        try:
            client = APIClient()
            client.force_authenticate(user=estudiante)
            client.raise_request_exception = False
            respuestas[nombre] = client.post("/api/v1/expedientes/", {}, format="json")
        finally:
            connections.close_all()

    hilo_a = threading.Thread(target=crear, args=("A",))
    hilo_a.start()
    assert retenido.wait(ESPERA_MAX)
    hilo_b = threading.Thread(target=crear, args=("B",))
    hilo_b.start()
    try:
        assert _esperando_bloqueo(), "B no llegó a esperar el bloqueo del estudiante"
    finally:
        continuar.set()
        hilo_a.join(ESPERA_MAX)
        hilo_b.join(ESPERA_MAX)

    codigos = sorted(r.status_code for r in respuestas.values())
    assert codigos == [201, 400]
    rechazo = next(r for r in respuestas.values() if r.status_code == 400)
    assert rechazo.json()["code"] == "expediente_activo_existente"
    assert (
        ExpedienteTitulacion.objects.filter(estudiante=estudiante, activa=True).count()
        == 1
    )
