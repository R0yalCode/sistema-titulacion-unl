"""Pruebas de scripts/cosmos/cosmos.py sobre repositorios Git temporales.

Ejecutar: python3 -m unittest discover -s scripts/cosmos -p 'test_*.py'
No usan red, GitHub ni el repositorio real: cada prueba crea su propio
repositorio, un remoto local desnudo y un `gh` falso que guarda las releases
en un directorio temporal.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import cosmos  # noqa: E402

CATALOGO = [
    {"nombre": n, "descripcion": f"Astro {n}", "tematica": f"Temática {n}"}
    for n in ("ORION", "ANDROMEDA", "ECLIPSE", "HELIOS", "TRAPPIST")
]
DOC = """# Versionado

<!-- cosmos:catalogo:inicio -->
<!-- cosmos:catalogo:fin -->
<!-- cosmos:versiones:inicio -->
<!-- cosmos:versiones:fin -->
<!-- cosmos:sin-version:inicio -->
<!-- cosmos:sin-version:fin -->
<!-- cosmos:detalle:inicio -->
<!-- cosmos:detalle:fin -->
"""
GH_FALSO = r"""#!/usr/bin/env python3
import json, os, pathlib, sys
d = pathlib.Path(os.environ["FAKE_GH_DIR"])
estado = d / "releases.json"
rel = json.loads(estado.read_text()) if estado.exists() else {}
a = sys.argv[1:]
with (d / "llamadas.log").open("a") as f:
    f.write(json.dumps(a) + "\n")
if a[:2] == ["release", "create"]:
    tag = a[2]
    titulo = a[a.index("--title") + 1]
    latest = [x for x in a if x.startswith("--latest=")][0].endswith("true")
    if tag in rel:
        sys.exit(1)
    if latest:
        for r in rel.values():
            r["latest"] = False
    rel[tag] = {"tagName": tag, "name": titulo, "isDraft": False,
                "url": "https://example.invalid/releases/tag/" + tag,
                "isPrerelease": False, "publishedAt": "2026-11-12T12:00:00Z",
                "latest": latest}
    estado.write_text(json.dumps(rel))
    print(rel[tag]["url"])
    sys.exit(0)
if a[:2] == ["release", "view"]:
    tag = a[2] if len(a) > 2 and not a[2].startswith("--") else None
    if tag is None:
        r = next((r for r in rel.values() if r["latest"]), None)
    else:
        r = rel.get(tag)
    if r is None:
        sys.exit(1)
    print(json.dumps({k: v for k, v in r.items() if k != "latest"}))
    sys.exit(0)
sys.exit(2)
"""


class RepoTemporal:
    """main con merges --no-ff (historia first-parent) y un remoto desnudo."""

    def __init__(self, base: Path):
        self.dir = base / "repo"
        self.remoto = base / "remoto.git"
        self.env = {
            **os.environ,
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": str(base / "gitconfig"),
            "GIT_AUTHOR_NAME": "Prueba",
            "GIT_AUTHOR_EMAIL": "prueba@example.invalid",
            "GIT_COMMITTER_NAME": "Prueba",
            "GIT_COMMITTER_EMAIL": "prueba@example.invalid",
        }
        (base / "gitconfig").write_text("[tag]\n\tgpgSign = false\n[commit]\n\tgpgSign = false\n")
        self.git_base("init", "-q", "--bare", "-b", "main", str(self.remoto), cwd=base)
        self.git_base("init", "-q", "-b", "main", str(self.dir), cwd=base)
        self.git("remote", "add", "origin", str(self.remoto))
        self.commit("inicio.txt", "chore: inicio", "2026-10-20T10:00:00-05:00")
        self.lateral: dict[str, str] = {}

    def git_base(self, *args, cwd, fecha=None):
        env = dict(self.env)
        if fecha:
            env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = fecha
        r = subprocess.run(["git", *args], cwd=cwd, env=env, capture_output=True, text=True)
        if r.returncode:
            raise RuntimeError(r.stderr)
        return r.stdout.strip()

    def git(self, *args, fecha=None):
        return self.git_base(*args, cwd=self.dir, fecha=fecha)

    def commit(self, archivo, mensaje, fecha):
        ruta = self.dir / archivo
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(f"{mensaje}\n{fecha}\n")
        self.git("add", "--", archivo)
        self.git("commit", "-q", "-m", mensaje, fecha=fecha)
        return self.git("rev-parse", "HEAD")

    def entrega(self, nombre, archivo, mensaje, fecha):
        """Rama lateral con un commit, integrada con merge --no-ff."""
        self.git("switch", "-q", "-c", nombre)
        lateral = self.commit(archivo, mensaje, fecha)
        self.git("switch", "-q", "main")
        self.git("merge", "-q", "--no-ff", nombre, "-m", f"Merge {nombre}", fecha=fecha)
        self.lateral[nombre] = lateral
        return self.git("rev-parse", "HEAD")

    def publicar_main(self):
        self.git("push", "-q", "origin", "main")
        self.git("fetch", "-q", "origin")


def version(v, hito, commit, fecha, **extra):
    datos = {
        "version": v,
        "hito": hito,
        "commit": commit,
        "fecha": fecha,
        "titulo": f"Entrega {v}",
        "descripcion": f"Descripción de {v}",
        "retrospectiva": False,
        "estado": "preparada",
        "cambios": ["cambio"],
        "validaciones": ["pruebas superadas"],
        "pendientes": [],
    }
    datos.update(extra)
    return datos


class BaseCosmos(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        base = Path(self._tmp.name)
        self.base = base
        bin_dir, self.gh_dir = base / "bin", base / "gh"
        bin_dir.mkdir()
        self.gh_dir.mkdir()
        (bin_dir / "gh").write_text(GH_FALSO)
        (bin_dir / "gh").chmod(0o755)
        entorno = {
            "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
            "FAKE_GH_DIR": str(self.gh_dir),
            "COSMOS_FECHA_HOY": "2026-11-12",
        }
        parche = mock.patch.dict(os.environ, entorno)
        parche.start()
        self.addCleanup(parche.stop)
        os.environ.pop("GITHUB_TOKEN", None)
        self.r = RepoTemporal(base)
        self.c1 = self.r.entrega("f1", "src/a.py", "feat: uno", "2026-11-05T09:00:00-05:00")
        self.c2 = self.r.entrega("f2", "src/b.py", "feat: dos", "2026-11-06T20:00:00-05:00")
        self.c3 = self.r.entrega("f3", "src/c.py", "fix: tres", "2026-11-10T08:00:00-05:00")
        self.r.publicar_main()
        self.registro_ruta = base / "registro.json"
        self.doc_ruta = base / "doc.md"
        self.registro = {
            "esquema": 1,
            "rama_principal": "main",
            "remoto": "origin",
            "primera_version_estable": None,
            "catalogo": [dict(h) for h in CATALOGO],
            "entregas_sin_version": [],
            "versiones": [
                version("v0.2.0", "ANDROMEDA", self.c1, "2026-11-05", retrospectiva=True),
                version("v0.3.0", "ECLIPSE", self.c2, "2026-11-06"),
            ],
        }
        self.guardar()

    def tearDown(self):
        self._tmp.cleanup()

    def guardar(self, documentar=True):
        cosmos.guardar_registro(self.registro_ruta, self.registro)
        self.doc_ruta.write_text(DOC)
        if documentar:
            cosmos.documentar(self.ctx())

    def ctx(self, remoto=True, releases=False):
        return cosmos.Contexto(
            repo=self.r.dir,
            registro_ruta=self.registro_ruta,
            doc_ruta=self.doc_ruta,
            remoto_activo=remoto,
            releases_activas=releases,
        )

    def ejecutar(self, *argv):
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(salida):
            codigo = cosmos.main(
                [
                    "--repo",
                    str(self.r.dir),
                    "--registro",
                    str(self.registro_ruta),
                    "--doc",
                    str(self.doc_ruta),
                    *argv,
                ]
            )
        return codigo, salida.getvalue()

    def errores(self, remoto=True, releases=False):
        return cosmos.verificar(self.ctx(remoto, releases)).errores

    def assertError(self, fragmento, remoto=True, releases=False):
        errores = self.errores(remoto, releases)
        self.assertTrue(any(fragmento in e for e in errores), f"'{fragmento}' no está en {errores}")

    def releases_falsas(self):
        ruta = self.gh_dir / "releases.json"
        return json.loads(ruta.read_text()) if ruta.exists() else {}


class TestSemVer(unittest.TestCase):
    def test_formatos(self):
        self.assertEqual(cosmos.parsear_version("v0.5.0"), (0, 5, 0))
        for malo in ("V0.5.0", "0.5.0", "v0.5", "v0.5.0-helios", "v0.5.0+helios", "v01.2.3"):
            with self.assertRaises(ValueError, msg=malo):
                cosmos.parsear_version(malo)

    def test_incrementos(self):
        self.assertEqual(cosmos.incrementar("v0.4.0", "minor"), "v0.5.0")
        self.assertEqual(cosmos.incrementar("v0.5.0", "patch"), "v0.5.1")
        self.assertEqual(cosmos.incrementar("v0.5.3", "major"), "v1.0.0")
        self.assertTrue(cosmos.es_incremento_valido("v0.4.0", "v0.5.0"))
        self.assertFalse(cosmos.es_incremento_valido("v0.2.0", "v0.4.0"))
        self.assertFalse(cosmos.es_incremento_valido("v0.5.0", "v0.5.0"))

    def test_clasificacion(self):
        c = cosmos.clasificar_cambios
        self.assertEqual(c([], "", []), "ninguno")
        self.assertEqual(c(["docs: x"], "", ["docs/a.md", "SIAAF-KNOWLEDGE/b.json"]), "documental")
        self.assertEqual(
            c(["feat: x"], "", ["scripts/cosmos/cosmos.py", "CLAUDE.md"]), "documental"
        )
        self.assertEqual(c(["fix: x"], "", ["src/a.py"]), "patch")
        self.assertEqual(c(["fix: x", "feat(api): y"], "", ["src/a.py"]), "minor")
        self.assertEqual(c(["feat(api)!: y"], "", ["src/a.py"]), "major")
        self.assertEqual(c(["feat: y"], "BREAKING CHANGE: z", ["src/a.py"]), "major")


class TestVerificar(BaseCosmos):
    def test_registro_coherente(self):
        self.assertEqual(self.errores(), [])
        self.assertEqual(self.ejecutar("verificar")[0], 0)

    def test_catalogo_requiere_descripcion_y_tematica(self):
        self.registro["catalogo"][4]["tematica"] = ""
        self.guardar()
        self.assertError("sin descripción o temática")
        self.registro["catalogo"][4] = {"nombre": "Trap pist", "descripcion": "x", "tematica": "y"}
        self.guardar()
        self.assertError("mayúsculas y sin espacios")

    def test_hito_fuera_del_catalogo(self):
        self.registro["versiones"][1]["hito"] = "KRYPTON"
        self.guardar()
        self.assertError("no está en el catálogo oficial")

    def test_hito_repetido_sin_excepcion(self):
        self.registro["versiones"][1]["hito"] = "ANDROMEDA"
        self.guardar()
        self.assertError("ya estaba asignado")
        self.registro["versiones"][1]["excepcion_hito"] = "histórica"
        self.guardar()
        self.assertEqual(self.errores(), [])

    def test_hito_fuera_de_orden_permitido(self):
        # DK-012: el hito se elige por propósito, no por el orden del catálogo.
        self.registro["versiones"][0]["hito"] = "TRAPPIST"
        self.registro["versiones"][1]["hito"] = "ORION"
        self.guardar()
        self.assertEqual(self.errores(), [])

    def test_hito_usado_sin_version(self):
        self.registro["entregas_sin_version"] = [
            {"commit": self.c3, "fecha": "2026-11-10", "hito": "HELIOS", "descripcion": "doc"}
        ]
        self.registro["versiones"].append(version("v0.4.0", "HELIOS", self.c3, "2026-11-10"))
        self.guardar()
        self.assertError("ya estaba asignado")

    def test_version_duplicada_y_formato(self):
        self.registro["versiones"][1]["version"] = "v0.2.0"
        self.guardar()
        self.assertError("versión duplicada")
        self.registro["versiones"][1]["version"] = "V0.3.0"
        self.guardar()
        self.assertError("formato vX.Y.Z")

    def test_incremento_invalido(self):
        self.registro["versiones"][1]["version"] = "v0.4.0"
        self.guardar()
        self.assertError("no es un incremento SemVer válido")

    def test_commit_fuera_de_la_historia_principal(self):
        self.registro["versiones"][1]["commit"] = self.r.lateral["f2"]
        self.guardar()
        self.assertError("no pertenece a la historia principal")

    def test_commit_abreviado_e_inexistente(self):
        self.registro["versiones"][1]["commit"] = self.c2[:7]
        self.guardar()
        self.assertError("SHA completo")
        self.registro["versiones"][1]["commit"] = "0" * 40
        self.guardar()
        self.assertError("no existe")

    def test_fecha_distinta(self):
        self.registro["versiones"][1]["fecha"] = "2026-11-07"
        self.guardar()
        self.assertError("distinta de la del commit")

    def test_orden_de_commits(self):
        self.registro["versiones"][0].update(commit=self.c2, fecha="2026-11-06")
        self.registro["versiones"][1].update(commit=self.c1, fecha="2026-11-05")
        self.guardar()
        self.assertError("no desciende")

    def test_version_estable_requiere_declaracion(self):
        self.registro["versiones"].append(version("v1.0.0", "HELIOS", self.c3, "2026-11-10"))
        self.guardar()
        self.assertError("sin primera versión estable declarada")
        self.registro["primera_version_estable"] = {"version": "v1.0.0", "decision": "DK-999"}
        self.guardar()
        self.assertEqual(self.errores(), [])

    def test_sin_validaciones(self):
        self.registro["versiones"][1]["validaciones"] = []
        self.guardar()
        self.assertError("sin validaciones")

    def test_documento_editado_a_mano(self):
        texto = self.doc_ruta.read_text().replace("Entrega v0.3.0", "Otra cosa")
        self.doc_ruta.write_text(texto)
        self.assertError("no coincide con el registro")
        self.assertEqual(self.ejecutar("documentar")[0], 0)
        self.assertEqual(self.errores(), [])

    def test_documento_sin_bloques(self):
        self.doc_ruta.write_text("# vacío\n")
        self.assertError("falta el bloque generado")


class TestEtiquetas(BaseCosmos):
    def etiquetar(self, nombre, commit, mensaje=None, anotada=True):
        if anotada:
            self.r.git("tag", "-a", nombre, "-m", mensaje or nombre, commit)
        else:
            self.r.git("tag", nombre, commit)

    def test_etiqueta_correcta_preparada_avisa(self):
        v = self.registro["versiones"][1]
        self.etiquetar("v0.3.0", self.c2, cosmos.mensaje_etiqueta(v))
        res = cosmos.verificar(self.ctx())
        self.assertEqual(res.errores, [])
        self.assertTrue(any("marcar-publicada" in a for a in res.avisos))

    def test_etiqueta_en_commit_equivocado(self):
        v = self.registro["versiones"][1]
        self.etiquetar("v0.3.0", self.c1, cosmos.mensaje_etiqueta(v))
        self.assertError("la etiqueta local apunta a")

    def test_etiqueta_ligera_y_mensaje(self):
        self.etiquetar("v0.3.0", self.c2, anotada=False)
        self.assertError("ligera")
        self.r.git("tag", "-d", "v0.3.0")
        self.etiquetar("v0.3.0", self.c2, "OTRO v0.3.0 — x")
        self.assertError("primera línea del mensaje")

    def test_etiqueta_no_registrada(self):
        self.etiquetar("v0.9.0", self.c3)
        self.assertError("no está en el registro")

    def test_publicada_sin_etiqueta_remota_ni_datos(self):
        v = self.registro["versiones"][1]
        self.etiquetar("v0.3.0", self.c2, cosmos.mensaje_etiqueta(v))
        v["estado"] = "publicada"
        self.guardar()
        self.assertError("no existe la etiqueta en 'origin'")
        self.assertError("sin datos de publicación")

    def test_remota_distinta_de_local(self):
        v = self.registro["versiones"][1]
        self.etiquetar("v0.3.0", self.c2, cosmos.mensaje_etiqueta(v))
        self.r.git("push", "-q", "origin", "refs/tags/v0.3.0")
        self.r.git("tag", "-d", "v0.3.0")
        self.etiquetar("v0.3.0", self.c2, cosmos.mensaje_etiqueta(v) + "\notro")
        self.assertError("objetos distintos")


class TestPublicar(BaseCosmos):
    def publicar(self, v, *extra):
        return self.ejecutar("publicar", v, "--ejecutar", "--confirmar", v, *extra)

    def test_simulacion_no_crea_nada(self):
        codigo, salida = self.ejecutar("publicar", "v0.3.0")
        self.assertEqual(codigo, 0, salida)
        self.assertIn("SIMULACIÓN superada", salida)
        self.assertIn("--latest=true", salida)
        self.assertEqual(self.r.git("tag", "-l"), "")
        self.assertEqual(self.r.git("ls-remote", "--tags", "origin"), "")
        self.assertEqual(self.releases_falsas(), {})

    def test_ejecutar_sin_confirmacion_rechaza(self):
        for extra in ([], ["--confirmar", "v0.2.0"]):
            codigo, salida = self.ejecutar("publicar", "v0.3.0", "--ejecutar", *extra)
            self.assertEqual(codigo, 2, salida)
            self.assertIn("RECHAZADO", salida)
        self.assertEqual(self.r.git("tag", "-l"), "")
        self.assertEqual(self.releases_falsas(), {})

    def test_ejecucion_completa_latest_y_no_repetible(self):
        for v in ("v0.2.0", "v0.3.0"):
            codigo, salida = self.publicar(v)
            self.assertEqual(codigo, 0, salida)
        self.assertEqual(self.r.git("cat-file", "-t", "v0.2.0"), "tag")
        self.assertEqual(self.r.git("rev-parse", "v0.2.0^{commit}"), self.c1)
        mensaje = self.r.git("tag", "-l", "--format=%(contents)", "v0.2.0")
        self.assertTrue(mensaje.startswith("ANDROMEDA v0.2.0 — Entrega v0.2.0"))
        self.assertIn("Publicación retrospectiva", mensaje)
        self.assertIn("2026-11-05", mensaje)
        self.assertIn("2026-11-12", mensaje)
        self.assertIn(self.c1, self.r.git("ls-remote", "--tags", "origin"))
        llamadas = [
            json.loads(linea) for linea in (self.gh_dir / "llamadas.log").read_text().splitlines()
        ]
        creadas = {c[2]: c for c in llamadas if c[:2] == ["release", "create"]}
        self.assertIn("--latest=false", creadas["v0.2.0"])
        self.assertIn("--latest=true", creadas["v0.3.0"])
        releases = self.releases_falsas()
        self.assertFalse(releases["v0.2.0"]["latest"])
        self.assertTrue(releases["v0.3.0"]["latest"])
        self.assertEqual(releases["v0.3.0"]["name"], "ECLIPSE v0.3.0 — Entrega v0.3.0")

        objeto = self.r.git("rev-parse", "v0.2.0")
        codigo, salida = self.publicar("v0.2.0")
        self.assertEqual(codigo, 1)
        self.assertIn("no se mueve ni se reemplaza", salida)
        self.assertIn("ya existe una GitHub Release", salida)
        self.assertEqual(self.r.git("rev-parse", "v0.2.0"), objeto)

        for v in ("v0.2.0", "v0.3.0"):
            self.assertEqual(self.ejecutar("marcar-publicada", v)[0], 0)
        datos = json.loads(self.registro_ruta.read_text())
        pub = datos["versiones"][0]["publicacion"]
        self.assertEqual(pub["etiqueta_objeto"], objeto)
        self.assertEqual(pub["fecha"], "2026-11-12")
        self.assertTrue(pub["release_url"].endswith("/v0.2.0"))
        self.assertEqual(self.errores(releases=True), [])
        self.assertEqual(self.ejecutar("verificar", "--releases")[0], 0)

    def test_verificar_releases_detecta_latest_y_titulo(self):
        for v in ("v0.2.0", "v0.3.0"):
            self.publicar(v)
            self.ejecutar("marcar-publicada", v)
        ruta = self.gh_dir / "releases.json"
        rel = json.loads(ruta.read_text())
        rel["v0.3.0"]["latest"], rel["v0.2.0"]["latest"] = False, True
        rel["v0.2.0"]["name"] = "otro título"
        ruta.write_text(json.dumps(rel))
        self.registro = json.loads(self.registro_ruta.read_text())
        self.assertError("se esperaba v0.3.0", releases=True)
        self.assertError("título de la release", releases=True)

    def test_marcar_publicada_sin_release_falla(self):
        self.publicar("v0.3.0", "--sin-release")
        codigo, salida = self.ejecutar("marcar-publicada", "v0.3.0")
        self.assertEqual(codigo, 1)
        self.assertIn("no existe la GitHub Release", salida)
        datos = json.loads(self.registro_ruta.read_text())
        self.assertEqual(datos["versiones"][1]["estado"], "preparada")

    def test_bloquea_si_main_remoto_no_contiene_el_commit(self):
        c4 = self.r.entrega("f4", "src/d.py", "feat: cuatro", "2026-11-12T06:00:00-05:00")
        self.registro["versiones"].append(version("v0.4.0", "HELIOS", c4, "2026-11-12"))
        self.guardar()
        codigo, salida = self.publicar("v0.4.0")
        self.assertEqual(codigo, 1)
        self.assertIn("historia principal publicada", salida)
        self.assertEqual(self.r.git("tag", "-l"), "")

    def test_exige_asignacion_confirmada_en_commit(self):
        dentro = self.r.dir / "registro.json"
        cosmos.guardar_registro(dentro, self.registro)
        self.registro_ruta = dentro
        codigo, salida = self.ejecutar("publicar", "v0.3.0")
        self.assertEqual(codigo, 1)
        self.assertIn("no está confirmada en un commit", salida)
        self.r.git("add", "--", "registro.json")
        self.r.git("commit", "-q", "-m", "docs: registro")
        codigo, salida = self.ejecutar("publicar", "v0.3.0")
        self.assertEqual(codigo, 0, salida)

    def test_sin_remoto_no_publica(self):
        codigo, _ = self.ejecutar("--sin-remoto", "publicar", "v0.3.0")
        self.assertEqual(codigo, 2)


class TestProponerYRegistrar(BaseCosmos):
    def test_sin_cambios(self):
        self.registro["versiones"].append(version("v0.4.0", "HELIOS", self.c3, "2026-11-10"))
        self.guardar()
        codigo, salida = self.ejecutar("proponer")
        self.assertEqual(codigo, 0)
        self.assertIn("No hay cambios", salida)

    def test_solo_documentacion(self):
        self.r.entrega("d1", "docs/guia.md", "docs: guía", "2026-11-11T09:00:00-05:00")
        self.registro["versiones"].append(version("v0.4.0", "HELIOS", self.c3, "2026-11-10"))
        self.guardar()
        codigo, salida = self.ejecutar("proponer")
        self.assertEqual(codigo, 0)
        self.assertIn("DK-005", salida)

    def test_patch_minor_y_major_en_0x(self):
        codigo, salida = self.ejecutar("--sin-remoto", "proponer")
        self.assertEqual(codigo, 0, salida)
        self.assertIn("PATCH", salida)  # desde v0.3.0 (c2) solo hay un fix
        self.assertIn("v0.3.1", salida)
        self.assertIn("propósito dominante", salida)
        self.assertIn("- ORION: Temática ORION", salida)
        self.assertNotIn("- ANDROMEDA:", salida)
        self.r.entrega("f5", "src/e.py", "feat(api)!: rompe", "2026-11-12T06:00:00-05:00")
        codigo, salida = self.ejecutar("--sin-remoto", "proponer")
        self.assertIn("MINOR (cambio incompatible en 0.x", salida)
        self.assertIn("v0.4.0", salida)
        codigo, salida = self.ejecutar("--sin-remoto", "proponer", "--incremento", "major")
        self.assertEqual(codigo, 1)
        self.assertIn("primera versión estable", salida)

    def test_hito_elegido(self):
        codigo, salida = self.ejecutar("--sin-remoto", "proponer", "--hito", "ORION")
        self.assertEqual(codigo, 0, salida)
        self.assertIn("Hito elegido: ORION", salida)
        codigo, salida = self.ejecutar("--sin-remoto", "proponer", "--hito", "ANDROMEDA")
        self.assertEqual(codigo, 1)
        self.assertIn("no está disponible", salida)

    def test_catalogo_agotado(self):
        self.registro["catalogo"] = [h for h in CATALOGO if h["nombre"] in ("ANDROMEDA", "ECLIPSE")]
        self.guardar()
        codigo, salida = self.ejecutar("--sin-remoto", "proponer")
        self.assertEqual(codigo, 1)
        self.assertIn("catálogo agotado", salida)

    def test_registrar_valido_e_invalido(self):
        codigo, salida = self.ejecutar(
            "--sin-remoto",
            "registrar",
            "--version",
            "v0.4.0",
            "--hito",
            "HELIOS",
            "--commit",
            self.c3[:7],
            "--titulo",
            "T",
            "--descripcion",
            "D",
            "--validacion",
            "pytest ok",
        )
        self.assertEqual(codigo, 0, salida)
        datos = json.loads(self.registro_ruta.read_text())
        self.assertEqual(datos["versiones"][-1]["commit"], self.c3)
        self.assertEqual(datos["versiones"][-1]["fecha"], "2026-11-10")
        self.assertEqual(self.errores(remoto=False), [])

        antes_doc, antes_reg = self.doc_ruta.read_text(), self.registro_ruta.read_text()
        codigo, salida = self.ejecutar(
            "--sin-remoto",
            "registrar",
            "--version",
            "v0.6.0",
            "--hito",
            "ANDROMEDA",
            "--commit",
            self.c3,
            "--titulo",
            "T",
            "--descripcion",
            "D",
            "--validacion",
            "x",
        )
        self.assertEqual(codigo, 1)
        self.assertEqual(self.doc_ruta.read_text(), antes_doc)
        self.assertEqual(self.registro_ruta.read_text(), antes_reg)


class TestRepositorioReal(unittest.TestCase):
    """El registro versionado del proyecto debe ser coherente (sin red)."""

    def test_registro_del_proyecto(self):
        raiz = Path(__file__).resolve().parents[2]
        registro = raiz / cosmos.RUTA_REGISTRO
        if not registro.exists() or not (raiz / ".git").exists():
            self.skipTest("fuera del repositorio del proyecto")
        ctx = cosmos.Contexto(raiz, registro, raiz / cosmos.RUTA_DOC, remoto_activo=False)
        self.assertEqual(cosmos.verificar(ctx).errores, [])


if __name__ == "__main__":
    unittest.main()
