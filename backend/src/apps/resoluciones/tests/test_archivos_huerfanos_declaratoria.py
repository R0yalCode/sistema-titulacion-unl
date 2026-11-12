"""I-3 (T4): la declaratoria no deja fragmentos ni memorandos huérfanos.

- H-I3-03: si la escritura del memorando falla a mitad, no queda fragmento
  y la operación responde el error de almacenamiento existente.
- Compensación común: si falla un paso posterior a guardar el memorando, se
  borra solo ese archivo (comportamiento de D-6, ahora con el gestor común).
- Archivos preexistentes y ajenos intactos (SHA-256).
"""

import hashlib
import importlib
import io
import itertools
from pathlib import Path
from unittest import mock

import pytest
from django.conf import settings
from django.core.files.base import File

from apps.authentication.adapters.models import Role, User, UserRole
from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.expedientes.services import (
    crear_expediente,
    enviar_expediente,
    iniciar_verificacion,
)
from apps.expedientes.services.transiciones import TransicionNoPermitidaError
from apps.peticiones.adapters.models import PeticionDocumental
from apps.resoluciones.adapters.models import DeclaratoriaAptitud
from apps.verificacion.adapters.models import ChecklistVerification
from apps.verificacion.services import evaluar_checklist

emitir_mod = importlib.import_module("apps.resoluciones.services.emitir_informe")
declarar_mod = importlib.import_module("apps.resoluciones.services.declarar_aptitud")

pytestmark = pytest.mark.django_db

E = ExpedienteTitulacion
CARRERA = "aaaaaaaa-1304-4111-8111-111111111111"
FACULTAD = "bbbbbbbb-1304-4111-8111-111111111111"
_CEDULAS = itertools.count(8040000001)
PDF = (
    b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    b"2 0 obj\n<< /Type /Pages /Kids [] /Count 0 >>\nendobj\n"
    b"trailer\n<< /Root 1 0 R >>\n%%EOF\n"
)


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


def _privada():
    return Path(settings.PRIVATE_MEDIA_ROOT)


def _memorandos():
    """Archivos privados fuera de `resoluciones/` (donde va el PDF del informe)."""
    raiz = _privada()
    return sorted(
        str(p.relative_to(raiz))
        for p in raiz.rglob("*")
        if p.is_file() and not str(p.relative_to(raiz)).startswith("resoluciones/")
    )


def _sha(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


class ArchivoQueFalla(File):
    """Entrega un primer bloque y falla (disco lleno simulado)."""

    def chunks(self, chunk_size=None):
        self.seek(0)
        yield self.read(20)
        raise OSError(28, "No space left on device (simulado)")


@pytest.fixture
def informe_emitido():
    estudiante = _usuario("i3t4_est", "ESTUDIANTE")
    jurista = _usuario("i3t4_jur", "SECRETARIO_ABOGADO")
    decano = _usuario("i3t4_dec", "DECANO")
    expediente = crear_expediente.execute(estudiante, CARRERA)
    PeticionDocumental.objects.filter(expediente=expediente).update(
        estado_peticion="CARGADO"
    )
    enviar_expediente.execute(expediente, actor=estudiante)
    iniciar_verificacion.execute(expediente.pk, actor=jurista)
    for item in ChecklistVerification.objects.filter(expediente=expediente):
        evaluar_checklist.execute(jurista, item.pk, "VERIFICADO")
    emitir_mod.execute(jurista, expediente.pk)
    expediente.refresh_from_db()
    assert expediente.estado == E.ESTADO_INFORME_EMITIDO
    return expediente, decano


def _con_centinelas():
    ajeno = _privada() / "ajeno.pdf"
    ajeno.write_bytes(b"%PDF-ajeno")
    return {ajeno: _sha(ajeno)}


def test_escritura_parcial_del_memorando_no_deja_fragmento(informe_emitido):
    expediente, decano = informe_emitido
    centinelas = _con_centinelas()
    antes = _memorandos()

    with pytest.raises(declarar_mod.PDFInvalidoError) as info:
        declarar_mod.execute(
            decano, expediente.pk, ArchivoQueFalla(io.BytesIO(PDF), name="m.pdf")
        )

    assert info.value.code == "storage_error"
    assert _memorandos() == antes
    for ruta, digest in centinelas.items():
        assert _sha(ruta) == digest
    expediente.refresh_from_db()
    assert expediente.estado == E.ESTADO_INFORME_EMITIDO
    assert not DeclaratoriaAptitud.objects.filter(expediente=expediente).exists()


def test_fallo_tras_guardar_borra_solo_el_memorando_propio(informe_emitido):
    expediente, decano = informe_emitido
    centinelas = _con_centinelas()
    antes = _memorandos()

    with mock.patch.object(
        declarar_mod,
        "registrar_transicion",
        side_effect=TransicionNoPermitidaError(
            "simulada",
            estado_anterior=E.ESTADO_INFORME_EMITIDO,
            estado_nuevo=E.ESTADO_DECLARADA_APTA,
        ),
    ):
        with pytest.raises(TransicionNoPermitidaError):
            declarar_mod.execute(decano, expediente.pk, io.BytesIO(PDF))

    assert _memorandos() == antes
    for ruta, digest in centinelas.items():
        assert _sha(ruta) == digest
    assert not DeclaratoriaAptitud.objects.filter(expediente=expediente).exists()


def test_declaratoria_correcta_conserva_el_memorando(informe_emitido):
    expediente, decano = informe_emitido
    declaratoria = declarar_mod.execute(decano, expediente.pk, io.BytesIO(PDF))
    ruta = _privada() / declaratoria.archivo_memorando_firmado_path
    assert ruta.read_bytes() == PDF
    assert _memorandos() == [declaratoria.archivo_memorando_firmado_path]
