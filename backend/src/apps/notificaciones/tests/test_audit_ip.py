"""Pruebas de SEC-T005: IP de auditoría confiable vía TRUSTED_PROXIES."""

import pytest
from django.test import override_settings
from rest_framework.test import APIClient

from apps.authentication.adapters.models import Role, User, UserRole
from apps.expedientes.services import crear_expediente
from apps.notificaciones.adapters.models import EventoAuditoria

pytestmark = pytest.mark.django_db

URL_EXPEDIENTES = "/api/v1/expedientes/"
PASSWORD = "pass1234"
CARRERA_1 = "11111111-1111-1111-1111-111111111111"


@pytest.fixture
def estudiante():
    role, _ = Role.objects.get_or_create(name="ESTUDIANTE")
    user = User.objects.create_user(
        username="sec_t005_est",
        password=PASSWORD,
        cedula="7300000001",
        carrera_id=CARRERA_1,
    )
    UserRole.objects.create(user=user, role=role)
    return user


def _ultimo_evento_creacion():
    return EventoAuditoria.objects.filter(
        accion=EventoAuditoria.Accion.EXPEDIENTE_CREADO
    ).latest("timestamp")


@override_settings(TRUSTED_PROXIES=["127.0.0.0/8"])
def test_audit_ip_captured_from_xff_with_trusted_proxy(estudiante):
    """REMOTE_ADDR del test client (127.0.0.1) está en TRUSTED_PROXIES →
    se confía en X-Forwarded-For y se usa el primer IP de la cadena."""
    client = APIClient()
    client.force_authenticate(user=estudiante)

    respuesta = client.post(
        URL_EXPEDIENTES,
        {"carrera_id": CARRERA_1},
        format="json",
        HTTP_X_FORWARDED_FOR="203.0.113.195, 198.51.100.1",
    )

    assert respuesta.status_code == 201
    assert _ultimo_evento_creacion().ip == "203.0.113.195"


def test_audit_ip_spoofing_blocked_untrusted_proxy(estudiante):
    """Sin TRUSTED_PROXIES configurado (estado real de settings.test),
    X-Forwarded-For NUNCA se confía, aunque esté presente: se usa
    REMOTE_ADDR, no el valor que el cliente podría falsificar."""
    client = APIClient()
    client.force_authenticate(user=estudiante)

    respuesta = client.post(
        URL_EXPEDIENTES,
        {"carrera_id": CARRERA_1},
        format="json",
        HTTP_X_FORWARDED_FOR="203.0.113.195",
    )

    assert respuesta.status_code == 201
    ip_registrada = _ultimo_evento_creacion().ip
    assert ip_registrada != "203.0.113.195"
    assert ip_registrada == "127.0.0.1"  # REMOTE_ADDR por defecto del test client


@override_settings(TRUSTED_PROXIES=["127.0.0.0/8"])
def test_audit_ip_persisted_in_eventoauditoria(estudiante):
    """La IP capturada queda persistida en EventoAuditoria, no solo
    calculada en memoria."""
    client = APIClient()
    client.force_authenticate(user=estudiante)

    client.post(
        URL_EXPEDIENTES,
        {"carrera_id": CARRERA_1},
        format="json",
        HTTP_X_FORWARDED_FOR="203.0.113.195",
    )

    evento = _ultimo_evento_creacion()
    assert evento.ip == "203.0.113.195"
    assert evento.expediente is not None


def test_audit_ip_none_when_no_request(estudiante):
    """Fuera de un ciclo de request (p. ej. un management command o, como
    aquí, invocar el servicio directamente sin pasar por la vista), no hay
    request en el thread-local → ip queda en None, no una excepción."""
    crear_expediente.execute(estudiante=estudiante, carrera_id=CARRERA_1)

    evento = _ultimo_evento_creacion()
    assert evento.ip is None
