"""Suite de pruebas de integración para ingestión, validación PDF y descarga segura (T025).

Tests de validación de *magic bytes*, rechazo de archivos >10 MB,
versionado de documentos y descargas protegidas.

Principio C-006: almacenamiento privado, validación estricta en servidor.
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
from apps.peticiones.services import cargar_documento, solicitar_emision
from core.adapters.local_storage import archivo_existe, obtener_ruta_absoluta

pytestmark = pytest.mark.django_db

CARRERA_1 = "11111111-1111-1111-1111-111111111111"
FACULTAD_1 = "22222222-2222-2222-2222-222222222222"
PASSWORD = "pass1234"

# PDF válido mínimo para testing (PDF 1.4)
PDF_VALIDO = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>\nendobj\n4 0 obj\n<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>\nendobj\n5 0 obj\n<</Length 44>>\nstream\nBT /F1 24 Tf 100 700 Td (Test) Tj ET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000218 00000 n \n0000000277 00000 n \ntrailer\n<</Size 6/Root 1 0 R>>\nstartxref\n347\n%%EOF"

# PDF válido versión 1.7
PDF_VALIDO_17 = b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>\nendobj\n4 0 obj\n<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>\nendobj\n5 0 obj\n<</Length 44>>\nstream\nBT /F1 24 Tf 100 700 Td (Test v1.7) Tj ET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000218 00000 n \n0000000277 00000 n \ntrailer\n<</Size 6/Root 1 0 R>>\nstartxref\n347\n%%EOF"

# Archivos inválidos para testing de seguridad
EJECUTABLE_RENOMBRADO = b"MZ\x90\x00"  # PE header (Windows executable)
IMAGEN_PNG_RENOMBRADA = b"\x89PNG\r\n\x1a\n"  # PNG header
IMAGEN_JPEG_RENOMBRADA = b"\xff\xd8\xff\xe0"  # JPEG header
TEXTO_PLANO = b"Esto no es un PDF"
ARCHIVO_VACIO = b""
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
    from apps.peticiones.adapters.models import CatalogoDocumental, ESTADO_PENDIENTE

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


class TestValidacionMagicBytes:
    """Tests de validación de magic bytes PDF (EX-005, RNF-004)."""

    def test_pdf_valido_pasa_validacion(self, estudiante, peticion_pendiente):
        """PDF con header %PDF- válido es aceptado."""
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "documento.pdf"

        documento = cargar_documento.execute(
            usuario=estudiante,
            peticion_id=peticion_pendiente.id,
            archivo=archivo,
            nombre_original="documento.pdf",
        )

        assert documento.tipo_mime == "application/pdf"
        assert len(documento.hash_sha256) == 64

    def test_pdf_version_17_pasa_validacion(self, estudiante, peticion_pendiente):
        """PDF versión 1.7 es aceptado."""
        archivo = io.BytesIO(PDF_VALIDO_17)
        archivo.name = "documento_v17.pdf"

        documento = cargar_documento.execute(
            usuario=estudiante,
            peticion_id=peticion_pendiente.id,
            archivo=archivo,
            nombre_original="documento_v17.pdf",
        )

        assert documento.tipo_mime == "application/pdf"

    def test_ejecutable_renombrado_rechazado(self, estudiante, peticion_pendiente):
        """Ejecutable .exe renombrado como .pdf es rechazado (EX-005)."""
        archivo = io.BytesIO(EJECUTABLE_RENOMBRADO)
        archivo.name = "malware.pdf"

        with pytest.raises(cargar_documento.ValidacionPDFError) as exc_info:
            cargar_documento.execute(
                usuario=estudiante,
                peticion_id=peticion_pendiente.id,
                archivo=archivo,
                nombre_original="malware.pdf",
            )
        assert exc_info.value.code == "invalid_magic_bytes"

    def test_png_renombrado_rechazado(self, estudiante, peticion_pendiente):
        """Imagen PNG renombrada como .pdf es rechazada."""
        archivo = io.BytesIO(IMAGEN_PNG_RENOMBRADA)
        archivo.name = "imagen.pdf"

        with pytest.raises(cargar_documento.ValidacionPDFError) as exc_info:
            cargar_documento.execute(
                usuario=estudiante,
                peticion_id=peticion_pendiente.id,
                archivo=archivo,
                nombre_original="imagen.pdf",
            )
        assert exc_info.value.code == "invalid_magic_bytes"

    def test_jpeg_renombrado_rechazado(self, estudiante, peticion_pendiente):
        """Imagen JPEG renombrada como .pdf es rechazada."""
        archivo = io.BytesIO(IMAGEN_JPEG_RENOMBRADA)
        archivo.name = "foto.pdf"

        with pytest.raises(cargar_documento.ValidacionPDFError) as exc_info:
            cargar_documento.execute(
                usuario=estudiante,
                peticion_id=peticion_pendiente.id,
                archivo=archivo,
                nombre_original="foto.pdf",
            )
        assert exc_info.value.code == "invalid_magic_bytes"

    def test_texto_plano_rechazado(self, estudiante, peticion_pendiente):
        """Archivo de texto plano es rechazado."""
        archivo = io.BytesIO(TEXTO_PLANO)
        archivo.name = "texto.pdf"

        with pytest.raises(cargar_documento.ValidacionPDFError) as exc_info:
            cargar_documento.execute(
                usuario=estudiante,
                peticion_id=peticion_pendiente.id,
                archivo=archivo,
                nombre_original="texto.pdf",
            )
        assert exc_info.value.code == "invalid_magic_bytes"

    def test_archivo_vacio_rechazado(self, estudiante, peticion_pendiente):
        """Archivo vacío es rechazado."""
        archivo = io.BytesIO(ARCHIVO_VACIO)
        archivo.name = "vacio.pdf"

        with pytest.raises(cargar_documento.ValidacionPDFError) as exc_info:
            cargar_documento.execute(
                usuario=estudiante,
                peticion_id=peticion_pendiente.id,
                archivo=archivo,
                nombre_original="vacio.pdf",
            )
        assert exc_info.value.code == "invalid_magic_bytes"

    def test_espacios_antes_de_header_rechazado(self, estudiante, peticion_pendiente):
        """PDF con espacios antes de %PDF- es rechazado."""
        archivo = io.BytesIO(b"   %PDF-1.4\ncontenido")
        archivo.name = "malformado.pdf"

        with pytest.raises(cargar_documento.ValidacionPDFError) as exc_info:
            cargar_documento.execute(
                usuario=estudiante,
                peticion_id=peticion_pendiente.id,
                archivo=archivo,
                nombre_original="malformado.pdf",
            )
        assert exc_info.value.code == "invalid_magic_bytes"


class TestValidacionTamano:
    """Tests de validación de tamaño máximo 10 MB (EX-004, RNF-004)."""

    def test_archivo_menor_10mb_aceptado(self, estudiante, peticion_pendiente):
        """Archivo de 5 MB es aceptado."""
        contenido = b"%PDF-1.4\n" + b"x" * (5 * 1024 * 1024)
        archivo = io.BytesIO(contenido)
        archivo.name = "5mb.pdf"

        documento = cargar_documento.execute(
            usuario=estudiante,
            peticion_id=peticion_pendiente.id,
            archivo=archivo,
            nombre_original="5mb.pdf",
        )

        assert documento.tamanio_bytes == 5 * 1024 * 1024 + 9

    def test_archivo_exactamente_10mb_aceptado(self, estudiante, peticion_pendiente):
        """Archivo de exactamente 10 MB es aceptado."""
        contenido = b"%PDF-1.4\n" + b"x" * (10 * 1024 * 1024 - 9)
        archivo = io.BytesIO(contenido)
        archivo.name = "10mb.pdf"

        documento = cargar_documento.execute(
            usuario=estudiante,
            peticion_id=peticion_pendiente.id,
            archivo=archivo,
            nombre_original="10mb.pdf",
        )

        assert documento.tamanio_bytes == 10 * 1024 * 1024

    def test_archivo_mayor_10mb_rechazado(self, estudiante, peticion_pendiente):
        """Archivo de 11 MB es rechazado (EX-004)."""
        archivo = io.BytesIO(ARCHIVO_GRANDE)
        archivo.name = "grande.pdf"

        with pytest.raises(cargar_documento.ValidacionPDFError) as exc_info:
            cargar_documento.execute(
                usuario=estudiante,
                peticion_id=peticion_pendiente.id,
                archivo=archivo,
                nombre_original="grande.pdf",
            )
        assert exc_info.value.code == "file_too_large"


class TestVersionadoDocumentos:
    """Tests de versionado N+1 de documentos (HU-008, CA-004)."""

    def test_primera_carga_version_1(self, estudiante, peticion_pendiente):
        """Primera carga crea versión 1 marcada como vigente."""
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "v1.pdf"

        documento = cargar_documento.execute(
            usuario=estudiante,
            peticion_id=peticion_pendiente.id,
            archivo=archivo,
            nombre_original="v1.pdf",
        )

        assert documento.version == 1
        assert documento.es_vigente is True

    def test_segunda_carga_incrementa_version(self, estudiante, peticion_pendiente):
        """Segunda carga incrementa versión a 2."""
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
        archivo2 = io.BytesIO(PDF_VALIDO_17)
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

    def test_multiples_cargas_incrementan_correctamente(self, estudiante, peticion_pendiente):
        """Múltiples cargas incrementan versión correctamente."""
        for i in range(1, 5):
            archivo = io.BytesIO(PDF_VALIDO)
            archivo.name = f"v{i}.pdf"
            doc = cargar_documento.execute(
                usuario=estudiante,
                peticion_id=peticion_pendiente.id,
                archivo=archivo,
                nombre_original=f"v{i}.pdf",
            )
            assert doc.version == i
            assert doc.es_vigente is True

        # Verificar que solo la última es vigente
        docs = DocumentoEntregado.objects.filter(peticion=peticion_pendiente).order_by("version")
        assert docs.count() == 4
        for i, doc in enumerate(docs, 1):
            if i == 4:
                assert doc.es_vigente is True
            else:
                assert doc.es_vigente is False


class TestHashSHA256Integridad:
    """Tests de hash SHA-256 para integridad documental."""

    def test_hash_calculado_correctamente(self, estudiante, peticion_pendiente):
        """Hash SHA-256 se calcula y almacena correctamente."""
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "test.pdf"

        documento = cargar_documento.execute(
            usuario=estudiante,
            peticion_id=peticion_pendiente.id,
            archivo=archivo,
            nombre_original="test.pdf",
        )

        assert len(documento.hash_sha256) == 64
        assert all(c in "0123456789abcdef" for c in documento.hash_sha256)

    def test_hash_consistente_mismo_contenido(self, estudiante, peticion_pendiente):
        """Mismo contenido produce mismo hash."""
        archivo1 = io.BytesIO(PDF_VALIDO)
        archivo1.name = "a.pdf"
        doc1 = cargar_documento.execute(
            usuario=estudiante,
            peticion_id=peticion_pendiente.id,
            archivo=archivo1,
            nombre_original="a.pdf",
        )

        # Segunda petición para mismo test
        from apps.peticiones.adapters.models import CatalogoDocumental, ESTADO_PENDIENTE
        requisito2 = CatalogoDocumental.objects.create(
            codigo_requisito="TEST-002",
            nombre="Test 2",
            es_obligatorio_base=False,
            fase="FASE_1",
            rol_emisor_sugerido="SECRETARIA_CARRERA",
            activo=True,
        )
        peticion2 = PeticionDocumental.objects.create(
            expediente=peticion_pendiente.expediente,
            requisito=requisito2,
            estado_peticion=ESTADO_PENDIENTE,
            dependencia_emisora="SECRETARIA_CARRERA",
        )

        archivo2 = io.BytesIO(PDF_VALIDO)
        archivo2.name = "b.pdf"
        doc2 = cargar_documento.execute(
            usuario=estudiante,
            peticion_id=peticion2.id,
            archivo=archivo2,
            nombre_original="b.pdf",
        )

        assert doc1.hash_sha256 == doc2.hash_sha256

    def test_hash_diferente_contenido_diferente(self, estudiante, peticion_pendiente):
        """Contenido diferente produce hash diferente."""
        archivo1 = io.BytesIO(PDF_VALIDO)
        archivo1.name = "a.pdf"
        doc1 = cargar_documento.execute(
            usuario=estudiante,
            peticion_id=peticion_pendiente.id,
            archivo=archivo1,
            nombre_original="a.pdf",
        )

        from apps.peticiones.adapters.models import CatalogoDocumental
        requisito2 = CatalogoDocumental.objects.create(
            codigo_requisito="TEST-003",
            nombre="Test 3",
            es_obligatorio_base=False,
            fase="FASE_1",
            rol_emisor_sugerido="SECRETARIA_CARRERA",
            activo=True,
        )
        peticion2 = PeticionDocumental.objects.create(
            expediente=peticion_pendiente.expediente,
            requisito=requisito2,
            estado_peticion=ESTADO_PENDIENTE,
            dependencia_emisora="SECRETARIA_CARRERA",
        )

        archivo2 = io.BytesIO(PDF_VALIDO_17)
        archivo2.name = "b.pdf"
        doc2 = cargar_documento.execute(
            usuario=estudiante,
            peticion_id=peticion2.id,
            archivo=archivo2,
            nombre_original="b.pdf",
        )

        assert doc1.hash_sha256 != doc2.hash_sha256


@pytest.fixture
def secretaria_carrera_para_notificacion(rol_secretaria_carrera, expediente_borrador):
    """Secretaria de Carrera para notificaciones en tests de flujo completo."""
    user = User.objects.create_user(
        username="secretaria_notificacion",
        email="sec_notif@test.com",
        password=PASSWORD,
        cedula="1234567899",
        carrera_id=CARRERA_1,
        facultad_id=FACULTAD_1,
    )
    UserRole.objects.create(user=user, role=rol_secretaria_carrera)
    return user


class TestDescargaSegura:
    """Tests de descarga segura desde almacenamiento privado (RNF-016, Principio C-018)."""

    def test_descarga_vigente_200_ok(self, estudiante, peticion_pendiente):
        """Descarga de versión vigente retorna 200 con archivo."""
        # Cargar documento
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "test.pdf"
        cargar_documento.execute(
            usuario=estudiante,
            peticion_id=peticion_pendiente.id,
            archivo=archivo,
            nombre_original="test.pdf",
        )

        client = auth_client(estudiante)
        url = f"/api/v1/peticiones/{peticion_pendiente.id}/documento/"
        response = client.get(url)

        assert response.status_code == 200
        assert response["Content-Type"] == "application/pdf"
        assert 'attachment; filename="test.pdf"' in response["Content-Disposition"]
        contenido = b"".join(response.streaming_content)
        assert contenido == PDF_VALIDO

    def test_descarga_version_especifica_200_ok(self, estudiante, peticion_pendiente):
        """Descarga de versión específica retorna 200."""
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "test.pdf"
        doc = cargar_documento.execute(
            usuario=estudiante,
            peticion_id=peticion_pendiente.id,
            archivo=archivo,
            nombre_original="test.pdf",
        )

        client = auth_client(estudiante)
        url = f"/api/v1/peticiones/{peticion_pendiente.id}/documento/{doc.version}/"
        response = client.get(url)

        assert response.status_code == 200
        assert response["Content-Type"] == "application/pdf"

    def test_descarga_401_sin_autenticacion(self, peticion_pendiente):
        """Sin token JWT retorna 401."""
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "test.pdf"
        cargar_documento.execute(
            usuario=peticion_pendiente.expediente.estudiante,
            peticion_id=peticion_pendiente.id,
            archivo=archivo,
            nombre_original="test.pdf",
        )

        client = APIClient()
        url = f"/api/v1/peticiones/{peticion_pendiente.id}/documento/"
        response = client.get(url)
        assert response.status_code == 401

    def test_descarga_403_rol_no_autorizado(self, secretario_abogado, peticion_pendiente):
        """Rol sin permisos (Secretario Abogado) retorna 403/404."""
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "test.pdf"
        cargar_documento.execute(
            usuario=peticion_pendiente.expediente.estudiante,
            peticion_id=peticion_pendiente.id,
            archivo=archivo,
            nombre_original="test.pdf",
        )

        client = auth_client(secretario_abogado)
        url = f"/api/v1/peticiones/{peticion_pendiente.id}/documento/"
        response = client.get(url)
        assert response.status_code in (403, 404)

    def test_descarga_404_estudiante_ajeno(self, rol_estudiante, peticion_pendiente):
        """Estudiante ajeno no puede descargar (IDOR protection)."""
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "test.pdf"
        cargar_documento.execute(
            usuario=peticion_pendiente.expediente.estudiante,
            peticion_id=peticion_pendiente.id,
            archivo=archivo,
            nombre_original="test.pdf",
        )

        otro_estudiante = User.objects.create_user(
            username="otro_estudiante",
            email="otro@test.com",
            password=PASSWORD,
            cedula="9999999999",
        )
        UserRole.objects.create(user=otro_estudiante, role=rol_estudiante)

        client = auth_client(otro_estudiante)
        url = f"/api/v1/peticiones/{peticion_pendiente.id}/documento/"
        response = client.get(url)
        assert response.status_code == 404

    def test_descarga_secretaria_carrera_200(self, secretaria_carrera, peticion_pendiente):
        """Secretaria de Carrera de la misma carrera puede descargar."""
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "test.pdf"
        cargar_documento.execute(
            usuario=peticion_pendiente.expediente.estudiante,
            peticion_id=peticion_pendiente.id,
            archivo=archivo,
            nombre_original="test.pdf",
        )

        client = auth_client(secretaria_carrera)
        url = f"/api/v1/peticiones/{peticion_pendiente.id}/documento/"
        response = client.get(url)
        assert response.status_code == 200

    def test_descarga_version_inexistente_404(self, estudiante, peticion_pendiente):
        """Versión inexistente retorna 404."""
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "test.pdf"
        cargar_documento.execute(
            usuario=estudiante,
            peticion_id=peticion_pendiente.id,
            archivo=archivo,
            nombre_original="test.pdf",
        )

        client = auth_client(estudiante)
        url = f"/api/v1/peticiones/{peticion_pendiente.id}/documento/999/"
        response = client.get(url)
        assert response.status_code == 404

    def test_descarga_peticion_sin_documento_404(self, estudiante, expediente_borrador):
        """Petición sin documento retorna 404."""
        from apps.peticiones.adapters.models import CatalogoDocumental, ESTADO_PENDIENTE

        # Usar código único para evitar conflicto unique
        requisito = CatalogoDocumental.objects.filter(
            codigo_requisito="TEST-999-SIN-DOC"
        ).first()
        if not requisito:
            requisito = CatalogoDocumental.objects.create(
                codigo_requisito="TEST-999-SIN-DOC",
                nombre="Requisito para test sin documento",
                es_obligatorio_base=False,
                fase="FASE_1",
                rol_emisor_sugerido="SECRETARIA_CARRERA",
                activo=True,
            )

        peticion = PeticionDocumental.objects.create(
            expediente=expediente_borrador,
            requisito=requisito,
            estado_peticion=ESTADO_PENDIENTE,
            dependencia_emisora="SECRETARIA_CARRERA",
        )

        client = auth_client(estudiante)
        url = f"/api/v1/peticiones/{peticion.id}/documento/"
        response = client.get(url)
        assert response.status_code == 404


class TestAlmacenamientoPrivado:
    """Tests de almacenamiento privado seguro (ADR-005, Principio C-018)."""

    def test_archivo_guardado_en_ruta_privada(self, estudiante, peticion_pendiente):
        """Archivo se guarda en /media/private/ y no en carpeta pública."""
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "test.pdf"
        documento = cargar_documento.execute(
            usuario=estudiante,
            peticion_id=peticion_pendiente.id,
            archivo=archivo,
            nombre_original="test.pdf",
        )

        assert documento.archivo_path.startswith("expedientes/")
        ruta_absoluta = obtener_ruta_absoluta(documento.archivo_path)
        assert "private" in str(ruta_absoluta).lower()

    def test_archivo_existe_en_almacenamiento(self, estudiante, peticion_pendiente):
        """Archivo existe físicamente en almacenamiento privado."""
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "test.pdf"
        documento = cargar_documento.execute(
            usuario=estudiante,
            peticion_id=peticion_pendiente.id,
            archivo=archivo,
            nombre_original="test.pdf",
        )

        assert archivo_existe(documento.archivo_path)
        ruta_absoluta = obtener_ruta_absoluta(documento.archivo_path)
        assert ruta_absoluta.exists()

    def test_private_storage_sin_base_url_publica(self):
        """PrivateMediaStorage no expone base_url pública."""
        from core.adapters.local_storage import PrivateMediaStorage

        storage = PrivateMediaStorage()
        assert storage.base_url is None

        with pytest.raises(NotImplementedError):
            storage.url("test.pdf")


class TestFlujoCompletoIntegracion:
    """Tests de flujo completo de integración: solicitud -> carga -> descarga."""

    def test_flujo_solicitud_carga_descarga_estudiante(self, estudiante, secretaria_carrera, peticion_pendiente):
        """Flujo completo: solicitar emisión -> cargar documento -> descargar."""
        # 1. Solicitar emisión
        peticion_actualizada = solicitar_emision.execute(
            usuario=estudiante,
            peticion_id=peticion_pendiente.id,
        )
        assert peticion_actualizada.estado_peticion == ESTADO_SOLICITADO

        # 2. Cargar documento
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "record.pdf"
        documento = cargar_documento.execute(
            usuario=estudiante,
            peticion_id=peticion_pendiente.id,
            archivo=archivo,
            nombre_original="record.pdf",
        )
        # Verificar que la petición cambió a CARGADO
        peticion_pendiente.refresh_from_db()
        assert peticion_pendiente.estado_peticion == ESTADO_CARGADO

        # 3. Descargar documento
        client = auth_client(estudiante)
        url = f"/api/v1/peticiones/{peticion_pendiente.id}/documento/"
        response = client.get(url)

        assert response.status_code == 200
        contenido = b"".join(response.streaming_content)
        assert contenido == PDF_VALIDO

    def test_flujo_solicitud_carga_descarga_secretaria(self, secretaria_carrera, peticion_pendiente):
        """Secretaria de Carrera puede cargar y descargar."""
        # Solicitar
        peticion_actualizada = solicitar_emision.execute(
            usuario=secretaria_carrera,
            peticion_id=peticion_pendiente.id,
        )
        assert peticion_actualizada.estado_peticion == ESTADO_SOLICITADO

        # Cargar
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "certificado.pdf"
        documento = cargar_documento.execute(
            usuario=secretaria_carrera,
            peticion_id=peticion_pendiente.id,
            archivo=archivo,
            nombre_original="certificado.pdf",
        )
        assert documento.subido_por == secretaria_carrera

        # Descargar
        client = auth_client(secretaria_carrera)
        url = f"/api/v1/peticiones/{peticion_pendiente.id}/documento/"
        response = client.get(url)

        assert response.status_code == 200

    def test_versionado_en_flujo_subsanacion(self, estudiante, peticion_pendiente):
        """Versionado funciona en flujo de subsanación (carga -> observación -> recarga)."""
        # Carga inicial
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

        # Simular observación (cambiar estado a OBSERVADO)
        peticion_pendiente.estado_peticion = "OBSERVADO"
        peticion_pendiente.save()

        # Subsanación: nueva carga
        archivo2 = io.BytesIO(PDF_VALIDO_17)
        archivo2.name = "v2_corregido.pdf"
        doc2 = cargar_documento.execute(
            usuario=estudiante,
            peticion_id=peticion_pendiente.id,
            archivo=archivo2,
            nombre_original="v2_corregido.pdf",
        )

        assert doc2.version == 2
        assert doc2.es_vigente is True
        assert doc2.nombre_original == "v2_corregido.pdf"

        doc1.refresh_from_db()
        assert doc1.es_vigente is False

        # Descargar versión vigente (v2)
        client = auth_client(estudiante)
        url = f"/api/v1/peticiones/{peticion_pendiente.id}/documento/"
        response = client.get(url)
        assert response.status_code == 200
        contenido = b"".join(response.streaming_content)
        assert contenido == PDF_VALIDO_17


class TestSeguridadEndpointAPI:
    """Tests de seguridad a nivel de endpoint API."""

    def test_endpoint_carga_400_magic_bytes_invalidos(self, estudiante, peticion_pendiente):
        """Endpoint POST /documento/ rechaza magic bytes inválidos con 400."""
        client = auth_client(estudiante)
        url = f"/api/v1/peticiones/{peticion_pendiente.id}/documento/"
        archivo = io.BytesIO(EJECUTABLE_RENOMBRADO)
        archivo.name = "malware.pdf"

        response = client.post(url, {"archivo": archivo}, format="multipart")
        assert response.status_code == 400

    def test_endpoint_carga_400_tamano_excedido(self, estudiante, peticion_pendiente):
        """Endpoint POST /documento/ rechaza >10MB con 400."""
        client = auth_client(estudiante)
        url = f"/api/v1/peticiones/{peticion_pendiente.id}/documento/"
        archivo = io.BytesIO(ARCHIVO_GRANDE)
        archivo.name = "grande.pdf"

        response = client.post(url, {"archivo": archivo}, format="multipart")
        assert response.status_code == 400

    def test_endpoint_carga_401_sin_token(self, peticion_pendiente):
        """POST /documento/ sin token retorna 401."""
        client = APIClient()
        url = f"/api/v1/peticiones/{peticion_pendiente.id}/documento/"
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "test.pdf"

        response = client.post(url, {"archivo": archivo}, format="multipart")
        assert response.status_code == 401

    def test_endpoint_carga_403_rol_no_autorizado(self, secretario_abogado, peticion_pendiente):
        """POST /documento/ con rol no autorizado retorna 403."""
        client = auth_client(secretario_abogado)
        url = f"/api/v1/peticiones/{peticion_pendiente.id}/documento/"
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "test.pdf"

        response = client.post(url, {"archivo": archivo}, format="multipart")
        assert response.status_code == 403

    def test_endpoint_carga_404_peticion_ajena(self, estudiante, peticion_pendiente):
        """POST /documento/ con petición ajena retorna 404 (IDOR)."""
        otro_estudiante = User.objects.create_user(
            username="otro_estudiante",
            email="otro@test.com",
            password=PASSWORD,
            cedula="8888888888",
        )
        from apps.authentication.adapters.models import Role, UserRole
        rol_est = Role.objects.get(name=ROLE_ESTUDIANTE)
        UserRole.objects.create(user=otro_estudiante, role=rol_est)

        client = auth_client(otro_estudiante)
        url = f"/api/v1/peticiones/{peticion_pendiente.id}/documento/"
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "test.pdf"

        response = client.post(url, {"archivo": archivo}, format="multipart")
        assert response.status_code == 404


class TestRegistroSubidoPor:
    """Tests de registro de auditoría subido_por (DEC-02)."""

    def test_subido_por_registrado_estudiante(self, estudiante, peticion_pendiente):
        """Campo subido_por se registra correctamente para estudiante."""
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "test.pdf"
        documento = cargar_documento.execute(
            usuario=estudiante,
            peticion_id=peticion_pendiente.id,
            archivo=archivo,
            nombre_original="test.pdf",
        )

        assert documento.subido_por == estudiante

    def test_subido_por_registrado_secretaria(self, secretaria_carrera, peticion_pendiente):
        """Campo subido_por se registra correctamente para secretaria."""
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "test.pdf"
        documento = cargar_documento.execute(
            usuario=secretaria_carrera,
            peticion_id=peticion_pendiente.id,
            archivo=archivo,
            nombre_original="test.pdf",
        )

        assert documento.subido_por == secretaria_carrera

    def test_endpoint_retorna_subido_por_username(self, estudiante, peticion_pendiente):
        """Endpoint retorna subido_por_username en respuesta."""
        client = auth_client(estudiante)
        url = f"/api/v1/peticiones/{peticion_pendiente.id}/documento/"
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "test.pdf"

        response = client.post(url, {"archivo": archivo}, format="multipart")
        assert response.status_code == 201
        assert response.data["subido_por_username"] == estudiante.username
        assert str(response.data["subido_por"]) == str(estudiante.pk)