"""Concilia el almacenamiento privado con los registros (I-3, H-I3-06/H-I3-08).

Lista los archivos del almacenamiento privado que ningún registro referencia:

- `DocumentoEntregado.archivo_path` (ruta relativa),
- `DeclaratoriaAptitud.archivo_memorando_firmado_path` (ruta relativa),
- `InformeAptitud.archivo_informe_path` (ruta absoluta del generador PDF).

Es de **solo lectura por defecto**. Solo borra con `--eliminar --confirmar`,
y únicamente archivos clasificados como huérfanos o temporales de escritura
abandonados. Nunca borra archivos referenciados, recientes (más nuevos que
`--antiguedad-minima-horas`, para no tocar operaciones en curso),
borradores de resoluciones no referenciados (requieren revisión) ni enlaces
simbólicos, y nunca sale de la raíz privada.

Uso::

    python manage.py reconciliar_archivos [--antiguedad-minima-horas 24]
        [--formato texto|json] [--eliminar --confirmar]
"""

import json
import logging
import os
import time
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.peticiones.adapters.models import DocumentoEntregado
from apps.resoluciones.adapters.models import DeclaratoriaAptitud, InformeAptitud
from core.adapters.local_storage import PREFIJO_TEMPORAL

logger = logging.getLogger(__name__)

CATEGORIAS = (
    "referenciados",
    "huerfanos",
    "temporales",
    "borradores_no_referenciados",
    "recientes_omitidos",
    "enlaces_omitidos",
)
ELIMINABLES = ("huerfanos", "temporales")


def raiz_privada() -> Path:
    raiz = getattr(settings, "PRIVATE_MEDIA_ROOT", None)
    if raiz is None:
        raiz = Path(settings.MEDIA_ROOT) / "private"
    return Path(raiz).resolve()


def _normalizar(valor: str) -> str:
    return Path(valor).as_posix().lstrip("/")


def rutas_referenciadas(raiz: Path) -> tuple[set[str], list[str]]:
    """Rutas relativas referenciadas y referencias que caen fuera de la raíz."""
    referenciadas: set[str] = set()
    fuera: list[str] = []
    relativas = list(
        DocumentoEntregado.objects.values_list("archivo_path", flat=True)
    ) + list(
        DeclaratoriaAptitud.objects.values_list(
            "archivo_memorando_firmado_path", flat=True
        )
    )
    for valor in relativas:
        if valor:
            referenciadas.add(_normalizar(valor))
    for valor in InformeAptitud.objects.values_list("archivo_informe_path", flat=True):
        if not valor:
            continue
        ruta = Path(valor)
        if not ruta.is_absolute():
            referenciadas.add(_normalizar(valor))
            continue
        try:
            referenciadas.add(ruta.resolve().relative_to(raiz).as_posix())
        except ValueError:
            fuera.append(valor)
    return referenciadas, fuera


def clasificar(raiz: Path, antiguedad_minima_s: float, ahora: float) -> dict:
    resultado = {categoria: [] for categoria in CATEGORIAS}
    if not raiz.is_dir():
        return resultado
    referenciadas, fuera = rutas_referenciadas(raiz)
    resultado["referencias_fuera_de_raiz"] = fuera
    for directorio, _subdirectorios, nombres in os.walk(raiz, followlinks=False):
        for nombre in nombres:
            ruta = Path(directorio) / nombre
            relativa = ruta.relative_to(raiz).as_posix()
            if ruta.is_symlink():
                resultado["enlaces_omitidos"].append({"ruta": relativa})
                continue
            if relativa in referenciadas:
                resultado["referenciados"].append({"ruta": relativa})
                continue
            estado = ruta.lstat()
            entrada = {
                "ruta": relativa,
                "bytes": estado.st_size,
                "antiguedad_horas": round((ahora - estado.st_mtime) / 3600, 2),
            }
            if ahora - estado.st_mtime < antiguedad_minima_s:
                resultado["recientes_omitidos"].append(entrada)
            elif nombre.startswith(PREFIJO_TEMPORAL):
                resultado["temporales"].append(entrada)
            elif relativa.startswith("resoluciones/") and "_BORRADOR" in nombre:
                resultado["borradores_no_referenciados"].append(entrada)
            else:
                resultado["huerfanos"].append(entrada)
    return resultado


def eliminar(raiz: Path, resultado: dict) -> list[str]:
    """Borra solo huérfanos y temporales, revalidando cada ruta antes."""
    referenciadas, _fuera = rutas_referenciadas(raiz)
    eliminados = []
    for categoria in ELIMINABLES:
        for entrada in resultado[categoria]:
            ruta = raiz / entrada["ruta"]
            if (
                entrada["ruta"] in referenciadas
                or ruta.is_symlink()
                or not ruta.is_file()
                or raiz not in ruta.resolve().parents
            ):
                continue
            ruta.unlink()
            eliminados.append(entrada["ruta"])
            logger.warning(
                "reconciliar_archivos: eliminado %s (%s)", entrada["ruta"], categoria
            )
    return eliminados


class Command(BaseCommand):
    help = (
        "Lista archivos del almacenamiento privado sin registro (solo lectura por "
        "defecto). Borrar exige --eliminar --confirmar."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--antiguedad-minima-horas",
            type=float,
            default=24.0,
            help="Ignora archivos más recientes (operaciones en curso). Defecto: 24.",
        )
        parser.add_argument("--formato", choices=("texto", "json"), default="texto")
        parser.add_argument(
            "--eliminar",
            action="store_true",
            help="Borra huérfanos y temporales abandonados (requiere --confirmar).",
        )
        parser.add_argument(
            "--confirmar",
            action="store_true",
            help="Confirmación explícita de --eliminar.",
        )

    def handle(self, *args, **opciones):
        if opciones["eliminar"] and not opciones["confirmar"]:
            raise CommandError(
                "--eliminar requiere --confirmar; no se ha borrado nada."
            )
        if opciones["antiguedad_minima_horas"] < 0:
            raise CommandError("--antiguedad-minima-horas no puede ser negativa.")
        raiz = raiz_privada()
        resultado = clasificar(
            raiz, opciones["antiguedad_minima_horas"] * 3600, time.time()
        )
        resultado["raiz"] = str(raiz)
        resultado["eliminados"] = (
            eliminar(raiz, resultado) if opciones["eliminar"] else []
        )
        resultado["modo"] = "eliminacion" if opciones["eliminar"] else "solo_lectura"

        if opciones["formato"] == "json":
            self.stdout.write(json.dumps(resultado, ensure_ascii=False, indent=2))
            return
        self.stdout.write(f"Raíz: {raiz} · modo: {resultado['modo']}")
        for categoria in CATEGORIAS:
            self.stdout.write(f"{categoria}: {len(resultado[categoria])}")
        for categoria in ("huerfanos", "temporales", "borradores_no_referenciados"):
            for entrada in resultado[categoria]:
                self.stdout.write(
                    f"  [{categoria}] {entrada['ruta']} "
                    f"({entrada['bytes']} B, {entrada['antiguedad_horas']} h)"
                )
        if resultado["referencias_fuera_de_raiz"]:
            self.stdout.write(
                "referencias_fuera_de_raiz: "
                f"{len(resultado['referencias_fuera_de_raiz'])}"
            )
        self.stdout.write(f"eliminados: {len(resultado['eliminados'])}")
