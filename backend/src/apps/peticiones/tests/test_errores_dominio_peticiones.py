"""PLB-E1-04 (T3): errores de `peticiones` sin 500 genéricos y aislamiento de media.

Comprueba la respuesta externa (status + JSON `{"detail", "code"}`) de
`solicitar-emision` y de la carga de documentos, el 500 explícito de emisor
no configurado (D-4) con rollback, y que las pruebas escriben en un
`MEDIA_ROOT` temporal (F-04). La política SHA-256 de INC-01 no cambia.
"""

import io
import itertools
from pathlib import Path
from unittest import mock

import pytest
from django.conf import settings
from django.core.cache import cache
from rest_framework.test import APIClient

from apps.authentication.adapters.models import Role, User, UserRole
from apps.expedientes.services import crear_expediente
from apps.notificaciones.adapters.models import NotificacionInterna
from apps.peticiones.adapters.models import DocumentoEntregado, PeticionDocumental
from apps.peticiones.services import cargar_documento, solicitar_emision
from core.adapters import api_errors

pytestmark = pytest.mark.django_db

CARRERA = "aaaaaaaa-e104-4333-8333-333333333333"
FACULTAD = "bbbbbbbb-e104-4333-8333-333333333333"
_CEDULAS = itertools.count(4030000001)
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


@pytest.fixture(autouse=True)
def _limpiar_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def estudiante():
    return _usuario("e104_pet_est", "ESTUDIANTE")


@pytest.fixture
def expediente(estudiante):
    return crear_expediente.execute(estudiante, CARRERA)


def _peticion_de(expediente, dependencia):
    return PeticionDocumental.objects.filter(
        expediente=expediente, dependencia_emisora=dependencia
    ).first()


def _solicitar(client, peticion):
    return client.post(
        f"/api/v1/peticiones/{peticion.pk}/solicitar-emision/", {}, format="json"
    )


def _cargar(client, peticion):
    archivo = io.BytesIO(PDF_VALIDO)
    archivo.name = "requisito.pdf"
    return client.post(
        f"/api/v1/peticiones/{peticion.pk}/documento/",
        {"archivo": archivo},
        format="multipart",
    )


# --- solicitar-emision ------------------------------------------------------


def test_emisor_no_configurado_500_explicito_con_rollback(expediente, estudiante):
    """D-4: sin usuarios con el rol emisor (y sin el fallback de H-27, que no
    se toca) la operación responde 500 explícito y no deja efectos."""
    peticion = _peticion_de(expediente, "SECRETARIA_CARRERA")
    assert not User.objects.filter(
        role_assignments__role__name="SECRETARIA_CARRERA"
    ).exists()
    with mock.patch.object(api_errors.logger, "error") as log_error:
        respuesta = _solicitar(_cliente(estudiante), peticion)
    assert respuesta.status_code == 500
    assert respuesta.json()["code"] == "emisor_no_configurado"
    log_error.assert_called_once()
    contexto = log_error.call_args.kwargs["extra"]["contexto"]
    assert contexto["dependencia_emisora"] == "SECRETARIA_CARRERA"
    peticion.refresh_from_db()
    assert peticion.estado_peticion == "PENDIENTE"
    assert peticion.fecha_solicitud is None
    assert not NotificacionInterna.objects.filter(peticion=peticion).exists()


def test_solicitar_peticion_eliminada_en_carrera_404_con_code(expediente, estudiante):
    peticion = _peticion_de(expediente, "SECRETARIA_CARRERA")
    with mock.patch.object(
        solicitar_emision,
        "execute",
        side_effect=solicitar_emision.PeticionNoEncontradaError("no existe"),
    ):
        respuesta = _solicitar(_cliente(estudiante), peticion)
    assert respuesta.status_code == 404
    assert respuesta.json()["code"] == "peticion_no_encontrada"


def test_solicitar_estado_invalido_400_con_code(expediente, estudiante):
    peticion = _peticion_de(expediente, "SECRETARIA_CARRERA")
    PeticionDocumental.objects.filter(pk=peticion.pk).update(estado_peticion="CARGADO")
    respuesta = _solicitar(_cliente(estudiante), peticion)
    assert respuesta.status_code == 400
    assert respuesta.json()["code"] == "estado_peticion_invalido"


def test_servicio_solicitar_inexistente_lanza_error_de_dominio():
    with pytest.raises(solicitar_emision.PeticionNoEncontradaError):
        solicitar_emision.execute(
            usuario=None, peticion_id="00000000-0000-4000-8000-000000000000"
        )


# --- carga de documento -----------------------------------------------------


def test_cargar_peticion_eliminada_en_carrera_404_con_code(expediente, estudiante):
    peticion = _peticion_de(expediente, "SECRETARIA_CARRERA")
    with mock.patch.object(
        cargar_documento,
        "execute",
        side_effect=cargar_documento.PeticionNoEncontradaError("no existe"),
    ):
        respuesta = _cargar(_cliente(estudiante), peticion)
    assert respuesta.status_code == 404
    assert respuesta.json()["code"] == "peticion_no_encontrada"


def test_servicio_cargar_inexistente_lanza_error_de_dominio(estudiante):
    with pytest.raises(cargar_documento.PeticionNoEncontradaError):
        cargar_documento.execute(
            usuario=estudiante,
            peticion_id="00000000-0000-4000-8000-000000000000",
            archivo=io.BytesIO(PDF_VALIDO),
            nombre_original="x.pdf",
        )


def test_cargar_estado_invalido_400_con_code(expediente, estudiante):
    peticion = _peticion_de(expediente, "SECRETARIA_CARRERA")
    PeticionDocumental.objects.filter(pk=peticion.pk).update(
        estado_peticion="VERIFICADO"
    )
    respuesta = _cargar(_cliente(estudiante), peticion)
    assert respuesta.status_code == 400
    assert respuesta.json()["code"] == "expediente_estado_invalido"


def test_cargar_correcto_escribe_en_media_temporal(expediente, estudiante):
    peticion = _peticion_de(expediente, "SECRETARIA_CARRERA")
    respuesta = _cargar(_cliente(estudiante), peticion)
    assert respuesta.status_code == 201
    documento = DocumentoEntregado.objects.get(peticion=peticion)
    raiz = Path(settings.PRIVATE_MEDIA_ROOT)
    assert (raiz / documento.archivo_path).is_file()
    repo_media = Path(__file__).resolve().parents[3] / "media"
    assert repo_media not in raiz.parents


def test_media_root_aislado_por_prueba(tmp_path):
    assert Path(settings.MEDIA_ROOT).is_relative_to(tmp_path)
    assert Path(settings.PRIVATE_MEDIA_ROOT).is_relative_to(tmp_path)
