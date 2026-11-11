"""Pruebas INC-01 (seguridad P0): VULN-001, VULN-002 y VULN-003.

- VULN-001 / INC-01-T01: `MutantOperationThrottle` limita por usuario las
  operaciones mutantes (429) sin afectar a las lecturas.
- VULN-002 / INC-01-T02: `SCOPE_ASIGNADO` en `ScopeFilterMixin`; descarga
  aislada por dependencia emisora + ámbito; carga de la Secretaría limitada
  a peticiones asignadas a la Secretaría (403).
- VULN-003 / INC-01-T03: la descarga verifica el SHA-256 registrado y no
  sirve un archivo alterado (500 `documento_integridad_comprometida`).
"""

import io
import uuid

import pytest
from django.core.cache import cache
from rest_framework.test import APIClient

from apps.authentication.adapters.models import (
    ROLE_ESTUDIANTE,
    ROLE_SECRETARIA_CARRERA,
    ROLE_SECRETARIO_ABOGADO,
    Role,
    User,
    UserRole,
)
from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.peticiones.adapters.models import (
    ESTADO_PENDIENTE,
    CatalogoDocumental,
    PeticionDocumental,
)
from apps.peticiones.services import cargar_documento
from core.adapters.local_storage import obtener_ruta_absoluta
from core.adapters.scope_filter import ScopeFilterMixin
from core.adapters.throttling import MutantOperationThrottle

pytestmark = pytest.mark.django_db

CARRERA_1 = "11111111-1111-1111-1111-111111111111"
CARRERA_2 = "33333333-3333-3333-3333-333333333333"
FACULTAD_1 = "22222222-2222-2222-2222-222222222222"
PASSWORD = "pass1234"

PDF_VALIDO = (
    b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n"
    b"2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n"
    b"3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources"
    b"<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>\nendobj\n"
    b"4 0 obj\n<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>\nendobj\n"
    b"5 0 obj\n<</Length 44>>\nstream\nBT /F1 24 Tf 100 700 Td (Test) Tj ET\n"
    b"endstream\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n"
    b"0000000058 00000 n \n0000000115 00000 n \n0000000218 00000 n \n"
    b"0000000277 00000 n \ntrailer\n<</Size 6/Root 1 0 R>>\nstartxref\n347\n%%EOF"
)


@pytest.fixture(autouse=True)
def limpiar_cache_throttle():
    cache.clear()
    yield
    cache.clear()


def _usuario(username, rol, carrera_id=None, facultad_id=FACULTAD_1):
    user = User.objects.create_user(
        username=username,
        email=f"{username}@test.com",
        password=PASSWORD,
        cedula=f"{abs(hash(username)) % 10**10:010d}",
        carrera_id=carrera_id,
        facultad_id=facultad_id,
    )
    role, _ = Role.objects.get_or_create(name=rol)
    UserRole.objects.create(user=user, role=role)
    return user


def _cliente(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def estudiante():
    return _usuario("est_inc01", ROLE_ESTUDIANTE, carrera_id=CARRERA_1)


@pytest.fixture
def expediente(estudiante):
    return ExpedienteTitulacion.objects.create(
        numero_expediente=f"EXP-INC01-{uuid.uuid4().hex[:8]}",
        estudiante=estudiante,
        carrera_id=CARRERA_1,
        facultad_id=FACULTAD_1,
        estado=ExpedienteTitulacion.ESTADO_BORRADOR,
        activa=True,
    )


def _peticion_con_documento(expediente, estudiante, dependencia):
    requisito = CatalogoDocumental.objects.create(
        codigo_requisito=f"INC01-{uuid.uuid4().hex[:8]}",
        nombre="Requisito INC-01",
        es_obligatorio_base=True,
        fase="FASE_1",
        rol_emisor_sugerido=dependencia,
        activo=True,
    )
    peticion = PeticionDocumental.objects.create(
        expediente=expediente,
        requisito=requisito,
        estado_peticion=ESTADO_PENDIENTE,
        dependencia_emisora=dependencia,
    )
    archivo = io.BytesIO(PDF_VALIDO)
    archivo.name = "doc.pdf"
    documento = cargar_documento.execute(
        usuario=estudiante,
        peticion_id=peticion.id,
        archivo=archivo,
        nombre_original="doc.pdf",
    )
    return peticion, documento


# --- VULN-001: throttling de operaciones mutantes ---------------------------


@pytest.fixture
def tasa_baja(monkeypatch):
    monkeypatch.setattr(
        MutantOperationThrottle, "THROTTLE_RATES", {"mutante": "2/minute"}
    )


def test_throttle_mutante_429_tras_exceder_tasa(estudiante, tasa_baja):
    client = _cliente(estudiante)
    url = f"/api/v1/expedientes/{uuid.uuid4()}/enviar/"
    codigos = [client.post(url).status_code for _ in range(3)]
    # Las dos primeras pasan el throttle (404: expediente inexistente).
    assert codigos == [404, 404, 429]


def test_throttle_mutante_no_limita_lecturas(estudiante, tasa_baja):
    client = _cliente(estudiante)
    url = f"/api/v1/expedientes/{uuid.uuid4()}/"
    codigos = {client.get(url).status_code for _ in range(5)}
    assert 429 not in codigos


def test_throttle_mutante_contador_por_usuario(estudiante, tasa_baja):
    otro = _usuario("est_inc01_b", ROLE_ESTUDIANTE, carrera_id=CARRERA_1)
    url = f"/api/v1/expedientes/{uuid.uuid4()}/enviar/"
    client_a = _cliente(estudiante)
    for _ in range(2):
        client_a.post(url)
    assert client_a.post(url).status_code == 429
    assert _cliente(otro).post(url).status_code == 404


def test_throttle_mutante_aplicado_a_vistas_criticas():
    from apps.expedientes.adapters.views import ExpedienteViewSet
    from apps.peticiones.adapters.views import PeticionViewSet
    from apps.resoluciones.adapters.views import DeclaratoriaViewSet, InformeViewSet
    from apps.verificacion.adapters.views import ChecklistViewSet

    for vista in (
        ExpedienteViewSet,
        ChecklistViewSet,
        InformeViewSet,
        DeclaratoriaViewSet,
        PeticionViewSet,
    ):
        assert MutantOperationThrottle in vista.throttle_classes, vista.__name__


# --- VULN-002: SCOPE_ASIGNADO ------------------------------------------------


def test_descarga_secretaria_peticion_de_otra_dependencia_404(estudiante, expediente):
    secretaria = _usuario("sec_inc01", ROLE_SECRETARIA_CARRERA, carrera_id=CARRERA_1)
    peticion, _ = _peticion_con_documento(
        expediente, estudiante, dependencia=ROLE_SECRETARIO_ABOGADO
    )
    response = _cliente(secretaria).get(f"/api/v1/peticiones/{peticion.id}/documento/")
    assert response.status_code == 404


def test_descarga_secretaria_otra_carrera_404(estudiante, expediente):
    secretaria = _usuario("sec_inc01_c2", ROLE_SECRETARIA_CARRERA, carrera_id=CARRERA_2)
    peticion, _ = _peticion_con_documento(
        expediente, estudiante, dependencia=ROLE_SECRETARIA_CARRERA
    )
    response = _cliente(secretaria).get(f"/api/v1/peticiones/{peticion.id}/documento/")
    assert response.status_code == 404


def test_descarga_funcionario_facultad_asignado_200(estudiante, expediente):
    """Un rol de facultad (sin carrera) ve lo asignado a su rol en su facultad."""
    secretario = _usuario("jur_inc01", ROLE_SECRETARIO_ABOGADO, carrera_id=None)
    peticion, _ = _peticion_con_documento(
        expediente, estudiante, dependencia=ROLE_SECRETARIO_ABOGADO
    )
    response = _cliente(secretario).get(f"/api/v1/peticiones/{peticion.id}/documento/")
    assert response.status_code == 200


def test_carga_secretaria_peticion_de_otra_dependencia_403(estudiante, expediente):
    secretaria = _usuario("sec_inc01_up", ROLE_SECRETARIA_CARRERA, carrera_id=CARRERA_1)
    requisito = CatalogoDocumental.objects.create(
        codigo_requisito=f"INC01-UP-{uuid.uuid4().hex[:8]}",
        nombre="Requisito otra dependencia",
        es_obligatorio_base=True,
        fase="FASE_1",
        rol_emisor_sugerido=ROLE_SECRETARIO_ABOGADO,
        activo=True,
    )
    peticion = PeticionDocumental.objects.create(
        expediente=expediente,
        requisito=requisito,
        estado_peticion=ESTADO_PENDIENTE,
        dependencia_emisora=ROLE_SECRETARIO_ABOGADO,
    )
    archivo = io.BytesIO(PDF_VALIDO)
    archivo.name = "doc.pdf"
    response = _cliente(secretaria).post(
        f"/api/v1/peticiones/{peticion.id}/documento/",
        {"archivo": archivo},
        format="multipart",
    )
    assert response.status_code == 403
    assert not peticion.documentos_entregados.exists()


class _VistaAsignada(ScopeFilterMixin):
    scope_owner_field = "expediente__estudiante_id"
    scope_carrera_field = "expediente__carrera_id"
    scope_facultad_field = "expediente__facultad_id"
    scope_asignado_field = "dependencia_emisora"

    def get_scope_grants(self, user, roles):
        return {"asignado"}


class _Req:
    def __init__(self, user):
        self.user = user


def test_scope_asignado_sin_ambito_institucional_no_concede(estudiante, expediente):
    _peticion_con_documento(expediente, estudiante, dependencia=ROLE_SECRETARIA_CARRERA)
    huerfana = _usuario(
        "sec_sin_ambito", ROLE_SECRETARIA_CARRERA, carrera_id=None, facultad_id=None
    )
    qs = _VistaAsignada().scope_queryset(
        PeticionDocumental.objects.all(), _Req(huerfana)
    )
    assert qs.count() == 0


def test_scope_asignado_filtra_por_dependencia_y_carrera(estudiante, expediente):
    propia, _ = _peticion_con_documento(
        expediente, estudiante, dependencia=ROLE_SECRETARIA_CARRERA
    )
    _peticion_con_documento(expediente, estudiante, dependencia=ROLE_SECRETARIO_ABOGADO)
    secretaria = _usuario("sec_qs", ROLE_SECRETARIA_CARRERA, carrera_id=CARRERA_1)
    qs = _VistaAsignada().scope_queryset(
        PeticionDocumental.objects.all(), _Req(secretaria)
    )
    assert list(qs.values_list("id", flat=True)) == [propia.id]


# --- VULN-003: verificación SHA-256 en la descarga ---------------------------


def test_descarga_archivo_alterado_500_sin_servirlo(estudiante, expediente):
    peticion, documento = _peticion_con_documento(
        expediente, estudiante, dependencia=ROLE_SECRETARIA_CARRERA
    )
    ruta = obtener_ruta_absoluta(documento.archivo_path)
    ruta.write_bytes(PDF_VALIDO + b"\n% alterado")

    response = _cliente(estudiante).get(f"/api/v1/peticiones/{peticion.id}/documento/")
    assert response.status_code == 500
    assert response.data["detail"].code == "documento_integridad_comprometida"


def test_descarga_archivo_integro_200(estudiante, expediente):
    peticion, _ = _peticion_con_documento(
        expediente, estudiante, dependencia=ROLE_SECRETARIA_CARRERA
    )
    response = _cliente(estudiante).get(f"/api/v1/peticiones/{peticion.id}/documento/")
    assert response.status_code == 200
    assert b"".join(response.streaming_content) == PDF_VALIDO


# --- Contrato OpenAPI (SGTAutoSchema) ------------------------------------------


def test_openapi_declara_429_y_500_de_integridad():
    from drf_spectacular.generators import SchemaGenerator

    paths = SchemaGenerator().get_schema(request=None, public=True)["paths"]
    mutantes = [
        ("/api/v1/expedientes/{id}/enviar/", "post"),
        ("/api/v1/expedientes/{id}/observar/", "post"),
        ("/api/v1/checklist/{id}/", "put"),
        ("/api/v1/checklist/{id}/subsanar/", "post"),
        ("/api/v1/informes/", "post"),
        ("/api/v1/declaratorias/", "post"),
        ("/api/v1/peticiones/{id}/solicitar-emision/", "post"),
    ]
    for ruta, metodo in mutantes:
        assert "429" in paths[ruta][metodo]["responses"], (ruta, metodo)
    for ruta in (
        "/api/v1/peticiones/{id}/documento/",
        "/api/v1/peticiones/{id}/documento/{version}/",
    ):
        respuestas = paths[ruta]["get"]["responses"]
        assert "500" in respuestas and "429" not in respuestas
    assert "429" not in paths["/api/v1/expedientes/bandeja/"]["get"]["responses"]
