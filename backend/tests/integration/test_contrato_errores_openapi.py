"""Contrato OpenAPI de los errores de dominio (PLB-E1-04 + O-2, T5).

1. El esquema generado declara, por operación, los códigos de error de
   PLB-E1-04 con los componentes `ErrorDominio`, `ErrorSimple` y
   `ErrorValidacion`; el 500 de integridad SHA-256 (INC-01) no cambia.
2. Respuestas de error **reales** de la API validan contra el esquema que el
   contrato declara para su operación y código (jsonschema).

Se ejecuta con SQLite (no requiere PostgreSQL).
"""

import itertools
import uuid
from unittest import mock

import jsonschema
import pytest
from django.core.cache import cache
from drf_spectacular.generators import SchemaGenerator
from rest_framework.test import APIClient

from apps.authentication.adapters.models import Role, User, UserRole
from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.expedientes.services import (
    crear_expediente,
    enviar_expediente,
    iniciar_verificacion,
)
from apps.peticiones.adapters.models import CatalogoDocumental, PeticionDocumental
from apps.verificacion.adapters.models import ChecklistVerification
from apps.verificacion.services import evaluar_checklist

E = ExpedienteTitulacion
CARRERA = "aaaaaaaa-c0a7-4111-8111-111111111111"
FACULTAD = "bbbbbbbb-c0a7-4111-8111-111111111111"
_CEDULAS = itertools.count(6010000001)

OPERACIONES = {
    ("/api/v1/expedientes/", "post"): {"400", "500"},
    ("/api/v1/expedientes/{id}/enviar/", "post"): {"400", "404", "422"},
    ("/api/v1/expedientes/{id}/iniciar-verificacion/", "post"): {
        "400",
        "403",
        "404",
        "500",
    },
    ("/api/v1/expedientes/{id}/observar/", "post"): {"400", "404"},
    ("/api/v1/checklist/{id}/", "put"): {"400", "404"},
    ("/api/v1/checklist/{id}/subsanar/", "post"): {"400", "404", "500"},
    ("/api/v1/peticiones/{id}/solicitar-emision/", "post"): {"400", "404", "500"},
    ("/api/v1/peticiones/{id}/documento/", "post"): {"400", "404"},
    ("/api/v1/informes/", "post"): {"400", "404", "409"},
    ("/api/v1/declaratorias/", "post"): {"400", "404"},
}


@pytest.fixture(scope="module")
def esquema():
    return SchemaGenerator().get_schema(request=None, public=True)


def _resolver(nodo, componentes):
    if isinstance(nodo, dict):
        if set(nodo) == {"$ref"}:
            nombre = nodo["$ref"].rsplit("/", 1)[-1]
            return _resolver(componentes[nombre], componentes)
        return {k: _resolver(v, componentes) for k, v in nodo.items()}
    if isinstance(nodo, list):
        return [_resolver(v, componentes) for v in nodo]
    return nodo


def _esquema_de(esquema, ruta, metodo, codigo):
    respuesta = esquema["paths"][ruta][metodo]["responses"][codigo]
    bruto = respuesta["content"]["application/json"]["schema"]
    return _resolver(bruto, esquema["components"]["schemas"])


def _valida(esquema, ruta, metodo, respuesta):
    jsonschema.validate(
        respuesta.json(),
        _esquema_de(esquema, ruta, metodo, str(respuesta.status_code)),
    )


# --- 1. Estructura del contrato ---------------------------------------------


def test_componentes_de_error(esquema):
    componentes = esquema["components"]["schemas"]
    assert componentes["ErrorDominio"]["required"] == ["detail", "code"]
    assert componentes["ErrorSimple"]["required"] == ["detail"]
    assert "additionalProperties" in componentes["ErrorValidacion"]


@pytest.mark.parametrize("operacion, codigos", sorted(OPERACIONES.items()))
def test_operaciones_declaran_sus_errores(esquema, operacion, codigos):
    ruta, metodo = operacion
    respuestas = esquema["paths"][ruta][metodo]["responses"]
    assert codigos <= set(respuestas), (operacion, sorted(respuestas))
    assert "429" in respuestas  # INC-01 sigue declarado


def test_409_o1_declarado_con_error_dominio(esquema):
    respuesta = esquema["paths"]["/api/v1/informes/"]["post"]["responses"]["409"]
    assert "regla_pendiente_o1" in respuesta["description"]
    assert "BE-11" in respuesta["description"]
    assert respuesta["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/ErrorDominio"
    }


def test_500_integridad_sha256_sin_cambios(esquema):
    for ruta in (
        "/api/v1/peticiones/{id}/documento/",
        "/api/v1/peticiones/{id}/documento/{version}/",
    ):
        respuesta = esquema["paths"][ruta]["get"]["responses"]["500"]
        assert "documento_integridad_comprometida" in respuesta["description"]
        assert respuesta["content"]["application/json"]["schema"]["required"] == [
            "detail"
        ]


# --- 2. Respuestas reales contra el contrato --------------------------------


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


@pytest.fixture
def actores(db):
    cache.clear()
    return {
        "estudiante": _usuario("ct_est", "ESTUDIANTE"),
        "jurista": _usuario("ct_jur", "SECRETARIO_ABOGADO"),
    }


@pytest.fixture
def enviado(actores):
    expediente = crear_expediente.execute(actores["estudiante"], CARRERA)
    PeticionDocumental.objects.filter(expediente=expediente).update(
        estado_peticion="CARGADO"
    )
    return enviar_expediente.execute(expediente, actor=actores["estudiante"])


@pytest.fixture
def en_verificacion(enviado, actores):
    return iniciar_verificacion.execute(enviado.pk, actor=actores["jurista"])


def test_400_y_404_de_observar_cumplen_el_contrato(esquema, enviado, actores):
    ruta = "/api/v1/expedientes/{id}/observar/"
    peticion = PeticionDocumental.objects.filter(expediente=enviado).first()
    url = f"/api/v1/expedientes/{enviado.pk}/observar/"
    client = _cliente(actores["jurista"])

    fuera = client.post(
        url, {"peticion_id": str(peticion.pk), "motivo_observacion": "x"}, format="json"
    )
    assert fuera.status_code == 400
    _valida(esquema, ruta, "post", fuera)

    inexistente = client.post(
        url, {"peticion_id": "mal-formado", "motivo_observacion": "x"}, format="json"
    )
    assert inexistente.status_code == 404
    _valida(esquema, ruta, "post", inexistente)


def test_404_fuera_de_ambito_sin_code_cumple_el_contrato(esquema, enviado):
    otro = User.objects.create_user(
        username="ct_jur_otra",
        password="x",
        cedula=f"{next(_CEDULAS):010d}",
        carrera_id=CARRERA,
        facultad_id="cccccccc-c0a7-4111-8111-111111111111",
    )
    UserRole.objects.create(
        user=otro, role=Role.objects.get_or_create(name="SECRETARIO_ABOGADO")[0]
    )
    respuesta = _cliente(otro).post(
        f"/api/v1/expedientes/{enviado.pk}/iniciar-verificacion/"
    )
    assert respuesta.status_code == 404
    _valida(
        esquema, "/api/v1/expedientes/{id}/iniciar-verificacion/", "post", respuesta
    )


def test_400_de_validacion_de_campos_cumple_el_contrato(esquema, actores):
    respuesta = _cliente(actores["estudiante"]).post(
        "/api/v1/expedientes/", {}, format="json"
    )
    assert respuesta.status_code == 400
    _valida(esquema, "/api/v1/expedientes/", "post", respuesta)


def test_409_o1_real_cumple_el_contrato(esquema, en_verificacion, actores):
    for item in ChecklistVerification.objects.filter(expediente=en_verificacion):
        evaluar_checklist.execute(actores["jurista"], item.pk, "VERIFICADO")
    E.objects.filter(pk=en_verificacion.pk).update(estado=E.ESTADO_OBSERVADA)
    respuesta = _cliente(actores["jurista"]).post(
        "/api/v1/informes/",
        {"expediente_id": str(en_verificacion.pk), "dictamen": "APTO"},
        format="json",
    )
    assert respuesta.status_code == 409
    assert respuesta.json()["code"] == "regla_pendiente_o1"
    _valida(esquema, "/api/v1/informes/", "post", respuesta)


def test_404_de_informe_cumple_el_contrato(esquema, actores):
    respuesta = _cliente(actores["jurista"]).post(
        "/api/v1/informes/",
        {"expediente_id": str(uuid.uuid4()), "dictamen": "APTO"},
        format="json",
    )
    assert respuesta.status_code == 404
    _valida(esquema, "/api/v1/informes/", "post", respuesta)


def test_500_explicitos_cumplen_el_contrato(esquema, enviado, actores):
    otro = crear_expediente.execute(_usuario("ct_est2", "ESTUDIANTE"), CARRERA)
    peticion_borrador = PeticionDocumental.objects.filter(
        expediente=otro, dependencia_emisora="SECRETARIA_CARRERA"
    ).first()
    emisor = _cliente(otro.estudiante).post(
        f"/api/v1/peticiones/{peticion_borrador.pk}/solicitar-emision/",
        {},
        format="json",
    )
    assert emisor.status_code == 500
    assert emisor.json()["code"] == "emisor_no_configurado"
    _valida(esquema, "/api/v1/peticiones/{id}/solicitar-emision/", "post", emisor)

    requisito = CatalogoDocumental.objects.filter(
        es_obligatorio_base=True, fase="FASE_1", activo=True
    ).first()
    requisito.activo = False
    requisito.save(update_fields=["activo"])
    catalogo = _cliente(actores["jurista"]).post(
        f"/api/v1/expedientes/{enviado.pk}/iniciar-verificacion/"
    )
    assert catalogo.status_code == 500
    assert catalogo.json()["code"] == "configuracion_catalogo_incompleta"
    _valida(esquema, "/api/v1/expedientes/{id}/iniciar-verificacion/", "post", catalogo)


def test_404_de_checklist_cumple_el_contrato(esquema, en_verificacion, actores):
    item = ChecklistVerification.objects.filter(expediente=en_verificacion).first()
    with mock.patch.object(
        evaluar_checklist,
        "execute",
        side_effect=evaluar_checklist.ChecklistVerificationNotFoundError("no existe"),
    ):
        respuesta = _cliente(actores["jurista"]).put(
            f"/api/v1/checklist/{item.pk}/",
            {"estado_verificacion": "VERIFICADO"},
            format="json",
        )
    assert respuesta.status_code == 404
    _valida(esquema, "/api/v1/checklist/{id}/", "put", respuesta)
