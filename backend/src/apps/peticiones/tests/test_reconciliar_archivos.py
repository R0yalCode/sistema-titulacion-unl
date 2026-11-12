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
    # Auditoría independiente (D-02): solo son eliminables los archivos de la
    # carpeta de un expediente existente; el escenario usa la del expediente real.
    carpeta = f"expedientes/2026/{expediente.pk}"
    rutas = {
        "expediente": str(expediente.pk),
        "documento": documento.archivo_path,
        "informe": "resoluciones/providencia_590_PROV-590-2026-0001.pdf",
        "huerfano": f"{carpeta}/20261101_000000_huerfano.pdf",
        "temporal": f"{carpeta}/.tmp-abandonado",
        "borrador": "resoluciones/providencia_590_PROV-590-2026-0009_BORRADOR.pdf",
        "reciente": f"{carpeta}/20261112_000000_en_curso.pdf",
    }
    _escribir(rutas["huerfano"])
    _escribir(rutas["temporal"], b"%PDF-parcial")
    _escribir(rutas["borrador"])
    _escribir(rutas["reciente"], antiguedad_s=60)
    destino_enlace = _escribir(f"{carpeta}/destino.pdf")
    os.symlink(destino_enlace, _raiz() / "enlace.pdf")
    rutas["destino_enlace"] = f"{carpeta}/destino.pdf"
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
    # D-02: un PDF de resoluciones/ sin referencia no se puede atribuir a un
    # expediente verificable: se informa pero nunca es eliminable.
    assert escenario["informe"] in _rutas(resultado, "no_verificables")


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


# --- Auditoría independiente: D-01, D-02, D-03, D-04, D-06 ------------------


def _expediente_con_documento(sufijo):
    estudiante = User.objects.create_user(
        username=f"i3c_{sufijo}",
        password="x",
        cedula=f"905100{sufijo:04d}",
        carrera_id=CARRERA,
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
    return expediente, documento


@pytest.mark.parametrize("formato", ["absoluta", "con_puntos", "con_punto"])
def test_d01_referencia_en_cualquier_formato_nunca_es_huerfana(formato):
    _, documento = _expediente_con_documento(1)
    relativa = documento.archivo_path
    carpeta, nombre = relativa.rsplit("/", 1)
    variantes = {
        "absoluta": str((_raiz() / relativa).resolve()),
        "con_puntos": f"{carpeta}/../{carpeta.rsplit('/', 1)[-1]}/{nombre}",
        "con_punto": f"{carpeta}/./{nombre}",
    }
    type(documento).objects.filter(pk=documento.pk).update(
        archivo_path=variantes[formato]
    )
    hash_antes = _sha(_raiz() / relativa)

    resultado = _ejecutar("--eliminar", "--confirmar")

    assert relativa in _rutas(resultado, "referenciados")
    assert relativa not in resultado["eliminados"]
    assert _sha(_raiz() / relativa) == hash_antes


def test_d01_referencia_de_declaratoria_absoluta():
    from apps.resoluciones.adapters.models import DeclaratoriaAptitud

    expediente, documento = _expediente_con_documento(2)
    memorando = _escribir(f"expedientes/2026/{expediente.pk}/memorando_162_X.pdf")
    DeclaratoriaAptitud.objects.create(
        expediente=expediente,
        numero_memorando="MEM-162-2026-9999",
        decano=documento.subido_por,
        archivo_memorando_firmado_path=str(memorando),
    )
    resultado = _ejecutar("--eliminar", "--confirmar")
    assert memorando.exists()
    assert f"expedientes/2026/{expediente.pk}/memorando_162_X.pdf" in _rutas(
        resultado, "referenciados"
    )


def test_d02_base_sin_referencias_aborta_sin_borrar():
    for i in range(3):
        _escribir(f"expedientes/2026/e/{i}.pdf")
    antes = _todas()
    with pytest.raises(CommandError, match="no se puede verificar"):
        call_command(
            "reconciliar_archivos", "--eliminar", "--confirmar", stdout=StringIO()
        )
    assert _todas() == antes


def test_d02_raiz_equivocada_aborta_sin_borrar():
    """La BD tiene referencias, pero ninguna está en esta raíz (raíz o base
    equivocadas): no se puede verificar la conciliación y no se borra nada."""
    expediente, documento = _expediente_con_documento(3)
    (_raiz() / documento.archivo_path).unlink()
    huerfano = _escribir(f"expedientes/2026/{expediente.pk}/viejo.pdf")
    with pytest.raises(CommandError, match="no se puede verificar"):
        call_command(
            "reconciliar_archivos", "--eliminar", "--confirmar", stdout=StringIO()
        )
    assert huerfano.exists()


def test_d02_carpeta_sin_expediente_no_es_eliminable(escenario):
    desconocido = _escribir(
        "expedientes/2026/00000000-0000-4000-8000-00000000dead/x.pdf"
    )
    resultado = _ejecutar("--eliminar", "--confirmar")
    assert desconocido.exists()
    assert "expedientes/2026/00000000-0000-4000-8000-00000000dead/x.pdf" in _rutas(
        resultado, "no_verificables"
    )


def test_d02_limite_de_eliminaciones(escenario):
    carpeta = f"expedientes/2026/{escenario['expediente']}"
    for i in range(5):
        _escribir(f"{carpeta}/extra_{i}.pdf")
    antes = _todas()
    with pytest.raises(CommandError, match="límite"):
        call_command(
            "reconciliar_archivos",
            "--eliminar",
            "--confirmar",
            "--max-eliminaciones",
            "3",
            stdout=StringIO(),
        )
    assert _todas() == antes


def test_d02_errores_de_lectura_abortan_la_eliminacion(escenario):
    ilegible = _raiz() / f"expedientes/2026/{escenario['expediente']}/sub"
    ilegible.mkdir()
    os.chmod(ilegible, 0)
    try:
        antes = _todas()
        with pytest.raises(CommandError, match="no se puede verificar"):
            call_command(
                "reconciliar_archivos", "--eliminar", "--confirmar", stdout=StringIO()
            )
        assert _todas() == antes
    finally:
        os.chmod(ilegible, 0o755)


def test_d03_eliminar_exige_antiguedad_minima(escenario):
    antes = _todas()
    with pytest.raises(CommandError, match="antigüedad"):
        call_command(
            "reconciliar_archivos",
            "--eliminar",
            "--confirmar",
            "--antiguedad-minima-horas",
            "0",
            stdout=StringIO(),
        )
    assert _todas() == antes


def test_d04_raiz_inexistente(settings, tmp_path):
    settings.PRIVATE_MEDIA_ROOT = tmp_path / "no_existe"
    texto = StringIO()
    call_command("reconciliar_archivos", stdout=texto)
    assert "raíz inexistente" in texto.getvalue()
    resultado = _ejecutar()
    assert resultado["raiz_existe"] is False and resultado["huerfanos"] == []


def test_d06_reporta_directorios_enlazados_e_ilegibles(escenario, tmp_path):
    externo = tmp_path / "externo"
    externo.mkdir()
    (externo / "x.pdf").write_bytes(PDF)
    os.symlink(externo, _raiz() / "dir_enlazado")
    ilegible = _raiz() / "expedientes/2026/ilegible"
    ilegible.mkdir(parents=True)
    os.chmod(ilegible, 0)
    try:
        resultado = _ejecutar()
    finally:
        os.chmod(ilegible, 0o755)
    assert {"ruta": "dir_enlazado", "tipo": "directorio"} in resultado[
        "enlaces_omitidos"
    ]
    assert any("ilegible" in e["ruta"] for e in resultado["errores_lectura"])
    assert (externo / "x.pdf").exists()
