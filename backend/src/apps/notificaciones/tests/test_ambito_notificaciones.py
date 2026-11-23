"""Ámbito institucional de GET y PATCH de notificaciones.

Regresión: los roles con alcance de carrera o facultad recibían HTTP 500 porque
el filtro buscaba `carrera_id`/`facultad_id` en `NotificacionInterna`. Una
notificación es visible solo si está dirigida al usuario **y** su expediente
pertenece al ámbito que le concede alguno de sus roles.
"""

import uuid

import pytest
from rest_framework.test import APIClient

from apps.authentication.adapters.models import Role, User, UserRole
from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.notificaciones.adapters.models import NotificacionInterna

pytestmark = pytest.mark.django_db

URL_LISTA = "/api/v1/notificaciones/"

FACULTAD_A = uuid.UUID("aaaaaaaa-0000-4000-8000-000000000001")
FACULTAD_B = uuid.UUID("bbbbbbbb-0000-4000-8000-000000000001")
CARRERA_A1 = uuid.UUID("aaaaaaaa-0000-4000-8000-0000000000a1")
CARRERA_A2 = uuid.UUID("aaaaaaaa-0000-4000-8000-0000000000a2")
CARRERA_B1 = uuid.UUID("bbbbbbbb-0000-4000-8000-0000000000b1")

ROLES_CARRERA = ["SECRETARIA_CARRERA", "DIRECTOR_CARRERA"]
ROLES_FACULTAD = ["SECRETARIO_ABOGADO", "ANALISTA_APOYO", "DECANO"]
ROLES_AFECTADOS = ROLES_CARRERA + ROLES_FACULTAD

CAMPOS_CONTRATO = {
    "id",
    "expediente",
    "expediente_numero",
    "peticion",
    "peticion_requisito_nombre",
    "titulo",
    "mensaje",
    "leida",
    "fecha_creacion",
}


def crear_usuario(*roles, carrera=CARRERA_A1, facultad=FACULTAD_A):
    sufijo = uuid.uuid4().hex[:10]
    usuario = User.objects.create_user(
        username=f"u_{sufijo}",
        email=f"u_{sufijo}@unl.edu.ec",
        password="clave-de-prueba",
        carrera_id=carrera,
        facultad_id=facultad,
    )
    for rol in roles:
        UserRole.objects.create(user=usuario, role=Role.objects.get_or_create(name=rol)[0])
    return usuario


def crear_expediente(carrera=CARRERA_A1, facultad=FACULTAD_A, estudiante=None):
    return ExpedienteTitulacion.objects.create(
        numero_expediente=f"EXP-T-{uuid.uuid4().hex[:12]}",
        estudiante=estudiante
        or crear_usuario("ESTUDIANTE", carrera=carrera, facultad=facultad),
        carrera_id=carrera,
        facultad_id=facultad,
    )


def notificar(usuario, expediente=None, **campos):
    return NotificacionInterna.objects.create(
        usuario_destino=usuario,
        expediente=expediente or crear_expediente(),
        titulo=campos.pop("titulo", "Aviso"),
        mensaje="Mensaje de prueba",
        **campos,
    )


def cliente(usuario):
    api = APIClient()
    api.force_authenticate(user=usuario)
    return api


def ids_visibles(usuario, consulta=""):
    respuesta = cliente(usuario).get(f"{URL_LISTA}{consulta}")
    assert respuesta.status_code == 200
    return {item["id"] for item in respuesta.json()["results"]}


def url_marcar(notificacion_id):
    return f"{URL_LISTA}{notificacion_id}/marcar-leida/"


@pytest.mark.parametrize("rol", ROLES_AFECTADOS)
def test_rol_con_ambito_valido_consulta_sus_notificaciones(rol):
    usuario = crear_usuario(rol)
    propia = notificar(usuario)

    respuesta = cliente(usuario).get(URL_LISTA)

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert set(cuerpo) == {"results"}
    assert [item["id"] for item in cuerpo["results"]] == [str(propia.id)]
    item = cuerpo["results"][0]
    assert set(item) == CAMPOS_CONTRATO
    assert item["expediente"] == str(propia.expediente_id)
    assert item["expediente_numero"] == propia.expediente.numero_expediente
    assert item["peticion"] is None
    assert item["peticion_requisito_nombre"] is None
    assert item["leida"] is False


@pytest.mark.parametrize("rol", ROLES_AFECTADOS)
def test_no_ve_notificaciones_de_otro_usuario_en_su_mismo_ambito(rol):
    usuario = crear_usuario(rol)
    colega = crear_usuario(rol)
    ajena = notificar(colega)

    assert str(ajena.id) not in ids_visibles(usuario)


@pytest.mark.parametrize("rol", ROLES_CARRERA)
def test_rol_de_carrera_no_ve_otra_carrera_de_su_facultad(rol):
    usuario = crear_usuario(rol)
    dentro = notificar(usuario, crear_expediente(CARRERA_A1, FACULTAD_A))
    notificar(usuario, crear_expediente(CARRERA_A2, FACULTAD_A))
    notificar(usuario, crear_expediente(CARRERA_B1, FACULTAD_B))

    assert ids_visibles(usuario) == {str(dentro.id)}


@pytest.mark.parametrize("rol", ROLES_FACULTAD)
def test_rol_de_facultad_ve_su_facultad_y_no_otra(rol):
    usuario = crear_usuario(rol, carrera=None)
    misma_carrera = notificar(usuario, crear_expediente(CARRERA_A1, FACULTAD_A))
    otra_carrera = notificar(usuario, crear_expediente(CARRERA_A2, FACULTAD_A))
    notificar(usuario, crear_expediente(CARRERA_B1, FACULTAD_B))

    assert ids_visibles(usuario) == {str(misma_carrera.id), str(otra_carrera.id)}


@pytest.mark.parametrize("rol", ROLES_AFECTADOS)
def test_usuario_sin_asignaciones_no_falla_ni_ve_expedientes(rol):
    usuario = crear_usuario(rol, carrera=None, facultad=None)
    notificar(usuario)

    assert ids_visibles(usuario) == set()


@pytest.mark.parametrize("rol", ROLES_CARRERA)
def test_rol_de_carrera_solo_con_facultad_no_obtiene_ambito(rol):
    usuario = crear_usuario(rol, carrera=None, facultad=FACULTAD_A)
    notificar(usuario)

    assert ids_visibles(usuario) == set()


@pytest.mark.parametrize("rol", ROLES_FACULTAD)
def test_rol_de_facultad_solo_con_carrera_no_obtiene_ambito(rol):
    usuario = crear_usuario(rol, carrera=CARRERA_A1, facultad=None)
    notificar(usuario)

    assert ids_visibles(usuario) == set()


@pytest.mark.parametrize("rol", ROLES_AFECTADOS)
def test_expediente_sin_carrera_ni_facultad_no_produce_error(rol):
    usuario = crear_usuario(rol)
    notificar(usuario, crear_expediente(carrera=None, facultad=None))

    assert ids_visibles(usuario) == set()


def test_multiples_roles_unen_sus_ambitos_sin_duplicar():
    usuario = crear_usuario("DIRECTOR_CARRERA", "DECANO")
    misma_carrera = notificar(usuario, crear_expediente(CARRERA_A1, FACULTAD_A))
    misma_facultad = notificar(usuario, crear_expediente(CARRERA_A2, FACULTAD_A))
    notificar(usuario, crear_expediente(CARRERA_B1, FACULTAD_B))

    respuesta = cliente(usuario).get(URL_LISTA)

    ids = [item["id"] for item in respuesta.json()["results"]]
    assert sorted(ids) == sorted([str(misma_carrera.id), str(misma_facultad.id)])


def test_estudiante_con_rol_de_carrera_no_ve_avisos_de_terceros():
    """El alcance propio del estudiante es lo dirigido a su cuenta, nunca lo ajeno."""
    usuario = crear_usuario("ESTUDIANTE", "DIRECTOR_CARRERA")
    propio = notificar(usuario, crear_expediente(CARRERA_B1, FACULTAD_B, estudiante=usuario))
    de_carrera = notificar(usuario, crear_expediente(CARRERA_A1, FACULTAD_A))
    notificar(crear_usuario("DIRECTOR_CARRERA"), crear_expediente(CARRERA_A1, FACULTAD_A))

    assert ids_visibles(usuario) == {str(propio.id), str(de_carrera.id)}


def test_rol_sin_celda_rbac_junto_a_rol_valido_no_amplia_ambito():
    usuario = crear_usuario("RESPONSABLE_DEPENDENCIA", "SECRETARIA_CARRERA")
    dentro = notificar(usuario, crear_expediente(CARRERA_A1, FACULTAD_A))
    notificar(usuario, crear_expediente(CARRERA_A2, FACULTAD_A))

    assert ids_visibles(usuario) == {str(dentro.id)}


def test_estudiante_conserva_su_alcance_por_destinatario():
    estudiante = crear_usuario("ESTUDIANTE")
    propio = notificar(estudiante, crear_expediente(estudiante=estudiante))
    notificar(crear_usuario("ESTUDIANTE"), crear_expediente(estudiante=estudiante))

    assert ids_visibles(estudiante) == {str(propio.id)}


def test_administrador_ve_solo_las_dirigidas_a_su_cuenta():
    administrador = crear_usuario("ADMINISTRADOR", carrera=None, facultad=None)
    propia = notificar(administrador, crear_expediente(CARRERA_B1, FACULTAD_B))
    notificar(crear_usuario("DECANO"))

    assert ids_visibles(administrador) == {str(propia.id)}


def test_sin_autenticacion_responde_401():
    assert APIClient().get(URL_LISTA).status_code == 401


@pytest.mark.parametrize("roles", [(), ("RESPONSABLE_DEPENDENCIA",)])
def test_usuario_sin_autorizacion_responde_403(roles):
    usuario = crear_usuario(*roles)
    notificar(usuario)

    assert cliente(usuario).get(URL_LISTA).status_code == 403


@pytest.mark.parametrize("rol", ROLES_AFECTADOS)
def test_filtro_leida_respeta_el_ambito(rol):
    usuario = crear_usuario(rol)
    leida = notificar(usuario, leida=True)
    sin_leer = notificar(usuario)
    notificar(usuario, crear_expediente(CARRERA_B1, FACULTAD_B), leida=True)

    assert ids_visibles(usuario, "?leida=true") == {str(leida.id)}
    assert ids_visibles(usuario, "?leida=false") == {str(sin_leer.id)}


@pytest.mark.parametrize("rol", ROLES_AFECTADOS)
def test_marcar_leida_dentro_del_ambito(rol):
    usuario = crear_usuario(rol)
    notificacion = notificar(usuario)

    respuesta = cliente(usuario).patch(url_marcar(notificacion.id))

    assert respuesta.status_code == 200
    assert set(respuesta.json()) == CAMPOS_CONTRATO
    assert respuesta.json()["leida"] is True
    notificacion.refresh_from_db()
    assert notificacion.leida is True


@pytest.mark.parametrize("rol", ROLES_AFECTADOS)
def test_idor_marcar_leida_de_otro_usuario_responde_404(rol):
    usuario = crear_usuario(rol)
    ajena = notificar(crear_usuario(rol))

    respuesta = cliente(usuario).patch(url_marcar(ajena.id))

    assert respuesta.status_code == 404
    ajena.refresh_from_db()
    assert ajena.leida is False


@pytest.mark.parametrize("rol", ROLES_AFECTADOS)
def test_marcar_leida_fuera_del_ambito_responde_404(rol):
    usuario = crear_usuario(rol)
    fuera = notificar(usuario, crear_expediente(CARRERA_B1, FACULTAD_B))

    respuesta = cliente(usuario).patch(url_marcar(fuera.id))

    assert respuesta.status_code == 404
    fuera.refresh_from_db()
    assert fuera.leida is False


@pytest.mark.parametrize("rol", ROLES_AFECTADOS)
def test_identificador_inexistente_responde_404(rol):
    usuario = crear_usuario(rol)

    assert cliente(usuario).patch(url_marcar(uuid.uuid4())).status_code == 404
