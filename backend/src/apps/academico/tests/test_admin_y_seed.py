"""Administración auditada del catálogo y comando `seed_mock_sga`."""

from io import StringIO

import pytest
from django.contrib.admin.sites import site
from django.core.management import CommandError, call_command
from django.test import Client

from apps.academico.adapters.management.commands.seed_mock_sga import uuid_mock
from apps.academico.adapters.models import (
    Carrera,
    EventoCatalogoAcademico,
    Facultad,
    PerfilSGASimulado,
)
from apps.academico.tests.factories import crear_carrera, crear_perfil_mock
from apps.authentication.adapters.models import Role, User, UserRole

pytestmark = pytest.mark.django_db


def _usuario(username, rol=None, **extra):
    user = User.objects.create_user(username=username, password="x", **extra)
    if rol:
        role, _ = Role.objects.get_or_create(name=rol)
        UserRole.objects.get_or_create(user=user, role=role)
    return user


@pytest.fixture
def admin_client():
    superuser = User.objects.create_superuser("adm_cat", password="x")
    client = Client()
    client.force_login(superuser)
    return client, superuser


# --- Admin ------------------------------------------------------------------


def test_modelos_registrados_en_el_admin():
    for modelo in (Facultad, Carrera, PerfilSGASimulado, EventoCatalogoAcademico):
        assert modelo in site._registry


def test_catalogo_no_se_elimina_y_bitacora_es_de_solo_lectura(rf):
    request = rf.get("/")
    request.user = User(is_superuser=True, is_staff=True)
    assert not site._registry[Carrera].has_delete_permission(request)
    assert not site._registry[Facultad].has_delete_permission(request)
    bitacora = site._registry[EventoCatalogoAcademico]
    assert not bitacora.has_add_permission(request)
    assert not bitacora.has_change_permission(request)
    assert not bitacora.has_delete_permission(request)


def test_cambio_de_perfil_desde_el_admin_queda_auditado(admin_client):
    client, superuser = admin_client
    estudiante = _usuario("adm_est", "ESTUDIANTE")
    perfil = crear_perfil_mock(estudiante)
    otra = crear_carrera("ADM-OTRA")

    respuesta = client.post(
        f"/admin/academico/perfilsgasimulado/{perfil.pk}/change/",
        {
            "identificacion": perfil.identificacion,
            "nombres": perfil.nombres,
            "apellidos": perfil.apellidos,
            "correo_institucional": perfil.correo_institucional,
            "codigo_carrera": otra.codigo,
            "codigo_facultad": otra.facultad.codigo,
            "activo": "on",
        },
    )
    assert respuesta.status_code == 302

    evento = EventoCatalogoAcademico.objects.get(
        tipo=EventoCatalogoAcademico.Tipo.MODIFICADO
    )
    assert evento.actor == superuser
    assert evento.origen == "admin"
    assert evento.objeto == "perfil_sga_simulado"
    assert evento.detalles["despues"]["codigo_carrera"] == "ADM-OTRA"
    assert "codigo_carrera" in evento.detalles["campos_modificados"]
    # Sin datos personales en la bitácora.
    assert perfil.identificacion not in str(evento.detalles)
    assert estudiante.email not in str(evento.detalles)


def test_baja_de_perfil_desde_el_admin_queda_auditada(admin_client):
    client, superuser = admin_client
    perfil = crear_perfil_mock(_usuario("adm_baja", "ESTUDIANTE"))
    respuesta = client.post(
        f"/admin/academico/perfilsgasimulado/{perfil.pk}/delete/", {"post": "yes"}
    )
    assert respuesta.status_code == 302
    assert not PerfilSGASimulado.objects.exists()
    evento = EventoCatalogoAcademico.objects.get(
        tipo=EventoCatalogoAcademico.Tipo.ELIMINADO
    )
    assert evento.objeto_id == str(perfil.pk)
    assert evento.actor == superuser


def test_admin_requiere_personal_autorizado():
    estudiante = _usuario("adm_no_staff", "ESTUDIANTE")
    client = Client()
    client.force_login(estudiante)
    respuesta = client.get("/admin/academico/carrera/")
    assert respuesta.status_code == 302
    assert "/admin/login/" in respuesta["Location"]


# --- seed_mock_sga ----------------------------------------------------------


def _seed(*args):
    salida = StringIO()
    call_command("seed_mock_sga", *args, stdout=salida)
    return salida.getvalue()


def test_seed_crea_catalogo_mock_y_perfil_del_estudiante_demo():
    estudiante = _usuario(
        "estudiante_1", "ESTUDIANTE", cedula="1100000002", email="sgtdemo.e@unl.edu.ec"
    )
    salida = _seed()

    facultad = Facultad.objects.get(codigo="MOCK-FEIRNNR")
    computacion = Carrera.objects.get(codigo="MOCK-COMPUTACION")
    inactiva = Carrera.objects.get(codigo="MOCK-CARRERA-INACTIVA")
    assert facultad.es_simulada and computacion.es_simulada and inactiva.es_simulada
    assert computacion.facultad == facultad and computacion.activa
    assert not inactiva.activa
    assert computacion.id == uuid_mock("MOCK-COMPUTACION")  # reproducible

    perfil = PerfilSGASimulado.objects.get(identificacion=estudiante.cedula)
    assert perfil.codigo_carrera == "MOCK-COMPUTACION"
    assert perfil.correo_institucional == estudiante.email
    # La salida no expone datos personales.
    assert estudiante.cedula not in salida and estudiante.email not in salida
    assert EventoCatalogoAcademico.objects.filter(origen="seed_mock_sga").count() == 4


def test_seed_es_idempotente_y_no_sobrescribe():
    estudiante = _usuario("estudiante_1", "ESTUDIANTE", cedula="1100000002")
    _seed()
    perfil = PerfilSGASimulado.objects.get(identificacion=estudiante.cedula)
    perfil.codigo_carrera = "MOCK-CARRERA-INACTIVA"
    perfil.save()
    eventos = EventoCatalogoAcademico.objects.count()

    _seed()

    perfil.refresh_from_db()
    assert perfil.codigo_carrera == "MOCK-CARRERA-INACTIVA"
    assert Carrera.objects.filter(codigo__startswith="MOCK-").count() == 2
    assert EventoCatalogoAcademico.objects.count() == eventos


def test_seed_omite_cuentas_inexistentes_sin_rol_o_sin_cedula():
    _usuario("sin_rol", cedula="1100000099")
    _usuario("sin_cedula", "ESTUDIANTE")
    _seed("--estudiantes", "no_existe", "sin_rol", "sin_cedula")
    assert not PerfilSGASimulado.objects.exists()


def test_seed_no_modifica_cuentas_sin_la_opcion_de_ambito():
    secretaria = _usuario("secretaria_carrera", "SECRETARIA_CARRERA")
    _seed()
    secretaria.refresh_from_db()
    assert secretaria.carrera_id is None and secretaria.facultad_id is None


def test_seed_asigna_ambito_solo_a_personal_sin_ambito():
    secretaria = _usuario("secretaria_carrera", "SECRETARIA_CARRERA")
    abogado = _usuario("secretario_abogado", "SECRETARIO_ABOGADO")
    otra = crear_carrera("YA-ASIGNADA")
    decano = _usuario("decano_feirnnr", "DECANO", facultad_id=otra.facultad_id)
    password_antes = secretaria.password

    _seed("--asignar-ambito-personal")

    computacion = Carrera.objects.get(codigo="MOCK-COMPUTACION")
    secretaria.refresh_from_db()
    abogado.refresh_from_db()
    decano.refresh_from_db()
    assert secretaria.carrera_id == computacion.id
    assert secretaria.facultad_id == computacion.facultad_id
    assert abogado.carrera_id is None
    assert abogado.facultad_id == computacion.facultad_id
    assert decano.facultad_id == otra.facultad_id  # no se reemplaza
    assert secretaria.password == password_antes
    assert (
        EventoCatalogoAcademico.objects.filter(
            tipo=EventoCatalogoAcademico.Tipo.AMBITO_ASIGNADO
        ).count()
        == 2
    )


def test_seed_se_niega_si_el_entorno_no_permite_el_mock(settings):
    settings.ACADEMIC_PROFILE_MOCK_ALLOWED = False
    with pytest.raises(CommandError):
        _seed()
    assert not Carrera.objects.exists()


def test_flujo_demo_extremo_a_extremo_alimenta_el_ambito_del_personal():
    """seed → perfil validado → creación sin UUID → visible por ámbito."""
    from rest_framework.test import APIClient

    estudiante = _usuario(
        "estudiante_1", "ESTUDIANTE", cedula="1100000002", email="sgtdemo.e@unl.edu.ec"
    )
    secretaria = _usuario("secretaria_carrera", "SECRETARIA_CARRERA")
    ajena = _usuario(
        "director_otra", "DIRECTOR_CARRERA", carrera_id=crear_carrera("AJENA").id
    )
    _seed("--asignar-ambito-personal")

    cliente = APIClient()
    cliente.force_authenticate(user=estudiante)
    perfil = cliente.get("/api/v1/perfil-academico/").json()
    assert perfil["puede_iniciar_tramite"] is True
    assert perfil["carrera"]["codigo"] == "MOCK-COMPUTACION"

    creado = cliente.post("/api/v1/expedientes/", {}, format="json")
    assert creado.status_code == 201
    expediente_id = creado.json()["id"]
    assert creado.json()["carrera_id"] == perfil["carrera"]["id"]

    secretaria.refresh_from_db()
    visor = APIClient()
    visor.force_authenticate(user=secretaria)
    assert visor.get(f"/api/v1/expedientes/{expediente_id}/").status_code == 200

    visor.force_authenticate(user=ajena)
    assert visor.get(f"/api/v1/expedientes/{expediente_id}/").status_code == 404
