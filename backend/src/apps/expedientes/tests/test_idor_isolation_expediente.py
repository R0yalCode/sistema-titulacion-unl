"""Pruebas de aislamiento IDOR en GET /api/v1/expedientes/{id}/ (T018).

Fuente de requisitos: RNF-003, EX-003, CA-008.
Verifica que un usuario no puede consultar expedientes ajenos mediante
manipulacion de UUID: respuesta 403 Forbidden o 404 Not Found.
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.authentication.adapters.models import Role, User, UserRole
from apps.expedientes.adapters.models import ExpedienteTitulacion

URL_BASE = "/api/v1/expedientes/"
PASSWORD = "pwd_seguro_t018"

C1 = "aaaaaaaa-c111-4111-8111-111111111111"
C2 = "aaaaaaaa-c222-4222-8222-222222222222"
F1 = "aaaaaaaa-f111-4111-8111-111111111111"
F2 = "aaaaaaaa-f222-4222-8222-222222222222"


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


def crear_expediente(estudiante, estado="ENVIADA", carrera_id=C1, facultad_id=F1):
    return ExpedienteTitulacion.objects.create(
        numero_expediente=f"EXP-2026-{ExpedienteTitulacion.objects.count() + 1:04d}",
        estudiante=estudiante,
        carrera_id=carrera_id,
        facultad_id=facultad_id,
        estado=estado,
        activa=True,
    )


@pytest.fixture(name="dos_estudiantes")
def fixture_dos_estudiantes(db):
    """Dos estudiantes en carreras/facultades distintas."""
    est_a = crear_usuario("t018_est_a", "ESTUDIANTE", C1, F1)
    est_b = crear_usuario("t018_est_b", "ESTUDIANTE", C2, F2)
    return {"A": est_a, "B": est_b}


def test_estudiante_no_ve_expediente_ajeno_404(dos_estudiantes):
    """CA-008 / EX-003: estudiante A consulta UUID de B -> 404."""
    exp_b = crear_expediente(dos_estudiantes["B"], estado="ENVIADA", facultad_id=F2)

    resp = cliente(dos_estudiantes["A"]).get(f"{URL_BASE}{exp_b.pk}/")

    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_estudiante_ve_su_propio_expediente_200(dos_estudiantes):
    """Propietario accede a su expediente -> 200 con datos completos."""
    exp_a = crear_expediente(dos_estudiantes["A"], estado="BORRADOR")

    resp = cliente(dos_estudiantes["A"]).get(f"{URL_BASE}{exp_a.pk}/")

    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["id"] == str(exp_a.pk)
    assert data["numero_expediente"].startswith("EXP-2026-")
    assert data["estado"] == "BORRADOR"
    assert "peticiones" in data
    assert "facultad_id" in data


def test_secretaria_carrera_ve_expediente_su_carrera_200(dos_estudiantes):
    """SECRETARIA_CARRERA ve expedientes de su carrera (scope carrera)."""
    exp_a = crear_expediente(dos_estudiantes["A"], estado="ENVIADA", carrera_id=C1)
    secretaria = crear_usuario("t018_sec_c1", "SECRETARIA_CARRERA", carrera_id=C1)

    resp = cliente(secretaria).get(f"{URL_BASE}{exp_a.pk}/")

    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["id"] == str(exp_a.pk)


def test_secretaria_carrera_no_ve_expediente_otra_carrera_404(dos_estudiantes):
    """SECRETARIA_CARRERA no ve expedientes de otra carrera -> 404."""
    exp_b = crear_expediente(dos_estudiantes["B"], estado="ENVIADA", carrera_id=C2)
    secretaria = crear_usuario("t018_sec_c1", "SECRETARIA_CARRERA", carrera_id=C1)

    resp = cliente(secretaria).get(f"{URL_BASE}{exp_b.pk}/")

    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_director_carrera_mismo_comportamiento_secretaria(dos_estudiantes):
    """DIRECTOR_CARRERA tiene scope carrera identico a SECRETARIA_CARRERA."""
    exp_a = crear_expediente(dos_estudiantes["A"], estado="ENVIADA", carrera_id=C1)
    director = crear_usuario("t018_dir_c1", "DIRECTOR_CARRERA", carrera_id=C1)

    resp_ok = cliente(director).get(f"{URL_BASE}{exp_a.pk}/")
    assert resp_ok.status_code == status.HTTP_200_OK

    exp_b = crear_expediente(dos_estudiantes["B"], estado="ENVIADA", carrera_id=C2)
    resp_no = cliente(director).get(f"{URL_BASE}{exp_b.pk}/")
    assert resp_no.status_code == status.HTTP_404_NOT_FOUND


def test_secretario_abogado_ve_expediente_su_facultad_200(dos_estudiantes):
    """SECRETARIO_ABOGADO ve expedientes de su facultad (scope facultad)."""
    exp_a = crear_expediente(dos_estudiantes["A"], estado="ENVIADA", facultad_id=F1)
    abogado = crear_usuario("t018_abog_f1", "SECRETARIO_ABOGADO", facultad_id=F1)

    resp = cliente(abogado).get(f"{URL_BASE}{exp_a.pk}/")

    assert resp.status_code == status.HTTP_200_OK


def test_secretario_abogado_no_ve_expediente_otra_facultad_404(dos_estudiantes):
    """SECRETARIO_ABOGADO no ve expedientes de otra facultad -> 404."""
    exp_b = crear_expediente(dos_estudiantes["B"], estado="ENVIADA", facultad_id=F2)
    abogado = crear_usuario("t018_abog_f1", "SECRETARIO_ABOGADO", facultad_id=F1)

    resp = cliente(abogado).get(f"{URL_BASE}{exp_b.pk}/")

    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_analista_apoyo_mismo_scope_que_abogado(dos_estudiantes):
    """ANALISTA_APOYO scope facultad identico a SECRETARIO_ABOGADO (T010/FL-05)."""
    exp_a = crear_expediente(
        dos_estudiantes["A"], estado="EN_VERIFICACION", facultad_id=F1
    )
    analista = crear_usuario("t018_anal_f1", "ANALISTA_APOYO", facultad_id=F1)

    resp_ok = cliente(analista).get(f"{URL_BASE}{exp_a.pk}/")
    assert resp_ok.status_code == status.HTTP_200_OK

    exp_b = crear_expediente(
        dos_estudiantes["B"], estado="EN_VERIFICACION", facultad_id=F2
    )
    resp_no = cliente(analista).get(f"{URL_BASE}{exp_b.pk}/")
    assert resp_no.status_code == status.HTTP_404_NOT_FOUND


def test_decano_scope_facultad(dos_estudiantes):
    """DECANO scope facultad (matriz 6.2)."""
    exp_a = crear_expediente(
        dos_estudiantes["A"], estado="INFORME_EMITIDO", facultad_id=F1
    )
    decano = crear_usuario("t018_dec_f1", "DECANO", facultad_id=F1)

    resp_ok = cliente(decano).get(f"{URL_BASE}{exp_a.pk}/")
    assert resp_ok.status_code == status.HTTP_200_OK

    exp_b = crear_expediente(
        dos_estudiantes["B"], estado="INFORME_EMITIDO", facultad_id=F2
    )
    resp_no = cliente(decano).get(f"{URL_BASE}{exp_b.pk}/")
    assert resp_no.status_code == status.HTTP_404_NOT_FOUND


def test_administrador_ve_todos_los_expedientes_200(dos_estudiantes):
    """ADMINISTRADOR scope ALL (matriz 6.2) -> acceso total sin filtro."""
    exp_a = crear_expediente(dos_estudiantes["A"], estado="ENVIADA", facultad_id=F1)
    exp_b = crear_expediente(dos_estudiantes["B"], estado="ENVIADA", facultad_id=F2)
    admin = crear_usuario("t018_admin", "ADMINISTRADOR")

    resp_a = cliente(admin).get(f"{URL_BASE}{exp_a.pk}/")
    resp_b = cliente(admin).get(f"{URL_BASE}{exp_b.pk}/")

    assert resp_a.status_code == status.HTTP_200_OK
    assert resp_b.status_code == status.HTTP_200_OK


def test_responsable_dependencia_sin_acceso_403(dos_estudiantes):
    """RESPONSABLE_DEPENDENCIA sin celda GET en matriz -> 403 (RBAC denegado)."""
    exp_a = crear_expediente(dos_estudiantes["A"], estado="ENVIADA")
    responsable = crear_usuario("t018_resp", "RESPONSABLE_DEPENDENCIA", facultad_id=F1)

    resp = cliente(responsable).get(f"{URL_BASE}{exp_a.pk}/")

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_sin_autenticacion_401(db):
    """EX-001: sin token -> 401."""
    user = crear_usuario("t018_victim", "ESTUDIANTE", C1, F1)
    exp = crear_expediente(user, estado="ENVIADA")
    client = APIClient()
    resp = client.get(f"{URL_BASE}{exp.pk}/")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_detalle_incluye_peticiones_y_campos_completos(dos_estudiantes):
    """El serializador de detalle expone peticiones, facultad_id, fechas, etc."""
    exp_a = crear_expediente(dos_estudiantes["A"], estado="ENVIADA")

    resp = cliente(dos_estudiantes["A"]).get(f"{URL_BASE}{exp_a.pk}/")

    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    campos_requeridos = {
        "id",
        "numero_expediente",
        "estudiante_id",
        "carrera_id",
        "facultad_id",
        "estado",
        "activa",
        "fecha_creacion",
        "fecha_recepcion",
        "numero_providencia",
        "fecha_limite_atencion",
        "dias_laborables_acumulados",
        "peticiones",
    }
    assert set(data.keys()) >= campos_requeridos
    assert isinstance(data["peticiones"], list)
