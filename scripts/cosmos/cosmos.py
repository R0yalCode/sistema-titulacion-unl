#!/usr/bin/env python3
"""COSMOS: versionado SemVer + hitos astronómicos de SGT-SIAAF.

Fuente única de verdad: SIAAF-KNOWLEDGE/15-GIT-AND-WORKFLOWS/COSMOS_REGISTRO.json.
Las tablas de COSMOS_VERSIONING.md se generan desde el registro
(`documentar`) y `verificar` comprueba que no se hayan editado a mano.

Subcomandos:
  verificar         Solo lectura. Coherencia registro <-> Git <-> documento
                    <-> remoto (y, con --releases, <-> GitHub Releases).
  proponer          Solo lectura. Cambios desde la última versión, incremento
                    SemVer y hitos disponibles con su temática.
  notas             Solo lectura. Mensaje de la etiqueta o notas de la release.
  documentar        Regenera los bloques generados de COSMOS_VERSIONING.md.
  registrar         Añade una versión "preparada" al registro (no toca Git).
  publicar          SIMULACIÓN por defecto. Solo con `--ejecutar --confirmar
                    vX.Y.Z` crea la etiqueta anotada, la publica con push
                    normal y crea la GitHub Release.
  marcar-publicada  Pasa una versión a "publicada" tras comprobar su etiqueta
                    local y remota y su GitHub Release (no toca Git).

Ninguna orden usa --force, mueve, borra ni reemplaza etiquetas.
Solo biblioteca estándar de Python (sin dependencias).
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

RUTA_REGISTRO = "SIAAF-KNOWLEDGE/15-GIT-AND-WORKFLOWS/COSMOS_REGISTRO.json"
RUTA_DOC = "SIAAF-KNOWLEDGE/15-GIT-AND-WORKFLOWS/COSMOS_VERSIONING.md"
SEMVER = re.compile(r"^v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
ESTADOS = ("preparada", "publicada")
BLOQUES = ("catalogo", "versiones", "sin-version", "detalle")
# Rutas cuyo cambio, por sí solo, no genera versión (DK-005): documentación
# y la propia herramienta de versionado.
PREFIJOS_DOCUMENTALES = (
    "docs/",
    "SIAAF-KNOWLEDGE/",
    "Documentacion-parte-2/",
    "DOCUMENTACION/",
    "scripts/cosmos/",
)


class ErrorCosmos(Exception):
    """Error de uso o de entorno (código de salida 2)."""


def hoy() -> str:
    return os.environ.get("COSMOS_FECHA_HOY") or datetime.date.today().isoformat()


# --------------------------------------------------------------------------
# SemVer
# --------------------------------------------------------------------------


def parsear_version(texto: str) -> tuple[int, int, int]:
    m = SEMVER.match(texto or "")
    if not m:
        raise ValueError(f"'{texto}' no tiene el formato vX.Y.Z (SemVer sin sufijos ni 'V')")
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def incrementar(version: str, tipo: str) -> str:
    mayor, menor, parche = parsear_version(version)
    if tipo == "major":
        return f"v{mayor + 1}.0.0"
    if tipo == "minor":
        return f"v{mayor}.{menor + 1}.0"
    if tipo == "patch":
        return f"v{mayor}.{menor}.{parche + 1}"
    raise ValueError(f"incremento desconocido: {tipo}")


def es_incremento_valido(anterior: str, nueva: str) -> bool:
    return nueva in {incrementar(anterior, t) for t in ("major", "minor", "patch")}


# --------------------------------------------------------------------------
# Git y gh (solo lectura salvo en `publicar --ejecutar`)
# --------------------------------------------------------------------------


class Git:
    def __init__(self, repo: Path):
        self.repo = repo
        self._primera_linea: dict[str, set[str]] = {}
        self._remotas: dict[str, dict[str, dict[str, str]]] = {}

    def __call__(self, *args: str, check: bool = True) -> str:
        r = subprocess.run(["git", "-C", str(self.repo), *args], capture_output=True, text=True)
        if check and r.returncode != 0:
            raise ErrorCosmos(f"git {' '.join(args)}: {r.stderr.strip()}")
        return r.stdout.strip() if r.returncode == 0 else ""

    def resolver(self, ref: str) -> str | None:
        sha = self("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}", check=False)
        return sha or None

    def primera_linea(self, ref: str) -> set[str]:
        if ref not in self._primera_linea:
            salida = self("rev-list", "--first-parent", ref, check=False)
            self._primera_linea[ref] = set(salida.split())
        return self._primera_linea[ref]

    def es_ancestro(self, a: str, b: str) -> bool:
        r = subprocess.run(
            ["git", "-C", str(self.repo), "merge-base", "--is-ancestor", a, b],
            capture_output=True,
        )
        return r.returncode == 0

    def fecha(self, sha: str) -> str:
        # `format:` conserva la zona horaria original del commit.
        return self("log", "-1", "--format=%cd", "--date=format:%Y-%m-%d", sha)

    def etiqueta_local(self, nombre: str) -> dict[str, str] | None:
        fmt = "%(objectname) %(objecttype) %(*objectname)"
        salida = self("for-each-ref", f"refs/tags/{nombre}", f"--format={fmt}")
        if not salida:
            return None
        partes = salida.split()
        objeto, tipo = partes[0], partes[1]
        commit = partes[2] if len(partes) > 2 else objeto
        mensaje = self("tag", "-l", "--format=%(contents)", nombre) if tipo == "tag" else ""
        return {"objeto": objeto, "tipo": tipo, "commit": commit, "mensaje": mensaje}

    def etiquetas_locales(self) -> list[str]:
        return [t for t in self("tag", "-l").split("\n") if t]

    def etiquetas_remotas(self, remoto: str) -> dict[str, dict[str, str]]:
        if remoto not in self._remotas:
            salida = self("ls-remote", "--tags", remoto)
            etiquetas: dict[str, dict[str, str]] = {}
            for linea in filter(None, salida.split("\n")):
                sha, ref = linea.split("\t")
                nombre = ref.removeprefix("refs/tags/")
                if nombre.endswith("^{}"):
                    etiquetas.setdefault(nombre[:-3], {})["commit"] = sha
                else:
                    datos = etiquetas.setdefault(nombre, {})
                    datos["objeto"] = sha
                    datos.setdefault("commit", sha)
            self._remotas[remoto] = etiquetas
        return self._remotas[remoto]

    def rama_remota(self, remoto: str, rama: str) -> str | None:
        salida = self("ls-remote", "--heads", remoto, f"refs/heads/{rama}")
        return salida.split("\t")[0] if salida else None


def gh_release(repo: Path, etiqueta: str | None) -> dict | None:
    """Datos de una GitHub Release (o de la marcada como Latest si etiqueta es None)."""
    if not shutil.which("gh"):
        raise ErrorCosmos("GitHub CLI (gh) no está disponible")
    campos = "tagName,name,url,isDraft,isPrerelease,publishedAt"
    orden = ["gh", "release", "view", *([etiqueta] if etiqueta else []), "--json", campos]
    r = subprocess.run(orden, cwd=repo, capture_output=True, text=True)
    if r.returncode != 0:
        return None
    return json.loads(r.stdout)


# --------------------------------------------------------------------------
# Registro y textos generados
# --------------------------------------------------------------------------


def cargar_registro(ruta: Path) -> dict:
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except FileNotFoundError as e:
        raise ErrorCosmos(f"no existe el registro {ruta}") from e
    except json.JSONDecodeError as e:
        raise ErrorCosmos(f"registro con JSON inválido: {e}") from e


def guardar_registro(ruta: Path, registro: dict) -> None:
    ruta.write_text(json.dumps(registro, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def nombres_catalogo(registro: dict) -> list[str]:
    return [h.get("nombre", "") for h in registro.get("catalogo", [])]


def linea_titulo(v: dict) -> str:
    return f"{v['hito']} {v['version']} — {v['titulo']}"


def es_la_mas_reciente(registro: dict, version: str) -> bool:
    return version == max((v["version"] for v in registro["versiones"]), key=parsear_version)


def _nota_publicacion(v: dict, fecha_publicacion: str) -> str:
    if v.get("retrospectiva"):
        return (
            f"Publicación retrospectiva: la entrega llegó a main el {v['fecha']} "
            f"(commit {v['commit'][:7]}); la etiqueta y la release se crearon el "
            f"{fecha_publicacion}."
        )
    return f"Etiqueta y release creadas el {fecha_publicacion}."


def _secciones(v: dict) -> list[tuple[str, list[str]]]:
    secciones = [
        ("Cambios", v.get("cambios", [])),
        ("Validaciones", v.get("validaciones", [])),
        ("Pendientes y limitaciones conocidos", v.get("pendientes", [])),
    ]
    if v.get("referencias"):
        secciones.append(("Referencias", v["referencias"]))
    return secciones


def mensaje_etiqueta(v: dict, fecha_publicacion: str | None = None) -> str:
    partes = [linea_titulo(v), "", v["descripcion"], ""]
    partes.append(f"Entrega publicada en main el {v['fecha']}: commit {v['commit']}.")
    partes.append(_nota_publicacion(v, fecha_publicacion or hoy()))
    for clave in ("excepcion_version", "excepcion_hito"):
        if v.get(clave):
            partes.append(f"Excepción: {v[clave]}")
    for titulo, elementos in _secciones(v):
        partes += ["", f"{titulo}:"]
        partes += [f"- {e}" for e in elementos] or ["- (ninguno registrado)"]
    return "\n".join(partes) + "\n"


def notas_release(v: dict, fecha_publicacion: str | None = None) -> str:
    partes = [v["descripcion"], ""]
    partes.append(
        f"**Hito:** {v['hito']} · **Versión:** {v['version']} · **Commit:** "
        f"`{v['commit'][:7]}` · **Fecha de la entrega:** {v['fecha']} · "
        f"**Fecha de publicación:** {fecha_publicacion or hoy()}"
    )
    partes += ["", f"> {_nota_publicacion(v, fecha_publicacion or hoy())}"]
    for clave in ("excepcion_version", "excepcion_hito"):
        if v.get(clave):
            partes += ["", f"> **Excepción:** {v[clave]}"]
    for titulo, elementos in _secciones(v):
        partes += ["", f"## {titulo}", ""]
        partes += [f"- {e}" for e in elementos] or ["- (ninguno registrado)"]
    return "\n".join(partes) + "\n"


def estado_hitos(registro: dict) -> dict[str, str]:
    """Estado de cada hito del catálogo según el registro."""
    usos: dict[str, list[str]] = {}
    for v in registro["versiones"]:
        usos.setdefault(v["hito"], []).append(v["version"])
    sin_version = {e["hito"] for e in registro.get("entregas_sin_version", []) if e.get("hito")}
    estados = {}
    for hito in nombres_catalogo(registro):
        if hito in usos:
            estados[hito] = "asignado a " + ", ".join(usos[hito])
        elif hito in sin_version:
            estados[hito] = "usado sin versión"
        else:
            estados[hito] = "disponible"
    return estados


def hitos_disponibles(registro: dict) -> list[dict]:
    estados = estado_hitos(registro)
    return [h for h in registro["catalogo"] if estados[h["nombre"]] == "disponible"]


def generar_bloques(registro: dict) -> dict[str, str]:
    estados = estado_hitos(registro)
    catalogo = ["| N.º | Hito | Descripción | Temática | Estado |", "|---|---|---|---|---|"]
    for i, h in enumerate(registro["catalogo"], 1):
        catalogo.append(
            f"| {i} | {h['nombre']} | {h['descripcion']} | {h['tematica']} "
            f"| {estados[h['nombre']]} |"
        )

    versiones = [
        "| Versión | Hito | Commit | Entrega | Título | Tipo | Estado | Publicación |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for v in registro["versiones"]:
        tipo = "retrospectiva" if v.get("retrospectiva") else "ordinaria"
        pub = v.get("publicacion") or {}
        enlace = f"[{pub['fecha']}]({pub['release_url']})" if pub else "—"
        versiones.append(
            f"| `{v['version']}` | {v['hito']} | `{v['commit'][:7]}` | {v['fecha']} "
            f"| {v['titulo']} | {tipo} | {v['estado']} | {enlace} |"
        )

    sin_version = ["| Commit | Fecha | Hito | Descripción |", "|---|---|---|---|"]
    for e in registro.get("entregas_sin_version", []):
        sin_version.append(
            f"| `{e['commit'][:7]}` | {e['fecha']} | {e.get('hito') or '—'} | {e['descripcion']} |"
        )

    detalle: list[str] = []
    for v in registro["versiones"]:
        detalle += [f"### {linea_titulo(v)}", "", v["descripcion"], ""]
        detalle.append(
            f"Commit `{v['commit']}` · entrega {v['fecha']} · estado **{v['estado']}**"
            + (" · **retrospectiva**" if v.get("retrospectiva") else "")
        )
        pub = v.get("publicacion")
        if pub:
            detalle += [
                "",
                f"Publicada el {pub['fecha']} · etiqueta `{pub['etiqueta_objeto']}` · "
                f"[GitHub Release]({pub['release_url']})",
            ]
        for clave, rotulo in (("excepcion_version", "versión"), ("excepcion_hito", "hito")):
            if v.get(clave):
                detalle += ["", f"Excepción de {rotulo}: {v[clave]}"]
        for titulo, elementos in _secciones(v):
            detalle += ["", f"**{titulo}:**", ""]
            detalle += [f"- {e}" for e in elementos] or ["- (ninguno registrado)"]
        detalle.append("")

    return {
        "catalogo": "\n".join(catalogo),
        "versiones": "\n".join(versiones),
        "sin-version": "\n".join(sin_version),
        "detalle": "\n".join(detalle).rstrip(),
    }


def _patron_bloque(nombre: str) -> re.Pattern:
    return re.compile(
        rf"(<!-- cosmos:{nombre}:inicio -->)(.*?)(<!-- cosmos:{nombre}:fin -->)", re.S
    )


def leer_bloques(texto: str) -> dict[str, str | None]:
    resultado: dict[str, str | None] = {}
    for nombre in BLOQUES:
        m = _patron_bloque(nombre).search(texto)
        resultado[nombre] = m.group(2).removeprefix("\n").removesuffix("\n") if m else None
    return resultado


def reescribir_bloques(texto: str, bloques: dict[str, str]) -> str:
    for nombre, contenido in bloques.items():
        patron = _patron_bloque(nombre)
        if not patron.search(texto):
            raise ErrorCosmos(
                f"falta el bloque <!-- cosmos:{nombre}:inicio/fin --> en el documento"
            )
        texto = patron.sub(lambda m: f"{m.group(1)}\n{contenido}\n{m.group(3)}", texto)
    return texto


# --------------------------------------------------------------------------
# Verificación
# --------------------------------------------------------------------------


@dataclass
class Resultado:
    errores: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)

    def error(self, texto: str) -> None:
        self.errores.append(texto)

    def aviso(self, texto: str) -> None:
        self.avisos.append(texto)


@dataclass
class Contexto:
    repo: Path
    registro_ruta: Path
    doc_ruta: Path
    remoto_activo: bool = True
    releases_activas: bool = False

    def __post_init__(self) -> None:
        self.git = Git(self.repo)
        self.registro = cargar_registro(self.registro_ruta)

    @property
    def rama(self) -> str:
        return self.registro.get("rama_principal", "main")

    @property
    def remoto(self) -> str:
        return self.registro.get("remoto", "origin")


def verificar_etiqueta(ctx: Contexto, v: dict, res: Resultado) -> None:
    nombre = v["version"]
    local = ctx.git.etiqueta_local(nombre)
    remota = ctx.git.etiquetas_remotas(ctx.remoto).get(nombre) if ctx.remoto_activo else None
    if local:
        if local["tipo"] != "tag":
            res.error(f"{nombre}: la etiqueta local es ligera; debe ser anotada")
        if local["commit"] != v["commit"]:
            res.error(
                f"{nombre}: la etiqueta local apunta a {local['commit'][:7]}, "
                f"el registro dice {v['commit'][:7]}"
            )
        primera = local["mensaje"].split("\n", 1)[0].strip()
        if local["tipo"] == "tag" and primera != linea_titulo(v):
            res.error(
                f"{nombre}: la primera línea del mensaje es '{primera}', "
                f"se esperaba '{linea_titulo(v)}'"
            )
    if remota:
        if remota["commit"] != v["commit"]:
            res.error(
                f"{nombre}: la etiqueta remota apunta a {remota['commit'][:7]}, "
                f"el registro dice {v['commit'][:7]}"
            )
        if local and remota["objeto"] != local["objeto"]:
            res.error(f"{nombre}: la etiqueta local y la remota son objetos distintos")
    if v["estado"] == "publicada":
        pub = v.get("publicacion") or {}
        if not all(pub.get(c) for c in ("fecha", "etiqueta_objeto", "release_url")):
            res.error(f"{nombre}: 'publicada' sin datos de publicación (fecha, objeto, release)")
        elif local and pub["etiqueta_objeto"] != local["objeto"]:
            res.error(f"{nombre}: el objeto de etiqueta registrado no coincide con el local")
        if not local:
            res.error(f"{nombre}: 'publicada' pero no existe la etiqueta local (git fetch --tags)")
        if ctx.remoto_activo and not remota:
            res.error(f"{nombre}: estado 'publicada' pero no existe la etiqueta en '{ctx.remoto}'")
        if not ctx.remoto_activo:
            res.aviso(f"{nombre}: etiqueta remota no comprobada (--sin-remoto)")
    elif local or remota:
        res.aviso(f"{nombre}: la etiqueta ya existe; actualiza el registro con 'marcar-publicada'")


def verificar_release(ctx: Contexto, v: dict, res: Resultado) -> None:
    datos = gh_release(ctx.repo, v["version"])
    if not datos:
        res.error(f"{v['version']}: no existe la GitHub Release")
        return
    if datos.get("tagName") != v["version"]:
        res.error(f"{v['version']}: la release usa la etiqueta {datos.get('tagName')}")
    if datos.get("name") != linea_titulo(v):
        res.error(f"{v['version']}: título de la release '{datos.get('name')}' incorrecto")
    if datos.get("isDraft"):
        res.error(f"{v['version']}: la release es un borrador")
    pub = v.get("publicacion") or {}
    if pub.get("release_url") and datos.get("url") != pub["release_url"]:
        res.error(f"{v['version']}: la URL de la release no coincide con el registro")


def verificar(ctx: Contexto) -> Resultado:
    res = Resultado()
    reg, git = ctx.registro, ctx.git
    catalogo = nombres_catalogo(reg)
    if not catalogo or len(set(catalogo)) != len(catalogo):
        res.error("el catálogo está vacío o tiene hitos repetidos")
    for h in reg.get("catalogo", []):
        nombre = h.get("nombre", "")
        if not nombre or nombre != nombre.upper() or not nombre.isalpha():
            res.error(f"catálogo: '{nombre}' debe ir en mayúsculas y sin espacios")
        if not h.get("descripcion") or not h.get("tematica"):
            res.error(f"catálogo: {nombre} sin descripción o temática")
    if not git.resolver(ctx.rama):
        res.error(f"no existe la rama principal '{ctx.rama}'")
        return res
    primera = git.primera_linea(ctx.rama)

    estable = reg.get("primera_version_estable")
    vistos: set[str] = set()
    hitos_usados = {e["hito"] for e in reg.get("entregas_sin_version", []) if e.get("hito")}
    anterior: dict | None = None
    for v in reg.get("versiones", []):
        nombre = v.get("version", "?")
        for clave in ("version", "hito", "commit", "fecha", "titulo", "descripcion", "estado"):
            if not v.get(clave):
                res.error(f"{nombre}: falta el campo '{clave}'")
        if not all(v.get(c) for c in ("version", "hito", "commit")):
            continue
        try:
            mayor, _, _ = parsear_version(nombre)
        except ValueError as e:
            res.error(str(e))
            continue
        if nombre in vistos:
            res.error(f"{nombre}: versión duplicada en el registro")
        vistos.add(nombre)
        if v["estado"] not in ESTADOS:
            res.error(f"{nombre}: estado '{v['estado']}' no válido ({', '.join(ESTADOS)})")
        if not v.get("validaciones"):
            res.error(f"{nombre}: sin validaciones registradas")
        if v["hito"] not in catalogo:
            res.error(f"{nombre}: el hito '{v['hito']}' no está en el catálogo oficial")
        elif v["hito"] in hitos_usados and not v.get("excepcion_hito"):
            res.error(f"{nombre}: el hito {v['hito']} ya estaba asignado")
        sha = git.resolver(v["commit"])
        if not sha:
            res.error(f"{nombre}: el commit {v['commit']} no existe")
        else:
            if sha != v["commit"]:
                res.error(f"{nombre}: el commit debe registrarse con su SHA completo ({sha})")
            if sha not in primera:
                res.error(
                    f"{nombre}: {sha[:7]} no pertenece a la historia principal "
                    f"(first-parent) de {ctx.rama}"
                )
            if git.fecha(sha) != v["fecha"]:
                res.error(
                    f"{nombre}: fecha {v['fecha']} distinta de la del commit ({git.fecha(sha)})"
                )
        if mayor >= 1:
            if not estable or not estable.get("decision"):
                res.error(f"{nombre}: versión >= 1.0.0 sin primera versión estable declarada")
            elif parsear_version(estable["version"]) > parsear_version(nombre):
                res.error(f"{nombre}: anterior a la primera versión estable declarada")
        if anterior:
            if not es_incremento_valido(anterior["version"], nombre):
                res.error(f"{nombre}: no es un incremento SemVer válido de {anterior['version']}")
            if (
                sha
                and git.resolver(anterior["commit"])
                and not git.es_ancestro(anterior["commit"], sha)
            ):
                res.error(f"{nombre}: su commit no desciende del de {anterior['version']}")
        hitos_usados.add(v["hito"])
        verificar_etiqueta(ctx, v, res)
        if ctx.releases_activas and v["estado"] == "publicada":
            verificar_release(ctx, v, res)
        anterior = v
    if estable and estable.get("version") not in vistos:
        res.error("primera_version_estable apunta a una versión no registrada")

    if ctx.releases_activas:
        publicadas = [v["version"] for v in reg["versiones"] if v["estado"] == "publicada"]
        if publicadas:
            ultima = gh_release(ctx.repo, None)
            esperada = max(publicadas, key=parsear_version)
            if not ultima or ultima.get("tagName") != esperada:
                res.error(
                    f"la release marcada como Latest es "
                    f"{(ultima or {}).get('tagName')}, se esperaba {esperada}"
                )

    for e in reg.get("entregas_sin_version", []):
        sha = git.resolver(e.get("commit", ""))
        if not sha or sha not in primera:
            res.error(
                f"entrega sin versión {e.get('commit', '?')[:7]}: commit inexistente "
                f"o fuera de {ctx.rama}"
            )
        if e.get("hito") and e["hito"] not in catalogo:
            res.error(
                f"entrega sin versión {e['commit'][:7]}: hito '{e['hito']}' fuera del catálogo"
            )

    for etiqueta in git.etiquetas_locales():
        if SEMVER.match(etiqueta) and etiqueta not in vistos:
            res.error(f"la etiqueta local {etiqueta} no está en el registro")
        elif not SEMVER.match(etiqueta):
            res.aviso(f"la etiqueta local '{etiqueta}' no sigue el formato vX.Y.Z")
    if ctx.remoto_activo:
        for etiqueta in git.etiquetas_remotas(ctx.remoto):
            if SEMVER.match(etiqueta) and etiqueta not in vistos:
                res.error(f"la etiqueta remota {etiqueta} no está en el registro")

    try:
        texto = ctx.doc_ruta.read_text(encoding="utf-8")
    except FileNotFoundError:
        res.error(f"no existe {ctx.doc_ruta}")
    else:
        actuales, esperados = leer_bloques(texto), generar_bloques(reg)
        for nombre in BLOQUES:
            if actuales[nombre] is None:
                res.error(f"documento: falta el bloque generado '{nombre}'")
            elif actuales[nombre] != esperados[nombre]:
                res.error(
                    f"documento: el bloque '{nombre}' no coincide con el registro "
                    f"(ejecuta 'documentar')"
                )
    return res


# --------------------------------------------------------------------------
# Propuesta de la siguiente versión
# --------------------------------------------------------------------------


def clasificar_cambios(asuntos: list[str], cuerpos: str, archivos: list[str]) -> str:
    """Devuelve 'ninguno', 'documental', 'major', 'minor' o 'patch'."""
    if not archivos:
        return "ninguno"
    no_documentales = [
        a for a in archivos if not a.startswith(PREFIJOS_DOCUMENTALES) and not a.endswith(".md")
    ]
    if not no_documentales:
        return "documental"
    if "BREAKING CHANGE" in cuerpos or any(re.match(r"^\w+(\(.*\))?!:", a) for a in asuntos):
        return "major"
    if any(re.match(r"^feat(\(.*\))?:", a) for a in asuntos):
        return "minor"
    return "patch"


def proponer(ctx: Contexto, destino: str, hito: str | None, incremento: str | None) -> int:
    reg, git = ctx.registro, ctx.git
    if not reg["versiones"]:
        raise ErrorCosmos("el registro no tiene ninguna versión de referencia")
    ultima = max(reg["versiones"], key=lambda v: parsear_version(v["version"]))
    sha = git.resolver(destino)
    if not sha:
        raise ErrorCosmos(f"no existe '{destino}'")
    print(
        f"Última versión registrada: {linea_titulo(ultima)} "
        f"({ultima['commit'][:7]}, {ultima['estado']})"
    )
    print(f"Destino: {destino} = {sha[:7]}")
    problemas: list[str] = []
    if sha not in git.primera_linea(ctx.rama):
        problemas.append(f"{sha[:7]} no pertenece a la historia principal de {ctx.rama}")
    if not git.es_ancestro(ultima["commit"], sha):
        problemas.append(f"{sha[:7]} no desciende de {ultima['version']}")

    rango = f"{ultima['commit']}..{sha}"
    archivos = [a for a in git("diff", "--name-only", ultima["commit"], sha).split("\n") if a]
    asuntos = [a for a in git("log", "--no-merges", "--format=%s", rango).split("\n") if a]
    cuerpos = git("log", "--no-merges", "--format=%b", rango)
    integraciones = git("log", "--first-parent", "--format=%h %cd %s", "--date=short", rango)
    print("\n1. Cambios integrados en la línea principal desde la última versión:")
    lineas = [f"   {linea}" for linea in integraciones.split("\n") if linea]
    print("\n".join(lineas) or "   (ninguno)")

    tipo = clasificar_cambios(asuntos, cuerpos, archivos)
    estable = bool(reg.get("primera_version_estable"))
    if tipo == "ninguno":
        print("\n2. No hay cambios desde la última versión: no corresponde versión nueva.")
        return 0
    if tipo == "documental":
        print("\n2. Solo hay cambios documentales o de herramientas: no genera versión (DK-005).")
        return 0
    sugerido, nota = tipo, ""
    if tipo == "major" and not estable:
        sugerido = "minor"
        nota = " (cambio incompatible en 0.x: MINOR hasta declarar la versión estable)"
    elegido = incremento or sugerido
    if elegido == "major" and not estable:
        problemas.append("MAJOR (v1.0.0) requiere declarar antes la primera versión estable")
    version = incrementar(ultima["version"], elegido)
    print(f"\n2. Incremento SemVer sugerido: {sugerido.upper()}{nota}")
    if incremento:
        print(f"   Incremento elegido: {elegido.upper()}")
    print(f"   Versión: {version}")

    disponibles = hitos_disponibles(reg)
    estados = estado_hitos(reg)
    if not disponibles:
        problemas.append("catálogo agotado: el equipo debe ampliarlo con una decisión registrada")
    if hito:
        if hito not in estados:
            problemas.append(f"el hito {hito} no está en el catálogo")
        elif estados[hito] != "disponible":
            problemas.append(f"el hito {hito} no está disponible ({estados[hito]})")
        print(f"\n3. Hito elegido: {hito}")
    else:
        print("\n3. Hito: elígelo según el propósito dominante de la entrega. Disponibles:")
        for h in disponibles:
            print(f"   - {h['nombre']}: {h['tematica']}")

    if any(v["version"] == version for v in reg["versiones"]):
        problemas.append(f"{version} ya está en el registro")
    if git.etiqueta_local(version):
        problemas.append(f"la etiqueta {version} ya existe localmente")
    if ctx.remoto_activo and version in git.etiquetas_remotas(ctx.remoto):
        problemas.append(f"la etiqueta {version} ya existe en {ctx.remoto}")
    print("\n4-5. Comprobaciones:", "correctas" if not problemas else "")
    for p in problemas:
        print(f"   ✗ {p}")
    print(
        "\nSiguientes pasos: 6) ejecutar y anotar las pruebas; 7) pedir autorización "
        "explícita; 8) 'registrar' y commit del registro; 9-10) 'publicar' (simulación "
        "y, con autorización, --ejecutar --confirmar); 11) 'marcar-publicada' y commit."
    )
    return 1 if problemas else 0


# --------------------------------------------------------------------------
# Publicación asistida
# --------------------------------------------------------------------------


def repo_github(url: str) -> tuple[str, str] | None:
    m = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(\.git)?$", url)
    return (m.group(1), m.group(2)) if m else None


def crear_release_api(propietario: str, nombre: str, token: str, datos: dict) -> str:
    peticion = urllib.request.Request(
        f"https://api.github.com/repos/{propietario}/{nombre}/releases",
        data=json.dumps(datos).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "cosmos-release-script",
        },
        method="POST",
    )
    with urllib.request.urlopen(peticion, timeout=30) as respuesta:
        return json.load(respuesta).get("html_url", "")


def registrada_en_commit(ctx: Contexto, v: dict) -> bool | None:
    """¿La entrada del registro está igual en HEAD? None si el registro está fuera del repo."""
    try:
        relativa = ctx.registro_ruta.resolve().relative_to(ctx.repo.resolve())
    except ValueError:
        return None
    contenido = ctx.git("show", f"HEAD:{relativa.as_posix()}", check=False)
    if not contenido:
        return False
    confirmado = json.loads(contenido)
    previa = next(
        (x for x in confirmado.get("versiones", []) if x["version"] == v["version"]), None
    )
    return previa == v


def publicar(
    ctx: Contexto, version: str, ejecutar: bool, confirmar: str | None, sin_release: bool
) -> int:
    if not ctx.remoto_activo:
        raise ErrorCosmos("publicar siempre comprueba el remoto; no admite --sin-remoto")
    v = next((x for x in ctx.registro["versiones"] if x["version"] == version), None)
    if not v:
        raise ErrorCosmos(f"{version} no está en el registro (usa 'registrar' primero)")
    git = ctx.git
    res = verificar(ctx)
    bloqueos = list(res.errores)
    if v["estado"] != "preparada":
        bloqueos.append(f"{version} está en estado '{v['estado']}', no 'preparada'")
    if registrada_en_commit(ctx, v) is False:
        bloqueos.append(f"la asignación de {version} no está confirmada en un commit del registro")
    if git.etiqueta_local(version):
        bloqueos.append(f"la etiqueta {version} ya existe localmente (no se mueve ni se reemplaza)")
    if version in git.etiquetas_remotas(ctx.remoto):
        bloqueos.append(f"la etiqueta {version} ya existe en {ctx.remoto} (no se reemplaza)")
    remota = git.rama_remota(ctx.remoto, ctx.rama)
    if not remota:
        bloqueos.append(f"no existe {ctx.remoto}/{ctx.rama}")
    elif not git.resolver(remota):
        bloqueos.append(f"{ctx.remoto}/{ctx.rama} ({remota[:7]}) no está en local: git fetch")
    elif v["commit"] not in git.primera_linea(remota):
        bloqueos.append(
            f"{v['commit'][:7]} no pertenece a la historia principal publicada de "
            f"{ctx.remoto}/{ctx.rama}"
        )
    latest = es_la_mas_reciente(ctx.registro, version)
    hay_gh = bool(shutil.which("gh"))
    if not sin_release and hay_gh and gh_release(ctx.repo, version):
        bloqueos.append(f"ya existe una GitHub Release para {version}")

    print(f"Publicación de {linea_titulo(v)}")
    print(
        f"Commit de destino: {v['commit']} ({v['fecha']})"
        + (" · retrospectiva" if v.get("retrospectiva") else "")
    )
    print("\nComandos previstos:")
    print(f"  git tag -a {version} -F <mensaje> {v['commit']}")
    print(f"  git push {ctx.remoto} refs/tags/{version}")
    if not sin_release:
        print(
            f"  gh release create {version} --verify-tag --title '{linea_titulo(v)}' "
            f"--notes-file <notas> --latest={'true' if latest else 'false'}"
        )
    print("\nMensaje de la etiqueta:")
    print("\n".join(f"  | {linea}" for linea in mensaje_etiqueta(v).rstrip().split("\n")))

    if bloqueos:
        print("\nBLOQUEADO; no se ha creado ni publicado nada:")
        for b in bloqueos:
            print(f"  ✗ {b}")
        return 1
    if not ejecutar:
        print("\nSIMULACIÓN superada: no se ha creado ni publicado nada.")
        print(f"Para ejecutar, con autorización: --ejecutar --confirmar {version}")
        return 0
    if confirmar != version:
        print(f"\nRECHAZADO: --confirmar debe ser exactamente {version}. No se ha hecho nada.")
        return 2

    with tempfile.TemporaryDirectory() as tmp:
        ruta_msg = Path(tmp) / "mensaje.txt"
        ruta_msg.write_text(mensaje_etiqueta(v), encoding="utf-8")
        git("tag", "-a", version, "-F", str(ruta_msg), v["commit"])
        print(f"\n✓ Etiqueta anotada {version} creada sobre {v['commit'][:7]}")
        git("push", ctx.remoto, f"refs/tags/{version}")
        git._remotas.clear()
        remota_tag = git.etiquetas_remotas(ctx.remoto).get(version)
        if not remota_tag or remota_tag["commit"] != v["commit"]:
            raise ErrorCosmos(f"la etiqueta remota {version} no se verificó tras el push")
        print(f"✓ Etiqueta publicada en {ctx.remoto} y verificada")

        if sin_release:
            print("Release omitida (--sin-release).")
        else:
            ruta_notas = Path(tmp) / "notas.md"
            ruta_notas.write_text(notas_release(v), encoding="utf-8")
            destino = repo_github(git("remote", "get-url", ctx.remoto))
            if hay_gh:
                subprocess.run(
                    [
                        "gh",
                        "release",
                        "create",
                        version,
                        "--verify-tag",
                        "--title",
                        linea_titulo(v),
                        "--notes-file",
                        str(ruta_notas),
                        f"--latest={'true' if latest else 'false'}",
                    ],
                    cwd=ctx.repo,
                    check=True,
                )
                print("✓ GitHub Release creada con gh")
            elif destino and os.environ.get("GITHUB_TOKEN"):
                datos = {
                    "tag_name": version,
                    "name": linea_titulo(v),
                    "body": notas_release(v),
                    "draft": False,
                    "prerelease": False,
                    "make_latest": "true" if latest else "false",
                }
                try:
                    enlace = crear_release_api(*destino, os.environ["GITHUB_TOKEN"], datos)
                except urllib.error.URLError as e:
                    raise ErrorCosmos(f"no se pudo crear la release: {e}") from e
                print(f"✓ GitHub Release creada: {enlace}")
            else:
                print("! Sin 'gh' ni GITHUB_TOKEN: crea la release con este título y notas:")
                print(f"  Título: {linea_titulo(v)}\n" + notas_release(v))
    print(f"\nPaso 11: 'marcar-publicada {version}' y commit del registro.")
    return 0


def marcar_publicada(ctx: Contexto, version: str) -> int:
    if not ctx.remoto_activo:
        raise ErrorCosmos("marcar-publicada exige comprobar el remoto")
    v = next((x for x in ctx.registro["versiones"] if x["version"] == version), None)
    if not v:
        raise ErrorCosmos(f"{version} no está en el registro")
    local = ctx.git.etiqueta_local(version)
    release = gh_release(ctx.repo, version)
    problemas = []
    if not local:
        problemas.append(f"no existe la etiqueta local {version}")
    if not release:
        problemas.append(f"no existe la GitHub Release {version}")
    if problemas:
        print("No se marca como publicada:\n" + "\n".join(f"  ✗ {p}" for p in problemas))
        return 1
    copia = dict(v)
    v["estado"] = "publicada"
    v["publicacion"] = {
        "fecha": (release.get("publishedAt") or "")[:10],
        "etiqueta_objeto": local["objeto"],
        "release_url": release.get("url", ""),
    }
    res = Resultado()
    verificar_etiqueta(ctx, v, res)
    verificar_release(ctx, v, res)
    if res.errores:
        v.clear()
        v.update(copia)
        print("No se marca como publicada:\n" + "\n".join(f"  ✗ {e}" for e in res.errores))
        return 1
    guardar_registro(ctx.registro_ruta, ctx.registro)
    documentar(ctx)
    print(f"✓ {version} marcada como publicada ({v['publicacion']['release_url']}).")
    return 0


def documentar(ctx: Contexto) -> None:
    texto = ctx.doc_ruta.read_text(encoding="utf-8")
    nuevo = reescribir_bloques(texto, generar_bloques(ctx.registro))
    ctx.doc_ruta.write_text(nuevo, encoding="utf-8")


def registrar(ctx: Contexto, a: argparse.Namespace) -> int:
    sha = ctx.git.resolver(a.commit)
    if not sha:
        raise ErrorCosmos(f"no existe el commit {a.commit}")
    nueva = {
        "version": a.version,
        "hito": a.hito,
        "commit": sha,
        "fecha": ctx.git.fecha(sha),
        "titulo": a.titulo,
        "descripcion": a.descripcion,
        "retrospectiva": a.retrospectiva,
        "estado": "preparada",
        "cambios": a.cambio or [],
        "validaciones": a.validacion or [],
        "pendientes": a.pendiente or [],
        "referencias": a.referencia or [],
    }
    ctx.registro["versiones"].append(nueva)
    original = ctx.doc_ruta.read_text(encoding="utf-8")
    ctx.doc_ruta.write_text(
        reescribir_bloques(original, generar_bloques(ctx.registro)), encoding="utf-8"
    )
    res = verificar(ctx)
    if res.errores:
        ctx.doc_ruta.write_text(original, encoding="utf-8")
        print("No se registra:\n" + "\n".join(f"  ✗ {e}" for e in res.errores))
        return 1
    guardar_registro(ctx.registro_ruta, ctx.registro)
    print(f"✓ {linea_titulo(nueva)} registrada como 'preparada' sobre {sha[:7]}.")
    return 0


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def construir_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="cosmos", description=__doc__.split("\n")[0])
    p.add_argument("--repo", help="raíz del repositorio (por defecto, la del directorio actual)")
    p.add_argument("--registro", help=f"ruta del registro (por defecto {RUTA_REGISTRO})")
    p.add_argument("--doc", help=f"documento con bloques generados (por defecto {RUTA_DOC})")
    p.add_argument("--sin-remoto", action="store_true", help="no consultar el remoto")
    sub = p.add_subparsers(dest="orden", required=True)
    ve = sub.add_parser("verificar")
    ve.add_argument("--releases", action="store_true", help="comprobar también las GitHub Releases")
    pr = sub.add_parser("proponer")
    pr.add_argument(
        "--destino", default=None, help="commit candidato (por defecto, la rama principal)"
    )
    pr.add_argument("--hito")
    pr.add_argument("--incremento", choices=("major", "minor", "patch"))
    no = sub.add_parser("notas")
    no.add_argument("version")
    no.add_argument("--formato", choices=("release", "etiqueta"), default="release")
    sub.add_parser("documentar")
    re_ = sub.add_parser("registrar")
    re_.add_argument("--version", required=True)
    re_.add_argument("--hito", required=True)
    re_.add_argument("--commit", required=True)
    re_.add_argument("--titulo", required=True)
    re_.add_argument("--descripcion", required=True)
    re_.add_argument("--retrospectiva", action="store_true")
    for opcion in ("cambio", "validacion", "pendiente", "referencia"):
        re_.add_argument(f"--{opcion}", action="append")
    pu = sub.add_parser("publicar")
    pu.add_argument("version")
    pu.add_argument(
        "--ejecutar", action="store_true", help="crear y publicar (requiere --confirmar)"
    )
    pu.add_argument("--confirmar", help="repetir la versión exacta para autorizar la ejecución")
    pu.add_argument("--sin-release", action="store_true")
    mp = sub.add_parser("marcar-publicada")
    mp.add_argument("version")
    return p


def main(argv: list[str] | None = None) -> int:
    a = construir_parser().parse_args(argv)
    try:
        if a.repo:
            repo = Path(a.repo).resolve()
        else:
            salida = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
            )
            if salida.returncode != 0:
                raise ErrorCosmos("no estás dentro de un repositorio Git (usa --repo)")
            repo = Path(salida.stdout.strip())
        ctx = Contexto(
            repo=repo,
            registro_ruta=Path(a.registro) if a.registro else repo / RUTA_REGISTRO,
            doc_ruta=Path(a.doc) if a.doc else repo / RUTA_DOC,
            remoto_activo=not a.sin_remoto,
            releases_activas=getattr(a, "releases", False),
        )
        if a.orden == "verificar":
            res = verificar(ctx)
            for aviso in res.avisos:
                print(f"! {aviso}")
            for error in res.errores:
                print(f"✗ {error}")
            n = len(ctx.registro["versiones"])
            estado = "✓ COSMOS coherente" if not res.errores else "✗ COSMOS incoherente"
            print(f"{estado}: {n} versiones, {len(res.errores)} errores, {len(res.avisos)} avisos")
            return 1 if res.errores else 0
        if a.orden == "proponer":
            return proponer(ctx, a.destino or ctx.rama, a.hito, a.incremento)
        if a.orden == "notas":
            v = next((x for x in ctx.registro["versiones"] if x["version"] == a.version), None)
            if not v:
                raise ErrorCosmos(f"{a.version} no está en el registro")
            if a.formato == "etiqueta":
                print(mensaje_etiqueta(v), end="")
            else:
                print(f"# {linea_titulo(v)}\n\n{notas_release(v)}", end="")
            return 0
        if a.orden == "documentar":
            documentar(ctx)
            print(f"✓ Bloques regenerados en {ctx.doc_ruta}")
            return 0
        if a.orden == "registrar":
            return registrar(ctx, a)
        if a.orden == "publicar":
            return publicar(ctx, a.version, a.ejecutar, a.confirmar, a.sin_release)
        if a.orden == "marcar-publicada":
            return marcar_publicada(ctx, a.version)
    except ErrorCosmos as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    sys.exit(main())
