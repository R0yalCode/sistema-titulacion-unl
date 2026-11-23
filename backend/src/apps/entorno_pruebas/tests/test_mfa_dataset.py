"""MFA (TOTP + QR) y RBAC con las cuentas del dataset.

Qué se prueba aquí (automatizado): el algoritmo TOTP con `pyotp`, que el QR
codifica exactamente el URI `otpauth://` de cada cuenta y el flujo HTTP real
de primer ingreso y de ingresos posteriores. El escaneo con Google
Authenticator en un teléfono NO se prueba aquí: es una prueba manual.
"""

import logging
import time
from urllib.parse import parse_qs, unquote, urlparse

import pyotp
import pytest
from django.conf import settings
from django.core.cache import cache
from django.test import RequestFactory
from rest_framework.test import APIClient

from apps.authentication.adapters.models import MfaChallenge, MfaDevice
from apps.authentication.services import mfa
from apps.entorno_pruebas import dataset
from apps.entorno_pruebas.tests.conftest import usuarios_del_dataset
from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.notificaciones.adapters.models import NotificacionInterna
from apps.peticiones.adapters.models import DocumentoEntregado

pytestmark = pytest.mark.django_db

LOGIN = "/api/v1/auth/login/"
SETUP = "/api/v1/auth/mfa/setup/"
CONFIRM = "/api/v1/auth/mfa/setup/confirm/"
VERIFY = "/api/v1/auth/mfa/verify/"
RECOVERY = "/api/v1/auth/mfa/recovery/"

#: Recurso de "inicio" de cada rol tras autenticarse (código HTTP esperado).
#: RESPONSABLE_DEPENDENCIA no tiene celdas RBAC de lectura (hallazgo ya
#: documentado): autentica, pero la API le responde 403.
INICIO_POR_ROL = {
    "ESTUDIANTE": ("/api/v1/perfil-academico/", 200),
    "SECRETARIA_CARRERA": ("/api/v1/expedientes/bandeja/", 200),
    "DIRECTOR_CARRERA": ("/api/v1/expedientes/bandeja/", 200),
    "SECRETARIO_ABOGADO": ("/api/v1/expedientes/bandeja/", 200),
    "ANALISTA_APOYO": ("/api/v1/expedientes/bandeja/", 200),
    "DECANO": ("/api/v1/expedientes/bandeja/", 200),
    "RESPONSABLE_DEPENDENCIA": ("/api/v1/notificaciones/", 403),
    "ADMINISTRADOR": ("/api/v1/expedientes/bandeja/", 200),
}


@pytest.fixture(autouse=True)
def _cache_limpia():
    cache.clear()
    yield
    cache.clear()


def _secreto(user) -> str:
    return mfa.descifrar_secreto(MfaDevice.objects.get(user=user).secret_encrypted)


def _codigo(secreto: str, desfase_pasos: int = 0) -> str:
    return pyotp.TOTP(secreto).at(time.time() + desfase_pasos * mfa.TOTP_INTERVAL)


def test_las_80_cuentas_inician_el_registro_con_secretos_independientes(
    dataset_creado, clave_dataset
):
    request = RequestFactory().post(LOGIN)
    secretos = {}
    for persona, user in usuarios_del_dataset():
        resultado = mfa.iniciar_sesion(request, user.email, clave_dataset, None)
        assert resultado.status == "mfa_setup_required"
        assert resultado.tokens == {}  # sin JWT antes del segundo factor
        datos = mfa.iniciar_registro(request, resultado.challenge)

        secreto = _secreto(user)
        uri = mfa.uri_aprovisionamiento(user, secreto)
        # El QR codifica exactamente el URI otpauth de ESTA cuenta.
        assert datos["qr_svg"] == mfa.qr_svg_data_uri(uri)
        assert datos["qr_svg"].startswith("data:image/svg+xml")
        assert datos["manual_key"].replace(" ", "") == secreto
        assert datos["account"] == user.username
        assert datos["issuer"] == settings.MFA_ISSUER_NAME

        partes = urlparse(uri)
        consulta = parse_qs(partes.query)
        assert partes.scheme == "otpauth" and partes.netloc == "totp"
        assert unquote(partes.path) == f"/{settings.MFA_ISSUER_NAME}:{user.username}"
        assert consulta["secret"] == [secreto]
        assert consulta["issuer"] == [settings.MFA_ISSUER_NAME]
        # Secreto cifrado en la base de datos.
        assert secreto not in MfaDevice.objects.get(user=user).secret_encrypted
        secretos[persona.clave] = secreto

    assert len(secretos) == 80
    assert len(set(secretos.values())) == 80
    # Ninguna cuenta queda registrada solo por iniciar el proceso.
    assert not MfaDevice.objects.filter(confirmed_at__isnull=False).exists()


def test_qr_de_una_cuenta_no_sirve_para_otra(dataset_creado, clave_dataset):
    request = RequestFactory().post(LOGIN)
    (_, ana), (_, beto) = usuarios_del_dataset("ESTUDIANTE")[:2]
    reto_a = mfa.iniciar_sesion(request, ana.email, clave_dataset, None).challenge
    mfa.iniciar_registro(request, reto_a)
    reto_b = mfa.iniciar_sesion(request, beto.email, clave_dataset, None).challenge
    mfa.iniciar_registro(request, reto_b)

    with pytest.raises(mfa.CodigoInvalido):
        mfa.confirmar_registro(request, reto_b, _codigo(_secreto(ana)), False)
    assert not MfaDevice.objects.get(user=beto).confirmed_at


@pytest.mark.parametrize("rol", dataset.ROLES)
def test_flujo_http_completo_de_primer_ingreso_y_posterior(
    dataset_creado, clave_dataset, rol, caplog
):
    _, user = usuarios_del_dataset(rol)[0]
    client = APIClient()
    caplog.set_level(logging.DEBUG)

    # 1. Correo + contraseña: sin MFA configurado → registro pendiente.
    paso1 = client.post(
        LOGIN, {"email": user.email, "password": clave_dataset}, format="json"
    )
    assert paso1.status_code == 200
    assert paso1.json()["status"] == "mfa_setup_required"
    assert "access" not in paso1.json()
    reto = paso1.json()["challenge"]

    # 2. El reto no es una sesión: no abre la API.
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {reto}")
    assert client.get(INICIO_POR_ROL[rol][0]).status_code == 401
    client.credentials()

    # 3. QR / clave manual (lo que el usuario escanea o escribe en la app).
    paso2 = client.post(SETUP, {"challenge": reto}, format="json")
    assert paso2.status_code == 200
    secreto = paso2.json()["manual_key"].replace(" ", "")

    # 4. Código incorrecto: rechazado y sin tokens.
    malo = client.post(CONFIRM, {"challenge": reto, "code": "000000"}, format="json")
    assert malo.status_code == 400 and "access" not in malo.json()

    # 5. Código correcto: registro confirmado y sesión emitida.
    paso3 = client.post(
        CONFIRM, {"challenge": reto, "code": _codigo(secreto)}, format="json"
    )
    assert paso3.status_code == 200
    cuerpo = paso3.json()
    assert cuerpo["status"] == "authenticated" and cuerpo["access"]
    assert len(cuerpo["recovery_codes"]) == settings.MFA_RECOVERY_CODES_COUNT
    assert "manual_key" not in cuerpo and secreto not in str(cuerpo)

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {cuerpo['access']}")
    ruta, esperado = INICIO_POR_ROL[rol]
    assert client.get(ruta).status_code == esperado
    client.credentials()

    # 6. Ingreso posterior: pide el código (no el registro) y lo valida.
    cache.clear()
    otro = APIClient()
    login2 = otro.post(
        LOGIN, {"email": user.email, "password": clave_dataset}, format="json"
    )
    assert login2.json()["status"] == "mfa_required"
    # El mismo código ya usado se rechaza (anti-reutilización).
    reusado = otro.post(
        VERIFY,
        {"challenge": login2.json()["challenge"], "code": _codigo(secreto)},
        format="json",
    )
    assert reusado.status_code == 400
    login3 = otro.post(
        LOGIN, {"email": user.email, "password": clave_dataset}, format="json"
    )
    final = otro.post(
        VERIFY,
        {
            "challenge": login3.json()["challenge"],
            "code": _codigo(secreto, desfase_pasos=1),
        },
        format="json",
    )
    assert final.status_code == 200 and final.json()["status"] == "authenticated"

    # El secreto nunca aparece en los registros (logs).
    assert secreto not in caplog.text


def test_codigo_vencido_fuera_de_la_tolerancia(dataset_creado, clave_dataset):
    request = RequestFactory().post(LOGIN)
    _, user = usuarios_del_dataset("DECANO")[0]
    reto = mfa.iniciar_sesion(request, user.email, clave_dataset, None).challenge
    mfa.iniciar_registro(request, reto)
    device = MfaDevice.objects.get(user=user)
    secreto = _secreto(user)
    ventana = settings.MFA_TOTP_VALID_WINDOW
    vencido = _codigo(secreto, desfase_pasos=-(ventana + 2))
    assert not mfa.verificar_totp(device, vencido)
    assert mfa.verificar_totp(device, _codigo(secreto, desfase_pasos=-ventana))


def test_limite_de_intentos_del_reto(dataset_creado, clave_dataset):
    _, user = usuarios_del_dataset("SECRETARIO_ABOGADO")[0]
    client = APIClient()
    reto = client.post(
        LOGIN, {"email": user.email, "password": clave_dataset}, format="json"
    ).json()["challenge"]
    client.post(SETUP, {"challenge": reto}, format="json")
    for _ in range(settings.MFA_CHALLENGE_MAX_ATTEMPTS):
        client.post(CONFIRM, {"challenge": reto, "code": "123456"}, format="json")
    # Agotado el reto, ni siquiera el código correcto funciona.
    respuesta = client.post(
        CONFIRM, {"challenge": reto, "code": _codigo(_secreto(user))}, format="json"
    )
    assert respuesta.status_code in (400, 401, 403, 429)
    assert "access" not in respuesta.json()
    assert not MfaDevice.objects.get(user=user).confirmed_at
    assert MfaChallenge.objects.filter(user=user).exists()


def test_recuperacion_con_codigo_de_un_solo_uso(dataset_creado, clave_dataset):
    _, user = usuarios_del_dataset("ADMINISTRADOR")[0]
    client = APIClient()
    reto = client.post(
        LOGIN, {"email": user.email, "password": clave_dataset}, format="json"
    ).json()["challenge"]
    secreto = (
        client.post(SETUP, {"challenge": reto}, format="json")
        .json()["manual_key"]
        .replace(" ", "")
    )
    codigos = client.post(
        CONFIRM, {"challenge": reto, "code": _codigo(secreto)}, format="json"
    ).json()["recovery_codes"]

    for intento, esperado in ((1, 200), (2, 400)):
        cache.clear()
        reto_v = client.post(
            LOGIN, {"email": user.email, "password": clave_dataset}, format="json"
        ).json()["challenge"]
        respuesta = client.post(
            RECOVERY, {"challenge": reto_v, "recovery_code": codigos[0]}, format="json"
        )
        assert respuesta.status_code == esperado, intento


# --- RBAC e IDOR sobre los escenarios ---------------------------------------


def _cliente(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def _estudiante(escenario):
    return next(
        u for p, u in usuarios_del_dataset("ESTUDIANTE") if p.escenario == escenario
    )


def test_estudiante_solo_ve_su_expediente(dataset_creado):
    propio = _estudiante(dataset.OBSERVADA)
    ajeno = ExpedienteTitulacion.objects.get(estudiante=_estudiante(dataset.ENVIADA))
    mio = ExpedienteTitulacion.objects.get(estudiante=propio)
    client = _cliente(propio)
    assert client.get(f"/api/v1/expedientes/{mio.pk}/").status_code == 200
    assert client.get(f"/api/v1/expedientes/{ajeno.pk}/").status_code == 404


def test_personal_solo_ve_su_ambito(dataset_creado):
    expediente = ExpedienteTitulacion.objects.get(
        estudiante=_estudiante(dataset.ENVIADA)
    )
    carrera = next(
        p
        for p in dataset.personas()
        if p.rol == "ESTUDIANTE" and p.escenario == dataset.ENVIADA
    ).carrera
    for rol, campo, valor in (
        ("SECRETARIA_CARRERA", "carrera", carrera),
        ("SECRETARIO_ABOGADO", "facultad", dataset.FACULTAD_DE[carrera]),
    ):
        propios = [
            u for p, u in usuarios_del_dataset(rol) if getattr(p, campo) == valor
        ]
        ajenos = [u for p, u in usuarios_del_dataset(rol) if getattr(p, campo) != valor]
        assert (
            _cliente(propios[0])
            .get(f"/api/v1/expedientes/{expediente.pk}/")
            .status_code
            == 200
        )
        assert (
            _cliente(ajenos[0]).get(f"/api/v1/expedientes/{expediente.pk}/").status_code
            == 404
        )


def test_descarga_de_documento_solo_en_ambito(dataset_creado):
    estudiante = _estudiante(dataset.ENVIADA)
    documento = DocumentoEntregado.objects.filter(
        peticion__expediente__estudiante=estudiante, es_vigente=True
    ).first()
    url = f"/api/v1/peticiones/{documento.peticion_id}/documento/"
    respuesta = _cliente(estudiante).get(url)
    assert respuesta.status_code == 200
    assert respuesta["Content-Type"] == "application/pdf"
    assert _cliente(_estudiante(dataset.BORRADOR)).get(url).status_code in (403, 404)


def test_notificaciones_solo_propias(dataset_creado):
    estudiante = _estudiante(dataset.OBSERVADA)
    respuesta = _cliente(estudiante).get("/api/v1/notificaciones/")
    assert respuesta.status_code == 200
    datos = respuesta.json()
    items = datos["results"] if isinstance(datos, dict) else datos
    propias = NotificacionInterna.objects.filter(usuario_destino=estudiante).count()
    assert len(items) == propias > 0
