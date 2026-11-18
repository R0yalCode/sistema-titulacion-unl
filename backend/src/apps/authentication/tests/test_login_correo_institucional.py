"""Acceso con correo institucional @unl.edu.ec (validación en backend)."""

import pytest
from django.core.cache import cache
from django.db import IntegrityError
from django.urls import reverse
from rest_framework.test import APIClient

from apps.authentication.adapters.models import EventoAutenticacion, User
from apps.authentication.domain.correo_institucional import (
    MENSAJE_CORREO_INVALIDO,
    es_correo_institucional,
    normalizar_correo,
)

PASSWORD = "pwd_correo_inst_2026"
EMAIL = "juan_perez@unl.edu.ec"


@pytest.fixture(autouse=True)
def _limpiar_throttle():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture(name="usuario")
def fixture_usuario(db):
    return User.objects.create_user(
        username="juan_perez", email=EMAIL, password=PASSWORD, cedula="7400000001"
    )


def _login(email, password=PASSWORD):
    return APIClient().post(
        reverse("auth-login"), {"email": email, "password": password}, format="json"
    )


@pytest.mark.parametrize(
    "valor,esperado",
    [
        ("juan_perez@unl.edu.ec", True),
        ("Juan.Perez@UNL.EDU.EC", True),
        ("juan_perez@gmail.com", False),
        ("juan_perez@hotmail.com", False),
        ("juan_perez@unl.edu", False),
        ("juan_perez@unl.edu.ec.com", False),
        ("juan_perez@mail.unl.edu.ec", False),
        ("juan_perez", False),
        ("@unl.edu.ec", False),
        ("a@b@unl.edu.ec", False),
        ("juan perez@unl.edu.ec", False),
        (".juan@unl.edu.ec", False),
        ("ju..an@unl.edu.ec", False),
    ],
)
def test_dominio_institucional(valor, esperado):
    assert es_correo_institucional(normalizar_correo(valor), "unl.edu.ec") is esperado


def test_normalizacion_espacios_y_mayusculas():
    assert normalizar_correo("  Juan_Perez@UNL.edu.EC ") == "juan_perez@unl.edu.ec"


def test_login_correcto_con_correo_institucional(usuario):
    respuesta = _login(EMAIL)
    assert respuesta.status_code == 200
    assert respuesta.json()["status"] == "mfa_setup_required"


def test_login_con_mayusculas_y_espacios_se_normaliza(usuario):
    respuesta = _login("  JUAN_PEREZ@Unl.Edu.Ec  ")
    assert respuesta.status_code == 200
    assert respuesta.json()["status"] == "mfa_setup_required"


@pytest.mark.parametrize(
    "valor",
    [
        "juan_perez@gmail.com",
        "juan_perez@hotmail.com",
        "juan_perez@unl.edu",
        "juan_perez",
    ],
)
def test_otro_dominio_rechazado_en_backend(usuario, valor):
    respuesta = _login(valor)
    assert respuesta.status_code == 400
    assert respuesta.json()["email"] == [MENSAJE_CORREO_INVALIDO]
    # No llega a consultar credenciales.
    assert not EventoAutenticacion.objects.exists()


def test_el_nombre_de_usuario_ya_no_sirve_para_ingresar(usuario):
    respuesta = APIClient().post(
        reverse("auth-login"),
        {"username": "juan_perez", "password": PASSWORD},
        format="json",
    )
    assert respuesta.status_code == 400
    assert respuesta.json()["email"] == ["El nombre de usuario es un campo requerido."]


def test_campos_vacios_con_mensajes_institucionales(db):
    respuesta = APIClient().post(
        reverse("auth-login"), {"email": "", "password": ""}, format="json"
    )
    assert respuesta.status_code == 400
    assert respuesta.json() == {
        "email": ["El nombre de usuario es un campo requerido."],
        "password": ["La contraseña es un campo requerido."],
    }


def test_contrasena_incorrecta_401_generico(usuario):
    respuesta = _login(EMAIL, password="incorrecta")
    assert respuesta.status_code == 401
    assert respuesta.json()["code"] == "credenciales_invalidas"


def test_correo_no_asociado_recibe_el_mismo_401(usuario):
    existente = _login(EMAIL, password="incorrecta").json()
    inexistente = _login("nadie_registrado@unl.edu.ec").json()
    assert inexistente == existente


def test_correo_unico_sin_distinguir_mayusculas(usuario):
    with pytest.raises(IntegrityError):
        User.objects.create_user(
            username="duplicado", email="JUAN_PEREZ@UNL.EDU.EC", password="x"
        )


def test_cuentas_sin_correo_no_chocan_entre_si(db):
    User.objects.create_user(username="sin_correo_1", password="x")
    User.objects.create_user(username="sin_correo_2", password="x")
    assert User.objects.filter(email="").count() == 2
