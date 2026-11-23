"""`AcademicProfileService`: validación del perfil y selección de la fuente."""

import pytest

from apps.academico.adapters.mock_sga import MockSGAAdapter
from apps.academico.domain.perfil import EstadoPerfil, RegistroAcademicoFuente
from apps.academico.ports.fuente_academica import (
    FuenteAcademicaNoConfiguradaError,
    FuenteAcademicaNoDisponibleError,
)
from apps.academico.services.fuentes import get_fuente_academica
from apps.academico.services.perfil_academico import (
    AcademicProfileService,
    get_academic_profile_service,
)
from apps.academico.tests.factories import (
    crear_carrera,
    crear_facultad,
    crear_perfil_mock,
)
from apps.authentication.adapters.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def usuario():
    return User.objects.create_user(
        username="perfil_svc", password="x", cedula="9200000001", email="e@unl.edu.ec"
    )


def _perfil(usuario):
    return get_academic_profile_service().obtener_perfil(usuario)


def _codigos(perfil):
    return [m.codigo for m in perfil.motivos]


def test_perfil_validado_deriva_facultad_de_la_carrera(usuario):
    facultad = crear_facultad("SVC-FAC")
    carrera = crear_carrera("SVC-CAR", facultad=facultad)
    crear_perfil_mock(usuario, carrera)

    perfil = _perfil(usuario)

    assert perfil.estado == EstadoPerfil.VALIDADO
    assert perfil.validado
    assert perfil.motivos == ()
    assert perfil.carrera.id == str(carrera.id)
    assert perfil.facultad.id == str(facultad.id)
    assert perfil.estudiante.identificacion == "9200000001"
    assert perfil.fuente.codigo == "MOCK_SGA"
    assert perfil.fuente.es_simulada is True


def test_codigo_facultad_vacio_en_fuente_usa_la_de_la_carrera(usuario):
    carrera = crear_carrera()
    crear_perfil_mock(usuario, carrera, codigo_facultad="")
    perfil = _perfil(usuario)
    assert perfil.validado
    assert perfil.facultad.codigo == carrera.facultad.codigo


def test_sin_identificacion_es_incompleto():
    user = User.objects.create_user(username="sin_cedula", password="x")
    perfil = _perfil(user)
    assert perfil.estado == EstadoPerfil.INCOMPLETO
    assert _codigos(perfil) == ["identificacion_no_registrada"]


def test_sin_registro_en_fuente_no_asociado(usuario):
    perfil = _perfil(usuario)
    assert perfil.estado == EstadoPerfil.NO_ASOCIADO
    assert perfil.estudiante is None
    assert perfil.carrera is None


def test_registro_inactivo_en_fuente_no_asociado(usuario):
    crear_perfil_mock(usuario, activo=False)
    assert _perfil(usuario).estado == EstadoPerfil.NO_ASOCIADO


def test_datos_personales_incompletos(usuario):
    crear_perfil_mock(usuario, nombres="")
    perfil = _perfil(usuario)
    assert perfil.estado == EstadoPerfil.INCOMPLETO
    assert "datos_personales_incompletos" in _codigos(perfil)


def test_sin_carrera_es_incompleto(usuario):
    crear_perfil_mock(usuario, codigo_carrera="")
    perfil = _perfil(usuario)
    assert perfil.estado == EstadoPerfil.INCOMPLETO
    assert _codigos(perfil) == ["carrera_no_registrada"]


def test_carrera_no_catalogada_es_inconsistente(usuario):
    crear_perfil_mock(usuario, codigo_carrera="NO-EXISTE")
    perfil = _perfil(usuario)
    assert perfil.estado == EstadoPerfil.INCONSISTENTE
    assert _codigos(perfil) == ["carrera_no_catalogada"]


def test_facultad_que_no_corresponde_es_inconsistente(usuario):
    crear_perfil_mock(usuario, codigo_facultad="OTRA")
    perfil = _perfil(usuario)
    assert perfil.estado == EstadoPerfil.INCONSISTENTE
    assert "facultad_no_corresponde" in _codigos(perfil)


def test_correo_distinto_al_de_la_cuenta_es_inconsistente(usuario):
    crear_perfil_mock(usuario, correo_institucional="otra.persona@unl.edu.ec")
    perfil = _perfil(usuario)
    assert perfil.estado == EstadoPerfil.INCONSISTENTE
    assert "correo_no_corresponde" in _codigos(perfil)


def test_correo_se_compara_sin_mayusculas(usuario):
    crear_perfil_mock(usuario, correo_institucional="E@UNL.EDU.EC")
    assert _perfil(usuario).validado


def test_carrera_local_distinta_es_inconsistente(usuario):
    crear_perfil_mock(usuario, crear_carrera())
    otra = crear_carrera("OTRA-CAR")
    usuario.carrera_id = otra.id
    usuario.save(update_fields=["carrera_id"])
    perfil = _perfil(usuario)
    assert perfil.estado == EstadoPerfil.INCONSISTENTE
    assert "asociacion_local_inconsistente" in _codigos(perfil)


def test_carrera_local_igual_es_valida(usuario):
    carrera = crear_carrera()
    crear_perfil_mock(usuario, carrera)
    usuario.carrera_id = carrera.id
    usuario.facultad_id = carrera.facultad_id
    usuario.save(update_fields=["carrera_id", "facultad_id"])
    assert _perfil(usuario).validado


def test_carrera_inactiva(usuario):
    crear_perfil_mock(usuario, crear_carrera(activa=False))
    perfil = _perfil(usuario)
    assert perfil.estado == EstadoPerfil.CARRERA_INACTIVA
    assert _codigos(perfil) == ["carrera_inactiva"]
    assert perfil.carrera.activa is False


def test_facultad_inactiva(usuario):
    facultad = crear_facultad("FAC-INACTIVA", activa=False)
    crear_perfil_mock(usuario, crear_carrera("CAR-F-INACT", facultad=facultad))
    perfil = _perfil(usuario)
    assert perfil.estado == EstadoPerfil.CARRERA_INACTIVA
    assert "facultad_inactiva" in _codigos(perfil)


def test_gravedad_el_estado_es_el_del_motivo_mas_grave(usuario):
    crear_perfil_mock(
        usuario, crear_carrera(activa=False), nombres="", codigo_facultad="OTRA"
    )
    perfil = _perfil(usuario)
    assert perfil.estado == EstadoPerfil.INCOMPLETO
    assert set(_codigos(perfil)) == {
        "datos_personales_incompletos",
        "facultad_no_corresponde",
        "carrera_inactiva",
    }


class _FuenteQueFalla:
    codigo = "PRUEBA"
    nombre = "Fuente de prueba"
    es_simulada = True

    def consultar_por_identificacion(self, identificacion):
        raise TimeoutError("sin respuesta")


class _FuenteQueDevuelveOtraPersona(_FuenteQueFalla):
    def consultar_por_identificacion(self, identificacion):
        return RegistroAcademicoFuente(
            identificacion="9999999999",
            nombres="Otra",
            apellidos="Persona",
            correo_institucional="otra@unl.edu.ec",
            codigo_carrera="X",
            codigo_facultad="",
        )


def test_fallo_de_la_fuente_es_no_disponible(usuario):
    with pytest.raises(FuenteAcademicaNoDisponibleError):
        AcademicProfileService(_FuenteQueFalla()).obtener_perfil(usuario)


def test_fuente_que_devuelve_otra_persona_no_se_usa(usuario):
    with pytest.raises(FuenteAcademicaNoDisponibleError):
        AcademicProfileService(_FuenteQueDevuelveOtraPersona()).obtener_perfil(usuario)


def test_fuente_mock_configurada(settings):
    settings.ACADEMIC_PROFILE_PROVIDER = "mock_sga"
    settings.ACADEMIC_PROFILE_MOCK_ALLOWED = True
    assert isinstance(get_fuente_academica(), MockSGAAdapter)


@pytest.mark.parametrize("proveedor", ["", "sga", "desconocido"])
def test_sin_fuente_valida_no_configurada(settings, proveedor):
    settings.ACADEMIC_PROFILE_PROVIDER = proveedor
    with pytest.raises(FuenteAcademicaNoConfiguradaError):
        get_fuente_academica()


def test_mock_no_permitido_no_se_activa(settings):
    """Producción: aunque se configure mock_sga, sin permiso expreso no se usa."""
    settings.ACADEMIC_PROFILE_PROVIDER = "mock_sga"
    settings.ACADEMIC_PROFILE_MOCK_ALLOWED = False
    with pytest.raises(FuenteAcademicaNoConfiguradaError):
        get_fuente_academica()


def test_settings_de_produccion_no_habilitan_el_mock_por_defecto(monkeypatch):
    """Sin variables explícitas, producción no tiene fuente ni permite el mock."""
    import importlib

    monkeypatch.delenv("ACADEMIC_PROFILE_PROVIDER", raising=False)
    monkeypatch.delenv("ACADEMIC_PROFILE_MOCK_ALLOWED", raising=False)
    monkeypatch.setenv("ALLOWED_HOSTS", "test.invalid")
    monkeypatch.setenv("CSRF_TRUSTED_ORIGINS", "https://test.invalid")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://test.invalid")

    produccion = importlib.reload(importlib.import_module("config.settings.production"))
    assert produccion.ACADEMIC_PROFILE_PROVIDER == ""
    assert produccion.ACADEMIC_PROFILE_MOCK_ALLOWED is False
