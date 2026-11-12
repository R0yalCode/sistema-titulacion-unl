"""Escenarios de concurrencia C1–C8 con PostgreSQL real (PLB-E1-04 + O-2, T5).

Método común a todos los escenarios:

1. Dos hilos, cada uno con **su propia conexión** de Django y transacciones
   reales (`django_db(transaction=True)`).
2. El hilo A se **retiene** en un punto conocido de su transacción (con sus
   bloqueos ya adquiridos) mediante un `threading.Event`.
3. Se lanza el hilo B y se confirma, sondeando `pg_stat_activity` desde otra
   conexión, que B está **realmente esperando un bloqueo** (no se presupone).
4. Se libera A y se esperan ambos hilos con límite de tiempo.

Se verifican las respuestas HTTP y su `code`, el estado final, el historial,
la auditoría, el checklist, las observaciones, los documentos y los archivos,
y que ninguna respuesta sea un 500 (interbloqueo 40P01 o espera agotada
55P03 terminarían como error 500 sin capturar).

Evidencia de H-29 (antes de T2): C1 terminó en `deadlock detected` (40P01).
"""

import hashlib
import importlib
import io
import itertools
import threading
import time
from pathlib import Path

import pytest
from django.conf import settings
from django.core.cache import cache
from django.db import connection, connections
from rest_framework.test import APIClient

from apps.authentication.adapters.models import Role, User, UserRole
from apps.expedientes.adapters.models import ExpedienteTitulacion, HistorialEstado
from apps.expedientes.services import (
    crear_expediente,
    enviar_expediente,
    iniciar_verificacion,
)
from apps.expedientes.services import transiciones
from apps.notificaciones.adapters.models import EventoAuditoria, NotificacionInterna
from apps.peticiones.adapters.models import DocumentoEntregado, PeticionDocumental
from apps.resoluciones.adapters.models import DeclaratoriaAptitud, InformeAptitud
from apps.resoluciones.adapters.pdf_generator import PDFGeneratorAdapter
from apps.verificacion.adapters.models import (
    ChecklistVerification,
    ObservacionAccionable,
)
from apps.verificacion.services import evaluar_checklist

pytestmark = [
    pytest.mark.postgres,
    pytest.mark.django_db(transaction=True, serialized_rollback=True),
]

E = ExpedienteTitulacion
CARRERA = "aaaaaaaa-c0c0-4111-8111-111111111111"
FACULTAD = "bbbbbbbb-c0c0-4111-8111-111111111111"
_CEDULAS = itertools.count(5010000001)
ESPERA_MAX = 20
PDF_VALIDO = (
    b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    b"2 0 obj\n<< /Type /Pages /Kids [] /Count 0 >>\nendobj\n"
    b"trailer\n<< /Root 1 0 R >>\n%%EOF\n"
)

subsanar_mod = importlib.import_module("apps.verificacion.services.subsanar_requisito")
observar_mod = importlib.import_module(
    "apps.verificacion.services.registrar_observacion"
)
iniciar_mod = importlib.import_module("apps.expedientes.services.iniciar_verificacion")
declarar_mod = importlib.import_module("apps.resoluciones.services.declarar_aptitud")
solicitar_mod = importlib.import_module("apps.peticiones.services.solicitar_emision")
emitir_mod = importlib.import_module("apps.resoluciones.services.emitir_informe")


# --- utilidades -------------------------------------------------------------


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


def _sha256(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def _esperando_bloqueo(timeout=ESPERA_MAX):
    """True cuando otra sesión de esta base espera un bloqueo de fila."""
    limite = time.monotonic() + timeout
    while time.monotonic() < limite:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT count(*) FROM pg_stat_activity "
                "WHERE datname = current_database() AND wait_event_type = 'Lock' "
                "AND pid <> pg_backend_pid()"
            )
            if cursor.fetchone()[0] > 0:
                return True
        time.sleep(0.05)
    return False


class Retencion:
    """Retiene la primera llamada a `modulo.nombre` hasta `liberar()`.

    Las llamadas siguientes pasan directamente: solo el hilo A queda
    retenido, con los bloqueos que ya haya adquirido en su transacción.
    """

    def __init__(self, monkeypatch, modulo, nombre):
        self.retenido = threading.Event()
        self._continuar = threading.Event()
        self._primera = threading.Lock()
        real = getattr(modulo, nombre)

        def envoltura(*args, **kwargs):
            if self._primera.acquire(blocking=False):
                self.retenido.set()
                assert self._continuar.wait(ESPERA_MAX)
            return real(*args, **kwargs)

        monkeypatch.setattr(modulo, nombre, envoltura)

    def liberar(self):
        self._continuar.set()


def _carrera(retencion, accion_a, accion_b):
    """Ejecuta A (retenido) y B (que debe quedar esperando un bloqueo)."""
    resultados = {}

    def hilo(clave, accion):
        def objetivo():
            try:
                resultados[clave] = accion()
            except Exception as error:  # se registra, no se oculta
                resultados[clave] = error
            finally:
                connections.close_all()

        return threading.Thread(target=objetivo)

    hilo_a, hilo_b = hilo("a", accion_a), hilo("b", accion_b)
    hilo_a.start()
    assert retencion.retenido.wait(ESPERA_MAX), "A no llegó al punto de retención"
    hilo_b.start()
    bloqueado = _esperando_bloqueo()
    retencion.liberar()
    hilo_a.join(ESPERA_MAX)
    hilo_b.join(ESPERA_MAX)
    assert not hilo_a.is_alive() and not hilo_b.is_alive(), "hilo colgado"
    assert bloqueado, "B no llegó a esperar un bloqueo: el escenario no es concurrente"
    for clave in ("a", "b"):
        respuesta = resultados[clave]
        assert not isinstance(respuesta, Exception), repr(respuesta)
        assert respuesta.status_code != 500, (clave, respuesta.content)
    return resultados["a"], resultados["b"]


def _transiciones(expediente, anterior, nuevo):
    return HistorialEstado.objects.filter(
        expediente=expediente, estado_anterior=anterior, estado_nuevo=nuevo
    )


def _eventos(expediente, nuevo):
    return EventoAuditoria.objects.filter(
        expediente=expediente,
        accion=EventoAuditoria.Accion.ESTADO_CAMBIADO,
        detalles__estado_nuevo=nuevo,
    )


def _archivos(directorio):
    raiz = Path(directorio)
    return sorted(str(p.relative_to(raiz)) for p in raiz.rglob("*") if p.is_file())


# --- fixtures ---------------------------------------------------------------


@pytest.fixture(autouse=True)
def _cache_limpia():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def actores():
    return {
        "estudiante": _usuario("c_est", "ESTUDIANTE"),
        "jurista": _usuario("c_jur", "SECRETARIO_ABOGADO"),
        "jurista2": _usuario("c_jur2", "SECRETARIO_ABOGADO"),
        "decano": _usuario("c_dec", "DECANO"),
        "decano2": _usuario("c_dec2", "DECANO"),
        "secretaria": _usuario("c_sec", "SECRETARIA_CARRERA"),
    }


@pytest.fixture
def borrador(actores):
    return crear_expediente.execute(actores["estudiante"], CARRERA)


@pytest.fixture
def enviado(borrador, actores):
    PeticionDocumental.objects.filter(expediente=borrador).update(
        estado_peticion="CARGADO"
    )
    return enviar_expediente.execute(borrador, actor=actores["estudiante"])


@pytest.fixture
def en_verificacion(enviado, actores):
    return iniciar_verificacion.execute(enviado.pk, actor=actores["jurista"])


@pytest.fixture
def observado(en_verificacion, actores):
    item = ChecklistVerification.objects.filter(expediente=en_verificacion).first()
    evaluar_checklist.execute(actores["jurista"], item.pk, "OBSERVADO", "Ilegible")
    en_verificacion.refresh_from_db()
    item.refresh_from_db()
    return en_verificacion, item


@pytest.fixture
def listo_para_informe(en_verificacion, actores):
    for item in ChecklistVerification.objects.filter(expediente=en_verificacion):
        evaluar_checklist.execute(actores["jurista"], item.pk, "VERIFICADO")
    en_verificacion.refresh_from_db()
    return en_verificacion


def _peticion_de(expediente, item):
    return PeticionDocumental.objects.get(
        expediente=expediente, requisito=item.requisito
    )


def _put_checklist(user, item, estado, motivo=None):
    datos = {"estado_verificacion": estado}
    if motivo:
        datos["motivo_observacion"] = motivo
    return lambda: _cliente(user).put(
        f"/api/v1/checklist/{item.pk}/", datos, format="json"
    )


def _subir(user, url, campo):
    def accion():
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "documento.pdf"
        return _cliente(user).post(url, {campo: archivo}, format="multipart")

    return accion


# --- C1 ---------------------------------------------------------------------


def test_c1_observar_y_evaluar_mismo_item_sin_interbloqueo(
    en_verificacion, actores, monkeypatch
):
    """H-29: evaluar OBSERVADO (retenido justo antes de la transición) frente a
    `observar` del mismo requisito. Antes de T2: 40P01; ahora, serializados."""
    item = ChecklistVerification.objects.filter(expediente=en_verificacion).first()
    peticion = _peticion_de(en_verificacion, item)
    retencion = Retencion(monkeypatch, evaluar_checklist, "registrar_transicion")

    evaluar, observar = _carrera(
        retencion,
        _put_checklist(actores["jurista"], item, "OBSERVADO", "Ilegible"),
        lambda: _cliente(actores["jurista2"]).post(
            f"/api/v1/expedientes/{en_verificacion.pk}/observar/",
            {"peticion_id": str(peticion.pk), "motivo_observacion": "Sin firma"},
            format="json",
        ),
    )

    assert evaluar.status_code == 200
    assert observar.status_code == 400
    assert observar.json()["code"] == "expediente_no_en_verificacion"
    en_verificacion.refresh_from_db()
    assert en_verificacion.estado == E.ESTADO_OBSERVADA
    assert (
        _transiciones(
            en_verificacion, E.ESTADO_EN_VERIFICACION, E.ESTADO_OBSERVADA
        ).count()
        == 1
    )
    assert _eventos(en_verificacion, E.ESTADO_OBSERVADA).count() == 1
    assert ObservacionAccionable.objects.filter(expediente=en_verificacion).count() == 1
    item.refresh_from_db()
    assert item.estado_verificacion == "OBSERVADO"


# --- C2 ---------------------------------------------------------------------


def test_c2_dos_evaluaciones_observado_sobre_items_distintos(
    en_verificacion, actores, monkeypatch
):
    item_a, item_b = list(
        ChecklistVerification.objects.filter(expediente=en_verificacion)[:2]
    )
    retencion = Retencion(monkeypatch, evaluar_checklist, "registrar_transicion")

    primera, segunda = _carrera(
        retencion,
        _put_checklist(actores["jurista"], item_a, "OBSERVADO", "Motivo A"),
        _put_checklist(actores["jurista2"], item_b, "OBSERVADO", "Motivo B"),
    )

    assert primera.status_code == 200
    assert segunda.status_code == 400
    assert segunda.json()["code"] == "expediente_not_in_verification"
    item_b.refresh_from_db()
    assert item_b.estado_verificacion == "PENDIENTE"
    assert (
        _transiciones(
            en_verificacion, E.ESTADO_EN_VERIFICACION, E.ESTADO_OBSERVADA
        ).count()
        == 1
    )
    assert _eventos(en_verificacion, E.ESTADO_OBSERVADA).count() == 1
    assert ObservacionAccionable.objects.filter(expediente=en_verificacion).count() == 1


# --- C3 ---------------------------------------------------------------------


def test_c3_subsanar_frente_a_evaluar(observado, actores, monkeypatch):
    """Subsanar (retenido antes de volver a EN_VERIFICACION) frente a la
    evaluación de otro ítem: la evaluación espera y se aplica sobre el
    estado ya confirmado por la subsanación."""
    expediente, item_obs = observado
    otro = (
        ChecklistVerification.objects.filter(
            expediente=expediente, estado_verificacion="PENDIENTE"
        )
        .exclude(pk=item_obs.pk)
        .first()
    )
    retencion = Retencion(monkeypatch, subsanar_mod, "registrar_transicion")

    subsanar, evaluar = _carrera(
        retencion,
        _subir(
            actores["estudiante"],
            f"/api/v1/checklist/{item_obs.pk}/subsanar/",
            "archivo",
        ),
        _put_checklist(actores["jurista"], otro, "VERIFICADO"),
    )

    assert subsanar.status_code == 201
    assert evaluar.status_code == 200
    expediente.refresh_from_db()
    item_obs.refresh_from_db()
    otro.refresh_from_db()
    assert expediente.estado == E.ESTADO_EN_VERIFICACION
    assert item_obs.estado_verificacion == "PENDIENTE"
    assert otro.estado_verificacion == "VERIFICADO"
    assert (
        _transiciones(expediente, E.ESTADO_OBSERVADA, E.ESTADO_EN_VERIFICACION).count()
        == 1
    )


# --- C4 ---------------------------------------------------------------------


def test_c4_doble_iniciar_verificacion(enviado, actores, monkeypatch):
    retencion = Retencion(monkeypatch, iniciar_mod, "registrar_transicion")
    url = f"/api/v1/expedientes/{enviado.pk}/iniciar-verificacion/"

    primera, segunda = _carrera(
        retencion,
        lambda: _cliente(actores["jurista"]).post(url),
        lambda: _cliente(actores["jurista2"]).post(url),
    )

    assert primera.status_code == 200
    assert segunda.status_code == 400
    assert segunda.json()["code"] == "transicion_invalida"
    assert ChecklistVerification.objects.filter(expediente=enviado).count() == 5
    assert (
        _transiciones(enviado, E.ESTADO_ENVIADA, E.ESTADO_EN_VERIFICACION).count() == 1
    )
    assert _eventos(enviado, E.ESTADO_EN_VERIFICACION).count() == 1
    assert (
        NotificacionInterna.objects.filter(
            expediente=enviado, titulo="Verificación iniciada"
        ).count()
        == 1
    )


# --- C5 ---------------------------------------------------------------------


def test_c5_doble_informe_un_solo_pdf_integro(listo_para_informe, actores, monkeypatch):
    """Dos `POST /informes/` simultáneos: un informe, un PDF íntegro, ningún
    archivo del perdedor y archivos preexistentes intactos (SHA-256)."""
    directorio = Path(PDFGeneratorAdapter().output_dir)
    directorio.mkdir(parents=True, exist_ok=True)
    numero = emitir_mod._generar_numero_providencia(listo_para_informe)
    centinela = directorio / f"providencia_590_{numero}.pdf"
    centinela.write_bytes(b"%PDF-centinela-preexistente")
    ajeno = directorio / "documento_ajeno.pdf"
    ajeno.write_bytes(b"%PDF-ajeno")
    hashes = {centinela: _sha256(centinela), ajeno: _sha256(ajeno)}
    antes = set(_archivos(directorio))

    retencion = Retencion(monkeypatch, transiciones, "registrar_transicion")
    cuerpo = {"expediente_id": str(listo_para_informe.pk), "dictamen": "APTO"}
    primera, segunda = _carrera(
        retencion,
        lambda: _cliente(actores["jurista"]).post(
            "/api/v1/informes/", cuerpo, format="json"
        ),
        lambda: _cliente(actores["jurista2"]).post(
            "/api/v1/informes/", cuerpo, format="json"
        ),
    )

    assert primera.status_code == 201
    assert segunda.status_code == 400
    assert segunda.json()["code"] == "informe_ya_emitido"
    informe = InformeAptitud.objects.get(expediente=listo_para_informe)
    assert InformeAptitud.objects.filter(expediente=listo_para_informe).count() == 1
    nuevos = set(_archivos(directorio)) - antes
    assert nuevos == {Path(informe.archivo_informe_path).name}
    assert Path(informe.archivo_informe_path).read_bytes().startswith(b"%PDF")
    for ruta, digest in hashes.items():
        assert _sha256(ruta) == digest
    listo_para_informe.refresh_from_db()
    assert listo_para_informe.estado == E.ESTADO_INFORME_EMITIDO
    assert (
        _transiciones(
            listo_para_informe, E.ESTADO_EN_VERIFICACION, E.ESTADO_INFORME_EMITIDO
        ).count()
        == 1
    )
    assert _eventos(listo_para_informe, E.ESTADO_INFORME_EMITIDO).count() == 1


# --- C6 ---------------------------------------------------------------------


def test_c6_carga_de_documento_frente_a_observar(en_verificacion, actores, monkeypatch):
    """`observar` (retenido con expediente y petición bloqueados) frente a la
    carga normal de la misma petición. Sin interbloqueo; la carga se aplica
    después. Nota: que la carga normal se acepte sobre OBSERVADO es H-21
    (E2-02b1, pendiente); aquí solo se comprueba la coherencia del bloqueo."""
    peticion = PeticionDocumental.objects.filter(expediente=en_verificacion).first()
    versiones_antes = DocumentoEntregado.objects.filter(peticion=peticion).count()
    retencion = Retencion(monkeypatch, observar_mod, "registrar_transicion")

    observar, cargar = _carrera(
        retencion,
        lambda: _cliente(actores["jurista"]).post(
            f"/api/v1/expedientes/{en_verificacion.pk}/observar/",
            {"peticion_id": str(peticion.pk), "motivo_observacion": "Sin firma"},
            format="json",
        ),
        _subir(
            actores["estudiante"],
            f"/api/v1/peticiones/{peticion.pk}/documento/",
            "archivo",
        ),
    )

    assert observar.status_code == 201
    assert cargar.status_code == 201
    documentos = DocumentoEntregado.objects.filter(peticion=peticion)
    assert documentos.count() == versiones_antes + 1
    assert documentos.filter(es_vigente=True).count() == 1
    en_verificacion.refresh_from_db()
    assert en_verificacion.estado == E.ESTADO_OBSERVADA
    assert (
        _transiciones(
            en_verificacion, E.ESTADO_EN_VERIFICACION, E.ESTADO_OBSERVADA
        ).count()
        == 1
    )


# --- C7 ---------------------------------------------------------------------


def test_c7_doble_declaratoria_un_solo_memorando(
    listo_para_informe, actores, monkeypatch
):
    emitir_mod.execute(actores["jurista"], listo_para_informe.pk)
    privada = Path(settings.PRIVATE_MEDIA_ROOT)
    antes = set(_archivos(privada))
    retencion = Retencion(monkeypatch, declarar_mod, "registrar_transicion")

    def declarar(user):
        def accion():
            archivo = io.BytesIO(PDF_VALIDO)
            archivo.name = "memorando.pdf"
            return _cliente(user).post(
                "/api/v1/declaratorias/",
                {
                    "expediente_id": str(listo_para_informe.pk),
                    "archivo_memorando": archivo,
                },
                format="multipart",
            )

        return accion

    primera, segunda = _carrera(
        retencion, declarar(actores["decano"]), declarar(actores["decano2"])
    )

    assert primera.status_code == 201
    assert segunda.status_code == 400
    assert segunda.json()["code"] == "expediente_invalido_para_declaratoria"
    declaratoria = DeclaratoriaAptitud.objects.get(expediente=listo_para_informe)
    nuevos = set(_archivos(privada)) - antes
    assert nuevos == {declaratoria.archivo_memorando_firmado_path}
    listo_para_informe.refresh_from_db()
    assert listo_para_informe.estado == E.ESTADO_DECLARADA_APTA
    assert _eventos(listo_para_informe, E.ESTADO_DECLARADA_APTA).count() == 1


# --- C8 ---------------------------------------------------------------------


def test_c8_solicitar_emision_frente_a_carga_sin_actualizacion_perdida(
    borrador, actores, monkeypatch
):
    """Antes de T3, `solicitar_emision` no bloqueaba nada: la carga podía
    pisar el estado. Ahora se serializan y ambos efectos persisten."""
    peticion = PeticionDocumental.objects.filter(
        expediente=borrador, dependencia_emisora="SECRETARIA_CARRERA"
    ).first()
    retencion = Retencion(monkeypatch, solicitar_mod, "obtener_usuario_emisor")

    solicitar, cargar = _carrera(
        retencion,
        lambda: _cliente(actores["estudiante"]).post(
            f"/api/v1/peticiones/{peticion.pk}/solicitar-emision/", {}, format="json"
        ),
        _subir(
            actores["estudiante"],
            f"/api/v1/peticiones/{peticion.pk}/documento/",
            "archivo",
        ),
    )

    assert solicitar.status_code == 200
    assert cargar.status_code == 201
    peticion.refresh_from_db()
    assert peticion.estado_peticion == "CARGADO"
    assert peticion.fecha_solicitud is not None
    assert NotificacionInterna.objects.filter(peticion=peticion).count() == 1
    assert (
        DocumentoEntregado.objects.filter(peticion=peticion, es_vigente=True).count()
        == 1
    )
