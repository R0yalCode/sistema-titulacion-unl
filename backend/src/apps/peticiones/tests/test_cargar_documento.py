"""Pruebas para T023: Carga de certificados PDF con registro subido_por (HU-003, DEC-02).

Verifica:
- Carga exitosa de PDF válido retorna 201 con metadata
- Validación de magic bytes y tamaño (integración con T022)
- Versionado N+1 y marca de vigencia
- Actualización de estado de petición a CARGADO
- Registro de subido_por (usuario y rol)
- Permisos (solo estudiante propietario o SECRETARIA_CARRERA)
- Rechazo de archivos inválidos (ejecutables, >10MB, etc.)
"""

import io

import pytest
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
    ESTADO_CARGADO,
    ESTADO_PENDIENTE,
    ESTADO_SOLICITADO,
    DocumentoEntregado,
    PeticionDocumental,
)
from apps.peticiones.services import cargar_documento
from core.adapters.pdf_validation import PDFValidationError

pytestmark = pytest.mark.django_db

CARRERA_1 = "11111111-1111-1111-1111-111111111111"
FACULTAD_1 = "22222222-2222-2222-2222-222222222222"
PASSWORD = "pass1234"

# PDF válido mínimo para testing
PDF_VALIDO = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>\nendobj\n4 0 obj\n<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>\nendobj\n5 0 obj\n<</Length 44>>\nstream\nBT /F1 24 Tf 100 700 Td (Test) Tj ET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000218 00000 n \n0000000277 00000 n \ntrailer\n<</Size 6/Root 1 0 R>>\nstartxref\n347\n%%EOF"

# Archivos inválidos
EJECUTABLE_RENOMBRADO = b"MZ\x90\x00"  # PE header
IMAGEN_PNG_RENOMBRADA = b"\x89PNG\r\n\x1a\n"
ARCHIVO_GRANDE = b"%PDF-1.4\n" + b"x" * (11 * 1024 * 1024)  # 11 MB


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


@pytest.fixture
def peticion_solicitada(peticion_pendiente):
    peticion_pendiente.estado_peticion = ESTADO_SOLICITADO
    peticion_pendiente.save()
    return peticion_pendiente


class TestCargarDocumentoService:
    """Tests del caso de uso cargar_documento (T023)."""

    def test_carga_exitosa_estudiante_retorna_documento_con_metadata(
        self, estudiante, peticion_pendiente
    ):
        """Estudiante propietario puede cargar PDF válido."""
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "record_academico.pdf"

        documento = cargar_documento.execute(
            usuario=estudiante,
            peticion_id=peticion_pendiente.id,
            archivo=archivo,
            nombre_original="record_academico.pdf",
        )

        assert documento.peticion == peticion_pendiente
        assert documento.version == 1
        assert documento.nombre_original == "record_academico.pdf"
        assert documento.tamanio_bytes == len(PDF_VALIDO)
        assert len(documento.hash_sha256) == 64
        assert documento.tipo_mime == "application/pdf"
        assert documento.subido_por == estudiante
        assert documento.es_vigente is True

        # Verificar que petición cambió a CARGADO
        peticion_pendiente.refresh_from_db()
        assert peticion_pendiente.estado_peticion == ESTADO_CARGADO

    def test_carga_exitosa_secretaria_carrera(self, secretaria_carrera, peticion_pendiente):
        """Secretaria de Carrera de la misma carrera puede cargar."""
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "certificado.pdf"

        documento = cargar_documento.execute(
            usuario=secretaria_carrera,
            peticion_id=peticion_pendiente.id,
            archivo=archivo,
            nombre_original="certificado.pdf",
        )

        assert documento.subido_por == secretaria_carrera
        assert documento.es_vigente is True

    def test_carga_con_peticion_en_solicitado(self, estudiante, peticion_solicitada):
        """Permite carga cuando petición está en SOLICITADO."""
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "doc.pdf"

        documento = cargar_documento.execute(
            usuario=estudiante,
            peticion_id=peticion_solicitada.id,
            archivo=archivo,
            nombre_original="doc.pdf",
        )

        assert documento.es_vigente is True
        peticion_solicitada.refresh_from_db()
        assert peticion_solicitada.estado_peticion == ESTADO_CARGADO

    def test_versionado_n_mas_1_marca_anterior_no_vigente(
        self, estudiante, peticion_pendiente
    ):
        """Segunda carga incrementa versión y marca anterior como no vigente."""
        # Primera carga
        archivo1 = io.BytesIO(PDF_VALIDO)
        archivo1.name = "v1.pdf"
        doc1 = cargar_documento.execute(
            usuario=estudiante,
            peticion_id=peticion_pendiente.id,
            archivo=archivo1,
            nombre_original="v1.pdf",
        )
        assert doc1.version == 1
        assert doc1.es_vigente is True

        # Segunda carga (simula subsanación)
        archivo2 = io.BytesIO(PDF_VALIDO)
        archivo2.name = "v2.pdf"
        doc2 = cargar_documento.execute(
            usuario=estudiante,
            peticion_id=peticion_pendiente.id,
            archivo=archivo2,
            nombre_original="v2.pdf",
        )

        assert doc2.version == 2
        assert doc2.es_vigente is True

        # Verificar que v1 ya no es vigente
        doc1.refresh_from_db()
        assert doc1.es_vigente is False

    def test_falla_si_peticion_no_existe(self, estudiante):
        """Error si peticion_id no existe."""
        from uuid import uuid4
        archivo = io.BytesIO(PDF_VALIDO)
        with pytest.raises(cargar_documento.PeticionNoEncontradaError):
            cargar_documento.execute(estudiante, uuid4(), archivo, "test.pdf")

    def test_falla_si_peticion_en_estado_invalido(
        self, estudiante, peticion_pendiente
    ):
        """Error si petición está en estado que no permite carga (ej. VERIFICADO)."""
        from apps.peticiones.adapters.models import ESTADO_VERIFICADO

        peticion_pendiente.estado_peticion = ESTADO_VERIFICADO
        peticion_pendiente.save()

        archivo = io.BytesIO(PDF_VALIDO)
        with pytest.raises(cargar_documento.EstadoPeticionInvalidoError):
            cargar_documento.execute(estudiante, peticion_pendiente.id, archivo, "test.pdf")

    def test_falla_si_usuario_no_autorizado(
        self, secretario_abogado, peticion_pendiente
    ):
        """Error si usuario no es estudiante propietario ni secretaria de carrera."""
        archivo = io.BytesIO(PDF_VALIDO)
        with pytest.raises(cargar_documento.UsuarioNoAutorizadoError):
            cargar_documento.execute(secretario_abogado, peticion_pendiente.id, archivo, "test.pdf")

    def test_falla_si_estudiante_ajeno(self, rol_estudiante, peticion_pendiente):
        """Estudiante que no es el propietario no puede cargar."""
        otro_estudiante = User.objects.create_user(
            username="otro_estudiante",
            email="otro@test.com",
            password=PASSWORD,
            cedula="9999999999",
        )
        UserRole.objects.create(user=otro_estudiante, role=rol_estudiante)

        archivo = io.BytesIO(PDF_VALIDO)
        with pytest.raises(cargar_documento.UsuarioNoAutorizadoError):
            cargar_documento.execute(otro_estudiante, peticion_pendiente.id, archivo, "test.pdf")

    def test_rechaza_ejecutable_renombrado_como_pdf(self, estudiante, peticion_pendiente):
        """Archivo .exe renombrado como .pdf es rechazado (magic bytes)."""
        archivo = io.BytesIO(EJECUTABLE_RENOMBRADO)
        archivo.name = "malware.pdf"

        with pytest.raises(cargar_documento.ValidacionPDFError) as exc_info:
            cargar_documento.execute(estudiante, peticion_pendiente.id, archivo, "malware.pdf")
        assert exc_info.value.code == "invalid_magic_bytes"

    def test_rechaza_png_renombrado_como_pdf(self, estudiante, peticion_pendiente):
        """Imagen PNG renombrada como .pdf es rechazada."""
        archivo = io.BytesIO(IMAGEN_PNG_RENOMBRADA)
        archivo.name = "imagen.pdf"

        with pytest.raises(cargar_documento.ValidacionPDFError) as exc_info:
            cargar_documento.execute(estudiante, peticion_pendiente.id, archivo, "imagen.pdf")
        assert exc_info.value.code == "invalid_magic_bytes"

    def test_rechaza_archivo_mayor_10mb(self, estudiante, peticion_pendiente):
        """Archivo > 10 MB es rechazado."""
        archivo = io.BytesIO(ARCHIVO_GRANDE)
        archivo.name = "grande.pdf"

        with pytest.raises(cargar_documento.ValidacionPDFError) as exc_info:
            cargar_documento.execute(estudiante, peticion_pendiente.id, archivo, "grande.pdf")
        assert exc_info.value.code == "file_too_large"


class TestCargarDocumentoEndpoint:
    """Tests de integración del endpoint POST /api/v1/peticiones/{id}/documento/."""

    def test_endpoint_201_created_con_metadata(self, estudiante, peticion_pendiente):
        """Endpoint retorna 201 con metadata del documento."""
        client = auth_client(estudiante)
        url = f"/api/v1/peticiones/{peticion_pendiente.id}/documento/"
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "test.pdf"

        response = client.post(url, {"archivo": archivo}, format="multipart")

        assert response.status_code == 201
        assert response.data["version"] == 1
        assert response.data["nombre_original"] == "test.pdf"
        assert response.data["tamanio_bytes"] == len(PDF_VALIDO)
        assert len(response.data["hash_sha256"]) == 64
        assert response.data["tipo_mime"] == "application/pdf"
        assert response.data["es_vigente"] is True
        assert "subido_por_username" in response.data

    def test_endpoint_actualiza_estado_peticion_a_cargado(
        self, estudiante, peticion_pendiente
    ):
        """Endpoint actualiza estado de petición a CARGADO."""
        client = auth_client(estudiante)
        url = f"/api/v1/peticiones/{peticion_pendiente.id}/documento/"
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "test.pdf"

        client.post(url, {"archivo": archivo}, format="multipart")

        peticion_pendiente.refresh_from_db()
        assert peticion_pendiente.estado_peticion == ESTADO_CARGADO

    def test_endpoint_401_sin_autenticacion(self, peticion_pendiente):
        """Sin token retorna 401."""
        client = APIClient()
        url = f"/api/v1/peticiones/{peticion_pendiente.id}/documento/"
        archivo = io.BytesIO(PDF_VALIDO)
        response = client.post(url, {"archivo": archivo}, format="multipart")
        assert response.status_code == 401

    def test_endpoint_403_rol_no_autorizado(
        self, secretario_abogado, peticion_pendiente
    ):
        """Rol no autorizado retorna 403."""
        client = auth_client(secretario_abogado)
        url = f"/api/v1/peticiones/{peticion_pendiente.id}/documento/"
        archivo = io.BytesIO(PDF_VALIDO)
        response = client.post(url, {"archivo": archivo}, format="multipart")
        assert response.status_code == 403

    def test_endpoint_400_archivo_invalido_magic_bytes(
        self, estudiante, peticion_pendiente
    ):
        """Archivo con magic bytes inválidos retorna 400."""
        client = auth_client(estudiante)
        url = f"/api/v1/peticiones/{peticion_pendiente.id}/documento/"
        archivo = io.BytesIO(EJECUTABLE_RENOMBRADO)
        archivo.name = "malware.pdf"

        response = client.post(url, {"archivo": archivo}, format="multipart")
        assert response.status_code == 400
        assert "magic" in str(response.data).lower() or "invalid" in str(response.data).lower()

    def test_endpoint_400_archivo_mayor_10mb(self, estudiante, peticion_pendiente):
        """Archivo > 10 MB retorna 400."""
        client = auth_client(estudiante)
        url = f"/api/v1/peticiones/{peticion_pendiente.id}/documento/"
        archivo = io.BytesIO(ARCHIVO_GRANDE)
        archivo.name = "grande.pdf"

        response = client.post(url, {"archivo": archivo}, format="multipart")
        assert response.status_code == 400

    def test_endpoint_404_peticion_no_en_ambito(self, estudiante, peticion_pendiente):
        """Estudiante no puede cargar en petición de expediente ajeno (IDOR)."""
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
        url = f"/api/v1/peticiones/{peticion_pendiente.id}/documento/"
        archivo = io.BytesIO(PDF_VALIDO)
        response = client.post(url, {"archivo": archivo}, format="multipart")
        assert response.status_code == 404

    def test_endpoint_versionado_n_mas_1(self, estudiante, peticion_pendiente):
        """Múltiples cargas incrementan versión correctamente via endpoint."""
        client = auth_client(estudiante)
        url = f"/api/v1/peticiones/{peticion_pendiente.id}/documento/"

        # Primera carga
        archivo1 = io.BytesIO(PDF_VALIDO)
        archivo1.name = "v1.pdf"
        response1 = client.post(url, {"archivo": archivo1}, format="multipart")
        assert response1.status_code == 201
        assert response1.data["version"] == 1

        # Segunda carga
        archivo2 = io.BytesIO(PDF_VALIDO)
        archivo2.name = "v2.pdf"
        response2 = client.post(url, {"archivo": archivo2}, format="multipart")
        assert response2.status_code == 201
        assert response2.data["version"] == 2

        # Verificar que solo la v2 es vigente
        docs = DocumentoEntregado.objects.filter(peticion=peticion_pendiente).order_by("version")
        assert docs.count() == 2
        assert docs[0].es_vigente is False  # v1
        assert docs[1].es_vigente is True   # v2