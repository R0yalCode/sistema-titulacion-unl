"""Concilia el almacenamiento privado con los registros (I-3, H-I3-06/H-I3-08).

Lista los archivos del almacenamiento privado que ningún registro referencia:

- `DocumentoEntregado.archivo_path`,
- `DeclaratoriaAptitud.archivo_memorando_firmado_path`,
- `InformeAptitud.archivo_informe_path`.

Todas las referencias se normalizan igual, sean absolutas o relativas (D-01):
un archivo referenciado nunca se clasifica como huérfano por el formato de su
ruta.

Es de **solo lectura por defecto**. Con `--eliminar --confirmar` solo borra
huérfanos y temporales de escritura abandonados, y únicamente si:

1. **la conciliación es verificable** (D-02): hay referencias en la BD, al
   menos una de ellas está presente en esta raíz, el recorrido no tuvo errores
   de lectura y los candidatos no superan `--max-eliminaciones`; si no, aborta
   sin borrar nada;
2. el archivo está en la carpeta de un **expediente existente**
   (`expedientes/<año>/<uuid>/`); lo demás se informa como `no_verificables`;
3. su antigüedad es al menos `--antiguedad-minima-horas`, que para eliminar no
   puede ser menor que `ANTIGUEDAD_MINIMA_ELIMINACION_HORAS` (D-03);
4. el expediente se puede **bloquear sin esperar** (`select_for_update(nowait)`):
   toda operación que escribe archivos (carga, subsanación, declaratoria)
   mantiene ese bloqueo desde antes de escribir hasta su *commit*, así que un
   expediente bloqueado indica una operación en curso y su carpeta se omite
   (`en_uso_omitidos`). Con el bloqueo adquirido se vuelve a comprobar que el
   archivo sigue sin referencia (D-03).

Nunca sale de la raíz privada ni sigue enlaces simbólicos, y registra cada
eliminación. El bloqueo solo es efectivo en PostgreSQL (SQLite ignora
`select_for_update`).

Uso::

    python manage.py reconciliar_archivos [--antiguedad-minima-horas 24]
        [--formato texto|json] [--eliminar --confirmar] [--max-eliminaciones 50]
"""

import json
import logging
import os
import posixpath
import re
import time
import uuid
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import OperationalError, transaction

from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.peticiones.adapters.models import DocumentoEntregado
from apps.resoluciones.adapters.models import DeclaratoriaAptitud, InformeAptitud
from core.adapters.local_storage import PREFIJO_TEMPORAL

logger = logging.getLogger(__name__)

CATEGORIAS = (
    "referenciados",
    "huerfanos",
    "temporales",
    "no_verificables",
    "borradores_no_referenciados",
    "recientes_omitidos",
    "enlaces_omitidos",
    "errores_lectura",
)
ELIMINABLES = ("huerfanos", "temporales")
ANTIGUEDAD_MINIMA_ELIMINACION_HORAS = 1.0
MAX_ELIMINACIONES_POR_DEFECTO = 50
_CARPETA_EXPEDIENTE = re.compile(r"^expedientes/\d{4}/([^/]+)/")


def raiz_privada() -> Path:
    raiz = getattr(settings, "PRIVATE_MEDIA_ROOT", None)
    if raiz is None:
        raiz = Path(settings.MEDIA_ROOT) / "private"
    return Path(raiz).resolve()


def relativa_a_raiz(valor: str, raiz: Path) -> str | None:
    """Ruta canónica relativa a la raíz, o None si queda fuera (D-01)."""
    texto = str(valor).strip().replace("\\", "/")
    if not texto:
        return None
    if texto.startswith("/"):
        try:
            return Path(texto).resolve().relative_to(raiz).as_posix()
        except ValueError:
            return None
    canonica = posixpath.normpath(texto)
    if canonica in (".", "..") or canonica.startswith("../"):
        return None
    return canonica


def rutas_referenciadas(raiz: Path, expediente_id=None) -> tuple[set[str], list[str]]:
    """Rutas referenciadas (canónicas) y referencias fuera de la raíz."""
    documentos = DocumentoEntregado.objects.all()
    declaratorias = DeclaratoriaAptitud.objects.all()
    informes = InformeAptitud.objects.all()
    if expediente_id is not None:
        documentos = documentos.filter(peticion__expediente_id=expediente_id)
        declaratorias = declaratorias.filter(expediente_id=expediente_id)
        informes = informes.filter(expediente_id=expediente_id)
    valores = (
        list(documentos.values_list("archivo_path", flat=True))
        + list(declaratorias.values_list("archivo_memorando_firmado_path", flat=True))
        + list(informes.values_list("archivo_informe_path", flat=True))
    )
    referenciadas: set[str] = set()
    fuera: list[str] = []
    for valor in valores:
        if not valor:
            continue
        canonica = relativa_a_raiz(valor, raiz)
        if canonica is None:
            fuera.append(valor)
        else:
            referenciadas.add(canonica)
    return referenciadas, fuera


def expediente_de(relativa: str):
    """UUID del expediente dueño de la carpeta, o None si no es verificable."""
    coincidencia = _CARPETA_EXPEDIENTE.match(relativa)
    if not coincidencia:
        return None
    try:
        return uuid.UUID(coincidencia.group(1))
    except ValueError:
        return None


def clasificar(raiz: Path, antiguedad_minima_s: float, ahora: float) -> dict:
    resultado = {categoria: [] for categoria in CATEGORIAS}
    resultado["referencias_fuera_de_raiz"] = []
    resultado["total_referencias"] = 0
    resultado["raiz_existe"] = raiz.is_dir()
    if not resultado["raiz_existe"]:
        return resultado
    referenciadas, fuera = rutas_referenciadas(raiz)
    resultado["referencias_fuera_de_raiz"] = fuera
    resultado["total_referencias"] = len(referenciadas) + len(fuera)
    expedientes_existentes: dict = {}

    def al_fallar(error):
        ruta = Path(getattr(error, "filename", "") or "")
        try:
            relativa = ruta.relative_to(raiz).as_posix()
        except ValueError:
            relativa = str(ruta)
        resultado["errores_lectura"].append({"ruta": relativa, "error": str(error)})

    for directorio, subdirectorios, nombres in os.walk(
        raiz, followlinks=False, onerror=al_fallar
    ):
        for subdirectorio in subdirectorios:
            ruta = Path(directorio) / subdirectorio
            if ruta.is_symlink():
                resultado["enlaces_omitidos"].append(
                    {"ruta": ruta.relative_to(raiz).as_posix(), "tipo": "directorio"}
                )
        for nombre in nombres:
            ruta = Path(directorio) / nombre
            relativa = ruta.relative_to(raiz).as_posix()
            if ruta.is_symlink():
                resultado["enlaces_omitidos"].append({"ruta": relativa})
                continue
            if relativa in referenciadas:
                resultado["referenciados"].append({"ruta": relativa})
                continue
            try:
                estado = ruta.lstat()
            except OSError as error:
                resultado["errores_lectura"].append(
                    {"ruta": relativa, "error": str(error)}
                )
                continue
            entrada = {
                "ruta": relativa,
                "bytes": estado.st_size,
                "antiguedad_horas": round((ahora - estado.st_mtime) / 3600, 2),
            }
            if ahora - estado.st_mtime < antiguedad_minima_s:
                resultado["recientes_omitidos"].append(entrada)
                continue
            if relativa.startswith("resoluciones/") and "_BORRADOR" in nombre:
                resultado["borradores_no_referenciados"].append(entrada)
                continue
            expediente_id = expediente_de(relativa)
            if (
                expediente_id is not None
                and expediente_id not in expedientes_existentes
            ):
                expedientes_existentes[expediente_id] = (
                    ExpedienteTitulacion.objects.filter(pk=expediente_id).exists()
                )
            if expediente_id is None or not expedientes_existentes[expediente_id]:
                resultado["no_verificables"].append(entrada)
            elif nombre.startswith(PREFIJO_TEMPORAL):
                resultado["temporales"].append(entrada)
            else:
                resultado["huerfanos"].append(entrada)
    return resultado


def motivos_para_no_eliminar(resultado: dict, max_eliminaciones: int) -> list[str]:
    """Condiciones que impiden verificar la conciliación (D-02)."""
    motivos = []
    candidatos = sum(len(resultado[c]) for c in ELIMINABLES)
    if not resultado["raiz_existe"]:
        motivos.append("la raíz privada no existe")
    if resultado["total_referencias"] == 0:
        motivos.append("la base de datos no contiene ninguna referencia a archivos")
    elif not resultado["referenciados"]:
        motivos.append(
            "ningún archivo referenciado está en esta raíz (raíz o base equivocadas)"
        )
    if resultado["errores_lectura"]:
        motivos.append("el recorrido tuvo errores de lectura")
    if candidatos > max_eliminaciones:
        motivos.append(
            f"{candidatos} candidatos superan el límite de {max_eliminaciones} "
            "(--max-eliminaciones)"
        )
    return motivos


def eliminar(raiz: Path, resultado: dict, antiguedad_minima_s: float) -> dict:
    """Borra huérfanos y temporales por expediente, con su bloqueo (D-03)."""
    referenciadas_inicio, _ = rutas_referenciadas(raiz)
    por_expediente: dict = {}
    for categoria in ELIMINABLES:
        for entrada in resultado[categoria]:
            por_expediente.setdefault(expediente_de(entrada["ruta"]), []).append(
                (categoria, entrada)
            )
    eliminados, en_uso = [], []
    for expediente_id, entradas in por_expediente.items():
        try:
            with transaction.atomic():
                ExpedienteTitulacion.objects.select_for_update(nowait=True).get(
                    pk=expediente_id
                )
                vigentes, _ = rutas_referenciadas(raiz, expediente_id)
                for categoria, entrada in entradas:
                    ruta = raiz / entrada["ruta"]
                    if (
                        entrada["ruta"] in referenciadas_inicio
                        or entrada["ruta"] in vigentes
                        or ruta.is_symlink()
                        or not ruta.is_file()
                        or raiz not in ruta.resolve().parents
                        or time.time() - ruta.lstat().st_mtime < antiguedad_minima_s
                    ):
                        continue
                    ruta.unlink()
                    eliminados.append(entrada["ruta"])
                    logger.warning(
                        "reconciliar_archivos: eliminado %s (%s)",
                        entrada["ruta"],
                        categoria,
                    )
        except ExpedienteTitulacion.DoesNotExist:
            continue
        except OperationalError:
            # Expediente bloqueado por una operación en curso: no se toca.
            en_uso.extend(entrada["ruta"] for _categoria, entrada in entradas)
    return {"eliminados": eliminados, "en_uso_omitidos": en_uso}


class Command(BaseCommand):
    help = (
        "Lista archivos del almacenamiento privado sin registro (solo lectura por "
        "defecto). Borrar exige --eliminar --confirmar y una conciliación verificable."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--antiguedad-minima-horas",
            type=float,
            default=24.0,
            help=(
                "Ignora archivos más recientes. Defecto: 24. Para --eliminar, "
                f"mínimo {ANTIGUEDAD_MINIMA_ELIMINACION_HORAS} h."
            ),
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
        parser.add_argument(
            "--max-eliminaciones",
            type=int,
            default=MAX_ELIMINACIONES_POR_DEFECTO,
            help="Aborta la eliminación si hay más candidatos. Defecto: %(default)s.",
        )

    def handle(self, *args, **opciones):
        horas = opciones["antiguedad_minima_horas"]
        if horas < 0:
            raise CommandError("--antiguedad-minima-horas no puede ser negativa.")
        if opciones["eliminar"]:
            if not opciones["confirmar"]:
                raise CommandError(
                    "--eliminar requiere --confirmar; no se ha borrado nada."
                )
            if horas < ANTIGUEDAD_MINIMA_ELIMINACION_HORAS:
                raise CommandError(
                    "Para eliminar, la antigüedad mínima debe ser al menos "
                    f"{ANTIGUEDAD_MINIMA_ELIMINACION_HORAS} h; no se ha borrado nada."
                )
        raiz = raiz_privada()
        resultado = clasificar(raiz, horas * 3600, time.time())
        resultado["raiz"] = str(raiz)
        resultado["modo"] = "eliminacion" if opciones["eliminar"] else "solo_lectura"
        resultado["eliminados"] = []
        resultado["en_uso_omitidos"] = []

        if opciones["eliminar"]:
            motivos = motivos_para_no_eliminar(resultado, opciones["max_eliminaciones"])
            if motivos:
                raise CommandError(
                    "Eliminación abortada, no se puede verificar la conciliación: "
                    + "; ".join(motivos)
                    + ". No se ha borrado nada."
                )
            resultado.update(eliminar(raiz, resultado, horas * 3600))

        if opciones["formato"] == "json":
            self.stdout.write(json.dumps(resultado, ensure_ascii=False, indent=2))
            return
        if not resultado["raiz_existe"]:
            self.stdout.write(f"Raíz: {raiz} · raíz inexistente: nada que conciliar.")
            return
        self.stdout.write(f"Raíz: {raiz} · modo: {resultado['modo']}")
        for categoria in CATEGORIAS:
            self.stdout.write(f"{categoria}: {len(resultado[categoria])}")
        for categoria in (
            "huerfanos",
            "temporales",
            "no_verificables",
            "borradores_no_referenciados",
        ):
            for entrada in resultado[categoria]:
                self.stdout.write(
                    f"  [{categoria}] {entrada['ruta']} "
                    f"({entrada['bytes']} B, {entrada['antiguedad_horas']} h)"
                )
        for entrada in resultado["enlaces_omitidos"] + resultado["errores_lectura"]:
            self.stdout.write(f"  [omitido] {entrada}")
        if resultado["referencias_fuera_de_raiz"]:
            self.stdout.write(
                "referencias_fuera_de_raiz: "
                f"{len(resultado['referencias_fuera_de_raiz'])}"
            )
        self.stdout.write(
            f"eliminados: {len(resultado['eliminados'])} · "
            f"en_uso_omitidos: {len(resultado['en_uso_omitidos'])}"
        )
