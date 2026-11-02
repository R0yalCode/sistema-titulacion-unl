"""Pruebas para T030: Subsanación y versionado N+1 de documentos observados (HU-008, RF-008, RN-011, CA-004).

Verifica:
- Carga de PDF válido para subsanar requisito OBSERVADO
- Incremento de versión N+1 y marca anterior como no vigente
- Reanudación del reloj de plazo laborable (AP-01)
- Cambio de estados: petición a CARGADO, expediente a EN_VERIFICACION
- Marcado de observación como resuelta
- Notificación al jurista/analista
- Validaciones de permisos, estados y archivos
"""

import io

import pytest
from django.db import transaction
from django.utils import timezone
from rest_framework.test import APIClient

from apps.authentication.adapters.models import (
    ROLE_ESTUDIANTE,
    ROLE_SECRETARIA_CARRERA,
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
    ESTADO_SOLICITADO,
    ESTADO_OBSERVADO,
    PeticionDocumental,
    DocumentoEntregado,
)
from apps.verificacion.adapters.models import (
    ChecklistVerification,
    ObservacionAccionable,
    ESTADO_VERIFICACION_PENDIENTE,
    ESTADO_VERIFICACION_VERIFICADO,
    ESTADO_VERIFICACION_OBSERVADO,
)
from apps.notificaciones.adapters.models import NotificacionInterna
from apps.verificacion.services import subsanar_requisito, evaluar_checklist
from apps.expedientes.domain.plazo_calculator import PlazoLaboralCalculator

pytestmark = pytest.mark.django_db

CARRERA_1 = "11111111-1111-1111-1111-111111111111"
FACULTAD_1 = "22222222-2222-2222-2222-222222222222"
FACULTAD_2 = "33333333-3333-3333-3333-333333333333"
PASSWORD = "pass1234"

# PDF válido mínimo para testing (PDF 1.4)
PDF_VALIDO = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>\nendobj\n4 0 obj\n<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>\nendobj\n5 0 obj\n<</Length 44>>\nstream\nBT /F1 24 Tf 100 700 Td (Test) Tj ET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000218 00000 n \n0000000277 00000 n \ntrailer\n<</Size 6/Root 1 0 R>>\nstartxref\n347\n%%EOF"

# PDF válido versión 1.7
PDF_VALIDO_V2 = b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>\nendobj\n4 0 obj\n<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>\nendobj\n5 0 obj\n<</Length 44>>\nstream\nBT /F1 24 Tf 100 700 Td (Test v1.7) Tj ET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000218 00000 n \n0000000277 00000 n \ntrailer\n<</Size 6/Root 1 0 R>>\nstartxref\n347\n%%EOF"

# Archivos inválidos para testing de seguridad
EJECUTABLE_RENOMBRADO = b"MZ\x90\x00"  # PE header (Windows executable)
IMAGEN_PNG_RENOMBRADA = b"\x89PNG\r\n\x1a\n"
IMAGEN_JPEG_RENOMBRADA = b"\xff\xd8\xff\xe0"
TEXTO_PLANO = b"Esto no es un PDF"
ARCHIVO_VACIO = b""
ARCHIVO_GRANDE = b"%PDF-1.4\n" + b"x" * (11 * 1024 * 1024)  # 11 MB


def auth_client(user):
    from rest_framework.test import APIClient
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
        username="secretario_test",
        email="sec@test.com",
        password=PASSWORD,
        cedula="1234567893",
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
        facultad_id=FACULTAD_1,
    )
    UserRole.objects.create(user=user, role=rol_analista_apoyo)
    return user


@pytest.fixture
def expediente_observada(estudiante, secretario_abogado):
    """Crea un expediente en estado OBSERVADA con una observación pendiente."""
    from apps.peticiones.adapters.models import CatalogoDocumental, ESTADO_CARGADO
    from django.utils import timezone
    from datetime import timedelta

    # Set fecha_ultima_pausa to 5 days ago to simulate pause duration
    fecha_pausa = timezone.now() - timedelta(days=5)
    fecha_recepcion = timezone.now() - timedelta(days=10)

    expediente = ExpedienteTitulacion.objects.create(
        numero_expediente="EXP-2026-0001",
        estudiante=estudiante,
        carrera_id=CARRERA_1,
        facultad_id=FACULTAD_1,
        estado=ExpedienteTitulacion.ESTADO_OBSERVADA,
        activa=True,
        fecha_ultima_pausa=fecha_pausa,  # Simular pausa al observar (5 días atrás)
        fecha_recepcion=fecha_recepcion,
    )

    requisito = CatalogoDocumental.objects.create(
        codigo_requisito="REQ-01",
        nombre="Requisito 1",
        descripcion="Record academico legalizado otorgado por la Secretaria de Carrera.",
        es_obligatorio_base=True,
        fase="FASE_1",
        rol_emisor_sugerido="SECRETARIA_CARRERA",
        activo=True,
    )

    peticion = PeticionDocumental.objects.create(
        expediente=expediente,
        requisito=requisito,
        estado_peticion="OBSERVADO",
        dependencia_emisora="SECRETARIA_CARRERA",
    )

    # Crear documento original (versión 1)
    DocumentoEntregado.objects.create(
        peticion=peticion,
        version=1,
        archivo_path=f"expedientes/2026/{expediente.id}/v1.pdf",
        nombre_original="v1.pdf",
        tamanio_bytes=len(PDF_VALIDO),
        hash_sha256="a" * 64,
        tipo_mime="application/pdf",
        subido_por=estudiante,
        es_vigente=True,
    )

    # Crear observación pendiente
    ObservacionAccionable.objects.create(
        expediente=expediente,
        peticion=peticion,
        registrada_por=secretario_abogado,
        motivo_observacion="Documento ilegible",
        resuelta=False,
    )

    # Crear verificación en OBSERVADO
    ChecklistVerification.objects.create(
        expediente=expediente,
        requisito=requisito,
        estado_verificacion="OBSERVADO",
        evaluado_por=secretario_abogado,
    )

    return expediente


CARRERA_1 = "11111111-1111-1111-1111-111111111111"
FACULTAD_1 = "22222222-2222-2222-2222-222222222222"
FACULTAD_2 = "33333333-3333-3333-3333-333333333333"
PASSWORD = "pass1234"

# PDF válido mínimo para testing (PDF 1.4)
PDF_VALIDO = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>\nendobj\n4 0 obj\n<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>\nendobj\n5 0 obj\n<</Length 44>>\nstream\nBT /F1 24 Tf 100 700 Td (Test) Tj ET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000218 00000 n \n0000000277 00000 n \ntrailer\n<</Size 6/Root 1 0 R>>\nstartxref\n347\n%%EOF"

# PDF válido versión 1.7
PDF_VALIDO_V2 = b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>\nendobj\n4 0 obj\n<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>\nendobj\n5 0 obj\n<</Length 44>>\nstream\nBT /F1 24 Tf 100 700 Td (Test v1.7) Tj ET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000218 00000 n \n0000000277 00000 n \ntrailer\n<</Size 6/Root 1 0 R>>\nstartxref\n347\n%%EOF"

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


class TestSubsanarRequisitoService:
    """Tests del servicio subsanar_requisito (T030)."""

    def test_subsanar_exitoso_estudiante(self, estudiante, expediente_observada):
        """Estudiante puede subsanar requisito observado."""
        checklist_verif = ChecklistVerification.objects.filter(
            expediente=expediente_observada, estado_verificacion="OBSERVADO"
        ).first()

        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "v2_corregido.pdf"

        documento = subsanar_requisito.execute(
            usuario=estudiante,
            checklist_verification_id=checklist_verif.id,
            archivo=archivo,
            nombre_original="v2_corregido.pdf",
        )

        assert documento.peticion.estado_peticion == "CARGADO"
        assert documento.version == 2
        assert documento.es_vigente is True
        assert documento.subido_por == estudiante

        # Verificar expediente en EN_VERIFICACION
        expediente = expediente_observada
        expediente.refresh_from_db()
        assert expediente.estado == ExpedienteTitulacion.ESTADO_EN_VERIFICACION

        # Verificar checklist en PENDIENTE
        checklist_verif = ChecklistVerification.objects.get(pk=checklist_verif.id)
        assert checklist_verif.estado_verificacion == "PENDIENTE"

        # Verificar observación resuelta
        observacion = ObservacionAccionable.objects.filter(peticion__expediente=expediente_observada).first()
        assert observacion.resuelta is True
        assert observacion.fecha_resolucion is not None

        # Verificar notificación al estudiante (jurista/analista)
        notificacion = NotificacionInterna.objects.filter(
            usuario_destino=expediente_observada.estudiante,
            expediente=expediente_observada,
        ).first()
        assert notificacion is not None
        assert "Subsanación recibida" in notificacion.titulo

    def test_subsanar_exitoso_secretaria_carrera(self, secretaria_carrera, expediente_observada):
        """Secretaria de Carrera de la misma carrera puede subsanar."""
        checklist_verif = ChecklistVerification.objects.filter(
            expediente=expediente_observada, estado_verificacion="OBSERVADO"
        ).first()

        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "certificado.pdf"

        documento = subsanar_requisito.execute(
            usuario=secretaria_carrera,
            checklist_verification_id=checklist_verif.id,
            archivo=archivo,
            nombre_original="certificado.pdf",
        )

        assert documento.subido_por == secretaria_carrera
        assert documento.es_vigente is True

    def test_versionado_n_mas_1(self, estudiante, expediente_observada):
        """Múltiples subsanaciones incrementan versión correctamente."""
        checklist_verif = ChecklistVerification.objects.filter(
            expediente=expediente_observada, estado_verificacion="OBSERVADO"
        ).first()

        # Primera subsanación
        archivo1 = io.BytesIO(PDF_VALIDO)
        archivo1.name = "v2.pdf"
        doc1 = subsanar_requisito.execute(
            usuario=estudiante,
            checklist_verification_id=checklist_verif.id,
            archivo=archivo1,
            nombre_original="v2.pdf",
        )
        assert doc1.version == 2
        assert doc1.es_vigente is True

        # Cambiar estado de vuelta a OBSERVADA para segunda subsanación
        expediente = expediente_observada
        expediente.estado = ExpedienteTitulacion.ESTADO_OBSERVADA
        expediente.save()
        peticion = expediente.peticiones_documentales.first()
        peticion.estado_peticion = "OBSERVADO"
        peticion.save()

        ChecklistVerification.objects.filter(
            expediente=expediente, requisito=checklist_verif.requisito
        ).update(estado_verificacion="OBSERVADO")

        ObservacionAccionable.objects.filter(peticion=peticion).update(resuelta=False)

        # Segunda subsanación
        archivo2 = io.BytesIO(PDF_VALIDO_V2)
        archivo2.name = "v3.pdf"
        doc2 = subsanar_requisito.execute(
            usuario=estudiante,
            checklist_verification_id=checklist_verif.id,
            archivo=archivo2,
            nombre_original="v3.pdf",
        )

        assert doc2.version == 3
        assert doc2.es_vigente is True

        # Verificar que v1 ya no es vigente
        doc1.refresh_from_db()
        assert doc1.es_vigente is False

    def test_falla_si_expediente_no_observada(self, estudiante, expediente_observada):
        """Error si expediente no está en OBSERVADA."""
        from apps.expedientes.adapters.models import ExpedienteTitulacion
        from apps.peticiones.adapters.models import CatalogoDocumental, PeticionDocumental
        from apps.verificacion.adapters.models import ChecklistVerification

        expediente = ExpedienteTitulacion.objects.create(
            numero_expediente="EXP-2026-0002",
            estudiante=expediente_observada.estudiante,
            carrera_id=CARRERA_1,
            facultad_id=FACULTAD_1,
            estado=ExpedienteTitulacion.ESTADO_ENVIADA,  # No OBSERVADA
            activa=True,
        )

        requisito = CatalogoDocumental.objects.create(
            codigo_requisito="REQ-TEST-2",
            nombre="Requisito 2",
            es_obligatorio_base=True,
            fase="FASE_1",
            rol_emisor_sugerido="SECRETARIA_CARRERA",
            activo=True,
        )

        peticion = PeticionDocumental.objects.create(
            expediente=expediente,
            requisito=requisito,
            estado_peticion="OBSERVADO",
            dependencia_emisora="SECRETARIA_CARRERA",
        )

        verif = ChecklistVerification.objects.create(
            expediente=expediente,
            requisito=requisito,
            estado_verificacion="OBSERVADO",
        )

        archivo = io.BytesIO(b"%PDF-1.4\ncontent")
        archivo.name = "test.pdf"

        with pytest.raises(subsanar_requisito.SubsanacionNoPermitidaError):
            subsanar_requisito.execute(
                usuario=estudiante,
                checklist_verification_id=verif.id,
                archivo=io.BytesIO(b"%PDF-1.4\ncontent"),
                nombre_original="test.pdf",
            )

    def test_falla_si_verificacion_no_observado(self, expediente_observada):
        """Error si verificación no está en OBSERVADO."""
        checklist_verif = ChecklistVerification.objects.filter(
            expediente=expediente_observada, estado_verificacion="OBSERVADO"
        ).first()
        checklist_verif.estado_verificacion = "VERIFICADO"
        checklist_verif.save()

        archivo = io.BytesIO(b"%PDF-1.4\ncontent")
        archivo.name = "test.pdf"

        with pytest.raises(subsanar_requisito.SubsanacionNoPermitidaError):
            subsanar_requisito.execute(
                usuario=expediente_observada.estudiante,
                checklist_verification_id=checklist_verif.id,
                archivo=io.BytesIO(b"%PDF-1.4\ncontent"),
                nombre_original="test.pdf",
            )

    def test_falla_si_usuario_no_autorizado(self, expediente_observada):
        """Error si usuario no tiene rol permitido."""
        from apps.authentication.adapters.models import User, Role, UserRole

        rol_est, _ = Role.objects.get_or_create(name="ESTUDIANTE")
        otro_estudiante = User.objects.create_user(
            username="otro_est",
            email="otro@test.com",
            password="pass1234",
            cedula="9999999999",
        )
        UserRole.objects.create(user=otro_estudiante, role=Role.objects.get(name="ESTUDIANTE"))

        checklist_verif = ChecklistVerification.objects.filter(
            expediente=expediente_observada, estado_verificacion="OBSERVADO"
        ).first()

        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "test.pdf"

        with pytest.raises(subsanar_requisito.UsuarioNoAutorizadoError):
            subsanar_requisito.execute(
                usuario=otro_estudiante,
                checklist_verification_id=checklist_verif.id,
                archivo=archivo,
                nombre_original="test.pdf",
            )

    def test_falla_si_archivo_invalido(self, estudiante, expediente_observada):
        """Rechaza archivos no PDF (magic bytes)."""
        checklist_verif = ChecklistVerification.objects.filter(
            expediente=expediente_observada, estado_verificacion="OBSERVADO"
        ).first()

        archivo = io.BytesIO(EJECUTABLE_RENOMBRADO)
        archivo.name = "malware.pdf"

        with pytest.raises(subsanar_requisito.ValidacionPDFError) as exc_info:
            subsanar_requisito.execute(
                usuario=estudiante,
                checklist_verification_id=checklist_verif.id,
                archivo=archivo,
                nombre_original="malware.pdf",
            )
        assert exc_info.value.code == "invalid_magic_bytes"

    def test_falla_si_archivo_mayor_10mb(self, estudiante, expediente_observada):
        """Rechaza archivos > 10 MB."""
        checklist_verif = ChecklistVerification.objects.filter(
            expediente=expediente_observada, estado_verificacion="OBSERVADO"
        ).first()

        archivo = io.BytesIO(ARCHIVO_GRANDE)
        archivo.name = "grande.pdf"

        with pytest.raises(subsanar_requisito.ValidacionPDFError) as exc_info:
            subsanar_requisito.execute(
                usuario=estudiante,
                checklist_verification_id=checklist_verif.id,
                archivo=archivo,
                nombre_original="grande.pdf",
            )
        assert exc_info.value.code == "file_too_large"


class TestSubsanarEndpoint:
    """Tests de integración del endpoint POST /api/v1/checklist/{id}/subsanar/."""

    def test_endpoint_201_created(self, api_client, estudiante, expediente_observada):
        """Endpoint retorna 201 con metadata del documento subsanado."""
        checklist_verif = ChecklistVerification.objects.filter(
            expediente=expediente_observada, estado_verificacion="OBSERVADO"
        ).first()

        client = auth_client(estudiante)
        url = f"/api/v1/checklist/{checklist_verif.id}/subsanar/"
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "v2.pdf"

        response = client.post(url, {"archivo": archivo}, format="multipart")

        assert response.status_code == 201
        assert response.data["version"] == 2
        assert response.data["nombre_original"] == "v2.pdf"
        assert response.data["es_vigente"] is True

    def test_endpoint_400_archivo_invalido(self, api_client, estudiante, expediente_observada):
        """Archivo con magic bytes inválidos retorna 400."""
        checklist_verif = ChecklistVerification.objects.filter(
            expediente=expediente_observada, estado_verificacion="OBSERVADO"
        ).first()

        client = auth_client(estudiante)
        url = f"/api/v1/checklist/{checklist_verif.id}/subsanar/"
        archivo = io.BytesIO(EJECUTABLE_RENOMBRADO)
        archivo.name = "malware.pdf"

        response = client.post(url, {"archivo": archivo}, format="multipart")
        assert response.status_code == 400

    def test_endpoint_400_archivo_mayor_10mb(self, api_client, estudiante, expediente_observada):
        """Archivo > 10 MB retorna 400."""
        checklist_verif = ChecklistVerification.objects.filter(
            expediente=expediente_observada, estado_verificacion="OBSERVADO"
        ).first()

        client = auth_client(estudiante)
        url = f"/api/v1/checklist/{checklist_verif.id}/subsanar/"
        archivo = io.BytesIO(ARCHIVO_GRANDE)
        archivo.name = "grande.pdf"

        response = client.post(url, {"archivo": archivo}, format="multipart")
        assert response.status_code == 400

    def test_endpoint_401_sin_autenticacion(self, expediente_observada):
        """Sin token retorna 401."""
        checklist_verif = ChecklistVerification.objects.filter(
            estado_verificacion="OBSERVADO"
        ).first()

        client = APIClient()
        url = f"/api/v1/checklist/{checklist_verif.id}/subsanar/"
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "test.pdf"

        response = client.post(url, {"archivo": archivo}, format="multipart")
        assert response.status_code == 401

    def test_endpoint_403_rol_no_autorizado(self, api_client, estudiante, expediente_observada):
        """Rol no permitido (ej. ANALISTA_APOYO) retorna 403."""
        from apps.authentication.adapters.models import User, Role, UserRole
        from apps.expedientes.adapters.models import ExpedienteTitulacion
        from apps.peticiones.adapters.models import CatalogoDocumental, PeticionDocumental
        from apps.verificacion.adapters.models import ChecklistVerification

        # Create expediente for different career
        expediente_otra_carrera = ExpedienteTitulacion.objects.create(
            numero_expediente="EXP-2026-0003",
            estudiante=estudiante,
            carrera_id="44444444-4444-4444-4444-444444444444",
            facultad_id=FACULTAD_1,
            estado=ExpedienteTitulacion.ESTADO_OBSERVADA,
            activa=True,
        )

        requisito = CatalogoDocumental.objects.create(
            codigo_requisito="REQ-TEST-3",
            nombre="Requisito 3",
            es_obligatorio_base=True,
            fase="FASE_1",
            rol_emisor_sugerido="SECRETARIA_CARRERA",
            activo=True,
        )

        peticion = PeticionDocumental.objects.create(
            expediente=expediente_otra_carrera,
            requisito=requisito,
            estado_peticion="OBSERVADO",
            dependencia_emisora="SECRETARIA_CARRERA",
        )

        checklist_verif = ChecklistVerification.objects.create(
            expediente=expediente_otra_carrera,
            requisito=requisito,
            estado_verificacion="OBSERVADO",
        )

        # Create user from different career (not owner, not same career)
        rol_est, _ = Role.objects.get_or_create(name="ESTUDIANTE")
        otro_estudiante = User.objects.create_user(
            username="otro_est",
            email="otro@test.com",
            password=PASSWORD,
            cedula="9999999999",
            carrera_id="44444444-4444-4444-4444-444444444444",
            facultad_id=FACULTAD_2,
        )
        UserRole.objects.create(user=otro_estudiante, role=Role.objects.get(name="ESTUDIANTE"))

        client = auth_client(otro_estudiante)
        url = f"/api/v1/checklist/{checklist_verif.id}/subsanar/"
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "test.pdf"

        response = client.post(url, {"archivo": archivo}, format="multipart")
        assert response.status_code in (403, 404)

    def test_endpoint_404_checklist_no_existe(self, api_client, estudiante):
        """Checklist inexistente retorna 404."""
        from uuid import uuid4
        client = auth_client(estudiante)
        url = f"/api/v1/checklist/{uuid4()}/subsanar/"
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "test.pdf"

        response = client.post(url, {"archivo": archivo}, format="multipart")
        assert response.status_code == 404


class TestPausaReanudaReloj:
    """Tests de integración: pausa al observar, reanuda al subsanar."""

    def test_pausa_al_observar_reanuda_al_subsanar(self, estudiante, expediente_observada):
        """El reloj se pausa al observar y se reanuda al subsanar."""
        checklist_verif = ChecklistVerification.objects.filter(
            expediente=expediente_observada, estado_verificacion="OBSERVADO"
        ).first()

        # Verificar que el expediente tiene fecha_ultima_pausa (pausado al observar)
        expediente = expediente_observada
        expediente.refresh_from_db()
        assert expediente.fecha_ultima_pausa is not None

        # Subsanar
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "test.pdf"
        subsanar_requisito.execute(
            usuario=estudiante,
            checklist_verification_id=checklist_verif.id,
            archivo=archivo,
            nombre_original="test.pdf",
        )

        # Verificar que se reanudó el reloj (fecha_ultima_pausa = None)
        expediente.refresh_from_db()
        assert expediente.fecha_ultima_pausa is None

        # Verificar que el plazo se extendió correctamente
        calc = PlazoLaboralCalculator()
        fecha_limite = calc.calcular_fecha_limite(expediente.fecha_recepcion)
        assert expediente.fecha_limite_atencion >= fecha_limite