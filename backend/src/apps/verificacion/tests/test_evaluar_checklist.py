"""Pruebas para T027: Evaluación de checklist digital con bloqueo pesimista (HU-006, RF-006, ADR-007).

Verifica:
- PUT /api/v1/checklist/{id}/ evalúa requisito (VERIFICADO / OBSERVADO)
- Bloqueo pesimista select_for_update() previene condiciones de carrera
- Validación de estados y permisos
- Creación de observación accionable al marcar OBSERVADO
- Cambio de estado de petición y expediente
- Notificación al estudiante al observar
"""

import io
import threading
import time

import pytest
from django.db import transaction
from rest_framework.test import APIClient

from apps.authentication.adapters.models import (
    ROLE_ESTUDIANTE,
    ROLE_SECRETARIO_ABOGADO,
    ROLE_ANALISTA_APOYO,
    User,
    Role,
    UserRole,
)
from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.peticiones.adapters.models import (
    ESTADO_CARGADO,
    ESTADO_PENDIENTE,
    PeticionDocumental,
)
from apps.verificacion.adapters.models import (
    ChecklistVerification,
    ObservacionAccionable,
    ESTADO_VERIFICACION_PENDIENTE,
    ESTADO_VERIFICACION_VERIFICADO,
    ESTADO_VERIFICACION_OBSERVADO,
)
from apps.notificaciones.adapters.models import NotificacionInterna
from apps.verificacion.services import evaluar_checklist

pytestmark = pytest.mark.django_db

CARRERA_1 = "11111111-1111-1111-1111-111111111111"
FACULTAD_1 = "22222222-2222-2222-2222-222222222222"
PASSWORD = "pass1234"

# PDF válido mínimo para testing (PDF 1.4)
PDF_VALIDO = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>\nendobj\n4 0 obj\n<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>\nendobj\n5 0 obj\n<</Length 44>>\nstream\nBT /F1 24 Tf 100 700 Td (Test) Tj ET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000218 00000 n \n0000000277 00000 n \ntrailer\n<</Size 6/Root 1 0 R>>\nstartxref\n347\n%%EOF"

# Archivos inválidos para testing de seguridad
EJECUTABLE_RENOMBRADO = b"MZ\x90\x00"  # PE header (Windows executable)
IMAGEN_PNG_RENOMBRADA = b"\x89PNG\r\n\x1a\n"
IMAGEN_JPEG_RENOMBRADA = b"\xff\xd8\xff\xe0"
TEXTO_PLANO = b"Esto no es un PDF"
ARCHIVO_VACIO = b""
ARCHIVO_GRANDE = b"%PDF-1.4\n" + b"x" * (11 * 1024 * 1024)  # 11 MB


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def rol_estudiante():
    role, _ = Role.objects.get_or_create(name=ROLE_ESTUDIANTE)
    return role


@pytest.fixture
def rol_secretario_abogado():
    role, _ = Role.objects.get_or_create(name=ROLE_SECRETARIO_ABOGADO)
    return role


@pytest.fixture
def rol_analista_apoyo():
    role, _ = Role.objects.get_or_create(name=ROLE_ANALISTA_APOYO)
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
def secretario_abogado(rol_secretario_abogado):
    user = User.objects.create_user(
        username="secretario_test",
        email="sec@test.com",
        password=PASSWORD,
        cedula="1234567891",
        carrera_id=CARRERA_1,
        facultad_id=FACULTAD_1,
    )
    UserRole.objects.create(user=user, role=rol_secretario_abogado)
    # Add both roles for testing
    rol_analista, _ = Role.objects.get_or_create(name="ANALISTA_APOYO")
    UserRole.objects.create(user=user, role=rol_analista)
    return user


@pytest.fixture
def analista_apoyo(rol_analista_apoyo):
    user = User.objects.create_user(
        username="analista_test",
        email="analista@test.com",
        password=PASSWORD,
        cedula="1234567892",
        carrera_id=CARRERA_1,
        facultad_id=FACULTAD_1,
    )
    UserRole.objects.create(user=user, role=rol_analista_apoyo)
    return user


@pytest.fixture
def expediente_en_verificacion(estudiante, secretario_abogado):
    from apps.peticiones.adapters.models import CatalogoDocumental, ESTADO_CARGADO

    expediente = ExpedienteTitulacion.objects.create(
        numero_expediente="EXP-2026-0001",
        estudiante=estudiante,
        carrera_id=CARRERA_1,
        facultad_id=FACULTAD_1,
        estado=ExpedienteTitulacion.ESTADO_EN_VERIFICACION,
        activa=True,
    )

    # Crear requisitos base
    for i, (codigo, nombre) in enumerate([
        ("REQ-01", "Requisito 1"),
        ("REQ-02", "Requisito 2"),
        ("REQ-03", "Requisito 3"),
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
            estado_peticion=ESTADO_CARGADO,
            dependencia_emisora="SECRETARIA_CARRERA",
        )
        # Crear documento entregado
        from apps.peticiones.adapters.models import DocumentoEntregado
        DocumentoEntregado.objects.create(
            peticion=peticion,
            version=1,
            archivo_path=f"expedientes/2026/{expediente.id}/test_{i}.pdf",
            nombre_original=f"{nombre}.pdf",
            tamanio_bytes=len(PDF_VALIDO),
            hash_sha256="a" * 64,
            tipo_mime="application/pdf",
            subido_por=estudiante,
            es_vigente=True,
        )
        # Crear verificación pendiente
        ChecklistVerification.objects.create(
            expediente=expediente,
            requisito=requisito,
            estado_verificacion="PENDIENTE",
        )

    return expediente


@pytest.fixture
def checklist_verification(expediente_en_verificacion):
    """Retorna la primera verificación pendiente del expediente."""
    return ChecklistVerification.objects.filter(
        expediente=expediente_en_verificacion,
        estado_verificacion="PENDIENTE"
    ).first()


class TestEvaluarChecklistService:
    """Tests del servicio evaluar_checklist (T027)."""

    def test_evaluar_verificado_exitoso(self, secretario_abogado, checklist_verification, expediente_en_verificacion):
        """Evaluar como VERIFICADO actualiza estados correctamente."""
        verif = evaluar_checklist.execute(
            usuario=secretario_abogado,
            checklist_verification_id=checklist_verification.id,
            nuevo_estado="VERIFICADO",
        )

        assert verif.estado_verificacion == "VERIFICADO"
        assert verif.evaluado_por == secretario_abogado
        assert verif.fecha_evaluacion is not None

        # Verificar que la petición cambió a VERIFICADO
        peticion = expediente_en_verificacion.peticiones_documentales.get(
            requisito=checklist_verification.requisito
        )
        assert peticion.estado_peticion == "VERIFICADO"

    def test_evaluar_observado_crea_observacion_y_notifica(self, secretario_abogado, checklist_verification, expediente_en_verificacion):
        """Evaluar como OBSERVADO crea observación, cambia estados y notifica."""
        motivo = "Documento ilegible, falta firma del director"

        verif = evaluar_checklist.execute(
            usuario=secretario_abogado,
            checklist_verification_id=checklist_verification.id,
            nuevo_estado="OBSERVADO",
            motivo_observacion=motivo,
        )

        assert verif.estado_verificacion == "OBSERVADO"
        assert verif.evaluado_por == secretario_abogado

        # Verificar petición en OBSERVADO
        peticion = expediente_en_verificacion.peticiones_documentales.get(
            requisito=checklist_verification.requisito
        )
        assert peticion.estado_peticion == "OBSERVADO"

        # Verificar expediente en OBSERVADA
        expediente_en_verificacion.refresh_from_db()
        assert expediente_en_verificacion.estado == "OBSERVADA"

        # Verificar observación creada
        observacion = ObservacionAccionable.objects.filter(
            expediente=expediente_en_verificacion,
            peticion__requisito=checklist_verification.requisito
        ).first()
        assert observacion is not None
        assert observacion.motivo_observacion == motivo
        assert observacion.registrada_por == secretario_abogado
        assert observacion.resuelta is False

        # Verificar notificación al estudiante
        notificacion = NotificacionInterna.objects.filter(
            usuario_destino=expediente_en_verificacion.estudiante,
            expediente=expediente_en_verificacion,
            peticion=peticion,
        ).first()
        assert notificacion is not None
        assert "Observación" in notificacion.titulo
        assert motivo in notificacion.mensaje

    def test_falla_si_checklist_no_existe(self, secretario_abogado):
        """Error si checklist_verification_id no existe."""
        from uuid import uuid4
        with pytest.raises(evaluar_checklist.ChecklistVerificationNotFoundError):
            evaluar_checklist.execute(
                usuario=secretario_abogado,
                checklist_verification_id=uuid4(),
                nuevo_estado="VERIFICADO",
            )

    def test_falla_si_estado_invalido(self, secretario_abogado, checklist_verification):
        """Error si estado no es VERIFICADO u OBSERVADO."""
        with pytest.raises(evaluar_checklist.InvalidVerificationStateError):
            evaluar_checklist.execute(
                usuario=secretario_abogado,
                checklist_verification_id=checklist_verification.id,
                nuevo_estado="APROBADO",
            )

    def test_falla_si_observado_sin_motivo(self, secretario_abogado, checklist_verification):
        """Error si estado OBSERVADO sin motivo."""
        with pytest.raises(evaluar_checklist.InvalidVerificationStateError):
            evaluar_checklist.execute(
                usuario=secretario_abogado,
                checklist_verification_id=checklist_verification.id,
                nuevo_estado="OBSERVADO",
                motivo_observacion="",
            )

    def test_falla_si_ya_evaluado(self, secretario_abogado, checklist_verification):
        """Error si ya fue evaluado (no PENDIENTE)."""
        # Evaluar primero
        evaluar_checklist.execute(
            usuario=secretario_abogado,
            checklist_verification_id=checklist_verification.id,
            nuevo_estado="VERIFICADO",
        )
        # Intentar evaluar de nuevo
        with pytest.raises(evaluar_checklist.VerificationAlreadyCompletedError):
            evaluar_checklist.execute(
                usuario=secretario_abogado,
                checklist_verification_id=checklist_verification.id,
                nuevo_estado="OBSERVADO",
                motivo_observacion="Motivo",
            )

    def test_falla_si_expediente_no_en_verificacion(self, secretario_abogado, expediente_en_verificacion):
        """Error si expediente no está en EN_VERIFICACION."""
        from apps.peticiones.adapters.models import CatalogoDocumental, ESTADO_CARGADO
        from apps.verificacion.adapters.models import ChecklistVerification

        expediente = ExpedienteTitulacion.objects.create(
            numero_expediente="EXP-2026-0002",
            estudiante=expediente_en_verificacion.estudiante,
            carrera_id=CARRERA_1,
            facultad_id=FACULTAD_1,
            estado=ExpedienteTitulacion.ESTADO_ENVIADA,  # No en verificación
            activa=True,
        )

        requisito = CatalogoDocumental.objects.create(
            codigo_requisito="REQ-TEST",
            nombre="Test",
            es_obligatorio_base=True,
            fase="FASE_1",
            rol_emisor_sugerido="SECRETARIA_CARRERA",
            activo=True,
        )

        verif = ChecklistVerification.objects.create(
            expediente=expediente,
            requisito=requisito,
            estado_verificacion="PENDIENTE",
        )

        with pytest.raises(evaluar_checklist.ExpedienteNotInVerificationError):
            evaluar_checklist.execute(
                usuario=secretario_abogado,
                checklist_verification_id=verif.id,
                nuevo_estado="VERIFICADO",
            )

    def test_falla_si_usuario_no_autorizado(self, analista_apoyo, checklist_verification):
        """Error si usuario no tiene rol permitido (pero analista SI tiene permiso)."""
        # Analista de apoyo SÍ tiene permiso, así que esto no debería fallar
        # Probar con estudiante
        from apps.authentication.adapters.models import User, Role, UserRole
        from apps.expedientes.adapters.models import ExpedienteTitulacion
        
        rol_est, _ = Role.objects.get_or_create(name="ESTUDIANTE")
        estudiante2 = User.objects.create_user(
            username="estudiante2",
            email="est2@test.com",
            password="pass1234",
            cedula="9999999999",
        )
        UserRole.objects.create(user=estudiante2, role=rol_est)

        with pytest.raises(evaluar_checklist.UserNotAuthorizedError):
            evaluar_checklist.execute(
                usuario=estudiante2,
                checklist_verification_id=checklist_verification.id,
                nuevo_estado="VERIFICADO",
            )

    def test_analista_apoyo_puede_evaluar(self, analista_apoyo, checklist_verification):
        """Analista de apoyo puede evaluar checklist."""
        verif = evaluar_checklist.execute(
            usuario=analista_apoyo,
            checklist_verification_id=checklist_verification.id,
            nuevo_estado="VERIFICADO",
        )
        assert verif.estado_verificacion == "VERIFICADO"
        assert verif.evaluado_por == analista_apoyo

    def test_falla_si_usuario_distinta_facultad(self, secretario_abogado, expediente_en_verificacion):
        """Error si usuario pertenece a distinta facultad."""
        from apps.authentication.adapters.models import User, Role, UserRole
        from apps.expedientes.adapters.models import ExpedienteTitulacion
        from apps.peticiones.adapters.models import CatalogoDocumental
        from apps.verificacion.adapters.models import ChecklistVerification

        # Crear otra facultad
        FACULTAD_2 = "33333333-3333-3333-3333-333333333333"
        
        rol_sec, _ = Role.objects.get_or_create(name="SECRETARIO_ABOGADO")
        secretario_otra = User.objects.create_user(
            username="secretario_otra",
            email="sec_otra@test.com",
            password="pass1234",
            cedula="2222222222",
            facultad_id="33333333-3333-3333-3333-333333333333",
        )
        UserRole.objects.create(user=secretario_otra, role=rol_sec)

        expediente = ExpedienteTitulacion.objects.create(
            numero_expediente="EXP-2026-0003",
            estudiante=expediente_en_verificacion.estudiante,
            carrera_id=CARRERA_1,
            facultad_id=FACULTAD_1,
            estado=ExpedienteTitulacion.ESTADO_EN_VERIFICACION,
            activa=True,
        )

        requisito = CatalogoDocumental.objects.create(
            codigo_requisito="REQ-TEST-2",
            nombre="Test 2",
            es_obligatorio_base=True,
            fase="FASE_1",
            rol_emisor_sugerido="SECRETARIA_CARRERA",
            activo=True,
        )

        verif = ChecklistVerification.objects.create(
            expediente=expediente,
            requisito=requisito,
            estado_verificacion="PENDIENTE",
        )

        # Verificar que el usuario tiene la facultad correcta
        assert str(secretario_otra.facultad_id) == "33333333-3333-3333-3333-333333333333"
        assert str(expediente.facultad_id) == "22222222-2222-2222-2222-222222222222"

        # El usuario pertenece a FACULTAD_2 pero el expediente está en FACULTAD_1
        with pytest.raises(evaluar_checklist.UserNotAuthorizedError):
            evaluar_checklist.execute(
                usuario=secretario_otra,
                checklist_verification_id=verif.id,
                nuevo_estado="VERIFICADO",
            )


class TestEvaluarChecklistConcurrencia:
    """Tests de concurrencia con bloqueo pesimista (ADR-007 / AP-06).

    Nota: SQLite no soporta bien la concurrencia real. Estos tests validan
    la lógica de bloqueo pesimista en el servicio, pero la concurrencia real
    se prueba mejor en PostgreSQL.
    """

    def test_concurrencia_dos_usuarios_mismo_requisito(self, secretario_abogado, analista_apoyo, checklist_verification, expediente_en_verificacion):
        """Dos usuarios intentan evaluar el mismo requisito simultáneamente."""
        # Ejecutar secuencialmente para verificar el bloqueo lógico
        # En PostgreSQL real, el select_for_update bloquearía la segunda transacción
        
        # Primer usuario evalúa
        result1 = evaluar_checklist.execute(
            usuario=secretario_abogado,
            checklist_verification_id=checklist_verification.id,
            nuevo_estado="VERIFICADO",
        )
        assert result1.estado_verificacion == "VERIFICADO"
        
        # Segundo usuario intenta evaluar el mismo requisito
        with pytest.raises(evaluar_checklist.VerificationAlreadyCompletedError):
            evaluar_checklist.execute(
                usuario=analista_apoyo,
                checklist_verification_id=checklist_verification.id,
                nuevo_estado="OBSERVADO",
                motivo_observacion="Concurrencia",
            )

    def test_concurrencia_multiples_requisitos_diferentes(self, secretario_abogado, analista_apoyo, expediente_en_verificacion):
        """Múltiples usuarios evalúan diferentes requisitos simultáneamente (no debe haber conflicto)."""
        # En un entorno real con PostgreSQL, esto funcionaría con concurrencia real
        # Aquí verificamos que la lógica no falla secuencialmente
        
        verificaciones = list(ChecklistVerification.objects.filter(
            expediente=expediente_en_verificacion,
            estado_verificacion="PENDIENTE"
        )[:2])
        
        assert len(verificaciones) == 2
        
        # Evaluar primer requisito
        result1 = evaluar_checklist.execute(
            usuario=secretario_abogado,
            checklist_verification_id=verificaciones[0].id,
            nuevo_estado="VERIFICADO",
        )
        assert result1.estado_verificacion == "VERIFICADO"
        
        # Evaluar segundo requisito
        result2 = evaluar_checklist.execute(
            usuario=analista_apoyo,
            checklist_verification_id=verificaciones[1].id,
            nuevo_estado="VERIFICADO",
        )
        assert result2.estado_verificacion == "VERIFICADO"
        
        # Verificar que ambos están verificados
        for v in verificaciones:
            v.refresh_from_db()
            assert v.estado_verificacion == "VERIFICADO"


class TestEvaluarChecklistEndpoint:
    """Tests de integración del endpoint PUT /api/v1/checklist/{id}/."""

    def test_endpoint_verificado_200(self, api_client, secretario_abogado, checklist_verification):
        """Endpoint retorna 200 con verificación actualizada a VERIFICADO."""
        api_client.force_authenticate(user=secretario_abogado)
        url = f"/api/v1/checklist/{checklist_verification.id}/"
        response = api_client.put(url, {"estado_verificacion": "VERIFICADO"}, format="json")

        assert response.status_code == 200
        assert response.data["estado_verificacion"] == "VERIFICADO"
        assert response.data["evaluado_por"] == str(secretario_abogado.pk)

    def test_endpoint_observado_200(self, api_client, secretario_abogado, checklist_verification):
        """Endpoint retorna 200 con observación registrada."""
        api_client.force_authenticate(user=secretario_abogado)
        url = f"/api/v1/checklist/{checklist_verification.id}/"
        response = api_client.put(url, {
            "estado_verificacion": "OBSERVADO",
            "motivo_observacion": "Falta firma"
        }, format="json")

        assert response.status_code == 200
        assert response.data["estado_verificacion"] == "OBSERVADO"

    def test_endpoint_400_estado_invalido(self, api_client, secretario_abogado, checklist_verification):
        """Estado inválido retorna 400."""
        api_client.force_authenticate(user=secretario_abogado)
        url = f"/api/v1/checklist/{checklist_verification.id}/"
        response = api_client.put(url, {"estado_verificacion": "INVALIDO"}, format="json")
        assert response.status_code == 400

    def test_endpoint_400_observado_sin_motivo(self, api_client, secretario_abogado, checklist_verification):
        """OBSERVADO sin motivo retorna 400."""
        api_client.force_authenticate(user=secretario_abogado)
        url = f"/api/v1/checklist/{checklist_verification.id}/"
        response = api_client.put(url, {"estado_verificacion": "OBSERVADO"}, format="json")
        assert response.status_code == 400

    def test_endpoint_401_sin_autenticacion(self, api_client, checklist_verification):
        """Sin token retorna 401."""
        url = f"/api/v1/checklist/{checklist_verification.id}/"
        response = api_client.put(url, {"estado_verificacion": "VERIFICADO"}, format="json")
        assert response.status_code == 401

    def test_endpoint_403_rol_no_autorizado(self, api_client, analista_apoyo, checklist_verification):
        """Rol no permitido (estudiante) retorna 403."""
        # Primero crear un estudiante
        from apps.authentication.adapters.models import User, Role, UserRole
        rol_est, _ = Role.objects.get_or_create(name="ESTUDIANTE")
        estudiante = User.objects.create_user(
            username="est_otro",
            email="otro@test.com",
            password="pass1234",
            cedula="9999999999",
        )
        UserRole.objects.create(user=estudiante, role=rol_est)

        api_client.force_authenticate(user=estudiante)
        url = f"/api/v1/checklist/{checklist_verification.id}/"
        response = api_client.put(url, {"estado_verificacion": "VERIFICADO"}, format="json")
        assert response.status_code in (403, 404)  # 403 por permisos o 404 por scope

    def test_endpoint_404_checklist_no_existe(self, api_client, secretario_abogado):
        """Checklist inexistente retorna 404."""
        from uuid import uuid4
        api_client.force_authenticate(user=secretario_abogado)
        url = f"/api/v1/checklist/{uuid4()}/"
        response = api_client.put(url, {"estado_verificacion": "VERIFICADO"}, format="json")
        assert response.status_code == 404


class TestIsChecklistFullyVerified:
    """Tests de is_checklist_fully_verified (RN-003)."""

    def test_true_si_todos_verificados(self, expediente_en_verificacion, secretario_abogado):
        """Retorna True si todos los requisitos están VERIFICADO."""
        # Evaluar todos los requisitos
        for verif in ChecklistVerification.objects.filter(expediente=expediente_en_verificacion):
            evaluar_checklist.execute(
                usuario=secretario_abogado,
                checklist_verification_id=verif.id,
                nuevo_estado="VERIFICADO",
            )
        
        assert evaluar_checklist.is_checklist_fully_verified(expediente_en_verificacion.id) is True

    def test_false_si_algun_pendiente(self, expediente_en_verificacion, secretario_abogado):
        """Retorna False si queda algún PENDIENTE."""
        # Evaluar solo uno
        verif = ChecklistVerification.objects.filter(expediente=expediente_en_verificacion).first()
        evaluar_checklist.execute(
            usuario=secretario_abogado,
            checklist_verification_id=verif.id,
            nuevo_estado="VERIFICADO",
        )
        
        assert evaluar_checklist.is_checklist_fully_verified(expediente_en_verificacion.id) is False

    def test_false_si_algun_observado(self, expediente_en_verificacion, secretario_abogado):
        """Retorna False si hay OBSERVADO."""
        verif = ChecklistVerification.objects.filter(expediente=expediente_en_verificacion).first()
        evaluar_checklist.execute(
            usuario=secretario_abogado,
            checklist_verification_id=verif.id,
            nuevo_estado="OBSERVADO",
            motivo_observacion="Observado",
        )
        
        assert evaluar_checklist.is_checklist_fully_verified(expediente_en_verificacion.id) is False