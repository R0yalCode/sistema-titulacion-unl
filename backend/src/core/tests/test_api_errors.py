"""Pruebas de `core.adapters.api_errors` (PLB-E1-04, T1a).

Comprueban la **respuesta externa** (status + JSON `{"detail","code"}`)
tal como la renderiza DRF sin manejador global (D-5), y el registro técnico
de los 500 explícitos.
"""

import json
from unittest import mock

import pytest
from rest_framework.renderers import JSONRenderer
from rest_framework.views import exception_handler

from core.adapters import api_errors
from core.adapters.api_errors import (
    ConfiguracionInconsistenteAPI,
    InconsistenciaDatosAPI,
    RecursoNoEncontradoAPI,
    ReglaPendienteAPI,
    RequisitosIncompletosAPI,
    SolicitudInvalidaAPI,
    TransicionInvalidaAPI,
)


def _renderizar(exc):
    respuesta = exception_handler(exc, {})
    return respuesta.status_code, json.loads(JSONRenderer().render(respuesta.data))


@pytest.mark.parametrize(
    "clase, status, codigo",
    [
        (SolicitudInvalidaAPI, 400, "solicitud_invalida"),
        (TransicionInvalidaAPI, 400, "transicion_invalida"),
        (RecursoNoEncontradoAPI, 404, "recurso_no_encontrado"),
        (ReglaPendienteAPI, 409, "regla_pendiente"),
        (RequisitosIncompletosAPI, 422, "requisitos_incompletos"),
        (ConfiguracionInconsistenteAPI, 500, "configuracion_inconsistente"),
        (InconsistenciaDatosAPI, 500, "inconsistencia_datos"),
    ],
)
def test_cuerpo_json_por_defecto(clase, status, codigo):
    estado, cuerpo = _renderizar(clase("Mensaje de prueba."))
    assert estado == status
    assert cuerpo == {"detail": "Mensaje de prueba.", "code": codigo}


def test_codigo_explicito_sustituye_al_por_defecto():
    estado, cuerpo = _renderizar(
        ReglaPendienteAPI("Pendiente de O-1.", code="regla_pendiente_o1")
    )
    assert estado == 409
    assert cuerpo == {"detail": "Pendiente de O-1.", "code": "regla_pendiente_o1"}


def test_mensaje_por_defecto():
    _, cuerpo = _renderizar(TransicionInvalidaAPI())
    assert cuerpo == {
        "detail": "Transición de estado no permitida.",
        "code": "transicion_invalida",
    }


def test_compatibilidad_errordetail_code():
    """Las pruebas previas leían `response.data["detail"].code`: sigue valiendo."""
    respuesta = exception_handler(TransicionInvalidaAPI("x"), {})
    assert respuesta.data["detail"].code == "transicion_invalida"


def test_500_explicito_registra_codigo_y_contexto_tecnico():
    with mock.patch.object(api_errors.logger, "error") as log_error:
        exc = ConfiguracionInconsistenteAPI(
            "Catálogo incompleto.",
            code="configuracion_catalogo_incompleta",
            contexto={"operacion": "crear_expediente"},
        )
    log_error.assert_called_once()
    extra = log_error.call_args.kwargs["extra"]
    assert extra == {
        "codigo_error": "configuracion_catalogo_incompleta",
        "contexto": {"operacion": "crear_expediente"},
    }
    assert exc.status_code == 500


def test_errores_4xx_no_registran_error_tecnico():
    with mock.patch.object(api_errors.logger, "error") as log_error:
        SolicitudInvalidaAPI("x")
        RecursoNoEncontradoAPI("x")
        ReglaPendienteAPI("x")
    log_error.assert_not_called()
