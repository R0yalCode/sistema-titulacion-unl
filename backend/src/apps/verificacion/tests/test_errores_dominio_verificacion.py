"""PLB-E1-04 + O-2 (T2): errores de `verificacion` sin 500 genéricos.

Respuesta externa (status + JSON `{"detail", "code"}`) de la evaluación y de
la subsanación, 500 explícito de inconsistencia de observación (D-3) y
rollback ante una transición que deja de ser válida.

Las carreras de este archivo son **simulaciones** con SQLite (se fuerza el
cambio de estado dentro de la transacción): sirven para comprobar el mapeo
HTTP y el rollback, no el bloqueo. El bloqueo real y la ausencia de
interbloqueos se prueban con PostgreSQL en
`tests/integration/test_concurrencia_postgres.py`.
"""

import io
import itertools
import uuid
from unittest import mock

import pytest
from django.core.cache import cache
from rest_framework.test import APIClient

from apps.authentication.adapters.models import Role, User, UserRole
from apps.expedientes.adapters.models import ExpedienteTitulacion, HistorialEstado
from apps.expedientes.services import (
    crear_expediente,
    enviar_expediente,
    iniciar_verificacion,
)
from apps.expedientes.services.transiciones import TransicionNoPermitidaError
from apps.peticiones.adapters.models import DocumentoEntregado, PeticionDocumental
from apps.verificacion.adapters.models import (
    ChecklistVerification,
    ObservacionAccionable,
)
from apps.verificacion.services import evaluar_checklist, subsanar_requisito
from core.adapters import api_errors

pytestmark = pytest.mark.django_db

E = ExpedienteTitulacion
CARRERA = "aaaaaaaa-e104-4222-8222-222222222222"
FACULTAD = "bbbbbbbb-e104-4222-8222-222222222222"
_CEDULAS = itertools.count(4020000001)
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
    return _usuario("e104_ver_est", "ESTUDIANTE")


@pytest.fixture
def jurista():
    return _usuario("e104_ver_jur", "SECRETARIO_ABOGADO")


@pytest.fixture
def en_verificacion(estudiante, jurista):
    expediente = crear_expediente.execute(estudiante, CARRERA)
    PeticionDocumental.objects.filter(expediente=expediente).update(
        estado_peticion="CARGADO"
    )
    enviar_expediente.execute(expediente, actor=estudiante)
    return iniciar_verificacion.execute(expediente.pk, actor=jurista)


def _item(expediente):
    return ChecklistVerification.objects.filter(expediente=expediente).first()


@pytest.fixture
def observado(en_verificacion, jurista):
    """Expediente OBSERVADA por el flujo real (evaluación OBSERVADO)."""
    item = _item(en_verificacion)
    evaluar_checklist.execute(jurista, item.pk, "OBSERVADO", "Documento ilegible")
    en_verificacion.refresh_from_db()
    item.refresh_from_db()
    return en_verificacion, item


def _evaluar(client, item, estado="VERIFICADO", motivo=None):
    datos = {"estado_verificacion": estado}
    if motivo:
        datos["motivo_observacion"] = motivo
    return client.put(f"/api/v1/checklist/{item.pk}/", datos, format="json")


def _subsanar(client, item, contenido=PDF_VALIDO):
    archivo = io.BytesIO(contenido)
    archivo.name = "subsanacion.pdf"
    return client.post(
        f"/api/v1/checklist/{item.pk}/subsanar/",
        {"archivo": archivo},
        format="multipart",
    )


# --- PUT /checklist/{id}/ ---------------------------------------------------


def test_servicio_evaluar_inexistente_lanza_error_de_dominio(jurista):
    with pytest.raises(evaluar_checklist.ChecklistVerificationNotFoundError):
        evaluar_checklist.execute(jurista, uuid.uuid4(), "VERIFICADO")


def test_evaluar_checklist_eliminado_en_carrera_404_con_code(en_verificacion, jurista):
    with mock.patch.object(
        evaluar_checklist,
        "execute",
        side_effect=evaluar_checklist.ChecklistVerificationNotFoundError("no existe"),
    ):
        respuesta = _evaluar(_cliente(jurista), _item(en_verificacion))
    assert respuesta.status_code == 404
    assert respuesta.json()["code"] == "checklist_no_encontrado"


def test_evaluar_fuera_de_verificacion_400_con_code(observado, jurista):
    expediente, _ = observado
    otro = ChecklistVerification.objects.filter(
        expediente=expediente, estado_verificacion="PENDIENTE"
    ).first()
    respuesta = _evaluar(_cliente(jurista), otro)
    assert respuesta.status_code == 400
    assert respuesta.json()["code"] == "expediente_not_in_verification"


def test_evaluar_ya_evaluado_400_con_code(en_verificacion, jurista):
    item = _item(en_verificacion)
    client = _cliente(jurista)
    assert _evaluar(client, item).status_code == 200
    respuesta = _evaluar(client, item)
    assert respuesta.status_code == 400
    assert respuesta.json()["code"] == "verification_already_done"


def test_evaluar_transicion_invalida_simulada_400_con_rollback(
    en_verificacion, jurista, monkeypatch
):
    """Simulación (SQLite): otro proceso cambia el estado justo antes de la
    transición. Debe responder 400 `transicion_invalida` sin efectos."""
    item = _item(en_verificacion)
    peticion = PeticionDocumental.objects.get(
        expediente=en_verificacion, requisito=item.requisito
    )
    real = evaluar_checklist.registrar_transicion

    def con_cambio_concurrente(expediente, nuevo, actor, **kwargs):
        ExpedienteTitulacion.objects.filter(pk=expediente.pk).update(
            estado=E.ESTADO_OBSERVADA
        )
        return real(expediente, nuevo, actor, **kwargs)

    monkeypatch.setattr(
        evaluar_checklist, "registrar_transicion", con_cambio_concurrente
    )
    respuesta = _evaluar(_cliente(jurista), item, "OBSERVADO", "Ilegible")

    assert respuesta.status_code == 400
    assert respuesta.json()["code"] == "transicion_invalida"
    item.refresh_from_db()
    peticion.refresh_from_db()
    en_verificacion.refresh_from_db()
    assert item.estado_verificacion == "PENDIENTE"
    assert peticion.estado_peticion == "CARGADO"
    assert en_verificacion.estado == E.ESTADO_EN_VERIFICACION
    assert not ObservacionAccionable.objects.filter(expediente=en_verificacion).exists()


def test_evaluar_valida_el_estado_sobre_la_fila_bloqueada(en_verificacion, jurista):
    """El estado se lee del expediente bloqueado en la misma transacción, no
    de una instancia previa: un cambio confirmado antes de la evaluación se
    respeta (antes se usaba `checklist.expediente` sin bloqueo)."""
    item = _item(en_verificacion)
    ExpedienteTitulacion.objects.filter(pk=en_verificacion.pk).update(
        estado=E.ESTADO_OBSERVADA
    )
    with pytest.raises(evaluar_checklist.ExpedienteNotInVerificationError):
        evaluar_checklist.execute(jurista, item.pk, "VERIFICADO")


# --- POST /checklist/{id}/subsanar/ -----------------------------------------


def test_servicio_subsanar_inexistente_lanza_error_especifico(estudiante):
    with pytest.raises(subsanar_requisito.ChecklistNoEncontradoError):
        subsanar_requisito.execute(
            usuario=estudiante,
            checklist_verification_id=uuid.uuid4(),
            archivo=io.BytesIO(PDF_VALIDO),
            nombre_original="x.pdf",
        )
    assert issubclass(
        subsanar_requisito.ChecklistNoEncontradoError,
        subsanar_requisito.SubsanacionNoPermitidaError,
    )


def test_subsanar_checklist_eliminado_en_carrera_404_con_code(observado, estudiante):
    _, item = observado
    with mock.patch.object(
        subsanar_requisito,
        "execute",
        side_effect=subsanar_requisito.ChecklistNoEncontradoError("no existe"),
    ):
        respuesta = _subsanar(_cliente(estudiante), item)
    assert respuesta.status_code == 404
    assert respuesta.json()["code"] == "checklist_no_encontrado"


def test_subsanar_no_permitida_400_antes_500(en_verificacion, estudiante):
    respuesta = _subsanar(_cliente(estudiante), _item(en_verificacion))
    assert respuesta.status_code == 400
    assert respuesta.json()["code"] == "subsanacion_no_permitida"


def test_subsanar_peticion_eliminada_en_carrera_404_con_code(observado, estudiante):
    _, item = observado
    with mock.patch.object(
        subsanar_requisito,
        "execute",
        side_effect=subsanar_requisito.PeticionNoEncontradaError("no existe"),
    ):
        respuesta = _subsanar(_cliente(estudiante), item)
    assert respuesta.status_code == 404
    assert respuesta.json()["code"] == "peticion_no_encontrada"


def test_subsanar_inconsistencia_observacion_500_explicito(observado, estudiante):
    """D-3: ítem y petición OBSERVADO sin observación pendiente."""
    expediente, item = observado
    ObservacionAccionable.objects.filter(expediente=expediente).update(resuelta=True)
    versiones_antes = DocumentoEntregado.objects.count()
    with mock.patch.object(api_errors.logger, "error") as log_error:
        respuesta = _subsanar(_cliente(estudiante), item)
    assert respuesta.status_code == 500
    assert respuesta.json()["code"] == "inconsistencia_observacion"
    log_error.assert_called_once()
    assert log_error.call_args.kwargs["extra"]["contexto"][
        "checklist_verification_id"
    ] == str(item.pk)
    expediente.refresh_from_db()
    assert expediente.estado == E.ESTADO_OBSERVADA
    assert DocumentoEntregado.objects.count() == versiones_antes


def test_subsanar_pdf_invalido_400_con_code(observado, estudiante):
    _, item = observado
    respuesta = _subsanar(_cliente(estudiante), item, contenido=b"no es un pdf")
    assert respuesta.status_code == 400
    assert "code" in respuesta.json()


def test_subsanar_transicion_invalida_simulada_400_con_rollback(
    observado, estudiante, monkeypatch
):
    expediente, item = observado
    historial_antes = HistorialEstado.objects.filter(expediente=expediente).count()
    versiones_antes = DocumentoEntregado.objects.count()
    monkeypatch.setattr(
        subsanar_requisito,
        "registrar_transicion",
        mock.Mock(
            side_effect=TransicionNoPermitidaError(
                "simulada", estado_anterior="X", estado_nuevo="Y"
            )
        ),
    )
    respuesta = _subsanar(_cliente(estudiante), item)
    assert respuesta.status_code == 400
    assert respuesta.json()["code"] == "transicion_invalida"
    expediente.refresh_from_db()
    item.refresh_from_db()
    assert expediente.estado == E.ESTADO_OBSERVADA
    assert item.estado_verificacion == "OBSERVADO"
    assert (
        ObservacionAccionable.objects.filter(
            expediente=expediente, resuelta=False
        ).count()
        == 1
    )
    assert DocumentoEntregado.objects.count() == versiones_antes
    assert (
        HistorialEstado.objects.filter(expediente=expediente).count() == historial_antes
    )


def test_subsanar_correcto_sigue_funcionando(observado, estudiante):
    expediente, item = observado
    respuesta = _subsanar(_cliente(estudiante), item)
    assert respuesta.status_code == 201
    expediente.refresh_from_db()
    assert expediente.estado == E.ESTADO_EN_VERIFICACION
