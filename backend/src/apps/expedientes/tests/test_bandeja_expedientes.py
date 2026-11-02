"""Pruebas de integracion de GET /api/v1/expedientes/bandeja/ (T017).

Fuente de requisitos: HU-005, RF-012, RNF-002, RNF-003, Principio C-005.
Criterio literal: SECRETARIO_ABOGADO retorna unicamente expedientes en
ENVIADA, EN_VERIFICACION y OBSERVADA pertenecientes a su facultad. Se
cubren los demas roles (mapa de intervencion), el aislamiento por
carrera/facultad/own, la paginacion y los casos 401/403.
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.authentication.adapters.models import Role, User, UserRole
from apps.expedientes.adapters.models import ExpedienteTitulacion

URL = "/api/v1/expedientes/bandeja/"
PASSWORD = "pwd_seguro_t017"

C1 = "aaaaaaaa-c111-4111-8111-111111111111"  # carrera 1
C2 = "aaaaaaaa-c222-4222-8222-222222222222"  # carrera 2
F1 = "aaaaaaaa-f111-4111-8111-111111111111"  # facultad 1
F2 = "aaaaaaaa-f222-4222-8222-222222222222"  # facultad 2


def crear_usuario(username, rol, carrera_id=None, facultad_id=None):
    user = User.objects.create_user(
        username=username,
        password=PASSWORD,
        carrera_id=carrera_id,
        facultad_id=facultad_id,
    )
    role, _ = Role.objects.get_or_create(name=rol)
    UserRole.objects.get_or_create(user=user, role=role)
    return user


def cliente(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def crear_expediente(
    estudiante,
    estado="ENVIADA",
    carrera_id=C1,
    facultad_id=F1,
    numero=None,
    contador=[0],
):
    contador[0] += 1
    return ExpedienteTitulacion.objects.create(
        numero_expediente=numero or f"EXP-2026-{contador[0]:04d}",
        estudiante=estudiante,
        carrera_id=carrera_id,
        facultad_id=facultad_id,
        estado=estado,
        activa=True,
    )


@pytest.fixture(name="escuela")
def fixture_escuela(db):
    """Dos estudiantes A (F1/C1) y B (F2/C2) con expedientes de prueba."""
    student_a = crear_usuario("t017_est_a", "ESTUDIANTE", C1, F1)
    student_b = crear_usuario("t017_est_b", "ESTUDIANTE", C2, F2)
    return {"A": student_a, "B": student_b}


def test_criterio_secretario_abogado_estados_y_facultad(escuela):
    """Celula literal del criterio: 3 estados y solo su facultad."""
    estados = ("ENVIADA", "EN_VERIFICACION", "OBSERVADA", "INFORME_EMITIDO")
    expedientes_a = [
        crear_expediente(escuela["A"], estado=estado) for estado in estados
    ]
    crear_expediente(escuela["B"], estado="ENVIADA", facultad_id=F2)
    abogado = crear_usuario("t017_abogado", "SECRETARIO_ABOGADO", facultad_id=F1)

    respuesta = cliente(abogado).get(URL)

    assert respuesta.status_code == status.HTTP_200_OK
    ids = [item["id"] for item in respuesta.json()["results"]]
    assert ids == [str(exp.id) for exp in expedientes_a[:3]]
    estados_json = {item["estado"] for item in respuesta.json()["results"]}
    assert estados_json == {"ENVIADA", "EN_VERIFICACION", "OBSERVADA"}


def test_estudiante_ve_sus_expedientes_accionables(escuela):
    """ESTUDIANTE: {BORRADOR, OBSERVADA} propios (own); nada ajeno."""
    borrador = crear_expediente(escuela["A"], estado="BORRADOR")
    crear_expediente(escuela["A"], estado="ENVIADA")
    crear_expediente(escuela["B"], estado="BORRADOR")

    respuesta = cliente(escuela["A"]).get(URL)

    assert respuesta.status_code == status.HTTP_200_OK
    ids = [item["id"] for item in respuesta.json()["results"]]
    assert ids == [str(borrador.id)]


def test_analista_apoyo_coincide_con_abogado(escuela):
    """FL-05: analista ve el mismo conjunto que el secretario-abogado."""
    for estado in ("ENVIADA", "OBSERVADA", "BORRADOR"):
        crear_expediente(escuela["A"], estado=estado)
    analista = crear_usuario("t017_analista", "ANALISTA_APOYO", facultad_id=F1)

    respuesta = cliente(analista).get(URL)

    assert respuesta.status_code == status.HTTP_200_OK
    estados_json = {item["estado"] for item in respuesta.json()["results"]}
    assert estados_json == {"ENVIADA", "OBSERVADA"}


def test_decano_solo_informe_emitido(escuela):
    """tasks.md ejemplo: INFORME_EMITIDO para Decanato."""
    expediente = crear_expediente(escuela["A"], estado="INFORME_EMITIDO")
    crear_expediente(escuela["A"], estado="ENVIADA")
    decano = crear_usuario("t017_decano", "DECANO", facultad_id=F1)

    respuesta = cliente(decano).get(URL)

    assert respuesta.status_code == status.HTTP_200_OK
    ids = [item["id"] for item in respuesta.json()["results"]]
    assert ids == [str(expediente.id)]


def test_administrador_solo_estados_en_curso(db, escuela):
    """ADMINISTRADOR: todos los ambitos, unicamente estados en curso."""
    estados = ("ENVIADA", "INFORME_EMITIDO", "DECLARADA_APTA", "CANCELADA")
    esperados = [crear_expediente(escuela["A"], estado=estado) for estado in estados]
    exp_b = crear_expediente(escuela["B"], estado="ENVIADA", facultad_id=F2)
    admin = crear_usuario("t017_admin", "ADMINISTRADOR")

    respuesta = cliente(admin).get(URL)
    assert respuesta.status_code == status.HTTP_200_OK
    ids = [item["id"] for item in respuesta.json()["results"]]
    estados_json = [item["estado"] for item in respuesta.json()["results"]]
    assert ids == [str(e.id) for e in esperados[:2]] + [str(exp_b.id)]
    assert estados_json == ["ENVIADA", "INFORME_EMITIDO", "ENVIADA"]
    assert str(esperados[2].id) not in ids
    assert str(esperados[3].id) not in ids


def test_secretaria_carrera_bandeja_vacia(db, escuela):
    """Mapa aprobado: sin expedientes asignados (intervencion via peticiones)."""
    crear_expediente(escuela["A"], estado="ENVIADA")
    secretaria = crear_usuario("t017_secretaria", "SECRETARIA_CARRERA", C1)
    respuesta = cliente(secretaria).get(URL)
    assert respuesta.status_code == status.HTTP_200_OK
    assert respuesta.json()["results"] == []


def test_rol_responsable_sin_concesion_403(escuela):
    """Matriz 6.2: RESPONSABLE_DEPENDENCIA no tiene celda GET -> 403."""
    crear_expediente(escuela["A"], estado="ENVIADA")
    responsable = crear_usuario(
        "t017_responsable", "RESPONSABLE_DEPENDENCIA", facultad_id=F1
    )
    respuesta = cliente(responsable).get(URL)
    assert respuesta.status_code == status.HTTP_403_FORBIDDEN


def test_sin_autenticacion_401(db):
    respuesta = APIClient().get(URL)
    assert respuesta.status_code == status.HTTP_401_UNAUTHORIZED


def test_paginacion_por_defecto_y_page_size(escuela):
    """Listado paginado: 10 por pagina por defecto, ?page_size= ajustable."""
    expedientes = [crear_expediente(escuela["A"], estado="ENVIADA") for _ in range(12)]
    admin = crear_usuario("t017_admin_pag", "ADMINISTRADOR")
    client = cliente(admin)

    primera = client.get(URL)
    cuerpo = primera.json()
    assert cuerpo["count"] == 12
    assert len(cuerpo["results"]) == 10
    assert "next" in cuerpo

    ajustada = client.get(URL, {"page": 2, "page_size": 5})
    cuerpo2 = ajustada.json()
    assert len(cuerpo2["results"]) == 5
    ids_totales = {item["id"] for item in cuerpo["results"]} | {
        item["id"] for item in cuerpo2["results"]
    }
    assert ids_totales == {str(e.id) for e in expedientes[:10]}
