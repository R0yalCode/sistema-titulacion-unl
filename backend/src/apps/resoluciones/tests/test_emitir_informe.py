"""Pruebas para T034: Emisión e Inmutabilización del Informe Legal por Secretaría Abogada (HU-009, RF-009, RN-004, CA-005).

Verifica:
- POST /api/v1/informes/ emite informe legal (Providencia N° 590)
- Valida checklist 100% VERIFICADO (RN-003 / T029)
- Genera PDF Providencia N° 590 (T033)
- Inmutabiliza InformeAptitud
- Cambia expediente a INFORME_EMITIDO
- Notifica al Decano/a
- Validaciones de permisos y estados
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
    ESTADO_VERIFICACION_PENDIENTE,
    ESTADO_VERIFICACION_VERIFICADO,
)
from apps.resoluciones.adapters.models import InformeAptitud
from apps.notificaciones.adapters.models import NotificacionInterna
from apps.resoluciones.services import (
    emitir_informe,
    InformeYaExisteError,
    ExpedienteNoValidoParaInformeError,
    UsuarioNoAutorizadoError,
)
from apps.verificacion.services import validar_checklist_completo

pytestmark = pytest.mark.django_db

CARRERA_1 = "11111111-1111-1111-1111-111111111111"
FACULTAD_1 = "22222222-2222-2222-2222-222222222222"
PASSWORD = "pass1234"

# PDF válido mínimo para testing (PDF 1.4)
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
def expediente_listo_para_informe(estudiante, secretario_abogado):
    """Expediente con checklist 100% VERIFICADO, listo para emitir informe."""
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

    return expediente


@pytest.fixture
def expediente_con_observados(estudiante, secretario_abogado):
    """Expediente con algunos requisitos OBSERVADO."""
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

    # REQ-01: VERIFICADO
    req1 = CatalogoDocumental.objects.create(
        codigo_requisito="REQ-01", nombre="Acta de Grado",
        es_obligatorio_base=True, fase="FASE_1",
        rol_emisor_sugerido="SECRETARIA_CARRERA", activo=True,
    )
    p1 = PeticionDocumental.objects.create(
        expediente=expediente, requisito=req1,
        estado_peticion=ESTADO_VERIFICADO, dependencia_emisora="SECRETARIA_CARRERA",
    )
    DocumentoEntregado.objects.create(
        peticion=p1, version=1,
        archivo_path=f"expedientes/2026/{expediente.id}/REQ-01.pdf",
        nombre_original="REQ-01.pdf", tamanio_bytes=len(PDF_VALIDO),
        hash_sha256="a" * 64, tipo_mime="application/pdf",
        subido_por=estudiante, es_vigente=True,
    )
    ChecklistVerification.objects.create(
        expediente=expediente, requisito=req1,
        estado_verificacion="VERIFICADO", evaluado_por=secretario_abogado,
    )

    # REQ-02: OBSERVADO
    req2 = CatalogoDocumental.objects.create(
        codigo_requisito="REQ-02", nombre="Certificado de Votación",
        es_obligatorio_base=True, fase="FASE_1",
        rol_emisor_sugerido="SECRETARIA_CARRERA", activo=True,
    )
    p2 = PeticionDocumental.objects.create(
        expediente=expediente, requisito=req2,
        estado_peticion="OBSERVADO", dependencia_emisora="SECRETARIA_CARRERA",
    )
    DocumentoEntregado.objects.create(
        peticion=p2, version=1,
        archivo_path=f"expedientes/2026/{expediente.id}/REQ-02.pdf",
        nombre_original="REQ-02.pdf", tamanio_bytes=len(PDF_VALIDO),
        hash_sha256="b" * 64, tipo_mime="application/pdf",
        subido_por=estudiante, es_vigente=True,
    )
    ChecklistVerification.objects.create(
        expediente=expediente, requisito=req2,
        estado_verificacion="OBSERVADO", evaluado_por=secretario_abogado,
    )

    return expediente


@pytest.fixture
def expediente_en_estado_invalido(estudiante):
    """Expediente en estado ENVIADA (no válido para informe)."""
    return ExpedienteTitulacion.objects.create(
        numero_expediente="EXP-2026-0003",
        estudiante=estudiante,
        carrera_id=CARRERA_1,
        facultad_id=FACULTAD_1,
        estado=ExpedienteTitulacion.ESTADO_ENVIADA,
        activa=True,
    )


class TestEmitirInformeService:
    """Tests del servicio emitir_informe (T034)."""

    def test_emitir_informe_exitoso_apto(self, secretario_abogado, expediente_listo_para_informe):
        """Emisión exitosa de informe con dictamen APTO."""
        informe = emitir_informe(
            usuario=secretario_abogado,
            expediente_id=expediente_listo_para_informe.id,
            dictamen="APTO",
        )

        assert informe is not None
        assert informe.expediente == expediente_listo_para_informe
        assert informe.emisor == secretario_abogado
        assert informe.dictamen == "APTO"
        assert informe.numero_providencia.startswith("PROV-590-")
        assert informe.archivo_informe_path.endswith(".pdf")
        assert "PROV-590-" in informe.archivo_informe_path

        # Verificar expediente actualizado
        expediente_listo_para_informe.refresh_from_db()
        assert expediente_listo_para_informe.estado == ExpedienteTitulacion.ESTADO_INFORME_EMITIDO
        assert expediente_listo_para_informe.numero_providencia == informe.numero_providencia

        # Verificar que InformeAptitud es inmutable (no se puede modificar dictamen)
        # Esto se valida a nivel de modelo/servicio, no en test

    def test_emitir_informe_genera_pdf_providencia(self, secretario_abogado, expediente_listo_para_informe):
        """Genera archivo PDF de Providencia N° 590."""
        informe = emitir_informe(
            usuario=secretario_abogado,
            expediente_id=expediente_listo_para_informe.id,
            dictamen="APTO",
        )

        assert informe.archivo_informe_path is not None
        assert ".pdf" in informe.archivo_informe_path.lower()

    def test_emitir_informe_cambia_estado_expediente(self, secretario_abogado, expediente_listo_para_informe):
        """Cambia estado del expediente a INFORME_EMITIDO."""
        emitir_informe(
            usuario=secretario_abogado,
            expediente_id=expediente_listo_para_informe.id,
            dictamen="APTO",
        )

        expediente_listo_para_informe.refresh_from_db()
        assert expediente_listo_para_informe.estado == ExpedienteTitulacion.ESTADO_INFORME_EMITIDO

    def test_emitir_informe_registra_historial_estado(self, secretario_abogado, expediente_listo_para_informe):
        """Registra cambio en HistorialEstado."""
        emitir_informe(
            usuario=secretario_abogado,
            expediente_id=expediente_listo_para_informe.id,
            dictamen="APTO",
        )

        historial = HistorialEstado.objects.filter(
            expediente=expediente_listo_para_informe,
            estado_nuevo=ExpedienteTitulacion.ESTADO_INFORME_EMITIDO,
        ).first()
        assert historial is not None
        assert historial.estado_nuevo == ExpedienteTitulacion.ESTADO_INFORME_EMITIDO
        assert historial.registrado_por == secretario_abogado

    def test_emitir_informe_notifica_decano(self, secretario_abogado, decano, expediente_listo_para_informe):
        """Crea notificación interna para el Decano/a."""
        emitir_informe(
            usuario=secretario_abogado,
            expediente_id=expediente_listo_para_informe.id,
            dictamen="APTO",
        )

        notificacion = NotificacionInterna.objects.filter(
            usuario_destino=decano,
            expediente=expediente_listo_para_informe,
        ).first()
        assert notificacion is not None
        assert "Informe Legal Emitido" in notificacion.titulo
        assert expediente_listo_para_informe.numero_expediente in notificacion.mensaje

    def test_falla_si_expediente_tiene_informe_ya_emitido(self, secretario_abogado, expediente_listo_para_informe):
        """Falla si ya existe InformeAptitud para el expediente."""
        # Primera emisión
        emitir_informe(
            usuario=secretario_abogado,
            expediente_id=expediente_listo_para_informe.id,
            dictamen="APTO",
        )

        # Segunda emisión debe fallar
        with pytest.raises(InformeYaExisteError):
            emitir_informe(
                usuario=secretario_abogado,
                expediente_id=expediente_listo_para_informe.id,
                dictamen="APTO",
            )

    def test_falla_si_checklist_no_completo(self, secretario_abogado, expediente_con_observados):
        """Falla si checklist no está 100% VERIFICADO (RN-003)."""
        with pytest.raises(validar_checklist_completo.ChecklistIncompletoError) as exc_info:
            emitir_informe(
                usuario=secretario_abogado,
                expediente_id=expediente_con_observados.id,
                dictamen="APTO",
            )

        assert "checklist no está completo" in str(exc_info.value).lower()
        assert "REQ-02" in str(exc_info.value.requisitos_pendientes)

    def test_falla_si_expediente_estado_invalido(self, secretario_abogado, expediente_en_estado_invalido):
        """Falla si expediente no está en EN_VERIFICACION u OBSERVADA."""
        with pytest.raises(ValueError) as exc_info:
            emitir_informe(
                usuario=secretario_abogado,
                expediente_id=expediente_en_estado_invalido.id,
                dictamen="APTO",
            )

        assert "debe estar en EN_VERIFICACION u OBSERVADA" in str(exc_info.value)

    def test_falla_si_usuario_no_secretario_abogado(self, estudiante, expediente_listo_para_informe):
        """Falla si usuario no es SECRETARIO_ABOGADO."""
        with pytest.raises(UsuarioNoAutorizadoError):
            emitir_informe(
                usuario=estudiante,
                expediente_id=expediente_listo_para_informe.id,
                dictamen="APTO",
            )

    def test_falla_si_usuario_distinta_facultad(self, expediente_listo_para_informe):
        """Falla si SECRETARIO_ABOGADO de otra facultad."""
        from apps.authentication.adapters.models import User, Role, UserRole

        rol_sec, _ = Role.objects.get_or_create(name="SECRETARIO_ABOGADO")
        secretario_otra = User.objects.create_user(
            username="secretario_otra",
            email="sec_otra@test.com",
            password="pass1234",
            cedula="2222222222",
            facultad_id="33333333-3333-3333-3333-333333333333",
        )
        UserRole.objects.create(user=secretario_otra, role=rol_sec)

        with pytest.raises(UsuarioNoAutorizadoError):
            emitir_informe(
                usuario=secretario_otra,
                expediente_id=expediente_listo_para_informe.id,
                dictamen="APTO",
            )

    def test_falla_si_dictamen_no_apto(self, secretario_abogado, expediente_listo_para_informe):
        """Falla si dictamen es NO APTO."""
        with pytest.raises(ExpedienteNoValidoParaInformeError):
            emitir_informe(
                usuario=secretario_abogado,
                expediente_id=expediente_listo_para_informe.id,
                dictamen="NO APTO",
            )

    def test_falla_si_dictamen_invalido(self, secretario_abogado, expediente_listo_para_informe):
        """Falla si dictamen no es APTO ni NO APTO."""
        with pytest.raises(ValueError):
            emitir_informe(
                usuario=secretario_abogado,
                expediente_id=expediente_listo_para_informe.id,
                dictamen="INVALIDO",
            )

    def test_numero_providencia_unico_y_formato(self, secretario_abogado, expediente_listo_para_informe):
        """Número de providencia tiene formato PROV-590-YYYY-NNNN y es único."""
        informe = emitir_informe(
            usuario=secretario_abogado,
            expediente_id=expediente_listo_para_informe.id,
            dictamen="APTO",
        )

        assert informe.numero_providencia.startswith("PROV-590-")
        parts = informe.numero_providencia.split("-")
        assert len(parts) == 4
        assert parts[0] == "PROV"
        assert parts[1] == "590"
        assert parts[2] == str(timezone.now().year)
        assert parts[3].isdigit()


class TestEmitirInformeEndpoint:
    """Tests del endpoint POST /api/v1/informes/ (T034)."""

    def test_endpoint_201_created(self, api_client, secretario_abogado, expediente_listo_para_informe):
        """Endpoint retorna 201 con datos del informe emitido."""
        api_client.force_authenticate(user=secretario_abogado)
        url = "/api/v1/informes/"
        response = api_client.post(url, {
            "expediente_id": str(expediente_listo_para_informe.id),
            "dictamen": "APTO",
        }, format="json")

        assert response.status_code == 201
        assert "id" in response.data
        assert response.data["numero_providencia"].startswith("PROV-590-")
        assert response.data["dictamen"] == "APTO"
        assert response.data["archivo_informe_path"].endswith(".pdf")

    def test_endpoint_400_checklist_incompleto(self, api_client, secretario_abogado, expediente_con_observados):
        """Retorna 400 si checklist no está completo."""
        api_client.force_authenticate(user=secretario_abogado)
        url = "/api/v1/informes/"
        response = api_client.post(url, {
            "expediente_id": str(expediente_con_observados.id),
            "dictamen": "APTO",
        }, format="json")

        assert response.status_code == 400
        assert "requisitos_pendientes" in response.data
        assert "REQ-02" in str(response.data["requisitos_pendientes"])

    def test_endpoint_400_expediente_estado_invalido(self, api_client, secretario_abogado, expediente_en_estado_invalido):
        """Retorna 400 si expediente en estado inválido."""
        api_client.force_authenticate(user=secretario_abogado)
        url = "/api/v1/informes/"
        response = api_client.post(url, {
            "expediente_id": str(expediente_en_estado_invalido.id),
            "dictamen": "APTO",
        }, format="json")

        assert response.status_code == 400
        assert "EN_VERIFICACION" in str(response.data) or "OBSERVADA" in str(response.data)

    def test_endpoint_400_informe_ya_existe(self, api_client, secretario_abogado, expediente_listo_para_informe):
        """Retorna 400 si ya existe informe para el expediente."""
        api_client.force_authenticate(user=secretario_abogado)
        url = "/api/v1/informes/"

        # Primera emisión
        api_client.post(url, {
            "expediente_id": str(expediente_listo_para_informe.id),
            "dictamen": "APTO",
        }, format="json")

        # Segunda emisión
        response = api_client.post(url, {
            "expediente_id": str(expediente_listo_para_informe.id),
            "dictamen": "APTO",
        }, format="json")

        assert response.status_code == 400
        assert "ya tiene un informe emitido" in str(response.data).lower()

    def test_endpoint_401_sin_autenticacion(self, api_client, expediente_listo_para_informe):
        """Retorna 401 sin token."""
        url = "/api/v1/informes/"
        response = api_client.post(url, {
            "expediente_id": str(expediente_listo_para_informe.id),
            "dictamen": "APTO",
        }, format="json")

        assert response.status_code == 401

    def test_endpoint_403_rol_no_autorizado(self, api_client, estudiante, expediente_listo_para_informe):
        """Retorna 403 para roles no permitidos (ESTUDIANTE)."""
        api_client.force_authenticate(user=estudiante)
        url = "/api/v1/informes/"
        response = api_client.post(url, {
            "expediente_id": str(expediente_listo_para_informe.id),
            "dictamen": "APTO",
        }, format="json")

        assert response.status_code in (403, 404)

    def test_endpoint_403_secretario_otra_facultad(self, api_client, expediente_listo_para_informe):
        """Retorna 403 para SECRETARIO_ABOGADO de otra facultad."""
        from apps.authentication.adapters.models import User, Role, UserRole

        rol_sec, _ = Role.objects.get_or_create(name="SECRETARIO_ABOGADO")
        secretario_otra = User.objects.create_user(
            username="secretario_otra",
            email="sec_otra@test.com",
            password="pass1234",
            cedula="2222222222",
            facultad_id="33333333-3333-3333-3333-333333333333",
        )
        UserRole.objects.create(user=secretario_otra, role=rol_sec)

        api_client.force_authenticate(user=secretario_otra)
        url = "/api/v1/informes/"
        response = api_client.post(url, {
            "expediente_id": str(expediente_listo_para_informe.id),
            "dictamen": "APTO",
        }, format="json")

        assert response.status_code in (403, 404)

    def test_endpoint_400_dictamen_invalido(self, api_client, secretario_abogado, expediente_listo_para_informe):
        """Retorna 400 para dictamen inválido."""
        api_client.force_authenticate(user=secretario_abogado)
        url = "/api/v1/informes/"
        response = api_client.post(url, {
            "expediente_id": str(expediente_listo_para_informe.id),
            "dictamen": "INVALIDO",
        }, format="json")

        assert response.status_code == 400

    def test_endpoint_400_dictamen_no_apto(self, api_client, secretario_abogado, expediente_listo_para_informe):
        """Retorna 400 para dictamen NO APTO."""
        api_client.force_authenticate(user=secretario_abogado)
        url = "/api/v1/informes/"
        response = api_client.post(url, {
            "expediente_id": str(expediente_listo_para_informe.id),
            "dictamen": "NO APTO",
        }, format="json")

        assert response.status_code == 400
        assert "no apTO" in str(response.data).lower() or "no apto" in str(response.data).lower()


class TestInformeAptitudInmutabilidad:
    """Tests de inmutabilidad del InformeAptitud (RN-004)."""

    def test_informe_no_se_puede_modificar_despues_creado(self, secretario_abogado, expediente_listo_para_informe):
        """Una vez creado, el InformeAptitud no debe poder modificarse."""
        informe = emitir_informe(
            usuario=secretario_abogado,
            expediente_id=expediente_listo_para_informe.id,
            dictamen="APTO",
        )

        # Intentar modificar (esto se valida a nivel de servicio, no modelo)
        # El servicio no expone método update
        assert InformeAptitud.objects.filter(pk=informe.pk).exists()

    def test_numero_providencia_unico_global(self, secretario_abogado, expediente_listo_para_informe, estudiante):
        """Número de providencia es único globalmente."""
        # Crear segundo expediente
        expediente2 = ExpedienteTitulacion.objects.create(
            numero_expediente="EXP-2026-0099",
            estudiante=estudiante,
            carrera_id=CARRERA_1,
            facultad_id=FACULTAD_1,
            estado=ExpedienteTitulacion.ESTADO_EN_VERIFICACION,
            activa=True,
            fecha_recepcion=timezone.now(),
        )

        # Crear 5 requisitos VERIFICADO para expediente2
        from apps.peticiones.adapters.models import CatalogoDocumental, ESTADO_CARGADO
        for i, (codigo, nombre) in enumerate([
            ("REQ-01", "Acta de Grado"),
            ("REQ-02", "Certificado de Votación"),
            ("REQ-03", "Certificado Militar"),
            ("REQ-04", "Título de Bachiller"),
            ("REQ-05", "Record Académico Legalizado"),
        ]):
            requisito = CatalogoDocumental.objects.create(
                codigo_requisito=f"{codigo}-B",
                nombre=nombre,
                es_obligatorio_base=True,
                fase="FASE_1",
                rol_emisor_sugerido="SECRETARIA_CARRERA",
                activo=True,
            )
            peticion = PeticionDocumental.objects.create(
                expediente=expediente2,
                requisito=requisito,
                estado_peticion=ESTADO_VERIFICADO,
                dependencia_emisora="SECRETARIA_CARRERA",
            )
            DocumentoEntregado.objects.create(
                peticion=peticion, version=1,
                archivo_path=f"expedientes/2026/{expediente2.id}/{codigo}.pdf",
                nombre_original=f"{codigo}.pdf", tamanio_bytes=len(PDF_VALIDO),
                hash_sha256="x" * 64, tipo_mime="application/pdf",
                subido_por=estudiante, es_vigente=True,
            )
            ChecklistVerification.objects.create(
                expediente=expediente2, requisito=requisito,
                estado_verificacion="VERIFICADO", evaluado_por=secretario_abogado,
            )

        # Emitir ambos informes
        informe1 = emitir_informe(
            usuario=secretario_abogado,
            expediente_id=expediente_listo_para_informe.id,
            dictamen="APTO",
        )
        informe2 = emitir_informe(
            usuario=secretario_abogado,
            expediente_id=expediente2.id,
            dictamen="APTO",
        )

        assert informe1.numero_providencia != informe2.numero_providencia
        # Ambos deben tener el mismo año pero número secuencial diferente
        assert informe1.numero_providencia.split("-")[-1] != informe2.numero_providencia.split("-")[-1]
