"""PLB-E1-04 + O-2 (T4): `resoluciones` sin 500 genéricos y sin archivos huérfanos.

- D-1 (O-1): emitir el informe desde OBSERVADA responde 409
  `regla_pendiente_o1` **antes** de generar el PDF; la regla no se decide.
- D-6: si la operación falla después de crear su archivo, se borra solo ese
  archivo; los archivos preexistentes (incluido uno con el mismo nombre base)
  y los ajenos quedan intactos (SHA-256 antes y después).
- H-28: el generador nunca sobrescribe un archivo existente.
- Invariante: sin `ATOMIC_REQUESTS`, la transacción del servicio es la
  externa en HTTP.

`MEDIA_ROOT` es temporal en cada prueba (`backend/conftest.py`).
"""

import hashlib
import importlib
import io
import itertools
import os
import uuid
from pathlib import Path
from unittest import mock

import pytest
from django.conf import settings
from django.core.cache import cache
from rest_framework.test import APIClient

from apps.authentication.adapters.models import Role, User, UserRole
from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.expedientes.services import (
    crear_expediente,
    enviar_expediente,
    iniciar_verificacion,
)
from apps.expedientes.services import transiciones
from apps.expedientes.services.transiciones import TransicionNoPermitidaError
from apps.peticiones.adapters.models import PeticionDocumental
from apps.resoluciones.adapters import pdf_generator
from apps.resoluciones.adapters.models import DeclaratoriaAptitud, InformeAptitud
from apps.resoluciones.adapters.pdf_generator import PDFGeneratorAdapter
from apps.verificacion.adapters.models import ChecklistVerification
from apps.verificacion.services import evaluar_checklist

# El paquete `resoluciones.services` reexporta funciones con el mismo nombre
# que sus módulos: se importan los módulos explícitamente.
emitir_mod = importlib.import_module("apps.resoluciones.services.emitir_informe")
declarar_mod = importlib.import_module("apps.resoluciones.services.declarar_aptitud")

pytestmark = pytest.mark.django_db

E = ExpedienteTitulacion
CARRERA = "aaaaaaaa-e104-4444-8444-444444444444"
FACULTAD = "bbbbbbbb-e104-4444-8444-444444444444"
_CEDULAS = itertools.count(4040000001)
PDF_VALIDO = (
    b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    b"2 0 obj\n<< /Type /Pages /Kids [] /Count 0 >>\nendobj\n"
    b"trailer\n<< /Root 1 0 R >>\n%%EOF\n"
)


def _usuario(username, rol):
    user = User.objects.create_user(
        username=username,
        password="x",
        cedula=f"{next(_CEDULAS):010d}",
        carrera_id=CARRERA,
        facultad_id=FACULTAD,
    )
    UserRole.objects.create(user=user, role=Role.objects.get_or_create(name=rol)[0])
    return user


def _cliente(user):
    client = APIClient()
    client.force_authenticate(user=user)
    client.raise_request_exception = False
    return client


def _sha256(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def _archivos(directorio):
    raiz = Path(directorio)
    return sorted(str(p.relative_to(raiz)) for p in raiz.rglob("*") if p.is_file())


@pytest.fixture(autouse=True)
def _limpiar_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def actores():
    return {
        "estudiante": _usuario("e104_res_est", "ESTUDIANTE"),
        "jurista": _usuario("e104_res_jur", "SECRETARIO_ABOGADO"),
        "decano": _usuario("e104_res_dec", "DECANO"),
    }


@pytest.fixture
def listo_para_informe(actores):
    """EN_VERIFICACION con los 5 requisitos VERIFICADO, por el flujo real."""
    expediente = crear_expediente.execute(actores["estudiante"], CARRERA)
    PeticionDocumental.objects.filter(expediente=expediente).update(
        estado_peticion="CARGADO"
    )
    enviar_expediente.execute(expediente, actor=actores["estudiante"])
    iniciar_verificacion.execute(expediente.pk, actor=actores["jurista"])
    for item in ChecklistVerification.objects.filter(expediente=expediente):
        evaluar_checklist.execute(actores["jurista"], item.pk, "VERIFICADO")
    expediente.refresh_from_db()
    assert expediente.estado == E.ESTADO_EN_VERIFICACION
    return expediente


@pytest.fixture
def directorio_resoluciones():
    ruta = Path(PDFGeneratorAdapter().output_dir)
    ruta.mkdir(parents=True, exist_ok=True)
    return ruta


def _emitir(client, expediente):
    return client.post(
        "/api/v1/informes/",
        {"expediente_id": str(expediente.pk), "dictamen": "APTO"},
        format="json",
    )


def _ruta_prevista(expediente, directorio):
    numero = emitir_mod._generar_numero_providencia(expediente)
    return directorio / f"providencia_590_{numero}.pdf"


# --- Invariante -------------------------------------------------------------


def test_invariante_sin_atomic_requests():
    from config.settings import base

    assert not base.DATABASES["default"].get("ATOMIC_REQUESTS", False)
    assert not settings.DATABASES["default"].get("ATOMIC_REQUESTS", False)


# --- D-1 / O-1: 409 sin PDF -------------------------------------------------


def test_o1_informe_desde_observada_409_sin_pdf_ni_cambios(
    listo_para_informe, actores, directorio_resoluciones
):
    E.objects.filter(pk=listo_para_informe.pk).update(estado=E.ESTADO_OBSERVADA)
    antes = _archivos(settings.PRIVATE_MEDIA_ROOT)

    respuesta = _emitir(_cliente(actores["jurista"]), listo_para_informe)

    assert respuesta.status_code == 409
    cuerpo = respuesta.json()
    assert cuerpo["code"] == "regla_pendiente_o1"
    assert "O-1" in cuerpo["detail"]
    assert _archivos(settings.PRIVATE_MEDIA_ROOT) == antes
    listo_para_informe.refresh_from_db()
    assert listo_para_informe.estado == E.ESTADO_OBSERVADA
    assert not InformeAptitud.objects.filter(expediente=listo_para_informe).exists()


def test_o1_no_modifica_la_tabla_de_transiciones():
    assert (E.ESTADO_OBSERVADA, E.ESTADO_INFORME_EMITIDO) not in (
        transiciones.TRANSICIONES_PERMITIDAS
    )


# --- 404 --------------------------------------------------------------------


def test_informe_expediente_inexistente_404_con_code(actores):
    respuesta = _cliente(actores["jurista"]).post(
        "/api/v1/informes/",
        {"expediente_id": str(uuid.uuid4()), "dictamen": "APTO"},
        format="json",
    )
    assert respuesta.status_code == 404
    assert respuesta.json()["code"] == "expediente_no_encontrado"


def test_servicio_informe_inexistente_es_valueerror_compatible(actores):
    with pytest.raises(emitir_mod.ExpedienteNoEncontradoError) as info:
        emitir_mod.execute(actores["jurista"], uuid.uuid4())
    assert isinstance(info.value, ValueError)


# --- D-6: rollback de archivos del informe ---------------------------------


def _fallo_en_transicion():
    return mock.patch.object(
        transiciones,
        "registrar_transicion",
        side_effect=TransicionNoPermitidaError(
            "simulada",
            estado_anterior=E.ESTADO_EN_VERIFICACION,
            estado_nuevo=E.ESTADO_INFORME_EMITIDO,
        ),
    )


def test_fallo_tras_crear_pdf_borra_solo_el_propio(
    listo_para_informe, actores, directorio_resoluciones
):
    ajeno = directorio_resoluciones / "documento_ajeno.pdf"
    ajeno.write_bytes(b"%PDF-ajeno")
    hash_ajeno = _sha256(ajeno)
    antes = _archivos(settings.PRIVATE_MEDIA_ROOT)

    with _fallo_en_transicion():
        respuesta = _emitir(_cliente(actores["jurista"]), listo_para_informe)

    assert respuesta.status_code == 400
    assert respuesta.json()["code"] == "transicion_invalida"
    assert _archivos(settings.PRIVATE_MEDIA_ROOT) == antes
    assert _sha256(ajeno) == hash_ajeno
    listo_para_informe.refresh_from_db()
    assert listo_para_informe.estado == E.ESTADO_EN_VERIFICACION
    assert not InformeAptitud.objects.filter(expediente=listo_para_informe).exists()


def test_preexistente_con_mismo_nombre_no_se_sobrescribe_ni_se_borra(
    listo_para_informe, actores, directorio_resoluciones
):
    centinela = _ruta_prevista(listo_para_informe, directorio_resoluciones)
    centinela.write_bytes(b"%PDF-centinela-preexistente")
    hash_centinela = _sha256(centinela)

    with _fallo_en_transicion():
        fallida = _emitir(_cliente(actores["jurista"]), listo_para_informe)
    assert fallida.status_code == 400
    assert _sha256(centinela) == hash_centinela
    assert _archivos(directorio_resoluciones) == [centinela.name]

    cache.clear()
    correcta = _emitir(_cliente(actores["jurista"]), listo_para_informe)
    assert correcta.status_code == 201
    assert _sha256(centinela) == hash_centinela
    informe = InformeAptitud.objects.get(expediente=listo_para_informe)
    assert Path(informe.archivo_informe_path) != centinela
    assert Path(informe.archivo_informe_path).read_bytes().startswith(b"%PDF")


def test_emision_correcta_conserva_el_pdf(listo_para_informe, actores):
    respuesta = _emitir(_cliente(actores["jurista"]), listo_para_informe)
    assert respuesta.status_code == 201
    informe = InformeAptitud.objects.get(expediente=listo_para_informe)
    assert os.path.isfile(informe.archivo_informe_path)
    listo_para_informe.refresh_from_db()
    assert listo_para_informe.estado == E.ESTADO_INFORME_EMITIDO


# --- H-28: el generador nunca sobrescribe ----------------------------------


def test_reserva_exclusiva_no_sobrescribe(tmp_path):
    existente = tmp_path / "providencia_590_X.pdf"
    existente.write_bytes(b"original")
    reservada = pdf_generator._reservar_ruta_exclusiva(str(existente))
    assert reservada != str(existente)
    assert existente.read_bytes() == b"original"
    assert os.path.isfile(reservada)


def test_fallo_al_construir_libera_la_reserva(tmp_path):
    doc = mock.Mock()
    doc.build.side_effect = RuntimeError("fallo de render")
    ruta = pdf_generator._reservar_ruta_exclusiva(str(tmp_path / "x.pdf"))
    with pytest.raises(RuntimeError):
        pdf_generator._construir_o_liberar(doc, ruta, True, flowables=[])
    assert not os.path.exists(ruta)


# --- Declaratoria -----------------------------------------------------------


@pytest.fixture
def informe_emitido(listo_para_informe, actores):
    emitir_mod.execute(actores["jurista"], listo_para_informe.pk)
    listo_para_informe.refresh_from_db()
    return listo_para_informe


def _declarar(client, expediente):
    archivo = io.BytesIO(PDF_VALIDO)
    archivo.name = "memorando.pdf"
    return client.post(
        "/api/v1/declaratorias/",
        {"expediente_id": str(expediente.pk), "archivo_memorando": archivo},
        format="multipart",
    )


def test_declaratoria_fallo_tras_guardar_borra_solo_su_memorando(
    informe_emitido, actores
):
    privada = Path(settings.PRIVATE_MEDIA_ROOT)
    ajeno = privada / "ajeno.pdf"
    ajeno.write_bytes(b"%PDF-ajeno")
    hash_ajeno = _sha256(ajeno)
    antes = _archivos(privada)

    with mock.patch.object(
        declarar_mod,
        "registrar_transicion",
        side_effect=TransicionNoPermitidaError(
            "simulada",
            estado_anterior=E.ESTADO_INFORME_EMITIDO,
            estado_nuevo=E.ESTADO_DECLARADA_APTA,
        ),
    ):
        respuesta = _declarar(_cliente(actores["decano"]), informe_emitido)

    assert respuesta.status_code == 400
    assert respuesta.json()["code"] == "transicion_invalida"
    assert _archivos(privada) == antes
    assert _sha256(ajeno) == hash_ajeno
    informe_emitido.refresh_from_db()
    assert informe_emitido.estado == E.ESTADO_INFORME_EMITIDO
    assert not DeclaratoriaAptitud.objects.filter(expediente=informe_emitido).exists()


def test_declaratoria_correcta_conserva_el_memorando(informe_emitido, actores):
    respuesta = _declarar(_cliente(actores["decano"]), informe_emitido)
    assert respuesta.status_code == 201
    declaratoria = DeclaratoriaAptitud.objects.get(expediente=informe_emitido)
    ruta = (
        Path(settings.PRIVATE_MEDIA_ROOT) / declaratoria.archivo_memorando_firmado_path
    )
    assert ruta.is_file()


def test_declaratoria_expediente_inexistente_404_con_code(actores):
    archivo = io.BytesIO(PDF_VALIDO)
    archivo.name = "memorando.pdf"
    respuesta = _cliente(actores["decano"]).post(
        "/api/v1/declaratorias/",
        {"expediente_id": str(uuid.uuid4()), "archivo_memorando": archivo},
        format="multipart",
    )
    assert respuesta.status_code == 404
    assert respuesta.json()["code"] == "expediente_no_encontrado"
