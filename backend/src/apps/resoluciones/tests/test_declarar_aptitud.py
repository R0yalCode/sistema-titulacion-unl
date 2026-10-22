"""Pruebas para T035: Registro de Declaratoria de Aptitud por Decano/a con Anexo PDF (HU-010, RF-011, RN-004, CA-006, DEC-04).

Verifica:
- POST /api/v1/declaratorias/ registra declaratoria (Memorando N° 162)
- Valida que expediente esté en INFORME_EMITIDO
- Valida que exista InformeAptitud (Providencia N° 590)
- Valida PDF del memorando firmado (FirmaEC) - T022
- Crea DeclaratoriaAptitud con número de memorando
- Cambia expediente a DECLARADA_APTA
- Notifica con copia a autoridades y estudiante (DEC-04)
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
    ROLE_DECANO,
    User,
    Role,
    UserRole,
)
from apps.expedientes.adapters.models import ExpedienteTitulacion, HistorialEstado
from apps.peticiones.adapters.models import (
    ESTADO_CARGADO,
    ESTADO_PENDIENTE,
    ESTADO_VERIFICADO,
    PeticionDocumental,
    DocumentoEntregado,
)
from apps.verificacion.adapters.models import (
    ChecklistVerification,
    ESTADO_VERIFICACION_VERIFICADO,
)
from apps.resoluciones.adapters.models import InformeAptitud, DeclaratoriaAptitud
from apps.notificaciones.adapters.models import NotificacionInterna
from apps.resoluciones.services import (
    emitir_informe,
    declarar_aptitud,
    ExpedienteNoValidoParaDeclaratoriaError,
    DeclaratoriaYaExisteError,
    UsuarioNoAutorizadoErrorDeclaratoria,
    PDFInvalidoError,
)
from apps.verificacion.services import validar_checklist_completo

pytestmark = pytest.mark.django_db

CARRERA_1 = "11111111-1111-1111-1111-111111111111"
FACULTAD_1 = "22222222-2222-2222-2222-222222222222"
PASSWORD = "pass1234"

# PDF válido mínimo para testing (PDF 1.4)
PDF_VALIDO = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>\nendobj\n4 0 obj\n<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>\nendobj\n5 0 obj\n<</Length 44>>\nstream\nBT /F1 24 Tf 100 700 Td (Test) Tj ET\nendstream\nendobj\nxref\n0 6\n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000218 00000 n \n0000000277 00000 n \ntrailer\n<</Size 6/Root 1 0 R>>\nstartxref\n347\n%%EOF"

# Archivos inválidos para testing de seguridad
EJECUTABLE_RENOMBRADO = b"MZ\x90\x00"  # PE header (Windows executable)
ARCHIVO_GRANDE = b"%PDF-1.4\n" + b"x" * (11 * 1024 * 1024)  # 11 MB


@pytest.fixture
def api_client():
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
def rol_decano():
    role, _ = Role.objects.get_or_create(name=ROLE_DECANO)
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
        cedula="1234567893",
        carrera_id=CARRERA_1,
        facultad_id=FACULTAD_1,
    )
    UserRole.objects.create(user=user, role=rol_secretario_abogado)
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
def decano(rol_decano):
    user = User.objects.create_user(
        username="decano_test",
        email="decano@test.com",
        password=PASSWORD,
        cedula="1234567894",
        facultad_id=FACULTAD_1,
    )
    UserRole.objects.create(user=user, role=rol_decano)
    return user


@pytest.fixture
def expediente_con_informe(estudiante, secretario_abogado):
    """Expediente con checklist 100% VERIFICADO e InformeAptitud emitido (INFORME_EMITIDO)."""
    from apps.peticiones.adapters.models import CatalogoDocumental, ESTADO_CARGADO

    expediente = ExpedienteTitulacion.objects.create(
        numero_expediente="EXP-2026-0001",
        estudiante=estudiante,
        carrera_id=CARRERA_1,
        facultad_id=FACULTAD_1,
        estado=ExpedienteTitulacion.ESTADO_EN_VERIFICACION,
        activa=True,
        fecha_recepcion=timezone.now(),
    )

    # Crear 5 requisitos base (Art. 235) todos VERIFICADO
    for i, (codigo, nombre) in enumerate([
        ("REQ-01", "Acta de Grado"),
        ("REQ-02", "Certificado de Votación"),
        ("REQ-03", "Certificado Militar"),
        ("REQ-04", "Título de Bachiller"),
        ("REQ-05", "Record Académico Legalizado"),
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
            estado_peticion=ESTADO_VERIFICADO,
            dependencia_emisora="SECRETARIA_CARRERA",
        )
        DocumentoEntregado.objects.create(
            peticion=peticion,
            version=1,
            archivo_path=f"expedientes/2026/{expediente.id}/{codigo}.pdf",
            nombre_original=f"{codigo}.pdf",
            tamanio_bytes=len(PDF_VALIDO),
            hash_sha256="a" * 64,
            tipo_mime="application/pdf",
            subido_por=estudiante,
            es_vigente=True,
        )
        ChecklistVerification.objects.create(
            expediente=expediente,
            requisito=requisito,
            estado_verificacion="VERIFICADO",
            evaluado_por=secretario_abogado,
        )

    # Emitir informe legal
    informe = emitir_informe(
        usuario=secretario_abogado,
        expediente_id=expediente.id,
        dictamen="APTO",
    )

    return expediente


@pytest.fixture
def expediente_en_verificacion_sin_informe(estudiante, secretario_abogado):
    """Expediente en EN_VERIFICACION sin informe emitido."""
    from apps.peticiones.adapters.models import CatalogoDocumental, ESTADO_CARGADO

    expediente = ExpedienteTitulacion.objects.create(
        numero_expediente="EXP-2026-0002",
        estudiante=estudiante,
        carrera_id=CARRERA_1,
        facultad_id=FACULTAD_1,
        estado=ExpedienteTitulacion.ESTADO_EN_VERIFICACION,
        activa=True,
        fecha_recepcion=timezone.now(),
    )

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
            estado_peticion=ESTADO_VERIFICADO,
            dependencia_emisora="SECRETARIA_CARRERA",
        )
        DocumentoEntregado.objects.create(
            peticion=peticion,
            version=1,
            archivo_path=f"expedientes/2026/{expediente.id}/{codigo}.pdf",
            nombre_original=f"{codigo}.pdf",
            tamanio_bytes=len(PDF_VALIDO),
            hash_sha256="a" * 64,
            tipo_mime="application/pdf",
            subido_por=estudiante,
            es_vigente=True,
        )
        ChecklistVerification.objects.create(
            expediente=expediente,
            requisito=requisito,
            estado_verificacion="VERIFICADO",
            evaluado_por=secretario_abogado,
        )

    return expediente


class TestDeclararAptitudService:
    """Tests del servicio declarar_aptitud (T035)."""

    def test_registrar_declaratoria_exitoso(self, decano, expediente_con_informe):
        """Registro exitoso de declaratoria con PDF válido."""
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "memorando_162_firmado.pdf"

        declaratoria = declarar_aptitud(
            usuario=decano,
            expediente_id=expediente_con_informe.id,
            archivo_memorando=archivo,
        )

        assert declaratoria is not None
        assert declaratoria.expediente == expediente_con_informe
        assert declaratoria.decano == decano
        assert declaratoria.numero_memorando.startswith("MEM-162-")
        assert declaratoria.archivo_memorando_firmado_path.endswith(".pdf")

        # Verificar expediente actualizado
        expediente_con_informe.refresh_from_db()
        assert expediente_con_informe.estado == ExpedienteTitulacion.ESTADO_DECLARADA_APTA

        # Verificar historial de estado
        historial = HistorialEstado.objects.filter(
            expediente=expediente_con_informe,
            estado_nuevo=ExpedienteTitulacion.ESTADO_DECLARADA_APTA,
        ).first()
        assert historial is not None
        assert historial.estado_nuevo == ExpedienteTitulacion.ESTADO_DECLARADA_APTA
        assert historial.registrado_por == decano

    def test_declaratoria_genera_numero_memorando_unico(self, decano, expediente_con_informe):
        """Genera número de memorando con formato MEM-162-YYYY-NNNN."""
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "mem1.pdf"

        declaratoria = declarar_aptitud(
            usuario=decano,
            expediente_id=expediente_con_informe.id,
            archivo_memorando=archivo,
        )

        assert declaratoria.numero_memorando.startswith("MEM-162-")
        parts = declaratoria.numero_memorando.split("-")
        assert len(parts) == 4
        assert parts[0] == "MEM"
        assert parts[1] == "162"
        assert parts[2] == str(timezone.now().year)
        assert parts[3].isdigit()

    def test_declaratoria_notifica_estudiante_y_autoridades(self, decano, expediente_con_informe, estudiante):
        """Crea notificaciones con copia a autoridades y estudiante (DEC-04)."""
        from apps.authentication.adapters.models import User, Role, UserRole

        # Crear otra autoridad en la misma facultad
        rol_dir, _ = Role.objects.get_or_create(name="DIRECTOR_CARRERA")
        director = User.objects.create_user(
            username="director_test",
            email="dir@test.com",
            password=PASSWORD,
            cedula="1234567895",
            facultad_id=FACULTAD_1,
        )
        UserRole.objects.create(user=director, role=rol_dir)

        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "mem.pdf"

        declarar_aptitud(
            usuario=decano,
            expediente_id=expediente_con_informe.id,
            archivo_memorando=archivo,
        )

        # Notificación al estudiante
        notif_est = NotificacionInterna.objects.filter(
            usuario_destino=estudiante,
            expediente=expediente_con_informe,
        ).first()
        assert notif_est is not None
        assert "Declaratoria de Aptitud" in notif_est.titulo
        assert expediente_con_informe.numero_expediente in notif_est.mensaje

        # Notificación a autoridad (copia)
        notif_dir = NotificacionInterna.objects.filter(
            usuario_destino=director,
            expediente=expediente_con_informe,
        ).first()
        assert notif_dir is not None
        assert "Copia: Declaratoria" in notif_dir.titulo

    def test_falla_si_expediente_no_en_informe_emitido(self, decano, expediente_en_verificacion_sin_informe):
        """Falla si expediente no está en INFORME_EMITIDO."""
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "mem.pdf"

        with pytest.raises(ExpedienteNoValidoParaDeclaratoriaError):
            declarar_aptitud(
                usuario=decano,
                expediente_id=expediente_en_verificacion_sin_informe.id,
                archivo_memorando=archivo,
            )

    def test_falla_si_expediente_sin_informe_apto(self, decano, expediente_en_verificacion_sin_informe):
        """Falla si no existe InformeAptitud emitido."""
        # Cambiar estado a INFORME_EMITIDO pero sin crear InformeAptitud
        expediente_en_verificacion_sin_informe.estado = ExpedienteTitulacion.ESTADO_INFORME_EMITIDO
        expediente_en_verificacion_sin_informe.save()

        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "mem.pdf"

        with pytest.raises(ExpedienteNoValidoParaDeclaratoriaError) as exc_info:
            declarar_aptitud(
                usuario=decano,
                expediente_id=expediente_en_verificacion_sin_informe.id,
                archivo_memorando=archivo,
            )

        assert "Informe de Aptitud" in str(exc_info.value)

    def test_falla_si_declaratoria_ya_existe(self, decano, expediente_con_informe):
        """Falla si intenta registrar segunda declaratoria (estado cambia a DECLARADA_APTA)."""
        archivo1 = io.BytesIO(PDF_VALIDO)
        archivo1.name = "mem1.pdf"
        declarar_aptitud(
            usuario=decano,
            expediente_id=expediente_con_informe.id,
            archivo_memorando=archivo1,
        )

        archivo2 = io.BytesIO(PDF_VALIDO)
        archivo2.name = "mem2.pdf"

        # El estado cambia a DECLARADA_APTA tras la primera, así que falla por estado
        with pytest.raises(ExpedienteNoValidoParaDeclaratoriaError) as exc_info:
            declarar_aptitud(
                usuario=decano,
                expediente_id=expediente_con_informe.id,
                archivo_memorando=archivo2,
            )
        assert "INFORME_EMITIDO" in str(exc_info.value)

    def test_falla_si_usuario_no_decano(self, estudiante, expediente_con_informe):
        """Falla si usuario no es DECANO ni ANALISTA_APOYO."""
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "mem.pdf"

        with pytest.raises(UsuarioNoAutorizadoErrorDeclaratoria):
            declarar_aptitud(
                usuario=estudiante,
                expediente_id=expediente_con_informe.id,
                archivo_memorando=archivo,
            )

    def test_falla_si_usuario_distinta_facultad(self, expediente_con_informe):
        """Falla si DECANO de otra facultad."""
        from apps.authentication.adapters.models import User, Role, UserRole

        rol_dec, _ = Role.objects.get_or_create(name="DECANO")
        decano_otra = User.objects.create_user(
            username="decano_otra",
            email="dec_otra@test.com",
            password=PASSWORD,
            cedula="2222222222",
            facultad_id="33333333-3333-3333-3333-333333333333",
        )
        UserRole.objects.create(user=decano_otra, role=rol_dec)

        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "mem.pdf"

        with pytest.raises(UsuarioNoAutorizadoErrorDeclaratoria):
            declarar_aptitud(
                usuario=decano_otra,
                expediente_id=expediente_con_informe.id,
                archivo_memorando=archivo,
            )

    def test_falla_si_archivo_invalido(self, decano, expediente_con_informe):
        """Falla si archivo no es PDF válido (magic bytes)."""
        archivo = io.BytesIO(EJECUTABLE_RENOMBRADO)
        archivo.name = "malware.pdf"

        with pytest.raises(PDFInvalidoError) as exc_info:
            declarar_aptitud(
                usuario=decano,
                expediente_id=expediente_con_informe.id,
                archivo_memorando=archivo,
            )
        assert exc_info.value.code == "invalid_magic_bytes"

    def test_falla_si_archivo_mayor_10mb(self, decano, expediente_con_informe):
        """Falla si archivo > 10 MB."""
        archivo = io.BytesIO(ARCHIVO_GRANDE)
        archivo.name = "grande.pdf"

        with pytest.raises(PDFInvalidoError) as exc_info:
            declarar_aptitud(
                usuario=decano,
                expediente_id=expediente_con_informe.id,
                archivo_memorando=archivo,
            )
        assert exc_info.value.code == "file_too_large"

    def test_falla_si_sin_archivo(self, decano, expediente_con_informe):
        """Falla si no se proporciona archivo."""
        with pytest.raises(PDFInvalidoError) as exc_info:
            declarar_aptitud(
                usuario=decano,
                expediente_id=expediente_con_informe.id,
                archivo_memorando=None,
            )
        assert exc_info.value.code == "no_file"

    def test_analista_apoyo_puede_registrar(self, analista_apoyo, expediente_con_informe):
        """ANALISTA_APOYO puede registrar declaratoria."""
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "mem_analista.pdf"

        declaratoria = declarar_aptitud(
            usuario=analista_apoyo,
            expediente_id=expediente_con_informe.id,
            archivo_memorando=archivo,
        )

        assert declaratoria.decano == analista_apoyo

    def test_permite_numero_memorando_personalizado(self, decano, expediente_con_informe):
        """Permite especificar número de memorando personalizado."""
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "mem_custom.pdf"

        declaratoria = declarar_aptitud(
            usuario=decano,
            expediente_id=expediente_con_informe.id,
            archivo_memorando=archivo,
            numero_memorando="MEM-162-2026-CUSTOM-001",
        )

        assert declaratoria.numero_memorando == "MEM-162-2026-CUSTOM-001"


class TestDeclaratoriaEndpoint:
    """Tests del endpoint POST /api/v1/declaratorias/ (T035)."""

    def test_endpoint_201_created(self, api_client, decano, expediente_con_informe):
        """Endpoint retorna 201 con datos de la declaratoria."""
        api_client.force_authenticate(user=decano)
        url = "/api/v1/declaratorias/"
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "memorando_162_firmado.pdf"

        response = api_client.post(url, {
            "expediente_id": str(expediente_con_informe.id),
            "archivo_memorando": archivo,
        }, format="multipart")

        assert response.status_code == 201
        assert "id" in response.data
        assert response.data["numero_memorando"].startswith("MEM-162-")
        assert response.data["archivo_memorando_firmado_path"].endswith(".pdf")
        assert response.data["expediente_numero"] == expediente_con_informe.numero_expediente

    def test_endpoint_400_expediente_estado_invalido(self, api_client, decano, expediente_en_verificacion_sin_informe):
        """Retorna 400 si expediente no está en INFORME_EMITIDO."""
        api_client.force_authenticate(user=decano)
        url = "/api/v1/declaratorias/"
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "mem.pdf"

        response = api_client.post(url, {
            "expediente_id": str(expediente_en_verificacion_sin_informe.id),
            "archivo_memorando": archivo,
        }, format="multipart")

        assert response.status_code == 400
        assert "INFORME_EMITIDO" in str(response.data) or "expediente" in str(response.data).lower()

    def test_endpoint_400_sin_informe_apto(self, api_client, decano, expediente_en_verificacion_sin_informe):
        """Retorna 400 si expediente en INFORME_EMITIDO pero sin InformeAptitud."""
        # Forzar estado pero sin informe
        expediente_en_verificacion_sin_informe.estado = ExpedienteTitulacion.ESTADO_INFORME_EMITIDO
        expediente_en_verificacion_sin_informe.save()

        api_client.force_authenticate(user=decano)
        url = "/api/v1/declaratorias/"
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "mem.pdf"

        response = api_client.post(url, {
            "expediente_id": str(expediente_en_verificacion_sin_informe.id),
            "archivo_memorando": archivo,
        }, format="multipart")

        assert response.status_code == 400
        assert "Informe de Aptitud" in str(response.data)

    def test_endpoint_400_declaratoria_ya_existe(self, api_client, decano, expediente_con_informe):
        """Retorna 400 si ya existe declaratoria."""
        api_client.force_authenticate(user=decano)
        url = "/api/v1/declaratorias/"

        # Primera
        archivo1 = io.BytesIO(PDF_VALIDO)
        archivo1.name = "mem1.pdf"
        api_client.post(url, {
            "expediente_id": str(expediente_con_informe.id),
            "archivo_memorando": archivo1,
        }, format="multipart")

        # Segunda - el estado ya cambió a DECLARADA_APTA
        archivo2 = io.BytesIO(PDF_VALIDO)
        archivo2.name = "mem2.pdf"
        response = api_client.post(url, {
            "expediente_id": str(expediente_con_informe.id),
            "archivo_memorando": archivo2,
        }, format="multipart")

        assert response.status_code == 400
        assert "INFORME_EMITIDO" in str(response.data)

    def test_endpoint_401_sin_autenticacion(self, api_client, expediente_con_informe):
        """Retorna 401 sin token."""
        url = "/api/v1/declaratorias/"
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "mem.pdf"

        response = api_client.post(url, {
            "expediente_id": str(expediente_con_informe.id),
            "archivo_memorando": archivo,
        }, format="multipart")

        assert response.status_code == 401

    def test_endpoint_403_rol_no_autorizado(self, api_client, estudiante, expediente_con_informe):
        """Retorna 403 para roles no permitidos."""
        api_client.force_authenticate(user=estudiante)
        url = "/api/v1/declaratorias/"
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "mem.pdf"

        response = api_client.post(url, {
            "expediente_id": str(expediente_con_informe.id),
            "archivo_memorando": archivo,
        }, format="multipart")

        assert response.status_code in (403, 404)

    def test_endpoint_403_decano_otra_facultad(self, api_client, expediente_con_informe):
        """Retorna 403 para DECANO de otra facultad."""
        from apps.authentication.adapters.models import User, Role, UserRole

        rol_dec, _ = Role.objects.get_or_create(name="DECANO")
        decano_otra = User.objects.create_user(
            username="decano_otra",
            email="dec_otra@test.com",
            password=PASSWORD,
            cedula="2222222222",
            facultad_id="33333333-3333-3333-3333-333333333333",
        )
        UserRole.objects.create(user=decano_otra, role=rol_dec)

        api_client.force_authenticate(user=decano_otra)
        url = "/api/v1/declaratorias/"
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "mem.pdf"

        response = api_client.post(url, {
            "expediente_id": str(expediente_con_informe.id),
            "archivo_memorando": archivo,
        }, format="multipart")

        assert response.status_code in (403, 404)

    def test_endpoint_400_archivo_invalido(self, api_client, decano, expediente_con_informe):
        """Retorna 400 para archivo con magic bytes inválidos."""
        api_client.force_authenticate(user=decano)
        url = "/api/v1/declaratorias/"
        archivo = io.BytesIO(EJECUTABLE_RENOMBRADO)
        archivo.name = "malware.pdf"

        response = api_client.post(url, {
            "expediente_id": str(expediente_con_informe.id),
            "archivo_memorando": archivo,
        }, format="multipart")

        assert response.status_code == 400
        assert "inválido" in str(response.data).lower() or "pdf" in str(response.data).lower()

    def test_endpoint_400_archivo_mayor_10mb(self, api_client, decano, expediente_con_informe):
        """Retorna 400 para archivo > 10 MB."""
        api_client.force_authenticate(user=decano)
        url = "/api/v1/declaratorias/"
        archivo = io.BytesIO(ARCHIVO_GRANDE)
        archivo.name = "grande.pdf"

        response = api_client.post(url, {
            "expediente_id": str(expediente_con_informe.id),
            "archivo_memorando": archivo,
        }, format="multipart")

        assert response.status_code == 400

    def test_endpoint_400_sin_archivo(self, api_client, decano, expediente_con_informe):
        """Retorna 400 si no se proporciona archivo."""
        api_client.force_authenticate(user=decano)
        url = "/api/v1/declaratorias/"

        response = api_client.post(url, {
            "expediente_id": str(expediente_con_informe.id),
        }, format="multipart")

        assert response.status_code == 400

    def test_endpoint_permite_numero_memorando_personalizado(self, api_client, decano, expediente_con_informe):
        """Permite especificar número de memorando personalizado."""
        api_client.force_authenticate(user=decano)
        url = "/api/v1/declaratorias/"
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "mem_custom.pdf"

        response = api_client.post(url, {
            "expediente_id": str(expediente_con_informe.id),
            "archivo_memorando": archivo,
            "numero_memorando": "MEM-162-2026-CUSTOM-001",
        }, format="multipart")

        assert response.status_code == 201
        assert response.data["numero_memorando"] == "MEM-162-2026-CUSTOM-001"

    def test_endpoint_analista_apoyo_puede_registrar(self, api_client, analista_apoyo, expediente_con_informe):
        """ANALISTA_APOYO puede registrar declaratoria via endpoint."""
        api_client.force_authenticate(user=analista_apoyo)
        url = "/api/v1/declaratorias/"
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "mem_analista.pdf"

        response = api_client.post(url, {
            "expediente_id": str(expediente_con_informe.id),
            "archivo_memorando": archivo,
        }, format="multipart")

        assert response.status_code == 201
        # DRF serializa UUID como string
        assert str(response.data["decano"]) == str(analista_apoyo.pk)


class TestFlujoCompletoInformeDeclaratoria:
    """Test de integración end-to-end: Informe -> Declaratoria."""

    def test_flujo_completo_emitir_informe_luego_declaratoria(
        self, decano, secretario_abogado, estudiante, expediente_en_verificacion_sin_informe
    ):
        """Flujo E2E: Verificar checklist -> Emitir Informe -> Registrar Declaratoria."""
        from apps.peticiones.adapters.models import CatalogoDocumental, ESTADO_CARGADO

        # Completar checklist para expediente_en_verificacion_sin_informe
        for codigo, nombre in [
            ("REQ-03", "Certificado Militar"),
            ("REQ-04", "Título de Bachiller"),
            ("REQ-05", "Record Académico Legalizado"),
        ]:
            requisito = CatalogoDocumental.objects.create(
                codigo_requisito=codigo, nombre=nombre,
                es_obligatorio_base=True, fase="FASE_1",
                rol_emisor_sugerido="SECRETARIA_CARRERA", activo=True,
            )
            peticion = PeticionDocumental.objects.create(
                expediente=expediente_en_verificacion_sin_informe, requisito=requisito,
                estado_peticion=ESTADO_VERIFICADO, dependencia_emisora="SECRETARIA_CARRERA",
            )
            DocumentoEntregado.objects.create(
                peticion=peticion, version=1,
                archivo_path=f"expedientes/2026/{expediente_en_verificacion_sin_informe.id}/{codigo}.pdf",
                nombre_original=f"{codigo}.pdf", tamanio_bytes=len(PDF_VALIDO),
                hash_sha256="a" * 64, tipo_mime="application/pdf",
                subido_por=estudiante, es_vigente=True,
            )
            ChecklistVerification.objects.create(
                expediente=expediente_en_verificacion_sin_informe, requisito=requisito,
                estado_verificacion="VERIFICADO", evaluado_por=secretario_abogado,
            )

        # 1. Emitir Informe (Secretario Abogado)
        informe = emitir_informe(
            usuario=secretario_abogado,
            expediente_id=expediente_en_verificacion_sin_informe.id,
            dictamen="APTO",
        )

        assert informe.numero_providencia.startswith("PROV-590-")

        # Verificar estado INFORME_EMITIDO
        expediente_en_verificacion_sin_informe.refresh_from_db()
        assert expediente_en_verificacion_sin_informe.estado == ExpedienteTitulacion.ESTADO_INFORME_EMITIDO

        # 2. Registrar Declaratoria (Decano)
        declaratoria = declarar_aptitud(
            usuario=decano,
            expediente_id=expediente_en_verificacion_sin_informe.id,
            archivo_memorando=io.BytesIO(PDF_VALIDO),
        )

        # Verificar estado final DECLARADA_APTA
        expediente_en_verificacion_sin_informe.refresh_from_db()
        assert expediente_en_verificacion_sin_informe.estado == ExpedienteTitulacion.ESTADO_DECLARADA_APTA

        # Verificar declaratoria creada
        assert hasattr(expediente_en_verificacion_sin_informe, "declaratoria_aptitud")
        assert expediente_en_verificacion_sin_informe.declaratoria_aptitud.numero_memorando.startswith("MEM-162-")

        # Verificar historial completo
        historial = HistorialEstado.objects.filter(expediente=expediente_en_verificacion_sin_informe)
        estados = list(historial.values_list("estado_nuevo", flat=True))
        assert ExpedienteTitulacion.ESTADO_INFORME_EMITIDO in estados
        assert ExpedienteTitulacion.ESTADO_DECLARADA_APTA in estados


class TestValidacionPDFMemorando:
    """Tests específicos de validación PDF para el memorando."""

    def test_rechaza_ejecutable_renombrado_como_pdf(self, decano, expediente_con_informe):
        """Rechaza .exe renombrado como .pdf."""
        archivo = io.BytesIO(EJECUTABLE_RENOMBRADO)
        archivo.name = "malware.pdf"

        with pytest.raises(PDFInvalidoError) as exc_info:
            declarar_aptitud(
                usuario=decano,
                expediente_id=expediente_con_informe.id,
                archivo_memorando=archivo,
            )
        assert exc_info.value.code == "invalid_magic_bytes"

    def test_rechaza_imagen_png_como_pdf(self, decano, expediente_con_informe):
        """Rechaza PNG renombrado como .pdf."""
        IMAGEN_PNG = b"\x89PNG\r\n\x1a\n" + b"x" * 100
        archivo = io.BytesIO(IMAGEN_PNG)
        archivo.name = "imagen.pdf"

        with pytest.raises(PDFInvalidoError) as exc_info:
            declarar_aptitud(
                usuario=decano,
                expediente_id=expediente_con_informe.id,
                archivo_memorando=archivo,
            )
        assert exc_info.value.code == "invalid_magic_bytes"

    def test_rechaza_archivo_vacio(self, decano, expediente_con_informe):
        """Rechaza archivo vacío."""
        archivo = io.BytesIO(b"")
        archivo.name = "vacio.pdf"

        with pytest.raises(PDFInvalidoError):
            declarar_aptitud(
                usuario=decano,
                expediente_id=expediente_con_informe.id,
                archivo_memorando=archivo,
            )
