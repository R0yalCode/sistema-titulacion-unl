"""Pruebas de GET /api/v1/expedientes/mi-tramite/ (dashboard del estudiante).

Cubre: RBAC (solo ESTUDIANTE; 401 sin sesión, 403 a funcionarios),
aislamiento (siempre el trámite propio; sin parámetros que permitan pedir
otro), estudiante sin trámite, etapas y progreso según el flujo real,
requisitos sin documento con la misma regla que el envío, observaciones
pendientes sin datos de quien las registró, y movimientos reales.
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.authentication.adapters.models import Role, User, UserRole
from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.expedientes.services import crear_expediente
from apps.expedientes.services.transiciones import registrar_transicion
from apps.peticiones.adapters.models import DocumentoEntregado, PeticionDocumental
from apps.verificacion.adapters.models import ObservacionAccionable

URL = "/api/v1/expedientes/mi-tramite/"
PASSWORD = "pwd_seguro_mi_tramite"
CARRERA = "aaaaaaaa-c111-4111-8111-111111111111"
FACULTAD = "aaaaaaaa-f111-4111-8111-111111111111"
E = ExpedienteTitulacion


def crear_usuario(username, rol, **extra):
    user = User.objects.create_user(
        username=username,
        password=PASSWORD,
        carrera_id=CARRERA,
        facultad_id=FACULTAD,
        **extra,
    )
    role, _ = Role.objects.get_or_create(name=rol)
    UserRole.objects.get_or_create(user=user, role=role)
    return user


def cliente(user=None):
    client = APIClient()
    if user is not None:
        client.force_authenticate(user=user)
    return client


def peticiones(expediente):
    return list(
        PeticionDocumental.objects.filter(expediente=expediente).order_by(
            "requisito__codigo_requisito"
        )
    )


def cargar_todo(expediente, estado="CARGADO"):
    for peticion in peticiones(expediente):
        peticion.estado_peticion = estado
        peticion.save()


@pytest.fixture(name="estudiante")
def fixture_estudiante(db):
    return crear_usuario(
        "mt_estudiante", "ESTUDIANTE", first_name="Ana", last_name="Pérez",
        email="ana.perez@unl.edu.ec",
    )


@pytest.fixture(name="secretario")
def fixture_secretario(db):
    return crear_usuario("mt_secretario", "SECRETARIO_ABOGADO")


def test_sin_sesion_401(db):
    assert cliente().get(URL).status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    "rol",
    [
        "SECRETARIA_CARRERA",
        "SECRETARIO_ABOGADO",
        "ANALISTA_APOYO",
        "DECANO",
        "DIRECTOR_CARRERA",
        "RESPONSABLE_DEPENDENCIA",
        "ADMINISTRADOR",
    ],
)
def test_roles_no_estudiante_403(db, rol):
    user = crear_usuario(f"mt_{rol.lower()}", rol)
    assert cliente(user).get(URL).status_code == status.HTTP_403_FORBIDDEN


def test_solo_lectura_metodos_no_permitidos(estudiante):
    respuesta = cliente(estudiante).post(URL, {}, format="json")
    assert respuesta.status_code in (
        status.HTTP_403_FORBIDDEN,
        status.HTTP_405_METHOD_NOT_ALLOWED,
    )


def test_estudiante_sin_tramite(estudiante):
    respuesta = cliente(estudiante).get(URL)
    assert respuesta.status_code == status.HTTP_200_OK
    cuerpo = respuesta.json()
    assert cuerpo["expediente"] is None
    assert cuerpo["total_expedientes"] == 0
    assert cuerpo["estudiante"] == {
        "nombre_completo": "Ana Pérez",
        "email": "ana.perez@unl.edu.ec",
        "cedula": None,
    }


def test_borrador_etapas_progreso_y_requisitos(estudiante):
    expediente = crear_expediente.registrar_expediente(estudiante, CARRERA)
    cuerpo = cliente(estudiante).get(URL).json()["expediente"]

    assert cuerpo["id"] == str(expediente.id)
    assert cuerpo["estado"] == E.ESTADO_BORRADOR
    assert [etapa["codigo"] for etapa in cuerpo["etapas"]] == [
        "BORRADOR", "ENVIADA", "EN_VERIFICACION", "INFORME_EMITIDO", "DECLARADA_APTA",
    ]
    assert [etapa["situacion"] for etapa in cuerpo["etapas"]] == [
        "actual", "pendiente", "pendiente", "pendiente", "pendiente",
    ]
    assert cuerpo["etapas"][0]["fecha"] is not None
    assert all(etapa["fecha"] is None for etapa in cuerpo["etapas"][1:])
    assert cuerpo["progreso"] == {"etapas_completadas": 0, "etapas_totales": 5}
    assert len(cuerpo["peticiones"]) == 5
    assert len(cuerpo["requisitos_sin_documento"]) == 5
    assert cuerpo["puede_enviarse"] is False
    assert cuerpo["movimientos"][0]["tipo"] == "creacion"


def test_borrador_completo_puede_enviarse(estudiante):
    expediente = crear_expediente.registrar_expediente(estudiante, CARRERA)
    cargar_todo(expediente)
    cuerpo = cliente(estudiante).get(URL).json()["expediente"]
    assert cuerpo["requisitos_sin_documento"] == []
    assert cuerpo["puede_enviarse"] is True


def test_enviado_registra_etapa_y_movimiento(estudiante):
    expediente = crear_expediente.registrar_expediente(estudiante, CARRERA)
    cargar_todo(expediente)
    client = cliente(estudiante)
    assert client.post(f"/api/v1/expedientes/{expediente.id}/enviar/").status_code == 200

    cuerpo = client.get(URL).json()["expediente"]
    assert cuerpo["estado"] == E.ESTADO_ENVIADA
    assert [etapa["situacion"] for etapa in cuerpo["etapas"][:3]] == [
        "completada", "actual", "pendiente",
    ]
    assert cuerpo["etapas"][1]["fecha"] is not None
    assert cuerpo["progreso"]["etapas_completadas"] == 1
    assert cuerpo["fecha_limite_atencion"] is not None
    assert cuerpo["puede_enviarse"] is False
    cambio = next(m for m in cuerpo["movimientos"] if m["tipo"] == "cambio_estado")
    assert cambio["estado_anterior"] == "BORRADOR"
    assert cambio["estado_nuevo"] == "ENVIADA"
    # El historial no revela quién ejecutó la transición.
    assert "registrado_por" not in cambio


def test_observada_expone_motivo_sin_datos_del_funcionario(estudiante, secretario):
    expediente = crear_expediente.registrar_expediente(estudiante, CARRERA)
    cargar_todo(expediente)
    registrar_transicion(expediente, E.ESTADO_ENVIADA, estudiante, origen="test")
    registrar_transicion(expediente, E.ESTADO_EN_VERIFICACION, secretario, origen="test")
    registrar_transicion(expediente, E.ESTADO_OBSERVADA, secretario, origen="test")
    peticion = peticiones(expediente)[0]
    ObservacionAccionable.objects.create(
        expediente=expediente,
        peticion=peticion,
        registrada_por=secretario,
        motivo_observacion="Falta la firma del documento",
        resuelta=False,
    )
    ObservacionAccionable.objects.create(
        expediente=expediente,
        peticion=peticiones(expediente)[1],
        registrada_por=secretario,
        motivo_observacion="Observación ya resuelta",
        resuelta=True,
    )

    respuesta = cliente(estudiante).get(URL)
    texto = respuesta.content.decode()
    cuerpo = respuesta.json()["expediente"]

    assert cuerpo["estado"] == E.ESTADO_OBSERVADA
    # OBSERVADA es una pausa de la verificación: la etapa actual sigue siendo esa.
    assert cuerpo["etapas"][2]["situacion"] == "actual"
    assert cuerpo["progreso"]["etapas_completadas"] == 2
    assert len(cuerpo["observaciones_pendientes"]) == 1
    observacion = cuerpo["observaciones_pendientes"][0]
    assert observacion["motivo_observacion"] == "Falta la firma del documento"
    assert observacion["peticion_id"] == str(peticion.id)
    assert "registrada_por" not in observacion
    assert secretario.username not in texto
    assert str(secretario.id) not in texto


def test_declarada_apta_progreso_completo(estudiante, secretario):
    expediente = crear_expediente.registrar_expediente(estudiante, CARRERA)
    cargar_todo(expediente, "VERIFICADO")
    decano = crear_usuario("mt_decano", "DECANO")
    registrar_transicion(expediente, E.ESTADO_ENVIADA, estudiante, origen="test")
    registrar_transicion(expediente, E.ESTADO_EN_VERIFICACION, secretario, origen="test")
    registrar_transicion(expediente, E.ESTADO_INFORME_EMITIDO, secretario, origen="test")
    registrar_transicion(expediente, E.ESTADO_DECLARADA_APTA, decano, origen="test")

    cuerpo = cliente(estudiante).get(URL).json()["expediente"]
    assert all(etapa["situacion"] == "completada" for etapa in cuerpo["etapas"])
    assert all(etapa["fecha"] is not None for etapa in cuerpo["etapas"])
    assert cuerpo["progreso"] == {"etapas_completadas": 5, "etapas_totales": 5}


def test_documento_cargado_aparece_sin_metadatos_de_archivo(estudiante):
    expediente = crear_expediente.registrar_expediente(estudiante, CARRERA)
    peticion = peticiones(expediente)[0]
    DocumentoEntregado.objects.create(
        peticion=peticion,
        version=1,
        archivo_path="expedientes/privado/doc.pdf",
        nombre_original="cedula-ana.pdf",
        tamanio_bytes=100,
        hash_sha256="a" * 64,
        tipo_mime="application/pdf",
        subido_por=estudiante,
        es_vigente=True,
    )
    respuesta = cliente(estudiante).get(URL)
    texto = respuesta.content.decode()
    movimiento = next(
        m for m in respuesta.json()["expediente"]["movimientos"]
        if m["tipo"] == "documento_cargado"
    )
    assert movimiento["requisito_nombre"] == peticion.requisito.nombre
    assert movimiento["version"] == 1
    assert "expedientes/privado" not in texto
    assert "cedula-ana.pdf" not in texto
    assert "a" * 64 not in texto


def test_aislamiento_solo_el_tramite_propio(estudiante):
    otro = crear_usuario("mt_otro_estudiante", "ESTUDIANTE")
    ajeno = crear_expediente.registrar_expediente(otro, CARRERA)
    propio = crear_expediente.registrar_expediente(estudiante, CARRERA)

    # Ni siquiera un parámetro inyectado cambia el expediente devuelto.
    cuerpo = cliente(estudiante).get(URL, {"id": str(ajeno.id)}).json()
    assert cuerpo["expediente"]["id"] == str(propio.id)
    assert str(ajeno.id) not in str(cuerpo)
    assert cuerpo["total_expedientes"] == 1

    cuerpo_otro = cliente(otro).get(URL).json()
    assert cuerpo_otro["expediente"]["id"] == str(ajeno.id)


def test_prefiere_expediente_activo(estudiante):
    anterior = crear_expediente.registrar_expediente(estudiante, CARRERA)
    anterior.activa = False
    anterior.estado = E.ESTADO_CANCELADA
    anterior.save()
    actual = crear_expediente.registrar_expediente(estudiante, CARRERA)
    anterior.fecha_creacion = actual.fecha_creacion  # mismo instante: decide `activa`
    anterior.save(update_fields=["fecha_creacion"])

    cuerpo = cliente(estudiante).get(URL).json()
    assert cuerpo["expediente"]["id"] == str(actual.id)
    assert cuerpo["total_expedientes"] == 2


def test_cancelada_sin_progreso(estudiante):
    expediente = crear_expediente.registrar_expediente(estudiante, CARRERA)
    expediente.estado = E.ESTADO_CANCELADA
    expediente.activa = False
    expediente.save()
    cuerpo = cliente(estudiante).get(URL).json()["expediente"]
    assert cuerpo["progreso"] is None
    assert cuerpo["etapas"][0]["situacion"] == "completada"
    assert all(etapa["situacion"] == "pendiente" for etapa in cuerpo["etapas"][1:])
