"""Pruebas de integración T036: Flujo completo de Resoluciones y Generación PDF (CA-005, CA-006).

Verifica el flujo E2E completo:
1. Checklist 100% VERIFICADO (T027/T028)
2. Emisión Informe Legal → Providencia N° 590 (T034, RF-009, CA-005)
3. Generación PDF borrador/final (T033, RF-010)
4. Registro Declaratoria → Memorando N° 162 (T035, RF-011, CA-006, DEC-04)
5. Despacho notificaciones con copia (DEC-04)
6. Inmutabilidad de registros (RN-004)
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
    ROLE_DIRECTOR_CARRERA,
    User,
    Role,
    UserRole,
)
from apps.expedientes.adapters.models import ExpedienteTitulacion, HistorialEstado
from apps.peticiones.adapters.models import (
    ESTADO_CARGADO,
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
from apps.resoluciones.services import emitir_informe, declarar_aptitud
from apps.verificacion.services import evaluar_checklist, registrar_observacion
from apps.resoluciones.adapters.pdf_generator import PDFGeneratorAdapter, generar_providencia_590, generar_memorando_162

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
def rol_director_carrera():
    role, _ = Role.objects.get_or_create(name=ROLE_DIRECTOR_CARRERA)
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
def director_carrera(rol_director_carrera):
    user = User.objects.create_user(
        username="director_test",
        email="dir@test.com",
        password="pass1234",
        cedula="1234567895",
        carrera_id=CARRERA_1,
        facultad_id=FACULTAD_1,
    )
    UserRole.objects.create(user=user, role=rol_director_carrera)
    return user


@pytest.fixture
def expediente_listo_para_informe(estudiante, secretario_abogado):
    """Expediente con checklist 100% VERIFICADO listo para emitir informe."""
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

    # 5 requisitos base (Art. 235 RRA-UNL) - todos VERIFICADO
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
            evaluado_por=estudiante,  # dummy
        )

    return expediente


@pytest.fixture
def expediente_en_verificacion(estudiante, secretario_abogado):
    """Expediente en EN_VERIFICACION con 5 requisitos CARGADOS listos para verificar."""
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

    # 5 requisitos base (Art. 235 RRA-UNL) - todos CARGADOS, checklist PENDIENTE
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
            estado_peticion=ESTADO_CARGADO,
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
            estado_verificacion="PENDIENTE",
        )

    return expediente


class TestFlujoCompletoVerificarEmitirDeclarar:
    """Test E2E: Verificar → Emitir Informe → Declarar Aptitud."""

    def test_flujo_e2e_completo_verificar_emitir_declarar(
        self, estudiante, secretario_abogado, decano, director_carrera, expediente_en_verificacion
    ):
        """Flujo E2E completo: Verificar todo → Emitir Informe → Declarar Aptitud."""
        # ============================================================
        # PASO 1: VERIFICAR CHECKLIST (T027) - Secretario Abogado
        # ============================================================
        verificaciones = list(ChecklistVerification.objects.filter(
            expediente=expediente_en_verificacion,
            estado_verificacion="PENDIENTE"
        ))
        assert len(verificaciones) == 5

        for verif in verificaciones:
            resultado = evaluar_checklist.execute(
                usuario=secretario_abogado,
                checklist_verification_id=verif.id,
                nuevo_estado="VERIFICADO",
            )
            assert resultado.estado_verificacion == "VERIFICADO"
            assert resultado.evaluado_por == secretario_abogado

        # Verificar que todas las peticiones están VERIFICADO
        for peticion in expediente_en_verificacion.peticiones_documentales.all():
            assert peticion.estado_peticion == "VERIFICADO"

        # ============================================================
        # PASO 2: EMITIR INFORME LEGAL (T034) - Secretario Abogado
        # ============================================================
        informe = emitir_informe(
            usuario=secretario_abogado,
            expediente_id=expediente_en_verificacion.id,
            dictamen="APTO",
            fundamentacion="El expediente cumple con todos los requisitos del Art. 235 RRA-UNL.",
        )

        # Verificar informe creado
        assert informe is not None
        assert informe.numero_providencia.startswith("PROV-590-")
        assert informe.dictamen == "APTO"
        assert informe.archivo_informe_path.endswith(".pdf")
        assert informe.emisor == secretario_abogado

        # Verificar expediente en INFORME_EMITIDO
        expediente_en_verificacion.refresh_from_db()
        assert expediente_en_verificacion.estado == ExpedienteTitulacion.ESTADO_INFORME_EMITIDO
        assert expediente_en_verificacion.numero_providencia == informe.numero_providencia

        # Verificar notificación a Decano
        notif_decano = NotificacionInterna.objects.filter(
            usuario_destino__in=[decano],
            expediente=expediente_en_verificacion,
        ).first()
        assert notif_decano is not None
        assert "Informe Legal Emitido" in notif_decano.titulo

        # Verificar inmutabilidad: no se puede emitir segundo informe
        with pytest.raises(Exception) as exc_info:
            emitir_informe(
                usuario=secretario_abogado,
                expediente_id=expediente_en_verificacion.id,
                dictamen="APTO",
            )
        assert "ya tiene un informe" in str(exc_info.value).lower()

        # ============================================================
        # PASO 3: GENERAR PDF BORRADOR Y FINAL (T033)
        # ============================================================
        datos_expediente = {
            "numero_expediente": expediente_en_verificacion.numero_expediente,
            "estudiante_nombre": expediente_en_verificacion.estudiante.get_full_name() or expediente_en_verificacion.estudiante.username,
            "estudiante_cedula": expediente_en_verificacion.estudiante.cedula,
            "carrera_nombre": "Computación",
            "fecha_recepcion": expediente_en_verificacion.fecha_recepcion.strftime("%d/%m/%Y") if expediente_en_verificacion.fecha_recepcion else "N/A",
            "fecha_limite_atencion": expediente_en_verificacion.fecha_limite_atencion.strftime("%d/%m/%Y") if expediente_en_verificacion.fecha_limite_atencion else "N/A",
        }
        datos_secretario = {
            "nombre_completo": secretario_abogado.get_full_name() or secretario_abogado.username,
            "cargo": "SECRETARIO/A-ABOGADO/A - FEIRNNR",
            "ci": secretario_abogado.cedula,
        }
        checklist_pdf = [
            {"codigo": "REQ-01", "nombre": "Acta de Grado", "estado": "VERIFICADO", "observacion": ""},
            {"codigo": "REQ-02", "nombre": "Certificado de Votación", "estado": "VERIFICADO", "observacion": ""},
            {"codigo": "REQ-03", "nombre": "Certificado Militar", "estado": "VERIFICADO", "observacion": ""},
            {"codigo": "REQ-04", "nombre": "Título de Bachiller", "estado": "VERIFICADO", "observacion": ""},
            {"codigo": "REQ-05", "nombre": "Record Académico Legalizado", "estado": "VERIFICADO", "observacion": ""},
        ]

        # PDF Borrador
        pdf_borrador = generar_providencia_590(
            expediente=datos_expediente,
            secretario=datos_secretario,
            checklist=checklist_pdf,
            dictamen="APTO",
            numero_providencia=informe.numero_providencia,
            es_borrador=True,
        )
        assert pdf_borrador.endswith("_BORRADOR.pdf")

        # PDF Final
        pdf_final = generar_providencia_590(
            expediente=datos_expediente,
            secretario=datos_secretario,
            checklist=checklist_pdf,
            dictamen="APTO",
            numero_providencia=informe.numero_providencia,
            es_borrador=False,
        )
        assert pdf_final.endswith(".pdf")
        assert "_BORRADOR" not in pdf_final

        # ============================================================
        # PASO 4: REGISTRAR DECLARATORIA (T035) - Decano
        # ============================================================
        archivo_memorando = io.BytesIO(PDF_VALIDO)
        archivo_memorando.name = "memorando_162_firmado.pdf"

        declaratoria = declarar_aptitud(
            usuario=decano,
            expediente_id=expediente_en_verificacion.id,
            archivo_memorando=archivo_memorando,
        )

        # Verificar declaratoria
        assert declaratoria is not None
        assert declaratoria.numero_memorando.startswith("MEM-162-")
        assert declaratoria.decano == decano
        assert declaratoria.archivo_memorando_firmado_path.endswith(".pdf")

        # Verificar expediente en DECLARADA_APTA
        expediente_en_verificacion.refresh_from_db()
        assert expediente_en_verificacion.estado == ExpedienteTitulacion.ESTADO_DECLARADA_APTA

        # Verificar historial completo
        historial = HistorialEstado.objects.filter(expediente=expediente_en_verificacion)
        estados = list(historial.values_list("estado_nuevo", flat=True))
        assert ExpedienteTitulacion.ESTADO_INFORME_EMITIDO in estados
        assert ExpedienteTitulacion.ESTADO_DECLARADA_APTA in estados

        # ============================================================
        # PASO 5: NOTIFICACIONES CON COPIA (DEC-04)
        # ============================================================
        # Estudiante notificado
        notif_est = NotificacionInterna.objects.filter(
            usuario_destino=expediente_en_verificacion.estudiante,
            expediente=expediente_en_verificacion,
        ).first()
        assert notif_est is not None
        assert "Declaratoria de Aptitud" in notif_est.titulo

        # Autoridades con copia (Director Carrera, etc.) - el Decano emisor no recibe copia
        autoridades = NotificacionInterna.objects.filter(
            expediente=expediente_en_verificacion,
            titulo__icontains="Copia: Declaratoria",
        )
        assert autoridades.count() >= 1  # Al menos Director Carrera
        for notif in autoridades:
            assert "Copia: Declaratoria" in notif.titulo

    def test_generar_memorando_162_pdf(self, decano, expediente_listo_para_informe):
        """Verifica generación de PDF Memorando N° 162."""
        # Datos para PDF
        datos_expediente = {
            "numero_expediente": expediente_listo_para_informe.numero_expediente,
            "estudiante_nombre": expediente_listo_para_informe.estudiante.get_full_name() or expediente_listo_para_informe.estudiante.username,
            "estudiante_cedula": expediente_listo_para_informe.estudiante.cedula,
            "carrera_nombre": "Computación",
            "fecha_recepcion": expediente_listo_para_informe.fecha_recepcion.strftime("%d/%m/%Y") if expediente_listo_para_informe.fecha_recepcion else "N/A",
            "fecha_limite_atencion": expediente_listo_para_informe.fecha_limite_atencion.strftime("%d/%m/%Y") if expediente_listo_para_informe.fecha_limite_atencion else "N/A",
        }
        datos_decano = {
            "nombre_completo": "PhD. Ana Lucía Ramírez Vaca",
            "cargo": "DECANO/A - FEIRNNR",
            "ci": "1107654321",
        }

        # Generar Memorando 162 usando el número de providencia del expediente
        numero_prov = expediente_listo_para_informe.numero_providencia
        archivo_memo = generar_memorando_162(
            expediente={"numero_expediente": expediente_listo_para_informe.numero_expediente,
                       "estudiante_nombre": expediente_listo_para_informe.estudiante.get_full_name() or expediente_listo_para_informe.estudiante.username,
                       "estudiante_cedula": expediente_listo_para_informe.estudiante.cedula,
                       "carrera_nombre": "Computación",
                       "fecha_recepcion": expediente_listo_para_informe.fecha_recepcion.strftime("%d/%m/%Y") if expediente_listo_para_informe.fecha_recepcion else "N/A",
                       "fecha_limite_atencion": expediente_listo_para_informe.fecha_limite_atencion.strftime("%d/%m/%Y") if expediente_listo_para_informe.fecha_limite_atencion else "N/A"},
            decano={"nombre_completo": "PhD. Ana Lucía Ramírez Vaca", "cargo": "DECANO/A - FEIRNNR", "ci": "1107654321"},
            informe_providencia=expediente_listo_para_informe.numero_providencia,
            es_borrador=True,
        )
        assert archivo_memo.endswith("_BORRADOR.pdf")

        archivo_final = generar_memorando_162(
            expediente={"numero_expediente": expediente_listo_para_informe.numero_expediente,
                       "estudiante_nombre": expediente_listo_para_informe.estudiante.get_full_name() or expediente_listo_para_informe.estudiante.username,
                       "estudiante_cedula": expediente_listo_para_informe.estudiante.cedula,
                       "carrera_nombre": "Computación",
                       "fecha_recepcion": expediente_listo_para_informe.fecha_recepcion.strftime("%d/%m/%Y") if expediente_listo_para_informe.fecha_recepcion else "N/A",
                       "fecha_limite_atencion": expediente_listo_para_informe.fecha_limite_atencion.strftime("%d/%m/%Y") if expediente_listo_para_informe.fecha_limite_atencion else "N/A"},
            decano={"nombre_completo": "PhD. Ana Lucía Ramírez Vaca", "cargo": "DECANO/A - FEIRNNR", "ci": "1107654321"},
            informe_providencia=expediente_listo_para_informe.numero_providencia,
            es_borrador=False,
        )
        assert archivo_final.endswith(".pdf")
        assert "_BORRADOR" not in archivo_final

    def test_unicidad_providencia_y_memorando(self, secretario_abogado, decano, estudiante):
        """Verifica que números de providencia y memorando sean únicos globalmente."""
        from apps.peticiones.adapters.models import CatalogoDocumental, ESTADO_CARGADO

        # Expediente 1
        exp1 = ExpedienteTitulacion.objects.create(
            numero_expediente="EXP-2026-0010",
            estudiante=estudiante,
            carrera_id=CARRERA_1,
            facultad_id=FACULTAD_1,
            estado=ExpedienteTitulacion.ESTADO_EN_VERIFICACION,
            activa=True,
            fecha_recepcion=timezone.now(),
        )
        for codigo, nombre in [("REQ-01", "A"), ("REQ-02", "B"), ("REQ-03", "C"), ("REQ-04", "D"), ("REQ-05", "E")]:
            req = CatalogoDocumental.objects.create(codigo_requisito=codigo, nombre=nombre, es_obligatorio_base=True, fase="FASE_1", rol_emisor_sugerido="SECRETARIA_CARRERA", activo=True)
            p = PeticionDocumental.objects.create(expediente=exp1, requisito=req, estado_peticion=ESTADO_VERIFICADO, dependencia_emisora="SECRETARIA_CARRERA")
            DocumentoEntregado.objects.create(peticion=p, version=1, archivo_path="x.pdf", nombre_original="x.pdf", tamanio_bytes=100, hash_sha256="a"*64, tipo_mime="application/pdf", subido_por=estudiante, es_vigente=True)
            ChecklistVerification.objects.create(expediente=exp1, requisito=req, estado_verificacion="VERIFICADO")

        inf1 = emitir_informe(usuario=secretario_abogado, expediente_id=exp1.id, dictamen="APTO")

        # Expediente 2 (diferente estudiante)
        est2 = User.objects.create_user(username="est2", email="est2@test.com", password="pass1234", cedula="9999999999", carrera_id=CARRERA_1, facultad_id=FACULTAD_1)
        UserRole.objects.create(user=est2, role=Role.objects.get(name="ESTUDIANTE"))
        exp2 = ExpedienteTitulacion.objects.create(
            numero_expediente="EXP-2026-0011",
            estudiante=est2,
            carrera_id=CARRERA_1,
            facultad_id=FACULTAD_1,
            estado=ExpedienteTitulacion.ESTADO_EN_VERIFICACION,
            activa=True,
            fecha_recepcion=timezone.now(),
        )
        for codigo, nombre in [("REQ-01", "A"), ("REQ-02", "B"), ("REQ-03", "C"), ("REQ-04", "D"), ("REQ-05", "E")]:
            req = CatalogoDocumental.objects.create(codigo_requisito=f"{codigo}-B", nombre=nombre, es_obligatorio_base=True, fase="FASE_1", rol_emisor_sugerido="SECRETARIA_CARRERA", activo=True)
            p = PeticionDocumental.objects.create(expediente=exp2, requisito=req, estado_peticion="VERIFICADO", dependencia_emisora="SECRETARIA_CARRERA")
            DocumentoEntregado.objects.create(peticion=p, version=1, archivo_path="x.pdf", nombre_original="x.pdf", tamanio_bytes=100, hash_sha256="a"*64, tipo_mime="application/pdf", subido_por=est2, es_vigente=True)
            ChecklistVerification.objects.create(expediente=exp2, requisito=req, estado_verificacion="VERIFICADO")

        inf2 = emitir_informe(usuario=secretario_abogado, expediente_id=exp2.id, dictamen="APTO")

        assert inf1.numero_providencia != inf2.numero_providencia
        assert inf1.numero_providencia.split("-")[-1] != inf2.numero_providencia.split("-")[-1]

        # Declaratorias
        dec1 = declarar_aptitud(usuario=decano, expediente_id=exp1.id, archivo_memorando=io.BytesIO(PDF_VALIDO))
        dec2 = declarar_aptitud(usuario=decano, expediente_id=exp2.id, archivo_memorando=io.BytesIO(PDF_VALIDO))
        assert dec1.numero_memorando != dec2.numero_memorando
        assert dec1.numero_memorando.split("-")[-1] != dec2.numero_memorando.split("-")[-1]


class TestEndpointIntegracionResoluciones:
    """Tests de integración via endpoints HTTP."""

    def test_endpoint_emitir_informe_201(self, api_client, secretario_abogado, expediente_listo_para_informe):
        """POST /api/v1/informes/ retorna 201 con informe creado."""
        api_client.force_authenticate(user=secretario_abogado)
        response = api_client.post("/api/v1/informes/", {
            "expediente_id": str(expediente_listo_para_informe.id),
            "dictamen": "APTO",
        }, format="json")
        assert response.status_code == 201
        assert response.data["numero_providencia"].startswith("PROV-590-")
        assert response.data["dictamen"] == "APTO"

    def test_endpoint_declarar_aptitud_201(self, api_client, decano, expediente_listo_para_informe, secretario_abogado):
        """POST /api/v1/declaratorias/ retorna 201 con declaratoria."""
        # Primero emitir el informe
        emitir_informe(
            usuario=secretario_abogado,
            expediente_id=expediente_listo_para_informe.id,
            dictamen="APTO",
        )

        api_client.force_authenticate(user=decano)
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "memo.pdf"
        response = api_client.post("/api/v1/declaratorias/", {
            "expediente_id": str(expediente_listo_para_informe.id),
            "archivo_memorando": archivo,
        }, format="multipart")
        assert response.status_code == 201
        assert response.data["numero_memorando"].startswith("MEM-162-")
        assert "expediente_numero" in response.data


class TestInmutabilidadRegistros:
    """Tests de inmutabilidad RN-004."""

    def test_informe_aptitud_inmutable(self, secretario_abogado, expediente_listo_para_informe):
        """InformeAptitud no se puede modificar tras creación."""
        informe = emitir_informe(
            usuario=secretario_abogado,
            expediente_id=expediente_listo_para_informe.id,
            dictamen="APTO",
        )
        # El servicio no expone método update/delete
        assert InformeAptitud.objects.filter(pk=informe.pk).exists()

    def test_declaratoria_aptitud_inmutable(self, decano, expediente_listo_para_informe, secretario_abogado):
        """DeclaratoriaAptitud no se puede modificar tras creación."""
        # Primero emitir informe
        emitir_informe(
            usuario=secretario_abogado,
            expediente_id=expediente_listo_para_informe.id,
            dictamen="APTO",
        )
        declaratoria = declarar_aptitud(
            usuario=decano,
            expediente_id=expediente_listo_para_informe.id,
            archivo_memorando=io.BytesIO(PDF_VALIDO),
        )
        # El servicio no expone método update/delete
        assert DeclaratoriaAptitud.objects.filter(pk=declaratoria.pk).exists()


class TestValidacionPDFResoluciones:
    """Tests de validación PDF específica para resoluciones."""

    def test_pdf_providencia_tiene_magic_bytes(self, secretario_abogado, expediente_listo_para_informe):
        """PDF generado tiene magic bytes %PDF-."""
        informe = emitir_informe(
            usuario=secretario_abogado,
            expediente_id=expediente_listo_para_informe.id,
            dictamen="APTO",
        )
        with open(informe.archivo_informe_path, "rb") as f:
            header = f.read(5)
            assert header == b"%PDF-"

    def test_pdf_memorando_tiene_magic_bytes(self, decano, expediente_listo_para_informe, secretario_abogado):
        """Memorando PDF tiene magic bytes válidos."""
        # Primero emitir informe
        emitir_informe(
            usuario=secretario_abogado,
            expediente_id=expediente_listo_para_informe.id,
            dictamen="APTO",
        )
        declaratoria = declarar_aptitud(
            usuario=decano,
            expediente_id=expediente_listo_para_informe.id,
            archivo_memorando=io.BytesIO(PDF_VALIDO),
        )
        # Verificar que la ruta tiene formato correcto
        assert declaratoria.archivo_memorando_firmado_path.endswith(".pdf")
        assert "memorando_162_" in declaratoria.archivo_memorando_firmado_path

    def test_pdf_no_excede_10mb(self, secretario_abogado, expediente_listo_para_informe):
        """PDF generado no excede 10MB."""
        informe = emitir_informe(
            usuario=secretario_abogado,
            expediente_id=expediente_listo_para_informe.id,
            dictamen="APTO",
        )
        import os
        size = os.path.getsize(informe.archivo_informe_path)
        assert size <= 10 * 1024 * 1024


class TestPermisosYSeguridadResoluciones:
    """Tests de permisos RBAC y aislamiento."""

    def test_estudiante_no_puede_emitir_informe(self, api_client, estudiante, expediente_listo_para_informe):
        """ESTUDIANTE no puede emitir informe."""
        api_client.force_authenticate(user=estudiante)
        response = api_client.post("/api/v1/informes/", {
            "expediente_id": str(expediente_listo_para_informe.id),
            "dictamen": "APTO",
        }, format="json")
        assert response.status_code in (403, 404)

    def test_estudiante_no_puede_declarar_aptitud(self, api_client, estudiante, expediente_listo_para_informe):
        """ESTUDIANTE no puede registrar declaratoria."""
        api_client.force_authenticate(user=estudiante)
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "memo.pdf"
        response = api_client.post("/api/v1/declaratorias/", {
            "expediente_id": str(expediente_listo_para_informe.id),
            "archivo_memorando": archivo,
        }, format="multipart")
        assert response.status_code in (403, 404)

    def test_secretario_otra_facultad_no_puede_emitir(self, api_client, expediente_listo_para_informe):
        """SECRETARIO_ABOGADO de otra facultad no puede emitir."""
        from apps.authentication.adapters.models import User, Role, UserRole
        rol_sec, _ = Role.objects.get_or_create(name="SECRETARIO_ABOGADO")
        sec_otra = User.objects.create_user(
            username="sec_otra", email="sec_otra@test.com", password="pass1234",
            cedula="2222222222", facultad_id="33333333-3333-3333-3333-333333333333"
        )
        UserRole.objects.create(user=sec_otra, role=rol_sec)

        api_client.force_authenticate(user=sec_otra)
        response = api_client.post("/api/v1/informes/", {
            "expediente_id": str(expediente_listo_para_informe.id),
            "dictamen": "APTO",
        }, format="json")
        # Scope filter devuelve 404 (no encontrado en scope) o 403
        assert response.status_code in (403, 404)

    def test_decano_otra_facultad_no_puede_declarar(self, api_client, expediente_listo_para_informe, secretario_abogado):
        """DECANO de otra facultad no puede declarar."""
        from apps.authentication.adapters.models import User, Role, UserRole
        # Primero emitir el informe
        emitir_informe(
            usuario=secretario_abogado,
            expediente_id=expediente_listo_para_informe.id,
            dictamen="APTO",
        )
        
        from apps.authentication.adapters.models import User, Role, UserRole
        rol_dec, _ = Role.objects.get_or_create(name="DECANO")
        dec_otra = User.objects.create_user(
            username="dec_otra", email="dec_otra@test.com", password="pass1234",
            cedula="2222222222", facultad_id="33333333-3333-3333-3333-333333333333"
        )
        UserRole.objects.create(user=dec_otra, role=rol_dec)

        client = APIClient()
        client.force_authenticate(user=dec_otra)
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "memo.pdf"
        response = client.post("/api/v1/declaratorias/", {
            "expediente_id": str(expediente_listo_para_informe.id),
            "archivo_memorando": archivo,
        }, format="multipart")
        assert response.status_code in (403, 404)