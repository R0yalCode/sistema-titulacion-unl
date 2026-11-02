"""Pruebas para T038: Endpoint GET /api/v1/notificaciones/ y PATCH /api/v1/notificaciones/{id}/marcar-leida/ (HU-005, RF-012).

Verifica:
- GET /api/v1/notificaciones/ retorna lista de notificaciones del usuario autenticado
- Filtro opcional por leida=true/false
- PATCH /api/v1/notificaciones/{id}/marcar-leida/ marca como leída
- Validación de permisos y aislamiento por usuario
"""

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.authentication.adapters.models import (
    ROLE_ESTUDIANTE,
    ROLE_SECRETARIO_ABOGADO,
    ROLE_DECANO,
    User,
    Role,
    UserRole,
)
from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.peticiones.adapters.models import (
    ESTADO_VERIFICADO,
    PeticionDocumental,
    DocumentoEntregado,
)
from apps.verificacion.adapters.models import (
    ChecklistVerification,
    ESTADO_VERIFICACION_VERIFICADO,
)
from apps.notificaciones.adapters.models import NotificacionInterna
from apps.notificaciones.services import (
    crear_notificacion,
    notificar_estudiante_subsanacion,
)
from apps.resoluciones.services import emitir_informe
from apps.verificacion.services import evaluar_checklist

pytestmark = pytest.mark.django_db

CARRERA_1 = "11111111-1111-1111-1111-111111111111"
FACULTAD_1 = "22222222-2222-2222-2222-222222222222"
PASSWORD = "pass1234"

# PDF válido mínimo para testing
PDF_VALIDO = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>\nendobj\n4 0 obj\n<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>\nendobj\n5 0 obj\n<</Length 44>>\nstream\nBT /F1 24 Tf 100 700 Td (Test) Tj ET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000218 00000 n \n0000000277 00000 n \ntrailer\n<</Size 6/Root 1 0 R>>\nstartxref\n347\n%%EOF"


@pytest.fixture
def api_client():
    return APIClient()


def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def rol_estudiante():
    role, _ = Role.objects.get_or_create(name="ESTUDIANTE")
    return role


@pytest.fixture
def rol_secretario_abogado():
    role, _ = Role.objects.get_or_create(name="SECRETARIO_ABOGADO")
    return role


@pytest.fixture
def rol_decano():
    role, _ = Role.objects.get_or_create(name="DECANO")
    return role


@pytest.fixture
def estudiante(rol_estudiante):
    user = User.objects.create_user(
        username="estudiante_test",
        email="est@test.com",
        password="pass1234",
        cedula="1234567890",
        carrera_id="11111111-1111-1111-1111-111111111111",
        facultad_id="22222222-2222-2222-2222-222222222222",
    )
    UserRole.objects.create(user=user, role=rol_estudiante)
    return user


@pytest.fixture
def otro_estudiante(rol_estudiante):
    user = User.objects.create_user(
        username="otro_est",
        email="otro@test.com",
        password="pass1234",
        cedula="9999999999",
        carrera_id="11111111-1111-1111-1111-111111111111",
        facultad_id="22222222-2222-2222-2222-222222222222",
    )
    UserRole.objects.create(user=user, role=rol_estudiante)
    return user


@pytest.fixture
def secretario_abogado(rol_secretario_abogado):
    user = User.objects.create_user(
        username="secretario_test",
        email="sec@test.com",
        password="pass1234",
        cedula="1234567893",
        carrera_id="11111111-1111-1111-1111-111111111111",
        facultad_id="22222222-2222-2222-2222-222222222222",
    )
    UserRole.objects.create(user=user, role=rol_secretario_abogado)
    return user


@pytest.fixture
def expediente_con_notificaciones(estudiante, otro_estudiante, secretario_abogado):
    """Expediente con notificaciones de prueba para ambos estudiantes."""
    from apps.peticiones.adapters.models import CatalogoDocumental, ESTADO_CARGADO

    expediente = ExpedienteTitulacion.objects.create(
        numero_expediente="EXP-2026-0001",
        estudiante=estudiante,
        carrera_id="11111111-1111-1111-1111-111111111111",
        facultad_id="22222222-2222-2222-2222-222222222222",
        estado=ExpedienteTitulacion.ESTADO_EN_VERIFICACION,
        activa=True,
        fecha_recepcion=timezone.now(),
    )

    # Crear 2 requisitos VERIFICADO
    for i, (codigo, nombre) in enumerate([
        ("REQ-01", "Acta de Grado"),
        ("REQ-02", "Certificado de Votación"),
    ]):
        requisito = CatalogoDocumental.objects.create(
            codigo_requisito=codigo,
            nombre=nombre,
            es_obligatorio_base=True,
            fase="FASE_1",
            rol_emisor_sugerido="SECRETARIA_CARRERA",
            activo=True,
        )
        peticion = PeticionDocumental.objects.create(
            expediente=expediente,
            requisito=requisito,
            estado_peticion="VERIFICADO",
            dependencia_emisora="SECRETARIA_CARRERA",
        )
        DocumentoEntregado.objects.create(
            peticion=peticion,
            version=1,
            archivo_path=f"expedientes/2026/{expediente.id}/{codigo}.pdf",
            nombre_original=f"{codigo}.pdf",
            tamanio_bytes=100,
            hash_sha256="a" * 64,
            tipo_mime="application/pdf",
            subido_por=estudiante,
            es_vigente=True,
        )
        ChecklistVerification.objects.create(
            expediente=expediente,
            requisito=requisito,
            estado_verificacion="VERIFICADO",
            evaluado_por=estudiante,  # dummy
        )

    # Crear notificaciones para el estudiante propietario
    NotificacionInterna.objects.create(
        usuario_destino=estudiante,
        expediente=expediente,
        titulo="Notificación 1 - Estudiante",
        mensaje="Mensaje 1",
        leida=False,
    )
    NotificacionInterna.objects.create(
        usuario_destino=estudiante,
        expediente=expediente,
        titulo="Notificación 2 - Estudiante",
        mensaje="Mensaje 2",
        leida=True,
    )

    # Crear notificación para otro estudiante (aislamiento)
    NotificacionInterna.objects.create(
        usuario_destino=otro_estudiante,
        expediente=expediente,
        titulo="Notificación Otro",
        mensaje="Otro mensaje",
        leida=False,
    )

    return expediente


class TestNotificacionesEndpoint:
    """Tests de los endpoints de notificaciones (T038)."""

    def test_endpoint_list_notificaciones_propias(self, api_client, estudiante, expediente_con_notificaciones):
        """GET /api/v1/notificaciones/ retorna solo notificaciones del usuario autenticado."""
        client = auth_client(estudiante)
        response = client.get("/api/v1/notificaciones/")

        assert response.status_code == 200
        assert "results" in response.data
        assert len(response.data["results"]) == 2
        for notif in response.data["results"]:
            assert notif["titulo"] in ["Notificación 1 - Estudiante", "Notificación 2 - Estudiante"]

    def test_endpoint_filtro_leida_false(self, api_client, estudiante, expediente_con_notificaciones):
        """Filtro leida=false retorna solo no leídas."""
        client = auth_client(estudiante)
        response = client.get("/api/v1/notificaciones/?leida=false")

        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["leida"] is False
        assert response.data["results"][0]["titulo"] == "Notificación 1 - Estudiante"

    def test_endpoint_filtro_leida_true(self, api_client, estudiante, expediente_con_notificaciones):
        """Filtro leida=true retorna solo leídas."""
        client = auth_client(estudiante)
        response = client.get("/api/v1/notificaciones/?leida=true")

        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["leida"] is True
        assert response.data["results"][0]["titulo"] == "Notificación 2 - Estudiante"

    def test_endpoint_aislamiento_estudiantes(self, api_client, otro_estudiante, expediente_con_notificaciones):
        """Estudiante solo ve sus propias notificaciones."""
        client = auth_client(otro_estudiante)
        response = client.get("/api/v1/notificaciones/")

        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["titulo"] == "Notificación Otro"

    def test_endpoint_401_sin_autenticacion(self, api_client):
        """Sin token retorna 401."""
        response = api_client.get("/api/v1/notificaciones/")
        assert response.status_code == 401


class TestMarcarLeidaEndpoint:
    """Tests del endpoint PATCH /api/v1/notificaciones/{id}/marcar-leida/."""

    def test_marcar_leida_exitosa(self, api_client, estudiante, expediente_con_notificaciones):
        """PATCH marca notificación como leída."""
        client = auth_client(estudiante)

        # Obtener una notificación no leída
        notif_no_leida = NotificacionInterna.objects.filter(
            usuario_destino=estudiante, leida=False
        ).first()
        assert notif_no_leida is not None
        assert notif_no_leida.leida is False

        url = f"/api/v1/notificaciones/{notif_no_leida.id}/marcar-leida/"
        response = client.patch(url, {}, format="json")

        assert response.status_code == 200
        assert response.data["leida"] is True
        assert response.data["id"] == str(notif_no_leida.id)

        # Verificar en BD
        notif_no_leida.refresh_from_db()
        assert notif_no_leida.leida is True

    def test_marcar_leida_otro_usuario_falla(self, api_client, estudiante, otro_estudiante, expediente_con_notificaciones):
        """No se puede marcar notificación de otro usuario."""
        client = auth_client(otro_estudiante)

        notif_estudiante = NotificacionInterna.objects.filter(
            usuario_destino=estudiante, leida=False
        ).first()

        url = f"/api/v1/notificaciones/{notif_estudiante.id}/marcar-leida/"
        response = client.patch(url, {}, format="json")

        # Debe fallar con 403 o 404 (no encontrado por scope)
        assert response.status_code in (403, 404)

    def test_marcar_leida_ya_leida(self, api_client, estudiante, expediente_con_notificaciones):
        """Marcar como leída una notificación ya leída (idempotente)."""
        client = auth_client(estudiante)

        notif_leida = NotificacionInterna.objects.filter(
            usuario_destino=estudiante, leida=True
        ).first()
        assert notif_leida is not None
        assert notif_leida.leida is True

        url = f"/api/v1/notificaciones/{notif_leida.id}/marcar-leida/"
        response = client.patch(url, {}, format="json")

        assert response.status_code == 200
        assert response.data["leida"] is True

    def test_marcar_leida_inexistente(self, api_client, estudiante):
        """Notificación inexistente retorna 404."""
        client = auth_client(estudiante)
        import uuid
        url = f"/api/v1/notificaciones/{uuid.uuid4()}/marcar-leida/"
        response = client.patch(url, {}, format="json")

        assert response.status_code == 404

    def test_marcar_leida_401_sin_autenticacion(self, api_client, expediente_con_notificaciones, estudiante):
        """Sin token retorna 401."""
        notif = NotificacionInterna.objects.filter(
            usuario_destino=estudiante, leida=False
        ).first()

        url = f"/api/v1/notificaciones/{notif.id}/marcar-leida/"
        response = api_client.patch(url, {}, format="json")

        assert response.status_code == 401


class TestNotificacionesResponseStructure:
    """Tests de estructura de respuesta."""

    def test_list_response_tiene_campos_esperados(self, api_client, estudiante, expediente_con_notificaciones):
        """Respuesta del listado tiene campos esperados."""
        client = auth_client(estudiante)
        response = client.get("/api/v1/notificaciones/")

        assert response.status_code == 200
        notif = response.data["results"][0]
        assert "id" in notif
        assert "expediente" in notif
        assert "expediente_numero" in notif
        assert "peticion" in notif
        assert "peticion_requisito_nombre" in notif
        assert "titulo" in notif
        assert "mensaje" in notif
        assert "leida" in notif
        assert "fecha_creacion" in notif

    def test_marcar_leida_response_tiene_campos(self, api_client, estudiante, expediente_con_notificaciones):
        """Respuesta de marcar leída tiene campos esperados."""
        client = auth_client(estudiante)
        notif = NotificacionInterna.objects.filter(usuario_destino=estudiante, leida=False).first()

        response = client.patch(f"/api/v1/notificaciones/{notif.id}/marcar-leida/", {}, format="json")

        assert response.status_code == 200
        assert "id" in response.data
        assert "leida" in response.data
        assert "titulo" in response.data
        assert "mensaje" in response.data
        assert "fecha_creacion" in response.data