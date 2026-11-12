"""I-3 (T5): comando `reconciliar_archivos` (H-I3-06/H-I3-08).

Solo lectura por defecto; clasifica referenciados (las tres formas de ruta),
huérfanos, temporales, borradores, recientes y enlaces; borra solo con
`--eliminar --confirmar` y únicamente huérfanos y temporales antiguos.
"""

import hashlib
import io
import json
import os
import time
from io import StringIO
from pathlib import Path

import pytest
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.authentication.adapters.models import Role, User, UserRole
from apps.expedientes.services import crear_expediente
from apps.peticiones.adapters.models import PeticionDocumental
from apps.peticiones.services import cargar_documento
from apps.resoluciones.adapters.models import InformeAptitud

pytestmark = pytest.mark.django_db

CARRERA = "aaaaaaaa-1305-4111-8111-111111111111"
PDF = (
    b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    b"2 0 obj\n<< /Type /Pages /Kids [] /Count 0 >>\nendobj\n"
    b"trailer\n<< /Root 1 0 R >>\n%%EOF\n"
)
DIA = 24 * 3600


def _raiz():
    return Path(settings.PRIVATE_MEDIA_ROOT)


def _escribir(relativa, contenido=b"%PDF-x", antiguedad_s=2 * DIA):
    ruta = _raiz() / relativa
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_bytes(contenido)
    instante = time.time() - antiguedad_s
    os.utime(ruta, (instante, instante))
    return ruta


def _sha(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def _ejecutar(*argumentos):
    salida = StringIO()
    call_command(
        "reconciliar_archivos", "--formato", "json", *argumentos, stdout=salida
    )
    return json.loads(salida.getvalue())


def _rutas(resultado, categoria):
    return sorted(entrada["ruta"] for entrada in resultado[categoria])


@pytest.fixture
def escenario():
    estudiante = User.objects.create_user(
        username="i3t5_est", password="x", cedula="9050000001", carrera_id=CARRERA
    )
    UserRole.objects.create(
        user=estudiante, role=Role.objects.get_or_create(name="ESTUDIANTE")[0]
    )
    expediente = crear_expediente.execute(estudiante, CARRERA)
    peticion = PeticionDocumental.objects.filter(expediente=expediente).first()
    documento = cargar_documento.execute(
        usuario=estudiante,
        peticion_id=peticion.pk,
        archivo=io.BytesIO(PDF),
        nombre_original="doc.pdf",
    )
    os.utime(_raiz() / documento.archivo_path, (time.time() - 2 * DIA,) * 2)
    informe_pdf = _escribir("resoluciones/providencia_590_PROV-590-2026-0001.pdf")
    InformeAptitud.objects.create(
        expediente=expediente,
        numero_providencia="PROV-590-2026-0001",
        emisor=estudiante,
        dictamen="APTO",
        archivo_informe_path=str(informe_pdf),
    )
    rutas = {
        "documento": documento.archivo_path,
        "informe": "resoluciones/providencia_590_PROV-590-2026-0001.pdf",
        "huerfano": "expedientes/2026/x/20261101_000000_huerfano.pdf",
        "temporal": "expedientes/2026/x/.tmp-abandonado",
        "borrador": "resoluciones/providencia_590_PROV-590-2026-0009_BORRADOR.pdf",
        "reciente": "expedientes/2026/x/20261112_000000_en_curso.pdf",
    }
    _escribir(rutas["huerfano"])
    _escribir(rutas["temporal"], b"%PDF-parcial")
    _escribir(rutas["borrador"])
    _escribir(rutas["reciente"], antiguedad_s=60)
    destino_enlace = _escribir("expedientes/2026/x/destino.pdf")
    os.symlink(destino_enlace, _raiz() / "enlace.pdf")
    rutas["destino_enlace"] = "expedientes/2026/x/destino.pdf"
    return rutas


def test_clasificacion_en_solo_lectura(escenario):
    hashes = {r: _sha(p) for r, p in ((r, _raiz() / r) for r in _todas())}
    resultado = _ejecutar()

    assert resultado["modo"] == "solo_lectura"
    assert _rutas(resultado, "referenciados") == sorted(
        [escenario["documento"], escenario["informe"]]
    )
    assert _rutas(resultado, "huerfanos") == sorted(
        [escenario["huerfano"], escenario["destino_enlace"]]
    )
    assert _rutas(resultado, "temporales") == [escenario["temporal"]]
    assert _rutas(resultado, "borradores_no_referenciados") == [escenario["borrador"]]
    assert _rutas(resultado, "recientes_omitidos") == [escenario["reciente"]]
    assert _rutas(resultado, "enlaces_omitidos") == ["enlace.pdf"]
    assert resultado["eliminados"] == []
    assert {r: _sha(_raiz() / r) for r in _todas()} == hashes


def _todas():
    raiz = _raiz()
    return sorted(
        str(p.relative_to(raiz))
        for p in raiz.rglob("*")
        if p.is_file() and not p.is_symlink()
    )


def test_eliminar_sin_confirmar_no_borra_nada(escenario):
    antes = _todas()
    with pytest.raises(CommandError):
        call_command("reconciliar_archivos", "--eliminar", stdout=StringIO())
    assert _todas() == antes


def test_eliminar_confirmado_borra_solo_huerfanos_y_temporales(escenario):
    conservados = [
        escenario["documento"],
        escenario["informe"],
        escenario["borrador"],
        escenario["reciente"],
    ]
    hashes = {r: _sha(_raiz() / r) for r in conservados}

    resultado = _ejecutar("--eliminar", "--confirmar")

    assert sorted(resultado["eliminados"]) == sorted(
        [escenario["huerfano"], escenario["temporal"], escenario["destino_enlace"]]
    )
    for ruta, digest in hashes.items():
        assert _sha(_raiz() / ruta) == digest
    assert (_raiz() / "enlace.pdf").is_symlink()
    restantes = _ejecutar()
    assert restantes["huerfanos"] == [] and restantes["temporales"] == []


def test_antiguedad_minima_configurable(escenario):
    resultado = _ejecutar("--antiguedad-minima-horas", "0")
    assert escenario["reciente"] in _rutas(resultado, "huerfanos")


def test_referencia_de_informe_fuera_de_la_raiz(escenario, tmp_path):
    InformeAptitud.objects.update(archivo_informe_path=str(tmp_path / "otro.pdf"))
    resultado = _ejecutar()
    assert resultado["referencias_fuera_de_raiz"] == [str(tmp_path / "otro.pdf")]
    assert escenario["informe"] in _rutas(resultado, "huerfanos")


def test_salida_de_texto():
    salida = StringIO()
    call_command("reconciliar_archivos", stdout=salida)
    texto = salida.getvalue()
    assert "modo: solo_lectura" in texto and "eliminados: 0" in texto


def test_antiguedad_negativa_rechazada():
    with pytest.raises(CommandError):
        call_command(
            "reconciliar_archivos", "--antiguedad-minima-horas", "-1", stdout=StringIO()
        )
