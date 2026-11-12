"""I-3 (T1): almacenamiento privado atómico, nombres acotados y compensación.

- H-I3-03: un fallo de escritura no deja fragmentos ni temporales.
- No sobrescritura: un archivo existente con el mismo nombre no cambia.
- H-I3-04: el nombre físico se acota en bytes y conserva la extensión.
- Compensación: si la operación falla, se borran solo los archivos que creó;
  los preexistentes y los ajenos quedan intactos (SHA-256).
"""

import hashlib
import io
import os
from pathlib import Path
from unittest import mock

import pytest
from django.conf import settings
from django.core.files.base import File

from core.adapters import local_storage
from core.adapters.local_storage import (
    MAX_BYTES_NOMBRE_FISICO,
    PREFIJO_TEMPORAL,
    PrivateMediaStorage,
    compensacion_de_archivos,
    generar_ruta_archivo,
    guardar_archivo_privado,
)

EXPEDIENTE = "e1e1e1e1-0000-4000-8000-000000000001"
PDF = b"%PDF-1.4\n" + b"x" * 200 + b"\n%%EOF\n"


def _raiz():
    return Path(settings.PRIVATE_MEDIA_ROOT)


def _archivos():
    return sorted(
        str(p.relative_to(_raiz())) for p in _raiz().rglob("*") if p.is_file()
    )


def _sha(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


class ArchivoQueFalla(File):
    """Entrega un primer bloque y falla (disco lleno simulado)."""

    def chunks(self, chunk_size=None):
        self.seek(0)
        yield self.read(20)
        raise OSError(28, "No space left on device (simulado)")


# --- Escritura atómica (H-I3-03) --------------------------------------------


def test_guardado_correcto_contenido_integro():
    ruta = guardar_archivo_privado(io.BytesIO(PDF), EXPEDIENTE, "doc.pdf")
    assert (_raiz() / ruta).read_bytes() == PDF
    assert _archivos() == [ruta]


def test_fallo_de_escritura_no_deja_fragmento_ni_temporal():
    archivo = ArchivoQueFalla(io.BytesIO(PDF), name="doc.pdf")
    with pytest.raises(OSError):
        guardar_archivo_privado(archivo, EXPEDIENTE, "doc.pdf")
    assert _archivos() == []


def test_posicion_del_archivo_se_restaura():
    contenido = io.BytesIO(PDF)
    contenido.seek(7)
    guardar_archivo_privado(contenido, EXPEDIENTE, "doc.pdf")
    assert contenido.tell() == 7


def test_no_sobrescribe_un_archivo_existente():
    with mock.patch.object(local_storage, "datetime") as reloj:
        reloj.now.return_value.year = 2026
        reloj.now.return_value.strftime.return_value = "20261112_120000"
        primera = guardar_archivo_privado(io.BytesIO(PDF), EXPEDIENTE, "doc.pdf")
        hash_primera = _sha(_raiz() / primera)
        segunda = guardar_archivo_privado(
            io.BytesIO(b"%PDF-otro"), EXPEDIENTE, "doc.pdf"
        )
    assert segunda != primera
    assert _sha(_raiz() / primera) == hash_primera
    assert (_raiz() / segunda).read_bytes() == b"%PDF-otro"


def test_permisos_iguales_a_los_del_almacenamiento():
    ruta = guardar_archivo_privado(io.BytesIO(PDF), EXPEDIENTE, "doc.pdf")
    esperado = PrivateMediaStorage().file_permissions_mode
    if esperado is not None:
        assert (os.stat(_raiz() / ruta).st_mode & 0o777) == esperado


# --- Nombre físico acotado (H-I3-04) ----------------------------------------


@pytest.mark.parametrize(
    "nombre",
    ["é" * 200 + ".pdf", "a" * 250 + ".pdf", "ñandú_" * 40 + ".pdf"],
)
def test_nombre_fisico_acotado_en_bytes_y_con_extension(nombre):
    ruta = generar_ruta_archivo(EXPEDIENTE, nombre)
    fisico = ruta.rsplit("/", 1)[-1]
    assert len(fisico.encode("utf-8")) <= MAX_BYTES_NOMBRE_FISICO
    assert fisico.endswith(".pdf")
    fisico.encode("utf-8").decode("utf-8")  # sin caracteres partidos


def test_nombre_multibyte_largo_se_guarda():
    ruta = guardar_archivo_privado(io.BytesIO(PDF), EXPEDIENTE, "é" * 200 + ".pdf")
    assert (_raiz() / ruta).read_bytes() == PDF


def test_nombre_corto_conserva_el_formato():
    ruta = generar_ruta_archivo(EXPEDIENTE, "Acta de grado.pdf")
    assert ruta.startswith("expedientes/") and ruta.endswith("_Actadegrado.pdf")


# --- Compensación (base de H-I3-01/02) --------------------------------------


def test_compensacion_borra_solo_lo_creado_por_la_operacion():
    preexistente = guardar_archivo_privado(
        io.BytesIO(b"%PDF-previo"), EXPEDIENTE, "doc.pdf"
    )
    ajeno = _raiz() / "ajeno.pdf"
    ajeno.write_bytes(b"%PDF-ajeno")
    hashes = {preexistente: _sha(_raiz() / preexistente), "ajeno.pdf": _sha(ajeno)}

    with pytest.raises(RuntimeError):
        with compensacion_de_archivos() as archivos:
            archivos.guardar(io.BytesIO(PDF), EXPEDIENTE, "doc.pdf")
            archivos.guardar(io.BytesIO(PDF), EXPEDIENTE, "otro.pdf")
            raise RuntimeError("fallo posterior simulado")

    assert _archivos() == sorted(hashes)
    for ruta, digest in hashes.items():
        assert _sha(_raiz() / ruta) == digest


def test_compensacion_no_borra_nada_si_la_operacion_termina_bien():
    with compensacion_de_archivos() as archivos:
        ruta = archivos.guardar(io.BytesIO(PDF), EXPEDIENTE, "doc.pdf")
    assert _archivos() == [ruta]


def test_compensacion_tolera_un_archivo_ya_borrado():
    with pytest.raises(RuntimeError):
        with compensacion_de_archivos() as archivos:
            ruta = archivos.guardar(io.BytesIO(PDF), EXPEDIENTE, "doc.pdf")
            (_raiz() / ruta).unlink()
            raise RuntimeError("fallo")
    assert _archivos() == []


def test_prefijo_temporal_publico():
    assert PREFIJO_TEMPORAL.startswith(".")


def test_sin_enlaces_duros_usa_reserva_exclusiva_y_no_sobrescribe():
    error = OSError(1, "Operation not permitted")
    error.errno = 1  # EPERM
    with mock.patch.object(local_storage.os, "link", side_effect=error):
        with mock.patch.object(local_storage, "datetime") as reloj:
            reloj.now.return_value.year = 2026
            reloj.now.return_value.strftime.return_value = "20261112_120000"
            primera = guardar_archivo_privado(io.BytesIO(PDF), EXPEDIENTE, "doc.pdf")
            hash_primera = _sha(_raiz() / primera)
            segunda = guardar_archivo_privado(
                io.BytesIO(b"%PDF-2"), EXPEDIENTE, "doc.pdf"
            )
    assert segunda != primera
    assert _sha(_raiz() / primera) == hash_primera
    assert (_raiz() / segunda).read_bytes() == b"%PDF-2"
    assert _archivos() == sorted([primera, segunda])
