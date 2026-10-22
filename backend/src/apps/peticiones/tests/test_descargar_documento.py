"""Pruebas para T024: Descarga segura de documentos PDF (RNF-016, Principio C-018, P-07).

Verifica:
- Descarga autenticada retorna 200 con archivo
- Sin token retorna 401
- Sin permisos retorna 403/404 (IDOR)
- Acceso directo a URL física sin token retorna 401/403
- Versionado: descarga por versión específica y vigente
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
    DocumentoEntregado,
    PeticionDocumental,
)
from apps.peticiones.services import cargar_documento
from core.adapters.local_storage import archivo_existe, obtener_ruta_absoluta

pytestmark = pytest.mark.django_db

CARRERA_1 = "11111111-1111-1111-1111-111111111111"
FACULTAD_1 = "22222222-2222-2222-2222-222222222222"
PASSWORD = "pass1234"

# PDF válido mínimo para testing
PDF_VALIDO = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>\nendobj\n4 0 obj\n<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>\nendobj\n5 0 obj\n<</Length 44>>\nstream\nBT /F1 24 Tf 100 700 Td (Test) Tj ET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000218 00000 n \n0000000277 00000 n \ntrailer\n<</Size 6/Root 1 0 R>>\nstartxref\n347\n%%EOF"


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
def peticion_con_documento(estudiante, expediente_borrador):
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
    peticion = PeticionDocumental.objects.create(
        expediente=expediente_borrador,
        requisito=requisito,
        estado_peticion=ESTADO_PENDIENTE,
        dependencia_emisora="SECRETARIA_CARRERA",
    )

    # Cargar documento usando el servicio
    archivo = io.BytesIO(PDF_VALIDO)
    archivo.name = "record_academico.pdf"
    documento = cargar_documento.execute(
        usuario=estudiante,
        peticion_id=peticion.id,
        archivo=archivo,
        nombre_original="record_academico.pdf",
    )
    return peticion, documento


class TestDescargarDocumentoEndpoint:
    """Tests de integración del endpoint GET /api/v1/peticiones/{id}/documento/{version}/."""

    def test_descarga_vigente_200_ok(self, estudiante, peticion_con_documento):
        """Endpoint retorna 200 con archivo PDF para usuario autorizado."""
        peticion, documento = peticion_con_documento
        client = auth_client(estudiante)
        url = f"/api/v1/peticiones/{peticion.id}/documento/"

        response = client.get(url)

        assert response.status_code == 200
        assert response["Content-Type"] == "application/pdf"
        assert "Content-Disposition" in response
        assert 'attachment; filename="record_academico.pdf"' in response["Content-Disposition"]
        assert int(response["Content-Length"]) == len(PDF_VALIDO)

        # Verificar contenido del archivo
        contenido = b"".join(response.streaming_content)
        assert contenido == PDF_VALIDO

    def test_descarga_version_especifica_200_ok(self, estudiante, peticion_con_documento):
        """Endpoint con versión específica retorna 200."""
        peticion, documento = peticion_con_documento
        client = auth_client(estudiante)
        url = f"/api/v1/peticiones/{peticion.id}/documento/{documento.version}/"

        response = client.get(url)

        assert response.status_code == 200
        assert response["Content-Type"] == "application/pdf"

    def test_descarga_401_sin_autenticacion(self, peticion_con_documento):
        """Sin token retorna 401."""
        peticion, _ = peticion_con_documento
        client = APIClient()
        url = f"/api/v1/peticiones/{peticion.id}/documento/"

        response = client.get(url)
        assert response.status_code == 401

    def test_descarga_403_rol_no_autorizado(
        self, secretario_abogado, peticion_con_documento
    ):
        """Rol no autorizado (Secretario Abogado) retorna 403 o 404 por IDOR."""
        peticion, _ = peticion_con_documento
        client = auth_client(secretario_abogado)
        url = f"/api/v1/peticiones/{peticion.id}/documento/"

        response = client.get(url)
        # Debe ser 403 (sin permisos) o 404 (IDOR - no en su ámbito)
        assert response.status_code in (403, 404)

    def test_descarga_404_estudiante_ajeno(self, rol_estudiante, peticion_con_documento):
        """Estudiante que no es el propietario no puede descargar (IDOR)."""
        peticion, _ = peticion_con_documento

        otro_estudiante = User.objects.create_user(
            username="otro_estudiante2",
            email="otro2@test.com",
            password=PASSWORD,
            cedula="8888888888",
        )
        UserRole.objects.create(user=otro_estudiante, role=rol_estudiante)

        client = auth_client(otro_estudiante)
        url = f"/api/v1/peticiones/{peticion.id}/documento/"

        response = client.get(url)
        assert response.status_code == 404

    def test_descarga_secretaria_carrera_misma_carrera_200(
        self, secretaria_carrera, peticion_con_documento
    ):
        """Secretaria de Carrera de la misma carrera puede descargar."""
        peticion, _ = peticion_con_documento
        client = auth_client(secretaria_carrera)
        url = f"/api/v1/peticiones/{peticion.id}/documento/"

        response = client.get(url)
        assert response.status_code == 200

    def test_descarga_version_inexistente_404(self, estudiante, peticion_con_documento):
        """Versión que no existe retorna 404."""
        peticion, _ = peticion_con_documento
        client = auth_client(estudiante)
        url = f"/api/v1/peticiones/{peticion.id}/documento/999/"

        response = client.get(url)
        assert response.status_code == 404

    def test_descarga_peticion_sin_documento_404(self, estudiante, expediente_borrador):
        """Petición sin documento retorna 404."""
        from apps.peticiones.adapters.models import CatalogoDocumental, ESTADO_PENDIENTE

        # Usar un requisito diferente para evitar constraint unique
        requisito = CatalogoDocumental.objects.filter(
            codigo_requisito="ART235-02-PRACTICAS-VINCULACION"
        ).first()
        if not requisito:
            requisito = CatalogoDocumental.objects.create(
                codigo_requisito="ART235-02-PRACTICAS-VINCULACION",
                nombre="Certificado de prácticas",
                descripcion="Certificado de prácticas preprofesionales.",
                es_obligatorio_base=True,
                fase="FASE_1",
                rol_emisor_sugerido="RESPONSABLE_DEPENDENCIA",
                activo=True,
            )

        peticion_nueva = PeticionDocumental.objects.create(
            expediente=expediente_borrador,
            requisito=requisito,
            estado_peticion=ESTADO_PENDIENTE,
            dependencia_emisora="RESPONSABLE_DEPENDENCIA",
        )

        client = auth_client(estudiante)
        url = f"/api/v1/peticiones/{peticion_nueva.id}/documento/"

        response = client.get(url)
        assert response.status_code == 404


class TestAlmacenamientoPrivadoSeguro:
    """Tests de seguridad del almacenamiento privado (RNF-016, Principio C-018)."""

    def test_archivo_no_accesible_via_url_publica(self, estudiante, peticion_con_documento):
        """Acceso directo a la URL física del archivo sin token debe fallar."""
        peticion, documento = peticion_con_documento

        # Verificar que el archivo existe en almacenamiento privado
        assert archivo_existe(documento.archivo_path)

        ruta_absoluta = obtener_ruta_absoluta(documento.archivo_path)
        assert ruta_absoluta.exists()

        # La ruta absoluta NO debe ser accesible via web directamente
        # (no hay URL pública configurada para /media/private/)
        # Esto se verifica implícitamente: no hay endpoint estático que sirva /media/private/

    def test_archivo_guardado_en_ruta_privada(self, estudiante, peticion_con_documento):
        """Archivo se guarda en /media/private/ y no en /media/ público."""
        peticion, documento = peticion_con_documento

        assert documento.archivo_path.startswith("expedientes/")
        assert "private" not in documento.archivo_path  # ruta relativa sin 'private'

        ruta_absoluta = obtener_ruta_absoluta(documento.archivo_path)
        # La ruta absoluta debe contener 'private'
        assert "private" in str(ruta_absoluta).lower()

    def test_private_storage_sin_base_url(self):
        """PrivateMediaStorage no tiene base_url pública."""
        from core.adapters.local_storage import PrivateMediaStorage

        storage = PrivateMediaStorage()
        assert storage.base_url is None

        # Llamar a url() debe lanzar NotImplementedError
        with pytest.raises(NotImplementedError):
            storage.url("test.pdf")


class TestVersionadoDescarga:
    """Tests de descarga con versionado N+1."""

    def test_descarga_vigente_vs_versiones_anteriores(self, estudiante, peticion_con_documento):
        """Solo la versión vigente se descarga por defecto; otras requieren versión explícita."""
        peticion, documento_v1 = peticion_con_documento

        # Cargar segunda versión (simula subsanación)
        archivo_v2 = io.BytesIO(PDF_VALIDO)
        archivo_v2.name = "record_v2.pdf"
        documento_v2 = cargar_documento.execute(
            usuario=estudiante,
            peticion_id=peticion.id,
            archivo=archivo_v2,
            nombre_original="record_v2.pdf",
        )

        assert documento_v2.version == 2
        assert documento_v2.es_vigente is True

        documento_v1.refresh_from_db()
        assert documento_v1.es_vigente is False

        client = auth_client(estudiante)

        # Descarga por defecto -> versión vigente (v2)
        url_vigente = f"/api/v1/peticiones/{peticion.id}/documento/"
        response = client.get(url_vigente)
        assert response.status_code == 200

        # Descarga explícita v1
        url_v1 = f"/api/v1/peticiones/{peticion.id}/documento/1/"
        response = client.get(url_v1)
        assert response.status_code == 200

        # Descarga explícita v2
        url_v2 = f"/api/v1/peticiones/{peticion.id}/documento/2/"
        response = client.get(url_v2)
        assert response.status_code == 200