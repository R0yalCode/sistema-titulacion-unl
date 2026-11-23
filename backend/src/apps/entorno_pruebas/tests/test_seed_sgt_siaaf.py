"""`seed_sgt_siaaf`: cuentas, asociaciones, perfiles, escenarios e idempotencia."""

import re
from collections import Counter

import pytest
from django.core.management import CommandError

from apps.academico.adapters.models import Carrera, PerfilSGASimulado
from apps.academico.services.perfil_academico import get_academic_profile_service
from apps.authentication.adapters.models import MfaDevice, Role, User, UserRole
from apps.entorno_pruebas import dataset
from apps.entorno_pruebas.adapters.models import RegistroDatasetSintetico
from apps.entorno_pruebas.tests.conftest import ejecutar_seed, usuarios_del_dataset
from apps.expedientes.adapters.models import ExpedienteTitulacion as E
from apps.notificaciones.adapters.models import NotificacionInterna
from apps.peticiones.adapters.models import DocumentoEntregado

pytestmark = pytest.mark.django_db

ESTADO_POR_ESCENARIO = {
    dataset.BORRADOR: E.ESTADO_BORRADOR,
    dataset.BORRADOR_CON_DOCUMENTOS: E.ESTADO_BORRADOR,
    dataset.ENVIADA: E.ESTADO_ENVIADA,
    dataset.EN_VERIFICACION: E.ESTADO_EN_VERIFICACION,
    dataset.OBSERVADA: E.ESTADO_OBSERVADA,
    dataset.SUBSANADA: E.ESTADO_EN_VERIFICACION,
    dataset.INFORME_EMITIDO: E.ESTADO_INFORME_EMITIDO,
    dataset.DECLARADA_APTA: E.ESTADO_DECLARADA_APTA,
}


def test_crea_10_cuentas_por_cada_rol_real(dataset_creado, clave_dataset):
    cuentas = usuarios_del_dataset()
    assert len(cuentas) == 80
    assert Counter(p.rol for p, _ in cuentas) == {rol: 10 for rol in dataset.ROLES}
    for persona, user in cuentas:
        assert user.get_roles() == [persona.rol]
        assert user.is_active and not user.is_staff and not user.is_superuser
        assert user.check_password(clave_dataset)
        assert user.email == f"{user.username}@{dataset.DOMINIO_CORREO}"
        assert user.cedula.startswith("99") and len(user.cedula) == 10
    assert len({u.email.lower() for _, u in cuentas}) == 80
    assert len({u.cedula for _, u in cuentas}) == 80


def test_identidades_claramente_ficticias(dataset_creado):
    for persona, user in usuarios_del_dataset():
        assert user.first_name == dataset.ETIQUETA_ROL[persona.rol]
        assert user.last_name == f"Ficticio {persona.indice:02d}"
        assert user.username.startswith("ds.")
        assert user.email.endswith("@sgt-siaaf.example")


def test_mfa_pendiente_sin_dispositivo(dataset_creado):
    ids = [u.pk for _, u in usuarios_del_dataset()]
    assert not MfaDevice.objects.filter(user_id__in=ids).exists()


def test_asociaciones_organizacionales(dataset_creado):
    carreras = {c.id: c for c in Carrera.objects.select_related("facultad")}
    for persona, user in usuarios_del_dataset():
        if persona.rol in ("ESTUDIANTE", *dataset.AMBITO_CARRERA):
            carrera = carreras[user.carrera_id]
            assert carrera.codigo == persona.carrera
            assert user.facultad_id == carrera.facultad_id  # derivada
        elif persona.rol in dataset.AMBITO_FACULTAD:
            assert user.carrera_id is None and user.facultad_id is not None
        else:  # ADMINISTRADOR
            assert user.carrera_id is None and user.facultad_id is None
    estudiantes = usuarios_del_dataset("ESTUDIANTE")
    assert len({u.carrera_id for _, u in estudiantes}) >= 4
    for rol in dataset.AMBITO_CARRERA:
        assert len({u.carrera_id for _, u in usuarios_del_dataset(rol)}) == 5


def test_catalogo_simulado_y_carrera_determina_facultad(dataset_creado):
    for datos in dataset.CARRERAS:
        carrera = Carrera.objects.get(codigo=datos.codigo)
        assert carrera.es_simulada and carrera.activa
        assert carrera.facultad.codigo == datos.facultad
        assert carrera.facultad.es_simulada


def test_perfiles_mocksga_validados(dataset_creado):
    servicio = get_academic_profile_service()
    for persona, user in usuarios_del_dataset("ESTUDIANTE"):
        perfil_sga = PerfilSGASimulado.objects.get(identificacion=user.cedula)
        assert perfil_sga.correo_institucional == user.email
        perfil = servicio.obtener_perfil(user)
        assert perfil.validado, perfil.motivos
        assert perfil.carrera.codigo == persona.carrera
        assert perfil.facultad.codigo == persona.facultad
        assert perfil.fuente.es_simulada


def test_escenarios_construidos_con_servicios(dataset_creado):
    for persona, user in usuarios_del_dataset("ESTUDIANTE"):
        expedientes = E.objects.filter(estudiante=user)
        if persona.escenario == dataset.SIN_EXPEDIENTE:
            assert not expedientes.exists()
            continue
        expediente = expedientes.get()
        assert expediente.estado == ESTADO_POR_ESCENARIO[persona.escenario]
        assert str(expediente.facultad_id) == str(user.facultad_id)
        historial = list(
            expediente.historial_estado.order_by("fecha_cambio").values_list(
                "estado_nuevo", flat=True
            )
        )
        if persona.escenario == dataset.SUBSANADA:
            assert historial[-2:] == [E.ESTADO_OBSERVADA, E.ESTADO_EN_VERIFICACION]
            assert DocumentoEntregado.objects.filter(
                peticion__expediente=expediente, version=2, es_vigente=True
            ).exists()
        if persona.escenario == dataset.DECLARADA_APTA:
            assert historial[-1] == E.ESTADO_DECLARADA_APTA
        if persona.escenario == dataset.BORRADOR_CON_DOCUMENTOS:
            assert (
                DocumentoEntregado.objects.filter(
                    peticion__expediente=expediente
                ).count()
                == 2
            )
    # Las notificaciones las generan los propios servicios.
    observada = next(
        u
        for p, u in usuarios_del_dataset("ESTUDIANTE")
        if p.escenario == dataset.OBSERVADA
    )
    assert NotificacionInterna.objects.filter(usuario_destino=observada).exists()


def test_salida_sin_contrasena_ni_cedulas(dataset_creado, clave_dataset):
    assert clave_dataset not in dataset_creado
    assert not re.search(r"99\d{8}", dataset_creado)
    listado = ejecutar_seed("--listar")
    assert clave_dataset not in listado
    assert "ds.estudiante.01@sgt-siaaf.example" in listado
    assert len(listado.strip().splitlines()) == 80


def test_idempotente_no_modifica_ni_regenera(dataset_creado, monkeypatch):
    _, user = usuarios_del_dataset("ESTUDIANTE")[0]
    MfaDevice.objects.create(user=user, secret_encrypted="cifrado", confirmed_at=None)
    antes = {
        u.pk: (u.password, u.email, u.carrera_id, u.facultad_id)
        for _, u in usuarios_del_dataset()
    }
    conteos = (
        User.objects.count(),
        UserRole.objects.count(),
        RegistroDatasetSintetico.objects.count(),
        E.objects.count(),
        DocumentoEntregado.objects.count(),
        NotificacionInterna.objects.count(),
        PerfilSGASimulado.objects.count(),
    )
    # La segunda ejecución no necesita la contraseña: no hay cuentas pendientes.
    monkeypatch.delenv("SEED_DATASET_PASSWORD")
    salida = ejecutar_seed()

    assert "creadas  0" in salida
    despues = {
        u.pk: (u.password, u.email, u.carrera_id, u.facultad_id)
        for _, u in usuarios_del_dataset()
    }
    assert despues == antes
    assert conteos == (
        User.objects.count(),
        UserRole.objects.count(),
        RegistroDatasetSintetico.objects.count(),
        E.objects.count(),
        DocumentoEntregado.objects.count(),
        NotificacionInterna.objects.count(),
        PerfilSGASimulado.objects.count(),
    )
    assert MfaDevice.objects.get(user=user).secret_encrypted == "cifrado"


def test_no_toca_cuentas_existentes_y_evita_colisiones(roles, clave_dataset):
    existente = User.objects.create_user(
        username="ds.estudiante.01",
        email=f"ds.estudiante.01@{dataset.DOMINIO_CORREO}",
        password="otra-clave-propia-123",
        cedula="9900000001",
    )
    UserRole.objects.create(user=existente, role=roles["DECANO"])
    hash_antes = existente.password

    ejecutar_seed("--sin-escenarios")

    existente.refresh_from_db()
    assert existente.password == hash_antes
    assert existente.get_roles() == ["DECANO"]
    assert existente.carrera_id is None and existente.facultad_id is None
    persona, nuevo = usuarios_del_dataset("ESTUDIANTE")[0]
    assert nuevo.pk != existente.pk
    assert nuevo.email != existente.email
    assert nuevo.email.startswith("ds.estudiante.01")
    assert nuevo.cedula != "9900000001"
    assert not RegistroDatasetSintetico.objects.filter(
        objeto_id=str(existente.pk)
    ).exists()


def test_no_crea_roles(clave_dataset, db):
    Role.objects.filter(name__in=dataset.ROLES).delete()
    Role.objects.get_or_create(name="ESTUDIANTE")
    with pytest.raises(CommandError, match="Faltan roles"):
        ejecutar_seed()
    assert Role.objects.count() == 1
    assert not RegistroDatasetSintetico.objects.filter(objeto="usuario").exists()


@pytest.mark.parametrize(
    "ajuste",
    [
        {"ACADEMIC_PROFILE_MOCK_ALLOWED": False},
        {"ACADEMIC_PROFILE_PROVIDER": ""},
        {"EMAIL_BACKEND": "django.core.mail.backends.smtp.EmailBackend"},
    ],
)
def test_aborta_fuera_de_un_entorno_local_seguro(
    roles, clave_dataset, settings, ajuste
):
    for clave, valor in ajuste.items():
        setattr(settings, clave, valor)
    with pytest.raises(CommandError):
        ejecutar_seed()
    assert not RegistroDatasetSintetico.objects.exists()


def test_aborta_con_settings_de_produccion(roles, clave_dataset, monkeypatch):
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "config.settings.production")
    with pytest.raises(CommandError, match="producción"):
        ejecutar_seed()
    assert not User.objects.filter(email__endswith=dataset.DOMINIO_CORREO).exists()


def test_exige_contrasena_y_politica(roles, monkeypatch):
    monkeypatch.delenv("SEED_DATASET_PASSWORD", raising=False)
    with pytest.raises(CommandError, match="SEED_DATASET_PASSWORD"):
        ejecutar_seed()
    monkeypatch.setenv("SEED_DATASET_PASSWORD", "123")
    with pytest.raises(CommandError, match="política"):
        ejecutar_seed()
    assert not RegistroDatasetSintetico.objects.exists()
