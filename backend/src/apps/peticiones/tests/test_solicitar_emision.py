"""Pruebas para T021: Peticion interna de certificados sin correo (HU-002).

Verifica:
- Cambio de estado PENDIENTE -> SOLICITADO
- Creacion de NotificacionInterna a la dependencia emisora
- Validaciones de estado de expediente y peticion
- Permisos (solo estudiante propietario o SECRETARIA_CARRERA)
"""
import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.authentication.adapters.models import (
    ROLE_ESTUDIANTE,
    ROLE_SECRETARIA_CARRERA,
    ROLE_SECRETARIO_ABOGADO,
    User,
    Role,
    UserRole,
)
from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.peticiones.adapters.models import (
    ESTADO_PENDIENTE,
    ESTADO_SOLICITADO,
    PeticionDocumental,
)
from apps.notificaciones.adapters.models import NotificacionInterna
from apps.peticiones.services import solicitar_emision


pytestmark = pytest.mark.django_db

CARRERA_1 = "11111111-1111-1111-1111-111111111111"
FACULTAD_1 = "22222222-2222-2222-2222-222222222222"
PASSWORD = "pass1234"


def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def rol_estudiante():
    role, _ = Role.objects.get_or_create(name=ROLE_ESTUDIANTE)
    return role


@pytest.fixture
def rol_secretaria_carrera():
    role, _ = Role.objects.get_or_create(name=ROLE_SECRETARIA_CARRERA)
    return role


@pytest.fixture
def rol_secretario_abogado():
    role, _ = Role.objects.get_or_create(name=ROLE_SECRETARIO_ABOGADO)
    return role


@pytest.fixture
def estudiante(rol_estudiante):
    user = User.objects.create_user(
        username="estudiante_test",
        email="est@test.com",
        password=PASSWORD,
        cedula="1234567890",
        carrera_id=CARRERA_1,
        facultad_id=FACULTAD_1,
    )
    UserRole.objects.create(user=user, role=rol_estudiante)
    return user


@pytest.fixture
def secretaria_carrera(rol_secretaria_carrera):
    user = User.objects.create_user(
        username="secretaria_test",
        email="sec@test.com",
        password=PASSWORD,
        cedula="1234567891",
        carrera_id=CARRERA_1,
        facultad_id=FACULTAD_1,
    )
    UserRole.objects.create(user=user, role=rol_secretaria_carrera)
    return user


@pytest.fixture
def secretario_abogado(rol_secretario_abogado):
    user = User.objects.create_user(
        username="abogado_test",
        email="abg@test.com",
        password=PASSWORD,
        cedula="1234567892",
        facultad_id=FACULTAD_1,
    )
    UserRole.objects.create(user=user, role=rol_secretario_abogado)
    return user


@pytest.fixture
def expediente_borrador(estudiante):
    return ExpedienteTitulacion.objects.create(
        numero_expediente="EXP-2026-0001",
        estudiante=estudiante,
        carrera_id=CARRERA_1,
        facultad_id=FACULTAD_1,
        estado=ExpedienteTitulacion.ESTADO_BORRADOR,
        activa=True,
    )


@pytest.fixture
def peticion_pendiente(expediente_borrador):
    from apps.peticiones.adapters.models import CatalogoDocumental

    requisito = CatalogoDocumental.objects.filter(
        codigo_requisito="ART235-01-RECORD-ACADEMICO"
    ).first()
    if not requisito:
        requisito = CatalogoDocumental.objects.create(
            codigo_requisito="ART235-01-RECORD-ACADEMICO",
            nombre="Record academico legalizado",
            descripcion="Record academico legalizado otorgado por la Secretaria de Carrera.",
            es_obligatorio_base=True,
            fase="FASE_1",
            rol_emisor_sugerido="SECRETARIA_CARRERA",
            activo=True,
        )
    return PeticionDocumental.objects.create(
        expediente=expediente_borrador,
        requisito=requisito,
        estado_peticion=ESTADO_PENDIENTE,
        dependencia_emisora="SECRETARIA_CARRERA",
    )


class TestSolicitarEmision:
    """Tests del caso de uso solicitar_emision (T021)."""

    def test_solicitud_exitosa_estudiante_cambia_estado_y_crea_notificacion(
        self, estudiante, secretaria_carrera, peticion_pendiente
    ):
        """Estudiante propietario puede solicitar emision."""
        peticion = solicitar_emision.execute(estudiante, peticion_pendiente.id)

        peticion.refresh_from_db()
        assert peticion.estado_peticion == ESTADO_SOLICITADO
        assert peticion.fecha_solicitud is not None

        notificaciones = NotificacionInterna.objects.filter(
            expediente=peticion.expediente, peticion=peticion
        )
        assert notificaciones.exists()
        notif = notificaciones.first()
        assert notif.usuario_destino.role_assignments.filter(
            role__name="SECRETARIA_CARRERA"
        ).exists()
        assert "Solicitud de emision" in notif.titulo
        assert peticion.requisito.nombre in notif.mensaje

    def test_solicitud_exitosa_secretaria_carrera(
        self, secretaria_carrera, peticion_pendiente
    ):
        """Secretaria de Carrera de la misma carrera puede solicitar."""
        peticion = solicitar_emision.execute(secretaria_carrera, peticion_pendiente.id)

        peticion.refresh_from_db()
        assert peticion.estado_peticion == ESTADO_SOLICITADO

        notif = NotificacionInterna.objects.filter(peticion=peticion).first()
        assert notif.usuario_destino.role_assignments.filter(
            role__name="SECRETARIA_CARRERA"
        ).exists()

    def test_falla_si_peticion_no_existe(self, estudiante):
        """Error si peticion_id no existe."""
        from uuid import uuid4
        with pytest.raises(solicitar_emision.PeticionNoEncontradaError):
            solicitar_emision.execute(estudiante, uuid4())

    def test_falla_si_peticion_no_esta_pendiente(
        self, estudiante, peticion_pendiente
    ):
        """Error si peticion ya fue solicitada."""
        peticion_pendiente.estado_peticion = ESTADO_SOLICITADO
        peticion_pendiente.fecha_solicitud = timezone.now()
        peticion_pendiente.save()

        with pytest.raises(solicitar_emision.EstadoPeticionInvalidoError):
            solicitar_emision.execute(estudiante, peticion_pendiente.id)

    def test_falla_si_expediente_no_en_borrador_ni_observada(
        self, estudiante, secretaria_carrera, peticion_pendiente
    ):
        """Error si expediente esta en ENVIADA u otro estado."""
        expediente = peticion_pendiente.expediente
        expediente.estado = ExpedienteTitulacion.ESTADO_ENVIADA
        expediente.save()

        with pytest.raises(solicitar_emision.ExpedienteEstadoInvalidoError):
            solicitar_emision.execute(estudiante, peticion_pendiente.id)

    def test_falla_si_usuario_no_es_propietario_ni_secretaria(
        self, secretario_abogado, peticion_pendiente
    ):
        """Error si usuario no tiene rol permitido."""
        with pytest.raises(solicitar_emision.UsuarioNoAutorizadoError):
            solicitar_emision.execute(secretario_abogado, peticion_pendiente.id)

    def test_falla_si_estudiante_ajeno_intenta_solicitar(
        self, rol_estudiante, peticion_pendiente
    ):
        """Estudiante que no es el propietario no puede solicitar."""
        otro_estudiante = User.objects.create_user(
            username="otro_estudiante",
            email="otro@test.com",
            password=PASSWORD,
            cedula="9999999999",
        )
        UserRole.objects.create(user=otro_estudiante, role=rol_estudiante)

        with pytest.raises(solicitar_emision.UsuarioNoAutorizadoError):
            solicitar_emision.execute(otro_estudiante, peticion_pendiente.id)

    def test_funciona_con_expediente_en_observada(
        self, estudiante, secretaria_carrera, peticion_pendiente
    ):
        """Permite solicitar emision si expediente esta en OBSERVADA."""
        expediente = peticion_pendiente.expediente
        expediente.estado = ExpedienteTitulacion.ESTADO_OBSERVADA
        expediente.save()

        peticion = solicitar_emision.execute(estudiante, peticion_pendiente.id)
        assert peticion.estado_peticion == ESTADO_SOLICITADO


class TestSolicitarEmisionEndpoint:
    """Tests de integracion del endpoint POST /api/v1/peticiones/{id}/solicitar-emision/."""

    def test_endpoint_200_ok(self, estudiante, secretaria_carrera, peticion_pendiente):
        """Endpoint retorna 200 con peticion actualizada."""
        client = auth_client(estudiante)
        url = f"/api/v1/peticiones/{peticion_pendiente.id}/solicitar-emision/"
        response = client.post(url, {}, format="json")

        assert response.status_code == 200
        assert response.data["estado_peticion"] == ESTADO_SOLICITADO
        assert response.data["fecha_solicitud"] is not None

    def test_endpoint_crea_notificacion(self, estudiante, secretaria_carrera, peticion_pendiente):
        """Endpoint crea NotificacionInterna en BD."""
        client = auth_client(estudiante)
        url = f"/api/v1/peticiones/{peticion_pendiente.id}/solicitar-emision/"
        client.post(url, {}, format="json")

        notificaciones = NotificacionInterna.objects.filter(
            expediente=peticion_pendiente.expediente, peticion=peticion_pendiente
        )
        assert notificaciones.exists()

    def test_endpoint_401_sin_autenticacion(self, peticion_pendiente):
        """Sin token retorna 401."""
        client = APIClient()
        url = f"/api/v1/peticiones/{peticion_pendiente.id}/solicitar-emision/"
        response = client.post(url, {}, format="json")
        assert response.status_code == 401

    def test_endpoint_403_rol_no_autorizado(
        self, secretario_abogado, peticion_pendiente
    ):
        """Rol no autorizado retorna 403."""
        client = auth_client(secretario_abogado)
        url = f"/api/v1/peticiones/{peticion_pendiente.id}/solicitar-emision/"
        response = client.post(url, {}, format="json")
        assert response.status_code == 403

    def test_endpoint_400_expediente_en_estado_invalido(
        self, estudiante, secretaria_carrera, peticion_pendiente
    ):
        """Expediente en ENVIADA retorna 400."""
        expediente = peticion_pendiente.expediente
        expediente.estado = ExpedienteTitulacion.ESTADO_ENVIADA
        expediente.save()

        client = auth_client(estudiante)
        url = f"/api/v1/peticiones/{peticion_pendiente.id}/solicitar-emision/"
        response = client.post(url, {}, format="json")
        assert response.status_code == 400

    def test_endpoint_400_peticion_ya_solicitada(
        self, estudiante, secretaria_carrera, peticion_pendiente
    ):
        """Peticion ya en SOLICITADO retorna 400."""
        peticion_pendiente.estado_peticion = ESTADO_SOLICITADO
        peticion_pendiente.fecha_solicitud = timezone.now()
        peticion_pendiente.save()

        client = auth_client(estudiante)
        url = f"/api/v1/peticiones/{peticion_pendiente.id}/solicitar-emision/"
        response = client.post(url, {}, format="json")
        assert response.status_code == 400

    def test_endpoint_404_peticion_no_en_ambito(
        self, estudiante, secretaria_carrera, peticion_pendiente
    ):
        """Estudiante no puede acceder a peticion de expediente ajeno (IDOR)."""
        otro_estudiante = User.objects.create_user(
            username="otro_estudiante2",
            email="otro2@test.com",
            password=PASSWORD,
            cedula="8888888888",
        )
        from apps.authentication.adapters.models import Role, UserRole
        rol_est = Role.objects.get(name=ROLE_ESTUDIANTE)
        UserRole.objects.create(user=otro_estudiante, role=rol_est)

        client = auth_client(otro_estudiante)
        url = f"/api/v1/peticiones/{peticion_pendiente.id}/solicitar-emision/"
        response = client.post(url, {}, format="json")
        assert response.status_code == 404